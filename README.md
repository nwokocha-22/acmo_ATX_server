
## ACTIVITY MONITOR

# Keyboard, Mouse, and Clipboard Activity Monitoring
This scripts monitors the user's keyboard, mouse, and clipboard activities. It captures the number of keystroke, and mouse moves every 10 minutes and logs the information to a remote server through a socket.

## Where to find Log Keyboard and Mouse Activiteis

-   C:/Activity Monitor/Logs/Log file

# Video Capturing
The activity monitor script also consist of a helper module that captures the screenshot of the user's screen and transmits the video via UDP sock ets to a remote server where it can be live streamed and also saved in a video file in a designated folder for future references. A new folder where the video is saved is created using the client's ip address if it does not already exist.

## Where to find Recorded Videos

- C:/Activity Monitor/Recorded Video/IP unique folder/Folder specifying month/video files

# Copy Policy
If the user copies content more than 500 KB per hour or equal or more than 1500 KB for 24 hours, an email notification is sent to the administrator. the email message includes the ip address of the client, the date and time of occurence, the size of the file copied, the actual text copied (for text files), or attachment of the file(s) for binary files.

## AUTHOR: Maru Koch
