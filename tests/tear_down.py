import shutil
import pytest
from pathlib import Path
import os

@pytest.fixture(scope='session', autouse=True)
def tear_down():
    """
    Removes the policy config file after each test.
    """
    path = Path(os.path.join(os.path.dirname(__file__), 'videos'))
    files = os.listdir(path)
    for file in files:
        _file = os.path.join(path, file)
        os.remove(_file)