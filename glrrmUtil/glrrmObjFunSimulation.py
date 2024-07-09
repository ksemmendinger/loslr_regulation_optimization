# import libraries
import os
import sys
import toml
import pathlib
import numpy as np
import pandas as pd
from glob import glob
from datetime import datetime
from importlib import import_module


# from pathlib import Path
# from os.path import exists

# -----------------------------------------------------------------------------
# script setup
# -----------------------------------------------------------------------------

# set variables from command line input
args = sys.argv
# args = [
#     "",
#     "/Users/kylasemmendinger/Documents/github/loslr_regulation_optimization",
#     "baseline/Bv7_GLRRM",
# ]

# [1]: path to working directory
os.chdir(args[1])

# [2]: folder name of experiment
folderName = args[2]

# read config for objective function modules
configFile = "output/data/" + folderName + "/config.toml"
with open(configFile, "r") as f:
    config = toml.load(f)

# load objective function modules
objectiveFormulation = config["performanceIndicators"]["objectiveFormulation"]
objectiveModelNames = config["performanceIndicators"]["objectiveModels"]

sys.path.append(".")
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
# run GLRRM output through PI models
# -----------------------------------------------------------------------------

# get filelist
# path = "output/data/" + folderName + "/simulation/historic"
# filelist = [
#     f for f in glob(path + "/*/formattedOutput**", recursive=True) if os.path.isfile(f)
# ]
path = "output/data/" + folderName
filelist = [
    f
    for f in glob(path + "/simulation/**", recursive=True)
    if "glrrmOutputFormatted.csv" in f
]

for i in range(len(filelist)):
    startTimeObj = datetime.now()
    print(pathlib.PurePath(filelist[i]).parent.name)

    # load glrrm output
    fn = filelist[i]
    dataTS = pd.read_csv(fn, sep=",")
    # data = data.iloc[:, 1:85]

    # format output
    # dataTS = data.drop(list(range(0, 48))).reset_index(drop=True)
    # dataTS = dataTS.drop(
    #     list(range(dataTS.shape[0] - 48, dataTS.shape[0]))
    # ).reset_index(drop=True)
    # dataTS = {x: dataTS[x].values for x in dataTS}

    # convert data frame to dictionary for faster computation
    data = {x: dataTS[x].values for x in dataTS}

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
        dataTS.merge(upcoast, on=["Sim", "Year", "Month", "QM"], how="left")
        .merge(downcoast, on=["Sim", "Year", "Month", "QM"], how="left")
        .merge(commNav, on=["Sim", "Year", "Month", "QM"], how="left")
        .merge(hydro, on=["Sim", "Year", "Month", "QM"], how="left")
        .merge(mMarsh, on=["Year", "QM"], how="left")
        .merge(muskrat, on=["Year", "QM"], how="left")
        .merge(recBoat, on=["Sim", "Year", "Month", "QM"], how="left")
    )

    # save output
    outputFile = os.path.dirname(fn) + "/sim.csv"
    output.to_csv(outputFile, sep=",", index=False)

    endTimeObj = datetime.now()

    # print time output
    print("sim time: " + str((endTimeObj - startTimeObj).total_seconds()))
