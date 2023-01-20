
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
from datetime import timedelta, datetime, date

machine = "WIN-35Q6G6JIQT0"
event_log = "Security"

event_handle = win32evtlog.OpenEventLog(machine, event_log)
flags= win32evtlog.EVENTLOG_BACKWARDS_READ|win32evtlog.EVENTLOG_SEQUENTIAL_READ

last_record = win32evtlog.GetNumberOfEventLogRecords(event_handle)
print("last record", last_record)
process = None
hWaitStop = win32event.CreateEvent(None, 0, 0, None)
isRunning = False
import pdb


while True:
    print("ENTER OUTER LOOP")
    logoff_flag = win32evtlog.EVENTLOG_AUDIT_FAILURE
    logon_flag = win32evtlog.EVENTLOG_AUDIT_FAILURE

    rc = win32event.WaitForSingleObject(hWaitStop, win32event.INFINITE)
   
    print(rc, win32event.WAIT_OBJECT_0)
    if rc == win32event.WAIT_OBJECT_0:
        print("Service has stopped")
        break
    # else:
       
    #print("EXITING OUTER LOOP")
    while True:
        #: Get list of events
        print("ENTERED INNER LOOP")
        events = win32evtlog.ReadEventLog(event_handle, flags, 0)
        #print("event:", len(events))
        
        for event in events:
            print("Event", event)

            #pdb.set_trace()
        #if events:
            # event  = events[len(events) - 1]
            print("Event:", event)
            evtOn_flag=win32con.EVENTLOG_AUDIT_SUCCESS
            evtOff_flag = win32con.EVENTLOG_AUDIT_FAILURE
        
            # if events:
            #     for index, event in enumerate(events):
            #         print("index:", index)
                    
            date_ = event.TimeGenerated
            date_generated = datetime(date_.year, date_.month, date_.day, date_.hour, date_.minute, date_.second)
            time_gen_ = str(event.TimeGenerated)
            dt = datetime.strptime(time_gen_, "%Y-%m-%d %H:%M:%S")
            dt1 = dt.timetuple() #: log in event time
            dt2 = datetime.today().timetuple() #: current event time
        
            print("--ABOUT TIMING--")

            if dt1.tm_hour == dt2.tm_hour and dt1.tm_min == dt2.tm_min:
                if abs(dt2.tm_sec - dt1.tm_sec) <= 5:
                    if event.EventType == logon_flag and event.EventID == 4624:
                
                        print("=================== last record =================", last_record)
                        print("######################===========================########################")
                        print("LOG IN")

                        script_path = r"C:\\ActivityMonitor\\core.py"
                        
                        if not isRunning:
                            print("Script started")
                            isRunning = True
                            process = subprocess.call(["python", script_path])
                            break
            
                    elif event.EventType == logoff_flag and event.EventID == 4634:
                    
                        print("===================last record========", last_record)
                        print("######################===========================########################")
                        print("LOG OUT")

                        if isRunning:
                            process.terminate()
                            print("Script stopped")
                            isRunning = False
                            break

        print("EXIT INNER LOOP")
    print("OUTER LOOP")
    time.sleep(5)