import csv
import json
import os

from .LogicalRecord import *
from .Component import Object
from .common import switch, myLogger, endPos, ComplexEncoder, JsonAble
import collections
from . import RCReader as reader

logger = myLogger('LogicalFile')


SimpleFrame = collections.namedtuple('SimpleFrame', 'ObName ChannelNames Channels Encrypted')
SimpleChannel = collections.namedtuple('SimpleChannel', 'ObName RepCode Dimension Units NumOfValue')


class LogicalFile(JsonAble):
    """Represent Logical File

    Attributes:
        eflrList    -   The list of EFLRs

        frameDataDict   -   A dict with key as frame name and value is a list of FrameData for this frame.

        noformList  -   All the noformat IFLR in this Logical file.
    """

    def __init__(self, eflrSegList, iflrSegList, fs, eflrOnly = False):
        """
        Parse a Logical file.
        
        :type eflrSegList: list
        :param eflrSegList: all the eflr segments list

        :type iflrSegList: list
        :param iflrSegList: all the iflr segments list

        :type fs: FileIO
        :param fs: File stream of the original DLIS file. Since the body part of IFLR segment will be loaded when needed, so we still need the file stream.

        :type eflrOnly: bool
        :param eflrOnly: If only parse EFLR. When it is true, only EFLR is loaded in this Logical File.
        """

        self.eflrList = []
        self.simpleFrames = {}
        self.simpleChannels = {}
        self.frameDataDict = {}
        self.noformList = []

        logger.info("Start parsing %s EFLR Segments", len(eflrSegList))
        tmpEflrSegList = []
        # First, parse all EFLRs.
        for eflrSeg in eflrSegList:
            logger.debug(eflrSeg)
            tmpEflrSegList.append(eflrSeg)
            if eflrSeg.hasSucc is False:
                _check_lr_seg(tmpEflrSegList)
                self._parseEFLR(tmpEflrSegList, fs = fs)
                tmpEflrSegList.clear()
        logger.info("End parsing EFLR Segments, in total %s LRs ", len(self.eflrList))

        self.iflrSegList = iflrSegList

        if eflrOnly is False:
            self.loadIFLR(fs)

    def loadIFLR(self, fs):
        """
        A method to load all the IFLRs in this logical file. This can be called if eflrOnly is set to False when created.
        
        :return: None. But the frameDataDict attribute will be loaded.
        """
        logger.info("Start parsing %s IFLR Segments", len(self.iflrSegList))
        tmpIflrSegList = []
        for iflrSeg in self.iflrSegList:
            tmpIflrSegList.append(iflrSeg)
            if iflrSeg.hasSucc is False:
                # _check_lr_seg(tmpIflrSegList)
                self._parseIFLR(tmpIflrSegList, fs = fs)
                tmpIflrSegList.clear()


    def _dump(self, path, eflrOnly = False):
        """
        Dump current logical file as a combination of a json file which includes all Logical record and several csv
        each representing frame data for a particular frame

        :type path: str
        :param path: which directory to dump the file

        :type eflrOnly: bool
        :param eflrOnly: if only dump all EFLRs

        :return: None

        """
        if not os.path.exists(path):
            os.makedirs(path)
        self._writeJson(path)
        print(eflrOnly)
        if eflrOnly is False:
            print("dump")
            self._writeCsv(path)
            if len(self.noformList) == 0:
                return
            udlrPath = os.path.join(path, 'UnformattedDataLogicalRecords')
            if not os.path.exists(udlrPath):
                os.makedirs(udlrPath)
            for no in self.noformList: # type:UnformattedDataLR
                name = "{}_{}_{}".format(no.noformatObject.name.origin,
                                         no.noformatObject.name.copy, no.noformatObject.name.identifier)
                output_json = os.path.join(udlrPath, "{}.json".format(name))
                with open(output_json, 'w') as outfile:
                    data = {'CONSUMER-NAME':no.noformatObject.getAttrValue(NoFormat.CONSUMER_NAME),
                            'DESCRIPTION':no.noformatObject.getAttrValue(NoFormat.DESCRIPTION) }
                    json.dump(data, fp=outfile)

                output_bytes = os.path.join(udlrPath, name)
                with open(output_bytes, 'wb') as outfile:
                    outfile.write(no.data)


    def _writeJson(self, path):
        """
        Dump all logical record as a json file

        :param path: which directory to dump the file

        :return: None
        """
        file_name = '{}.json'.format(self.id.strip())
        output_file = os.path.join(path, file_name)
        with open(output_file, 'w') as outfile:
            json.dump(self.toJSON(), cls=ComplexEncoder, fp=outfile)


    def toJSON(self):
        """

        :return: A dict which only includes EFLR lists.
        
        """
        return {'ExplicitlyFormattedLogicalRecords': self.eflrList}


    def _writeCsv(self, path):
        """
           Dump all frame as csv files,  each csv representing frame data for a particular frame

           :param path: which directory to dump the file
           
           :return: None
           """
        for frameName, frameDatas in self.frameDataDict.items():
            frame = self.simpleFrames[frameName]
            file_name = '{}_{}_{}.csv'.format(frameName.origin, frameName.copy, frameName.identifier)
            output_file = os.path.join(path, file_name)
            channels = frame.Channels
            columnNames = list(map(lambda channel: channel.ObName.identifier+(', '+channel.Units if channel.Units is not None else ''), channels))
            with open(output_file, 'w') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=['frameNumber']+columnNames)
                writer.writeheader()
                for fData in frameDatas:
                    fData = fData
                    writer.writerow({**{'frameNumber':fData.frameNumber}, **dict(zip(columnNames, fData.slots))})

    def __str__(self):
        return "LogicalFile[SeqNum:{} id:{} NumOfEFLR:{}]". \
            format(self.seqNum, self.id, len(self.eflrList))

    def _getSimpleChannelsFromFrame(self, frameName):
        """
        Retrieve Simple Channels with given frame name.

        :type frameName: ObName
        :param frameName: The target framename

        :return: the simple channels.

        """

        simpleFrame = self.simpleFrames[frameName]
        # Another lazy loading, if channel is not already loaded, then load them
        if len(simpleFrame.Channels) == 0 and len(simpleFrame.ChannelNames)>0:
            for channelName in simpleFrame.ChannelNames:
                simpleFrame.Channels.append(self.simpleChannels[channelName])
        return simpleFrame.Channels

    def _parseIFLR(self, lrSegList, fs):
        """
        Parse the IFLR, currently all EoD, FData and  unform are parsed, FDatas and unforms are part of LogicalFile
        object, but not EoD since it doesn't provide any value for upper layer application.

        :param lrSegList: The segments list for this logical record.

        :return: None

        """
        assert(len(lrSegList)>0)
        first = lrSegList[0]
        lrBytes = bytearray()
        for lrSeg in lrSegList:
            lrBytes.extend(lrSeg.readBody(fs))
        bStream = io.BytesIO(lrBytes)
        eof = endPos(bStream)
        for case in switch(first.lrType):
            if case(0):
                frameObjectName = reader.readOBNAME(bStream)
                simpleFrame = self.simpleFrames[frameObjectName]

                channelObjectList = self._getSimpleChannelsFromFrame(simpleFrame.ObName)

                if simpleFrame.Encrypted is not None and simpleFrame.Encrypted is True:
                    logger.error("Encrypted FData, not supported")

                fData = FrameData(reader.readUVARI(bStream))

                while bStream.tell() < eof:
                    for c in channelObjectList:
                        if c.NumOfValue>1:
                            slot = []
                            for i in range(c.NumOfValue):
                                slot.append(reader.readByRC(c.RepCode, bStream))
                            fData.slots.append(slot)
                        else:
                            slot = reader.readByRC(c.RepCode, bStream)
                            fData.slots.append(slot)

                if simpleFrame.ObName not in self.frameDataDict:
                    self.frameDataDict[simpleFrame.ObName] = []
                self.frameDataDict[simpleFrame.ObName].append(fData)
                break
            if case(1):
                dataDescRef = reader.readOBNAME(bStream)
                noformatEflr = list(filter((lambda eflr: type(eflr) is UdiEFLR), self.eflrList))
                noformatObject = None
                for eflr in noformatEflr:
                    for obj in eflr.objects: # type:Object
                        if obj.name == dataDescRef:
                            noformatObject = obj
                            break
                if noformatObject is None:
                    logger.error("Can't find noformat object")
                else:
                    data =  lrBytes[bStream.tell():]
                    unformIFLR = UnformattedDataLR(noformatObject, data)
                    self.noformList.append(unformIFLR)
                break
            if case(127):
                dataDescRef = reader.readOBNAME(bStream)
                # in some file, seems the data part of EoD IFLR is missing,
                # for example, BakerHughes/NO_6507_7-A-8/WL_RAW_NMR_MWD_1.DLIS
                if bStream.tell() == eof:
                    logger.warning("EoF without logical record type")
                    lr = EoD(dataDescRef, None)
                else:
                    lrType = reader.readUSHORT(bStream)
                    assert(bStream.tell() == eof)
                    lr = EoD(dataDescRef, lrType)
                break
            if case():
                lr = PrivateIFLR()
                break


    def _parseEFLR(self, lrSegList, fs):
        """
        Parse an EFLR and append to eflr list in this :class:`LogicalFile.LogicalFile`.

        :param lrSegList: A list of :class:`LogicalRecordSegment.LogicalRecordSegment` which compose a LogicalRecord.

        :return: None
        
        """
        assert(len(lrSegList)>0)
        first = lrSegList[0]
        lr = None

        # For encrypted and private EFLR, we will skip its body byt only includes
        # its encrypt packet which has prodCode and payload.
        if first.lrType >11 and first.encrypted:
            lr = PrivateEncryptedEFLR(first._encryptPkt)
            self.eflrList.append(lr)
            return
        if first.lrType<0:
            raise Exception("Unknow EFLR type")

        # Put bodies of all LogicalRecordSegments together, so can we can parse the Set.
        lrBytes = bytearray()
        for lrSeg in lrSegList:
            lrBytes.extend(lrSeg.readBody(fs))

        bStream = io.BytesIO(lrBytes)

        if first.lrType >11:
            lgSet = parseSet(bStream)
            lr = PrivateEFLR(lgSet, lgSet.objects)
            self.eflrList.append(lr)
            return

        eflrSet = parseSet(bStream)
        # TODO： Handle encrypted public EFLR, but we never see one so far.
        for case in switch(first.lrType):
            if case(PublicEFLRType.FHLR.value):
                lr = FhlrEFLR(eflrSet, list(map(lambda obj: FileHeader(obj), eflrSet.objects)))
                assert(len(lr.objects) == 1)
                break
            if case(PublicEFLRType.OLR.value):
                if eflrSet.type == 'ORIGIN':
                    lr = OlrEFLR(eflrSet, [Origin(obj) for obj in eflrSet.objects])
                elif eflrSet.type == 'WELL-REFERENCE-POINT':
                    lr = OlrEFLR(eflrSet, [WellReferencePoint(obj) for obj in eflrSet.objects])
                break
            if case(PublicEFLRType.AXIS.value):
                lr = AxisEFLR(eflrSet, [Axis(obj) for obj in eflrSet.objects])
                break
            if case(PublicEFLRType.CHANNL.value):
                channels = [Channel(obj) for obj in eflrSet.objects]
                lr = ChannelEFLR(eflrSet, channels)
                for c in channels:
                    self.simpleChannels[c.name] = \
                        SimpleChannel(c.name, c.getAttrValue(Channel.REPRESENTATION_CODE), c.getAttr(Channel.DIMENSION),
                                      c.getAttrValue(Channel.UNITS), _calculate_num_of_value(c.getAttr(Channel.DIMENSION)))

                break
            if case(PublicEFLRType.FRAME.value):
                if eflrSet.type == 'FRAME':
                    frames = [Frame(obj) for obj in eflrSet.objects]
                    lr = FrameEFLR(eflrSet, frames)
                    for f in frames:
                        if type(f.getAttrValue(Frame.CHANNELS)) is list:
                            self.simpleFrames[f.name] =\
                                SimpleFrame(f.name, f.getAttrValue(Frame.CHANNELS), [], f.getAttrValue(Frame.ENCRYPTED))
                        else:
                            self.simpleFrames[f.name] = \
                                SimpleFrame(f.name, [f.getAttrValue(Frame.CHANNELS)], [], f.getAttrValue(Frame.ENCRYPTED))
                elif lr.mySet.type == 'PATH':
                    lr = FrameEFLR(eflrSet, [Path(obj) for obj in eflrSet.objects])
                else:
                    logger.warn("Other frame set type:{}".format(lr.mySet))
                break
            if case(PublicEFLRType.STATIC.value):
                lr = StaticEFLR.getInstance(eflrSet)
                break
            if case(PublicEFLRType.SCRIPT.value):    # SCRIPT
                lr = ScriptEFLR(eflrSet, [Comment(obj) for obj in eflrSet.objects])
                break
            if case(PublicEFLRType.UPDATE.value): # UPDATE
                lr = UpdateEFLR(eflrSet, [Update(obj) for obj in eflrSet.objects])
                break
            if case(PublicEFLRType.UDI.value): #UDI
                lr = UdiEFLR(eflrSet, [NoFormat(obj) for obj in eflrSet.objects])
                break
            if case(PublicEFLRType.LNAME.value):

                lr = LongNameEFLR(eflrSet, [LongName(obj) for obj in eflrSet.objects])
                break
            if case(PublicEFLRType.SPEC.value):
                lr = SpecEFLR(eflrSet, [SpecObject(obj) for obj in eflrSet.objects])
                break
            if case(PublicEFLRType.DICT.value):
                lr = DictEFLR(eflrSet, eflrSet.objects)
                break
        self.eflrList.append(lr)


    @property
    def seqNum(self):
        """
        :return: The Sequence number of this logical file
        """
        # FHLR only has single object
        return self.eflrList[0].objects[0].getAttrValue(FileHeader.SEQUENCE_NUMBER)

    @property
    def id(self):
        """
        :return: ID of this logical file
        """
        return self.eflrList[0].objects[0].getAttrValue(FileHeader.ID)


def _calculate_num_of_value(dimensionAttr):
    """
    Based on dimension information, caculate how many size of the list when squeeze
     the high dimension value into single dimension array.
     
    :param dimensionAttr: The dimension attribute

    :return: An integer which specifies the size of one dimension arry

    """
    if dimensionAttr.count>1: # multi dimension channel
        from functools import reduce
        return reduce((lambda x, y: x*y), dimensionAttr.value)
    else:
        return dimensionAttr.value


def _check_lr_seg(tmpList):
    """
    Helper method to validate the LR Segment.

    :param tmpList: List of LRSegment

    :return: None. In case of error, assert will fail.

    """
    assert(len(tmpList)>0)
    assert(tmpList[0].hasPred is False)
    for i in range(len(tmpList)):
        if i == 0:
            assert(tmpList[i].hasPred is False)
        else:
            assert(tmpList[i].hasPred is True)
        assert(tmpList[i].encrypted == tmpList[0].encrypted)
        assert(tmpList[i].isEFLR == tmpList[0].isEFLR)
        assert(tmpList[i].hasTrailingLength == tmpList[0].hasTrailingLength)

