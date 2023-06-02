# import libraries
import os
import sys
import pandas as pd
import dill as pickle
from time import time
from pathlib import Path
from functools import partial
from pathos.multiprocessing import ProcessPool as Pool

# -----------------------------------------------------------------------------
# functions
# -----------------------------------------------------------------------------

# call to parallelize simulation across traces from the same input category
def policySimulationParallel(
    leadtime, skill, v, folderName, inputV, traceFN, cfg_info, soln, sim_data, vault, vars
):

    import os
    import sys
    # import objective functions
    sys.path.insert(1, os.getcwd() + "/objectiveFunctions")
    import objectiveFunctions
    
    subFolder = traceFN.split("/")[-1]
    # print(subFolder)

    # simulate

    # use the GLRRM model to simulate output
    if leadtime != "12month":
        raise ValueError(
            "At this time, GLRRM only supports simulations with a 12-month lead long forecast."
        )
    if skill != "sqAR":
        raise ValueError(
            "At this time, GLRRM only supports simulations with AR skill."
        )
    data = glrrm_simulation(v, vars, cfg_info, soln, sim_data, vault)


    # format output
    dataTS = data.dropna().reset_index(drop=True)
    dataTS = {x: dataTS[x].values for x in dataTS}

    (
        coastal,
        commNav,
        hydro,
        mMarsh,
        recBoat,
    ) = objectiveFunctions.objectiveEvaluationSimulation(dataTS)

    output = (
        data.merge(coastal, on=["Sim", "Year", "Month", "QM"], how="left")
        .merge(commNav, on=["Sim", "Year", "Month", "QM"], how="left")
        .merge(hydro, on=["Sim", "Year", "Month", "QM"], how="left")
        .merge(mMarsh, on=["Year", "QM"], how="left")
        .merge(recBoat, on=["Sim", "Year", "Month", "QM"], how="left")
    )

    # create folder to save simulated output
    newpath = os.path.join(os.getcwd(), "output/data/" + folderName + "/simulation/" + inputV + "/" + subFolder)

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
        + vars['policyFN'],
        compression="gzip",
    )

def glrrm_simulation(version, vars, cfg_info, soln, sim_data, vault, **kwargs):
    """
    Function to pilot a GLRRM simulation using pareto policies.

    Parameters
    ----------
    version : str
        The type of simulation, either historic or stochastic
    vars : dict
        The modifiable parameters that compose the pareto policy
    cfg_info : dict
        The configuration information to instantiate the GLRRM simulation
    soln : str
        The version of Plan 2014 to use, either Bv7 or Plan2014BOC
    sim_data : dict
        The pre-processed simulation data for GLRRM
    vault : dict
        The pre-processed input data for GLRRM
    **kwargs : dict
        Additional keyword arguments for the simulation

    Returns
    -------
    wide_df : DataFrame
        The results of the pareto policy simulation, formatted in the same way
        as output from the plan2014_optim.simulation() function.

    """
    from glrrm.ontario.simulate import BoxMixSimulation
    from glrrm.util.quartermonth import QuarterMonth
    from glrrm.handler.databank import DataKind, DataLocation

    dvs = vars
    
    # set modifiable parameters
    params = {'OfficialNTSTrendCnst' : {'c1' : dvs['rcWetC']*10,
                                        'c1_wet_hconf' : dvs['rcWetConfC']*10},
            'OfficialDrySupplyCurve' : {'c2' : dvs['rcDryC']*10,
                                        'p2' : dvs['rcDryP']},
            'OfficialWetSupplyCurve' : {'p1' : dvs['rcWetP']},
            'OfficialNTSStats' : {'_ANN_NTS_AVG' : dvs['rcThreshold'],
                                  '_ANN_NTS_MAX' : dvs['rcWetAdjustment'],
                                  '_ANN_NTS_MIN' : dvs['rcDryAdjustment']},
            'OfficialReduceRC' : {'ont_mlv' : dvs['rcDryLevel'],
                                  'flw_reduce' : dvs['rcDryFlowAdj']},
            'OfficialWetDry' : {'wet' : dvs['lfWetThreshold'],
                                'dry' : dvs['lfDryThreshold']},
            'OfficialConfidence' : {'bot' : dvs['lf50Conf'],
                                    'top' : dvs['lf99Conf']}
    }

    # get the start and end date of the simulation from the pre-processed simulation data
    start = sim_data['start_date']
    end = sim_data['end_date']
    
    # instantiate the simulation with pre-processed input data and configuration variables 
    loslr_sim = BoxMixSimulation(
        parameters=params,
        sim_data=sim_data,
        vault=vault,
        tstart=start,
        tend=end,
        sim_info=cfg_info,
        solution_template=soln,
        inputs_from_cfg=False,
    )

    # run the simulation
    loslr_sim.route_for_full_period()

    # withdraw vault with simulation output
    vault = loslr_sim.vault_out()
    
    # withdraw all time series from the vault
    ds_list = []
    for key in vault.contents:
        ds = vault.withdraw(key=key, first=start, last=end)
        ds_list.append(ds)
    
    dfs = []
    for ds in ds_list:
        # rename the timeseries to match simulation_optimization_framework
        kind = ds.dataKind
        kind_pose = DataKind(kind).pose_handle            
        loc = ds.dataLocation
        if loc == 'na' or loc == 'stl' or kind == 'sym':
            col_name = kind_pose
        else:
            loc_pose = DataLocation(loc).pose_handle
            col_name = loc_pose + kind_pose
        if loc == 'intw' and kind == 'mlv':
            col_name = 'saunderstwLevel'
        if loc == 'ont' and kind == 'flw':
            suffix = ds.dataMeta['dataSuffix']
            if suffix == 'plan':
                col_name = 'ontFlow'
            else:
                col_name = loc_pose + suffix + kind_pose
        if loc == 'ont' and kind == 'mlv':
            col_name = loc_pose + 'mlv' + kind_pose
        if loc == 'ont' and kind == 'blv':
            col_name = loc_pose + 'blv' + kind_pose
        # collect all columns for dataframe
        df = ds.dataVals.to_frame(col_name) 
        dfs.append(df)
        
    wide_df = pd.concat([df for df in dfs], axis=1)
    # reset multi-index, then reset index again to create Sim column
    wide_df = wide_df.reset_index().reset_index(names='Sim')
    # simulation time steps are 1-indexed
    wide_df['Sim'] = wide_df['Sim'] + 1 
    # add month column
    ds = ds.dataVals.reset_index().astype(object)
    qm_temp = ds.apply(lambda x: QuarterMonth(year=x.year, qm48=x.qm48), axis=1)
    months = qm_temp.apply(lambda x: x.month)
    wide_df.insert(2, 'Month', months)
    # insert freshet indicator column
    wide_df['freshetIndicator'] = 1.0
    # insert kingston level column
    wide_df['kingstonLevel'] = wide_df['ontLevel'] - 0.03
    # rename columns for POSE format
    wide_df = wide_df.rename(columns={'year' : 'Year',
                                      'qm48' : 'QM',
                            }
                )
    wide_df = wide_df.loc[:,~wide_df.columns.duplicated()].copy()
    return wide_df

# -----------------------------------------------------------------------------
# Multiprocessing simulations
# -----------------------------------------------------------------------------

if __name__ == '__main__':
  
    # we need the following line if we're running in Spyder
    __spec__ = "ModuleSpec(name='builtins', loader=<class '_frozen_importlib.BuiltinImporter'>)"
    
    # set variables from command line input
    # args = sys.argv
    args = ["", "glslro", "historic", "off", "12month", "sqAR", "100000", "14", "4"]
    # args = ["", "mac_loc", "stochastic", "on", "12month", "sqLM", "50000", "14", "4"]
    # args = ["", "mac_loc", "historic", "off", "baseline", "4"]

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
        wd = "/Users/kylasemmendinger/Box/Plan_2014/optimization"
    elif args[1] == "hopper":
        wd = "/home/fs02/pmr82_0001/kts48/optimization"
    elif args[1] == 'glslro':
        wd = "C:\\Users\\GervasiN\\Documents\\simulation_optimization_framework"
        glrrm_path = "C:\\Users\\GervasiN\\Documents\\GLRRM-Ontario"
        cfg_pth = os.path.join(glrrm_path, "glrrm\\config\\ontario\\ontario.ini")
    os.chdir(wd)

    # names of objectives
    pis = [
        "Coastal Impacts: Upstream Buildings Impacted (#)",
        "Coastal Impacts: Downstream Buildings Impacted (#)",
        "Commercial Navigation: Ontario + Seaway + Montreal Transportation Costs ($)",
        "Hydropower: Moses-Saunders + Niagara Energy Value ($)",
        "Meadow Marsh: Area (ha)",
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
        "Long Forecast Wet Threshold",
        "Long Forecast Dry Threshold",
        "Rule Curve Low Level Flow Adjustment",
        "Long Forecast 50% Confidence Interval",
        "Long Forecast 99% Confidence Interval",
    ]

    # -----------------------------------------------------------------------------
    # simulate pareto policies
    # -----------------------------------------------------------------------------

    # load in policies that make up the pareto front
    pareto_path = os.path.join(os.getcwd(), "output/data/" + folderName + "/NonDominatedPolicies_test.txt")
    pop = pd.read_csv(pareto_path, sep="\t")

    # create folder to save simulated output
    newpath = os.path.join(os.getcwd(), "output/data/" + folderName + "/simulation/" + inputV)
    if not os.path.exists(newpath):
        os.makedirs(newpath)

    preproc_path = os.path.join(os.getcwd(), "output/postScripts")
    sys.path.insert(1, preproc_path)
    from preprocGLRRM import get_solution

    trace = Path("input/" + inputV + '/' + leadtime + "_" + skill)

    # read in the vault (from preprocGLRRM)
    vaultPath = Path(trace / 'vault.pkl')
    with open(vaultPath, 'rb') as pickle_jar:
        vault = pickle.load(pickle_jar)

    # read in the sim_data dictionary (from preprocGLRRM)
    simdataPath = Path(trace / 'sim_data.pkl')
    with open(simdataPath, 'rb') as small_pickle_jar:
        sim_data = pickle.load(small_pickle_jar)

    # get the solution (eg. Bv7, Plan2014H14, etc) and sim data formatted into a dict
    soln, _, cfg_info = get_solution(cfg_pth)    

    vars_list = []
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
        vars["lf50Conf"] = pop.loc[i, "Long Forecast 50% Confidence Interval"]
        vars["lf99Conf"] = pop.loc[i, "Long Forecast 99% Confidence Interval"]
        vars["lfWetThreshold"] = pop.loc[i, "Long Forecast Wet Threshold"]
        vars["lfDryThreshold"] = pop.loc[i, "Long Forecast Dry Threshold"]
        vars['policyFN'] = policyFN
        vars_list.append(vars)

    # get input dir list
    filelist = [f.path for f in os.scandir(os.path.join(os.getcwd(), "input/" + inputV)) if f.is_dir()]
    traceFN = filelist[0]

    partialSim = partial(
        policySimulationParallel,
        leadtime,
        skill,
        v,
        folderName,
        inputV,
        traceFN,
        cfg_info, 
        soln, 
        sim_data, 
        vault
    )
    
    ts = time()

    executor = Pool()
    executor.map(partialSim, vars_list)
    executor.close()
    executor.join()
    executor.clear()
    
    print('Process pool jobs took %s seconds', time() - ts)


 