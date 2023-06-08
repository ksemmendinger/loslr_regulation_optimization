# import libraries
import os
import sys
import numpy as np
import pandas as pd
from glob import glob
from concurrent.futures import ProcessPoolExecutor

# set variables from command line input
args = sys.argv
# args = ["", "mac_loc", "12month", "sqAR", "50000", "17", "4"]
# args = ["", "mac_loc", "baseline"]

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
newpath = "data/" + folderName + "/postAnalysis/hCriteria"
if not os.path.exists(newpath):
    os.makedirs(newpath)

# -----------------------------------------------------------------------------
# function to read time series data and count h criteria
# -----------------------------------------------------------------------------

# load data (for parallel run)
def readData(fn):

    # read file and get relevant columns
    df = (
        pd.read_parquet(fn)
        .loc[
            :,
            [
                "Sim",
                "Year",
                "Month",
                "QM",
                "jetty1Level",
                "ptclaireLevel",
                "ontLevel",
                "flowRegime",
            ],
        ]
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

    # -----------------------------------------------------------------------------
    # h1 - montreal harbor low levels
    # -----------------------------------------------------------------------------

    # get h1 criteria
    H1 = pd.read_excel("postScripts/hCriteria.xlsx", sheet_name="H1", engine="openpyxl")
    H1 = (
        H1.loc[:, ["Threshold", "Threshold Exceedance"]]
        .sort_values(by="Threshold")
        .reset_index(drop=True)
    )

    # extract levels and add lower bound of 0
    levsH1 = [0.0] + list(H1.loc[:, "Threshold"].dropna())

    # bin the simulated water levels
    countH1 = (
        pd.cut(df["jetty1Level"], levsH1, right=True)
        .value_counts()
        .sort_index()
        .reset_index()
    )

    countH1.columns = ["Water Level Bin (m)", "Simulated Exceedances"]
    countH1["Plan 2014 Exceedances"] = H1["Threshold Exceedance"]
    countH1["Performance"] = np.select(
        [
            countH1["Simulated Exceedances"] <= countH1["Plan 2014 Exceedances"],
            countH1["Simulated Exceedances"] > countH1["Plan 2014 Exceedances"],
        ],
        ["Pass", "Fail"],
    )

    # -----------------------------------------------------------------------------
    # h2 - pt claire low levels
    # -----------------------------------------------------------------------------

    # get h1 criteria
    H2 = pd.read_excel("postScripts/hCriteria.xlsx", sheet_name="H2", engine="openpyxl")
    H2 = (
        H2.loc[:, ["Threshold", "Threshold Exceedance"]]
        .sort_values(by="Threshold")
        .reset_index(drop=True)
    )

    # extract levels and add lower bound of 0
    levsH2 = [0.0] + list(H2.loc[:, "Threshold"].dropna())

    # bin the simulated water levels
    countH2 = (
        pd.cut(df["ptclaireLevel"], levsH2, right=True)
        .value_counts()
        .sort_index()
        .reset_index()
    )

    countH2.columns = ["Water Level Bin (m)", "Simulated Exceedances"]
    countH2["Plan 2014 Exceedances"] = H2["Threshold Exceedance"]
    countH2["Performance"] = np.select(
        [
            countH2["Simulated Exceedances"] <= countH2["Plan 2014 Exceedances"],
            countH2["Simulated Exceedances"] > countH2["Plan 2014 Exceedances"],
        ],
        ["Pass", "Fail"],
    )

    # -----------------------------------------------------------------------------
    # h3 - pt claire high levels
    # -----------------------------------------------------------------------------

    # get h1 criteria
    H3 = pd.read_excel("postScripts/hCriteria.xlsx", sheet_name="H3", engine="openpyxl")
    H3 = (
        H3.loc[:, ["Threshold", "Threshold Exceedance"]]
        .sort_values(by="Threshold")
        .reset_index(drop=True)
    )

    # extract levels and add upper bound of inf
    levsH3 = list(H3.loc[:, "Threshold"].dropna()) + [np.inf]

    # bin the simulated water levels
    countH3 = (
        pd.cut(df["ptclaireLevel"], levsH3, right=True)
        .value_counts()
        .sort_index()
        .reset_index()
    )

    countH3.columns = ["Water Level Bin (m)", "Simulated Exceedances"]
    countH3["Plan 2014 Exceedances"] = H3["Threshold Exceedance"]
    countH3["Performance"] = np.select(
        [
            countH3["Simulated Exceedances"] <= countH3["Plan 2014 Exceedances"],
            countH3["Simulated Exceedances"] > countH3["Plan 2014 Exceedances"],
        ],
        ["Pass", "Fail"],
    )

    # -----------------------------------------------------------------------------
    # h4 - monthly mean high ontario levels
    # -----------------------------------------------------------------------------

    # get h4 criteria
    H4 = pd.read_excel("postScripts/hCriteria.xlsx", sheet_name="H4", engine="openpyxl")
    H4 = H4.loc[:, ["Month", "Threshold"]]

    # get monthly mean simulated water levels
    levsH4 = (
        df.loc[:, ["Year", "Month", "ontLevel"]]
        .groupby(["Year", "Month"])
        .agg("mean")
        .droplevel(0)
        .merge(H4, on="Month")
    )

    # compare to monthly thresholds
    levsH4["Performance"] = np.select(
        [
            levsH4["ontLevel"] <= levsH4["Threshold"],
            levsH4["ontLevel"] > levsH4["Threshold"],
        ],
        ["Pass", "Fail"],
    )

    # count occurences of passes/fails
    countH4 = (
        levsH4.groupby(["Month", "Performance"])["Performance"]
        .count()
        .unstack()
        .reset_index()
        .rename_axis(None, axis=1)
    )

    countH4.insert(1, "Threshold (m)", H4.Threshold)

    # -----------------------------------------------------------------------------
    # h6 - monthly mean freq of high ontario levels
    # -----------------------------------------------------------------------------

    # get h6 criteria
    H6 = pd.read_excel("postScripts/hCriteria.xlsx", sheet_name="H6", engine="openpyxl")
    H6 = H6.loc[:, ["Month", "Threshold"]]

    # get monthly mean simulated water levels
    levsH6 = (
        df.loc[:, ["Year", "Month", "ontLevel"]]
        .groupby(["Year", "Month"])
        .agg("mean")
        .droplevel(0)
        .merge(H6, on="Month")
    )

    # compare to monthly thresholds
    levsH6["Performance"] = np.select(
        [
            levsH6["ontLevel"] <= levsH6["Threshold"],
            levsH6["ontLevel"] > levsH6["Threshold"],
        ],
        ["Pass", "Fail"],
    )

    # count occurences of passes/fails
    countH6 = (
        levsH6.groupby(["Month", "Performance"])["Performance"]
        .count()
        .unstack()
        .reset_index()
        .rename_axis(None, axis=1)
    )

    countH6.insert(1, "Threshold (m)", H6.Threshold)

    # -----------------------------------------------------------------------------
    # h7 - monthly mean low ontario levels
    # -----------------------------------------------------------------------------

    # get h7 criteria
    H7 = pd.read_excel("postScripts/hCriteria.xlsx", sheet_name="H7", engine="openpyxl")
    H7 = H7.loc[:, ["Month", "Threshold"]]

    # get monthly mean simulated water levels
    levsH7 = (
        df.loc[:, ["Year", "Month", "ontLevel"]]
        .groupby(["Year", "Month"])
        .agg("mean")
        .droplevel(0)
        .merge(H7, on="Month")
    )

    # compare to monthly thresholds
    levsH7["Performance"] = np.select(
        [
            levsH7["ontLevel"] >= levsH7["Threshold"],
            levsH7["ontLevel"] < levsH7["Threshold"],
        ],
        ["Pass", "Fail"],
    )

    # count occurences of passes/fails
    countH7 = (
        levsH7.groupby(["Month", "Performance"])["Performance"]
        .count()
        .unstack()
        .reset_index()
        .rename_axis(None, axis=1)
        .replace(np.nan, 0)
        .astype(int)
    )

    countH7.insert(1, "Threshold (m)", H7.Threshold)

    # -----------------------------------------------------------------------------
    # h14 - quartermonthly highs and lows
    # -----------------------------------------------------------------------------

    # get h4 criteria
    H14 = pd.read_excel(
        "postScripts/hCriteria.xlsx", sheet_name="H14", engine="openpyxl"
    )
    H14 = H14.loc[:, ["QM", "highTrigger", "lowTrigger"]]

    # get monthly mean simulated water levels
    levsH14 = df.loc[:, ["QM", "ontLevel", "flowRegime"]].merge(H14, on="QM")

    # set conditions of exceedances
    conditions = [
        # 58DD rules applied and rules brought level within h14 criteria
        (
            (levsH14["flowRegime"].str.contains("58DD"))
            & (levsH14["ontLevel"] < levsH14["highTrigger"])
            & (levsH14["ontLevel"] > levsH14["lowTrigger"])
        ),
        # 58DD rules applied but levels were still above h14 criteria
        (
            (levsH14["flowRegime"].str.contains("58DD"))
            & (levsH14["ontLevel"] >= levsH14["highTrigger"])
        ),
        # 58DD rules applied but levels were still below h14 criteria
        (
            (levsH14["flowRegime"].str.contains("58DD"))
            & (levsH14["ontLevel"] <= levsH14["lowTrigger"])
        ),
        # plan 2014 levels within h14 criteria
        (
            (~levsH14["flowRegime"].str.contains("58DD"))
            & (levsH14["ontLevel"] < levsH14["highTrigger"])
            & (levsH14["ontLevel"] > levsH14["lowTrigger"])
        ),
        # plan 2014 levels above h14 criteria
        (
            (~levsH14["flowRegime"].str.contains("58DD"))
            & (levsH14["ontLevel"] >= levsH14["highTrigger"])
        ),
        # plan 2014 levels below h14 criteria
        (
            (~levsH14["flowRegime"].str.contains("58DD"))
            & (levsH14["ontLevel"] <= levsH14["lowTrigger"])
        ),
    ]

    # set identifying values
    choices = [
        "58DD Applied - Okay",
        "58DD Applied - Still High",
        "58DD Applied - Still Low",
        "2014 Applied - Okay",
        "2014 Applied - High",
        "2014 Applied - Low",
    ]

    # find exceedances
    levsH14["Performance"] = np.select(conditions, choices, default="na")

    # count occurences of passes/fails
    countH14 = (
        levsH14.groupby(["QM", "Performance"])["Performance"]
        .count()
        .unstack()
        .reset_index()
        .rename_axis(None, axis=1)
        .replace(np.nan, 0)
        .astype(int)
    )

    countH14.insert(1, "Low Threshold (m)", H14.lowTrigger)
    countH14.insert(1, "High Threshold (m)", H14.highTrigger)

    countH1.insert(0, "Policy", fn.split("/")[-1].split(".parquet.gzip")[0])
    countH1.insert(0, "SOW", sow)
    countH2.insert(0, "Policy", fn.split("/")[-1].split(".parquet.gzip")[0])
    countH2.insert(0, "SOW", sow)
    countH3.insert(0, "Policy", fn.split("/")[-1].split(".parquet.gzip")[0])
    countH3.insert(0, "SOW", sow)
    countH4.insert(0, "Policy", fn.split("/")[-1].split(".parquet.gzip")[0])
    countH4.insert(0, "SOW", sow)
    countH6.insert(0, "Policy", fn.split("/")[-1].split(".parquet.gzip")[0])
    countH6.insert(0, "SOW", sow)
    countH7.insert(0, "Policy", fn.split("/")[-1].split(".parquet.gzip")[0])
    countH7.insert(0, "SOW", sow)
    countH14.insert(0, "Policy", fn.split("/")[-1].split(".parquet.gzip")[0])
    countH14.insert(0, "SOW", sow)

    return countH1, countH2, countH3, countH4, countH6, countH7, countH14


# -----------------------------------------------------------------------------
#  read BoC time series data and get annual averages
# -----------------------------------------------------------------------------

path = "data/" + folderName + "/simulation/historic/BoC/**"
filelist = [f for f in glob(path, recursive=True) if os.path.isfile(f)]

totalH1 = []
totalH2 = []
totalH3 = []
totalH4 = []
totalH6 = []
totalH7 = []
totalH14 = []

with ProcessPoolExecutor(max_workers=nWorkers) as executor:
    for tmpH1, tmpH2, tmpH3, tmpH4, tmpH6, tmpH7, tmpH14 in executor.map(
        readData, filelist
    ):
        totalH1.append(tmpH1)
        totalH2.append(tmpH2)
        totalH3.append(tmpH3)
        totalH4.append(tmpH4)
        totalH6.append(tmpH6)
        totalH7.append(tmpH7)
        totalH14.append(tmpH14)

# append all results
h1 = pd.concat(totalH1)
h2 = pd.concat(totalH2)
h3 = pd.concat(totalH3)
h4 = pd.concat(totalH4)
h6 = pd.concat(totalH6)
h7 = pd.concat(totalH7)
h14 = pd.concat(totalH14)

#     idCols = ["Experiment", "Lead-Time", "Skill", "ID", "Policy"]
#     countH1[idCols] = pop.loc[i, idCols].to_list()
#     countH1 = countH1[idCols + (countH1.columns.drop(idCols).tolist())]
#     countH2[idCols] = pop.loc[i, idCols].to_list()
#     countH2 = countH2[idCols + (countH2.columns.drop(idCols).tolist())]
#     countH3[idCols] = pop.loc[i, idCols].to_list()
#     countH3 = countH3[idCols + (countH3.columns.drop(idCols).tolist())]
#     countH4[idCols] = pop.loc[i, idCols].to_list()
#     countH4 = countH4[idCols + (countH4.columns.drop(idCols).tolist())]
#     countH6[idCols] = pop.loc[i, idCols].to_list()
#     countH6 = countH6[idCols + (countH6.columns.drop(idCols).tolist())]
#     countH7[idCols] = pop.loc[i, idCols].to_list()
#     countH7 = countH7[idCols + (countH7.columns.drop(idCols).tolist())]
#     countH14[idCols] = pop.loc[i, idCols].to_list()
#     countH14 = countH14[idCols + (countH14.columns.drop(idCols).tolist())]

h1.to_csv(
    "data/" + folderName + "/postAnalysis/hCriteria/h1.txt", sep="\t", index=False
)
h2.to_csv(
    "data/" + folderName + "/postAnalysis/hCriteria/h2.txt", sep="\t", index=False
)
h3.to_csv(
    "data/" + folderName + "/postAnalysis/hCriteria/h3.txt", sep="\t", index=False
)
h4.to_csv(
    "data/" + folderName + "/postAnalysis/hCriteria/h4.txt", sep="\t", index=False
)
h6.to_csv(
    "data/" + folderName + "/postAnalysis/hCriteria/h6.txt", sep="\t", index=False
)
h7.to_csv(
    "data/" + folderName + "/postAnalysis/hCriteria/h7.txt", sep="\t", index=False
)
h14.to_csv(
    "data/" + folderName + "/postAnalysis/hCriteria/h14.txt", sep="\t", index=False
)
