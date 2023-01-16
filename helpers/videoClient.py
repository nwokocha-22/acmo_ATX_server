import socket
from threading import Thread
import cv2
import numpy as np
import pyautogui
import queue
import time


class SendVideo:

    BUFFER = 1024 * 1024

    def __init__(self, ip, port, password, sender, receiver):
        super().__init__(password, sender, receiver)
       
        self.address = (ip, port)
        self.queue = queue.Queue(20)
        print("video thread started")

    
    def send_data(self):
        # create a window with the with title of the client ip 
        print("sending data ...")
        
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock_udp:
            
            while True:
                try:
                    img = pyautogui.screenshot(region=(0,0, 300, 400))
                    self.queue.put(img)
                    frame = np.array(self.queue.get())
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    img_bytes = cv2.imencode('.jpg', frame)[1].tobytes()
                    sock_udp.sendto(img_bytes, self.address)
                except OSError as os_err:
                    print(os_err)

    def connect_to_server(self):
        """
        establishes a three way hand shake with the clients, and spawn a thread to send data
        to the connect client
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock_tcp:
                connected = False

                while not connected:
                    try:
                        sock_tcp.connect(self.address)
                        connected = True

                        print("connection established")
                    except Exception:
                        print("Unable to connect to server. Retrying...")
                    time.sleep(5)
                    
                while True:
                    sock_tcp.send(b"ready")
                    data = sock_tcp.recv(1024).decode()
                    print("response from server:", data)
                    if data == "shoot":
                        self.send_data()
        except ConnectionRefusedError:
            print("connection refused; confirm the server is active")
            
        
                   
# if __name__=="__main__":
#     IP = "127.0.0.1"
#     PORT = 5005
#     video_server = SendVideo(IP, PORT)
#     video_server.connect_to_server()