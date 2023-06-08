# import libraries
import os
import sys
import numpy as np
import pandas as pd
from glob import glob
from concurrent.futures import ProcessPoolExecutor

# set variables from command line input
args = sys.argv
# args = ["", "mac_loc", "12month", "sqAR", "50000", "17", 4]
# args = ["", "mac_loc", "baseline", 4]

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
newpath = "data/" + folderName + "/postAnalysis/annualStatistics"
if not os.path.exists(newpath):
    os.makedirs(newpath)

# -----------------------------------------------------------------------------
# function to read time series data and get annual averages
# -----------------------------------------------------------------------------

# load data (for parallel run)
def readData(fn):

    # state SOW for grouping
    sup = fn.split("/")[3]
    if sup == "stochastic":
        sow = "Stochastic Century " + fn.split("/")[4].split("_")[1]
    elif sup == "historic":
        tmp = fn.split("/")[4]
        sow = tmp[0].upper() + tmp[1:]
    elif sup == "climate_scenarios":
        sow = fn.split("/")[4]

    # read file and get relevant columns
    df = pd.read_parquet(fn).loc[
        :,
        [
            "Sim",
            "Year",
            "Month",
            "QM",
            "ontLevel",
            "ptclaireLevel",
            # "ontFlow",
            "flowRegime",
        ],
    ]

    # get monthly min, mean,
    annStats = (
        df.loc[:, ["Sim", "Year", "ontLevel", "ptclaireLevel"]]
        .melt(
            id_vars=["Sim", "Year"],
            var_name="Variable",
            value_name="Value",
        )
        .groupby(["Year", "Variable"], as_index=False)
        .agg(
            annualMin=("Value", "min"),
            annualMean=("Value", "mean"),
            annualMax=("Value", "max"),
        )
        .melt(
            id_vars=["Year", "Variable"],
            var_name="statType",
            value_name="Value",
        )
    )

    annStats.insert(0, "Policy", fn.split("/")[-1].split(".parquet.gzip")[0])
    annStats.insert(0, "SOW", sow)

    annRules = (
        df.loc[:, ["Sim", "Year", "flowRegime"]]
        .groupby(["Year", "flowRegime"], as_index=False)
        .agg("count")
    )

    annRules.insert(0, "Policy", fn.split("/")[-1].split(".parquet.gzip")[0])
    annRules.insert(0, "SOW", sow)

    return annStats, annRules


# -----------------------------------------------------------------------------
# read time series data and get annual averages
# -----------------------------------------------------------------------------

# load data from specified run
path = "data/" + folderName + "/simulation/**"
filelist = [f for f in glob(path, recursive=True) if os.path.isfile(f)]

hydroStats = []
rules = []

with ProcessPoolExecutor(max_workers=nWorkers) as executor:
    for tmpHydro, tmpRules in executor.map(readData, filelist):
        hydroStats.append(tmpHydro)
        rules.append(tmpRules)

hydroStats = pd.concat(hydroStats)

hydroStats.to_csv(
    "data/" + folderName + "/postAnalysis/annualStatistics/annualStatistics.txt",
    sep="\t",
    index=False,
)

rules = pd.concat(rules)

rules.to_csv(
    "data/" + folderName + "/postAnalysis/annualStatistics/regimeCounts.txt",
    sep="\t",
    index=False,
)
