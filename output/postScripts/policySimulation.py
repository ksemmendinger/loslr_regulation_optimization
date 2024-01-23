# -----------------------------------------------------------------------------
# script info
# -----------------------------------------------------------------------------

# adapted from the GLRRM_Ontario example for modifying regulation plan parameters

# FROM GLRRM:
# Simulations with programmatically modified parameters are piloted by the
# ParamExpSimulation class. The ParamExpSimulation class behaves the same way as
# the Simulation class. For users, the only differences is that we pass the
# modified parameters directly to the ParamExpSimulation class, rather than the
# class reading them from a configuration file. The modified parameters are passed
# to the ParamExpSimulation class in a standard Python dictionary with the format:
#     modified_params = {'FunctionWithParam' : {'param_to_modify' : param_value}}
# The regulation plan functions with modifiable parameters can be found in the
# regulation plan's strategy module. For example, for Plan 2014:
#     ../GLRRM/glrrm/ontario/plan2014/strategies/

# -----------------------------------------------------------------------------
# import libraries
# -----------------------------------------------------------------------------

import os
import sys
import toml
import pandas as pd
from pathlib import Path

# set variables from command line input
args = sys.argv
# args = [
#     "",
#     "mac_ext",
#     "RC_Bv7_offSepRule_percentDiff_12month_sqAR_14dv_7obj_historic_25000nfe",
# ]

# [1]: location to run [mac_loc, glhpc]
loc = args[1]
if loc == "mac_loc":
    wd = "/Users/kylasemmendinger/Documents/CIGLR/Research/dps/output"
elif loc == "mac_ext":
    wd = "/Volumes/ky_backup/dps/output"
elif loc == "glhpc":
    wd = "/home/kylasr/optimization/output"
os.chdir(wd)

# [2]: folder name of experiment
expName = args[2]

# import logging
glrrmDir = "/Users/kylasemmendinger/Documents/github/GLRRM-Ontario"
sys.path.append(glrrmDir)

from glrrm.util import logger
from glrrm.util.config_utils import read_config, SimulationInfo
from glrrm.handler import databank as db
from glrrm.handler import databank_io as dbio
from glrrm.ontario.simulate import ParamExpSimulation

# -----------------------------------------------------------------------------
# reading the ontario.ini config file for glrrm
# -----------------------------------------------------------------------------

# this simulation will be piloted with information from the ontario.ini file
# we'll start by reading the configuration file and storing the information in
# a SimulationInfo object

# path to the ontario.ini config file
cfg_file = os.path.join(glrrmDir, "glrrm", "config", "ontario", "ontario.ini")

# read and parse the config file
cfgparser = read_config(cfg_file)
sim_info = SimulationInfo.from_configparser(cfgparser)

# -----------------------------------------------------------------------------
# reading the experiment config file from optimization run
# -----------------------------------------------------------------------------

# read in experiment config file
with open("data/" + expName + "/config.toml", "r") as f:
    config = toml.load(f)

# extract decision variable names
dvs = config["decisionVariables"]["dvName"]

# -----------------------------------------------------------------------------
# loading policy information
# -----------------------------------------------------------------------------

# read in file with candidate policies
pols = pd.read_csv("data/" + expName + "/satisficingPolicies.csv")

# Lake St. Lawrence at Long Sault Dame prescribed minimum levels for us to test
pols = pols.loc[:, ["ID"] + dvs]
npol = pols.shape[0]

# next, we will define the regulation solution we want to use for the simulation
solution = "Bv7"

# here we specify the start and end dates for the simulation
start = "1900-01-01"
end = "2020-12-31"

# -----------------------------------------------------------------------------
# loslr simulation
# -----------------------------------------------------------------------------

from datetime import datetime

for p in range(npol):
# for p in range(4, 5):
    startTimeObj = datetime.now()

    pID = pols.loc[p, "ID"]
    print(pID)

    # parameters to change in the regulation model
    # params = {
    #     "strategies": {},
    #     "parameters": {
    #         "OfficialWetDry": {
    #             "dry": pols.loc[p, "lfDryThreshold"],
    #             "wet": pols.loc[p, "lfWetThreshold"],
    #         },
    #         "OfficialConfidence": {
    #             "top": pols.loc[p, "lf50Conf"] + pols.loc[p, "lf99Conf"],
    #             "bot": pols.loc[p, "lf50Conf"],
    #         },
    #         "OfficialNTSTrendCnst": {
    #             "c1": pols.loc[p, "C1"] * 10,
    #             "c1_wet_hconf": (pols.loc[p, "C1"] + pols.loc[p, "addC1"]) * 10,
    #         },
    #         "OfficialWetSupplyCurve": {
    #             "p1": pols.loc[p, "P1"],
    #         },
    #         "OfficialDrySupplyCurve": {
    #             "c2": pols.loc[p, "C2"] * 10,
    #             "p2": pols.loc[p, "P2"],
    #         },
    #         "OfficialNTSStats": {
    #             "_ANN_NTS_MAX": pols.loc[p, "rcThreshold"]
    #             + pols.loc[p, "wetDenominator"],
    #             "_ANN_NTS_AVG": pols.loc[p, "rcThreshold"],
    #             "_ANN_NTS_MIN": pols.loc[p, "rcThreshold"]
    #             - pols.loc[p, "dryDenominator"],
    #         },
    #         "OfficialReduceRC": {
    #             "ont_mlv": pols.loc[p, "adjLevel"],
    #             "flw_reduce": pols.loc[p, "adjFlow"] * 10,
    #         },
    #     },
    # }

    params = {
        "strategies": {
            "RuleCurve": {
                "wet_curve_strategy": "POSEWetSupplyCurve",
                "dry_curve_strategy": "POSEDrySupplyCurve",
            }
        },
        "parameters": {
            # turn OFF september rule
            "Bounds": {"start": 0, "end": 0},
            "WetDryforIndConf": {
                "dry": pols.loc[p, "lfDryThreshold"],
                "wet": pols.loc[p, "lfWetThreshold"],
            },
            "ConfidenceBounds": {
                "top": pols.loc[p, "lf50Conf"] + pols.loc[p, "lf99Conf"],
                "bot": pols.loc[p, "lf50Conf"],
            },
            "NTSTrendConstantC1": {
                "c1": pols.loc[p, "C1"] * 10,
                "c1_wet_hconf": (pols.loc[p, "C1"] + pols.loc[p, "addC1"]) * 10,
            },
            "POSEWetSupplyCurve": {
                "p1": pols.loc[p, "P1"],
            },
            "POSEDrySupplyCurve": {
                "c2": pols.loc[p, "C2"] * 10,
                "p2": pols.loc[p, "P2"],
            },
            "NTSStatistics": {
                "_ANN_NTS_MAX": pols.loc[
                    p, "wetDenominator"
                ],  # CALL POSE SINCE DENOMINATOR
                "_ANN_NTS_AVG": pols.loc[p, "rcThreshold"],
                "_ANN_NTS_MIN": pols.loc[
                    p, "dryDenominator"
                ],  # CALL POSE SINCE DENOMINATOR
            },
            "ReduceRuleCurve": {
                "ont_mlv": pols.loc[p, "adjLevel"],
                "flw_reduce": pols.loc[p, "adjFlow"] * -1,
            },
        },
    }

    # before we instantiate the simulation object we will create an empty vault to
    # store the simulation results
    vault = db.DataVault()

    loslr_sim = ParamExpSimulation(
        parameters=params,
        vault=vault,
        tstart=start,
        tend=end,
        sim_info=sim_info,
        solution_template=solution,
        serial_num=f"exp_rc_pol_{p}",
    )

    # next we can run the simulation with the `route_for_full_period` method
    loslr_sim.route_for_full_period()

    # once the solution is finished, we can retrieve our vault
    vault = loslr_sim.vault_out()

    # we can also retrieve the output time series metadata
    meta = loslr_sim.dataMeta

    # next we will read the output options from the configuration file

    # path to output
    output_path = Path("data/" + expName + "/simulation/historic")

    # read output options from ont_sim_info to get file and data formatting
    formt = sim_info.get("output_options", "file_format", obj_type="str")
    options = sim_info.get(formt + "_options")

    # next we create directory path for experiment
    # if this folder doesn't already exist, GLRRM will create one for us
    soln_outpath = output_path / ("id" + str(pID))

    # the Simulation object allows us to write the output time series meta data to
    # a file for reference
    # loslr_sim.write_metadata_file(soln_outpath, csv=True)

    # # save additional experiment information (OPTIONAL)
    # info = {"experiment": {"details": "Bv7 with rc params."}}
    # loslr_sim.write_exp_info(soln_outpath / "experiment_info.json")

    # and finally, we can write the simulation results to file(s)
    dbio.write_vault(
        vault=vault,
        out_path=soln_outpath,
        file_format=formt,
        key_list=meta.keys(),
        first=loslr_sim.start,
        last=loslr_sim.end,
        **options,
    )

    endTimeObj = datetime.now()

    # print time output
    print("sim time: " + str((endTimeObj - startTimeObj).total_seconds()))
