# import libraries
import os
import sys
import pathlib
import numpy as np
import pandas as pd
from math import *
from borg import *
from datetime import datetime
from functools import partial

trace = "historic"
args = sys.argv
# args = ["", "mac_loc", "historic", "12month", "0", "5", "50000", "100", "100", "0.75", "12"]
# [1]: location to run [mac_loc, mac_ext, linux, hopper]
# [2]: version [historic, stochastic]
# [3]: forecast lead time [12month, 6month, 3month, 1month]
# [4]: forecast skill [sq, 0 - 1.0]
# [5]: seed [int]
# [6]: number of function evaluations [int]
# [7]: initial population size [int]
# [8]: frequency to report pareto front evolution and runtime dynamics
# [9]: % difference to vary decision variables [0 - 0.99]
# [10]: # of decision variables [int]

# set working directory
if args[1] == "mac_loc":
    wd = "/Users/kylasemmendinger/Box/Plan_2014/optimization"
elif args[1] == "hopper":
    wd = "/home/fs02/pmr82_0001/kts48/optimization"

os.chdir(wd)

import plan2014_optim

# -----------------------------------------------------------------------------
# set up parameters
# -----------------------------------------------------------------------------

# set variables from command line input
version = args[2]
leadtime = args[3]
skill = args[4]
nseed = int(args[5])
nfe = int(args[6])
popSize = int(args[7])
metFreq = int(args[8])
perDifDV = float(args[9])
nvars = int(args[10])

# set number of objectives and decision variables
nobjs = 6
nconstrs = 0

# decision variable starting values
dvs = [
    220.0,  # rcWetC
    260.0,  # rcWetConfC
    60.0,  # rcDryC
    0.9,  # rcWetP
    1.0,  # rcDryP
    7011.0,  # rcThreshold
    1541.0,  # rcWetAdjustment
    1294.0,  # rcDryAdjustment
    74.60,  # rcDryLevel
    20.0,  # rcDryFlowAdj
    7237.0,  # lfWetThreshold
    6859.0,  # lfDryThreshold
    50.0,  # lf50Conf
    189.0,  # lf99Conf
]

# dvs = dvs[:nvars]
# nvars = len(dvs)

# set experiment name
expName = leadtime + "_" + skill

# set experiment name and create output directory
folderName = leadtime + "_" + str(skill) + "_" + str(nfe) + "nfe_" + str(nvars) + "dvs"
path = pathlib.Path("output/data/" + folderName + "/raw/")
path.mkdir(parents=True, exist_ok=True)

# percent of original value to vary, can't be 100% because on lower side, you end up dividing by zero
perDif = perDifDV

# lower and upper bounds
lowerb = [x - perDif * x for x in dvs]
upperb = [x + perDif * x for x in dvs]

# -----------------------------------------------------------------------------
# run borg
# -----------------------------------------------------------------------------

# set seed
Configuration.seed(nseed)

dataName = version + "/" + trace + "/" + leadtime + "_" + skill

# initialize borg with problem --> partial(fn, data_name)(*vars)
borg = Borg(nvars, nobjs, 0, partial(plan2014_optim.optimization, dataName, version))

# set decision variable bounds
borg.setBounds(*[list(x) for x in list(zip(lowerb, upperb))])

# set objective tolerance epsilons
# up ci (#), down ci (#), comm nav ($) [0.1% of 4M], hydro ($) [1% of 40M], mm (ha), rb ($)
borg.setEpsilons(
    *[
        54423.005638655464 * (5 / 100),
        2908.2436974789916 * (5 / 100),
        193243206.05042017 * (0.5 / 100),
        2239512900.2167616 * (15 / 100),
        8768.159925000002 * (7.5 / 100),
        22373818.834033597 * (10 / 100),
    ]
)

# set up configuration
borgConfig = {
    "maxEvaluations": nfe,
    "initialPopulationSize": popSize,
    "runtimefile": "output/data/" + folderName + "/raw/runtime_S" + str(nseed) + ".txt",
    "runtimeformat": "borg",
    "frequency": metFreq,
}

# run borg
result = borg.solve(borgConfig)

# -----------------------------------------------------------------------------
# save output
# -----------------------------------------------------------------------------

# write objective values and decision variable values to output file
output_location = (
    "output/data/" + folderName + "/raw/pareto_front_S" + str(nseed) + ".txt"
)

with open(output_location, "w") as f:
    f.write("#Borg Optimization Results\n")
    f.write(
        "#First "
        + str(nvars)
        + " are the decision variables, "
        + "last "
        + str(nobjs)
        + " are the "
        + "objective values\n"
    )

    for solution in result:

        line = ""

        for i in range(len(solution.getVariables())):
            line = line + (str(solution.getVariables()[i])) + " "

        for i in range(len(solution.getObjectives())):
            line = line + (str(solution.getObjectives()[i])) + " "

        line = line + "\n"

        f.write(line)
