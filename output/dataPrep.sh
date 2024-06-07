#!/bin/bash

source ~/.bash_profile
conda activate py-plan2014

currentDir=$(pwd)

loc="$1"
folderName="$2"
nseeds="$3"
nobjs="$4"

# path where output data is stored
moeaFileDirName="${loc}"/output/data

# path to moeaFramework/ folder
# NOTE: DO NOT store moeaFramework/ on Google Drive Desktop or Box Drive - the syncing will mess up results
# moeaDir="/Users/kylasemmendinger/Documents/github/loslr_regulation_optimization/moeaFramework"
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