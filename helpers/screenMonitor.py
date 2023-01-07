
import cv2
import pyautogui
import numpy
from threading import Thread
import socket
import cv2
from concurrent.futures import ThreadPoolExecutor
import socket
import numpy as np
import time
import base64

import queue
import os

class VideoCapture:
    """
    captures the system screen and transmits the video to another server
    """
    BUFF_SIZE = 65536
    FPS = 60.0

    def __init__(self, host_ip, port, isActive):
        #Thread.__init__(self)
        self.videoFile = self.createVideoObject()
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.BUFF_SIZE)
        socket_address = (host_ip, port)
        self.server_socket.bind(socket_address)
        self.isActiveUser = isActive
        self.queue = queue.Queue(maxsize=10)


    def createVideoObject(self):
        """
        Creates the video object to which  the captured image frame will be written
        """
        resolution = (1920, 1080)
        codec = cv2.VideoWriter_fourcc(*"XVID")
        file_name = "user_activity.avi"
       
        return cv2.VideoWriter(file_name, codec, self.FPS, resolution) 

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

    def video_stream_gen(self):
   
        WIDTH=400
        while self.isActiveUser:
            try:
                frame = self.captureScreen()
                #frame = imutils.resize(frame, width=WIDTH)
                self.queue.put(frame)
            except:
                os._exit(1)

        print('Player closed')
        BREAK=True
        
        
    def transmitVideo(self):
        """
        Transmits the captured video frame to a remote server
        """
        # while True:
        #     frame = self.captureScreen()
        #     if not frame.any():
        #         break
        #     video = self.saveVideo(self.videoFile, frame)

        #     #:  SEND VIDEO FRAME VIA SOCKET TO REMOTE SERVER

        # self.videoFile.release()
        # def video_stream():
	
        global TS
        fps,st,frames_to_count,cnt = (0,0,1,0)
        # cv2.namedWindow('TRANSMITTING VIDEO')        
        # cv2.moveWindow('TRANSMITTING VIDEO', 10,30) 
        while True:
            msg, client_addr = self.server_socket.recvfrom(self.BUFF_SIZE)
            print('GOT connection from ',client_addr)
            WIDTH=400
            
            while self.isActiveUser:
                frame = self.queue.get()
                encoded, buffer = cv2.imencode('.mpeg', frame, [cv2.IMWRITE_JPEG_QUALITY,80])
                message = base64.b64encode(buffer)
                self.server_socket.sendto(message, client_addr)
                frame = cv2.putText(frame,'FPS: '+str(round(fps,1)),(10,40),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
                if cnt == frames_to_count:
                    try:
                        fps = (frames_to_count/(time.time()-st))
                        st=time.time()
                        cnt=0
                        if fps>self.FPS:
                            TS+=0.001
                        elif fps<self.FPS:
                            TS-=0.001
                        else:
                            pass
                    except:
                        pass
                cnt+=1
                
                cv2.imshow('TRANSMITTING VIDEO', frame)
                key = cv2.waitKey(int(1000*TS)) & 0xFF	
                if key == ord('q'):
                    os._exit(1)
                    TS=False
                    break	

if __name__=="__main__":
    import socket
    host_ip = socket.gethostbyname(socket.gethostname())
    port = 57170
    isActive = True
    video =VideoCapture(host_ip, port, isActive)
    with ThreadPoolExecutor(max_workers=2) as executor:
	    executor.submit(video.transmitVideo)