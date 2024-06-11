#!/bin/bash

source ~/.bash_profile
conda activate py-plan2014

currentDir=$(pwd)

loc="$1"                # home directory for the optimization code
folderName="$2"         # name of folder with results
nseeds="$3"             # number of random seeds to run optimization
nobjs="$4"              # number of objectives included in optimization

# path where output data is stored
moeaFileDirName="${loc}"/output/data

# path to `moeaFramework/` folder - NOTE: DO NOT store `moeaFramework/` on Google Drive Desktop or Box Drive, the syncing will freeze the code
moeaDir="${loc}"/moeaFramework

# -----------------------------------------------------------------------------
# format data
# -----------------------------------------------------------------------------

echo "... formatting raw data ..."
python postScripts/dataFormat.py "${loc}" "${folderName}" "${nseeds}"

# -----------------------------------------------------------------------------
# MOEA performance
# -----------------------------------------------------------------------------

echo "... calculating borg metrics ..."

cd "${moeaDir}"
./find_metrics.sh "${moeaFileDirName}" "${folderName}" "${nseeds}" "${nobjs}"

echo "... making convergence plots ..."
cd  ${currentDir}
Rscript postScripts/convergencePlots.R "${loc}" "${folderName}" "${nseeds}"