import io
import os

import click
import time

from .StorageUnitLabel import StorageUnitLabel
from .VisibleRecord import VisibleRecord
from .LogicalFile import LogicalFile
from .common import myLogger, file_size

logger = myLogger('core')


def parse(path, eflr_only = False):
    """
    Parse a DLIS file which may include multiple Logical Files.
    :type path: str
    :param path: File path to the DLIS file

    :type eflr_only: bool
    :param eflr_only: If Truem, then only parse EFLR in each logical file.

    :return: a tuple, first element is instance of :class:`.StorageUnitLabel` and second element is a list of :class:`.LogicalFile`.

    """

    start = time.time()
    logger.info("Start parsing DLIS file %s", path)
    fs = None
    try:
        fs = open(path, 'rb')

        # record the total bytes
        fs.seek(0, io.SEEK_END)
        total_bytes = fs.tell()
        # move back to the beginning of the file
        fs.seek(0, io.SEEK_SET)
        # fs_seek_start(fs, 0)
        logger.debug("Start parsing Storage Unit Label")
        sul = StorageUnitLabel.parse(fs)
        logger.debug(sul)
        logger.debug("End parsing Storage Unit Label")
        vrList = []
        lrSegList = []
        while fs.tell() < total_bytes:
            vr = VisibleRecord.parse(fs)
            vrList.append(vr)
            #Lazy loading for IFLR: if lrSeg is part of EFLR, then its body is loaded,
            #  otherwise only the pos and length are recorded.
            lrSegList.extend(vr.lrSegList)
            logger.debug(vr)

        logger.debug("Start parsing %s LR Segments", len(lrSegList))
        lfList = _splitLogicalFiles(lrSegList, fs, eflr_only)
        logger.info("End parsing DLIS file, found %s LogicalFiles", len(lfList))

    except IOError as err:
        logger.error("Can't open DLIS file {}".format(path))
        fs.close()
        raise err
    finally:
        fs.close()
    end = time.time()
    logger.info("Took %s sec to parse %s file - %s", end-start, file_size(path), path)
    return sul, lfList


def dump(df_path, output_path, eflr_only  = False):
    """
    Dump a given DLIS file. In the "output_path", you will folder a few folder which for one logical file.
    :type df_path: str
    :param df_path: Path to the dlis file.

    :type output_path: str
    :param output_path: Where to dump this dlis file.

    :type eflr_only: bool
    :param eflr_only: True if only dump EFLRs, otherwise IFLR will also be dumped.

    :return: None
    """
    print(eflr_only)
    _, lf_list = parse(df_path, eflr_only)

    if not os.path.exists(output_path):
        os.makedirs(output_path)
    for lf in lf_list:
        id = lf.id.strip()
        lf_path = os.path.join(output_path, id)
        if not os.path.exists(lf_path):
            os.makedirs(lf_path)
        lf._dump(path=lf_path, eflrOnly = eflr_only)


def dump_all(df_folder_path, output_path, eflr_only = False):
    """
    Dump all the dlis files in the give folder recursively

    :type df_folder_path: str
    :param df_folder_path:

    :type output_path: str
    :param output_path:

    :type eflr_only: bool
    :param eflr_only:

    :return: None
    """

    if not os.path.exists(df_folder_path):
        raise Exception("df_folder_path \"{}\" does not exist")

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    from .common import _find_files
    from os.path import relpath
    all_df_files = _find_files(df_folder_path, ['*.DLIS', '*.dlis'])
    for file in all_df_files:
        relative_path = relpath(file, df_folder_path)[:-5]
        df_output_path = os.path.join(output_path, relative_path)
        if not os.path.exists(df_output_path):
            os.makedirs(df_output_path)
        try:
            dump(file, df_output_path, eflr_only)
        except Exception:
            logger.error("Fail to dump file \"{}\"".format(file))




def _splitLogicalFiles(lrSegList, fs, eflr_only = False):
    eflrSegList = []
    iflrSegList = []
    lf_list = []
    for lrSeg in lrSegList:
        if lrSeg.isEFLR:
            if lrSeg.lrType == 0: # FHLR, starts a new LogicalFile, note FHLR must be in a single Logical Record Segment.
                if len(eflrSegList) == 0:    # first one
                    eflrSegList.append(lrSeg)
                else:       # Start a new logical file
                    # checkLrSeg(eflrSegList)
                    lf_list.append(LogicalFile(eflrSegList, iflrSegList, fs, eflrOnly=eflr_only))
                    eflrSegList.clear()
                    iflrSegList.clear()
                    eflrSegList.append(lrSeg)
            else:
                eflrSegList.append(lrSeg)
        else:
            iflrSegList.append(lrSeg)
    lf_list.append(LogicalFile(eflrSegList, iflrSegList, fs, eflrOnly=eflr_only))

    return lf_list


@click.command()
@click.option('--input', help='The input DLIS(dlis) file or a folder includes DLIS files for parsing')
@click.option('--output', default='.', help='The output path')
@click.option('--eflronly', default=False, help='If only dump EFLRs', type=bool)
def cli(input, output, eflronly):
    print('hello world')
    if os.path.exists(input) and os.path.isdir(input):
        dump_all(input, output, eflr_only=eflronly)
    elif os.path.exists(input) and os.path.isfile(input):
        print(eflronly)
        dump(input, output, eflr_only=eflronly)
    else:
        print('Input dlis file or dir [{}] does not exist'.format(input))

if __name__ == '__main__':
    cli()




