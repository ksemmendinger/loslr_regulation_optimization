# import libraries
import os
import sys
import toml
import numpy as np
import pandas as pd

# parameter file to test
parFile = "/Users/kylasemmendinger/Downloads/run_of_the_mill.toml_output_seed3.txt"
pars = []

with open(parFile) as f:
    for line in f.readlines():
        if line.startswith("("):
            vars = line.replace('(','').replace(')','')
            pars.append([float(x) for x in vars.split(",")])

pars.reverse()

# specify config and location
args = ["", "mac_ext", "run_of_the_mill.toml", "1"]

# -----------------------------------------------------------------------------
# set up experimental design from inputs
# -----------------------------------------------------------------------------

# [1]: location to run [mac_loc, glhpc]
loc = args[1]
if loc == "mac_loc":
    wd = "/Users/kylasemmendinger/Documents/CIGLR/Research/dps"
elif loc == "mac_ext":
    wd = "/Volumes/ky_backup/dps"
elif loc == "glhpc":
    wd = "/home/kylasr/optimization"
os.chdir(wd)

# [2]: path to configuration file
configFile = args[2]

# load configuration file from folder
with open(configFile, "r") as f:
    config = toml.load(f)

# set variables from config file
releaseFun = config["experimentalDesign"]["releaseFunction"]
limitType = config["experimentalDesign"]["limitType"]
septemberRule = config["experimentalDesign"]["septemberRule"]
leadtime = config["experimentalDesign"]["forecastLeadTime"]
skill = config["experimentalDesign"]["forecastSkill"]
nvars = config["experimentalDesign"]["numDV"]
nobjs = config["experimentalDesign"]["numObj"]
nconstrs = config["experimentalDesign"]["numCon"]
trace = config["experimentalDesign"]["trace"]
nfe = config["experimentalDesign"]["nfe"]
popSize = config["experimentalDesign"]["popSize"]
metFreq = config["experimentalDesign"]["metFreq"]
piWeighting = config["performanceIndicators"]["metricWeighting"]

# supply trace - set routing version to run with SLON or Ottawa River flows [historic, stochastic]
if trace == "stochastic":
    version = "stochastic"
else:
    version = "historic"

# -----------------------------------------------------------------------------
# file pointers
# -----------------------------------------------------------------------------

# input data to load
dataName = version + "/" + trace + "/" + leadtime + "_" + skill

# import policy simulation function
import optimizationSimulation

# initialize simulation with problem
try:
    for i in range(len(pars)):
        print(i)
        tmp = optimizationSimulation.optimization(
            dataName,
            version,
            limitType,
            septemberRule,
            releaseFun,
            config["decisionVariables"],
            piWeighting,
            *pars[i]
        )

except RuntimeWarning:
    print("failed for par combo:" + pars[i])




# # -----------------------------------------------------------------------------
# # write config file
# # -----------------------------------------------------------------------------

# # for first seed, copy config file to output directory
# if nseed == 1:
#     # config = {
#     #     "experimentalDesign": {
#     #         "releaseFunction": releaseFun,
#     #         "limitType": limitType,
#     #         "forecastLeadTime": leadtime,
#     #         "forecastSkill": skill,
#     #         "numDV": nvars,
#     #         "numObj": nobjs,
#     #         "numCon": nconstrs,
#     #         "trace": trace,
#     #         "nfe": nfe,
#     #         "popSize": popSize,
#     #         "metFreq": metFreq,
#     #     },
#     #     "decisionVariables": {
#     #         "dvName": [],
#     #         "lowerBounds": lowerb,
#     #         "upperBounds": upperb,
#     #     },
#     #     "performanceIndicators": {"piName": [], "epsilonValue": epsilon},
#     # }
#     with open("output/data/" + folderName + "/config.toml", "w") as f:
#         toml.dump(config, f)

# # -----------------------------------------------------------------------------
# # run borg
# # -----------------------------------------------------------------------------

# # run borg
# result = borg.solve(borgConfig)

# # -----------------------------------------------------------------------------
# # save output
# # -----------------------------------------------------------------------------

# output_location = (
#     "output/data/" + folderName + "/raw/pareto_front_S" + str(nseed) + ".txt"
# )

# # write objective values and decision variable values to output file
# with open(output_location, "w") as f:
#     f.write("# Borg Optimization Results\n")
#     f.write(
#         "# First "
#         + str(nvars)
#         + " are the decision variables, "
#         + "last "
#         + str(nobjs)
#         + " are the "
#         + "objective values\n"
#     )

#     for solution in result:
#         line = ""

#         for i in range(len(solution.getVariables())):
#             line = line + (str(solution.getVariables()[i])) + " "

#         for i in range(len(solution.getObjectives())):
#             line = line + (str(solution.getObjectives()[i])) + " "

#         line = line + "\n"

#         f.write(line)
