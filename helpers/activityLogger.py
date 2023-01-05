import logging
from threading import Thread
from pathlib import Path
import os

class ActivityLogger(logging.Logger):

    def __init__(self, path=None):
        #Thread.__init__(self)
        self.path = path
        self.startLogger()
        print("activity log thread started")
        
    def startLogger(self):
        filename = str()
        if os.path.exists(self.path):
            filename = self.path
        else:
            filename = "activityLog.log"
        logging.basicConfig(
            #filename="activityLog.log", 
            filemode='w',
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.DEBUG, 
            )

    def open_log(self):
        """
        opens and retrieves the log file
        """
        path = None
        try:
            if os.path.exists(self.path): 
                path = self.path 
            else: path = "activityLog.txt"
            with open(path, 'r') as log:
                log_file = log.read()
            return log_file
        except os.error as err:
            print("path does not exist in the path specified")

if __name__=="__main__":
    logg = ActivityLogger(Path("activityLog.log"))
    logg.info('o man')

    
