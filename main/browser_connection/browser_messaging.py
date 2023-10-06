from selenium import webdriver
from selenium.webdriver.remote.webdriver import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, InvalidElementStateException, ElementNotInteractableException, StaleElementReferenceException, TimeoutException
import time
import socket
import threading
import subprocess
import sys
from os import path
import yaml

program_path = path.abspath(path.join(path.dirname(__file__), '..', '..'))
sys.path.insert(0, program_path)
import browser_config

chrome_path = browser_config.chrome_path
chrome_driver_path = browser_config.chrome_driver_path

def init():
    global driver
    url = r"https://chat.openai.com"
    free_port = find_available_port()
    launch_chrome_with_remote_debugging(free_port, url)
    response = wait_for_human_verification()
    if response == "y":
        driver = setup_webdriver(free_port)
        return "done"

def find_available_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]

def launch_chrome_with_remote_debugging(port, url):
    def open_chrome():
        chrome_cmd = [chrome_path, f'--remote-debugging-port={port}', '--user-data-dir=remote-profile', url]
        chrome_process = subprocess.Popen(chrome_cmd, stderr=subprocess.DEVNULL)
        chrome_pid = chrome_process.pid
        if chrome_pid:
            chrome_pids_path = path.join(path.dirname(path.abspath(path.realpath(__file__))), "previous_chrome_pids.yaml")
            with open(chrome_pids_path, "w") as file:
                yaml.dump([chrome_pid], file)
    
    chrome_thread = threading.Thread(target=open_chrome)
    chrome_thread.start()

def wait_for_human_verification():
    print("You need to manually complete the log-in or the human verification if required.")
    while True:
        user_input = input("Enter 'y' if you have completed the log-in or the human verification, 'n' to check again, or 'q' to abort the login procedure: ").lower()

        if user_input == 'y':
            return user_input
        elif user_input == 'n':
            print("\nWaiting for you to complete the human verification")
            time.sleep(5)
        elif user_input == 'q':
            quit()
            return user_input
        else:
            print("\nInvalid input. Please enter 'y', 'n', or 'q'.")

def setup_webdriver(port):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
    driver = webdriver.Chrome(executable_path=chrome_driver_path, options=chrome_options)

    return driver

def new_chat():
    global driver
    new_chat = driver.find_element(By.LINK_TEXT, "New chat")
    new_chat.click()

    return True

def send_to_chatgpt(content, wait):
    global driver
    input = driver.find_element(By.TAG_NAME, "textarea")
    input.send_keys(content)
    input.send_keys(Keys.RETURN)

    if wait == "noReplynoWait":
        time.sleep(1)
    elif wait == "waitForReply":
        tfr = browser_config.timeForResponse
        print(f"Waiting {tfr} seconds for ChatGPT reply (wait time is editable in `browser_config`)")
        time.sleep(tfr)

    reply = driver.find_elements(by=By.CSS_SELECTOR, value="div.text-base")[-1].text
    return reply

def select_chat(target_name, option):
    try:
        name = "dbChat_"+target_name
        chat_button = driver.find_element(By.LINK_TEXT, name)
        chat_button.click()

        return True
    except NoSuchElementException:
        if option == "load":
            print(f"There's no debugging state of {target_name}")
    
def delete_chat(target_name):
    try:
        bin_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "(//button[@class='p-1 hover:text-white'])[2]")))
        bin_button.click()
        delete_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//button[@class='btn relative btn-danger']//div[contains(text(), 'Delete')]")))
        delete_button.click()

    except StaleElementReferenceException:
        print("Operation failed. Try again")

def rename_chat(target_name):
    def std_exception():
        print("The https://chat.openai.com/ html code has been changed. Patch is required.")

    try:
        name = "dbChat_"+target_name

        chat_button = driver.find_element(By.CSS_SELECTOR, "li:first-child")
        chat_button.click()
        modify_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "(//button[@class='p-1 hover:text-white'])[1]")))
        modify_button.click()

        text_input = driver.find_element(By.XPATH, "//input[@type='text']")
        driver.execute_script("arguments[0].value = arguments[1];", text_input, name)

        check_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "(//button[@class='p-1 hover:text-white'])[1]")))
        check_button.click()

        return True

    except InvalidElementStateException:
        std_exception()
    except ElementNotInteractableException:
        std_exception()
    except StaleElementReferenceException:
        print("Operation failed. Try again")
    except TimeoutException:
        print("An error has occured on ChatGPT, the chat has been lost")

def quit():
    chrome_pids_path = path.join(path.dirname(path.abspath(path.realpath(__file__))), "previous_chrome_pids.yaml")
    try:
        with open(chrome_pids_path, 'r') as file:
            chrome_pids = yaml.safe_load(file)
            if chrome_pids is not None and isinstance(chrome_pids, list):
                for pid in chrome_pids:
                    subprocess.run(["kill", "-9", str(pid)], stderr=subprocess.DEVNULL)
            else:
                print("Can't close previous chrome session, proceed manually.")
    except Exception as e:
        print(f"Error in YAML file reading:", e)
