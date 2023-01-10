
import sys
import io
import time
import socket
import os
import zipfile
from helpers.videoClient import SendVideo as Video
from helpers.emailClient import EmailClient as Email
from helpers.keyMouseActivity import KeyMouseMonitor as KeyMouse
from helpers.clipboardActivity import ClipboardMonitor as Clipboard


class ActivityMonitor(Video, Email, KeyMouse, Clipboard):
    """
    A script that continously monitors the user's activity by capturing video 
    of the screen and logs all the processes of the user activities.

    -   If the user copies more than 500 characters an hour, 
        or 1500 characters a day in total, then we get emails with the copied content,

    -   and using the clipboard is disabled for 24 hours (even after reboot, etc). 

    ---------------------
    params:
        :videoRecorder: a threaded class that captures the screen video frame in mpeg format
        :activityLogger: a class that logs the users activity every 10 minutes
        :emailClient: a class instance that handles sending emails to a recipient email when the user defaults on the content copy policy
        :ClipboardMonitor: a threaded class that monitors the clipboard. it fetches the content copied to clipboard so that its size can be estimate. 
    
    """

    _LOG_INTERVAL = 10

    def __init__(self, ):

        self.user = socket.gethostbyname(socket.gethostname())

        #: start the clipboard monitoring on a separate thread
        #self.clipMonitor = ClipboardMonitor(on_text = self.on_text, on_file=self.on_file, on_image=self.on_image)
        #self.clipMonitor.start()

        self._copied_content_size = int()
        self._copied_content = str()

        self._time_in = None
        self._time_out = None
        
        self._1_hr_content_size = None
        self._24_hrs_content_size = None
        
    

    def on_text(self, text:str):
        """
        is triggered when text is copied to clipboard
        """
        #: check size of the copied content
        text_size = sys.getsizeof(text)
        self.checkFileSize(text_size, text, "text")

    def getSize_ZippedFiles(self, files):

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
        
    def on_file(self, files:io.FileIO):
        """
        is triggered when files are copied to clipboard
        """
        # file_size = 0
        
        # def getFile(path):
        #     """
        #     gets the files size
        #     """
        #     try:
        #         if not os.path.islink(path):
        #             file_size = os.path.getsize(path)
        #             return round(file_size / 1000)
        #     except Exception as err:
        #         print(err)
                
        # for file in files:
        #     file_size += getFile(file)
            
        # ZipFile = zipfile.ZipFile("copiedFiles.zip", "w")
        
        # for file in files:
        #     ZipFile.write(file, compress_type=zipfile.ZIP_DEFLATED)
        # # except FileNotFoundError:
        # #     print(f"{os.path.basename(file)} not found")
            
        # # finally:
        # ZipFile.close()

        file_size, zipped_files = self.getSize_ZippedFiles(files)
        print("file, zip", file_size, zipped_files)

        self.checkFileSize(file_size, zipped_files, "file")

    def on_image(self, image):
        """
        is triggered when files are copied to clipboard
        """
        image_size = sys.getsizeof(image)
        self.checkFileSize(image_size, image, "image")

    def checkFileSize(self, file_size, file, type):
        """
        Checks if the size of the copied file is more than five hundred. if yes, calls the notify function.
        Else, add it to the self._copied_content_size global variable which is checked at the interval of 1 hour
        -----------------
        parameter:
            file_size: size of the copied file
        -----------------
        return: None
        """
        print(f"file size: {file_size}\ncontent: {file}\n type: {type}")
      
        print(dir(self.emailClient))
       

        if file_size >= 50:
            if type == "text":
                #: omits attachment for test files
                self.emailClient.sent_email(self.user, file_size, file)
                pass
            else:
                #: send files as attachment if not text (i.e for bytes and images)
                self.emailClient.send_email(self.user, file_size, "see attached zipped file(s)", file)
                pass
        else:
            self._copied_content_size += file_size
            print("copied file size less than 500")

    def logActivity(self):
        """
        gets the number of keystrokes, mouse move, and the size of item copied to clipboard
        and logs the information
        """
        key_stroke = self._key_stroke_count
        print("key stroke", key_stroke)

    def logTimer(self):
        """
        calls the log activity function every ten minutes
        """
        while True:
            self.logActivity()
            time.sleep(5)

    def checkCopiedContent(self):
        """
        checks the size of the copied content every hour.
        if greater than 500, calls the send method of the email client and sends
        all content copied up until that time.
        """
        print("content copied!")
        
        if self._copied_content_size >= 500:
            # Send notification
            print("Notification sent!")
            pass

        self._copied_content.clear()


    def disable_clipboard(self):
        """
        Disables the clipboard for 24 hours
        """
        pass
    
    def estimateIdleTime(self, keyboard_stroke_count, mouse_count):
        """
        Estimates the number of time the user is idle
        """
        pass

    
        


if __name__=="__main__":

    # from activityLogger import ActivityLogger
    # from emailClient import EmailClient 
   
    # password = os.environ["PASSWORD"]
    # sender = os.environ["SENDER"]
    # receiver = os.environ["RECEIVER"]
    # path = Path.joinpath(Path.cwd(), "autotest", "data", "activityLog.txt")

    # emailClient = EmailClient(password, sender, receiver)
    # video_recorder = VideoCapture()
    # activityLogger = ActivityLogger(path)
    
    # emailClient.start()
    # video_recorder.start()
    # activityLogger.start
    

    #monitor = ActivityMonitor(video_recorder, activityLogger, emailClient)  

    # k = Thread(target=monitor.keyMonitor)
    # m = Thread(target=monitor.mouseMonitor)
    
    # k.start()
    # m.start()
    
    pass

    
    