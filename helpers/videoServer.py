#!usr/bin/env python
# 2023, implemented by maru koch

import socket
import threading
import cv2
import platform
import numpy as np
from datetime import datetime
from pathlib import Path
import os
from helpers.loggers.errorLog import error_logger
from configparser import ConfigParser

_BUFFER: int = 65536
_index = 0
config = ConfigParser()
config.read('amserver.ini')

class StreamVideo(threading.Thread):
	"""Receives the video frame comming from the connected client
		and saves the video file at a designated directory.
	"""
	def __init__(self, client_ip, server_port, video_file, **kwargs):
		self.ip = client_ip
		self.server_port = server_port
		self.video_file = video_file

		super(StreamVideo, self).__init__(**kwargs)

	def run(self):
		thread = threading.Thread(target= self.recv_video_frame)
		thread.start()

	def recv_video_frame(self):
		"""Establishes a connection with the client through a UDP
		socket, receives the video frame transmitted by the client.
		"""
		global _index
		video_window_name = f"{self.ip}-{_index}"
		cv2.namedWindow(video_window_name, cv2.WINDOW_NORMAL)
		_index += 1
		with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock_udp:
			sock_udp.setsockopt(
				socket.SOL_SOCKET, socket.SO_REUSEADDR, _BUFFER)
			sock_udp.bind(('', self.server_port))
			
			while True:
				packet, addr = sock_udp.recvfrom(_BUFFER) # 1 MB buffer
				if packet == None:
					break

				if self.ip == addr[0]:
					frame = cv2.imdecode(
						np.frombuffer(packet, np.uint8), 
						cv2.IMREAD_COLOR)
					title = f'{self.ip if addr else "VIDEO"}'
					self.video_file.write(frame)
					cv2.imshow(video_window_name, frame)
					key = cv2.waitKey(1) & 0xFF

				if key == ord('q'):
					sock_udp.close()
					break

		self.video_file.release()


class VideoServer(threading.Thread):
	"""
	Parameters
	----------
	config: configParser.ConfigParser()
		Configuration parameters for the video module.

	Attributes
	----------
	FPS: int	
		Frames per second (default = 30)

	SIZE: tuple (int, int)
		Resolution of each frame in pixels
	"""

	connected_clients = []
	"""
	List of connected clients' IP addresses (list)
	"""

	fps: int = config['VIDEO']['fps']
	frame_height: int = int(config['VIDEO']['frame.height'])
	frame_width: int = int(config['VIDEO']['frame.width'])
	server_ip: str = socket.gethostbyname(socket.gethostname())
	server_port: int = int(config['DEFAULT']['port'])

	def __init__(self, **kwargs):
		super(VideoServer, self).__init__(**kwargs)

	def run(self):
		self.connect()

	def connect(self):
		"""Establishes a three way hand shake with the clients, and
		spawn a thread to send data to the connect client through a udp
		socket.

		"""
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock_tcp:
			sock_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			sock_tcp.bind((self.server_ip, self.server_port))
			sock_tcp.listen(5)
			
			while True:
				# waiting for a client to connect
				print("Waiting for a new connection")
				client, addr = sock_tcp.accept()
				client_ip, _ = addr
				print(f"{client_ip} connected")
				error_logger.info(f"{client_ip} connected")
				# once a new client is connected, create a video file
				# using the client ip
				video_file = self.get_video_file(client_ip)
				data = client.recv(1024).decode()

				if data == "ready":
					client.send(str.encode("shoot"))
					video_stream_thread = StreamVideo(client_ip, 
													  self.server_port, 
													  video_file)
					video_stream_thread.start()
					self.connected_clients.append(video_stream_thread)

				print(f"{len(self.connected_clients)} clients connected")

				for thread in self.connected_clients:
					thread.join()

	def get_root_folder(self):
		"""Checks the operating system and returns the appropriate root dir. 
		
		Return:
			system path
		"""
		sys_os = platform.system().lower()
		base = os.path.abspath(os.sep)
		root_folder = os.path.join(base, 'home', 'Activity Monitor') \
			if sys_os == 'linux' else os.path.join(base, 'Activity Monitor')
		return root_folder

	def create_dir(self, client_ip) -> str:
		"""Creates the path where the video file will be saved if it
		doesn't exist yet.
	
		Parameters
		----------
		client_ip: str
			The IP address of the client.
		
		Returns
		-------
		path: str
			The path where the video file will be saved.
		"""
		
		try:
			root_folder = Path(self.get_root_folder())
			month = datetime.today().strftime("%B")
			path = Path.joinpath(root_folder, client_ip, f"{month}", "Videos")
			if path.exists():
				return path
			else:
				os.makedirs(path)
				return path
		except FileNotFoundError as err:
			print(err)
			

	def create_video_file(self, path) -> cv2.VideoWriter:
		"""Creates the video file using the path.
		
		Parameters
		----------
		path: str
			The parent path of the file. This is joined with the
			filename to create the absolute path e.g.
			`video:
			C:\\Activity Monitor\\127.0.0.1\\January\\Videos\\\
				12/1/2022-video.mkv`
	
		Returns
		-------
		video_file: cv2.VideoWriter
			The videoWriter object where the video frame received from
			the client will be written.

		Notes
		-----
		The video frame should be the same size as incoming frames from
		client. The video frame can be changed in the config file
		(amserver.ini).
		"""
		filename = self.create_unique_video_name(path)
		file_path = Path.joinpath(path, filename)
		FOURCC = cv2.VideoWriter_fourcc(*'XVID')
		# FOURCC = cv2.VideoWriter_fourcc(*'hvc1')
		# SUPPORTS->XVID, MJPG(HIGH VIDEO QUALITY), DIVX(FOR WINDOWS)
		video_file = cv2.VideoWriter(
			str(file_path),
			FOURCC,
			int(self.fps),
			(self.frame_height, self.frame_width))
		return video_file
			
	def get_video_file(self, ip):
		"""Gets the created video file.

		Parameters
		----------
		ip: str
			Client's IP address.
		"""
		# create_dir -> create_video_file -> get_video_file
		path = self.create_dir(ip)
		video_file = self.create_video_file(path)
		return video_file

	def create_unique_video_name(self, path):
		"""Creates unique video file name.

		Parameters
		----------
		path: str
			The paths where the video files are saved.
			
		Returns
		-------
		filename: str
			The new video file name.
		"""
		date_str = datetime.now().strftime('%d-%m-%Y')
		num = len([video_file for video_file in os.listdir(path) \
			if video_file.startswith(date_str)])
		filename = f"{date_str}-screen-recording-{num}.mkv"
		return filename


		
