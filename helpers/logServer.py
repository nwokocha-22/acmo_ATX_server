import pickle
import socketserver
import struct
import logging, logging.handlers

class LogRequestHandler(socketserver.StreamRequestHandler):

    def handleRequest(self):
        """
        handle incoming request to the server. calls the loadData function 
        loads the pickled data and records the log

        """
        while True:
            data = self.connection.recv(4)
            if len(data) < 4:
                break
            slen = struct.unpack('>L', data)[0]
            data = self.connection.recv(slen)
            while len(data) < slen:
                data = data + self.connection.recv(slen - len(data))
            pickle_obj = self.loadData(data)
            record = logging.makeLogRecord(pickle_obj)
            self.recordLog(record)

    def loadData(self, data):
        """
        Loads the received pickled object
        """
        return pickle.loads(data)

    def recordLog(self, record):
        """
        Records the received log
        """
        if self.server.logname is not None:
            log_name = self.server.logname
        else:
            log_name = record.name

        logger= logging.getLogger(log_name)
        logger.handle(record)

class LogReceiver(socketserver.ThreadingTCPServer):
    """
    Simple TCP socket-based logging receiver suitable for testing.
    """

    reuse_address = True

    def __init__(\

        self, host='localhost', 
        port=logging.handlers.DEFAULT_TCP_LOGGING_PORT, 
        handler=LogRequestHandler):

        socketserver.ThreadingTCPServer.__init__(self, (host, port), handler)
        self.abort = 0
        self.timeout = 1
        self.logname = None

    def serve_until_stopped(self):
        import select
        abort = 0
        while not abort:
            rd, wr, ex = select.select([self.socket.fileno()], [], [], self.timeout)
            if rd:
                self.handle_request()
            abort = self.abort

def main():
    logging.basicConfig(format='%(relativeCreated)5d %(name)-15s %(levelname)-8s %(message)s')
    tcpserver = LogReceiver()
    print('About to start TCP server...')
    tcpserver.serve_until_stopped()

if __name__ == '__main__':
    main()