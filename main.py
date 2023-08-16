import sys
sys.path.append('.')
import helpers
from threading import Thread
from helpers.logServer import LogRecordSocketReceiver
from helpers.videoServer import VideoServer
import configparser

def main_app():
    """Starts the Video receiver and the Log receivers on different threads.

    Note
    ------
        - The received video (mkv format) is writen to a file and save in the Activity 
          Monitor folder.
        - the received log is also save in the log sub folder of the Activity Monitor folder.
        - The Activity Monitor directory is automatically created if it does not exist.
    """
    config = configparser.ConfigParser()
    config.read('amserver.ini')

    video_server = VideoServer()
    video_server.start()
    
    log_tcpserver = LogRecordSocketReceiver()
    log_thread = Thread(target=log_tcpserver.serve_until_stopped)
    log_thread.start()

    log_thread.join()
    video_server.join()

if __name__=="__main__":
    main_app()