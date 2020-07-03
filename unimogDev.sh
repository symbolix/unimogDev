#!/bin/bash -f
# ;---------------------------------------------------------------------------------------
# ; {UNIMOG} Integrated Pipeline Tools
# ;
# ; Name    :   unimogDev.sh
# ; Version :   0.0.1.[4]
# ; Author  :   Muhittin Bilginer
# ; Created :   08/10/2014
# ; Edited  :   08/10/2014
# ;
# ; Info    :   This is a front-end wrapper script for the "unimogDev.py" tool
# ;
# ; This tool is part of Unimog.
# ;----------------------------------------------------------------------------------------

# Assign the execution variable
command=unimogDev.py 

# Utility Functions {{{

# Utility: Get File Name {{{
function getFileName() {
    (
    local self=$1
    local filename=$(basename $self)
    
    # Return the file name.
    echo $filename
    )
}
# }}}

# Utility: Build Command String {{{
function buildCommandString() {
    # Check for SITE/LOCALSITE priorities
    if [[ $UNIMOG_PIPELINE_DEV -eq 0 ]]; then
        # Debug line
        #echo "UNIMOG_PIPELINE_DEV is \"OFF\", SITE has the priority";
        # PIPELINE_DEV mode is "OFF", the primary location should be the global site
        primaryCommandString=/tools/SITE/$OSname/scripts/bin/${command}
        # And the scondary location should be the local site
        secondaryCommandString=$HOME/tools/LOCALSITE/$OSname/scripts/bin/${command}
        
    else
        # Debug line
        #echo "UNIMOG_PIPELINE_DEV is \"ON\", LOCALSITE has the priority";
        # PIPELINE_DEV mode is "ON", the primary location should be the local site
        primaryCommandString=$HOME/tools/LOCALSITE/$OSname/scripts/bin/${command}
        # And the scondary location should be the global site
        secondaryCommandString=/tools/SITE/$OSname/scripts/bin/${command}
    fi
}
# }}}

# Any other utility function goes here

# }}}

# Assign a debug signature
currentFileName=$(getFileName $BASH_SOURCE)

# Intro {{{
echo ""
echo "${currentFileName}.sh v0.0.1.[4] (BETA) (Darwin64) | Dev Environment Wrapper Script | {UNIMOG} Integrated Pipeline Tools"
# }}}

if [ $# -eq 0 ]; then
    # Debug line
    #echo "No arguments supplied"
    # Pass, do nothing, WARNING: Do not remove the ":" below!
    :
else
    # Build the command string
    buildCommandString

    # Execute the command
    if [ ! -f ${primaryCommandString} ]; then
        if [ ! -f ${secondaryCommandString} ]; then
            echo -e "\n<"$currentFileName"> (ERROR): Core pipeline tool: \"${command}\" is not accessible!\n"
        else
            # Fallback to the secondary command
            $secondaryCommandString $*
        fi
    else
        # Execute the primary command
        ${primaryCommandString} $*
    fi

    # Check for any errors
    if [ "$?" -ne "0" ]; then
        echo -e "\n<"$currentFileName"> (ERROR) A critical error regarding a core pipeline tool: \"${command}\" has occured!\n"
    fi

fi

# Refresh the environment
# source $HOME/tools/LOCALSITE/$OSname/.env/unimogDev.env
source $UNIMOG_LOCAL_SITE/unimogDev.env

# vim: nowrap fdm=marker
