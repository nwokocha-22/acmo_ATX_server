
import subprocess
import win32evtlog
import win32evtlogutil
import win32con
import win32event
import win32service
import win32serviceutil

event_log = "Security"
h = win32evtlog.OpenEventLog(None, event_log)
#flags = win32evtlog.EVENTLOG_FORWARDS_READ|win32evtlog.EVENTLOG_SEEK_READ
flags = win32evtlog.EVENTLOG_SEQUENTIAL_READ | win32evtlog.EVENTLOG_FORWARDS_READ
last_record = win32evtlog.GetNumberOfEventLogRecords(h)
process = None

while True:
    events = win32evtlog.ReadEventLog(h, flags, last_record)
    if events:
        for event in events:
            #if event.EventType == win32con.EVENTLOG_AUDIT_SUCCESS:
            print(event.EventID)
            if event.EventID == win32con.EVENTLOG_AUDIT_SUCCESS:
                print(event.StringInserts[-1])
                if event.StringInserts[-1] == "Logon":
                    print("Remote desktop logon event detected")
                    script_path = r"C:\ActivityMonitor\core.py"
                    args = ["arg1", "arg2", "arg3"]
                    # Start the script and pass arguments
                    process = subprocess.Popen(script_path, shell=True)
                elif event.StringInserts[-1] == "Logoff":
                    print("Remote desktop logoff event detected")
                    # Kill the script when logoff event is detected
                    if process:
                        process.kill()
                    current_record = win32evtlog.GetNumberOfEventLogRecords(h)
                    if current_record != last_record:
                        last_record = current_record
                    else:
                    # Wait for a second before checking again
                        win32event.WaitForSingleObject(self.hWaitStop, 1000)