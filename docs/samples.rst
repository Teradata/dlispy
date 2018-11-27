Usage examples
====================================================

Basic parsing example
----------------------------------------------------
In this sample code, you can see

* How to parse a dlis file
* How to iterate through multiple logical files in one dlis file
* How to iterate through each EFLR in each logical file
* How to access Frames in each logical file.


.. code-block:: python

        from dlispy import LogicalFile, Object, Attribute, FrameData, PrivateEncryptedEFLR, parse
        # you can also set eflrOnly as True to only load EFLRs
        _, logical_file_list = parse('../data/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS', eflr_only= False)
        for lf  in logical_file_list: # type:LogicalFile
            print("LogicalFile with ID:{}, SequenceNumber:{}".format(lf.id, lf.seqNum))
            for eflr in lf.eflrList:
                if type(eflr) is PrivateEncryptedEFLR:              # PrivateEncryptedEFLR needs to handle separately.
                    continue
                print("     Set with Type:{}, Name:{}".format(eflr.setType, eflr.setName))
                for obj in eflr.objects: # type:Object
                    print("             Object with Name:{}".format(obj.name))
                    for attribute in obj.attributes:    #type:Attribute
                        print("                     Attribute with Label:{}, Value:{}, Count:{}, RepCode:{}, Units:{} ".
                              format(attribute.label, ' '.join(map(str, attribute.value))
                              if type(attribute.value) is list else attribute.value,
                              attribute.count, attribute.repCode, attribute.units))

            for frameName, fDataList in lf.frameDataDict.items():
                print("     Frame:{}".format(frameName))
                for fdata in fDataList: # type:FrameData
                    print("             FrameData with FrameNumber:{} and {} of slots".
                    format(fdata.frameNumber, len(fdata.slots)))




Basic dump example
----------------------------------------------------
In this sample code, you can see How to dump a dlis file to a read format including. Since each dlis file could include one or more logical files,
there is no dependency between logical record cross logical files, so it means treat each logical file seperately, thus we create
separate folder for each logical file in the given output path, we use `id` of the logical file as folder name. In each folder, there are following content:

* a json file which includes all EFLRs (public and private oens) in this logical file
* a set of csv files each represents one frame. The naming convension of the file is `<origin of ObjectName>_<copy of ObjectName>_<identifier of ObjectName>.csv`. In the csv file, each column represents one channel and each row represents one FrameData. For high dimension channel, the value is squeezed into single dimension array and user can use channel dimension attribute in the json file to convert it back.
* a folder named `UnformattedDataLogicalRecords`, all the `Unformatted Data LogicalRecords` are stored in this folder in binary format.


.. code-block:: python

        from dlisparser import dump
        # you can also set eflrOnly as True to only dump the EFLRs as json file load EFLRs
        dump('./data/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS', eflrOnly= False)


Advance samples
----------------------------------------------------
In this sample code, you can see
* How to access attribute and value for specific object in specific type of EFLR

.. code-block:: python

        from dlispy import LogicalFile, Object, Attribute, FrameData, PrivateEncryptedEFLR, parse
        from dlispy import OlrEFLR, FrameEFLR
        from dlispy import Frame, FrameData, Origin
        # you can also set eflrOnly as True to only load EFLRs
        _, logical_file_list = parse('../../data/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS')
        for lf  in logical_file_list: # type:LogicalFile
            for eflr in lf.eflrList:
                if type(eflr) is OlrEFLR:
                    for obj in eflr.objects: #type:Origin
                        print("File {} created by company {} at {}".format(
                            obj.getAttrValue(Origin.FILE_ID),obj.getAttrValue(Origin.COMPANY),obj.getAttrValue(Origin.CREATION_TIME)))

                if type(eflr) is FrameEFLR:
                    for obj in eflr.objects: #type:Frame
                        chanel_names = ', '.join(map(str, obj.getAttrValue(Frame.CHANNELS)))
                        print("Frame {} with channel list {}".format(obj.name, chanel_names))

Also you can use this parser to dump all files in a directory recursively:

.. code-block:: python

        from dlispy import dump_all
        from dlispy import OlrEFLR, FrameEFLR
        from dlispy import Frame, FrameData, Origin

        dlis_root_folder = './data/public_data/Well_logs_Volve'
        dump_all(dlis_root_folder, path.join('output', 'dump_all'))
