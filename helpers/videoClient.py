import socket
from threading import Thread
import cv2
import numpy as np


class ReceiveVideo:

	BUFFER = 1024 * 1024

	def __init__(self, host, port):
		self.address = (host, port)

	def recv_data(self, addrs):
		# create a window with the with title of the client ip 
		cv2.namedWindow(addr[0])

		with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock_udp:
			sock_udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			sock_udp.bind(self.address)

			while True:
				packet, addr = sock_udp.recvfrom(self.BUFFER) # 1 MB buffer
				client_ip = addr[0]

				#: stream the data from that particular client
				if client_ip == addrs[0]:
					img = cv2.imdecode(np.frombuffer(packet, np.uint8), cv2.IMREAD_COLOR)
					title = f'{client_ip if addr else "VIDEO"}'
					cv2.imshow(title, img)
					key = cv2.waitKey(1) & 0xFF

				if key == ord('q'):
					self.sock_udp.close()
					break

	def connect(self):
		"""
		establishes a three way hand shake with the clients, and spawn a thread to send data
		to the connect client
		"""
	
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock_tcp:
			sock_tcp.connect(self.address)
			while True:
				#: waiting for a client to connect
				
				client, addr = sock_tcp.accept()
				print("connected to:", client)
				thread = Thread(target=self.recv_data, args=(addr))
				thread.start()
				thread.join()

	
if __name__=="__main__":
	video_server = ReceiveVideo('', 1980)
	video_server.connect()