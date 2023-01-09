import socket
from threading import Thread
import cv2
import numpy as np
import pyautogui
import queue


class SendVideo:

    BUFFER = 1024 * 1024
    def __init__(self, host, port):
        self.address = (host, port)
        self.queue = queue.Queue(20)
      

    def send_data(self):
        # create a window with the with title of the client ip 
        print("sending data ...")
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock_udp:
            while True:
                img = pyautogui.screenshot(region=(0,0, 300, 400))
                self.queue.put(img)
                frame = np.array(self.queue.get())
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                try:
                    img_bytes = cv2.imencode('.jpg', frame)[1].tobytes()
                    sock_udp.sendto(img_bytes, self.address)
                except Exception as err:
                    print(err)

    def connect_to_server(self):
        """
        establishes a three way hand shake with the clients, and spawn a thread to send data
        to the connect client
        """
	
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock_tcp:
            sock_tcp.connect(self.address)
            print("connected to server!")
            while True:
                sock_tcp.send(b"ready")
                data = sock_tcp.recv(1024).decode()
                print("response from server:", data)
                if data == "shoot":

                    self.send_data()
               
        
                   
if __name__=="__main__":
    IP = "127.0.0.1"  
    PORT = 5005
    video_server = SendVideo(IP, PORT)
    video_server.connect_to_server()