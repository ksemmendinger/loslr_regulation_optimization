# import libraries
import os
import sys

# import toml
import pathlib
import numpy as np
import pandas as pd
from glob import glob
from datetime import datetime

# from pathlib import Path
# from os.path import exists

# set variables from command line input
args = sys.argv
# args = ["", "mac_ext", "adjANN", "Bv7", "12month", "sqAR", "61", "7", "0", "historic", "30000", "5"]
# args = ["", "mac_ext", "RC_Bv7_offSepRule_12month_sqAR_14dv_7obj_historic_100000nfe"]
# args = ["", "mac_ext", "baseline"]

# -----------------------------------------------------------------------------
# experimental design from inputs
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

# [2]: folder name of experiment
folderName = args[2]

# import objective functions
sys.path.insert(1, os.getcwd() + "/objectiveFunctions")
import objectiveFunctions

# -----------------------------------------------------------------------------
# run GLRRM output through PI models
# -----------------------------------------------------------------------------

# get filelist
path = "output/data/" + folderName + "/simulation/historic"
filelist = [
    f for f in glob(path + "/*/formattedOutput**", recursive=True) if os.path.isfile(f)
]

for i in range(len(filelist)):
    startTimeObj = datetime.now()
    print(pathlib.PurePath(filelist[i]).parent.name)

    # load glrrm output
    fn = filelist[i]
    data = pd.read_csv(fn, sep="\t")

    # format output
    dataTS = data.dropna().reset_index(drop=True)
    dataTS = {x: dataTS[x].values for x in dataTS}

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
    outputFile = os.path.dirname(fn) + "/piOutput.csv"
    output.to_csv(outputFile, sep="\t", index=False)

    endTimeObj = datetime.now()

    # print time output
    print("sim time: " + str((endTimeObj - startTimeObj).total_seconds()))
