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

class ActivityMonitorService (win32serviceutil.ServiceFramework):
    _svc_name_ = "ActivityMonitorService"
    _svc_display_name_ = "Activity Monitor"

    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self, *args)
        self.log('Service Initialized.')
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)


    def log(self, msg):
        servicemanager.LogInfoMsg(str(msg))

    def sleep(self, sec):
        win32api.Sleep(sec*1000, True)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.stop()
        self.log('Service has stopped.')
        win32event.SetEvent(self.stop_event)
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)

    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        try:
            self.ReportServiceStatus(win32service.SERVICE_RUNNING)
            self.log('Service is starting.')
            self.main()
            win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)
            servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,servicemanager.PYS_SERVICE_STARTED,(self._svc_name_, ''))
        except Exception as e:
            s = str(e)
            self.log('Exception :'+s)
            self.SvcStop()

    def stop(self):
        self.runflag=False
        try:
            #logic
            print("stopped")
        except Exception as e:
            self.log(str(e))

    def main(self):

        self.runflag=True
        event_log = "Security"
        h = win32evtlog.OpenEventLog(None, event_log)
        flags = win32evtlog.EVENTLOG_FORWARDS_READ|win32evtlog.EVENTLOG_SEEK_READ
        last_record = win32evtlog.GetNumberOfEventLogRecords(h)
        process = None
        
        while self.runflag:
            rc = win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)
            
            # Check to see if self.hWaitStop happened
            if rc == win32event.WAIT_OBJECT_0:
                self.log("Service has stopped")
                break
            else:
                try:
                    while True:
                        events = win32evtlog.ReadEventLog(h, flags, 0)
                        if events:
                            for event in events:
                                if event.EventType == win32con.EVENTLOG_AUDIT_SUCCESS:
                                    #if event.EventID == win32con.EVENTLOG_AUDIT_SUCCESS:
                                    print("log on event",event.StringInserts[-1])
                                    if event.StringInserts[-1] == "Logon":
                                        print("Remote desktop logon event detected")
                                        script_path = r"C:\ActivityMonitor\core.py"
                                        # args = ["arg1", "arg2", "arg3"]
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

                except Exception as e:
                    self.log(str(e))

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(ActivityMonitorService)
        servicemanager.StartServiceCtrlDispatcher()
        
    else:
        win32serviceutil.HandleCommandLine(ActivityMonitorService)