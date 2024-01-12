# import libraries
import os
import sys
import toml
import pathlib
import numpy as np
import pandas as pd
from math import *
from borg import *
from datetime import datetime
from functools import partial

args = sys.argv
# args = ["", "mac_ext", "config/glam/run_of_the_mill.toml", "1"]

# -----------------------------------------------------------------------------
# set up experimental design from inputs
# -----------------------------------------------------------------------------

# [1]: location to run [mac_loc, glhpc]
loc = args[1]
if loc == "mac_loc":
    wd = "/Users/kylasemmendinger/Documents/CIGLR/Research/dps"
elif loc == "mac_ext":
    wd = "/Volumes/ky_backup/dps"
elif loc == "glhpc":
    wd = "/home/kylasr/optimization"
os.chdir(wd)

# [2]: path to configuration file
configFile = args[2]

# [3]: seed [int]
nseed = int(args[3])

# load configuration file from folder
with open(configFile, "r") as f:
    config = toml.load(f)

# set variables from config file
releaseFun = config["experimentalDesign"]["releaseFunction"]
limitType = config["experimentalDesign"]["limitType"]
septemberRule = config["experimentalDesign"]["septemberRule"]
leadtime = config["experimentalDesign"]["forecastLeadTime"]
skill = config["experimentalDesign"]["forecastSkill"]
nvars = config["experimentalDesign"]["numDV"]
nobjs = config["experimentalDesign"]["numObj"]
nconstrs = config["experimentalDesign"]["numCon"]
trace = config["experimentalDesign"]["trace"]
nfe = config["experimentalDesign"]["nfe"]
popSize = config["experimentalDesign"]["popSize"]
metFreq = config["experimentalDesign"]["metFreq"]
piWeighting = config["performanceIndicators"]["metricWeighting"]

# supply trace - set routing version to run with SLON or Ottawa River flows [historic, stochastic]
if trace == "stochastic":
    version = "stochastic"
else:
    version = "historic"

# -----------------------------------------------------------------------------
# file pointers
# -----------------------------------------------------------------------------

# input data to load
dataName = version + "/" + trace + "/" + leadtime + "_" + skill

# output folder name
folderName = (
    releaseFun
    + "_"
    + limitType
    + "_"
    + septemberRule
    + "SepRule"
    + "_"
    + piWeighting
    + "_"
    + leadtime
    + "_"
    + str(skill)
    + "_"
    + str(nvars)
    + "dv_"
    + str(nobjs)
    + "obj_"
    + trace
    + "_"
    + str(nfe)
    + "nfe"
)

# create output directory
path = pathlib.Path("output/data/" + folderName + "/raw/")
path.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------------------------------
# set up borg
# -----------------------------------------------------------------------------

# import policy simulation function
import optimizationSimulation

# set seed
Configuration.seed(nseed)

# initialize borg with problem --> partial(fn, data_name)(*vars)
borg = Borg(
    nvars,
    nobjs,
    nconstrs,
    partial(
        optimizationSimulation.optimization,
        dataName,
        version,
        limitType,
        septemberRule,
        releaseFun,
        config["decisionVariables"],
        piWeighting,
    ),
)

# set decision variable bounds
b = config["decisionVariables"]["normalizedRange"]
lowerb = [b[0]] * nvars
upperb = [b[1]] * nvars
borg.setBounds(*[list(x) for x in list(zip(lowerb, upperb))])

# set objective tolerance epsilons - defines "meaningful" improvement
epsilon = config["performanceIndicators"]["epsilonValue"]
borg.setEpsilons(*epsilon)

# set up configuration
borgConfig = {
    "maxEvaluations": nfe,
    "initialPopulationSize": popSize,
    "runtimefile": "output/data/" + folderName + "/raw/runtime_S" + str(nseed) + ".txt",
    "runtimeformat": "borg",
    "frequency": metFreq,
}

# -----------------------------------------------------------------------------
# write config file
# -----------------------------------------------------------------------------

# for first seed, copy config file to output directory
if nseed == 1:
    with open("output/data/" + folderName + "/config.toml", "w") as f:
        toml.dump(config, f)

# -----------------------------------------------------------------------------
# run borg
# -----------------------------------------------------------------------------

# run borg
result = borg.solve(borgConfig)

# -----------------------------------------------------------------------------
# save output
# -----------------------------------------------------------------------------

output_location = (
    "output/data/" + folderName + "/raw/pareto_front_S" + str(nseed) + ".txt"
)

# write objective values and decision variable values to output file
with open(output_location, "w") as f:
    f.write("# Borg Optimization Results\n")
    f.write(
        "# First "
        + str(nvars)
        + " are the decision variables, "
        + "last "
        + str(nobjs)
        + " are the "
        + "objective values\n"
    )

    for solution in result:
        line = ""

        for i in range(len(solution.getVariables())):
            line = line + (str(solution.getVariables()[i])) + " "

        for i in range(len(solution.getObjectives())):
            line = line + (str(solution.getObjectives()[i])) + " "

        line = line + "\n"

        f.write(line)
