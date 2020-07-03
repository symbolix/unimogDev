#!/usr/bin/env python2.7
# ;-----------------------------------------------------------------------------------------------
# ; {UNIMOG} Integrated Pipeline Tools
# ;
# ; Name    : pathconfig.utilities
# ; Author  : Muhittin Bilginer
# ; Created : 15/06/2014
# ;
# ; Info    : Main functions and classes used by the unimogDev.py tool.
# ;
# ; This tool is part of Unimog.
# ;-----------------------------------------------------------------------------------------------


# Declare external imports
import sys
import os
import re
import time
import string
import logging
import pprint
from itertools import imap

# Define a version variable:
moduleName = __name__
moduleVersion = moduleName + " 0.0.1.[6]"

# Set a local empty logger to avoid the "No handlers could be found for logger FOO"
# message in case logging is not set up properly up the chain of the parent application.
logging.getLogger('unimog.unimogdev.utilities').addHandler(logging.NullHandler())

# Initialise YAML {{{
logger = logging.getLogger('unimog.unimogdev.utilities')
try:
    from yaml import load, dump
    try:
        from yaml import CLoader as Loader, CDumper as Dumper
        logger.debug("%s" % ("C module LibYAML is available."))
    except ImportError:
        try:
            from yaml import Loader, Dumper
        except:
            logger.warning("%s" % ("C module LibYAML is NOT available."))
except:
    logger.critical("YAML module is not available.")
    logger.critical("EXIT_CODE: 1")
    sys.exit(1)
# }}}

# Setup the Utility Functions {{{

# UTILITY: Define a sample function {{{
# ;---------------------------------------------------------------------------
# ; A test function
# ;---------------------------------------------------------------------------
def printMessage():
    logger = logging.getLogger('unimog.unimogdev.utilities')
    logger.debug("External module accessed.")

#}}}

# UTILITY: Define a KEY extractor function {{{
# ;---------------------------------------------------------------------------
# ; The "extractKey" Function:
# ;     This function should return a list of dictionary keys.
# ;---------------------------------------------------------------------------
def extractKeys(dictionary):
    keyList = []

    for key in dictionary:
        keyList.append(key)

    return keyList
#}}}

# Any additional function goes here.

#}}}

# Setup the YAML Functions {{{

# YAML: Define an "Importer" function {{{
# ;---------------------------------------------------------------------------
# ; Import Yaml Data:
# ;     Accepts the incoming YAML data through the stream object
# ;     passed in as a function argument.
# ;---------------------------------------------------------------------------
def importYamlData(fileName):
    # Link to logger
    logger = logging.getLogger('unimog.unimogdev.utilities')

    # Create the stream object
    try:
        inStream = open(fileName, 'r')
    except:
        logger.critical("%s: %s" % ("Unable to access the input file handler", fileName))
        logger.critical("EXIT_CODE: 2")
        sys.exit(2)

    # Perform the import process
    try:
        incomingData = load(inStream, Loader=Loader)
        logger.debug("%s" % ("Configuration successfully imported through the file handler."))
        inStream.close()
        return incomingData
    except:
        logger.critical("Failed to import the configuration through the file handler!")
        return {'error':'broken data handler'}
# }}}

# YAML: Define an "Exporter" function {{{
# ;---------------------------------------------------------------------------
# ; Export Yaml Data:
# ;     Dumps out an incoming dictionary using the stream object
# ;     passed in with the function arguments.
# ;---------------------------------------------------------------------------
def exportYamlData(sourceDictionary, fileName):
    # Link to logger
    logger = logging.getLogger('unimog.unimogdev.utilities')

    # Run a file check
    if not os.path.isfile(fileName):
        logger.critical("%s: %s" % ("Unable to access the output file handler", fileName))
        logger.critical("EXIT_CODE: 3")
        sys.exit(3)

    # Create the stream object
    outStream = open(fileName, 'w')

    # Perform the import process
    try:
        output = dump(sourceDictionary, outStream, Dumper=Dumper, default_flow_style=False)
        logger.debug("%s" % ("Configuration successfully exported to the file handler."))
    except:
        logger.critical("Failed to export the configuration to file handler!")
# }}}

# Any additional function goes here.

#}}}

# Setup Main Functions {{{
# ;---------------------------------------------------------------------------
# ; Setup the core functions
# ;---------------------------------------------------------------------------

# OPERATION: Define an "Get" function {{{
# ;---------------------------------------------------------------------------
# ; The "executeGet" Function:
# ;     This is one of the main operational functions. The role of this
# ;     function is to get the flags for the "targetObject".
# ;---------------------------------------------------------------------------
def executeGet(yamlObject, devVar):
    # Link to logger
    logger = logging.getLogger('unimog.unimogdev.utilities')
    logger.debug("%s: %s\n" % ("<get> call for", yamlObject))

    try:
        print ("1" if getattr(yamlObject, devVar[0]) else "0")
        logger.debug("\"%s\" %s" % (devVar[0], "is a valid dev variable."))
    except:
        logger.critical("\"%s\" %s" % (devVar[0], "is NOT a valid dev variable!"))

#}}}

# OPERATION: Define the "Set / Unset" function {{{
# ;---------------------------------------------------------------------------
# ; The "executeSet" Function:
# ;     This is one of the main operational functions. The role of this
# ;     function is to update the flags for the "targetObjects" to TRUE or FALSE.
# ;---------------------------------------------------------------------------
def executeSet(yamlObject, devVar, verbosityFlag, state):
    # This is a hybrid set / unset function, so handle the verbose string

    # Link to logger
    logger = logging.getLogger('unimog.unimogdev.utilities')

    stateSignature = "unset"
    if state: stateSignature = "set"

    # Link debugger
    logger.debug("<%s> %s: %s\n" % (stateSignature, "call for", yamlObject))
    logger = logging.getLogger('unimog.unimogdev.utilities')

    # Cycle over the provided variables

    # Create a counter
    index = 0

    # Start iterator
    for variable in devVar:
        # Debug information
        if verbosityFlag > 2: print "%s%s%s" % ("Variable Cycle [", index, "]")

        # Check if the provided value is a key in our YAML object
        # If it is, update the flag
        if variable in yamlObject.GetPublicDict():
            if verbosityFlag > 2: print "\t%s%s%s{%s}" % ("Current value for [", variable, "] ", getattr(yamlObject, variable))
            setattr(yamlObject, variable, state)
            if verbosityFlag > 2: print "\t%s%s%s{%s}" % ("New value for [", variable, "] ", getattr(yamlObject, variable))
        # If NOT, skip the process
        else:
            if verbosityFlag > 2: print "\t%s%s%s" % ("Variable [", variable, "] does NOT exist.")
            if verbosityFlag > 2: print "\t%s" % ("Nothing to process.")

        # Update the counter
        index = index + 1

    # Return the modified YAML object
    return yamlObject.GetPublicDict()

#}}}

# OPERATION: Define a "List" function {{{
# ;---------------------------------------------------------------------------
# ; The "executeList" Function:
# ;     This is one of the main operational functions. The role of this
# ;     function is to list the flags for the "targetObject(s)".
# ;---------------------------------------------------------------------------
def executeList(yamlObject, mode="default"):
    # Link debugger
    logger = logging.getLogger('unimog.unimogdev.utilities')
    logger.debug("%s: %s\n" % ("<list> call for", yamlObject))

    if mode == "default":
        # Print the results
        print ""
        yamlObject.listElements()
        print ""
    elif mode == "bash":
        pythonDict = yamlObject.GetPublicDict()
        bashString = ' '.join('{}={}'.format(key, int(val)) for key, val in pythonDict.items())
        print bashString

    elif mode == "python":
        pythonDict = yamlObject.GetPublicDict()
        print pythonDict
    else:
        pass

#}}}

# Any additional function goes here.

#}}}

# Setup the Core Functions {{{

# CORE: Define an "Empty Template" function {{{
# ;---------------------------------------------------------------------------
# ; Empty template:
# ;     Information goes here.
# ;---------------------------------------------------------------------------

# Any additional functions go here.

#}}}

# Setup Object Classes {{{

# Setup a template object {{{
# ;---------------------------------------------------------------------------
# ; Template Object
# ;---------------------------------------------------------------------------

class YamlObj:
    def __init__(self, **entries):
        self.__dict__.update(entries)
        self.public_names = entries.keys()

    def testMe(self):
        self.myVariable = 67

    def GetPublicDict(self):
        return {key:getattr(self, key) for key in self.public_names}

    def GetBashDict(self):
        return 0

    def listElements(self):
        #return str(self.GetPublicDict())
        self.maxKeyLength = max(imap(len, self.GetPublicDict()))
        for key, value in self.GetPublicDict().items():
            print "{0:{width}} : [{1:5}]".format(key, str(value), width=self.maxKeyLength)

#}}}

# Setup a custom StreamHandler object {{{
# ;---------------------------------------------------------------------------
# ; Conditional Handler Filter
# ;---------------------------------------------------------------------------

class CustomFilter(logging.Filter):

    def __init__(self, state):
        self.state = state

    def filter(self, record):
        if self.state == 1:
            return record.levelno in [logging.INFO, logging.ERROR,
                                      logging.CRITICAL]
        elif self.state == 2:
            return record.levelno in [logging.INFO, logging.DEBUG,
                                      logging.ERROR, logging.CRITICAL]
        elif self.state > 2:
            return record.levelno in [logging.INFO, logging.DEBUG,
                                      logging.ERROR, logging.CRITICAL,
                                      logging.WARNING]
        else:
            return False
#}}}

# Any additional class goes here.

#}}}

# vim: ts=4 ft=python nowrap fdm=marker
