import pytest
import sys
import os
sys.path.append('.')
from helpers.videoServer import VideoServer, StreamVideo

@pytest.fixture
def video_server():
    vid_serv = VideoServer()
    return vid_serv

@pytest.fixture
def video_stream():
    str_vid = StreamVideo()
    return str_vid