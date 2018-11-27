import fnmatch
import json
import logging
import os
import io


DLIS_VERSION = 1


def myLogger(module_name):
    logger = logging.getLogger(module_name)
    return logger


def readAsString(fs, n):
    """Reads exactly n bytes and returns them as str."""
    b_value = readBytes(fs, n)
    return b_value.decode('ascii')


def readBytes(fs, n):
    """Reads exactly n bytes and returns them."""
    r = fs.read(n)
    if len(r) != n:
        raise Exception('Can not read {} bytes only {} left'.format(n, len(r)))
    return r


def readAsInteger(fs, n):
    """
    Reads n bytes and returns them as an integer.
    """
    b = fs.read(n)
    if len(b) != n:
        raise Exception('Can not read {} bytes only {}'.format(n, len(b)))
    try:
        r = int(b)
    except ValueError:
        raise Exception('Can not determine integer RP66 version number from {}'.format(b))
    return r



def fs_seek_start(fs, offset):
    """Seeks the file to n bytes from beginning of the file."""
    assert (fs is not None)
    assert(offset >= 0)
    fs.seek(offset, io.SEEK_SET)


def endPos(stream):
    """
    :param stream: File stream
    :return: The end position of given stream
    """

    currPos = stream.tell()
    stream.seek(0, io.SEEK_END)
    endPos = stream.tell()
    stream.seek(currPos, io.SEEK_SET)
    return endPos


def fs_seek_current(fs, offset):
    """Seeks the file to n bytes from current position."""
    assert (fs is not None)
    assert(offset >= 0)
    fs.seek(offset, io.SEEK_CUR)


class switch(object):
    """
    Since python doesn't support switch, this is a syntax sugar for it
    """
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration

    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args: # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False


class ComplexEncoder(json.JSONEncoder):
    """
    A json encoder for complex object.
    """
    def default(self, obj):
        if hasattr(obj,'toJSON'):
            return obj.toJSON()
        else:
            return json.JSONEncoder.default(self, obj)

class JsonAble:
    """
    Super class for any class which should support json serialization
    """
    def toJSON(self):
        return self.__dict__


def convert_bytes(num):
    """
    this function will convert bytes to MB.... GB... etc
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0


def file_size(file_path):
    """
    this function will return the file size
    """
    if os.path.isfile(file_path):
        file_info = os.stat(file_path)
        return convert_bytes(file_info.st_size)


def _find_files(directory, patterns):
    for root, dirs, files in os.walk(directory):
        for basename in files:
            for pattern in patterns:
                if fnmatch.fnmatch(basename, pattern):
                    filename = os.path.join(root, basename)
                    yield filename