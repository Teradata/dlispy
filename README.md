# Introduction
Parser for DLIS-files (Digital Log Interchange Standard), a binary format for Well Log Data, described by [RP66 Version 1](http://w3.energistics.org/rp66/v1/Toc/main.html)

# Scope
This parser can handle the both the visiable envolope and logical format of RP66 version 1 which means as long as it is a DLIS file end up on a computer/server, this parser should be able to read and parse it. However, it is in a disk tape, this parser will Not be able to parse it.
Most of format defined in standard has been coverred, for example
-   Logical file and multiple logical files in a single DLIS file
-   EFLR (both public EFLR and private EFLR) and IFLR (FData, EoF and NOFORM IFLR)
-   Multiple dimension FData
-   This parser has limited support for encrypted DLIS files. For example, it is only able to read Producer's Company Code from the Logical Record Segment. Also can't read the encrypted FData
-   Currently this parser only support RP66 version 1, version 2 is out of scope since it is NOT actively used.
-   So far, only reading of DLIS file is supported, writing or updating is not supported

# Installation
Right now we have not hosted this parser at https://pypi.org, but still you can install it as local package via `pip install`:
-   Make sure you have python 3.5+
-   (Optional) Create a virtualenv with python 3.5+
-   Go to parental folder of this repository, then install the package `pip install -e dlispy`
    
# How to use
Here is a code snippet demonstrating how to use its API:

## Use it as command line tool
After install it as package, you can transform single DLIS file or a folder which includes DLIS files with following command:
    `python -m dlispy.core --input=<path to single dlis file or a folder> --output=<output path> --eflronly=<if True only dump EFPRs, otherwise dump everything>`
    
### Output
When uses this parser to parse some dlis file and generate output, in the specified output directory, you can expect one folder for each logical file from original dlis file. In each logical file folder, following parts are included:
-   A directory named `UnformattedDataLogicalRecords` which includes all the Unformatted Data Logical Records. For each records, there are two part, the binary data file and a json file describes its `CONSUMER-NAME` and `DESCRIPTION`
-   A json file which represents all the EFLRs in the logical file
-   A set of CSV files, each represents all the FData for one frame. Note: the value for a channel could be a single integer, a list of integer of float, or a multiple dimension volume.
 The parse always squeeze the high dimension volumen to 1 dimension list, for example a channel value with dimension [320, 6] will be squeezed to a list with length 1920 (320x6). After get such list, you can look back the csv file to figure out the dimension and restore to its high dimension representation.

## How to parse a dlis file and iterate through logical records:
```python

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

```

## How to dump a dlis file to a readable format

In this sample code, you can see How to dump a dlis file to a read format including. Since each dlis file could include one or more logical files,
there is no dependency between logical record cross logical files, so it means treat each logical file seperately, thus we create
separate folder for each logical file in the given output path, we use `id` of the logical file as folder name. In each folder, there are following content:
- a json file which includes all EFLRs (public and private oens) in this logical file
- a set of csv files each represents one frame. The naming convension of the file is `<origin of ObjectName>_<copy of ObjectName>_<identifier of ObjectName>.csv`.
In the csv file, each column represents one channel and each row represents one FrameData. For high dimension channel, the value is squeezed into single
dimension array and user can use channel dimension attribute in the json file to convert it back.
- a folder named `UnformattedDataLogicalRecords`, all the `Unformatted Data LogicalRecords` are stored in this folder in binary format.

```python

from dlispy import dump
# you can also set eflrOnly as True to only dump the EFLRs as json file load EFLRs
dump('../data/206_05a-_3_DWL_DWL_WIRE_258276498.DLIS', output_path='output', eflr_only= False)

```

### Advance usage
In this sample code, you will see how to find information about specific object in specific type of EFLR.

```python

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

```

# Additional tips:
## Compability test for different Python versions:
 -  Install tool: `pip install tox pytest pyenv`
 -  Then make sure you have python 3.5, 3.6 install
 -  `tox`
## Generate coverage report:
`py.test --cov-report html --cov=dlis_parser  dlis_parser/tests/test_basic.py`
## Generate docs:
-   Install sphinx: `brew install sphinx-doc`
-   Delete old `.rst` files except `index.rst` in docs folder
-   Re-generate `.rst` file source code:
`cd docs;sphinx-apidoc -o .  ../dlis_parser ../dlis_parser/tests/*; cd ..`
-   Generate HTML docs: `cd docs;make clean html`
-   Then you can find documentation at `docs/_build/html` directory

# License
This project is licenced under [BSD-3-Clause](https://spdx.org/licenses/BSD-3-Clause.html)
