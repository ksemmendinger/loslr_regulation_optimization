# import libraries
import os
import sys
import numpy as np
import pandas as pd
from glob import glob
from functools import partial
from concurrent.futures import ProcessPoolExecutor

# set variables from command line input
args = sys.argv
# args = ["", "mac_loc", "12month", "sqAR", "50000", "14", "4"]
# args = ["", "mac_loc", "baseline", "4"]

# set working directory
if args[1] == "mac_loc":
    wd = "/Users/kylasemmendinger/Box/Plan_2014/optimization/output"
elif args[1] == "hopper":
    wd = "/home/fs02/pmr82_0001/kts48/optimization/output"
os.chdir(wd)

if args[2] == "baseline":

    # folder name
    folderName = "baseline"

    # set number of workers
    nWorkers = int(args[3])

else:

    # forecast lead-time
    leadtime = args[2]

    # forecast skill
    skill = args[3]

    # number of function evaluations
    nfe = int(args[4])

    # number of decision variables
    nvars = int(args[5])

    # folder name
    folderName = (
        leadtime + "_" + str(skill) + "_" + str(nfe) + "nfe_" + str(nvars) + "dvs"
    )

    # set number of workers
    nWorkers = int(args[6])

# create folder for clean decision variable and objective files
newpath = "data/" + folderName + "/postAnalysis/impactZones"
if not os.path.exists(newpath):
    os.makedirs(newpath)

# load impact zone data
impactZones = pd.read_csv("postScripts/impactZones.csv")
impactZones = impactZones[~impactZones["Category"].str.contains("Context")]

# get unique locations
impactLocations = list(impactZones["Impact Location"].unique())
gageLocations = list(impactZones["Water Level Location"].unique())

# -----------------------------------------------------------------------------
# function to read time series data and get annual averages
# -----------------------------------------------------------------------------

# load data (for parallel run)
def readData(gageLocations, impactLocations, impactZones, fn):

    # read file and get relevant columns
    df = (
        pd.read_parquet(fn)
        .loc[:, ["Sim", "Year", "Month", "QM"] + gageLocations]
        .dropna()
    )

    # state SOW for grouping
    sup = fn.split("/")[3]
    if sup == "stochastic":
        sow = "Stochastic Century " + fn.split("/")[4].split("_")[1]
    elif sup == "historic":
        sow = "Historic"
    elif sup == "climate_scenarios":
        sow = fn.split("/")[4]

    tmpDf = []

    # check # of QM-ly exceedances for each impact location
    for i in impactLocations:

        # get location specific impacts
        tmpImpacts = impactZones.loc[impactZones["Impact Location"] == i].reset_index(
            drop=True
        )
        tmpGage = list(tmpImpacts["Water Level Location"].unique())

        # get time series of water levels
        tmp = df.loc[:, ["Sim", "Year", "Month", "QM"] + tmpGage]

        # get level thresholds
        levs = tmpImpacts.loc[:, "Thresholds (m)"].sort_values().reset_index(drop=True)
        lev1 = float(levs[0])
        lev2 = float(levs[1])
        lev3 = float(levs[2])
        lev4 = float(levs[3])
        lev5 = float(levs[4])

        tmp["impactZone"] = np.select(
            [
                (tmp[tmpGage] < lev1),
                ((tmp[tmpGage] >= lev1) & (tmp[tmpGage] < lev2)),
                ((tmp[tmpGage] >= lev2) & (tmp[tmpGage] < lev3)),
                ((tmp[tmpGage] >= lev3) & (tmp[tmpGage] < lev4)),
                ((tmp[tmpGage] >= lev4) & (tmp[tmpGage] < lev5)),
                (tmp[tmpGage] >= lev5),
            ],
            [
                "Low Concern",
                "Low Concern",
                "Moderate",
                "Major",
                "Severe",
                "Extreme",
            ],
            default="Unknown",
        )

        countTMP = pd.DataFrame(tmp.groupby("impactZone").size()).reset_index()
        countTMP.columns = ["impactZone", "exceedancesQM"]
        countTMP["exceedancesFreq"] = round(
            (countTMP["exceedancesQM"] / tmp.shape[0]) * 100, 2
        )
        countTMP = countTMP.loc[:, ["impactZone", "exceedancesFreq"]]
        countTMP = (
            countTMP.pivot_table(columns="impactZone")
            .reset_index(drop=True)
            .rename_axis(None, axis=1)
        )

        countTMP.insert(0, "impactZone", i)
        tmpDf.append(countTMP)

    tmpDf = pd.concat(tmpDf)
    tmpDf.insert(0, "Policy", fn.split("/")[-1].split(".parquet.gzip")[0])
    tmpDf.insert(0, "SOW", sow)

    return tmpDf


# -----------------------------------------------------------------------------
# read time series data and get annual averages
# -----------------------------------------------------------------------------

path = "data/" + folderName + "/simulation/**"
filelist = [f for f in glob(path, recursive=True) if os.path.isfile(f)]

data = []

partialReadData = partial(readData, gageLocations, impactLocations, impactZones)

with ProcessPoolExecutor(max_workers=nWorkers) as executor:
    for tmpData in executor.map(partialReadData, filelist):
        data.append(tmpData)

finalImpacts = pd.concat(data)

finalImpacts.to_csv(
    "data/" + folderName + "/postAnalysis/impactZones/impactZoneExceedances.txt",
    sep="\t",
    index=False,
)
