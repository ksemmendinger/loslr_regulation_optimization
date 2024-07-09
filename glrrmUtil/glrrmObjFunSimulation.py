# import libraries
import os
import sys
import pathlib
import numpy as np
import pandas as pd
from glob import glob
from datetime import datetime

# from pathlib import Path
# from os.path import exists

# -----------------------------------------------------------------------------
# script setup
# -----------------------------------------------------------------------------

# set variables from command line input
args = sys.argv
# args = ["", "/Users/kylasemmendinger/Library/CloudStorage/GoogleDrive-kylasr@umich.edu/My Drive/loslrRegulation", "baseline/Bv7"]

# [1]: path to working directory
os.chdir(args[1])

# [2]: folder name of experiment
folderName = args[2]

# import objective functions
sys.path.append(".")
import objectiveFunctions.objectiveFunctions as objectiveFunctions

# -----------------------------------------------------------------------------
# run GLRRM output through PI models
# -----------------------------------------------------------------------------

# get filelist
# path = "output/data/" + folderName + "/simulation/historic"
# filelist = [
#     f for f in glob(path + "/*/formattedOutput**", recursive=True) if os.path.isfile(f)
# ]
path = "output/data/" + folderName
filelist = [f for f in glob(path + "/**", recursive=True) if "sim.csv" in f]

for i in range(len(filelist)):
    startTimeObj = datetime.now()
    print(pathlib.PurePath(filelist[i]).parent.name)

    # load glrrm output
    fn = filelist[i]
    data = pd.read_csv(fn, sep=",")
    # data = data.iloc[:, 1:85]

    # format output
    # dataTS = data.drop(list(range(0, 48))).reset_index(drop=True)
    # dataTS = dataTS.drop(
    #     list(range(dataTS.shape[0] - 48, dataTS.shape[0]))
    # ).reset_index(drop=True)
    # dataTS = {x: dataTS[x].values for x in dataTS}
    dataTS = {x: data[x].values for x in data}

    (
        coastal,
        commNav,
        hydro,
        mMarsh,
        muskrat,
        recBoat,
    ) = objectiveFunctions.objectiveSimulation(dataTS, "simulation")

    output = (
        data.merge(coastal, on=["Sim", "Year", "Month", "QM"], how="left")
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
