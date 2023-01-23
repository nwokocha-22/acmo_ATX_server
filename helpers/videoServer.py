import socket
from threading import Thread
import cv2
import numpy as np
from datetime import datetime
from pathlib import Path
import os



class ReceiveVideo:

	BUFFER:int = 1024 * 1024 * 1024
	FPS:int = 30
	size:tuple = (720, 450)
	date:datetime = datetime.now()

	print(date)

	def __init__(self, host, port):
		self.port = port
		self.address = (host, port)

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
	
		print("receiving data...")
		
		#: create a video player with a title of the client's ip address
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
					#video_file.write(frame)

					#: display the frame
					cv2.imshow(title, frame)
					key = cv2.waitKey(1) & 0xFF

				if key == ord('q'):
					sock_udp.close()
					break

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

				video_file = self.get_videio_file(addr[0])

				data = client.recv(1024).decode()

				print("message from client:", data)
				if data == "ready":
					client.send(str.encode("shoot"))
					thread = Thread(target=self.recv_data, args=(addr[0], video_file))
					thread.start()
					print("exited thread")

	def create_dir(self, client_ip):
		"""
		Creates the path where to save the video file if it doesn't exist yet
		----------------
		parameter:
			:client_ip: the ip of the client
		----------------
		return: 
			Path: the path where the video file is saved
		"""
		month = datetime.today().strftime("%B")
		root_folder = Path("C:/Activity Monitor")
		try:
			path = Path.joinpath(root_folder, client_ip, f"{month}", "Videos")
			if path.exists():
				return path
			else:
				os.makedirs(path)
				return path
		except FileNotFoundError as err:
			print(err)
			

	def create_video_file(self, filename:None, path):
		"""
		creates the video file using the path
		----------------
		Parameter:
			:filename: the file. creates a name with today's day if filename is not provide
			:path: the parent path to the file. this is joined with the filename to create the absolute path
		----------------
		Return:
			:video_file: the videoWriter object where the video frame received from the client will be written
			:file_path: the path where the video is saved
		"""
		if filename is None or not filename.endswith(".mkv"):
			filename = f"{datetime.now().strftime('%d-%m-%Y')}.mkv"

		today = datetime.today().strftime("%d-%m-%Y")
		sub_dir = "Screen Recordings"
		filefolder = f'{today}-screen-recording'

		file_path = Path.joinpath(path, sub_dir, filefolder, filename)
	
		FPS = 30
		# SIZE= (720, 450)
		# FOURCC = cv2.VideoWriter_fourcc(*'MJPG')

		#SIZE = (1920, 1080)
		SIZE = (300, 400)
		FOURCC = cv2.VideoWriter_fourcc(*"XVID")
        #file_name = "user_activity.avi"

		video_file = cv2.VideoWriter(str(file_path), FOURCC, FPS, SIZE)

		return video_file, file_path
			
	
	def get_videio_file(self, ip):
		"""
		gets the created video file
		---------------
		Parameter:
			ip: client's ip
		"""
		path = self.create_dir(ip)
		video, _ = self.create_video_file("video", path)
		return video



		
