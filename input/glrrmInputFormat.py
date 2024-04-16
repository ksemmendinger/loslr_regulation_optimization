# -----------------------------------------------------------------------------
# get input data from the GLRRM directory and format for input to optimization
# -----------------------------------------------------------------------------

# import libraries
import pandas as pd
from functools import reduce

folder = "1961_2020"

# file directory with glrrm inputs
glrrmDir = (
    "/Users/kylasemmendinger/Documents/github/GLRRM-Ontario/data/data_in/ontario/"
    + folder
)

# output file name
outputFile = (
    "/Users/kylasemmendinger/Documents/github/Plan-2014-Python/simulation_model/input/"
    + folder
    + "/hydro/historic.txt"
)

# match up for GLRRM and optimization variable names
names = pd.read_csv(
    "/Users/kylasemmendinger/Library/CloudStorage/GoogleDrive-kylasr@umich.edu/My Drive/loslrRegulation/input/glrrmInputMatchup.csv"
)
names = names.loc[names["glrrm"] != "ont_mlv_m_qm48_na", :].reset_index(drop=True)
# names = names.loc[names["glrrm"] != "stl_tde_m_qm48_na", :].reset_index(drop=True)
# names = names.loc[names["glrrm"] != "stmc_flw_cms_qm48_na", :].reset_index(drop=True)
# names = names.loc[names["glrrm"] != "triv_rgh_xx_qm48_na", :].reset_index(drop=True)
# names = names.loc[names["glrrm"] != "vare_rgh_xx_qm48_na", :].reset_index(drop=True)
# names = names.loc[names["glrrm"] != "summ_rgh_xx_qm48_na", :].reset_index(drop=True)

# -----------------------------------------------------------------------------
# get input data from the GLRRM directory and format for input to optimization
# -----------------------------------------------------------------------------

data = []

for i in range(names.shape[0]):
    # get glrrm variable name
    glrrmName = names.loc[i, "glrrm"]

    # get optimization name
    optimName = names.loc[names["glrrm"] == glrrmName, "optim"].reset_index(drop=True)[
        0
    ]

    # load data
    tmp = pd.read_csv(glrrmDir + "/" + glrrmName + ".csv", skiprows=5)

    # set optimization name for variables
    tmp.columns = ["Year", "QM", optimName]

    # check for extra spinup file
    if names.loc[i, "spinup"] == 1:
        # load spinup
        spinup = pd.read_csv(glrrmDir + "/" + glrrmName + "_spinup.csv", skiprows=5)
        spinup.columns = ["Year", "QM", optimName]

        tmp = pd.concat([spinup, tmp])

    # append to output dataframe
    data.append(tmp)

# join data frames on Year and QM
output = reduce(lambda x, y: x.merge(y, on=["Year", "QM"], how="outer"), data)
output = output.dropna(thresh=5, axis=0)

# add column for simulation time step and month
output.insert(0, "Sim", list(range(1, output.shape[0] + 1)))
output.insert(
    2,
    "Month",
    [x for xs in [[x] * 4 for x in list(range(1, 13))] for x in xs]
    * len(output.Year.unique()),
)
output.insert(7, "ontNTS", output["erieOut"] + output["ontNBS"])

# switch ice status [1 --> 2 and vice versa]
for i in range(output.shape[0]):
    if output.loc[i, "iceInd"] == 1:
        output.loc[i, "iceInd"] = 2
    elif output.loc[i, "iceInd"] == 2:
        output.loc[i, "iceInd"] = 1

# save output
output.to_csv(outputFile, sep="\t", index=False)
