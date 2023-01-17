
from dataclasses import dataclass
import logging
import logging.handlers as handler
#: LOGS USER KEYBOARD AND MOUSE ACTIVITY, AND THE COPIED FILE SIZE

#: GET LOG FILE


class Logger(logging.Logger):
    def __init__(self, logger, handler, formatter) -> None:
        
clipboardLogger = logging.getLogger("clipboardLogger")
clipboardLogger.setLevel(logging.DEBUG)

#:  ADDING FILE HANDLER - LOGS TO FILE
logFileFormatter = logging.Formatter(
    fmt=f"%(levelname)s %(asctime)s -\t%(filename)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

#: FILE HANDLER
fileHandler = logging.FileHandler(filename='activityLog.log')
fileHandler.setFormatter(logFileFormatter)
fileHandler.setLevel(level=logging.INFO)

#: DD SOCKET HANDLER 
socketHandler = handler.SocketHandler('localhost',
                    handler.DEFAULT_TCP_LOGGING_PORT)

#: Socket handler sends log across socket as unformated pickle so no 
#: need for formatter

#: SAVE LOG IN A FILE ('activityLog.log) and also sends it through a tcp socket
clipboardLogger.addHandler(socketHandler)
clipboardLogger.addHandler(fileHandler)

import logging
import logging.handlers as handler
#: LOGS USER KEYBOARD AND MOUSE ACTIVITY, AND THE COPIED FILE SIZE

#: GET LOG FILE

class Logger(logging.Logger):
    def __init__(self, name: str, handler, level=logging.INFO,) -> None:
        super().__init__(name, level)
        self.setLevel(level)
        self.addHandler(handler)

clipboardLogger = logging.getLogger("clipboardLogger")
clipboardLogger.setLevel(logging.INFO)

#:  ADDING FILE HANDLER - LOGS TO FILE
logFileFormatter = logging.Formatter(
    fmt=f"%(levelname)s %(asctime)s -\t%(filename)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

#: FILE HANDLER
fileHandler = logging.FileHandler(filename='clipboardLog.log')
fileHandler.setFormatter(logFileFormatter)
fileHandler.setLevel(level=logging.INFO)

#: DD SOCKET HANDLER 
socketHandler = handler.SocketHandler('localhost',
                handler.DEFAULT_TCP_LOGGING_PORT)

#: Socket handler sends log across socket as unformated pickle so no 
#: need for formatter

#: SAVE LOG IN A FILE ('activityLog.log) and also sends it through a tcp socket
clipboardLogger.addHandler(socketHandler)
clipboardLogger.addHandler(fileHandler)