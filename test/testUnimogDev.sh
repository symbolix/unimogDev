#!/bin/bash -f
# ;---------------------------------------------------------------------------------------
# ; {UNIMOG} Integrated Pipeline Tools
# ;
# ; Name    :   unimogDev.env
# ; Author  :   Muhittin Bilginer
# ; Created :   03/10/2015
# ;
# ; Info    :   This file is responsible for propagating the DEV flags across the Unimog 
# ;             environment. It uses another core Unimog tool "unimogDev.py" to gather the
# ;             required information.
# ;
# ; This tool is part of Unimog.
# ;----------------------------------------------------------------------------------------

#export ELEMENTS=`unimogDev.py -v=0 list --mode=bash`
export ELEMENTS=`${UNIMOG_LOCAL_SITE}/scripts/bin/unimogDev.py -v=0 list --mode=bash`

# Cycle on the incoming element list and propagate the variables
for element in $ELEMENTS
do
    # Run the setup-up cycle
    # Debug lines
    #echo -n "Current variable is: ["$element"]";
    #echo ""; echo -n
    
    # The actual command
    eval "export $element"
done 
