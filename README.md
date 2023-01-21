
## ACTIVITY MONITOR - SERVER


# CLIENT

# Starting the script

#: You can start the script by starting the activity monitor server service

    task manager -> service - ActivityMonitorServer -> right clik and select 'start' to start the script or 'stop' to stop it

#: Alteranatively, you can navigate to the script through an IDE (Vscode).

#: Ensure you are in the directory containing the script.

#: To run the script, type:
    python ./core.py

## Where to find Recorded Videos and Logs

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
#: pyinstaller --noconfirm --onefile --windowed --hidden-import win32timezone path-to-py file

#: STEP 2: INSTALL YOUR EXECUTABLE

#: first navigate to the folder containing the executable file

#: yourexefile.exe --startup delayed install

#: STEP 3: START YOUR EXECUATABLE
#: yourexefile.exe start

#: REMOVE SERVICE
#: sc delete servicename
