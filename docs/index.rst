``dlispy`` - a python parser for DLIS file
=====================================================================================================================

Introduction
----------------------------------
This project intends to create a parser for DLIS file which is defined in `RP66 Version 1 <http://w3.energistics.org/rp66/v1/Toc/main.html>`_

This parser can handle the both the visible envelope and logical format of RP66 version 1 which means as long as it is a DLIS file end up on a computer/server, this parser should be able to read and parse it. However, it is in a disk tape, this parser will Not be able to parse it.
Most of format defined in standard has been covered, for example

* Logical file and multiple logical files in a single DLIS file
* EFLR (both public EFLR and private EFLR) and IFLR (FData, EoF and NOFORM IFLR)
* Multiple dimension FData
* This parser has limited support for encrypted DLIS files. For example, it is only able to read Producer's Company Code from the Logical Record Segment. Also can't read the encrypted FData
* Currently this parser only support RP66 version 1, version 2 is out of scope since it is NOT actively used.
* So far, only reading of DLIS file is supported, writing or updating is not supported

Installation
---------------------------------------

1. Make sure you have python 3.5+ available and optionally you can create a virtualenv.
2. Install all dependencies

.. code-block:: bash

    $ pip install -r requirements.txt

3. Install this package. Go to parent folder of this repository, then install with

.. code-block:: bash

    $ pip install -m ./dlispy


4. Then, this parser can be used both as a lib or command line interface.
6. Command line interface. You can parse a DLIS/dlis file or a folder including DLIS files with following command

.. code-block:: bash

    $ python -m dlispy/core --input=<path to the dlis file or a folder including dlis files> --output=<output path> --eflronly=<if True only dump EFPRs, otherwise dump everything>


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   samples
   dlispy



Indices and tables
======================================================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
