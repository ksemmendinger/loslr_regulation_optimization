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
# args = ["", "mac_loc", "12month", "sqAR", "50000", "17", "4"]
# args = ["", "mac_loc", "baseline", "4"]

# set working directory
if args[1] == "mac_loc":
    wd = "/Users/kylasemmendinger/Library/CloudStorage/Box-Box/Plan_2014/optimization/output"
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
newpath = "data/" + folderName + "/postAnalysis/seawayMetrics"
if not os.path.exists(newpath):
    os.makedirs(newpath)

# load seaway data
seawayDepths = pd.read_csv("postScripts/seawayMetrics.csv")

# get unique locations
impactLocations = list(seawayDepths["Location"].unique())
gageLocations = list(seawayDepths["gageLocation"].unique())

# -----------------------------------------------------------------------------
# function to read time series data and get annual averages
# -----------------------------------------------------------------------------

# load data (for parallel run)
def readData(gageLocations, seawayDepths, fn):

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
        tmp = fn.split("/")[4]
        sow = tmp[0].upper() + tmp[1:]
    elif sup == "climate_scenarios":
        sow = fn.split("/")[4]

    tmp = (
        df.melt(
            id_vars=["Sim", "Year", "Month", "QM"],
            var_name="gageLocation",
            value_name="Level",
        )
        .merge(seawayDepths, on="gageLocation", how="left")
        .melt(
            id_vars=["Sim", "Year", "Month", "QM", "gageLocation", "Location", "Level"],
            var_name="loadingDepth",
            value_name="criticalLevel",
        )
    )

    tmp["criticalDifference"] = tmp["Level"] - tmp["criticalLevel"]

    tmp = tmp.loc[
        tmp.groupby(["Sim", "Year", "Month", "QM", "loadingDepth"])[
            "criticalDifference"
        ].idxmin()
    ].reset_index()

    tmp["criticalFlag"] = 0
    tmp.loc[tmp["criticalDifference"] <= 0, "criticalFlag"] = 1

    tmp = tmp.loc[tmp["criticalFlag"] == 1, :].reset_index(drop=True)

    tmp.insert(0, "Policy", fn.split("/")[-1].split(".parquet.gzip")[0])
    tmp.insert(0, "SOW", sow)

    sumtbl = pd.DataFrame(
        {"Policy": fn.split("/")[-1].split(".parquet.gzip")[0], "SOW": sow}, index=[0]
    )

    sumtbl["criticalQMs"] = tmp["criticalFlag"].sum()
    sumtbl["totalDifference"] = abs(tmp["criticalDifference"]).sum()
    sumtbl["avgQMDifference"] = abs(tmp["criticalDifference"]).mean()
    sumtbl["minQMDifference"] = abs(tmp["criticalDifference"]).min()
    sumtbl["maxQMDifference"] = abs(tmp["criticalDifference"]).max()

    return tmp, sumtbl


# -----------------------------------------------------------------------------
#  read BoC time series data and get annual averages
# -----------------------------------------------------------------------------

path = "data/" + folderName + "/simulation/**"
filelist = [f for f in glob(path, recursive=True) if os.path.isfile(f)]

# array to store data
data = []
summary = []

partialReadData = partial(readData, gageLocations, seawayDepths)

with ProcessPoolExecutor(max_workers=nWorkers) as executor:
    for tmpData, tmpSummary in executor.map(partialReadData, filelist):
        data.append(tmpData)
        summary.append(tmpSummary)

finalImpacts = pd.concat(data)
finalImpacts.to_csv(
    "data/" + folderName + "/postAnalysis/seawayMetrics/seawayMetrics.txt",
    sep="\t",
    index=False,
)
finalSummary = pd.concat(summary)
finalSummary.to_csv(
    "data/" + folderName + "/postAnalysis/seawayMetrics/seawayMetricsSummary.txt",
    sep="\t",
    index=False,
)
