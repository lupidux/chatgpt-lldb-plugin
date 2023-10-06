import prompts
import api_connection.api_messaging as api_messaging
import browser_connection.browser_messaging as browser_messaging
import browser_config
import os
from os import path
import time
import yaml
import subprocess
import multiprocessing

modality = "api_key_mode"
def mode(debugger, command, result, internal_dict):
    global modality
    print(modality)

def switch(debugger, command, result, internal_dict):
    def cleaner_caller():
        cleaner_path = path.join(path.dirname(path.abspath(path.realpath(__file__))),"browser_connection","cleaner.py")
        subprocess.Popen(["python3", cleaner_path], stderr=subprocess.DEVNULL)

    global modality
    if modality == "api_key_mode":
        browser_messaging.quit()
        initialization = browser_messaging.init()
        if initialization == "done":
            modality = "browser_mode"
            cleaner_proc = multiprocessing.Process(target=cleaner_caller)
            cleaner_proc.start()
        else:
            print("You must log in into your ChatGPT account to use `browser_mode`")
    elif modality == "browser_mode":
        browser_messaging.quit()
        modality = "api_key_mode"

def code(debugger, command, result, internal_dict):
    sourceCode = prompts.code(debugger)
    if sourceCode:
        print(sourceCode)

codeAlreadySent = False
startedChat = False
def send(debugger, command, result, internal_dict):
    global modality
    debuggingInfo = ""

    codeInfo = prompts.codeInfo(debugger)
    stepInfo = prompts.stepInfo(debugger)
    if codeInfo and stepInfo is not None:
        global codeAlreadySent
        if codeAlreadySent is False:
            debuggingInfo = codeInfo

        debuggingInfo = debuggingInfo + stepInfo
        if (modality == "api_key_mode"):
            reply = api_messaging.send_to_chatgpt(debuggingInfo)
        elif (modality == "browser_mode"):
            global startedChat
            if startedChat is False:
                startedChat = browser_messaging.new_chat()
            reply = browser_messaging.send_to_chatgpt(debuggingInfo, "noReplynoWait")

        if reply:
            codeAlreadySent = True

def ask(debugger, command, result, internal_dict):
    global modality

    userRequest = command.strip()
    if userRequest:
        if (modality == "api_key_mode"):
            reply = api_messaging.send_to_chatgpt(userRequest)
        elif (modality == "browser_mode"):
            global startedChat
            if startedChat is False:
                startedChat = browser_messaging.new_chat()
            reply = browser_messaging.send_to_chatgpt(userRequest, "waitForReply")

        if reply:
            print(reply)
    else:
        print("You must place an argument: YOUR_REQUEST")

def wait(debugger, command, result, internal_dict):
    if (modality == "api_key_mode"):
        print("This command is supported only in `browser_mode`")
    elif (modality == "browser_mode"):
        newWaitTime = command.strip()
        if newWaitTime:
            browser_config.timeForResponse = int(newWaitTime)
        else:
            print("You must place an argument: TIME_IN_SECONDS")

def autodebug(debugger, command, result, internal_dict):
    if (modality == "api_key_mode"):
        look_for_errors_request = prompts.automatedDebuggingInfo(debugger)
        debugger.HandleCommand('send')
        debugger.HandleCommand(f'ask ' + look_for_errors_request)
    elif (modality == "browser_mode"):
        look_for_errors_request = prompts.automatedDebuggingInfo(debugger)
        debugger.HandleCommand('send')
        wait_to_write = browser_config.timeForResponse / 4
        time.sleep(wait_to_write) #It is recommended to wait at least 5 seconds.
        debugger.HandleCommand(f'ask ' + look_for_errors_request)

alreadySaved = False
def save(debugger, command, result, internal_dict):
    src_name = prompts.sourceFile_name(debugger)

    if src_name is not None:
        dirName = path.join(path.dirname(path.abspath(path.realpath(__file__))), "saves")
        fileName = "dbChat_"+src_name+".yaml"
        filePath = path.join(dirName, fileName)
        
        if not path.exists(dirName):
            os.makedirs(dirName)

        if (modality == "api_key_mode"):
            history = api_messaging.retrieve_chat()
            with open(filePath, "w") as file:
                yaml.dump(history, file)
        elif (modality == "browser_mode"):
            global alreadySaved
            if alreadySaved is False:
                chatAlreadyExisting = browser_messaging.select_chat(src_name, "save")
                if chatAlreadyExisting:
                    browser_messaging.delete_chat(src_name)
                alreadySaved = browser_messaging.rename_chat(src_name)
            else:
                print("Chat has already been saved")

def load(debugger, command, result, internal_dict):
    src_name = prompts.sourceFile_name(debugger)

    if src_name is not None:
        dirName = path.join(path.dirname(path.abspath(path.realpath(__file__))), "saves")
        fileName = "dbChat_"+src_name+".yaml"
        filePath = path.join(dirName, fileName)

        if (modality == "api_key_mode"):
            try:
                with open(filePath, 'r') as file:
                    api_messaging.history = yaml.safe_load(file)

            except FileNotFoundError:
                print(f"There's no debugging state of {src_name}")
            except yaml.YAMLError:
                print(f"Failure in loading the debugging state of {src_name}")

        elif (modality == "browser_mode"):
            global startedChat
            startedChat = browser_messaging.select_chat(src_name, "load")

def expChat(debugger, command, result, internal_dict):
    if (modality == "api_key_mode"):
        filePath = command.strip()+".yaml"

        dirName = path.dirname(filePath)
        if not path.exists(dirName):
            os.makedirs(dirName)
        
        history = api_messaging.retrieve_chat()
        with open(filePath, "w") as file:
            yaml.dump(history, file)
    elif (modality == "browser_mode"):
        print("This command is supported only in `api_key_mode`")

def impChat(debugger, command, result, internal_dict):
    if (modality == "api_key_mode"):
        filePath = command.strip()

        try:
            with open(filePath, 'r') as file:
                api_messaging.history = yaml.safe_load(file)

        except FileNotFoundError:
            print(f"There's no debugging state here {filePath}")
        except yaml.YAMLError:
            print(f"Failure in loading the following debugging state {filePath}")

    elif (modality == "browser_mode"):
        print("This command is supported only in `api_key_mode`")

def clear(debugger, command, result, internal_dict):
    if (modality == "api_key_mode"):
        api_messaging.history.clear()
    elif (modality == "browser_mode"):
        browser_messaging.new_chat()

def info(debugger, command, result, internal_dict):
    print(f"ChatGPT LLDB Plugin commands: \n    {'mode'.ljust(10)} -- See the actual connection mode to ChatGPT, `api_key_mode` is the default one.\n    {'switch'.ljust(10)} -- Switch among `api_key_mode`(default) and `browser_mode` connection to ChatGPT.\n    {'code'.ljust(10)} -- See the source code of the debugging target.\n    {'send'.ljust(10)} -- Sends informations about the source code, the current line and the visible variables to ChatGPT.\n    {'ask'.ljust(10)} -- Directly interact with ChatGPT expressing your issues, ex.: `ask YOUR_REQUEST`.\n    {'wait'.ljust(10)} -- Changes, for the current session, the time (seconds) you wait for ChatGPT responses (supported only in `browser_mode`), ex.: `wait TIME_IN_SECONDS`.\n    {'autodebug'.ljust(10)} -- Automatically track down code bugs with this compact command.\n    {'save'.ljust(10)} -- Save your current chat about the program you're debugging (in `browser_mode` you have just one saving per session).\n    {'load'.ljust(10)} -- Load last saved chat about the program you're debugging.\n    {'import'.ljust(10)} -- Import a saved chat about the program you're debugging (supported only in `api_key_mode`), ex.: `import /home/user/PATH/TO/YOUR_FILE`.\n    {'export'.ljust(10)} -- Export your current chat about the program you're debugging (supported only in `api_key_mode`), ex.: `export /home/user/PATH/TO/YOUR_FILE`.\n    {'clear'.ljust(10)} -- Clear your interactions with ChaGPT.\n    {'info'.ljust(10)} -- List the commands introduced by `chatgpt-lldb-plugin` with a brief description of each one.")

def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f commands.mode mode')
    debugger.HandleCommand('command script add -f commands.switch switch')
    debugger.HandleCommand('command script add -f commands.code code')
    debugger.HandleCommand('command script add -f commands.send send')
    debugger.HandleCommand('command script add -f commands.ask ask')
    debugger.HandleCommand('command script add -f commands.wait wait')
    debugger.HandleCommand('command script add -f commands.autodebug autodebug')
    debugger.HandleCommand('command script add -f commands.save save')
    debugger.HandleCommand('command script add -f commands.load load')
    debugger.HandleCommand('command script add -f commands.expChat export')
    debugger.HandleCommand('command script add -f commands.impChat import')
    debugger.HandleCommand('command script add -f commands.clear clear')
    debugger.HandleCommand('command script add -f commands.info info')
