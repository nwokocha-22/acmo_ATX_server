import win32evtlog
import win32event
import pywintypes

server = "WIN-35Q6G6JIQT0"
log_type = "Security"
eventLog = win32evtlog.OpenEventLog(server, log_type)

def logoff_callback(z, x, y):
    print("event fired, ", z, x, y)
    # if event.EventID == 4634:
    #     print("Logoff detected. Event details:", event)

# Create a handle for the event
signalEvent = win32event.CreateEvent(None, 0, 0, None)

#subscription = win32evtlog.EvtSubscribe(hand, signalEvent, None, (4634,), None, None, 0)

venttype = win32evtlog.EvtRpcLogin
subscription = win32evtlog.EvtSubscribe(log_type, 1, None, Callback = logoff_callback)

while True:
    win32event.WaitForSingleObject(signalEvent, win32event.INFINITE)
    events = win32evtlog.EvtNext(signalEvent, 1)
    for event in events:
        if event.EventID == 4634:
            logoff_callback(event)
        elif event.EventID == 4624:
            print("log in detected")

win32evtlog.CloseEventLog(eventLog)
win32evtlog.EvtClose(subscription)