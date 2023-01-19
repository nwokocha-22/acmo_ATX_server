import win32service, win32serviceutil, win32api, win32con, win32event, win32evtlogutil
import psutil
import subprocess
import os, sys, string, time, socket, signal
import servicemanager

class Service (win32serviceutil.ServiceFramework):
    _svc_name_ = "Service"
    _svc_display_name_ = "Service"

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
        while self.runflag:
            rc = win32event.WaitForSingleObject(self.stop_event, 24*60*60)
            # Check to see if self.hWaitStop happened
            if rc == win32event.WAIT_OBJECT_0:
                self.log("Service has stopped")
                break
            else:
                try:
                    #logic
                    print()
                except Exception as e:
                    self.log(str(e))

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(Service)
        servicemanager.StartServiceCtrlDispatcher()
        
    else:
        win32serviceutil.HandleCommandLine(Service)