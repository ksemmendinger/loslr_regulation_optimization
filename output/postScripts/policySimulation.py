# import libraries
import os
import sys
import pandas as pd
from functools import partial
from concurrent.futures import ProcessPoolExecutor

# set variables from command line input
args = sys.argv
# args = ["", "mac_loc", "historic", "off", "12month", "sqAR", "75000", "17", "4"]
# args = ["", "mac_loc", "stochastic", "on", "baseline", "4"]

# operating system
loc = args[1]

# version to simulate
inputV = args[2]

# SLON calculation on/off
if args[3] == "on":
    v = "stochastic"
else:
    v = "historic"

if args[4] == "baseline":

    # folder name
    folderName = "baseline"
    nWorkers = int(args[5])

else:

    # forecast lead-time
    leadtime = args[4]

    # forecast skill
    skill = args[5]

    # number of function evaluations
    nfe = int(args[6])

    # number of decision variables
    nvars = int(args[7])

    # folder name
    folderName = (
        leadtime + "_" + str(skill) + "_" + str(nfe) + "nfe_" + str(nvars) + "dvs"
    )

    nWorkers = int(args[8])

# set working directory
if args[1] == "mac_loc":
    wd = "/Users/kylasemmendinger/Library/CloudStorage/Box-Box/Plan_2014/optimization"
elif args[1] == "hopper":
    wd = "/home/fs02/pmr82_0001/kts48/optimization/output"
os.chdir(wd)

# names of objectives
pis = [
    "Coastal Impacts: Upstream Buildings Impacted (#)",
    "Coastal Impacts: Downstream Buildings Impacted (#)",
    "Commercial Navigation: Ontario + Seaway + Montreal Transportation Costs ($)",
    "Hydropower: Moses-Saunders + Niagara Energy Value ($)",
    "Meadow Marsh: Area (ha)",
    "Muskrat House Density (%)",
    "Recreational Boating: Impact Costs ($)",
]

# names of decision variables
dvs = [
    "Rule Curve Wet Multiplier",
    "Rule Curve Confident Wet Multiplier",
    "Rule Curve Dry Multiplier",
    "Rule Curve Wet Power",
    "Rule Curve Dry Power",
    "Rule Curve Threshold",
    "Rule Curve Wet Adjustment",
    "Rule Curve Dry Adjustment",
    "Rule Curve Low Level Threshold",
    "Rule Curve Low Level Flow Adjustment",
    "Long Forecast Wet Threshold",
    "Long Forecast Dry Threshold",
    "Long Forecast 50% Confidence Interval",
    "Long Forecast 99% Confidence Interval",
    "R+ Threshold",
    "R+ Starting Quarter-Month",
    "R+ Ending Quarter-Month",
]

# -----------------------------------------------------------------------------
# functions
# -----------------------------------------------------------------------------

# import simulation function
sys.path.insert(1, os.getcwd())
import plan2014_optim

# import objective functions
sys.path.insert(1, os.getcwd() + "/objectiveFunctions")
import objectiveFunctions

# call to parallelize simulation across traces from the same input category
def policySimulationParallel(
    leadtime, skill, v, vars, folderName, inputV, policyFN, traceFN
):

    subFolder = traceFN.split("/")[-1]
    # print(subFolder)

    inputData = pd.read_csv(
        traceFN + "/" + leadtime + "_" + skill + ".txt",
        sep="\t",
    )

    # simulate
    data = plan2014_optim.simulation(inputData, v, **vars)

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
    ) = objectiveFunctions.objectiveEvaluationSimulation(dataTS)

    output = (
        data.merge(coastal, on=["Sim", "Year", "Month", "QM"], how="left")
        .merge(commNav, on=["Sim", "Year", "Month", "QM"], how="left")
        .merge(hydro, on=["Sim", "Year", "Month", "QM"], how="left")
        .merge(mMarsh, on=["Year", "QM"], how="left")
        .merge(muskrat, on=["Year", "QM"], how="left")
        .merge(recBoat, on=["Sim", "Year", "Month", "QM"], how="left")
    )

    # create folder to save simulated output
    newpath = "output/data/" + folderName + "/simulation/" + inputV + "/" + subFolder

    if not os.path.exists(newpath):
        os.makedirs(newpath)

    output.to_parquet(
        "output/data/"
        + folderName
        + "/simulation/"
        + inputV
        + "/"
        + subFolder
        + "/"
        + policyFN,
        compression="gzip",
    )


# -----------------------------------------------------------------------------
# simulate pareto policies
# -----------------------------------------------------------------------------

# load in policies that make up the pareto front
pop = pd.read_csv("output/data/" + folderName + "/NonDominatedPolicies.txt", sep="\t")

# create folder to save simulated output
newpath = "output/data/" + folderName + "/simulation/" + inputV
if not os.path.exists(newpath):
    os.makedirs(newpath)

# initialize process pool, do here to save overhead
with ProcessPoolExecutor(max_workers=nWorkers) as executor:

    for i in range(pop.shape[0]):
        # for i in range(2, pop.shape[0]):

        print(pop.loc[i, "Policy"])

        if folderName == "baseline":
            leadtime = pop.loc[i, "Lead-Time"].split("-")[0] + "month"
            skillPretty = pop.loc[i, "Skill"]
            if skillPretty == "Status Quo (AR)":
                skill = "sqAR"
            elif skillPretty == "Status Quo (LM)":
                skill = "sqLM"
            elif skillPretty == "Perfect":
                skill = "0"
            else:
                skill = skillPretty

            # set file output name
            policyFN = pop.loc[i, "Policy"].replace(" ", "_") + ".parquet.gzip"

        else:

            # set file output name
            policyFN = (
                "Seed"
                + str(pop.loc[i, "Policy"])
                + "_Policy"
                + str(pop.loc[i, "ID"])
                + ".parquet.gzip"
            )

        vars = {}
        vars["rcWetC"] = pop.loc[i, "Rule Curve Wet Multiplier"]
        vars["rcWetConfC"] = pop.loc[i, "Rule Curve Confident Wet Multiplier"]
        vars["rcDryC"] = pop.loc[i, "Rule Curve Dry Multiplier"]
        vars["rcWetP"] = pop.loc[i, "Rule Curve Wet Power"]
        vars["rcDryP"] = pop.loc[i, "Rule Curve Dry Power"]
        vars["rcThreshold"] = pop.loc[i, "Rule Curve Threshold"]
        vars["rcWetAdjustment"] = pop.loc[i, "Rule Curve Wet Adjustment"]
        vars["rcDryAdjustment"] = pop.loc[i, "Rule Curve Dry Adjustment"]
        vars["rcDryLevel"] = pop.loc[i, "Rule Curve Low Level Threshold"]
        vars["rcDryFlowAdj"] = pop.loc[i, "Rule Curve Low Level Flow Adjustment"]
        vars["lfWetThreshold"] = pop.loc[i, "Long Forecast Wet Threshold"]
        vars["lfDryThreshold"] = pop.loc[i, "Long Forecast Dry Threshold"]
        vars["lf50Conf"] = pop.loc[i, "Long Forecast 50% Confidence Interval"]
        vars["lf99Conf"] = pop.loc[i, "Long Forecast 99% Confidence Interval"]
        vars["limSepThreshold"] = pop.loc[i, "R+ Threshold"]
        vars["limSepThresholdQM1"] = pop.loc[i, "R+ Starting Quarter-Month"]
        vars["limSepThresholdQM2"] = pop.loc[i, "R+ Ending Quarter-Month"]

        # get input dir list
        filelist = [f.path for f in os.scandir("input/" + inputV) if f.is_dir()]

        partialSim = partial(
            policySimulationParallel,
            leadtime,
            skill,
            v,
            vars,
            folderName,
            inputV,
            policyFN,
        )

        for fn, _ in zip(filelist, executor.map(partialSim, filelist)):
            print(fn)