
import sys
import io
import time
import signal
import socket
import os
import ssl
import getpass
import zipfile
from datetime import datetime
from threading import Thread
from helpers.videoClient import SendVideo as Video
from helpers.emailClient import EmailClient as Email
from helpers.keyMouseActivity import KeyMouseMonitor as KeyMouse
from helpers.clipboardActivity import ClipboardMonitor as Clipboard
from helpers.activityLogger import ActivityLogger as Logger
from helpers.policy import CopyPolicy
from helpers.alarm_signal import timer
from pathlib import Path

import win32security
import win32api



class ActivityMonitor(Email, KeyMouse, CopyPolicy):
    """
    This script continously monitors user's activity by capturing video 
    of the user's screen, mouse and keyboard activities, and the content copied to clipboard.
    
    If the copy policy is violated, an email, which includes the IP address of the User's machine, 
    size of the file copied, the actual copied content, date and time, is sent to the chief administrator,
    
    As a result of this violation, the user's clipboard will be disabled for 24hours even after rebooth

    --------------------
    TRANSMITION OF CAPTURED VIDEO
    The captured video is transmitted to a remote server using a UDP socket

    --------------------
    TRANSMITION OF LOG
    Logged user activity (Keyboard and mouse) is instantly transmitted a remote server
    via the Logger socket formmatter

    --------------------
    Parents:
        :videoRecorder: a threaded class that captures the screen video frame in mpeg format
        :activityLogger: a class that logs the users activity every 10 minutes
        :emailClient: a class instance that handles sending emails to a recipient email when the user defaults on the content copy policy
        :ClipboardMonitor: a threaded class that monitors the clipboard. it fetches the content copied to clipboard so that its size can be estimate. 
    
    """

    _LOG_INTERVAL = 10

    def __init__(self, ip, port, password, sender, receiver):

        #: initialize the parent classes
        super().__init__()

        key_mouse = [0, 0]

        self.checkPolicyStatus()
        #self.detectLogin()
        self.user = socket.gethostbyname(socket.gethostname())
        self.ctx = ssl.create_default_context()

        self._copied_content_size = int()
        self._copied_content = str()

        #: when the user is logged in
        self._time_in = datetime.now().strftime("%d-%m-%Y, %H:%M:%S")
        #: when the user logged out.
        self._time_out = None
        
        self._1_hr_content_size = None
        self._24_hrs_content_size = None

        #: this values are accessed by the Email Parent class through cooperate inheritance
        self.ip = ip
        self.port = port
        self.password = password
        self.sender = sender
        self.receiver = receiver

    def start(self):
        """
        begin the monitoring processes -> Clipboard, Video, key and mouse
        """
        video =Video(self.ip, self.port)
        clipboard = Clipboard(on_text=self._on_text, on_image=self._on_image, on_file=self._on_file)
    
        t_timer_10_mins = Thread(target=self._setTimer, args=(self.logUserActivities, self._LOG_INTERVAL, 'sec'))
        t_timer_10_mins.start()

        _timer_1_hr = Thread(target=self._setTimer, args=(self.checkCopiedContent, 1, 'sec'))
        _timer_1_hr.start()

        t_video = Thread(target=video.connect_to_server())
        t_video.start()
        t_clip = Thread(target=clipboard.run())
        t_clip.start()

        t_timer_10_mins.join()
        t_video.join()
        t_clip.join() 

    def _on_text(self, text:str):
        """
        is triggered when text is copied to clipboard
        """
        #: check size of the copied content
        print("text copied")
        text_size = sys.getsizeof(text)
        self.invokeCopyPolicy(text_size, text, "text")

    def getSize_ZippedFiles(self, files):
        """
        gets the size of the copied file(s) and zips it
        """
        file_size = 0
        zip = zipfile.ZipFile("copiedFiles.zip", "w")

        try:
            for file in files:
                if not os.path.islink(file):
                    size = os.path.getsize(file)
                    file_size += round(size / 1000)
                    zip.write(file, compress_type=zipfile.ZIP_DEFLATED)
        except Exception as err:
            print(err)
        finally:
            zip.close()

        return file_size, zip
        
    def _on_file(self, files:io.FileIO):
        """
        is triggered when files are copied to clipboard
        """

        file_size, zipped_files = self.getSize_ZippedFiles(files)
        self.invokeCopyPolicy(file_size, zipped_files, "file")

    def _on_image(self, image):
        """
        is triggered when image(s) are copied to clipboard
        """
        image_size = sys.getsizeof(image)
        self.invokeCopyPolicy(image_size, image, "image")

    def invokeCopyPolicy(self, file_size, file, type):
        """
        Checks if the size of the copied file is more than five hundred. 
        if yes, invokes a disciplinary action
        Else, increment the _copied_content_size which is checked at the interval of 1 hour
        -----------------
        parameter:
            file_size: size of the copied file
        -----------------
        return: None
        """
        if type == "text":
            if file_size >= 500:
                self.invokeDisciplinaryAction(self.user, file_size, file, type)

            elif file_size + self._copied_content_size >= 500:
                updated_size = file_size + self._copied_content_size
                updated_content = file + self._copied_content
                self.invokeDisciplinaryAction(self.user, updated_size, updated_content, type)

            else:
                self.updateCopiedContent(file, file_size)

    def updateCopiedContent(self, content='', size=0, clear=False):
        """
        increment the copied content and content size each time 
        text file is copied
        """
        if clear:
            self._copied_content_size = 0
            self._copied_content = ''

        self._copied_content_size += size
        self._copied_content += "\n" + content

    def logActivity(self):
        """
        gets the number of keystrokes, mouse move, and the size of item copied to clipboard
        and logs the information
        """
        key_stroke = self._key_stroke_count
        #print("key stroke", key_stroke)

    def logTimer(self):
        """
        calls the log activity function every ten minutes
        """
        pass

    def checkCopiedContent(self):
        """
        checks the size of the copied content every hour.
        if greater than 500, calls the send method of the email client and sends
        all content copied up until that time.
        """
        #print("checking content copied!") 
        
        if self._copied_content_size >= 500:
            self.invokeDisciplinaryAction(self._copied_content_size, self._copied_content, )
        else:
            self.updateCopiedContent(clear=True)

    def logUserActivities(self):
        """
        logs the users keystr oke and mouseMove activities every 10 minutes
        """
        print("logging key mouse activity")
        status = "active"

        keystroke, mouseMove= self.getAverage(60 * self._LOG_INTERVAL)
    
        print(keystroke, mouseMove)

        if not keystroke and not mouseMove:
            status = "idle"

        #print(f"keystroke:{keystroke}, mouseMoves:{mouseMove}, status:{status}")
        
    def disable_clipboard(self, disable=False):
        """
        Disables the clipboard for 24 hours
        """                                                                            
        print("keyboard is disabled; can't copy file")
        

    def invokeDisciplinaryAction(self, file_size, file, file_type=None):
        """
        This is called when the copy policy is violiated. It sets the users hasDefaulted status
        to True, set the time of violation, and triggers the function to disable clipboard
        for 24hours
        """
        time = datetime.now().strftime("%d-%m-%Y - %H:%M:%S")

        self.updatePolicy(hasDefaulted=True, timeDefaulted=time)
        self.disable_clipboard(True)

        if file_type == "text":
            self.send_email(self.user, file_size, file)
        else:
            #: send files as attachment if not text (i.e for bytes and images)
            self.send_email(self.user, file_size, "see attached zipped file(s)", file)

    def handle_time_elapsed_signal(self, signum, frame):
        """
        a signal handler function that is called when the 24 hours in which the clipboard is 
        disabled is up
        """
        if self.hasDefaulted:
            self.hasDefaulted = False
        else:
            self.hasDefaulted = True

    def estimateTime(self, signum, frame):
        """
        Estimates the number of time the user is idle
        """
        print("sig num", signum, os.getpid())

        #: kill the process that emits the signal -> SIGPROF

    def _terminateScript(self):
        """
         terminates the script when a User is logged out of the remote Machine
        """
        os.kill(os.getpid(), signal.SIGPROF)

    def _autoStartScript(self):
        """
        - starts the script when a User is logged in
        """
        os.startfile("core.exe")

    def autostartProgram(name, location):
        """ 
        Automatically start the script when a User is logged in
        """
        os.system(r"reg add HKCU\software\microsoft\windows\currentversion\run /v%s /t REG_SZ /d %s" % (name, location) )

    @staticmethod
    @timer
    def _setTimer(callback, interval, mode):

        """
        sets the alarm interval.the callback function is called on the expiration of the interval 
        -------------
        parameter:
            :callback: a function that is called when the interval alapses
            :interval: the duration for the alarm
            :mode: the time frame i.e either sec, min, or hour
        """
        print("timer started") 

    @staticmethod
    @timer
    def _setTimer(callback, inteval, mode):
        print("alarm triggeed!")


    # def detectLogin(self):
    #     user = win32api.GetUserName()
    #     print("user--", user)
    #     events = win32security.GetSystemSecurityInfo(win32security.SE_SECURITY_DESCRIPTOR).AuditEvents
      
    #     if events & win32security.EVENTLOG_SUCCESS:
    #         print(f"{user} has logged in.")
    #         pass
    #     else:
    #         pass
    #         print("No login event detected.")


        
if __name__=="__main__":
    import os
    # import win32net, time
    # users,nusers,_ = win32net.NetUserEnum(None,2)
    # for user in users:
    #     print(user["name"], time.ctime(user["last_logon"]) )
        
    # print("user:", os.getlogin())
    # current_user = getpass.getuser()

    ip = "127.0.0.1" 
    port = 5005 

    password = os.environ["PASSWORD"] 
    sender = os.environ["SENDER"]
    receiver = os.environ["RECEIVER"]
   
    monitor = ActivityMonitor(ip, port, password, sender, receiver) 

    monitor._setTimer(monitor.caller2, 10, 'sec')
    
    

    
    