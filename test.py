from typing import Iterator, Tuple
from pprint import pprint
import sqlite3
import hashlib
import os

def scantree(path):
    """Recursively yield DirEntry objects for given directory."""
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            
            yield from scantree(entry.path)  # see below for Python 2.x
        else:
            yield entry


