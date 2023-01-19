
import sys
import io
import time
import os
import ssl
import zipfile
from threading import Thread
from datetime import datetime, timedelta
from helpers.videoClient import SendVideo as Video
from helpers.emailClient import EmailClient as Email
from helpers.keyMouseActivity import KeyMouseMonitor as KeyMouse
from helpers.clipboardActivity import ClipboardMonitor as Clipboard
from helpers.logger import keyMouseLogger, clipboardLogger
from helpers.policy import CopyPolicy
from helpers.alarm_signal import timer


class ActivityMonitor(Clipboard, Video, Email, KeyMouse, CopyPolicy):
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
    _copied_content_limit = 500 # KB

    def __init__(self, ip, port, password, sender, receiver):

        #: initialize the parent classes
        super().__init__(self._on_text, self._on_image, self._on_file, ip, port, password, sender, receiver)

        self.key_mouse = [0, 0]

        #self.checkPolicyStatus()
        #self.detectLogin()
        #self.user = socket.gethostbyname(socket.gethostname())
        self.ctx = ssl.create_default_context()

        # self._copied_content_size = int()
        # self._copied_content = str()

        #: when the user is logged in
        self._time_in = datetime.now().strftime("%d-%m-%Y, %H:%M:%S")
        print("time in", self._time_in)
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
        
        clipboard_thread = Thread(target=self.run_clipboard_listener)
        clipboard_thread.start()

        video_thread = Thread(target=self.connect_to_server)
        video_thread.start()

        #: Log user mouse and keyboard activities every 10 minutes
        timer_thread = Thread(target=self._setTimer, args=(self.logUserActivities, self._LOG_INTERVAL, 'min'))
        timer_thread.start()

        #: check the policy status every 1 hour
        timer_hr_thread = Thread(target=self._setTimer, args=(self.checkPolicyStatus, 1, 'hour'))
        timer_hr_thread.start()

        clipboard_thread.join()
        video_thread.join()
        timer_thread.join()
        timer_hr_thread.join()

    def _on_text(self, text:str):
        """
        is triggered when text is copied to clipboard
        """
        #: check size of the copied content
        
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

    def invokeCopyPolicy(self, file_size, file, file_type):
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

        print("policy invoked")

        message = f"Activity: copy, file size: {file_size} KB, file type: {file_type}"
        clipboardLogger.info(message)

        if file_type == "text":
            if file_size >= self._copied_content_limit:
                self.invokeDisciplinaryAction(file_size, file, file_type)

            elif file_size + self._copied_content_size >= self._copied_content_limit:
                updated_size = file_size + self._copied_content_size
                updated_content = file + self._copied_content
                self.invokeDisciplinaryAction(updated_size, updated_content, file_type)

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

        print("copied content size:", self._copied_content_size)


    def checkCopiedContent(self):
        """
        checks the size of the copied content every hour.
        if greater than 500, calls the send method of the email client and sends
        all content copied up until that time.
        """
        if self._copied_content_size >= 500:
            self.invokeDisciplinaryAction(self._copied_content_size, self._copied_content, "text")
        else:
            self.updateCopiedContent(clear=True)
        

    def logUserActivities(self):
        """
        logs the users keystr oke and mouseMove activities every 10 minutes
        """
        status = "active"

        keystroke, k = self._key_stroke_count, self._key_stroke_count - self.key_mouse[0]
        mouseMove, m = self._mouse_move_count, self._mouse_move_count - self.key_mouse[1]

        print(keystroke, k, mouseMove, m)
        if keystroke == 0 and mouseMove == 0:
            status = "idle"

        self.key_mouse[0] = keystroke   
        self.key_mouse[1] = mouseMove
        
        print("activity logged")
    
        message = f"keystroke:{k}, mouseMoves:{m}, status:{status}"
        keyMouseLogger.info(message)

        
    def invokeDisciplinaryAction(self, file_size, file, file_type):
        """
        This is called when the copy policy is violiated. It sets the users hasDefaulted status
        to True, set the time of violation, and triggers the function to disable clipboard
        for 24hours
        """
        print("deciplinary actiion invoked!")
        #time = datetime.now().strftime("%d-%m-%Y - %H:%M:%S")
        
        if file_type == "text":
            self.send_email(self.user, file_size, file)
        else:
            #: send files as attachment if not text (i.e for bytes and images)
            self.send_email(self.user, file_size, "see attached zipped file(s)", file)

        if not self.hasDefaulted:
            self.updatePolicy(True, time.time())
            self.disableClipboard()

    def checkPolicyStatus(self):
        """ 
        - Checks the time elapsed since the copy policy was violated.

        - When Script is started, checks if the current user has defaulted by copying file size more than
          500 in one hour, or 1500 in 24 hours. 
          if yes, checks if it has been more than 24 hours.
          If more than 24 hours, enables the clipboard. If less, ensures the clipboard remain disabled.
        
        """
        if self.hasDefaulted:

            default_time = self.policy["timeDefaulted"]
            current_time = time.time()
            print(default_time, current_time)
            time_elapsed_seconds = timedelta(time.time() - self.policy["timeDefaulted"]).seconds
            
            if time_elapsed_seconds:
                time_elapsed_hour = time_elapsed_seconds // 3600

                if time_elapsed_hour >= 24:
                    self.updatePolicy()
                   
                else:
                    
                    print("clipboard disabled. elapse time:", time_elapsed_hour)
                   
        pass
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
    PASSWORD="ituqxqmjipuschlo"
    SENDER="nwokochafranklyn@gmail.com"
    RECEIVER="maruche.nwokocha@gmail.com"
    password = PASSWORD #os.environ["PASSWORD"] 
    sender = SENDER#os.environ["SENDER"]
    receiver = RECEIVER#os.environ["RECEIVER"]
   
    monitor = ActivityMonitor(ip, port, password, sender, receiver) 



   # monitor._setTimer(monitor.caller2, 10, 'sec')
    
    

    
    # async def main():
    #     ip = "127.0.0.1" 
    #     port = 5005 

    #     password = os.environ["PASSWORD"] 
    #     sender = os.environ["SENDER"]
    #     receiver = os.environ["RECEIVER"]
   
    #     monitor = ActivityMonitor(ip, port, password, sender, receiver)

    #     await asyncio.gather(
            
    #         monitor.video_client_connection(),
    #         monitor.clipboard_pump_messages(),
    #         monitor.run_timer()
    #     )

    # asyncio.run(main())
