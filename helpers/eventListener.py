# import win32evtlog 
# import win32event
# import win32api

# server = 'localhost' # name of the target computer to get event logs
# logtype = 'Windows Log'
# hand = win32evtlog.OpenEventLog(server, logtype)
# flags = win32evtlog.EVENTLOG_FORWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
# total = win32evtlog.GetNumberOfEventLogRecords(hand)
# print(total)
# total += 1

# h_evt = win32event.CreateEvent(None, False, False, "evt0")
# notify = win32evtlog.NotifyChangeEventLog(hand, h_evt)

# while True:
#     wait_result = win32event.WaitForSingleObject(h_evt, win32event.INFINITE)
#     readlog = win32evtlog.ReadEventLog(hand, flags, total)
#     for event in readlog:
#         print(f"{event.TimeGenerated.Format()} : [{event.RecordNumber}] : {event.SourceName}")
#     total += len(readlog)

# win32evtlog.CloseEventLog(hand)
# win32api.CloseHandle(h_evt)
# import psutil

# def get_ip(port=3389):
#     ip = ""
#     for x in psutil.net_connections():
#         print(x)
#         if x.status == "ESTABLISHED" and x.laddr.port == port:
#             ip = x.raddr.ip
#             break

# get_ip()

# DETECT LOGON EVENT FROM RDP

# Event ID: 21
# Provider Name: Microsoft-Windows-TerminalServices-LocalSessionManager
# Description: “Remote Desktop Services: Session logon succeeded:”

#: This precedes event ID 22: which indicates the Source Network Address: Local means the loging is not 
# remote RDP logon event.

import win32evtlog
import win32event
import win32api
import socket

server =  socket.gethostbyname(socket.gethostname())# replace with the name of your server
log_type = 'Security'
#log_type = 'System'

# Open a handle to the event log
handle = win32evtlog.OpenEventLog(server, log_type)

# Register for notifications of new events
#notify = win32evtlog.NotifyChangeEventLog(handle, win32event.CreateEvent(None, 0, 0, None))
#notify = win32evtlog.NotifyChangeEventLog(handle, win32event.WaitForSingleObject)

while True:
    # Wait for a new event
    events = win32evtlog.ReadEventLog(handle, win32evtlog.EVENTLOG_SEQUENTIAL_READ | win32evtlog.EVENTLOG_FORWARDS_READ, 0)
    #print("event methods", dir(events))
    
    for event in events:
        # Check if the event is a RDP logon event
       
        if event.EventType == win32evtlog.EVENTLOG_AUDIT_SUCCESS and event.EventID == 4624:
            #if event.EventType == 10:
            print('RDP logon event found:')
            print('User:', event.StringInserts)
            print("Computer name", event.ComputerName)
            print("eventType", event.EventType)
            print("")
            print('Time:', event.TimeGenerated)
            pass

        elif event.EventType == win32evtlog.EVENTLOG_AUDIT_FAILURE and event.EventID == 4634:
            print("log out:", event.TimeGenerated)

        elif event.EventID == 24:
            print("Session Disconnected")

win32evtlog.CloseEventLog(handle)

#: prevent application from running

# import os
# import pythoncom
# from threading import Thread
# import time
# import wmi

# def listener():
#     pythoncom.CoInitialize()
#     c = wmi.WMI()
#     process_watcher = c.Win32_Process.watch_for("creation")
#     while True:
#         new_process = process_watcher()
#         if new_process.Caption == 'myApplication.exe':
#             os.system('taskkill /im myApplication.exe')


# active_time = int(input('How long would you like to block programs for?'))

# t = Thread(target=listener)
# t.daemon = True
# t.start()

# time.sleep(active_time)

import win32evtlog # module name for pywin32
import win32evtlogutil
import smtplib
import os
import lxml.etree as ET
from xml.etree import cElementTree as ElementTree
from xmLParser import XmlDictConfig

parser = ET.XMLParser(recover=True)
from xml.etree.ElementTree import XML, fromstring



# Connect to the Windows event log
server = "localhost"
log_type = "Security"
hand = win32evtlog.OpenEventLog(server, log_type)

# Set up event notification
flags = win32evtlog.EVENTLOG_SEQUENTIAL_READ | win32evtlog.EVENTLOG_FORWARDS_READ
total = win32evtlog.GetNumberOfEventLogRecords(hand)
last_record = total - 1
flush = True
while True:
    events = win32evtlog.ReadEventLog(hand, flags, last_record)
    if flush:
        events.clear()
        flush = False
    if events:
        for event in events:
            if event.EventID == 4624 and event.EventType == win32evtlog.EVENTLOG_AUDIT_SUCCESS:
                # Check if the event is an RDP logon
                event_data = win32evtlogutil.SafeFormatMessage(event, log_type)
                #print("event data:", event_data) 
                #parent_tree = ET.ElementTree(ET.fromstring(event_data, parser=parser)) 
                #root = ElementTree.XML(event_data)
                new = event_data.split("\n")
                #workStation = new[24].split(':')[-1]
                sourceNetworkIp = new[25].split(':')[-1].strip()
                #sourcePort = new[26].split(':')[-1] 

                #print("network:", sourceNetworkIp) 
                #  
                #logon_dict = XmlDictConfig(root)
                #print("__logo ", xml_str)
                if sourceNetworkIp:
                    print("login detected:")

                if 'Remote Desktop' in event_data:
                    #Send email notification
                    print("login detected. sending email")
                    sender_email = os.environ["SENDER"]
                    receiver_email = os.environ["RECEIVER"]
                    password = os.environ["PASSWORD"]
                    message = f"New RDP logon detected: {event_data}"

                    server = smtplib.SMTP("smtp.gmail.com", 587)
                    server.starttls()
                    server.login(sender_email, password)
                    server.sendmail(sender_email, receiver_email, message)
                    server.quit()
                    print("login detected")
                
    last_record = win32evtlog.GetNumberOfEventLogRecords(hand)


