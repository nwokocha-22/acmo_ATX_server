
## ACTIVITY MONITOR - SERVER

# Starting the script

#: You can get the script running by starting the activity monitor server service

### to start the activity service

    task manager -> service - ActivityMonitorServer -> right clik and select 'start' to start the script or 'stop' to stop it

#: Alteranatively, you can navigate to the script through an IDE (Vscode).

#: Ensure you are in the directory containing the script.

#: To run the script, type:
    python ./main.py

### Where to find Recorded Videos and Logs

#: Screen recordings are logs can be found in the resources folder.

#: Path to Logs
    - current directory /Resources /IP unique folder/Month/Logs/daily activity Log

#: Path to Screen recordings
    - current directory /Resources /IP unique folder/Month/Videos/daily screen recordings


### WINDOW SERVICES

#: INSTALL SERVICE
#: python scriptName.py install

#: UNINSTALL SERVICE
#: python scriptName.py remove

#: START SERVICE
#: python scriptName.py start

#: UPDATE SERVICE
#: python scriptName.py update

#: STOP SERVICE
#: python scriptName.py update

#: ALTERNATIVELY - USING EXEUTABLE

#: STEP 1: CONVERT TO EXECUTABLE FILE
#: pyinstaller --onefile --console --name --core_server main.py

#: STEP 2: INSTALL YOUR EXECUTABLE

#: first navigate to the folder containing the executable file

#: yourexefile.exe --startup delayed install

#: STEP 3: START YOUR EXECUATABLE
#: yourexefile.exe start

#: REMOVE SERVICE
#: sc delete servicename

# LIBRARIES AND DEPENDENCIES
- using cv2 from opencv-python (4.7.0.68) raises AttributeError: partially initialized module 'cv2' has no attribute 'gapi_wip_gst_GStreamerPipeline' (most likely due to a circular import)
- to solve this problem uninstall opencv-python, opencv-contrib-python, and opencv-python-headless, then reinstall opencv-python

## RESOLVING SERVICE RELATED ERROR
- you you encounter this error: `Error removing service: The specified service has been marked for deletion. (1072)`
- right click on the service in task manager > services and select go to process. Kill the process attached to the service (pythonservice.exe). That should fix the problem
- 