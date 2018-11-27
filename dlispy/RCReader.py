import datetime
from enum import Enum
from .common import JsonAble, readBytes
from struct import Struct


# RP66 V1 Representation code use big-endian.

def _read_struct(stream, _struct):
    """
    Read a struct from a given stream.
    """
    b = readBytes(stream, _struct.size)
    if len(b) != _struct.size:
        raise Exception('Not enough bytes left')
    return _struct.unpack(b)

S_FSHORT = Struct('>h')

def readFSHORT(stream):
    """
    Read FSHORT

    :type stream: FileIO or ByteIO
    :param stream: the stream object, could be either FileIO or ByteIO

    :return: The result
    :rtype: int
    """
    return _read_struct(stream, S_FSHORT)


S_FSINGL = Struct('>f')
def readFSINGL(stream):
    """
    read FSINGL from stream

    :type stream: FileIO or ByteIO
    :param stream: The stream to read

    :return: the result.
    :rtype: float
    """
    return _read_struct(stream, S_FSINGL)[0]


S_FSING1 = Struct('>ff')
class FSING1(JsonAble):
    """
    FSING1, Validated Single Precision Floating Point with confidence interval of [value - bound, value + bound]
    """
    def __init__(self, theStream):
        """Constructor from a stream."""
        self.value, self.bound = S_FSING1.unpack(theStream.read(S_FSING1.size))

    def __eq__(self, other):
        return self.value == other.value and self.bound == other.bound


#TODO: untested
def readFSING1(stream):
    """
    Read FSING1.

    :type stream: FileIO or ByteIO
    :param stream: The stream object to read from.


    :return: The value.
    :rtype: FSING1
    """
    # raise Exception("FSING1 not supported")
    return FSING1(stream)


S_FSING2 = Struct('>fff')
class FSING2(JsonAble):
    """
    Two-Way Validated Single Precision Floating Point with a confidence interval of
    [V - A, V + B].
    """
    def __init__(self, stream):
        self.V, self.A, self.B = S_FSING2.unpack(stream.read(S_FSING2.size))


    def __eq__(self, other):
        return self.V == other.V \
               and self.A == other.A \
               and self.B == other.B

    def toJSON(self):
        return dict(V=self.V, A=self.A, B=self.B)


#TODO: untested
def readFSING2(stream):
    """
    Read FSING2 from stream

    :type stream: FileIO or ByteIO
    :param stream: stream to be read

    :return: the result
    :rtype: FSING2
    """
    # raise Exception("FSING2 not supported")
    return FSING2(stream)


#TODO: untested
def readISINGL(stream):
    """
    Read ISINGL from stream

    :type stream: FileIO or ByteIO
    :param stream: stream to be read

    :return: the result
    :rtype: float

    """
    # raise Exception("ISINGL not supported")
    return _read_struct(stream, Struct('>i'))


#TODO: untested
def readVSINGL(stream):
    """
    Read VSINGL from given stream

    :type stream: FileIO or ByteIO
    :param stream: stream to be read

    :return: result
    :rtype: float

    """
    # raise Exception("VSINGL not supported")
    return _read_struct(stream, Struct('>i'))


S_FDOUBL = Struct('>d')
def readFDOUBL(stream):
    """
    Read FDOUBL from given stream

    :type stream: FileIO or ByteIO
    :param stream: stream to be read

    :return: Result.
    :rtype: float
    """
    return _read_struct(stream, S_FDOUBL)[0]



S_FDOUB1 =  Struct('>dd')
class FDOUB1(JsonAble):

    """
    Validated Double Precision Floating Point with a confidence interval of [V - A, V + A].
    """

    def __init__(self, stream):
        """
        Constructor a FDOUB1 from a stream.
        :type stream: FileIO or ByteIO
        :param stream: stream to be read
        """

        self.V, self.A = S_FDOUB1.unpack(stream.read(S_FDOUB1.size))

    def __eq__(self, other):
        return self.V == other.V and self.A == other.A

    def toJSON(self):
        return dict(V=self.V, A=self.A)

def readFDOUB1(stream):
    """
    Read FDOUB1 from given stream
    :type stream: FileIO or ByteIO
    :param stream: stream to be read

    :return: Result.
    :rtype: FDOUB1
    """
    return FDOUB1(stream)


S_FDOUB2 = Struct('>ddd')
class FDOUB2(JsonAble):
    """
    Two-Way Validated Double Precision Floating Point with a confidence interval of [V - A, V + B].
    """
    def __init__(self, stream):
        """Constructor from a stream."""
        self.V, self.A, self.B = S_FDOUB2.unpack(stream.read(S_FDOUB2.size))

    def __eq__(self, other):
        return self.V == other.V \
               and self.A == other.A \
               and self.B == other.B

    def toJSON(self):
        return dict(V=self.V, A=self.A, B=self.B)


def readFDOUB2(stream):
    """
    Read FDOUB2 from given stream

    :type stream: FileIO or ByteIO
    :param stream: Where to read

    :return: Result
    :rtype: FDOUB2
    """

    return FDOUB2(stream)


S_CSINGL = Struct('>ff')
def readCSINGL(stream):
    """
    Read Single Precision Complex.

    :type stream: FileIO or ByteIO
    :param stream: The Stream.

    :return: result
    :rtype: complex

    """
    return complex(S_CSINGL.unpack(stream.read(S_CSINGL.size)))


S_CDOUBL = Struct('>dd')
def readCDOUBL(stream):
    """
    Read Double Precision Complex from stream

    :type stream: FileIO or ByteIO
    :param stream: Where to read from

    :return: result
    :rtype: complex
    """
    return complex(S_CDOUBL.unpack(stream.read(S_CDOUBL.size)))


S_SSHORT = Struct('>b')
def readSSHORT(stream):
    """
    Read short signed integer

    :type stream: FileIO or ByteIO
    :param stream: Where to read from

    :return: result
    :rtype: int     
    """
    return _read_struct(stream, S_SSHORT)[0]


S_SNORM = Struct('>h')
def readSNORM(stream):
    """
    Read Normal Signed Integer
    
    :type stream: FileIO or ByteIO
    :param stream: Where to read from

    :return: result
    :rtype: int
    """
    return _read_struct(stream, S_SNORM)[0]


S_SLONG =  Struct('>i')
def readSLONG(stream):
    return _read_struct(stream, S_SLONG)[0]

S_USHORT =   Struct('>B')
def readUSHORT(stream):
    """
    read short unsigned integer from given stream

    :type stream: FileIO or BytesIO
    :param stream: Where to read from

    :return: result
    :rtype: int
    """
    return _read_struct(stream, S_USHORT)[0]

S_UNORM = Struct('>H')
def readUNORM(stream):
    """
    read Normal Unsigned Integer from given stream

    :type stream: FileIO or BytesIO
    :param stream: Where to read from

    :return: result
    :rtype: int
    """
    return _read_struct(stream, S_UNORM)[0]

S_ULONG = Struct('>I')
def readULONG(stream):
    """
    read Long Unsigned Integer from given stream

    :type stream: FileIO or BytesIO
    :param stream: Where to read from

    :return: result
    :rtype: int
    """
    return _read_struct(stream, S_ULONG)[0]



def readUVARI(stream):
    """
    Reads a Variable-Length Unsigned Integer from stream

    :type stream: FileIO or BytesIO
    :param stream: Where to read from

    :return: result
    :rtype: int

    """
    b = stream.read(1)[0]
    if b & 0x80:
        if b & 0x40:
            b &= 0x3F
            for i in range(3):
                b <<= 8
                b |= stream.read(1)[0]
        else:
            b &= 0x7F
            b <<= 8
            b |= stream.read(1)[0]
    return b


def readIDENT(stream):
    """
    Read a Variable-Length Identifier from given stream. Note: some of DLIS file vendor doesn't follow the standard,
    for example whitespace is included also some not of non ASCII char are included, so in case it failed to decode with
    ASCII, we will also try with CP1252.

    :type stream: FileIO or BytesIO
    :param stream: Where to read from

    :return: result
    :rtype: str
    """
    l = stream.read(1)[0]
    payload = stream.read(l)
    try:
        return payload.decode('ascii')
    except UnicodeDecodeError:
        return payload.decode('cp1252')


def readASCII(stream):
    """
    Read ASCII.

    :type stream: FileIO or BytesIO
    :param stream: Where to read from

    :return: result
    :rtype: str

    """
    l = readUVARI(stream)
    payload = stream.read(l)
    try:
        return payload.decode('ascii')
    except UnicodeDecodeError:
        # Some DLIS file contains some special char which is out of ASCII, try cp1252 instead.
        try:
            return payload.decode('cp1252')
        except UnicodeDecodeError:
            return payload.decode('iso-8859-1')



class TZ(Enum):
    """A enum class to define different type of timezone info in RP66, note: it is different from timezone in python"""
    LocalStandard = 0
    LocalDaylightSavings = 1
    GreenwichMeanTime = 2

    def toJSON(self):
        return {'timezone':self.name}


S_DTIME = Struct('>BBBBBBH')


class DTime(JsonAble):
    """
    Represent DTime object.
    Attributes:

        time  - time. The actual time info
        tzone - TZ. Time zone info.

    """
    YEAR_OFFSET = 1900

    def __init__(self, stream):
        y, tz_m, d, h, min, s, ms = S_DTIME.unpack(stream.read(S_DTIME.size))
        # Now fix various fields
        y += self.YEAR_OFFSET
        mon = tz_m & 0xF
        self.tzone = TZ(tz_m >> 4)
        self.time = datetime.datetime(y, mon, d, h, min, s, ms * 1000)

    def __str__(self):
        return "Dtime[time:{} timeZone:{}]".format(self.time,self.tzone)

    def toJSON(self):
        return dict(time=str(self.time), tzone=self.tzone)


def readDTIME(stream):
    """
    Read DTIME

    :type stream: FileIO or BytesIO
    :param stream: Where to read from

    :return: result
    :rtype: DTime
    """

    return DTime(stream)


def readORIGIN(stream):

    """
    Reads a ORIGIN from stream which must have read(n) implemented that returns a single unsigned byte.
    """
    return readUVARI(stream)


class ObName(JsonAble):
    """
    Represent Object Name
    Attributes:

        origin - int
        copy - int
        identifier - str
    """

    def __init__(self, stream = None):
        if stream is not None:
            self.origin = readORIGIN(stream)
            self.copy = readUSHORT(stream)
            self.identifier = readIDENT(stream)

    def __eq__(self, other):
        return self.identifier == other.identifier and self.origin == other.origin and self.copy == other.copy

    def __hash__(self):
        return hash((self.identifier, self.origin, self.copy))

    def __str__(self):
        return "OBNAME[origin:{} copy:{} identifier:{}]".format(self.origin, self.copy, self.identifier)

    @staticmethod
    def instance(origin, copy, identifier):
        """
        Create a new ObName instance with given parameter

        :type origin: int

        :type copy: int

        :type identifier: str

        :return: A new instance.
        :rtype: ObName
        """
        newInstance = ObName()
        newInstance.origin = origin
        newInstance.copy = copy
        newInstance.identifier = identifier
        return newInstance


def readOBNAME(stream):
    """
    Read object name

    :type stream: FileIO or BytesIO
    :param stream: Where to read from

    :return: result
    :rtype: ObName

    """
    return ObName(stream)


class ObjRef(JsonAble):
    """"
    Represent Object reference.
    Attributes:

        type - str
        origin - int.
        copy - int
        identifier - str

    """
    def __init__(self, stream):
        self.type = readIDENT(stream)
        self.origin = readORIGIN(stream)
        self.copy = readUVARI(stream)
        self.identifier = readIDENT(stream)


def readOBJREF(stream):
    """
    Read a Object reference.

    :type stream: FileIO or BytesIO
    :param stream: Where to read from

    :return: result
    :rtype: ObjRef
    """
    return ObjRef(stream)


class ATTREF(JsonAble):
    """
    Represent Attribute reference object.

    Attributes:
        type - str.
        origin - int.
        copy - int.
        identifier - str.
        label - str.

    """
    def __init__(self, stream):
        """Constructor from a stream."""
        self.type = readIDENT(stream)
        self.origin = readORIGIN(stream)
        self.copy = readUVARI(stream)
        self.identifier = readIDENT(stream)
        self.label = readIDENT(stream)


#TODO: not tested with sample data
def readATTREF(stream):
    """
    Read Attribute Reference

    :type stream: FileIO or BytesIO
    :param stream: Where to read from

    :return: result
    :rtype: ATTREF

    """
    return ATTREF(stream)

S_STATUS = Struct('>B')
def readSTATUS(stream):
    """
    Read Boolean Status Value from given stream, if return value == 1, it means "Value", "ALLOWED", "TRUE", "ON", if return value
    == 0, it means "DISALLOWED", "FALSE", or "OFF"

    :type stream: FileIO or BytesIO
    :param stream: Where to read from

    :return: result
    :rtype: int
    """
    return _read_struct(stream, S_STATUS)[0]

def readUNITS(stream):
    """
    Read units from given stream

    :type stream: FileIO or BytesIO
    :param stream: Where to read from

    :return: result
    :rtype: str
    """
    return readASCII(stream)


CODE_TO_RC = {1:'FSHORT',
              2: 'FSINGL',
              3: 'FSING1',
              4: 'FSING2',
              5: 'ISINGL',
              6: 'VSINGL',
              7: 'FDOUBL',
              8: 'FDOUB1',
              9: 'FDOUB2',
              10: 'CSINGL',
              11: 'CDOUBL',
              12: 'SSHORT',
              13: 'SNORM',
             14: 'SLONG',
             15: 'USHORT',
             16: 'UNORM',
             17: 'ULONG',
             18: 'UVARI',
             19: 'IDENT',
             20: 'ASCII',
             21: 'DTIME',
             22: 'ORIGIN',
             23: 'OBNAME',
             24: 'OBJREF',
             25: 'ATTREF',
             26: 'STATUS',
             27: 'UNITS'}

RC_TO_CODE =  {v: k for k, v in CODE_TO_RC.items()}


READ_RC_METHOD = tuple(
    [globals()['read'+k] for k, _ in RC_TO_CODE.items()]
)


def readByRC(c, stream):
    """Given an Rep code in integer, read a single value from stream."""
    if c < 1 or c > len(RC_TO_CODE.items()):
        raise Exception('Unexpected rc code :{}'.format(c))

    # index of READ_RC_METHOD starts from 0 but code starts from 1
    f = globals()['read'+CODE_TO_RC[c]]
    return f(stream)