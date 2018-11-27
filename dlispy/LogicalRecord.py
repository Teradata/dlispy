import io
from .RCReader import *
from .Component import *
from .common import endPos, myLogger

logger = myLogger("LogicalRecord")


def _find_attr(label, object):
    for attribute in object.attributes:
        if attribute.label == label:
            return attribute
    return None

def _find_attr_value(label, object):
    for attribute in object.attributes:
        if attribute.label == label:
            return attribute.value
    return None


class LogicalRecord(JsonAble):
    """
    A class represent Logical Record in RP66 V1: 
    """
    def toJSON(self):
        return {type(self).__name__: self.__dict__}


class EncryptedEFLR:
    """
    Represent an Encrypted EFLR which could be either public or private.
    TODO: Add more detail info about this LR, like Encryption Info
    """
    def __init__(self, lrType):
        """
        :type lrType:int
        :param lrType: Type of this LogicalRecord.
        """
        self.lrType = lrType


class EFLR(LogicalRecord):
    """
    A class represents Explicitly Formatted Logical Record
    """

    def __init__(self, set,  objects):
        """
        Construct a EFLR.

        :type set: Set
        :param set: The set belongs to this EFLR

        :type objects: list
        :param objects: List of objects in the set.
        """
        self.setName = set.name
        self.setType = set.type
        self.template = set.template
        self.objects = objects


class PublicEFLR(EFLR):
    """
    Represents all Public EFLR, LR types from 0(File Header) to 11 (Dictionary)
    """
    pass


class PublicEFLRType(Enum):
    """
    A ENUM class represents different public EFLR types.
    """

    FHLR = 0
    OLR = 1
    AXIS = 2
    CHANNL = 3
    FRAME = 4
    STATIC = 5
    SCRIPT = 6
    UPDATE = 7
    UDI = 8
    LNAME = 9
    SPEC = 10
    DICT = 12


class PublicEflrObject(Object):
    """
    Represents object in a specific type of EFLR.
    """
    def __init__(self, obj):
        """
        
        :param obj:
        """
        self._name = obj.name
        self._attributes = obj.attributes

    def getAttrValue(self, attrName):
        return _find_attr_value(attrName, self)

    def getAttr(self, attrName):
        return _find_attr(attrName, self)

    def toJSON(self):
        return {type(self).__name__: self.__dict__}


class IFLR(LogicalRecord):
    """
    Represents Indirectly formatted Logical Record
    """
    pass

class FileHeader(PublicEflrObject):
    """
    Represents object with set type "FILE-HEADER" in FHLR EFLR
    """
    SEQUENCE_NUMBER = 'SEQUENCE-NUMBER'
    ID = 'ID'


class FhlrEFLR(PublicEFLR):
    """File Header Logical record"""
    pass


class Origin(PublicEflrObject):
    """
    Represent objects within set "Origin" in Origin EFLR.
    """
    FILE_ID = 'FILE-ID'
    FILE_SET_NAME = 'FILE-SET-NUMBER'
    FILE_SET_NUMBER = 'FILE-SET-NUMBER'
    FILE_NUMBER = 'FILE-NUMBER'
    FILE_TYPE = 'FILE-TYPE'
    PRODUCT = 'PRODUCT'
    VERSION = 'VERSION'
    PROGRAMS = 'PROGRAMS'
    CREATION_TIME = 'CREATION-TIME'
    ORDER_NUMBER = 'ORDER-NUMBER'
    RUN_NUMBER = 'RUN-NUMBER'
    WELL_ID = 'WELL-ID'
    WELL_NUMBER = 'WELL-NUMBER'
    PRODUCER_CODE = 'PRODUCER-CODE'
    PRODUCER_NAME = 'PRODUCER-NAME'
    COMPANY =  'COMPANY'
    NAME_SPACE_NAME = 'NAME-SPACE-NAME'
    NAME_SPACE_VERSION = 'NAME-SPACE-VERSION'


class WellReferencePoint:
    """
    Represents object within set "WELL-REFERENCE-POINT" in Origin EFLR
    """
    PERMANENT_DATUM = 'PERMANENT-DATUM'
    VERTICAL_ZERO = 'VERTICAL-ZERO'
    PERMANENT_DATUM_ELEVATION = 'PERMANENT-DATUM-ELEVATION'
    ABOVE_PERMANENT_DATUM = 'ABOVE-PERMANENT-DATUM'
    MAGNETIC_DECLINATION = 'MAGNETIC-DECLINATION'
    COORDINATE_1_NAME = 'COORDINATE-1-NAME'
    COORDINATE_1_VALUE = 'COORDINATE-1-VALUE'
    COORDINATE_2_NAME = 'COORDINATE-2-NAME'
    COORDINATE_2_VALUE = 'COORDINATE-2-VALUE'
    COORDINATE_3_NAME = 'COORDINATE-3-NAME'
    COORDINATE_3_VALUE = 'COORDINATE-3-VALUE'

class OlrEFLR(PublicEFLR):
    """Represents Origin EFLR"""
    pass


class Axis(PublicEflrObject):
    """
    Represents object within set "AXIS" in Axis EFLR
    """
    AXIS_ID = 'AXIS-ID'
    COORDINATES = 'COORDINATES'
    SPACING = 'SPACING'


class AxisEFLR(PublicEFLR):
    """Represent Axis EFLR"""
    pass

class ChannelEFLR(PublicEFLR):
    """
    Represents Channel EFLR.
    """
    pass


class LongNameEFLR(PublicEFLR):
    """
    Represents Long Name EFLR.
    """
    pass

class LongName(PublicEflrObject):
    """
    Represents object within set "LONG-NAME" in LongName EFLR
    """
    GENERAL_MODIFIER = 'GENERAL-MODIFIER'
    QUANTITY = 'QUANTITY'
    QUANTITY_MODIFIER = 'QUANTITY-MODIFIER'
    ALTERED_FORM = 'ALTERED-FORM'
    ENTITY = 'ENTITY'
    ENTITY_MODIFIER = 'ENTITY-MODIFIER'
    ENTITY_NUMBER = 'ENTITY-NUMBER'
    ENTITY_PART = 'ENTITY-PART'
    ENTITY_PART_NUMBER = 'ENTITY-PART-NUMBER'
    GENERIC_SOURCE = 'GENERIC-SOURCE'
    SOURCE_PART = 'SOURCE-PART'
    SOURCE_PART_NUMBER = 'SOURCE-PART-NUMBER'
    CONDITIONS = 'CONDITIONS'
    STANDARD_SYMBOL = 'STANDARD-SYMBOL'
    PRIVATE_SYMBOL = 'PRIVATE-SYMBOL'


class Channel(PublicEflrObject):
    """
    Represents object within set "CHANNEL" in Channel EFLR
    """
    LONG_NAME = 'LONG-NAME'
    PROPERTIES = 'PROPERTIES'
    REPRESENTATION_CODE = 'REPRESENTATION-CODE'
    UNITS = 'UNITS'
    DIMENSION = 'DIMENSION'
    AXIS = 'AXIS'
    ELEMENT_LIMIT = 'ELEMENT-LIMIT'
    SOURCE = 'SOURCE'



class Path(PublicEflrObject):
    """
    Represents object within set "PATH" in Frame EFLR
    """
    FRAME_TYPE = 'FRAME-TYPE'
    WELL_REFERENCE_POINT = 'WELL-REFERENCE-POINT'
    VALUE = 'VALUE'
    BOREHOLE_DEPTH = 'BOREHOLE-DEPTH'
    VERTICAL_DEPTH = 'VERTICAL-DEPTH'
    RADIAL_DRIFT = 'RADIAL-DRIFT'
    ANGULAR_DRIFT = 'ANGULAR-DRIFT'
    TIME = 'TIME'
    DEPTH_OFFSET = 'DEPTH-OFFSET'
    MEASURE_POINT_OFFSET = 'MEASURE-POINT-OFFSET'
    TOOL_ZERO_OFFSET = 'TOOL-ZERO-OFFSET'


class Frame(PublicEflrObject):
    """
    Represents object within set "FRAME" in Frame EFLR
    """
    DESCRIPTION = 'DESCRIPTION'
    INDEX_MIN = 'INDEX-MIN'
    INDEX_MAX = 'INDEX-MAX'
    ENCRYPTED = 'ENCRYPTED'
    SPACING = 'SPACING'
    INDEX_TYPE = 'INDEX-TYPE'
    CHANNELS = 'CHANNELS'


class Zone(PublicEflrObject):
    """
    Represents object within type "ZONE" in Static EFLR
    """
    DESCRIPTION = 'DESCRIPTION'
    DOMAIN = 'DOMAIN'
    MAXIMUM = 'MAXIMUM'
    MINIMUM= 'MINIMUM'


class Parameter(PublicEflrObject):
    """
    Represents object within set "PARAMETER" in Static EFLR
    """
    LONG_NAME = 'LONG-NAME'
    DIMENSION = 'DIMENSION'
    AXIS = 'AXIS'
    ZONES = 'VALUES'
    VALUES = 'VALUES'


class Equipment(PublicEflrObject):
    """
    Represents object within set "EQUIPMENT" in Static EFLR
    """
    TRADEMARK_NAME = 'TRADEMARK-NAME'
    STATUS = 'STATUS'
    TYPE = 'TYPE'
    SERIAL_NUMBER = 'SERIAL-NUMBER'
    LOCATION = 'LOCATION'
    HEIGHT = 'HEIGHT'
    LENGTH = 'LENGTH'
    MINIMUM_DIAMETER = 'MINIMUM-DIAMETER'
    MAXIMUM_DIAMETER = 'MAXIMUM-DIAMETER'
    VOLUME = 'VOLUME'
    WEIGHT = 'WEIGHT'
    HOLE_SIZE = 'HOLE-SIZE'
    PRESSURE = 'PRESSURE'
    TEMPERATURE = 'TEMPERATURE'
    VERTICAL_DEPTH = 'VERTICAL-DEPTH'
    RADIAL_DRIFT = 'RADIAL-DRIFT'
    ANGULAR_DRIFT = 'ANGULAR-DRIFT'



class Tool(PublicEflrObject):
    """
    Represents object within set "Tool" in Static EFLR
    """
    DESCRIPTION = 'DESCRIPTION'
    TRADEMARK_NAME = 'TRADEMARK-NAME'
    GENERIC_NAME = 'GENERIC-NAME'
    PARTS = 'PARTS'
    STATUS = 'STATUS'
    CHANNELS = 'CHANNELS'
    PARAMETERS = 'PARAMETERS'


class Process(PublicEflrObject):
    """
    Represents object within set "PROCESS" in Static EFLR
    """
    DESCRIPTION = 'DESCRIPTION'
    TRADEMARK_NAME = 'TRADEMARK-NAME'
    VERSION = 'VERSION'
    PROPERTIES = 'PROPERTIES'
    STATUS = 'STATUS'
    INPUT_CHANNELS = 'INPUT-CHANNELS'
    OUTPUT_CHANNELS = 'OUTPUT-CHANNELS'
    INPUT_COMPUTATIONS = 'INPUT-COMPUTATIONS'
    OUTPUT_COMPUTATIONS = 'OUTPUT-COMPUTATIONS'
    PARAMETERS = 'PARAMETERS'
    COMMENTS = 'COMMENTS'


class Computation(PublicEflrObject):
    """
    Represents object within set "COMPUTATION" in Static EFLR
    """
    DESCRIPTION = 'DESCRIPTION'
    PROPERTIES = 'PROPERTIES'
    DIMENSION = 'DIMENSION'
    AXIS = 'AXIS'
    ZONES = 'ZONES'
    VALUES = 'VALUES'
    SOURCE = 'SOURCE'


class CalibrationMeasurement(PublicEflrObject):
    """
    Represents object within set "CALIBRATION-MEASUREMENT" in Static EFLR
    """
    PHASE = 'PHASE'
    MEASUREMENT_SOURCE = 'MEASUREMENT-SOURCE'
    TYPE = 'TYPE'
    DIMENSION = 'DIMENSION'
    AXIS = 'AXIS'
    MEASUREMENT = 'MEASUREMENT'
    SAMPLE_COUNT = 'SAMPLE-COUNT'
    MAXIMUM_DEVIATION = 'MAXIMUM-DEVIATION'
    STANDARD_DEVIATION = 'STANDARD-DEVIATION'
    BEGIN_TIME = 'BEGIN-TIME'
    DURATION = 'DURATION'
    REFERENCE = 'REFERENCE'
    STA = 'STA'
    PLUS_TOLERANCE = 'PLUS-TOLERANCE'
    MINUS_TOLERANCE = 'MINUS-TOLERANCE'


class CalibrationCoefficient(PublicEflrObject):
    """
    Represents object within set "CALIBRATION-COEFFICIENT" in Static EFLR
    """
    LABEL = 'LABEL'
    COEFFICIENTS = 'COEFFICIENTS'
    REFERENCES = 'REFERENCES'
    PLUS_TOLERANCE = 'PLUS-TOLERANCE'
    MINUS_TOLERANCE = 'MINUS-TOLERANCE'


class Calibration(PublicEflrObject):
    """
    Represents object within set "CALIBRATION" in Static EFLR
    """
    CALIBRATED_CHANNELS = 'CALIBRATED-CHANNELS'
    UNCALIBRATED_CHANNELS = 'UNCALIBRATED-CHANNELS'
    COEFFICIENTS = 'COEFFICIENTS'
    MEASUREMENT = 'MEASUREMENT'
    PARAMETERS = 'PARAMETERS'
    METHOD = 'METHOD'


class Group(PublicEflrObject):
    """
    Represents object within set "GROUP" in Static EFLR
    """
    DESCRIPTION = 'DESCRIPTION'
    OBJECT_TYPE = 'OBJECT-TYPE'
    OBJECT_LIST = 'OBJECT-LIST'
    GROUP_LIST = 'GROUP-LIST'
    

class Splice(PublicEflrObject):
    """
    Represents object within set "SPLICE" in Static EFLR
    """
    OUTPUT_CHANNELS = 'OUTPUT-CHANNELS'
    INPUT_CHANNELS = 'INPUT-CHANNELS'
    ZONES = 'ZONES'


class FrameEFLR(PublicEFLR):
    "Represents Frame EFLR"
    pass

def _getClassName(set_type):
    words = set_type.split('-')
    classname = ''
    for w in words:
        classname +=w.capitalize()
    return classname


class StaticEFLR(PublicEFLR):
    """Represents Static EFLR"""
    SET_TYPES = {'CALIBRATION', 'CALIBRATION-COEFFICIENT', 'CALIBRATION-MEASUREMENT', 'COMPUTATION',
                 'EQUIPMENT', 'GROUP','PARAMETER', 'PROCESS', 'SPICE', 'TOOL','ZONE'}


    @staticmethod
    def getInstance(set):
        """
        A factory method for Static EFLRs which supports different types of set, like Parameter, Tool, etc.

        :type set: Set
        :param set: The set insides this EFLR

        :return: A StaticEFLR instance.
        """
        if set.type in StaticEFLR.SET_TYPES:
            objectClassname = globals()[_getClassName(set.type)]
            return StaticEFLR(set, list(map(lambda obj: objectClassname(obj), set.objects)))
        else:
            return StaticEFLR(set, list(set.objects))
            # raise Exception('Unsupported Set Type for STATIC EFLR: {}'.format(set))
                

class Comment(PublicEflrObject):
    """object within set "COMMENT" in Script EFLR"""
    pass


class ScriptEFLR(PublicEFLR):
    """Represent Script EFLR"""
    pass


class Update(PublicEflrObject):
    """Object within set "UPDATE" in Update EFLR"""
    pass


class UpdateEFLR(PublicEFLR):
    """Represents Update EFLR"""
    pass


class NoFormat(PublicEflrObject):
    """
    Represents object with type "NO-FORMAT" in UDI EFLR
    """
    CONSUMER_NAME = 'CONSUMER-NAME'
    DESCRIPTION = 'DESCRIPTION'


class UdiEFLR(PublicEFLR):
    """Unformatted Data Identifier EFLR"""
    pass


class LongName(PublicEflrObject):
    """Long name object in LongName EFLR"""
    pass


class LNameEFLR(PublicEFLR):
    """Long Name EFLR"""
    pass


class SpecObject(PublicEflrObject):
    """objects in Spec EFLR"""
    pass

class DictObject(PublicEflrObject):
    """Objects in Dict EFLR"""
    pass


class SpecEFLR(PublicEFLR):
    """Specification EFLR"""
    pass


class DictEFLR(PublicEFLR):
    """Dictionary EFLR"""
    pass


class FrameData:
    """
    Represents object in FData IFLR.
    """
    def __init__(self, fr):
        self.frameNumber = fr
        self.slots = []


class UnformattedDataLR(IFLR):
    """Unformatted Data	"""
    def __init__(self, noformatObject, data):
        self.data = data
        self.noformatObject = noformatObject
        

class EoD(IFLR):
    """End of Data IFLR """
    def __init__(self, ddr, lr_type):
        self._frameTypeRef = ddr
        self._lrType = lr_type

    @property
    def frameTypeRef(self):
        """
        :return: Data Descriptor Reference of the sequence of IFLRs that is to be indicated ended
        """
        return self._frameTypeRef

    @property
    def lrType(self):
        """
        :return: the Logical Record Type of the sequence of IFLRs that has ended
        """
        return self._lrType


class PrivateEFLR(EFLR):
    pass

class PrivateEncryptedEFLR(PrivateEFLR):
    """Private Encrypted EFLR"""
    def __init__(self, encryptedPkg):
        self.producerCode = encryptedPkg.prodCode

class PrivateIFLR(IFLR):
    """Private IFLR"""
    # TODO
    pass

def nextRole(bStream):
    """Return next role in this byte stream, note the position of stream remains the same after this operation.
    :param bStream: byte stream 
    :return: ComponentRole next fole in the stream  
    """
    
    currPos = bStream.tell()
    desc = '{0:08b}'.format(readUSHORT(bStream))
    role = ComponentRole[desc[:3]]
    bStream.seek(currPos, io.SEEK_SET)
    return role

def parseObjects(bStream, template):
    """Parse all the objects in the current set based on given template.
    :param bStream: The stream.
    :param template: Define the schema of the object, like attribute list
    :return: A list of object. It will end until current byte stream (which only includes single set)
    """
    eof = endPos(bStream)
    objs = []
    while bStream.tell() < eof:
        obj = parseObject(bStream, template)
        logger.debug(obj)
        objs.append(obj)
    return objs


def parseObject(bStream, template):
    """Parse a single object
    :param bStream: Byte stream in memory
    :param template: Defines The object schema, like attribute list.
    :return: A Object
    """

    eof = endPos(bStream)
    desc = '{0:08b}'.format(readUSHORT(bStream))
    role = ComponentRole[desc[:3]]
    if role == OBJECT:
        logger.debug("parsing object")
        obj = Object()
        # assert(int(desc[3])) # object must have label
        obj._name = readOBNAME(bStream)
        i = 0
        while bStream.tell() < eof and nextRole(bStream) is not OBJECT:
            if i < len(template.attrList):
                attrRef = template.attrList[i]
                attr = parseAttrInObj(bStream, attrRef)
                if type(attr) is AbsentAttribute:
                    logger.debug("get absentAttr")
                obj._attributes.append(attr)
            else:
                attr = parseAttrInObjWithoutRef(bStream)
                if type(attr) is AbsentAttribute:
                    logger.debug("get absentAttr")
                obj._attributes.append(attr)
            i+=1
        # start to read attributes
        return obj
    else:
        raise Exception("Only object is allowed")



def parseTemplate(bStream):
    """Parse the Template in current byte stream, it terminates when meets an object.
    :param bStream: Byte stream
    :return: The template.
    """
    template = Template()
    eof = endPos(bStream)
    while True:
        currPos = bStream.tell()
        if currPos <eof:
            desc = '{0:08b}'.format(readUSHORT(bStream))
            bStream.seek(currPos, io.SEEK_SET)
            if ComponentRole[desc[:3]] == OBJECT:
                return template
            else:
                assert(int(desc[3])) # all components in Template must have label.
                template._attrList.append(parseAttributeInTemplate(bStream))
        else:
            logger.warning("Encounter a Set without Objects")
            break


def parseAttrInObj(bStream, attrRef):
    """Parse Single attribute in an object
    :param bStream: The byte stream
    :param attrRef: Attribute defination in Template.
    :return: The attribute in current object
    """
    # logger.debug("Attribute def:{}".format(attrRef))

    desc = '{0:08b}'.format(readUSHORT(bStream))
    role = ComponentRole[desc[:3]]
    if role == ATTRIB:
        attr = Attribute()
        attrRef.clone(attr)
    elif role == INVATR:
        attr = InvariantAttribute()
        attrRef.clone(attr)
    elif role == ABSATER:
        attr = AbsentAttribute(attrRef)
        return attr
    else:
        raise Exception("Only attribute is allowed")
    if int(desc[3]): # label
        attr._label = readIDENT(bStream)
    if int(desc[4]): # count
        attr._count = readUVARI(bStream)
    if int(desc[5]): # representation code
        attr._repCode = readUSHORT(bStream)
    if int(desc[6]):
        attr._units = readUNITS(bStream)

    if int(desc[7]):
        if attr._count> 1:
            attr._value =  [readByRC(attr._repCode, bStream) for i in range(attr._count)]
        else:
            attr._value =  readByRC(attr._repCode, bStream)

    # logger.debug(attr)
    return attr

def parseAttrInObjWithoutRef(bStream):
    """Parse Single attribute in an object
    :param bStream: The byte stream
    :param attrRef: Attribute defination in Template.
    :return: The attribute in current object
    """
    # logger.debug("Attribute def:{}".format(attrRef))

    desc = '{0:08b}'.format(readUSHORT(bStream))
    role = ComponentRole[desc[:3]]
    if role == ATTRIB:
        attr = Attribute()
    elif role == INVATR:
        attr = InvariantAttribute()
    elif role == ABSATER:
        attr = AbsentAttribute()
        return attr
    else:
        raise Exception("Only attribute is allowed")
    if int(desc[3]): # label
        attr._label = readIDENT(bStream)
    if int(desc[4]): # count
        attr._count = readUVARI(bStream)
    if int(desc[5]): # representation code
        attr._repCode = readUSHORT(bStream)
    if int(desc[6]):
        attr._units = readUNITS(bStream)

    if int(desc[7]):
        if attr._count> 1:
            attr._value =  [readByRC(attr._repCode, bStream) for i in range(attr._count)]
        else:
            attr._value =  readByRC(attr._repCode, bStream)
    return attr



def parseAttributeInTemplate(bStream):
    """Parse the attribute in current Template
    :param bStream: The byte stream
    :return: An attribute,
    """
    desc = '{0:08b}'.format(readUSHORT(bStream))
    role = ComponentRole[desc[:3]]
    if role == ATTRIB:
        attr = Attribute()
    elif role == INVATR:
        attr = InvariantAttribute()
    elif role == ABSATER:
        attr = AbsentAttribute()
        return attr
    else:
        raise Exception("Only attribute is allowed")
    if int(desc[3]): # label
        attr._label = readIDENT(bStream)
    if int(desc[4]): # count
        attr._count = readUVARI(bStream)
    if int(desc[5]): # representation code
        attr._repCode = readUSHORT(bStream)
    if int(desc[6]):
        attr._units = readUNITS(bStream)
    if int(desc[7]):
        if attr._count> 1:
            attr._channelValue =  [readByRC(attr._repCode, bStream) for i in range(attr._count)]
        else:
            attr._channelValue =  readByRC(attr._repCode, bStream)
    return attr


def parseSet(bStream):
    """Parse a set in current bStream, terminate when meet a Template
    :param bStream: The byte stream
    :return: A set
    """
    desc = '{0:08b}'.format(readUSHORT(bStream))
    role = ComponentRole[desc[:3]]
    if role == SET:
        mySet = Set()
    elif role == RDSET:
        mySet = RedundantSet()
    elif role == RSET:
        mySet = ReplacementSet
    else:
        raise Exception("Only set is allowed")
    assert(int(desc[3])) # set must have type
    mySet._type = readIDENT(bStream)
    if int(desc[4]):
        mySet._name = readIDENT(bStream)

    mySet.template = parseTemplate(bStream)
    mySet.objects = parseObjects(bStream, mySet.template)

    return mySet