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
# args = ["", "mac_loc", "12month", "sqAR", "100", "17", "4"]
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
newpath = "data/" + folderName + "/postAnalysis/annualObjectives"
if not os.path.exists(newpath):
    os.makedirs(newpath)

allPIs = [
    "upstreamCoastal",
    "downstreamCoastal",
    "ontarioCoastal",
    "alexbayCoastal",
    "cardinalCoastal",
    "lerybeauharnoisCoastal",
    "ptclaireCoastal",
    "maskinongeCoastal",
    "lacstpierreCoastal",
    "sorelCoastal",
    "troisrivieresCoastal",
    "totalCommercialNavigation",
    "ontarioCommercialNavigation",
    "seawayCommercialNavigation",
    "montrealCommercialNavigation",
    "totalEnergyValue",
    "opgMosesSaundersEnergyValue",
    "nypaMosesSaundersEnergyValue",
    "opgNiagaraEnergyValue",
    "nypaNiagaraEnergyValue",
    "peakingMosesSaundersValue",
    "mmArea",
    "mmLowSupply",
    "muskratHouseDensity",
    "totalRecBoating",
    "ontarioRecBoating",
    "alexbayRecBoating",
    "ogdensburgRecBoating",
    "brockvilleRecBoating",
    "longsaultRecBoating",
    "ptclaireRecBoating",
    "varennesRecBoating",
    "sorelRecBoating",
]

qmPIs = [
    "upstreamCoastal",
    "downstreamCoastal",
    "ontarioCoastal",
    "alexbayCoastal",
    "cardinalCoastal",
    "lerybeauharnoisCoastal",
    "ptclaireCoastal",
    "maskinongeCoastal",
    "lacstpierreCoastal",
    "sorelCoastal",
    "troisrivieresCoastal",
    "totalCommercialNavigation",
    "ontarioCommercialNavigation",
    "seawayCommercialNavigation",
    "montrealCommercialNavigation",
    "totalEnergyValue",
    "opgMosesSaundersEnergyValue",
    "nypaMosesSaundersEnergyValue",
    "opgNiagaraEnergyValue",
    "nypaNiagaraEnergyValue",
    "peakingMosesSaundersValue",
    "totalRecBoating",
    "ontarioRecBoating",
    "alexbayRecBoating",
    "ogdensburgRecBoating",
    "brockvilleRecBoating",
    "longsaultRecBoating",
    "ptclaireRecBoating",
    "varennesRecBoating",
    "sorelRecBoating",
]

annualPIs = ["mmArea", "muskratHouseDensity"]


# -----------------------------------------------------------------------------
# function to read time series data and get annual averages
# -----------------------------------------------------------------------------

# load data (for parallel run)
def readData(allPIs, qmPIs, annualPIs, fn):

    # state SOW for grouping
    sup = fn.split("/")[3]
    if sup == "stochastic":
        sow = "Stochastic Century " + fn.split("/")[4].split("_")[1]
    elif sup == "historic":
        sow = "Historic"
    elif sup == "climate_scenarios":
        sow = fn.split("/")[4]

    # read file and get relevant columns
    df = pd.read_parquet(fn).loc[
        :,
        ["Sim", "Year", "Month", "QM"] + allPIs,
    ]

    # data analysis on qm-ly objective values
    qmObjs = (
        # drop na values
        df.loc[:, ["Year"] + qmPIs]
        .dropna(
            subset=qmPIs,
            how="all",
        )
        # get net annual values for QM-ly objectives
        .groupby("Year")[qmPIs]
        .sum()
        .reset_index()
        # calculate annual statistics
        .melt(id_vars="Year", value_name="Value", var_name="PI")
        .groupby("PI", as_index=False)
        .agg(
            annualAverage=("Value", "mean"),
            annualMinimum=("Value", "max"),
            annualMaximum=("Value", "min"),
            annualTotal=("Value", "sum"),
        )
        .melt(id_vars="PI", value_name="Value", var_name="statType")
    )

    # data analysis on annual objective values
    annObjs = (
        df.loc[:, ["Year", "mmLowSupply"] + annualPIs]
        .dropna(
            subset=annualPIs,
            how="all",
        )
        .reset_index(drop=True)
    )

    lowSup = (
        annObjs.loc[annObjs["mmLowSupply"] == 1, ["Year"] + annualPIs]
        .melt(id_vars="Year", value_name="Value", var_name="PI")
        .groupby("PI")
        .agg(
            annualAverage=("Value", "mean"),
            annualMinimum=("Value", "max"),
            annualMaximum=("Value", "min"),
            annualTotal=("Value", "sum"),
        )
        .reset_index()
        .rename_axis(0, axis=1)
        .melt(id_vars="PI", value_name="Value", var_name="statType")
    )

    allSup = (
        annObjs.loc[:, ["Year"] + annualPIs]
        .melt(id_vars="Year", value_name="Value", var_name="PI")
        .groupby("PI")
        .agg(
            annualAverage=("Value", "mean"),
            annualMinimum=("Value", "min"),
            annualMaximum=("Value", "max"),
            annualTotal=("Value", "sum"),
        )
        .reset_index()
        .rename_axis(0, axis=1)
        .melt(id_vars="PI", value_name="Value", var_name="statType")
    )

    # join all obj values and set identifiers
    objs = pd.concat([qmObjs, allSup, lowSup]).reset_index(drop=True)
    objs.insert(0, "Policy", fn.split("/")[-1].split(".parquet.gzip")[0])
    objs.insert(0, "SOW", sow)

    return objs


# -----------------------------------------------------------------------------
# read time series data and get annual averages
# -----------------------------------------------------------------------------

# load data from specified run
path = "data/" + folderName + "/simulation/**"
filelist = [f for f in glob(path, recursive=True) if os.path.isfile(f)]

objValues = []

partialReadData = partial(readData, allPIs, qmPIs, annualPIs)

with ProcessPoolExecutor(max_workers=nWorkers) as executor:
    for tmpObjs in executor.map(partialReadData, filelist):
        objValues.append(tmpObjs)

objValues = pd.concat(objValues)

objValues.to_csv(
    "data/" + folderName + "/postAnalysis/annualObjectives/annualValues.txt",
    sep="\t",
    index=False,
)
