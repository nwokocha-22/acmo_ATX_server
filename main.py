
#import socket
from threading import Thread
#from helpers.logServer import LogRecordSocketReceiver
from helpers.logServer import LogRecordSocketReceiver
from helpers.videoServer import ReceiveVideo

def main():
    #: IP = socket.gethostbyname(socket.gethostname())

    #: starts the Video receiver and the Log receivers on different threads
    #: The received video is writen to a file and save in the Resource folder
    #: the received log is also save in the log sub folder of the Resources directory
    #: The Resources directory is automatically recreated if it does not exist

    IP = "127.0.0.1"
    PORT = 5005
	
    print("starting video thread...")
    video_server = ReceiveVideo(IP, PORT)
    video_thread = Thread(target=video_server.connect)
    video_thread.start()
    
    print("starting Log thread...")
    log_tcpserver = LogRecordSocketReceiver()
    print('About to start Log TCP server...')
    log_thread = Thread(target=log_tcpserver.serve_until_stopped)
    log_thread.start()


    log_thread.join()
    video_thread.join()

if __name__=="__main__":
    main()