
import cv2
import pyautogui
import numpy
from threading import Thread

class VideoCapture(Thread):
    """
    captures the system screen and transmits the video to another server
    """

    def __init__(self):
        Thread.__init__(self)
        self.videoFile = self.createVideoObject()

    def createVideoObject(self):
        """
        Creates the video object to which  the captured image frame will be written
        """
        resolution = (1920, 1080)
        codec = cv2.VideoWriter_fourcc(*"XVID")
        file_name = "user_activity.avi"
        fps = 60.0
        return cv2.VideoWriter(file_name, codec, fps, resolution)

    def captureScreen(self):
        """
        captures the screen of the user
        -----------
        Return: Frame
            returns frame that is to be writen into a video object using video writer
        """
        screenshot = pyautogui.screenshot()
        frame = numpy.array(screenshot)
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def saveVideo(self, video, frame):
        """
        Writes the captured video frame into the video object
        """
        video.write(frame)
        return video
        
    def transmitVideo(self):
        """
        Transmits the captured video frame to a remote server
        """
        while True:
            frame = self.captureScreen()
            if not frame.any():
                break
            video = self.saveVideo(self.videoFile, frame)

            #:  SEND VIDEO FRAME VIA SOCKET TO REMOTE SERVER

        self.videoFile.release()