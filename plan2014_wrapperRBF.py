# import libraries
import os
import sys
import math
import pathlib
import numpy as np
import pandas as pd
from math import *
from borg import *
from datetime import datetime
from functools import partial

trace = "historic"
args = sys.argv
# args = ["", "mac_loc", "historic", "12month", "sqAR", "5", "50000", "100", "100", "0.75", "17"]
# args = ["", "mac_loc", "historic", "12month", "sqAR", "5", "50000", "100", "100"]
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
    wd = "/Users/kylasemmendinger/Library/CloudStorage/Box-Box/Plan_2014/optimization"
elif args[1] == "hopper":
    wd = "/home/fs02/pmr82_0001/kts48/optimization"

os.chdir(wd)

import plan2014_optimRBF

m = 3  # total number of inputs
mt = 1  # number of time inputs
nRBFs = m + 2  # from lit: rbfs should be m + 2

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
# perDifDV = float(args[9])
# nvars = int(args[10])

# set number of objectives and decision variables
nobjs = 7
nconstrs = 0

# vars = [
#     0.2, c11
#     1.1, b11
#     0.34, c12
#     0.7, b12
#     0.41, w1
#     0.34, c21
#     0.7, b21
#     0.2, c22
#     1.1, b22
#     0.59, w2
#     0.2, c31
#     1.1, b31
#     0.34, c32
#     0.7, b32
#     0.41, w3
#     0.34, c41
#     0.7, b41
#     0.2, c42
#     1.1, b42
#     0.59, w4
#     0.2, c51
#     1.1, b51
#     0.34, c52
#     0.7, b52
#     0.41,w5
#     (2 * math.pi) / 2, phi1
#     (2 * math.pi) / 3, phi2
# ]

# dvs = dvs[:nvars]
# nvars = len(dvs)

# lower and upper bounds
lowerb = ([-1, 0] * (m - mt) + [0]) * nRBFs + [0] * 2
upperb = ([1, 1] * (m - mt) + [1]) * nRBFs + [2 * math.pi] * 2

nvars = len(lowerb)

# set experiment name
expName = leadtime + "_" + skill

# set experiment name and create output directory
folderName = (
    "RBF_" + leadtime + "_" + str(skill) + "_" + str(nfe) + "nfe_" + str(nvars) + "dvs"
)
path = pathlib.Path("output/data/" + folderName + "/raw/")
path.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------------------------------
# run borg
# -----------------------------------------------------------------------------

# set seed
Configuration.seed(nseed)

dataName = version + "/" + trace + "/" + leadtime + "_" + skill

# initialize borg with problem --> partial(fn, data_name)(*vars)
borg = Borg(nvars, nobjs, 0, partial(plan2014_optimRBF.optimization, dataName, version))

# set decision variable bounds
borg.setBounds(*[list(x) for x in list(zip(lowerb, upperb))])

# set objective tolerance epsilons
# up ci (#), down ci (#), comm nav ($) [0.1% of 4M], hydro ($) [1% of 40M], mm (ha), rb ($)
borg.setEpsilons(
    *[
        61159.141361344526 * (5 / 100),
        2823.126050420168 * (5 / 100),
        193066983.99159664 * (0.5 / 100),
        2242916365.175907 * (10 / 100),
        9211.199907142856 * (7.5 / 100),
        0.15604516924270675 * (7.5 / 100),  # include new muskrat PI
        16712952.096386557 * (10 / 100),
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
