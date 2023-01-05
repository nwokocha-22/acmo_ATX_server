import logging
import sys

logger = logging.getLogger("activityLogger")
logger.setLevel(logging.DEBUG)

# ADD FORMATER
logStreamFormatter = logging.Formatter(\
     fmt=f"%(levelname)-8s %(asctime)s \t %(filename)s @function %(funcName)s line %(lineno)s - %(message)s", 
     datefmt="%H:%M:%S")

#: ADDING A HANDLER
consoleHandler = logging.StreamHandler(stream=sys.stdout)
consoleHandler.setFormatter(logStreamFormatter)
consoleHandler.setLevel(level=logging.DEBUG)

logger.addHandler(consoleHandler)

logger.debug("testing the logger")


#:  ADDING FILE HANDLER
logFileFormatter = logging.Formatter(
    fmt=f"%(levelname)s %(asctime)s -\t%(filename)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
fileHandler = logging.FileHandler(filename='activityLog.log')
fileHandler.setFormatter(logFileFormatter)
fileHandler.setLevel(level=logging.INFO)

logger.addHandler(fileHandler)
logger.info("Nothing has gone wrong")

from logging import handlers
logHttpFormatter = logging.Formatter(
  fmt=f"%(levelname)-8s %(asctime)s \t %(filename)s @function %(funcName)s line %(lineno)s - %(message)s", 
  datefmt="%Y-%m-%d %H:%M:%S"
)
httpHandler = logging.handlers.HTTPHandler(host='localhost', url='/logs', method='POST')
httpHandler.setFormatter(logHttpFormatter)

logger.addHandler(httpHandler)