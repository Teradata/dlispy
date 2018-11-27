import re
from .common import myLogger, readAsInteger, readAsString, readBytes, DLIS_VERSION



logger = myLogger("StorageUnitLabel")


class StorageUnitLabel(object):
    """Represent Logical File. Only RP66 V1 is supported"""
    # Length of "Storage Unit Label",

    LENGTH = 80
    SU_SEQNUM_LENGTH = 4
    DLIS_VERSION_LENGTH = 5
    SU_STRUCTURE_LENGTH = 6
    MAX_RECORD_LEN_LENGTH = 5
    SSI_LENGTH = 60
    # Storage unit structure
    SU_STRUCTURE_RECORD = 'RECORD'

    def __init__(self):
        """Constructor."""

        # Storage unit sequence number. An integer.
        self._susn = -1
        # Current support for v1. An integer.
        self._version = 0
        self._sus = None
        self._maxRecordLen = -1
        self._ssi = None

    def __str__(self):
        return '\nStorageUnitLabel[SUSN={} Vers={} SUS={} MaxRecordLen={} SSI={}]'.format(
            self._susn,
            self._version,
            self._sus,
            self._maxRecordLen,
            self._ssi
            )

    @staticmethod
    def parse(fs):
        sul = StorageUnitLabel()

        """ Start to parse the Logical File. The first part of a logical file is so called "Storage Unit Label" which follows following format:

        - Storage Unit Seq Number: 4xChar Integer.

        - DLIS Ver: 5xChar string, follows  "Vn.mm" format, "n": one-digit major version number, "mm": two-digits minor version only support "v1.00" for now.

        - Storage Unit Structure: 6xChar string, left with trailing blanks if needed. Only support option is "RECORD"

        - Maximum Record Length: non-negative integer, 5xChar, with preceding blanks or zeors. A value 0 indicates max length of a record is unknow.

        - Storage Set Identifier: 60xChar."""
        
        # First 4 bytes are Storage unit sequence number
        value = readBytes(fs, StorageUnitLabel.SU_SEQNUM_LENGTH)
        try:
            sul._susn = int(value)
        except ValueError:
            raise Exception('Fail to interpret SequenceNumber of SU from value [{}]'.format(value))
        logger.debug("Storage Unit Sequence Number:%s", sul._susn)

        # Next 5 bytes are RP66 version and format edition in the form "VN.nn".
        value = readAsString(fs, StorageUnitLabel.DLIS_VERSION_LENGTH)
        if re.match(r'V1.[0-9][0-9]', value) is None:
            raise Exception('Only supported DLIS version is  V1.xx, but get {}'.format(value))
        sul._version = int(value[1:2])
        logger.debug("DLIS Version:%s", sul._version)

        # Next 6 bytes is the Storage unit structure, only supported option in v1 is "RECORD"
        sul._sus = readAsString(fs, StorageUnitLabel.SU_STRUCTURE_LENGTH)
        if sul._sus != StorageUnitLabel.SU_STRUCTURE_RECORD:
            raise Exception('Unsupported Storage Unit Structure in V1: {} '.format(sul._sus))
        logger.debug("Storage Unit Structure:%s", sul._sus)

        # Read the max record length (5 bytes)
        sul._maxRecordLen = readAsInteger(fs, StorageUnitLabel.MAX_RECORD_LEN_LENGTH)
        logger.debug("Maximum Record Length:%s", sul._maxRecordLen)

        # Finally the Storage Set Identifier (60 bytes) that is common to both versions
        sul._ssi = readAsString(fs, StorageUnitLabel.SSI_LENGTH)
        logger.debug("Storage Set Identifer:%s", sul._ssi)
        assert(StorageUnitLabel.LENGTH == fs.tell())
        return sul
