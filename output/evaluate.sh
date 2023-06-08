#!/bin/bash

source ~/.bash_profile
conda activate py-plan2014

if [ $1 != "baseline" ]; then

    loc="$1"
    nseeds="$2"
    leadtime="$3"
    skill="$4"
    nfe="$5"
    nobjs="$6"
    nvars="$7"
    nworkers="$8"

    echo "... formatting raw data ..."
    python postScripts/dataFormat.py ${loc} ${nseeds} ${leadtime} ${skill} ${nfe} ${nvars}

    # -----------------------------------------------------------------------------
    # simulation
    # -----------------------------------------------------------------------------

    echo "... simulating policies for historic, climate change, and stochastic supplies ..."

    echo "... simulating policies for historic supplies ..."
    python postScripts/policySimulation.py ${loc} historic off ${leadtime} ${skill} ${nfe} ${nvars} ${nworkers}

    echo "... simulating policies for stochastic supplies ..."
    python postScripts/policySimulation.py ${loc} stochastic on ${leadtime} ${skill} ${nfe} ${nvars} ${nworkers}

    echo "... simulating policies for climate change supplies ..."
    python postScripts/policySimulation.py ${loc} climate_scenarios off ${leadtime} ${skill} ${nfe} ${nvars} ${nworkers}

    wait
    echo "... done simulating policies ..."

    # -----------------------------------------------------------------------------
    # robustness check and scenario discovery
    # -----------------------------------------------------------------------------

    echo "... scenario discovery ..."
    python postScripts/scenarioDiscovery.py ${loc} ${leadtime} ${skill} ${nfe} ${nvars} ${nworkers}

    # echo "... making plots ..."
    # Rscript postScripts/scenarioDiscoveryPlots.R ${loc} ${leadtime} ${skill} ${nfe} ${nvars}

    # -----------------------------------------------------------------------------
    # impact zones
    # -----------------------------------------------------------------------------

    echo "... impact zones ..."
    python postScripts/impactZones.py ${loc} ${leadtime} ${skill} ${nfe} ${nvars} ${nworkers}

    # -----------------------------------------------------------------------------
    # seaway metrics
    # -----------------------------------------------------------------------------

    echo "... seaway metrics ..."
    python postScripts/seawayMetrics.py ${loc} ${leadtime} ${skill} ${nfe} ${nvars} ${nworkers}

    # -----------------------------------------------------------------------------
    # h criteria
    # -----------------------------------------------------------------------------

    echo "...h criteria ..."
    python postScripts/hCriteria.py ${loc} ${leadtime} ${skill} ${nfe} ${nvars}

    # -----------------------------------------------------------------------------
    # water level statistics
    # -----------------------------------------------------------------------------

    echo "... monthly water level statistics ..."
    python postScripts/hydroStatistics.py ${loc} ${leadtime} ${skill} ${nfe} ${nvars} ${nworkers}

    # -----------------------------------------------------------------------------
    # annual hydrologic statistics
    # -----------------------------------------------------------------------------

    echo "... annual water level statistics ..."
    python postScripts/annualStatistics.py ${loc} ${leadtime} ${skill} ${nfe} ${nvars} ${nworkers}

    # -----------------------------------------------------------------------------
    # annual objective statistics
    # -----------------------------------------------------------------------------

    echo "... water level statistics ..."
    python postScripts/annualObjValues.py ${loc} ${leadtime} ${skill} ${nfe} ${nvars} ${nworkers}

    wait
    echo "... done with post processing ... "

else

    nworkers="$2"

    # -----------------------------------------------------------------------------
    # simulation
    # -----------------------------------------------------------------------------

    echo "... simulating policies for historic, climate change, and stochastic supplies ..."

    echo "... simulating policies for historic supplies ..."
    python postScripts/policySimulation.py hopper historic off baseline ${nworkers}

    echo "... simulating policies for stochastic supplies ..."
    python postScripts/policySimulation.py hopper stochastic on baseline ${nworkers}

    echo "... simulating policies for climate change supplies ..."
    python postScripts/policySimulation.py hopper climate_scenarios off baseline ${nworkers}

    wait
    echo "... done simulating policies ..."

    # -----------------------------------------------------------------------------
    # robustness check and scenario discovery
    # -----------------------------------------------------------------------------

    echo "... scenario discovery ..."
    python postScripts/scenarioDiscovery.py hopper baseline ${nworkers}

    # -----------------------------------------------------------------------------
    # impact zones
    # -----------------------------------------------------------------------------

    echo "... impact zones ..."
    python postScripts/impactZones.py hopper baseline ${nworkers}

    # -----------------------------------------------------------------------------
    # seaway metrics
    # -----------------------------------------------------------------------------

    echo "... seaway metrics ..."
    python postScripts/seawayMetrics.py baseline ${nworkers}

    # -----------------------------------------------------------------------------
    # h criteria
    # -----------------------------------------------------------------------------

    echo "...h criteria ..."
    python postScripts/hCriteria.py hopper baseline

    # -----------------------------------------------------------------------------
    # water level statistics
    # -----------------------------------------------------------------------------

    echo "... water level statistics ..."
    python postScripts/hydroStatistics.py hopper baseline ${nworkers}

    # -----------------------------------------------------------------------------
    # annual objective statistics
    # -----------------------------------------------------------------------------

    echo "... water level statistics ..."
    python postScripts/annualObjValues.py hopper baseline ${nworkers}

    wait
    echo "... done with post processing ... "

fi