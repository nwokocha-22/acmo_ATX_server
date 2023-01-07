import socket
import cv2
import numpy as np
import threading
from matplotlib import pyplot as plt
import base64
from PIL import Image

# Set up the UDP socket
UDP_IP = "0.0.0.0"  # Listen on all available interfaces
UDP_PORT = 5005
BUFFER = 1024*1024
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#sock.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFFER)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('', 5005))
#sock.bind((UDP_IP, UDP_PORT))

# Set up the video player
#cv2.namedWindow("Video", cv2.WINDOW_NORMAL)
#cv2.namedWindow('TRANSMITTING VIDEO') 
# Receive and display the video frames

### RE-OCCURING ERROR
"""
just incase you get this stuborn error for any reason:

OpenCV Error: Unspecified error (The function is not implemented. 
Rebuild the library with Windows, GTK+ 2.x or Carbon support. 
If you are on Ubuntu or Debian, install libgtk2.0-dev and pkg-config, 
then re-run cmake or configure script) in cvShowImage, 
file /io/opencv/modules/highgui/src/window.cpp, line 545

=======================
SOLUTION
------------------
: kindly uninstall opencv-python-headless
: uninstall opencv-python
: pip install opencv-python

"""
def receive_video():
    while True:
        # Receive a video frame from a client
        print("waiting to receive packet")
        packet, addr = sock.recvfrom(BUFFER)  # 1 MB buffer

        img = cv2.imdecode(np.frombuffer(packet, np.uint8), cv2.IMREAD_COLOR)
        title = f'{addr[0] if addr else "VIDEO"}'
        cv2.imshow(title, img)
       
        key = cv2.waitKey(1) & 0xFF
	
        if key == ord('q'):
            sock.close()
            break

# Start the video receiving thread
if __name__=="__main__":
    thread = threading.Thread(target=receive_video)
    thread.start()
    #receive_video()

# Wait for the thread to finish
#thread.join()

# Release the video player
cv2.destroyAllWindows()