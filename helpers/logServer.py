import pickle
import logging
import logging.handlers
import socketserver
import struct
from datetime import datetime
from pathlib import Path, PurePosixPath
import os


class LogRecordStreamHandler(socketserver.StreamRequestHandler):
  
    def handle(self):
        """
        Handle multiple requests - each expected to be a 4-byte length,
        followed by the LogRecord in pickle format. Logs the record
        according to whatever policy is configured locally.
        """
        while True:
            chunk = self.connection.recv(4)
            if len(chunk) < 4:
                break
            slen = struct.unpack('>L', chunk)[0]
            chunk = self.connection.recv(slen)
            while len(chunk) < slen:
                chunk = chunk + self.connection.recv(slen - len(chunk))
            obj = self.unPickle(chunk)
            record = logging.makeLogRecord(obj)
            self.logRecord(record)

    def unPickle(self, data):
        return pickle.loads(data)

    def create_dir(self, client_ip):
        """
        constructs a path where the log file is saved
        """
        date = datetime.now()
        root_folder = Path("C:/Activity Monitor")
        try:
            path = Path.joinpath(root_folder, client_ip, f"{date.month}")
            if path.exists():
                return path
            else:
                os.makedirs(path)
                return path
        except FileNotFoundError as err:
            print(err)

    def logRecord(self, record):
        # if a name is specified, we use the named logger rather than the one
        # implied by the record.
        print("record made")
        client_ip =  self.server.server_address[0]
        #Activity Monitor/127.0.0.1/January/Logs/12-/1/2022-activityLog
        
        root_folder = Path.home()/"Activity Monitor"
        month = datetime.today().strftime("%B")

        path = Path.joinpath(root_folder, client_ip, f"{month}", "Logs")
       
        print("path:", path)
    

        if not path.exists():
            os.makedirs(path)

        if self.server.logname is not None:
            name = self.server.logname
        else:
            name = record.name

        logger = logging.getLogger()

        date = datetime.today().strftime("%d-%m-%Y")
        file_name = f"{date}-activityLog.log"

        file = Path.joinpath(path, file_name)

        fileHandler = logging.FileHandler(filename=str(file))
        
        logFileFormatter = logging.Formatter(
            fmt=f"%(levelname)s %(asctime)s -\t%(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        fileHandler.setFormatter(logFileFormatter)
        logger.addHandler(fileHandler)
        logger.handle(record)

class LogRecordSocketReceiver(socketserver.ThreadingTCPServer):
    """
    Simple TCP socket-based logging receiver suitable for testing.
    """

    allow_reuse_address = True

    def __init__(self, host='localhost',
                 port=logging.handlers.DEFAULT_TCP_LOGGING_PORT,
                 handler=LogRecordStreamHandler):

        socketserver.ThreadingTCPServer.__init__(self, (host, port), handler)
        self.abort = 0
        self.timeout = 1
        self.logname = None

    def serve_until_stopped(self):
        import select
        abort = 0
        while not abort:
            rd, wr, ex = select.select([self.socket.fileno()],
                                       [], [],
                                       self.timeout)
            if rd:
                self.handle_request()
            abort = self.abort



   