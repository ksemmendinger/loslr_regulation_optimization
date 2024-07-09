# -----------------------------------------------------------------------------
# import libraries
# -----------------------------------------------------------------------------

import os
import sys
import toml
import pathlib
import pandas as pd
from glob import glob
from datetime import datetime
from importlib import import_module

# -----------------------------------------------------------------------------
# script setup
# -----------------------------------------------------------------------------

# set variables from command line input
args = sys.argv

# args = [
#     "",
#     "/Users/kylasemmendinger/Documents/github/loslr_regulation_optimization",
#     "ruleCurve_Bv7_offSepRule_netAnnualAverage_12month_sqAR_9dv_7obj_1961_2020_75000nfe",
#     "historic",
#     "1961_2020",
#     # "12month_0",
# ]

# [1]: path to working directory
os.chdir(args[1])

# [2]: folder name of experiment
expName = args[2]

# [3]: path to input data to simulate (historic, stochastic, climate_change)
traceType = args[3]

# [4]: input trace: may be empty string to simulate all traces in a specified folder
inputTrace = args[4]

# COMMENTED OUT BECAUSE THIS SHOULD ALWAYS CORRESPOND TO THE INPUT FILE IN THE CONFIG
# YOU WOULDN'T TRAIN ON 12MONTH FORECASTS AND SIMULATE WITH 3MONTH
# # [5]: input data file: may be specific to certain forecast information
# inputData = args[5]

# -----------------------------------------------------------------------------
# load functions for simulation - specified in config file
# -----------------------------------------------------------------------------

# load configuration file from folder
configFile = "output/data/" + expName + "/config.toml"
with open(configFile, "r") as f:
    config = toml.load(f)

# get decision variable info from config file
decisionVariables = config["decisionVariables"]

# get simulation function names from config file
releaseFunctionName = config["experimentalDesign"]["releaseFunction"]
planLimitsName = config["experimentalDesign"]["limitType"]
septemberRule = config["experimentalDesign"]["septemberRule"]
stlawRoutingName = config["experimentalDesign"]["stlawRouting"]
objectiveFormulation = config["performanceIndicators"]["objectiveFormulation"]
objectiveModelNames = config["performanceIndicators"]["objectiveModels"]

# release function parameters
releaseFunInputs = config["releaseFunction"]

# input data to simulate
optimizedInput = config["experimentalDesign"]["inputFile"]
inputData = optimizedInput.split("/")[1]

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

# import objective function simulation script
objectiveFunctions = import_module(
    "objectiveFunctions." + objectiveFormulation + ".objectiveSimulation"
)

# import individual objecive function modules
piModels = []
for x in range(len(objectiveModelNames)):
    tmpPI = objectiveModelNames[x]
    tmp = import_module(
        "objectiveFunctions." + objectiveFormulation + ".functions." + tmpPI
    )
    piModels.append(tmp)

# -----------------------------------------------------------------------------
# get filelist of user specified input data to simulate
# -----------------------------------------------------------------------------

# get filelist in trace type
path = "input/" + traceType
filelist = [
    t
    for t in [f for f in glob(path + "/**", recursive=True) if inputTrace in f]
    if inputData in t
]

# -----------------------------------------------------------------------------
# loading policy information
# -----------------------------------------------------------------------------

# read in file with candidate policies
pols = pd.read_csv("output/data/" + expName + "/satisficingPolicies.csv")
pols = pols.loc[:, ["ID"] + decisionVariables["dvName"]]
npol = pols.shape[0]

# -----------------------------------------------------------------------------
# policy simulation
# -----------------------------------------------------------------------------

# extract and format decision variables for each policy
for p in range(npol):
    pID = pols.loc[p, "ID"]
    print(pID)

    # extract decision variables from csv
    vars = pols.loc[p, decisionVariables["dvName"]].to_list()

    # format decision variables into names dictionary
    pars = formatDecisionVariables(vars, **releaseFunInputs)

    # simulate each trace in the filelist
    for f in range(len(filelist)):
        # load input data
        input = pd.read_table(filelist[f])

        # FIX INPUT DATA TO FILTER OUT NA VALUES FOR FORECAST AT THE END OF DATA FRAME
        # drop end dataframe -- maybe from in[itdata names?]
        fcstNA = input["forNTS"].notna()
        fcstNA[:48] = True
        input = input.loc[fcstNA, :]

        # simulate time series of water levels and flows
        outSim = optimizationSimulation.simulation(
            input,
            releaseFunInputs,
            getReleaseFunctionInputs,
            releaseFunction,
            septemberRule,
            getPlanLimitsInputs,
            planLimits,
            getStLawrenceRoutingInputs,
            stLawrenceRouting,
            pars,
        )

        # startTimeObj = datetime.now()

        # filter out first year of spinup data from time series
        outSim = outSim.loc[outSim["Year"] > min(outSim.Year), :].reset_index(drop=True)

        # convert data frame to dictionary for faster computation
        data = {x: outSim[x].values for x in outSim}

        # run pi models over time series and return full simulation results
        (
            upcoast,
            downcoast,
            commNav,
            hydro,
            mMarsh,
            muskrat,
            recBoat,
        ) = objectiveFunctions.objectiveSimulation(data, piModels, "simulation")

        output = (
            outSim.merge(upcoast, on=["Sim", "Year", "Month", "QM"], how="left")
            .merge(downcoast, on=["Sim", "Year", "Month", "QM"], how="left")
            .merge(commNav, on=["Sim", "Year", "Month", "QM"], how="left")
            .merge(hydro, on=["Sim", "Year", "Month", "QM"], how="left")
            .merge(mMarsh, on=["Year", "QM"], how="left")
            .merge(muskrat, on=["Year", "QM"], how="left")
            .merge(recBoat, on=["Sim", "Year", "Month", "QM"], how="left")
        )

        # save output
        outPath = (
            "output/data/"
            + expName
            + "/simulation/"
            + traceType
            + "/"
            + inputTrace.split("/")[0]
            + "/id"
            + str(pID)
        )
        path = pathlib.Path(outPath)
        path.mkdir(parents=True, exist_ok=True)
        output.to_csv(outPath + "/sim.csv", sep=",", index=False)

        # endTimeObj = datetime.now()
