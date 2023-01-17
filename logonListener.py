import os
import win32evtlog
import getpass

from core import ActivityMonitor

# logon type = 10 = remote desktop
# The right events are 4624 (LOGON) and 4634(LOGOFF).

channel = 'Security'
ip = "127.0.0.1" 
port = 5005 
password = os.environ["PASSWORD"] 
sender = os.environ["SENDER"]
receiver = os.environ["RECEIVER"]

monitoring = False


def on_logon_event(action, context, event_handle):
    """ starts the monitoring script """
    print(action, context, event_handle)
    print("======== triggered =======")
    if getpass.getuser() == "Administrator":
        activityMonitor = ActivityMonitor(ip, port, password, sender, receiver)
        activityMonitor.start()

def on_logout_event(action, context, event_handle):
    """ Terminates the script """

    pass

eventtype = win32evtlog.EvtRpcLogin
handle = win32evtlog.EvtSubscribe(channel, win32evtlog.EvtRpcLoginAuthNegotiate, None, Callback = on_logon_event)


input()

win32evtlog.CloseEventLog(handle)