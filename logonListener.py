#!/usr/bin/env python

import os
import win32evtlog, win32event
import subprocess
import getpass
from pathlib import Path
from threading import Thread


from core import ActivityMonitor

# logon type = 10 = remote desktop
# The right events are 4624 (LOGON) and 4634(LOGOFF).
server = "WIN-35Q6G6JIQT0"
log_type = "Security"


log_off = win32event.CreateEvent(None, 0, 0, "event_log")
eventLog = win32evtlog.OpenEventLog(server, log_type)

channel = 'Security'
ip = "127.0.0.1" 
port = 5005 
password = os.environ["PASSWORD"] 
sender = os.environ["SENDER"]
receiver = os.environ["RECEIVER"]

monitoring = False
process = None
calls = 0
def on_logon_event(action, context, event_handle):
    """ starts the monitoring script """
    print(action, context, event_handle)
    print("======== triggered =======")
    # if getpass.getuser() == "Administrator":
    #     activityMonitor = ActivityMonitor(ip, port, password, sender, receiver)
    #     activityMonitor.start()
    path_to_script = Path.cwd()/'core.py'

    global monitoring
    global process

    def start_script(path):
        global process
        process = subprocess.call(["python", path])
    
    if not monitoring:
        global calls 
        calls += 1
        print("function called:", calls)
        print("script started")
       
        # t =Thread(target = start_script, args=(path_to_script,))
        # t.start()
        # t.join()
        
    else:
        process.terminate()
        monitoring=False
        print("script terminated")

def on_logout_event(action, context, event_handle):
    """ Terminates the script """
    print("Logout occured")

eventtype = win32evtlog.EvtRpcLogin
handle =win32evtlog.EvtSubscribe(channel, win32evtlog.EvtRpcLogin, None, Callback = on_logon_event)
win32evtlog.NotifyChangeEventLog(eventLog, log_off)
#win32evtlog.EvtSubscribe(channel, win32evtlog.EvtLogAttributes, None, Callback = on_logout_event)
win32event.WaitForSingleObject(log_off, win32event.INFINITE)
input()

win32evtlog.CloseEventLog(handle)