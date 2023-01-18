import logging, logging.handlers

rootLogger = logging.getLogger('')
rootLogger.setLevel(logging.DEBUG)

socketHandler = logging.handlers.SocketHandler('localhost', logging.handlers.DEFAULT_TCP_LOGGING_PORT)

#: NOTE: Didn't use formatter as that will not be recognized by the socket

rootLogger.addHandler(socketHandler)

keyMouseLogger = logging.getLogger('activityLog')
clipboardLogger = logging.getLogger('clipboardLog')
