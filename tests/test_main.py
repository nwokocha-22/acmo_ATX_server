import pytest
import platform
from datetime import datetime
import os
import cv2
from pathlib import Path


def test_video_file(video_server):
    """Tests that a root dir is created based on the system os. """
    root = video_server.get_root_folder()
    if platform.system().lower() == 'linux':
        assert root == '/home/Activity Monitor'
    elif platform.system().lower() == 'windows':
        assert root == 'C:\\Activity Monitor'
        
def test_create_dir(video_server):
    """Tests the creation of directory to save video file. """
    ip = ' 127.0.0.1'
    month = datetime.today().strftime("%B")
    path = video_server.create_dir(ip)
    assert str(path) == f'C:\\Activity Monitor\\ 127.0.0.1\\{month}\\Videos'

def test_naming_of_video_file(video_server):
    """Tests the unique naming of the video file. """
    path = os.path.join(os.path.dirname(__file__), 'videos')
    filename = video_server.create_unique_video_name(path)
    assert filename.endswith('.mkv')

def test_create_video_file(video_server):
    """Tests successful creation of video writer. """
    path = Path(os.path.join(os.path.dirname(__file__), 'videos'))
    video_file = video_server.create_video_file(path)
    assert isinstance(video_file, cv2.VideoWriter)

def test_get_video_file(video_server):
    """Tests the retriever of the video writer. """
    video = video_server.get_video_file('127.0.0.1')
    assert isinstance(video, cv2.VideoWriter)

def test_video_file_numbering(video_server):
    """Test for numbered videos. """
    path = Path(os.path.join(os.path.dirname(__file__), 'videos'))
    files = os.listdir(path)

    file_num = files[0].split('-')[-1].split('.')[0]
     
    for file in files:
        _file = os.path.join(path, file)
        os.remove(_file)

    assert file_num == '0'
   