#!/usr/bin/env python2.7
# ;----------------------------------------------------------------------------------------
# ; {UNIMOG} Integrated Pipeline Tools
# ;
# ; Name    :   unimogDev.py
# ; Version :   0.0.1.[5]
# ; Author  :   Muhittin Bilginer
# ; Created :   07/09/2014
# ; Edited  :   08/10/2014
# ;
# ; Info    :   A pipeline tool responsible for managing the dev flags.
# ;
# ; This tool is part of Unimog.
# ;----------------------------------------------------------------------------------------

# Implementation outline:
#
# {Functions / Sub-programs}
#   Get     (get)   : Gets a flag status (single)
#   List    (list)  : Lists all of the current flags. (multiple)
#   Set     (set)   : Set the flag for a specific item (multiple).
#   Unset   (unset) : Unset the flag for a specific item. (multiple)
#
# {Options}
#   Verbosity   (-v, --verbosity)   : Verbosity scale from 0 (silent) to 3 (a detailed message).
#   Help        (-h)                : Displays a help message, possible to use just after the function flag.
#   Version     (--version)         : Display the version of the utility.
#
# {Special Options}
#   Mode    (--mode="modifier")     : Will run a special mode for the parrent function.
#                                     Current modes are:
#
#                                     --mode=all                : For the "Set" and "Unset" functions.
#                                     --mode=bash, --mode=python: For the "List" function.
# Examples:
#
#   unimogDev.py get UNIMOG_NUKE_DEV
#   unimogDev.py set UNIMOG_HOUDINI_DEV UNIMOG_MAYA_DEV UNIMOG_NUKE_DEV
#   unimogDev.py set --mode=all
#   unimogDev.py unset UNIMOG_HOUDINI_DEV
#   unimogDev.py list
#   unimogDev.py list --mode=bash
#
# Updates:
#   v0.0.1.[3]:
#       With this version, we have introduced a bash front-end script "unimogDev.sh".
#       This bash script should glue the python side of this tool with the actual environment
#       modifier "unimogDev.env"
#   v0.0.1.[4]:
#       No change, just a sync with the other components
#   v0.0.1.[5]:
#       Code restructured so that all of the functions are in the module
#
# TODO:
#   Nothing to implement.
# ;----------------------------------------------------------------------------------------

# Declare external imports
import sys, os, re, time, string
import argparse
import logging
from argparse import RawTextHelpFormatter
from datetime import datetime

# Declare internal imports
import modules.utilities as utils

# Setup prog related variables
program = {'name' : 'unimogDev.py', 'majorVersion' : '0', 'minorVersion' : '0', 'buildVersion' : '1', 'devCounter' : '5'}

# Argument Parser Setup {{{
# ;---------------------------------------------------------------------------
# ; Setup the argparser
# ;---------------------------------------------------------------------------

# Define the main parser. {{{
mainProgram = argparse.ArgumentParser(
    prog=program['name'],
    description='Operates on flags provided by a YAML structure.',
    usage='''
    \t%(prog)s <main options: -v=0 (1,2,3), --version, -h> <functions: get set unset list> [DEV_VARIABLE(s)] \n\t("set" and "unset" supports multiple items, "get" operates on a single item, "list" maybe used with no item)
    ''',
    # Provide an example text
    epilog='''
    EXAMPLES
        Activate dev mode for Maya and Houdini:
        unimogDev --verbosity=2 set MAYA_DEV HOUDINI_DEV

        De-activate dev mode for Houdini and Nuke:
        unimogDev --verbosity=3 unset HOUDINI_DEV NUKE_DEV

        List all dev flags:
        unimogDev list
    ''',
    formatter_class=RawTextHelpFormatter
)
#}}}

# Add a global verbosity argument to the main parser. {{{
mainProgram.add_argument('-v', '--verbosity', nargs=1, type=int, default=0, help='The verbosity level required for the debug functions', metavar="0, 1, 2")
mainProgram.add_argument('--version', action='version', version=' \n' + '%(prog)s' + ' v' + program['majorVersion'] + '.' + program['minorVersion'] + '.' + program['buildVersion'] + '.[' + program['devCounter'] + ']' + ' (BETA) (Darwin64) | Environment Dev Flags Manager | {UNIMOG} Integrated Pipeline Tools\n ', help="Show program's version number and exit")
# }}}

# Define the parser for the sub functions. {{{
# Needs an extra line for the folding.
subProgram = mainProgram.add_subparsers(help='Please choose one of the main functions:')
#}}}

# Create the parser for the "get" sub-command {{{
get = subProgram.add_parser('get', help='Get the dev flag for a single item.')
get.add_argument('targetObject', nargs=1, type=str, metavar='VARIABLE, a target dev environment variable to work on.')
get.set_defaults(func='get')
# }}}

# Create the parser for the "set" sub-command {{{
set = subProgram.add_parser('set', help='Set the dev flag to TRUE for a single or multiple items. (use "--mode=all" for all items)')
set.add_argument('targetObject', nargs='*', type=str, metavar='VARIABLE, a target dev environment variable to work on.')
set.add_argument('--mode', nargs='?')
set.set_defaults(func='set', mode='default')
# }}}

# Create the parser for the "unset" command {{{
unset = subProgram.add_parser('unset', help='Unset the dev flag for a single or multiple items, the resulting state is FALSE. (use "--mode=all" for all items)')
unset.add_argument('targetObject', nargs='*', type=str, metavar='variable, a target dev environment variable to work on.')
unset.add_argument('--mode', nargs='?')
unset.set_defaults(func='unset', mode='default')
# }}}

# Create the parser for the "list" command {{{
list = subProgram.add_parser('list', help='Lists the status of all flags. (use "--mode=bash" for bash style list)')
list.add_argument('--mode', nargs='?')
list.set_defaults(func='list', mode='default')
# }}}

# Any additional function goes here.

# }}}

args = mainProgram.parse_args()

# Debug Logger Setup {{{
# ;---------------------------------------------------------------------------
# ; Setup the logger
# ;---------------------------------------------------------------------------

# Get the verbosity flag
try:
    verbosityFlag = args.verbosity[0]
except:
    # Verbose INFO, ERROR, CRITICAL by default
    verbosityFlag = 1

# Process the verbosityFlag to assign a verbosityState
verbosityState = max(min(verbosityFlag, 3), 0)

# Initiate the logger.
logger = logging.getLogger('unimog')

# Create a console handler.
console = logging.StreamHandler()

# Set the default level to INFO

# Put the logger into DEBUG mode
logger.setLevel(logging.DEBUG)

# Put the handler into DEBUG mode
console.setLevel(logging.DEBUG)

# Define a default CustomFilter
consoleFilter = utils.CustomFilter(0)

# Create the conditional filters
consoleFilter = utils.CustomFilter(verbosityState)

# Attach the filters
console.addFilter(consoleFilter)

# Create a formatter dictionary.
consoleFormatter = logging.Formatter('[%(asctime)s] {%(funcName)s, %(name)s} {%(filename)s, line: %(lineno)d} | (%(levelname)s) %(message)s')

# Set the formatter of the console logger
console.setFormatter(consoleFormatter)

# Link the console handler to the logger.
logger.addHandler(console)

# }}}

# ;---------------------------------------------------------------------------
# ; Main Execution Block
# ;---------------------------------------------------------------------------

# <START>

# Check the internal module
utils.printMessage()
logger.debug("%s: %s\n" % ("Utility module version", utils.moduleVersion))

# Initial debugging information
logger.debug("%s:\n%s\n" % ("Incoming arguments", sys.argv))
logger.debug("%s:\n%s\n" % ("Argparse results", args))

# Build YAML data dictionary
try:
    unimogLocalSiteConfig = os.environ['UNIMOG_LOCAL_SITE_CONFIG']
except:
    logger.critical("Unable to get the \"$UNIMOG_LOCAL_SITE_CONFIG\" environment variable!")
    logger.critical("EXIT_CODE: 6")
    sys.exit(6)

fileString = unimogLocalSiteConfig + '/unimogDev.yaml'
inData = utils.importYamlData(fileString)

# Debug
logger.debug("%s \n%s\n" % ("Incoming YAML dictionary is:", inData))

# Create a YAML class object using the incoming dictionary
s = utils.YamlObj(**inData)

# Function Block {{{
# ;---------------------------------------------------------------------------
# ; The actual function distribution block
# ;---------------------------------------------------------------------------

# MAIN: This is the GET block {{{
if args.func=="get":
    logger.debug("Mode: <get>")
    utils.executeGet(s, args.targetObject)
#}}}

# MAIN: This is the SET block {{{

elif args.func=="set":
    logger.debug("Mode: <set>")

    # A secondary check for the "ALL" sub mode.
    # In case the "ALL" sub mode is active, we need to gather all the keys
    # from the YAML object and build our own targetObject.

    # --all was used
    if args.mode == "all":
        # --all was used but and additional arguments were provided
        if len(args.targetObject) != 0:
            logger.error("No arguments allowed after --all.")

            # Exit
            logger.critical("EXIT_CODE: 4")
            sys.exit(4)

        # Throw a debug warning about the "--all" mode being active
        logger.warning("%s" % ("Sub-mode: <all> is active, any operation will affect all target objects."))

        # Extract the keys of the YAML object
        keyList = utils.extractKeys(s.GetPublicDict())

        # Override the argument list
        args.targetObject = keyList

    # --all was not used
    else:
        pass

    # Run the function
    newData = utils.executeSet(s, args.targetObject, verbosityFlag, True)

    # Attempt to write the YAML object back to the file
    utils.exportYamlData(newData, fileString)
#}}}

# MAIN: This is the UNSET block {{{
elif args.func=="unset":
    logger.debug("Mode: <unset>")

    # A secondary check for the "ALL" sub mode.
    # In case the "ALL" sub mode is active, we need to gather all the keys
    # from the YAML object and build our own targetObject.

    # --all was used
    if args.mode == "all":
        # --all was used but and additional arguments were provided
        if len(args.targetObject) != 0:
            logger.error("No arguments allowed after --all.")

            # Exit
            logger.critical("EXIT_CODE: 4")
            sys.exit(4)

        # Throw a debug warning about the "--all" mode being active
        logger.warning("%s" % ("Sub-mode: <all> is active, any operation will affect all target objects."))

        # Extract the keys of the YAML object
        keyList = utils.extractKeys(s.GetPublicDict())

        # Override the argument list
        args.targetObject = keyList

    # --all was not used
    else:
        pass

    # Run the function
    newData = utils.executeSet(s, args.targetObject, verbosityFlag, False)

    # Attempt to write the YAML object back to the file
    utils.exportYamlData(newData, fileString)
#}}}

# MAIN: This is the LIST block {{{
elif args.func=="list":
    logger.debug("Mode: <list>")

    # A secondary check for the sub mode argument.
    # In case the "ALL" sub mode is active, we need to gather all the keys
    # from the YAML object and build our own targetObject.

    # --mode used: bash
    if args.mode == "bash":
        # Run the function
        utils.executeList(s, args.mode)

    # --mode used: python
    elif args.mode == "python":
        # Run the function
        utils.executeList(s, args.mode)

    # handle non supported --mode usage
    elif args.mode != "default":
        logger.error("%s: %s" % ("Unknown --mode", args.mode))

        # Exit
        logger.critical("EXIT_CODE: 5")
        sys.exit(5)

    else:
        utils.executeList(s, args.mode)
#}}}

# MAIN: This is an EMPTY block {{{
else:
    logger.critical("Function list out of range.")
#}}}

# Any additional function goes here.

# }}}

# <END__>
pass

# vim: ts=4 ft=python nowrap fdm=marker
