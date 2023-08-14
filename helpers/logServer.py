import pickle
import logging
import logging.handlers
import socket
import socketserver
import struct
from datetime import datetime
from pathlib import Path
from helpers.loggers.errorLog import error_logger
import os


class LogRecordStreamHandler(socketserver.StreamRequestHandler):
    logged = False
    def handle(self):
        """ Handle multiple requests - each expected to be a 4-byte length,
        followed by the LogRecord in pickle format. Logs the record
        according to whatever policy is configured locally.
        """
        while True:
            try:
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
            except ConnectionResetError:
                if not self.logged:
                    client_ip =  self.server.server_address[0]
                    trace = f"{client_ip} disconnected"
                    error_logger.info(trace)
                    self.logged = True
                    break

    def unPickle(self, data):
        """Unpickles the pickled log object received
        
        Parameter
        ---------
        data : bytes
            The pickled log object
        """


        return pickle.loads(data)

    def create_dir(self, client_ip):
        """Constructs a path where the log file is saved.

        Paremeter
        ---------
        client_ip : str
            IP address of the client that connected with the server

        Returns
        ---------
        path: str
            path to the folder where the log file will be saved
        """
        
        try:
            root_folder = Path("C:/Activity Monitor")
            month = datetime.today().strftime("%B")
            path = Path.joinpath(root_folder, client_ip, f"{month}", "Logs")
            if path.exists():
                return path
            else:
                os.makedirs(path)
                return path
        except FileNotFoundError as err:
            print(err)

    def logRecord(self, record):
        """ Records the log received from client.

        Parameter
        ---------
        record : `str`
            log file received from client
        """

        client_ip =  self.server.server_address[0]
        path = self.create_dir(client_ip)

        if not path.exists():
            os.makedirs(path)

        if self.server.logname is not None:
            name = self.server.logname
        else:
            name = record.name
        logger = logging.getLogger()

        if not logger.hasHandlers():
            date = datetime.today().strftime("%d-%m-%Y")
            file_ = f"{date}-activityLog.log"
            file_name = Path.joinpath(path, file_)
            fileHandler = logging.FileHandler(filename=str(file_name))
            
            logFileFormatter = logging.Formatter(
                fmt=f"%(levelname)s : %(asctime)s - %(name)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

            fileHandler.setFormatter(logFileFormatter)
            logger.addHandler(fileHandler)

            logger.handle(record)
        else:
            logger.handle(record)

class LogRecordSocketReceiver(socketserver.ThreadingTCPServer):
    """Simple TCP socket-based logging receiver.
    """

    allow_reuse_address = True

    def __init__(self, 
                 host=socket.gethostbyname(socket.gethostname()),
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



   