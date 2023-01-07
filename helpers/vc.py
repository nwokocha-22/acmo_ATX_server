import socket
import pyautogui
import cv2
import numpy as np
import base64
import queue

# Set up the UDP socket
UDP_IP = "127.0.0.1"  # Local host
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
q = queue.Queue(maxsize=10)
# Set up the video writer
fourcc = cv2.VideoWriter_fourcc(*'MJPG')
out = cv2.VideoWriter('output.avi', fourcc, 30.0, (1920, 1080))

# Capture and send the video frames
while True:
    # Capture a screenshot
    img = pyautogui.screenshot(region=(0,0, 300, 400))
    q.put(img)
    # Convert the image to a video frame
    #print("screen shot", img)
    frame = np.array(q.get())
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    
    # Write the frame to the video file
    out.write(frame)
    
    # Encode the frame into a JPEG image
    
    try:

        img_bytes = cv2.imencode('.jpg', frame)[1].tobytes()
        #encoded, buffer = cv2.imencode('.jpeg',frame,[cv2.IMWRITE_JPEG_QUALITY, 80])
    
        #message = base64.b64encode(bytes(buffer))
        
        # Send the image over the UDP socket
        sock.sendto(img_bytes, (UDP_IP, UDP_PORT))
    except Exception as err:
        print(err)