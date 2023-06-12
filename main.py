
from threading import Thread
from helpers.logServer import LogRecordSocketReceiver
from helpers.videoServer import VideoServer

def main(ip, port):

    #: starts the Video receiver and the Log receivers on different threads
    #: The received video (mkv format) is writen to a file and save in the Activity Monitor folder
    #: the received log is also save in the log sub folder of the Activity Monitor folder
    #: The Activity Monitor directory is automatically created if it does not exist

    print("starting video thread...")
    video_server = VideoServer(ip, port)
    video_server.start()
    
    print("starting Log thread...")
    log_tcpserver = LogRecordSocketReceiver()
    print('About to start Log TCP server...')
    log_thread = Thread(target=log_tcpserver.serve_until_stopped)
    log_thread.start()

    log_thread.join()
    video_server.join()

if __name__=="__main__":
    import socket

    ip = socket.gethostbyname(socket.gethostname())#'127.0.0.1'
    port = 5055

    main(ip, port)