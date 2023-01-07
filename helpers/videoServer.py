
import cv2, socket
import numpy as np
import time, os
import base64

BUFFER =1024*1024 #65536

BREAK = False
client_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
client_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFFER)
host_name = socket.gethostname()
host_ip = "0.0.0.0"  #socket.gethostbyname(host_name)
#print(host_ip)
#port = 9688
port = 5005
message = b'Hello'

#client_socket.sendto(message,(host_ip,port))

def video_stream():
	
	# cv2.namedWindow('RECEIVING VIDEO')        
	# cv2.moveWindow('RECEIVING VIDEO', 10, 360) 
	fps,st,frames_to_count,cnt = (0,0,20,0)
	while True:
		packet,_ = client_socket.recvfrom(BUFFER)
		data = base64.b64decode(packet,' /')
		npdata = np.fromstring(data,dtype=np.uint8)
	
		frame = cv2.imdecode(npdata, 1)
		frame = cv2.putText(frame,'FPS: '+str(fps),(10,40),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
		cv2.imshow("RECEIVING VIDEO",frame)
		key = cv2.waitKey(1) & 0xFF
	
		if key == ord('q'):
			client_socket.close()
			os._exit(1)
			break

		if cnt == frames_to_count:
			try:
				fps = round(frames_to_count/(time.time()-st))
				st=time.time()
				cnt=0
			except:
				pass
		cnt+=1
		
			
	client_socket.close()
	cv2.destroyAllWindows() 
if __name__=="__main__":
    video_stream()