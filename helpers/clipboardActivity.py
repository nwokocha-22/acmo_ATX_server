
from typing import Union, List, Optional
import win32clipboard as wc
from pathlib import Path
from dataclasses import dataclass
import win32gui
import  win32api
import ctypes
import socket
from threading import Thread
from .policy import CopyPolicy
   
@dataclass
class ClipboardMonitor:

    """
    Extends the copy policy class and monitors the clipboard
    """
    #: when the main script is started, checks if the user has defaulted
    policy = CopyPolicy().policy
    hasDefaulted = policy["hasDefaulted"]
    
    @dataclass
    class Content:
        def __init__(self, type:str, value:Union[str, List[Path]]):
            self.type = type
            self.value = value
        
    
    def __init__(self, on_text, on_image, on_file, ip, port, password, sender, receiver):
       
        self._on_text=on_text
        self._on_image=on_image
        self._on_files=on_file

        self.user = socket.gethostbyname(socket.gethostname())

        self._copied_content_size = int()
        self._copied_content = str()

        #: args passed on to sibling classes -> Video(ip, port) -> Email(password, sender, receiver)
        super().__init__(ip, port, password, sender, receiver)
        
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

    def run_clipboard_listener(self):
        print("Clipthread started!")

        hwnd = self._create_base_window()
        ctypes.windll.user32.AddClipboardFormatListener(hwnd)
        win32gui.PumpMessages()
        #input()
       
           
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
        try:
            if content:
                if content.type == 'text' and self._on_text:
                    self._on_text(content.value)

                elif content.type == "image" and self._on_image:
                    self._on_image(content.value)

                elif content.type == "files" and self._on_files:
                    self._on_files(content.value)
        except Exception as err:
            print(err)

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
                    print("default status:", ClipboardMonitor.hasDefaulted)
                    if ClipboardMonitor.hasDefaulted:
                        ClipboardMonitor.clearClipboard()
                        print("has default")
                        return None
                    else:
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
            pass
            #wc.CloseClipboard()

    def disableClipboard(self):
        """
        Empties and disables the clipboard
        """
        self.hasDefaulted = True
        self.clearClipboard()

    def enableClipboard(self):
        """
        Enables clipboard 
        """
        print("clipboard enabled")

    @staticmethod
    def clearClipboard():
        print("Unauthorized, clipboard disabled!")
        wc.OpenClipboard(None)
        wc.EmptyClipboard()
        #wc.CloseClipboard()

        #ctypes.windll.user32.OpenClipboard(None)
        #ctypes.windll.user32.EmptyClipboard()
        #ctypes.windll.user32.CloseClipboard()

# if __name__=="__main__":
#     clipboard = ClipboardMonitor(on_text=print, on_file=None, on_image=None)
#     clipboard.run()
#     clipboard.join()
    
  
        