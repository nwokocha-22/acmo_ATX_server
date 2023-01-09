import socket
from threading import Thread
import cv2
import numpy as np
from datetime import datetime
from pathlib import Path
import os


class ReceiveVideo:

	BUFFER:int = 1024 * 1024
	FPS:int = 30
	size:tuple = (720, 450)
	date:datetime = datetime.now()

	print(date)

	def __init__(self, host, port):
		self.port = port
		self.address = (host, port)
		fourcc = cv2.VideoWriter_fourcc(*'MJPG')
		self.filename = f'{self.date}-screen-recording.mkv'
		self.video_file = cv2.VideoWriter(self.filename, fourcc, self.FPS, self.size)


	def processImg(self, sock, ip):
		while True:
			packet, addr = sock.recvfrom(self.BUFFER) # 1 MB buffer
			client_ip = addr[0]

			#: stream the data from that particular client
			if client_ip == ip:
				img = cv2.imdecode(np.frombuffer(packet, np.uint8), cv2.IMREAD_COLOR)
				title = f'{client_ip if addr else "VIDEO"}'
				cv2.imshow(title, img)
				key = cv2.waitKey(1) & 0xFF
				if key == ord('q'):
					sock.close()
					break

	def recv_data(self, client_ip, video_file):
		# create a window with the with title of the client ip 
		print("receiving data...")
		cv2.namedWindow(client_ip, cv2.WINDOW_NORMAL)

		with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock_udp:
			sock_udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			sock_udp.bind(('', self.port))
			while True:
				packet, addr = sock_udp.recvfrom(self.BUFFER) # 1 MB buffer
				
				#: stream the data from that particular client
				if client_ip == addr[0]:
					frame = cv2.imdecode(np.frombuffer(packet, np.uint8), cv2.IMREAD_COLOR)
					title = f'{client_ip if addr else "VIDEO"}'

					#. write frame to video File:
					video_file.write(frame)
					cv2.imshow(title, frame)
					key = cv2.waitKey(1) & 0xFF

				if key == ord('q'):
					sock_udp.close()
					break
				
		# thread = Thread(target=processImg, args=(sock_udp, addrs[0]))
		# thread.start()

		#: release the video file
		video_file.release()

	def connect(self):
		"""
		establishes a three way hand shake with the clients, and spawn a thread to send data
		to the connect client
		"""
	
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock_tcp:
			sock_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			sock_tcp.bind(self.address)
			sock_tcp.listen(5)
			
			while True:
				#: waiting for a client to connect
				print("waiting for a new connection")
				client, addr = sock_tcp.accept()
				print("connected to:", client)

				#: create_dir(addr[0])
				filepath = self.create_dir(addr[0], self.date.month, self.filename)
				data = client.recv(1024).decode()

				print("message from client:", data)
				if data == "ready":
					client.send(str.encode("shoot"))
					thread = Thread(target=self.recv_data, args=(addr, filepath))
					thread.start()
					print("exited thread")

	def create_dir(self, client_ip, month, filename):
		#: if video recoring folder exists, open it, else create it
		#: if existing folder for the current month, open it, else create it
		#: if video_recoding for today, open it, else create it
		#: write streamed frame to video_file

		path = Path("C:\Recorded Videos")/client_ip/month/f'{self.date}-screen-recording.mkv'
		#: check if Recorded Videos folder exists in the local drive dir
		if not path.exists():
			return Path.mkdir(dir)

		else:
			#: if the folder exits, navigate to it.
			#: if there is a folder for the client, navigate to it
			#: if there is a folder for the current month, navigate to it
			#: if there is a file for the current day, wirte to it, else create it
			
			folders = path.glob(ip)
			folder = [for folder in path.iterdir() if folder.name == ip][0]

		return file_dir

	def save_video(self, frame):
		pass

if __name__=="__main__":
	#IP = socket.gethostbyname(socket.gethostname())
	IP = "127.0.0.1"
	print("IP", IP)
	PORT = 5005
	video_server = ReceiveVideo(IP, PORT)
	video_server.connect()
		
