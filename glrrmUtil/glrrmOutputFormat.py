# import libraries
import os
import sys
import numpy as np
import pandas as pd
from glob import glob
import pathlib

# from os.path import exists

# -----------------------------------------------------------------------------
# experimental design from inputs
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

# [2]: folder name of baseline policy
expName = args[2]

# match up for GLRRM and optimization variable names
names = pd.read_csv("glrrmUtil/glrrmOutputMatchup.csv")

# -----------------------------------------------------------------------------
# format GLRRM output
# -----------------------------------------------------------------------------

# get filelist
path = "output/data/" + expName
filelist = [
    f for f in glob(path + "/simulation/**", recursive=True) if "glrrmOutput.csv" in f
]

for i in range(len(filelist)):
    # print(pathlib.PurePath(filelist[i]).parent.name)

    # load glrrm output
    fn = filelist[i]
    data = pd.read_csv(fn)

    # -----------------------------------------------------------------------------
    # format glrrm ouput
    # -----------------------------------------------------------------------------

    glrrmNames = names.loc[:, "glrrm"].to_list()

    data = data.loc[:, glrrmNames]
    data.columns = names.loc[:, "optim"].to_list()

    # -----------------------------------------------------------------------------
    # calculate additional pi model inputs not output from glrrm
    # -----------------------------------------------------------------------------

    # add simulation and month variables
    data.insert(0, "Sim", range(1, data.shape[0] + 1))
    data.insert(
        2,
        "Month",
        [x for xs in [[x] * 4 for x in list(range(1, 13))] for x in xs]
        * len(data.Year.unique()),
    )

    # format ontFlow to 10*cms
    data["ontFlow"] = data["ontFlow"] / 10
    data["rfFlow"] = data["rfFlow"] / 10

    # caluclate lac st louis flow from ontario release and slon flow
    data["stlouisFlow"] = data["ontFlow"] + (data["stlouisontOut"] / 10)

    # calculate freshet indicator based on Lac St. Louis flows
    # SVM defines a freshet as a spring flow that starts 1.5 times bigger than the last QM flow at LSL
    # and stays a freshet until flows drop to 90% or less of the previous QM
    lsl = data.loc[:, ["Sim", "Year", "Month", "QM", "stlouisFlow"]]
    lsl["criteria1"] = lsl.loc[:, "stlouisFlow"].shift(1, fill_value=np.nan) * 1.5
    lsl["criteria2"] = lsl.loc[:, "stlouisFlow"].shift(1, fill_value=np.nan) * 0.9
    lsl["freshetIndicator"] = 0.0

    tmpLSL = lsl

    while tmpLSL.shape[0] > 0:
        # get first occurence of Lac St. Louis flow exceeding previous flow by 1.5 and set freshet indicator to 1
        ind1 = tmpLSL.loc[tmpLSL["stlouisFlow"] > tmpLSL["criteria1"], "Sim"].min()

        # find next occurence where Lac St. Louis flow falls below previous flow by 0.9
        ind2 = tmpLSL.loc[tmpLSL["stlouisFlow"] < tmpLSL["criteria2"], "Sim"].min()

        # assign freshet indicator to rows between [ind1, ind2)
        lsl.loc[(lsl["Sim"] >= ind1) & (lsl["Sim"] < ind2), "freshetIndicator"] = 1.0

        # filter out remaining rows
        tmpLSL = tmpLSL.loc[tmpLSL["Sim"] > ind2]

    data["freshetIndicator"] = lsl["freshetIndicator"]

    # switch ice status [1 --> 2 and vice versa]
    for t in range(data.shape[0]):
        if data.loc[t, "iceInd"] == 1:
            data.loc[t, "iceInd"] = 2
        elif data.loc[t, "iceInd"] == 2:
            data.loc[t, "iceInd"] = 1

    # caluclate mean kingston water level (from ontario mean water level)
    data["kingstonLevel"] = data["ontLevelMOQ"] - 0.03

    # SAVE ONTLEVEL AS QM MEAN
    data["ontLevel"] = data["ontLevelMOQ"]

    # -----------------------------------------------------------------------------
    # save output
    # -----------------------------------------------------------------------------

    # save output
    outputFile = os.path.dirname(fn) + "/glrrmOutputFormatted.csv"
    data.to_csv(outputFile, sep=",", index=False)
