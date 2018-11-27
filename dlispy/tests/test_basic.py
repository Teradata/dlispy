import os
import sys
import unittest
from io import BytesIO
from logging.config import fileConfig
from os import path


log_conf = path.join(path.dirname(path.dirname(path.realpath(__file__))), 'logging.ini')
if os.path.exists(log_conf):
    print(log_conf)
    print('Load logging configuration file at {}'.format(log_conf))
    fileConfig(log_conf)


from ..common import _find_files
from ..core import dump_all


from ..LogicalFile import LogicalFile
from ..LogicalRecord import _getClassName
from ..__init__ import parse, dump
sys.path.insert(0, path.abspath(path.join(path.dirname(__file__), '.')))
from ..StorageUnitLabel import StorageUnitLabel
parent_path = path.dirname(path.dirname(path.dirname(path.realpath(__file__))))
from ..LogicalRecord import *



unsupported_filenames = ['WL_RAW_CAL-DEN-ELEM-GR-NEU-REMP_MWD_1.DLIS', 'WLC_COMPUTED_CAL-DEN-ELEM-GR-NEU-REMP_MWD_1.DLIS']


def _bitstr_to_bytes(s):
    return int(s, 2).to_bytes(len(s) // 8, byteorder='big')

class DlisFileTest(unittest.TestCase):


    @unittest.skip("wrong in standard: http://w3.energistics.org/rp66/v1/rp66v1_appb.html#B_7")
    def testReadFDOUBL(self):
        stream = BytesIO(_bitstr_to_bytes('01000000011000110010000000000000'))
        result = readFDOUBL(stream)
        assert(result == 153)

        stream = BytesIO(_bitstr_to_bytes('11000000011000110010000000000000'))
        result = readFDOUBL(stream)
        assert(result == -153)

    def testReadFSINGL(self):
        stream = BytesIO(_bitstr_to_bytes('01000011000110010000000000000000 '))
        result = readFSINGL(stream)
        assert(result == 153)

        stream = BytesIO(_bitstr_to_bytes('11000011000110010000000000000000'))
        result = readFSINGL(stream)
        assert(result == -153)



    def testReadSLONG(self):
        stream = BytesIO(_bitstr_to_bytes('00000000000000000000000010011001'))
        result = readSLONG(stream)
        assert(result == 153)

        stream = BytesIO(_bitstr_to_bytes('11111111111111111111111101100111'))
        result = readSLONG(stream)
        assert(result == -153)

    def testReadUSHORT(self):
        stream = BytesIO(_bitstr_to_bytes('10100111'))
        result = readUSHORT(stream)
        # this test case is from standard, but seems wrong: http://w3.energistics.org/rp66/v1/rp66v1_appb.html#B_15
        assert(result == 167)


    def testReadUNORM(self):
        stream = BytesIO(_bitstr_to_bytes('1000000010011001'))
        result = readUNORM(stream)
        assert(result == 32921)


    def testReadULONG(self):
        stream = BytesIO(_bitstr_to_bytes('00000000000000000000000010011001'))
        result = readULONG(stream)
        assert(result == 153)


    def testReadIDENT(self):
        stream = BytesIO(_bitstr_to_bytes('00000011010000010100001001000011'))
        result = readIDENT(stream)
        assert(result == 'ABC')


    def testReadASCII(self):
        stream = BytesIO(_bitstr_to_bytes('00000011010000010000101001100010'))
        result = readASCII(stream)
        assert(result == 'A\nb')


    def testReadDTIME(self):
        stream = BytesIO(_bitstr_to_bytes('0101011100010100000100110001010100010100000011110000001001101100'))
        result = readDTIME(stream)
        t = result.time
        assert(t.year == 1987 and t.month == 4 and t.day == 19 and
               t.hour == 21 and t.minute == 20 and t.second == 15 and t.microsecond == 620000)
        assert(result.tzone.name == 'LocalDaylightSavings')


    def testReadSSHORT(self):
        stream = BytesIO(_bitstr_to_bytes('01011001'))
        result = readSSHORT(stream)
        assert(result == 89)

        stream = BytesIO(_bitstr_to_bytes('10100111'))
        result = readSSHORT(stream)
        assert(result == -89)


    def testReadSNORM(self):
        stream = BytesIO(_bitstr_to_bytes('1111111101100111'))
        result = readSNORM(stream)
        assert(result == -153)

        stream = BytesIO(_bitstr_to_bytes('0000000010011001'))
        result = readSNORM(stream)
        assert(result == 153)


    def testGetClassName(self):
        """
        Test retrieve classname
        :return:
        """
        set_type = 'WELL-REFERENCE'
        assert(_getClassName(set_type) == 'WellReference')
        set_type = 'ORIGIN'
        assert(_getClassName(set_type) == 'Origin')


    def testLazyLoadIRLR(self):
        """
        This test code verified the lazy loading of IFRL, initially, eflr_only is set to true, so no IFLR will be loaded,
        then loadIFLR with a filestream.
        :return:
        """
        test_file = path.join(parent_path,'data','206_05a-_3_DWL_DWL_WIRE_258276498.DLIS')

        df_name_without_ext = os.path.basename(test_file)[:-5]
        complete_output_path = os.path.join('./output', df_name_without_ext)

        _, lf_list = parse(test_file, eflr_only=True)

        for lf in lf_list:  # type:LogicalFile
            dict = lf.frameDataDict #type:dict
            assert(len(dict.items()) == 0)
            try:
                fs = open(test_file, 'rb')
                lf.loadIFLR(fs)
                assert(len(lf.frameDataDict.items())>0)
            finally:
                fs.close()


    def testDump(self):
        """
        Test dump file.
        :return:
        """
        test_file = path.join(parent_path,'data','206_05a-_3_DWL_DWL_WIRE_258276498.DLIS')

        df_name_without_ext = os.path.basename(test_file)[:-5]
        complete_output_path = os.path.join('./output', df_name_without_ext)

        dump(test_file, complete_output_path)
        expected_files = ['2_0_2000T.csv','2_0_800T.csv', 'MSCT_197LTP.json']
        num_of_files = 0
        for r, d, f in os.walk(complete_output_path):
            for file in f:
                num_of_files+=1
                assert(file in expected_files)

        assert(num_of_files == len(expected_files))
        


    def testReadTime(self):
        """
        A test case to verify that one channel in a frame including multiple value, like a vector.
        :return:
        """
        test_file = path.join(parent_path,'data','206_05a-_3_DWL_DWL_WIRE_258276501.DLIS')
        _, lf_list = parse(test_file)
        assert(len(lf_list) == 1)
        lf = lf_list[0]
        assert(lf.id.strip() == 'MSCT_200LTP')
        assert(lf.seqNum.strip() == '200')

        originEflr = lf.eflrList[1] #type:OlrEFLR

        creationTime = originEflr.objects[0].getAttrValue(Origin.CREATION_TIME)

        assert(str(creationTime.time) == '2011-08-20 23:25:07')
        assert(creationTime.tzone == TZ.LocalDaylightSavings)



    def testReadObjRef(self):
        test_file = path.join(parent_path,'data','206_05a-_3_DWL_DWL_WIRE_258276498.DLIS')
        sul, lf_list = parse(test_file)

        lf = lf_list[0] # type: LogicalFile

        found = False
        for eflr in lf.eflrList:
            if type(eflr) is ChannelEFLR:
                for obj in eflr.objects:
                    if obj.name == ObName.instance(2, 0, 'LMVL_DL'):
                        found = True
                        sourceValue = obj.getAttrValue(Channel.SOURCE) #type:ObjRef
                        assert(type(sourceValue) is ObjRef)
                        assert(sourceValue.type == 'TOOL' and sourceValue.identifier == 'MSCT'
                               and sourceValue.copy == 0 and sourceValue.origin == 2)

        assert(found == True)


    def testParseEFLRandIFLR(self):
        test_file = path.join(parent_path,'data','206_05a-_3_DWL_DWL_WIRE_258276498.DLIS')
        sul, lf_list = parse(test_file)
        assert(sul._susn ==  1)
        assert(sul._version == 1)
        assert(sul._sus == StorageUnitLabel.SU_STRUCTURE_RECORD)
        assert(sul._maxRecordLen == 8192)
        assert(sul._ssi == "Default Storage Set                                         ")
        assert(len(lf_list) == 1)
        lf = lf_list[0] # type: LogicalFile


        assert(type(lf.eflrList[0]) is FhlrEFLR)
        assert(type(lf.eflrList[1]) is OlrEFLR)
        assert(type(lf.eflrList[2]) is StaticEFLR)
        lr = lf.eflrList[2] # type: StaticEFLR
        assert(lr.setName == '51')
        assert(lr.setType == 'EQUIPMENT')
        
        assert(type(lf.eflrList[3]) is PrivateEncryptedEFLR)
        assert(type(lf.eflrList[4]) is PrivateEncryptedEFLR)
        assert(type(lf.eflrList[5]) is StaticEFLR)
        lr = lf.eflrList[5]             #type: StaticEFLR
        assert(lr.setName == '54')
        assert(lr.setType == 'TOOL')

        assert(type(lf.eflrList[6]) is PrivateEncryptedEFLR)
        assert(type(lf.eflrList[7]) is PrivateEncryptedEFLR)
        assert(type(lf.eflrList[8]) is PrivateEFLR)

        assert(lf.eflrList[8].setName == '57')
        assert(lf.eflrList[8].setType == '440-CHANNEL')


        assert(type(lf.eflrList[9]) is StaticEFLR)
        lr = lf.eflrList[9]
        assert(lr.setName == '58')
        assert(lr.setType == 'PARAMETER')

        assert(type(lf.eflrList[10]) is PrivateEncryptedEFLR)

        assert(type(lf.eflrList[11]) is StaticEFLR)
        lr = lf.eflrList[11]
        assert(lr.setName == '60')
        assert(lr.setType == 'PARAMETER')

        assert(type(lf.eflrList[12]) is PrivateEncryptedEFLR)

        assert(type(lf.eflrList[13]) is StaticEFLR)
        lr = lf.eflrList[13]
        assert(lr.setName == '62')
        assert(lr.setType == 'PARAMETER')

        assert(type(lf.eflrList[14]) is PrivateEncryptedEFLR)

        assert(type(lf.eflrList[15]) is StaticEFLR)
        lr = lf.eflrList[15]
        assert(lr.setName == '64')
        assert(lr.setType == 'CALIBRATION-MEASUREMENT')

        assert(type(lf.eflrList[16]) is PrivateEncryptedEFLR)

        assert(type(lf.eflrList[17]) is StaticEFLR)
        lr = lf.eflrList[17]
        assert(lr.setName == '72')
        assert(lr.setType == 'CALIBRATION-COEFFICIENT')


        assert(type(lf.eflrList[18]) is StaticEFLR)
        lr = lf.eflrList[18]
        assert(lr.setName == '73')
        assert(lr.setType == 'CALIBRATION-COEFFICIENT')

        assert(type(lf.eflrList[19]) is StaticEFLR)
        lr = lf.eflrList[19]
        assert(lr.setName == '74')
        assert(lr.setType == 'CALIBRATION')

        assert(type(lf.eflrList[20]) is PrivateEncryptedEFLR)
        assert(type(lf.eflrList[21]) is PrivateEncryptedEFLR)
        assert(type(lf.eflrList[22]) is PrivateEncryptedEFLR)

        assert(type(lf.eflrList[23]) is StaticEFLR)
        lr = lf.eflrList[23]
        assert(lr.setName == '78')
        assert(lr.setType == 'PROCESS')

        assert(type(lf.eflrList[24]) is PrivateEFLR)
        assert(lf.eflrList[24].setName == '79')
        assert(lf.eflrList[24].setType == '440-OP-CORE_TABLES')


        assert(type(lf.eflrList[25]) is PrivateEFLR)
        assert(lf.eflrList[25].setName == '330')
        assert(lf.eflrList[25].setType == '440-OP-CORE_REPORT_FORMAT')


        assert(type(lf.eflrList[26]) is ChannelEFLR)
        lr = lf.eflrList[26]
        assert(len(lr.objects) >40)



        assert(type(lf.eflrList[27]) is PrivateEFLR)
        assert(lf.eflrList[27].setName == '375')
        assert(lf.eflrList[27].setType == '440-PRESENTATION-DESCRIPTION')

        assert(type(lf.eflrList[28]) is PrivateEFLR)
        assert(lf.eflrList[28].setName == '377')
        assert(lf.eflrList[28].setType == '440-OP-CHANNEL')


        assert(type(lf.eflrList[29]) is FrameEFLR)

        assert(len(lf.eflrList[29].objects) == 2)
        objs = lf.eflrList[29].objects
        assert(objs[0].name == ObName.instance(2, 0, '2000T'))
        assert(objs[1].name == ObName.instance(2, 0, '800T'))



        frame2000T = lf.frameDataDict[ObName.instance(2, 0, '2000T')]
        assert(len(frame2000T) == 921)
        lastFData = frame2000T[-1]
        assert(lastFData.frameNumber == 921)
        assert(lastFData.slots == [17597260.0, 891961.0, 2363.0, 891961.0])
        firstFdata = frame2000T[0]
        assert(firstFdata.frameNumber == 1)
        assert(firstFdata.slots == [16677259.0, 852606.0, 2233.0, 852606.0])
        frame800T = lf.frameDataDict[ObName.instance(2, 0, '800T')]
        assert(len(frame800T) == 2301)

    def testMultiLogicalFile(self):
        """
        A test case to verify that one physical .DLIS file including multiple logical files.
        :return:
        """
        test_file = path.join(parent_path,'data','volve_data','WLC_PETROPHYSICAL_COMPOSITE_1.DLIS')
        _, lf_list = parse(test_file)
        assert(len(lf_list) == 2)
        assert(lf_list[0].id.strip() == 'Fil#1_alle_MWD.logdata')
        assert(lf_list[0].seqNum.strip() == '1')


    def testOneDimensionChannel(self):
        """
        A frame including a channel has value as a list.
        :return:
        """
        test_file = path.join(parent_path,'data','volve_data', 'WL_RAW_PROD_AAC-AIMG-CCL-GR_2016-08-18_2.DLIS')
        _, lf_list = parse(test_file)
        assert(len(lf_list) == 1)
        lf1 = lf_list[0]

        frame = lf1.simpleFrames[ObName.instance(13,0, '30B')]
        assert(len(frame.Channels) == 13)
        channel =frame.Channels[1]
        dimensionAttr= channel.Dimension
        assert(dimensionAttr.value == 6 and dimensionAttr.count == 1)
        firstFData = lf1.frameDataDict[ObName.instance(13,0, '30B')][0]
        assert(firstFData.frameNumber == 1 and len(firstFData.slots[1]) == 6)
        assert(firstFData.slots[1][0] == 37.0 and firstFData.slots[1][-1] == 3237.0)

        lastFData = lf1.frameDataDict[ObName.instance(13,0, '30B')][-1]
        assert(lastFData.frameNumber == 1388 and len(lastFData.slots[1]) == 6)
        assert(lastFData.slots[1][0] == 312.0 and lastFData.slots[1][-1] == 3818.0 and lastFData.slots[1][-2] == 685.0)


    def testTwoDimensionChannel(self):
        """
        A frame including a channel has two dimension
        :return:
        """
        test_file = path.join(parent_path,'data','volve_data','Well_logs','11.INTEGRITY LOGS','15_9-F-12', 'RAW', 'WL_RAW_PROD_AAC-AIMG-CCL-GR_2016-08-18_2.DLIS')
        _, lf_list = parse(test_file)
        assert(len(lf_list) == 1)
        lf1 = lf_list[0]

        frame = lf1.simpleFrames[ObName.instance(13,0, '30B')]
        assert(len(frame.Channels) == 13)
        channel =frame.Channels[5]
        dimensionAttr= channel.Dimension
        assert(dimensionAttr.value == [256, 6] and dimensionAttr.count == 2)
        firstFData = lf1.frameDataDict[ObName.instance(13,0, '30B')][0]
        assert(firstFData.frameNumber == 1 and len(firstFData.slots[5]) == 1536)
        assert(firstFData.slots[5][0] == 173 and firstFData.slots[5][-1] == 1355)

        lastFData = lf1.frameDataDict[ObName.instance(13,0, '30B')][-1]
        assert(lastFData.frameNumber == 1388 and len(lastFData.slots[5]) == 1536)
        assert(lastFData.slots[5][0] == 143 and lastFData.slots[5][-1] == 145 and lastFData.slots[5][-2] == 313)



    def testFDOUBLInDlis(self):
        """
        A frame including a channel has two dimension
        :return:
        """
        test_file = path.join(parent_path,'data','volve_data','Well_logs','11.INTEGRITY LOGS','15_9-F-12', 'RAW', 'WL_RAW_PROD_AAC-AIMG-CCL-GR_2016-08-18_2.DLIS')
        _, lf_list = parse(test_file, eflr_only=True)
        assert(len(lf_list) == 1)
        lf0 = lf_list[0]   # type:LogicalFile

        for eflr in lf0.eflrList:
            if type(eflr) is StaticEFLR and eflr.setName == 'HzParameter':
                target =  next(obj for obj in eflr.objects if obj.name == ObName.instance(13, 0, "EAE")) #type:Parameter
                assert(target is not None and target.getAttrValue(Parameter.VALUES) == -999.25)


    def testSetWitoutObject(self):
        """
        In following file, there is a set with template but without any objects, this test case is to verify parser can handle it.
        :return:
        """
        test_file = path.join(parent_path,'data','volve_data','Well_logs','04.COMPOSITE','15_9-F-11 B', 'WLC_PETROPHYSICAL_COMPOSITE_1.DLIS')
        parse(test_file)


    @unittest.skip("long running test")
    def testPublicDataEFLROnly(self):
        """
        Test Equnior volve open data set, pls run ./download_public_data.sh first to download all public data,
        it may take a while as it is about 15GB data. The whole test will take about 3 hours, please be patient.
        Note: Two files will fail as they are wrongly formatted.
        :return:
        """
        test_folder = path.join(parent_path,'data','public_data')

        failed_files = 0
        success_files =0
        for filename in _find_files(test_folder, ['*.DLIS', '*.dlis']):
            logger.info('Parsing :{}'.format(filename))
            try:
                _, lf_list = parse(filename)
                success_files+=1
            except Exception:
                assert(os.path.basename(filename) in unsupported_filenames)
                failed_files +=1
                logger.error("fail to parse {}".format(filename))
                continue
        assert(success_files == 1212)
        assert(failed_files == len(unsupported_filenames))


    @unittest.skip("long running test")
    def testPublicData(self):
        """
        Test Equnior volve open data set, pls run ./download_public_data.sh first to download all public data,
        it may take a while as it is about 15GB data. The whole test will take about 3 hours, please be patient.
        Note: Two files will fail as they are wrongly formatted.
        :return:
        """
        test_folder = path.join(parent_path,'data','public_data')
        failed_files = 0
        success_files =0
        for filename in _find_files(test_folder, ['*.DLIS', '*.dlis']):
            logger.info('Parsing :{}'.format(filename))
            try:
                _, lf_list = parse(filename)
                df_path = os.path.join('public_data', os.path.basename(filename).split('.')[0])
                if not os.path.exists(df_path):
                    os.makedirs(df_path)
                for lf in lf_list:
                    id = lf.id.strip()
                    lf_path = os.path.join(df_path, id)
                    if not os.path.exists(lf_path):
                        os.makedirs(lf_path)
                    lf._dump(lf_path)
                success_files+=1

            except Exception:
                assert(os.path.basename(filename) in unsupported_filenames)
                failed_files +=1
                logger.error("fail to parse {}".format(filename))
                continue
        assert(success_files == 1212)
        assert(failed_files == len(unsupported_filenames))


    @unittest.skip('long running test')
    def testDumpAll(self):
        """
        Test the functionality to dump all dlis files in a folder recursively.
        :return: None
        """
        test_folder = path.join(parent_path,'data','public_data', 'Well_logs_Volve', 'Well_logs', '03.PRESSURE')
        dump_all(test_folder, path.join(parent_path, 'output', 'dump_all'))

    @unittest.skip('under test')
    def testSULFile(self):
        test_file = path.join(parent_path, 'WL_PROD_2001-03-18.DLIS')
        sul, lf_list = parse(test_file)
        print(sul)

    def testFix(self):
        test_file = path.join(parent_path,'encoding_pb', 'WL_RAW_PROD_CCL-CEM-GR_2007-04-09_1.DLIS')
        _, _ = parse(test_file)
        # print(sul)

    @unittest.skip('under test')
    def testEncodingPb(self):
        wrong_file = ['WL_RAW_PROD_AC-AIMG-CCL-GR_2016-07-08_1.DLIS','WL_RAW_PROD_AIMG-AC-CCL-GEOM-GR_2008-10-19_4.DLIS']
        to_be_fix = [
            'WL_RAW_PROD_2001-03-04_1.DLIS',
            'WL_RAW_PROD_CCL-CEM-GR_2007-04-09_1.DLIS'
        ]

        for f in os.listdir(path.join(parent_path,'encoding_pb')):
            if f not in wrong_file and f not in to_be_fix:
                print("start to parse {}".format(path.join(parent_path,'encoding_pb', f)))
                try:
                    parse(path.join(parent_path,'encoding_pb', f))
                except Exception:
                    print("fail to parse {}".format(f))


if __name__ == '__main__':
    unittest.main()

