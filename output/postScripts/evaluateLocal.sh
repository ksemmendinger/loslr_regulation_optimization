#!/bin/bash

source ~/.bash_profile
conda activate py-plan2014

currentDir=$(pwd)
nobjs=7

loc="$1"
folderName="$2"
nseeds="$3"

# -----------------------------------------------------------------------------
# format data
# -----------------------------------------------------------------------------

echo "... formatting raw data ..."
python postScripts/dataFormat.py ${loc} ${folderName} ${nseeds}

# -----------------------------------------------------------------------------
# MOEA performance
# -----------------------------------------------------------------------------

echo "... calculating borg metrics ..."

fileDirName="${currentDir}/data"
cd /Users/kylasemmendinger/Desktop/moeaFramework
./find_metrics.sh ${fileDirName} ${folderName} ${nseeds} ${nobjs}

echo "... making convergence plots ..."
cd  ${currentDir}
Rscript postScripts/convergencePlots.R ${loc} ${folderName} ${nseeds}

# -----------------------------------------------------------------------------
# policy simulation in glrrm
# -----------------------------------------------------------------------------

echo "... policy simulation ..."
python postScripts/policySimulation.py ${loc} ${folderName}

echo "... formatting glrrm output ..."
python postScripts/glrrmOutputFormat.py ${loc} ${folderName}

echo "... pi simulation ..."
python postScripts/piSimulation.py ${loc} ${folderName}

# if [ $1 != "baseline" ]; then

#     folderName="$1"
#     nseeds="$2"

#     # loc="$1"
#     # nseeds="$2"
#     # leadtime="$3"
#     # skill="$4"
#     # nfe="$5"
#     # nobjs="$6"
#     # nvars="$7"
#     # nworkers="$8"
#     # form="$9"

#     # if [ $9 == "RBF" ]
#     # then
#     # folderName="RBF_${leadtime}_${skill}_${nfe}nfe_${nvars}dvs"
#     # else
#     # folderName="${leadtime}_${skill}_${nfe}nfe_${nvars}dvs"
#     # fi

#     currentDir=$(pwd)

#     # echo "... formatting raw data ..."
#     # python postScripts/dataFormat.py ${loc} ${nseeds} ${leadtime} ${skill} ${nfe} ${nvars} ${form}

#     # -----------------------------------------------------------------------------
#     # MOEA performance
#     # -----------------------------------------------------------------------------

#     # echo "... calculating borg metrics ..."
#     # fileDirName="/Volumes/ky_backup/dps/output/data"

#     # nobjs=7
#     # cd /Users/kylasemmendinger/Desktop/moeaFramework
#     # ./find_metrics.sh ${fileDirName} ${folderName} ${nseeds} ${nobjs}

#     echo "... making convergence plots ..."
#     cd  ${currentDir}
#     Rscript postScripts/convergencePlots.R mac_ext ${folderName} ${nseeds}

#     # -----------------------------------------------------------------------------
#     # parallel axis plot 
#     # -----------------------------------------------------------------------------

#     # echo "... parallel axis plot ..."
#     # Rscript postScripts/paretoPlots.R ${loc} ${nseeds} ${leadtime} ${skill} ${nfe} ${nvars} ${form}

#     # # -----------------------------------------------------------------------------
#     # # simulation
#     # # -----------------------------------------------------------------------------

#     # echo "... simulating policies for historic, climate change, and stochastic supplies ..."

#     # echo "... simulating policies for historic supplies ..."
#     # python postScripts/policySimulation.py ${loc} historic off ${leadtime} ${skill} ${nfe} ${nvars} ${nworkers}

#     # echo "... simulating policies for stochastic supplies ..."
#     # python postScripts/policySimulation.py ${loc} stochastic on ${leadtime} ${skill} ${nfe} ${nvars} ${nworkers}

#     # echo "... simulating policies for climate change supplies ..."
#     # python postScripts/policySimulation.py ${loc} climate_scenarios off ${leadtime} ${skill} ${nfe} ${nvars} ${nworkers}

#     # wait
#     # echo "... done simulating policies ..."

#     # # -----------------------------------------------------------------------------
#     # # robustness check and scenario discovery
#     # # -----------------------------------------------------------------------------

#     # echo "... scenario discovery ..."
#     # python postScripts/scenarioDiscovery.py ${loc} ${leadtime} ${skill} ${nfe} ${nvars} ${nworkers}

#     # echo "... making plots ..."
#     # Rscript postScripts/scenarioDiscoveryPlots.R ${loc} ${leadtime} ${skill} ${nfe} ${nvars}

#     # # -----------------------------------------------------------------------------
#     # # impact zones
#     # # -----------------------------------------------------------------------------

#     # echo "... impact zones ..."
#     # python postScripts/impactZones.py ${loc} ${leadtime} ${skill} ${nfe} ${nvars} ${nworkers}
    
#     # # -----------------------------------------------------------------------------
#     # # seaway metrics
#     # # -----------------------------------------------------------------------------

#     # echo "... seaway metrics ..."
#     # python postScripts/seawayMetrics.py ${loc} ${leadtime} ${skill} ${nfe} ${nvars} ${nworkers}

#     # # -----------------------------------------------------------------------------
#     # # h criteria
#     # # -----------------------------------------------------------------------------

#     # echo "...h criteria ..."
#     # python postScripts/hCriteria.py ${loc} ${leadtime} ${skill} ${nfe} ${nvars}

#     # # -----------------------------------------------------------------------------
#     # # water level statistics
#     # # -----------------------------------------------------------------------------

#     # echo "... water level statistics ..."
#     # python postScripts/hydroStatistics.py ${loc} ${leadtime} ${skill} ${nfe} ${nvars} ${nworkers}

#     # # -----------------------------------------------------------------------------
#     # # annual objective statistics
#     # # -----------------------------------------------------------------------------

#     # echo "... water level statistics ..."
#     # python postScripts/annualObjValues.py ${loc} ${leadtime} ${skill} ${nfe} ${nvars} ${nworkers}

#     wait
#     echo "... done with post processing ... "

# else

#     nworkers="$2"

#     # # -----------------------------------------------------------------------------
#     # # simulation
#     # # -----------------------------------------------------------------------------

#     # echo "... simulating policies for historic, climate change, and stochastic supplies ..."

#     # echo "... simulating policies for historic supplies ..."
#     # python postScripts/policySimulation.py mac_loc historic off baseline ${nworkers}

#     # echo "... simulating policies for stochastic supplies ..."
#     # python postScripts/policySimulation.py mac_loc stochastic on baseline ${nworkers}

#     # echo "... simulating policies for climate change supplies ..."
#     # python postScripts/policySimulation.py mac_loc climate_scenarios off baseline ${nworkers}

#     # wait
#     # echo "... done simulating policies ..."

#     # # -----------------------------------------------------------------------------
#     # # robustness check and scenario discovery
#     # # -----------------------------------------------------------------------------

#     # echo "... scenario discovery ..."
#     # python postScripts/scenarioDiscovery.py mac_loc baseline ${nworkers}

#     # # -----------------------------------------------------------------------------
#     # # impact zones
#     # # -----------------------------------------------------------------------------

#     # echo "... impact zones ..."
#     # python postScripts/impactZones.py mac_loc baseline ${nworkers}
    
#     # # -----------------------------------------------------------------------------
#     # # seaway metrics
#     # # -----------------------------------------------------------------------------

#     # echo "... seaway metrics ..."
#     # python postScripts/seawayMetrics.py baseline ${nworkers}

#     # # -----------------------------------------------------------------------------
#     # # h criteria
#     # # -----------------------------------------------------------------------------

#     # echo "...h criteria ..."
#     # python postScripts/hCriteria.py mac_loc baseline

#     # # -----------------------------------------------------------------------------
#     # # water level statistics
#     # # -----------------------------------------------------------------------------

#     # echo "... water level statistics ..."
#     # python postScripts/hydroStatistics.py mac_loc baseline ${nworkers}

#     # # -----------------------------------------------------------------------------
#     # # annual objective statistics
#     # # -----------------------------------------------------------------------------

#     # echo "... annual objective statistics ..."
#     # python postScripts/annualObjValues.py mac_loc baseline ${nworkers}

#     # wait
#     # echo "... done with post processing ... "
# fi