# import libraries
import os
import sys
import toml
import pathlib
from math import *
from borg import *
from functools import partial
from importlib import import_module

args = sys.argv
# args = [
#     "",
#     "/Users/kylasemmendinger/Library/CloudStorage/GoogleDrive-kylasr@umich.edu/My Drive/loslrRegulation",
#     #     "config/glam/juneWorkshop.toml",
#     "config/firo/config_12_lm_4inputs.toml",
#     "1",
# ]

# -----------------------------------------------------------------------------
# set up experimental design from command line inputs
# -----------------------------------------------------------------------------

# [1]: location to run [mac_loc, glhpc]
wd = args[1]
os.chdir(wd)

# [2]: path to configuration file
configFile = args[2]

# [3]: seed [int]
nseed = int(args[3])

# -----------------------------------------------------------------------------
# set variables for experiment form config file
# -----------------------------------------------------------------------------

# load configuration file from folder
with open(configFile, "r") as f:
    config = toml.load(f)

# get optimization parameters from config file
nvars = config["optimizationParameters"]["numDV"]
nobjs = config["optimizationParameters"]["numObj"]
nconstrs = config["optimizationParameters"]["numCon"]
nfe = config["optimizationParameters"]["nfe"]
popSize = config["optimizationParameters"]["popSize"]
metFreq = config["optimizationParameters"]["metFreq"]

# get simulation parameters from config file
releaseFunctionName = config["experimentalDesign"]["releaseFunction"]
planLimitsName = config["experimentalDesign"]["limitType"]
septemberRule = config["experimentalDesign"]["septemberRule"]
stlawRoutingName = config["experimentalDesign"]["stlawRouting"]
slonValues = config["experimentalDesign"]["slonValues"]
leadtime = config["experimentalDesign"]["forecastLeadTime"]
skill = config["experimentalDesign"]["forecastSkill"]
trace = config["experimentalDesign"]["trace"]

# get decision variable info from config file
decisionVariables = config["decisionVariables"]

# release function parameters
releaseFunInputs = config["releaseFunction"]

# get objective function parameters from config file
epsilon = config["performanceIndicators"]["epsilonValue"]
piWeighting = config["performanceIndicators"]["metricWeighting"]
objectiveFunctionName = config["performanceIndicators"]["objectiveFunction"]

# supply trace - set routing version to run with SLON or Ottawa River flows [historic, stochastic]
version = "historic"
# if trace == "stochastic":
#     version = "stochastic"
# else:
#   version = "historic"

# -----------------------------------------------------------------------------
# load functions for simulation - specified in config file
# -----------------------------------------------------------------------------

sys.path.append(".")

# import policy simulation function
import optimizationSimulation

# import config specified simulation functions
formatDecisionVariables = import_module(
    "functions.release." + releaseFunctionName
).formatDecisionVariables
getReleaseFunctionInputs = import_module(
    "functions.release." + releaseFunctionName
).getReleaseFunctionInputs
releaseFunction = import_module(
    "functions.release." + releaseFunctionName
).releaseFunction
getPlanLimitsInputs = import_module(
    "functions.limits." + planLimitsName
).getPlanLimitsInputs
planLimits = import_module("functions.limits." + planLimitsName).planLimits
getStLawrenceRoutingInputs = import_module(
    "functions.routing." + stlawRoutingName
).getStLawrenceRoutingInputs
stLawrenceRouting = import_module(
    "functions.routing." + stlawRoutingName
).stLawrenceRouting

if septemberRule != "off":
    septemberRule = import_module("functions.limits.septemberRule").septemberRule

# import objective functions
objectiveFunctions = import_module("objectiveFunctions." + objectiveFunctionName)

# -----------------------------------------------------------------------------
# file pointers
# -----------------------------------------------------------------------------

# input data to load
dataName = version + "/" + trace + "/" + leadtime + "_" + skill

# output folder name
folderName = (
    releaseFunctionName
    + "_"
    + planLimitsName
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

# set seed
Configuration.seed(nseed)

# initialize borg with problem --> partial(fn, data_name)(*vars)
borg = Borg(
    nvars,
    nobjs,
    nconstrs,
    partial(
        optimizationSimulation.optimization,
        formatDecisionVariables,
        decisionVariables,
        dataName,
        releaseFunInputs,
        getReleaseFunctionInputs,
        releaseFunction,
        septemberRule,
        getPlanLimitsInputs,
        planLimits,
        getStLawrenceRoutingInputs,
        stLawrenceRouting,
        objectiveFunctions,
    ),
)

# set decision variable bounds
if str(decisionVariables["normalized"]) == True:
    lowerBounds = [decisionVariables["normalizedRange"][0]] * nvars
    upperBounds = [decisionVariables["normalizedRange"][1]] * nvars
else:
    lowerBounds = decisionVariables["lowerBounds"]
    upperBounds = decisionVariables["upperBounds"]
borg.setBounds(*[list(x) for x in list(zip(lowerBounds, upperBounds))])

# set objective tolerance epsilons - defines "meaningful" improvement
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
