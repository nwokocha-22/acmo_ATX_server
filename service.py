#!usr/bin/
import sys
sys.path.append('.')
import helpers
from helpers.logServer import LogRecordSocketReceiver
from helpers.videoServer import VideoServer
from helpers.loggers.errorLog import error_logger
from threading import Thread
import win32serviceutil  # ServiceFramework and commandline helper
import win32serviceutil
import win32event
import servicemanager
import sys
import servicemanager  # Simple setup and logging
import multiprocessing

def main_app():
    """Starts the Video receiver and the Log receivers on different
    threads.

    Notes
    -----
        - The received video (mkv format) is writen to a file and saved
        in the Activity Monitor folder.
        - The received log is also saved in the log sub folder of the
        Activity Monitor folder.
        - The Activity Monitor directory is automatically created if it
        does not exist.
    """

    video_server = VideoServer()
    video_server.start()
    
    log_tcpserver = LogRecordSocketReceiver()
    log_thread = Thread(target=log_tcpserver.serve_until_stopped)
    log_thread.start()

    log_thread.join()
    video_server.join()


class ActivityMonitorServerService(win32serviceutil.ServiceFramework):
    """Starts and stops the core_app.exe client file.
    """

    _svc_name_ = "AMService"
    _svc_display_name_ = "Activity Monitor Service"
    _svc_description_ = "Starts, stops, udpate, and removes the activity monitor server."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.process = None

    def SvcStop(self):
        self.stop()
        win32event.SetEvent(self.stop_event)

    def SvcDoRun(self):
        self.start()
        win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)

    def start(self):
        self.process = multiprocessing.Process(target=main_app)
        self.process.start()
        self.process.join()

    def stop(self):
        self.process.terminate()

if __name__ == "__main__":
    multiprocessing.freeze_support()
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(ActivityMonitorServerService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(ActivityMonitorServerService)

# COMMAND TO CONVERT TO EXECUTABLE
"""
pyinstaller.exe --runtime-tmpdir=. --hidden-import win32timezone --collect-submodules helpers --hidden-import logging.handlers --hidden-import socketserver --hidden-import cv2 --name main_server --onefile main.py
"""