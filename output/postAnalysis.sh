#!/bin/bash

source ~/.bash_profile
conda activate py-plan2014

currentDir=$(pwd)

loc="$1"                # home directory for the optimization code
folderName="$2"         # name of folder with results
inputTrace="$3"         # trace type to simulate: historic, stochastic, etc...
inputData="$4"          # input data file name without extension

# -----------------------------------------------------------------------------
# policy simulation - time series and objective functions
# -----------------------------------------------------------------------------

echo "... policy simulation ..."
python postScripts/policySimulation.py "${loc}" "${folderName}" "${inputTrace}" "${inputData}"