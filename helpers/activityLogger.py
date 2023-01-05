import logging
from threading import Thread
from pathlib import Path
import os

class ActivityLogger(logging.Logger):

    def __init__(self, path=None):
        super(ActivityLogger, self).__init__(name="activityLog", level=logging.DEBUG)
        self.configLog()
        print("activity log thread started")
        
    def configLog(self):
        self.setLevel(logging.DEBUG)
        self.addHandler(logging.StreamHandler)
        logging.basicConfig(
        filename="activityLog.log", 
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
            path = "activityLog.log"
            with open(path, 'r') as log:
                log_file = log.read()
            return log_file
        except os.error as err:
            print("path does not exist in the path specified")

if __name__=="__main__":
    logg = ActivityLogger("activityLog.log")
    logg.info('o man')
    log =logg.open_log()
    print(log)
   

    
