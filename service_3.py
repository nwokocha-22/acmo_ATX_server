import win32serviceutil
import win32event
import subprocess

#: INSTALL SERVICE
#: python path/to/service.py install

#: START SERVICE
#: net start ActivityMonitorService

#: STOP SERVICE
#: net stop ActivityMonitorService

#: REMOVE SERVICE
# sc delete servicename

# 1072 error: means service is still there but marked for delection

"""

Anyone facing this issue, just copy pywintypes36.dll

from Python36\Lib\site-packages\pywin32_system32

to Python36\Lib\site-packages\win32

Helpful commands:

"""

#: Install a service: python scriptName.py install

#: Uninstall a service: python scriptName.py remove

#: Start a service: python scriptName.py start

#: Update service: python scriptName.py update


#: ALTERNATIVELY:

#: STEP 1: CONVERT TO EXECUTABLE FILE
#: pyinstaller --noconfirm --onefile --windowed --hidden-import win32timezone path-to-py file

#: STEP 2: INSTALL YOUR EXECUTABLE
#: yourexefile.exe --startup delayed install

#: STEP 3: START YOUR EXECUATABLE
#: yourexefile.exe start

# HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\

class ActivityMonitorService(win32serviceutil.ServiceFramework):

    _svc_name_ = "ActivyMonitorService"
    _svc_display_name_ = "Activity Monitor Service"
    _svc_description_ = "Starts the activity monitor script when a user is log in"

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
        self.process = subprocess.Popen("./core.py", shell=True)

    def stop(self):
        if self.process:
            self.process.terminate()

if __name__ == '__main__':
    import os
    try:
        win32serviceutil.HandleCommandLine(ActivityMonitorService)
    except SystemExit:
        os._exit(1)
    