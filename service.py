import win32serviceutil
import win32event
import subprocess
import servicemanager
import sys


class ActivityMonitorServerService(win32serviceutil.ServiceFramework):

    _svc_name_ = "ActivyMonitorServer"
    _svc_display_name_ = "Activity Monitor Service"
    _svc_description_ = "Starts the activity monitor server script when a user is log in"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.process = None

    def SvcStop(self):
        self.stop()
        win32event.SetEvent(self.stop_event)

    def SvcDoRun(self):
        self.start()
        #: Listen for Login 
        win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)

    def start(self):
        self.process = subprocess.call(["python", "./core.py"], shell=True, stdout=subprocess.PIPE)

    def stop(self):
        if self.process:
            self.process.terminate()

if __name__ == '__main__':
  
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(ActivityMonitorServerService)
        servicemanager.StartServiceCtrlDispatcher()
        
    else:
        win32serviceutil.HandleCommandLine(ActivityMonitorServerService)
    