import socket
import threading
import cv2
import numpy as np
from datetime import datetime
from pathlib import Path
import os
import random
from string import ascii_letters
i =0
class StreamVideo(threading.Thread):
	"""
		Receives the video frame comming from the connected client
		and saves the video file at a directory
	"""
	print(" ==VIDEO  STREAM STARTED== ")
	BUFFER:int = 65536
	FPS:int = 60
	# self.size = (720, 480)
	size:tuple = (320, 240)
	date:datetime = datetime.now()

	def __init__(self, client_ip,server_port, video_file, **kwargs):

		self.ip = client_ip
		self.server_port = server_port
		self.video_file = video_file

		super(StreamVideo, self).__init__(**kwargs)

	def run(self):
		thread = threading.Thread(target= self.recv_video_frame)
		thread.start()

	def recv_video_frame(self):
		"""
		Establishes a connection to the client through a UDP socket, 
		receives the video frame transmitted by the client.

		"""
		print("receiving data...")
		global i
		#: create a video player with a title of the client's ip address
		video_window_name = f"{self.ip}-{i}"
		cv2.namedWindow(video_window_name, cv2.WINDOW_NORMAL)
		i += 1
		with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock_udp:
			sock_udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, self.BUFFER)
			#sock_udp.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.BUFFER)
			
			sock_udp.bind(('', self.server_port))
			
			while True:
				#: Receive the data from the client
				packet, addr = sock_udp.recvfrom(self.BUFFER) # 1 MB buffer
				# Terminates loop if the client is no longer active
				
				if packet == None:
					break

				#: stream the data from a particular client
				#: check if the video frame received is comming from the client connected to this thread
				if self.ip == addr[0]:
					frame = cv2.imdecode(np.frombuffer(packet, np.uint8), cv2.IMREAD_COLOR)
					title = f'{self.ip if addr else "VIDEO"}'

					#. write frame to video File:
					self.video_file.write(frame)
					#video_file.write(frame)

					#: display the frame
					cv2.imshow(video_window_name, frame)
					key = cv2.waitKey(1) & 0xFF

				if key == ord('q'):
					sock_udp.close()
					break

		#: release the video file
		self.video_file.release()

class VideoServer(threading.Thread):
	print(" VIDEO SERVER STARTED ")
	connected_clients = []

	def __init__(self, server_ip, server_port, **kwargs):
		self.server_ip = server_ip
		self.server_port = server_port
		super(VideoServer, self).__init__(**kwargs)

	def run(self):
		self.connect()

	def connect(self):
		"""
		establishes a three way hand shake with the clients, and spawn a thread to send data
		to the connect client through a udp socket
		"""
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock_tcp:
			sock_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			#sock_tcp.bind(self.address)
			sock_tcp.bind((self.server_ip, self.server_port))
			sock_tcp.listen(5)
			
			while True:
				#: waiting for a client to connect
				print("waiting for a new connection")

				client, addr = sock_tcp.accept()
				client_ip, _ = addr
				print("connected to:", client)
				#: once a new client is connected, create a video file using the client ip
				video_file = self.get_video_file(client_ip)

				data = client.recv(1024).decode()

				print("message from client:", data)

				if data == "ready":
					client.send(str.encode("shoot"))
					video_stream_thread = StreamVideo(client_ip, self.server_port, video_file)
					video_stream_thread.start()
					self.connected_clients.append(video_stream_thread)

				print(f"{len(self.connected_clients)} clients connected")

				for thread in self.connected_clients:
					thread.join()

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
		
		try:
			root_folder = Path("C:/Activity Monitor")
			month = datetime.today().strftime("%B")
			path = Path.joinpath(root_folder, client_ip, f"{month}", "Videos")
			if path.exists():
				return path
			else:
				os.makedirs(path)
				return path
		except FileNotFoundError as err:
			print(err)
			

	def create_video_file(self, filename:str, path) -> cv2.VideoWriter:
		"""
		creates the video file using the path
		----------------
		Parameter:
			:filename: the video file (.mkv). creates a name with today's day if filename is not provide
			:path: the parent path to the file. this is joined with the filename to create the absolute path
			abs_path ** video: C:\ \Activity Monitor \\ 127.0.0.1 \\ January \\ Videos \\ 12/1/2022-video.mkv
			abs_path ** Logs: C:\\ Activity Monitor \\ 127.0.0.1 \\ January \\ Logs \\ 12-/1/2022-activityLog
		----------------
		Return:
			:video_file: the videoWriter object where the video frame received from the client will be written
		"""
		#: C:\\Activity Monitor\\127.0.0.1\\January\\Vidoes
		if filename is None or not filename.endswith(".mkv"):
			filename = f"{datetime.now().strftime('%d-%m-%Y')}-screen-recording.mkv"

		file_path = Path.joinpath(path, filename)
		FPS = 30
		#: ensure that SIZE is the same as size of the frame received else
		#: the frame will not write to the video file
		#: WARING: Do not change the size except the size of the transmitted frame changes

		
		#: pixel aspect ration 1: 1
		#: Screen aspect ration 4: 3
		#: suitable for web streaming

		SIZE = (320, 240) 
		
		# SIZE = (720, 480) => alternativen Frame: Warning, when using this 
		# ensure the size of the in-coming video frames are the same

		FOURCC = cv2.VideoWriter_fourcc(*"XVID")

		#file_name = "user_activity.mkv"
		video_file = cv2.VideoWriter(str(file_path), FOURCC, FPS, SIZE)
		#video_file = cv2.VideoWriter(file_name, FOURCC, FPS, SIZE)
		
		return video_file
			
	
	def get_video_file(self, ip):
		"""
		gets the created video file
		---------------
		Parameter:
			ip: client's ip
		"""
		# create_dir -> create_video_file -> get_video_file
		path = self.create_dir(ip)
		video_file = self.create_video_file("video", path)
		return video_file



		
