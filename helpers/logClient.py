import logging, logging.handlers

rootLogger = logging.getLogger('')
rootLogger.setLevel(logging.DEBUG)
socketHandler = logging.handlers.SocketHandler('localhost',
                    logging.handlers.DEFAULT_TCP_LOGGING_PORT)
# don't bother with a formatter, since a socket handler sends the event as
# an unformatted pickle
rootLogger.addHandler(socketHandler)

# Now, we can log to the root logger, or any other logger. First the root...
logging.info('Jackdaws love my big sphinx of quartz.')

# Now, define a couple of other loggers which might represent areas in your
# application:

keyMouseActivity = logging.getLogger('KeyMouse')
clipboardActivity = logging.getLogger('Clipboard')

status = 'active'
message = f"keystroke:{102}, mouseMoves:{390}, copied file size: {20}, status:{status}"

keyMouseActivity.debug(message)
keyMouseActivity.info(message)

clipboardActivity.warning(message)
clipboardActivity.error(message)