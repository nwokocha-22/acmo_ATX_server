from threading import Thread
from typing import Union, List, Optional, Callable
import win32clipboard as wc
from pathlib import Path
from dataclasses import dataclass
import win32gui
import time
import datetime
import  win32api
import ctypes
import pickle

from threading import Thread

class ClipboardMonitor(Thread):

    hasDefaulted = True

    @dataclass
    class Content:
        def __init__(self, type:str, value:Union[str, List[Path]]):
            self.type = type
            self.value = value
        
    
    def __init__(self, on_text, on_image, on_file):
        #Thread.__init__()
        self._on_text=on_text
        self._on_image=on_image
        self._on_files=on_file
        self.running = True
        self.hasDefaulted = False
        self.initiateConfig()
        self.checkStatus()
        print("clipboard thread started..")
        

    def _create_base_window(self) -> int:
        """
        Creates a window for listening to clipboard
        -----------
        return: window hwnd
        """
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = self._handle_message_from_clipboard
        wc.lpszClassName = self.__class__.__name__
        wc.hInstance = win32api.GetModuleHandle(None)
        class_atom = win32gui.RegisterClass(wc)
        return win32gui.CreateWindow(class_atom, self.__class__.__name__, 0, 0, 0, 0, 0, 0, 0, wc.hInstance, None)
    
    def _handler():
        print("handler")

    def run(self):
        print("Thread started!")

        hwnd = self._create_base_window()
        ctypes.windll.user32.AddClipboardFormatListener(hwnd)
        win32gui.PumpMessages()
           
    def _handle_message_from_clipboard(self, hwnd: int, msg: int, wparam: int, lparam: int):
        WM_CLIPBOARDUPDATE = 0x031D
        if msg == WM_CLIPBOARDUPDATE:
            print(msg)
            self._handle_clipboard_content()
        return 0

    def _handle_clipboard_content(self):
        """
        processes the clipboard content based on the file type
        """
        content = self.getClipboardContent()

        if content.type == 'text' and self._on_text:
            self._on_text(content.value)

        elif content.type == "image" and self._on_image:
            self._on_image(content.value)

        elif content.type == "files" and self._on_files:
            self._on_files(content.value)

    @staticmethod
    def getClipboardContent() -> Optional[Content]:
        """
        Checks the format of the copied content.
        Gets and returns the recently copied content
        ----------
        """
        try:
            wc.OpenClipboard()
            def checkFormat(format):
                if wc.IsClipboardFormatAvailable(format):
                    return wc.GetClipboardData(format)
                return 0
            if text:= checkFormat(wc.CF_UNICODETEXT):
                return ClipboardMonitor.Content('text', text)
                
            elif image:= checkFormat(wc.CF_BITMAP):
                return ClipboardMonitor.Content('image', image)
            
            elif files:= checkFormat(wc.CF_HDROP):
                return ClipboardMonitor.Content('files', [Path(file) for file in files])

            return None
            
        finally:
            wc.CloseClipboard()

    def disableClipboard(self):
        """
        Empties and disables the clipboard
        """
        # wc.EmptyClipboard()
        # win32api.RegSetValue()
        print("clipboard disabled")

    def enableClipboard(self):
        """
        Enables clipboard 
        """
        print("clipboard enabled")

    def initiateConfig(self):
        """ Creates and saves the logConfig file """

        config = dict()

        config["hasDefaulted"] = False
        config["time_defaulted"] = None
        config["copied_file_size"] = 0

        try:
            with open('logConfig', 'xb') as logConfig:
                pickle.dump(config, logConfig)
        except FileExistsError:
            print("log config file already exists")

    def loadLogConfig(self):
        """ Loads the log config for writing """

        with open('logConfig', 'rb') as logConfig:
            log_config = pickle.load(logConfig)
        return log_config

    def checkStatus(self):
        """ 
            Checks if the current user has defaulted by copying file size more than
            500 in one hour, or 1500 in 24 hours. 
            if yes, checks if it has been more than 24 hours.
            If more than 24 hours, enables the clipboard. If less, ensures the clipboard remain disabled.
        """
        if Path("logConfig").exists():
            config = self.loadLogConfig()
            if config["time_defaulted"]:
                seconds = datetime.timedelta(time.time() - config["time_defaulted"]).seconds
                if seconds:
                    time_elapsed_hour = seconds // 3600
                    #: if the user defaulted but 24 hours has passed, enable the clipboard
                    if config["hasDefaulted"] and time_elapsed_hour >= 24:
                        self.enableClipboard()
                    else:
                        #: Be sure the user has defaulted before disabling clipboard
                        if config["hasDefaulted"]:
                            self.disableClipboard() 

    def clearClipboard(self):
        wc.EmptyClipboard()
        wc.CloseClipboard()
        
if __name__=="__main__":
    clipboard = ClipboardMonitor(on_text=print, on_file=None, on_image=None)
    clipboard.run()
    clipboard.join()
    
  
        