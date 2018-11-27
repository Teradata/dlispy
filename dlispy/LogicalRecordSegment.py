import io

from .common import myLogger, fs_seek_start, fs_seek_current
from .RCReader import *

logger = myLogger("LogicalRecordSegment")


LAZY_LOAD = True
class LogicalRecordSegment(object):
    """
    Represent Logical Record Segment.
    """

    def __init__(self):
        self._startPos = 0
        self._segLen = 0
        # Segment attributes
        # Type of Logical record (version 1 only). Otherwise reserved bits in v2.
        self._lrType = None
        # An Encryption.EncryptionPacketBase
        self._encryptPkt = None
        # Length of the available data in a particular segment
        # This includes the padding bytes (if any).
        self._dataLen = 0
        # Optional fields in the trailer
        self._padCount = 0
        self._checksum = None
        self._attrs = None
        self._trailerLen = 0
        self._body = None
        self._dataStartPos = 0


    def __str__(self):
        return 'LogicalRecordSegment[len:{} isEFLR:{} hasPredecessor:{} hasSuccessor:{} encrypted:{} ' \
               'hasEncryptPkt:{} hasCheckSum:{} hasTrailLen:{} hasPad:{} lrType:{}]'.format(
            self._segLen,
            self.isEFLR,
            self.hasPred,
            self.hasSucc,
            self.encrypted,
            self.hasEncryptionPkt,
            self.hasChecksum,
            self.hasTrailingLength,
            self.hasPadding,
            self.lrType)


    @property
    def startPos(self):
        return self._startPos

    @property
    def endPos(self):
        return self._startPos+self._segLen


    @property
    def segLen(self):
        return self._segLen


    @property
    def isEFLR(self):
        return int(self._attrs[0]) == 1


    @property
    def hasPred(self):
        """True if the segment has a predecessor segment."""
        return int(self._attrs[1]) == 1

    @property
    def hasSucc(self):
        """True if the segment has a successor segment."""
        return int(self._attrs[2]) == 1

    @property
    def encrypted(self):
        return int(self._attrs[3]) == 1


    @property
    def hasEncryptionPkt(self):
        return int(self._attrs[4]) == 1


    @property
    def hasChecksum(self):
        return int(self._attrs[5]) == 1


    @property
    def hasTrailingLength(self):
        return int(self._attrs[6]) == 1


    @property
    def hasPadding(self):
        return int(self._attrs[7]) == 1


    @property
    def hasTrailer(self):
        return self.hasPadding or self.hasChecksum or self.hasTrailingLength

    def readBody(self, fs):
        if self._body is None:
            fs.seek(self._dataStartPos, io.SEEK_SET)
            r = bytearray()
            r.extend(readBytes(fs, self._dataLen))
            self._body =  bytes(r)
        return self._body

    @property
    def lrType(self):
        return self._lrType

    @property
    def trailerLen(self):
        return self._trailerLen


def _checkLrSegLen(len):
    assert(len %2 == 0)
    assert(len>=16)


def _readHeader(fs, lrSeg):
    """
    Read the head of a Logical Record Segment
    :param fs: The file stream
    :param lrSeg: The segment object
    :return: Nothing returned, the segment object is updated directly.
    """
    lrSeg._startPos = fs.tell()
    lrSeg._segLen = readUNORM(fs)
    _checkLrSegLen(lrSeg._segLen)
    myAttr = readUSHORT(fs)
    lrSeg._attrs =  '{0:08b}'.format(myAttr)
    # logger.debug(lrSeg._attrs)
    lrSeg._lrType = readUSHORT(fs)

    # now fs points to either encryption packet or body.

    # 2 bytes for LR seg length, 1 byte for LR seg attr and 1 byte for LR type.
    lrSeg._dataLen = lrSeg._segLen - 4

    _getTrailerLenth(fs, lrSeg)
    lrSeg._dataLen -= lrSeg.trailerLen

    # Handle encryption
    if lrSeg.hasEncryptionPkt:
        lrSeg._encryptPkt = EncryptionPacket(fs)
        lrSeg._dataLen -= len(lrSeg._encryptPkt)
    else:
        lrSeg._encryptPkt = None
    if lrSeg.encrypted is False and lrSeg._dataLen < 0:
        raise Exception('Illegal negative data length of {:d}'.format(lrSeg._dataLen))


def _readTrailer(fs, lrSeg):
    """
    Read the Trailer of a Logical Record Segment
    :param fs: The file stream
    :param lrSeg: The segment object
    :return: Nothing returned, the segment object is updated directly.
    """
    if lrSeg.hasTrailer:
        if lrSeg.hasPadding:
            fs_seek_current(fs, lrSeg._padCount)
        if lrSeg.hasChecksum:
            lrSeg._checksum = readUNORM(fs)
        else:
            lrSeg._checksum = None
        if lrSeg.hasTrailingLength:
            assert(readULONG(fs) == lrSeg._segLen)


def _readBody(fs, lrSeg):
    """
    Read the body of LogicalRecordSegment, if it is part of an EFLR, then read it directly, otherwise,
    just read its index.
    :param fs:
    :param lrSeg:
    :return:
    """
    if lrSeg.isEFLR is False or (lrSeg.isEFLR and lrSeg.encrypted):
        lrSeg._dataStartPos = fs.tell()
        fs.seek(lrSeg._dataLen, io.SEEK_CUR)
    else:
        r = bytearray()
        r.extend(readBytes(fs, lrSeg._dataLen))
        lrSeg._body = bytes(r)


def parseLRSegment(fs):
    """
    Parse a Logical Record Segment
    :param fs: The file stream
    :return: The logical record segment object
    """
    lrSeg = LogicalRecordSegment()
    _readHeader(fs, lrSeg)
    _readBody(fs, lrSeg)
    _readTrailer(fs, lrSeg)
    logger.debug(lrSeg)
    return lrSeg


def _getTrailerLenth(fs, lrSeg):
    """
    Compute total length of trailer including padding (optional),
    checksum and duplicated LR Segment length at the end.
    """
    lrSeg._trailerLen = 0
    if lrSeg.hasTrailingLength:
        lrSeg._trailerLen +=2
    if lrSeg.hasChecksum:
        lrSeg._trailerLen +=2
    if lrSeg.hasPadding:
        currPos = fs.tell()

        padCountPos = lrSeg.endPos-1
        if lrSeg.hasTrailingLength:
            if lrSeg.hasChecksum:
                padCountPos -= 4
            else:
                padCountPos -= 2
        else:
            if lrSeg.hasChecksum:
                padCountPos -= 2
        # move to the position of pad count byte.
        fs_seek_start(fs, padCountPos)
        lrSeg._padCount = readUSHORT(fs)
        assert(lrSeg._padCount<=255)
        # logger.debug("PadCount:{}".format(lrSeg._padCount))
        # move back to the original position
        fs_seek_start(fs, currPos)
    lrSeg._trailerLen += lrSeg._padCount
    # logger.debug("Trailer length:{}".format(lrSeg._trailerLen))


class EncryptionPacket(object):
    """
    Represent EncryptionPacket in LogicalRecordSegment.
    """

    # Rep code UNORM
    length = None
    # This is the organization code of the group responsible for the computer
    # program that encrypted the record (see Appendix A). This field is required.
    # Rep code ULONG
    prodCode = None
    payload = None
    LENGTH_UNORM = 2

    def __len__(self):
        return self.length


    def __init__(self, fs):
        self.length = readUNORM(fs)
        self.prodCode = readUNORM(fs)
        payLen = self.length - self.LENGTH_UNORM - self.LENGTH_UNORM
        if payLen < 0:
            raise Exception('Negative encryption payload of {:d}'.format(payLen))
        self.payload = fs.read(payLen)