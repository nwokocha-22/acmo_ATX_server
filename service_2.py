import subprocess
import win32evtlog
import win32evtlogutil
import win32con
import win32event
import win32service
import win32serviceutil

class LogonLogoffService(win32serviceutil.ServiceFramework):
    """
    A windows service that listens for remote desktop logon and logoff events in real-time
    and starts/kills a python script when a logon/logoff event is detected
    """
    _svc_name_ = "ActivyMonitorService"
    _svc_display_name_ = "Activity Monitor Service"
    _svc_description_ = "Starts the activity monitor script when a user is log in"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.process = None

    def SvcDoRun(self):
        """
        Service initialization code
        """
        # Report service status as running
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        # Log service start event
        win32evtlogutil.ReportEvent(self._svc_name_,
                                    win32evtlog.EVENTLOG_INFORMATION_TYPE,
                                    0, # eventCategory
                                    win32service.SERVICE_STARTED, # eventID
                                    None, # userSid
                                    [self._svc_name_], # strings
                                    None) # data
        # Continuously listen for logon and logoff events
        while 1:
            # Check for service stop event
            rc = win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
            if rc == win32event.WAIT_OBJECT_0:
                # Log service stop event
                win32evtlogutil.ReportEvent(self._svc_name_,
                                    win32evtlog.EVENTLOG_INFORMATION_TYPE,
                                    0, # eventCategory
                                    win32service.SERVICE_STOPPED, # eventID
                                    None, # userSid
                                    [self._svc_name_], # strings
                                    None) # data
                break
            # Open the Security event log in real-time
            event_log = "Security"
            event_source = None
            h = win32evtlog.OpenEventLog(None, event_log)
            flags = win32evtlog.EVENTLOG_FORWARDS_READ|win32evtlog.EVENTLOG_SEEK_READ
            last_record = win32evtlog.GetNumberOfEventLogRecords(h)
            process = None
            while True:
                events = win32evtlog.ReadEventLog(h, flags, 0)
                if events:
                    for event in events:
                        if event.EventType == win32con.EVENTLOG_AUDIT_SUCCESS:
                            if event.EventID == win32con.EVENTLOG_AUDIT_SUCCESS:
                                if event.StringInserts[-1] == "Logon":
                                    print("Remote desktop logon event detected")
                                    script_path = r"C:\ActivityMonitor\core.py"
                                    args = ["arg1", "arg2", "arg3"]
                                    # Start the script and pass arguments
                                    process = subprocess.Popen(["python", script_path, *args])
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

    def SvcStop(self):
        """
        Stops the service.
        """
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

if __name__ == "__main__":
    win32serviceutil.HandleCommandLine(LogonLogoffService)