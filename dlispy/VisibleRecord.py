from .RCReader import *
from .common import *

logger = myLogger("VisibleRecord")

from .LogicalRecordSegment import parseLRSegment


class VisibleRecord(object):
    """
    Visible Record consists of three parts in order:

    - Visible Record Length expressed in Representation Code UNORM

    - Two-byte Format version field

    - One or more complete Logical Record Segments

    """

    # Header attributes
    VERSION_FIXED_VALUE = 0xFF

    def __init__(self):
        self._len = None
        self._ff = None
        self._version = None
        self._startPos = 0
        self._restPos = 0
        self._lrSegList = []

    def __str__(self):
        return '\nVisibleRecord[Length={} Version={} startPos={}, remaining={}]'.format(
            self._len,
            self._version,
            self._startPos,
            self.remaining
        )

    @property
    def remaining(self):
        return self._len - self._restPos

    @property
    def lrSegList(self):
        return self._lrSegList


    @staticmethod
    def parse(fs):
        vr = VisibleRecord()

        vr._startPos = fs.tell()
        vr._len = readUNORM(fs)
        logger.debug("Visible Record Length:%s", vr._len)

        vr._ff = readUSHORT(fs)
        assert(vr._ff == 0xFF)

        myV = readUSHORT(fs)
        logger.debug("Format Version:%s", myV)
        if myV != DLIS_VERSION:
            raise Exception(
                'VisibleRecord, unsupported format version. Expected {}, but get {}, at file position'
                    .format(1, myV, fs.tell()))

        vr._version = myV
        vr._restPos = fs.tell() - vr._startPos

        while vr.remaining>0:
            currSeg = parseLRSegment(fs)

            vr._restPos += currSeg.segLen
            vr._lrSegList.append(currSeg)
            # insurance policy in case any bug when parsing LogicalRecordSegment
            assert(fs.tell() == currSeg.endPos)

        assert(fs.tell() == (vr._startPos + vr._len))

        return vr
