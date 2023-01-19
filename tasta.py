
import win32service 
import win32serviceutil
import win32api
import win32con
import win32event
import win32evtlogutil
import win32evtlog
import psutil
import subprocess
import os, sys, string, time, socket, signal
import servicemanager

event_log = "Security"

h = win32evtlog.OpenEventLog(None, event_log)
#flags = win32evtlog.EVENTLOG_FORWARDS_READ|win32evtlog.EVENTLOG_SEEK_READ
flags= win32evtlog.EVENTLOG_BACKWARDS_READ|win32evtlog.EVENTLOG_SEQUENTIAL_READ
last_record = win32evtlog.GetNumberOfEventLogRecords(h)
process = None
hWaitStop = win32event.CreateEvent(None, 0, 0, None)
while True:
    events = win32evtlog.ReadEventLog(h, flags, last_record)
    if events:
        for event in events:
            if event.EventType == win32con.EVENTLOG_AUDIT_SUCCESS:
                if event.EventID == 4624:
                    print("log in", event.StringInserts)
                    script_path = r"C:\ActivityMonitor\core.py"
                    args = ["arg1", "arg2", "arg3"]
                    #Start the script and pass arguments
                    process = subprocess.Popen(script_path, shell=True)
                    
                elif event.EventID == 4634:
                    print("log out", event.StringInserts)
                    current_record = win32evtlog.GetNumberOfEventLogRecords(h)
                    if current_record != last_record:
                        last_record = current_record
                    else:
                    # Wait for a second before checking again
                        win32event.WaitForSingleObject(hWaitStop, 1000)
                # if event.StringInserts:
                #     if event.StringInserts[-1] == "Logon":
                #         print("Remote desktop logon event detected")
                #         script_path = r"C:\ActivityMonitor\core.py"
                #         # args = ["arg1", "arg2", "arg3"]
                #         # Start the script and pass arguments
                #         process = subprocess.Popen(script_path, shell=True)
                #     elif event.StringInserts[-1] == "Logoff":
                #         print("Remote desktop logoff event detected")
                #         # Kill the script when logoff event is detected
                #         if process:
                #             process.kill()
                #         current_record = win32evtlog.GetNumberOfEventLogRecords(h)
                #         if current_record != last_record:
                #             last_record = current_record
                #         else:
                #         # Wait for a second before checking again
                #             win32event.WaitForSingleObject(hWaitStop, 1000)