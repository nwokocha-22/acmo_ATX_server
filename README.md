
## ACTIVITY MONITOR


# CLIENT

# Starting the script

To run the script, type:
    python ./core.py

- Running the main module (core.py) starts the Video, Clipboard, Email, and KeyMouse threads.

# Keyboard and  MouseMonitoring
The KeyMouseActivity module monitors the user's keyboard, mouse, and clipboard activities. It captures the number of keystroke, and mouse moves

- KeyMouseMonitor class of the KeyMouseActivity Module inherits from both the MouseActivity and KeyboardActivity classes respectively

## CLIPBOARD MONITORING
- The clipboardActivity Module monitors the content copied to clipboard. also detects the type of content (text, image or file), and calls appropriate functions (on_text, on_image, and on_file) in the main application (core.py) for coresponding handling of the copied content.

- the clipboard event handlers invoke a policy check to see if the copied content violates the copy policy or not. If not, it takes count of the size of the copied content. If it does, the invokes a deciplinary action which disapples the clipbaord, updates the policyConfig file by setting the hasDefaulted key to True and appending the time the defaulting occurs. A corresponding email is sent to the Admin to inform of the policy violation.

## Where to find Logged Keyboard and Mouse Activiteis

-   C:/Activity Monitor/client ip/Logs/Logfile.log

# Screen 
The activity monitor script also consist of a helper module that captures the screenshot of the user's screen and transmits the video via UDP sock ets to a remote server where it can be live streamed and also saved in a video file in a designated folder for future references. A new folder where the video is saved is created using the client's ip address if it does not already exist.

## Where to find Recorded Videos

- C:/Activity Monitor/Recorded Video/IP unique folder/Folder specifying month/video files

# Copy Policy
If the user copies content more than 500 KB per hour or equal or more than 1500 KB for 24 hours, an email notification is sent to the administrator. the email message includes the ip address of the client, the date and time of occurence, the size of the file copied, the actual text copied (for text files), or attachment of the file(s) for binary files.


### SERVER

## Starting the Script
type:
    python ./helpers/videoServer.py

- This starts the Video and LogServer threads

- The ReceiveVideo class handles the handling of the video frames receipt through the UDP sockets and outputs the frame in a CV2 Window.

- The captured video can be viewed in real time. The frames are also written to a video file that is saved in C:\\Activity Monitor\\client ip\\current month\\screen recording\\video_file.mkv

- The vidoe file can be played using VLC media player

- The log output in the client is transmitted through a tcp connection and saved in a log file in the server. The saved log file can be found in C:\\Activity Monitor\\client ip\\current month\\Logs\\logfile.log


### WINDOW SERVICES
- The Windows starts the script when user is logged into the machine through rdp connection and terminated when user is logged out

- The script runs in the background inviscible to the user

- The script can manually be started by:
    net ActivityMonitorService start

- To stop it:
    net ActivityMonitorService stop

This operation can also be done through the GUI by going to the Task Manager -> Services -> right click on the ActivityMonitorService. Select 'start' to run the service or 'stop' to terminate the service. The service can also be removed by selecting 'delete'
