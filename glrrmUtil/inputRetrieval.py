# -----------------------------------------------------------------------------
# get input data from the Plan-2014-Python directory and compile
# -----------------------------------------------------------------------------

# import libraries
import sys
import pandas as pd

args = sys.argv
# args = ["", "1961_2020", "sqAR", "12month"]

expName = args[1]
skill = args[2]
lt = args[3]

# output file name
inDir = (
    "/Users/kylasemmendinger/Documents/github/Plan-2014-Python/simulation_model/input/"
    + expName
)

outDir = (
    "/Users/kylasemmendinger/Library/CloudStorage/GoogleDrive-kylasr@umich.edu/My Drive/loslrRegulation/input/historic/"
    + expName
)

# supply data, indicators, and roughness coefficients
hydro = pd.read_table(inDir + "/hydro/historic.txt")

# load short term forecast predictions (status quo)
sf = pd.read_table(inDir + "/short_forecast/sq/historic.txt")

# load long term forecast predictions of interest
lf = pd.read_table(
    inDir
    + "/long_forecast/"
    + lt
    + "/"
    + skill
    + "/"
    + "historic"
    + "/skill_"
    + str(skill)
    + "_S1.txt"
)

spinup = pd.read_table(inDir + "/spin_up/historic.txt")

# join input data, short forecast, and long forecast data
data = (
    hydro.merge(sf, how="outer", on=["Sim", "Year", "Month", "QM"])
    .merge(lf, how="outer", on=["Sim", "Year", "Month", "QM"])
    .merge(spinup, how="outer", on=["Sim", "Year", "Month", "QM"])
)

# save output
data.to_csv(outDir + "/" + lt + "_" + skill + ".txt", sep="\t", index=False)
