# import libraries
import os
import numpy as np
import pandas as pd
from pathlib import Path

# set working directory
wd = "/Users/kylasemmendinger/Box/Plan_2014/optimization/output"
os.chdir(wd)

# set file names and whether or not to mutate a policy column
filelist = pd.DataFrame(
    {
        "varname": [
            "annualObjs",
            "hydroStats",
            "h1",
            "h2",
            "h3",
            "h4",
            "h6",
            "h7",
            "h14",
            "impactZones",
            "dynamicRob",
            "dynamicNorm",
            "staticRob",
            "staticNorm",
            "factorRank",
            "exoHydro",
        ],
        "dirname": [
            "annualObjectives/annualValues.txt",
            "hydroStatistics/hydroStatistics.txt",
            "hCriteria/h1.txt",
            "hCriteria/h2.txt",
            "hCriteria/h3.txt",
            "hCriteria/h4.txt",
            "hCriteria/h6.txt",
            "hCriteria/h7.txt",
            "hCriteria/h14.txt",
            "impactZones/impactZoneExceedances.txt",
            "scenarioDiscovery/dynamicRobustness.txt",
            "scenarioDiscovery/dynamicNormalized.txt",
            "scenarioDiscovery/staticRobustness.txt",
            "scenarioDiscovery/staticNormalized.txt",
            "scenarioDiscovery/dynamicFactorRanking.txt",
            "scenarioDiscovery/exogenousHydro.txt",
        ],
        "polCol": [
            0,
            0,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
        ],
    }
)

# -----------------------------------------------------------------------------
# read data (baseline and then runs)
# -----------------------------------------------------------------------------

# get run data
runInfo = [f.path for f in os.scandir("data/") if f.is_dir()]
runInfo = [x for x in runInfo if "baseline" not in x]

for i in range(filelist.shape[0]):

    print(filelist.loc[i, "varname"])

    fn = "data/baseline/postAnalysis/" + filelist.loc[i, "dirname"]
    tmp = pd.read_csv(fn, sep="\t")
    tmp["Policy"] = tmp["Policy"].str.replace("_", " ")
    tmp["Lead-Time"] = np.select(
        [tmp["Policy"] == "Plan 2014 Baseline"],
        ["12-month"],
        default=tmp["Policy"].str.split(" ").str[0],
    )
    tmp["Skill"] = np.select(
        [
            tmp["Policy"].str.contains("Plan 2014 Baseline"),
            tmp["Policy"].str.contains("Perfect"),
            tmp["Policy"].str.contains("(AR)"),
            tmp["Policy"].str.contains("(LM)"),
        ],
        ["Status Quo (AR)", "Perfect", "Status Quo (AR)", "Status Quo (LM)"],
        default="NaN",
    )

    cols = ["Policy", "Lead-Time", "Skill"]
    tmp = tmp[cols + [c for c in tmp.columns if c not in cols]]

    if filelist.loc[i, "polCol"] == 1:
        tmp = tmp.drop(columns=["Experiment", "ID"])

    # save baseline
    baseline = tmp

    output = []
    count = []

    for j in runInfo:

        print(j)
        fn = j + "/postAnalysis/" + filelist.loc[i, "dirname"]

        if Path(fn).is_file():

            tmp = pd.read_csv(fn, sep="\t")

            if j.split("/")[1].split("_")[1] == "0":
                skill = "Perfect"
            elif j.split("/")[1].split("_")[1] == "sqLM":
                skill = "Status Quo (LM)"
            elif j.split("/")[1].split("_")[1] == "sqAR":
                skill = "Status Quo (AR)"
            else:
                skill = j.split("/")[1].split("_")[1]

            tmp["Skill"] = skill
            tmp["Lead-Time"] = (
                j.split("/")[1].split("_")[0].split("month")[0] + "-month"
            )

            cols = ["Policy", "Lead-Time", "Skill"]
            tmp = tmp[cols + [c for c in tmp.columns if c not in cols]]

            if filelist.loc[i, "polCol"] == 1:
                tmp["Policy"] = (
                    "Seed"
                    + tmp["Policy"].astype(str)
                    + "_Policy"
                    + tmp["ID"].astype(str)
                )
                tmp = tmp.drop(columns=["Experiment", "ID"])

            output.append(tmp)

    data = pd.concat(output)
    data = pd.concat([baseline, data]).reset_index(drop=True)

    stringVars = data.select_dtypes("object").columns
    if len(stringVars) > 0:
        data.loc[:, stringVars] = data[stringVars].astype("category")

    floatVars = data.select_dtypes("float64").columns
    if len(floatVars) > 0:
        data.loc[:, floatVars] = pd.to_numeric(
            data[floatVars].stack(), downcast="float"
        ).unstack()

    intVars = data.select_dtypes("int").columns
    if len(intVars) > 0:
        data.loc[:, intVars] = pd.to_numeric(
            data[intVars].stack(), downcast="integer"
        ).unstack()

    # create folder if needed
    outputPath = "dashboard/data/" + filelist.loc[i, "dirname"].split("/")[0]
    if not os.path.exists(outputPath):
        os.makedirs(outputPath)

    fileName = "dashboard/data/" + filelist.loc[i, "dirname"].split(".")[0] + ".feather"
    # data.to_feather(fileName, version=1)
    data.to_feather(fileName)
