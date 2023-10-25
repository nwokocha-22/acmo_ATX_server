
# ACTIVITY MONITOR - SERVER
## v 1.0.0

## Starting the Script
`python ./main.py`

### HOW IT WORKS
- Running the main.py module starts the Video and LogServer threads

- The ReceiveVideo class of the videoServer module handles the writing and streaming of video frames receipt through the UDP sockets and outputs the frame in a CV2 Window.

- The captured video can be viewed in real time. The frames are also written to a video file that is saved to `C:\\Activity Monitor\\client ip\\current month\\Videos\\video_file.mkv` (windows) and to `/home/Activity Monitor/client ip/current month/videos/video_file.mkv` for Linux.

- The video file can be played using VLC media player

- Allow TCP connections on the port indicated in the config file (5055 is the default) to be able to receive video streams.

### Where to find Activity Logs transmitted from the client(s)
- The log output in the client is transmitted through a tcp connection and saved in a log file in the server. The saved log file can be found in `C:\\Activity Monitor\\client ip\\current month\\Logs\\logfile.log` (windows) or `/home/Activity Monitor/client ip/current month/Logs/logfile.log` for Linux.

- Allow TCP connections on port 9020 to be able to receive logs.


### WINDOW SERVICES

- To setup the window service for the server, please  refer to the steps outlined below:

# TO INSTALL
- ./dist/main_client.exe install

# TO START
- ./dist/main_client.exe start

# TO STOP
- ./dist/main_client.exe stop

# To REMOVE
- ./dist/main_client.exe remove


# THIRD PARTY LIBRARIES AND POSSIBLE EXCEPTIONS
- using cv2 from opencv-python (4.7.0.68) raises AttributeError: partially initialized module 'cv2' has no attribute 'gapi_wip_gst_GStreamerPipeline' (most likely due to a circular import)
- to solve this problem uninstall opencv-python, opencv-contrib-python, and opencv-python-headless, then reinstall opencv-python

## RESOLVING SERVICE RELATED ERROR
- When you encounter this error: `Error removing service: The specified service has been marked for deletion. (1072)`
- Right click on the service in task manager > services and select go to process. Kill the process attached to the service (pythonservice.exe). That should fix the problem
- 
### PREPARING THE SCRIPT FOR PRODUCTION
- Refer to the steps outlined in the ACTIVITY_MONITOR_CLIENT's README.md

### GENERATING EXECUTABLE
- To build the executable, run the code below in the terminal

`pyinstaller.exe --runtime-tmpdir=. --hidden-import win32timezone --collect-submodules helpers --hidden-import logging.handlers --hidden-import socketserver --hidden-import cv2 --name main_server --onefile main.py`

- to avoid unpacking files in the window's temporary folder which will be deleted, always include `--runtime-tmpdir=.` in your build command. it unpacks your executable where it will not be deleted by windows.

### NEED MORE INFO?
- Reach out to Maruche