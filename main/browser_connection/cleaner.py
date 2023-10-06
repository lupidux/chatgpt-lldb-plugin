import psutil
import time
import atexit
import browser_messaging

def cleanup():
    browser_messaging.quit()

def lldb_monitor():
    try:
        lldb_process = None
        while True:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] == 'lldb':
                    lldb_process = psutil.Process(proc.info['pid'])
                    break

            if lldb_process is None:
                print("LLDB process not found... exiting")
                break

            if lldb_process.status() == psutil.STATUS_ZOMBIE:
                cleanup()
                break

            time.sleep(1)

    except KeyboardInterrupt:
        print("LLDB tracking interrupted")

atexit.register(cleanup)
lldb_monitor()
