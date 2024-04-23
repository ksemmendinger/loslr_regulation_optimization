# import libraries
import sys
import numpy as np
import pandas as pd
from datetime import datetime

# import os
# os.chdir(
#     "/Users/kylasemmendinger/Library/CloudStorage/GoogleDrive-kylasr@umich.edu/My Drive/loslrRegulation"
# )

sys.path.append(".")
from functions.utils import minmaxNorm, round_d

# -----------------------------------------------------------------------------
# simulation and objective evaluation
# -----------------------------------------------------------------------------


# takes in supplies and calculates releases/levels
def simulation(
    data,
    releaseFunInputs,
    getReleaseFunctionInputs,
    releaseFunction,
    septemberRule,
    getPlanLimitsInputs,
    planLimits,
    getStLawrenceRoutingInputs,
    stLawrenceRouting,
    pars,
):
    # set number of timesteps
    timesteps = data.shape[0]

    # -----------------------------------------------------------------------------
    # input data formatting
    # -----------------------------------------------------------------------------

    # create columns for release function outputs
    data["rfOutput"] = np.nan
    data["pprFlow"] = np.nan
    data["rfFlow"] = np.nan
    data["rfRegime"] = str(np.nan)

    # create columns for Lake Ontario water levels and flows
    data["ontLevelBOQ"] = np.nan
    data["ontLevelEOQ"] = np.nan
    data["ontLevel"] = np.nan  # used for st. law and objective function calculations
    data["ontFlow"] = np.nan
    data["flowRegime"] = str(np.nan)

    # create columns for St. Lawrence water levels and flows
    data["stlouisFlow"] = np.nan
    data["kingstonLevel"] = np.nan
    data["alexbayLevel"] = np.nan
    data["brockvilleLevel"] = np.nan
    data["ogdensburgLevel"] = np.nan
    data["cardinalLevel"] = np.nan
    data["iroquoishwLevel"] = np.nan
    data["iroquoistwLevel"] = np.nan
    data["morrisburgLevel"] = np.nan
    data["longsaultLevel"] = np.nan
    data["saundershwLevel"] = np.nan
    data["saunderstwLevel"] = np.nan
    data["cornwallLevel"] = np.nan
    data["summerstownLevel"] = np.nan
    data["lerybeauharnoisLevel"] = np.nan
    data["ptclaireLevel"] = np.nan
    data["jetty1Level"] = np.nan
    data["stlambertLevel"] = np.nan
    data["varennesLevel"] = np.nan
    data["sorelLevel"] = np.nan
    data["lacstpierreLevel"] = np.nan
    data["maskinongeLevel"] = np.nan
    data["troisrivieresLevel"] = np.nan
    data["batiscanLevel"] = np.nan

    # create columns for long forecast confidence and indicator
    data["confidence"] = np.nan
    data["indicator"] = np.nan

    # create column for freshet indicator, needed for commercial navigation PI model
    data["freshetIndicator"] = np.nan

    # initialize previous QM's flow, EOQ level, and ice status
    data.loc[48, "ontLevelBOQ"] = 74.55
    data.loc[47, "ontFlow"] = 595.0
    data.loc[47, "iceInd"] = 2.0

    # # initialize columns for slon and other ottsplit flow calculations
    # if str(slonValues) != "True":
    #     data["stlouisontOut"] = np.nan
    #     data["vaudreuilFlow"] = np.nan
    #     data["stanneFlow"] = np.nan
    #     data["dpmiFlow"] = np.nan

    # convert to dictionary for faster lookup
    data = {x: data[x].values for x in data}

    # -----------------------------------------------------------------------------
    # simulation
    # -----------------------------------------------------------------------------

    # 2970 cms-quarters is the conversion factor for converting flows to levels
    conv = 2970

    # set start iteration at 49 to allow for one year of spin up
    s = 48

    # get number of time steps
    # timesteps = len(data["forNTS"][~np.isnan(data["forNTS"])])

    for t in range(s, timesteps):
        # quarter month and year
        qm = data["QM"][t]
        year = data["Year"][t]

        # ontario water level
        ontLevelStart = data["ontLevelBOQ"][t]

        # true nts
        obsontNTS = data["ontNTS"][t]

        # forecasted NTS
        sfSupplyNTS = data["ontNTS_QM1"][t]

        # flow, level, and flag if september levels are dangerously high
        if septemberRule != "off":
            if qm <= 32:
                qm32Flow = np.nan
                qm32Level = np.nan

            elif qm > 32:
                qm32Flow = data["ontFlow"][data["Year"] == year][32 - 1]
                qm32Level = data["ontLevelBOQ"][data["Year"] == year][32 - 1]

        # -------------------------------------------------------------------------
        # format inputs and call release function
        # -------------------------------------------------------------------------

        x = getReleaseFunctionInputs(data, t, **releaseFunInputs)
        rfOutputs = releaseFunction(x, pars, **releaseFunInputs)

        ontFlow = rfOutputs["rfFlow"]
        ontRegime = rfOutputs["rfRegime"]
        pprFlow = rfOutputs["pprFlow"]
        rfOutput = rfOutputs["rfOutput"]

        # compute averaged quarter-monthly release using forecasted nts
        dif1 = round_d((sfSupplyNTS / 10 - ontFlow) / conv, 6)
        ontLevel = ontLevelStart + dif1

        # save release function outputs for reference later
        data["rfFlow"][t] = ontFlow
        data["rfRegime"][t] = ontRegime
        data["pprFlow"][t] = pprFlow
        data["rfOutput"][t] = rfOutput
        ontRegime = "RF"

        # ---------------------------------------------------------------------------
        #
        # R+ limit - dangerously high levels
        #
        # from qm 32 september check comments in ECCC fortran code: if sep 1 lake
        # levels are dangerously high (above 75.0), begin adjusting rule curve flow
        # to target 74.8 by beginning of qm 47 and sustain through qm 48. reassess
        # each qm and modify the adjustment
        #
        # ---------------------------------------------------------------------------

        # DOUBLE CHECK SEPTEMBER RULE WORKS AS EXPECTED
        if septemberRule != "off":
            ontFlow, ontRegime = septemberRule(
                qm,
                ontLevelStart,
                ontFlow,
                ontRegime,
                qm32Level,
                qm32Flow,
                conv=2970,
            )

            # calculate resulting water level if R+ applied
            if ontRegime != "RF":
                dif1 = round_d((sfSupplyNTS / 10 - ontFlow) / conv, 6)
                ontLevel = round_d(ontLevelStart + dif1, 6)

        # -----------------------------------------------------------------------------
        # limit check
        # -----------------------------------------------------------------------------

        x = getPlanLimitsInputs(data, t)
        limitsOutput = planLimits(qm, ontLevel, ontFlow, ontRegime, x, septemberRule)

        # write limit checked flow and regime
        ontFlow = limitsOutput["ontFlow"]
        ontRegime = limitsOutput["ontRegime"]

        # -------------------------------------------------------------------------
        # final lake ontario water level calulations based on observed NTS
        # -------------------------------------------------------------------------

        # final outflow and flow regime
        data["ontFlow"][t] = ontFlow
        data["flowRegime"][t] = ontRegime

        # calculate final ontario water level using observed nts
        dif2 = round_d(((obsontNTS / 10) - ontFlow) / conv, 6)
        ontLevelEOQ_unrounded = ontLevelStart + dif2

        # save this QM's UNROUNDED EOQ level as next QM's BOQ level
        if t < (timesteps - 1):
            data["ontLevelBOQ"][t + 1] = ontLevelEOQ_unrounded

        # round and save EOQ level
        data["ontLevelEOQ"][t] = round_d(ontLevelEOQ_unrounded, 2)

        # calculate MOQ level and round
        ontLevelMOQ = (ontLevelEOQ_unrounded + ontLevelStart) * 0.5
        data["ontLevelMOQ"][t] = round_d(ontLevelMOQ, 2)

        # use MEAN ontario level to calculate st. law levels and objective functions
        ontLevel = ontLevelMOQ
        data["ontLevel"][t] = ontLevel

        # -------------------------------------------------------------------------
        # st. lawrence levels and flows calculation
        # -------------------------------------------------------------------------

        # call routing subroutine
        x = getStLawrenceRoutingInputs(data, t)
        stLawLevels = stLawrenceRouting(ontLevel, ontFlow, x)

        # save timestep in dataframe
        data["stlouisFlow"][t] = stLawLevels["stlouisFlow"]
        data["kingstonLevel"][t] = stLawLevels["kingstonLevel"]
        data["alexbayLevel"][t] = stLawLevels["alexbayLevel"]
        data["brockvilleLevel"][t] = stLawLevels["brockvilleLevel"]
        data["ogdensburgLevel"][t] = stLawLevels["ogdensburgLevel"]
        data["cardinalLevel"][t] = stLawLevels["cardinalLevel"]
        data["iroquoishwLevel"][t] = stLawLevels["iroquoishwLevel"]
        data["iroquoistwLevel"][t] = stLawLevels["iroquoistwLevel"]
        data["morrisburgLevel"][t] = stLawLevels["morrisburgLevel"]
        data["longsaultLevel"][t] = stLawLevels["longsaultLevel"]
        data["saundershwLevel"][t] = stLawLevels["saundershwLevel"]
        data["saunderstwLevel"][t] = stLawLevels["saunderstwLevel"]
        data["cornwallLevel"][t] = stLawLevels["cornwallLevel"]
        data["summerstownLevel"][t] = stLawLevels["summerstownLevel"]
        data["lerybeauharnoisLevel"][t] = stLawLevels["lerybeauharnoisLevel"]
        data["ptclaireLevel"][t] = stLawLevels["ptclaireLevel"]
        data["jetty1Level"][t] = stLawLevels["jetty1Level"]
        data["stlambertLevel"][t] = stLawLevels["stlambertLevel"]
        data["varennesLevel"][t] = stLawLevels["varennesLevel"]
        data["sorelLevel"][t] = stLawLevels["sorelLevel"]
        data["lacstpierreLevel"][t] = stLawLevels["lacstpierreLevel"]
        data["maskinongeLevel"][t] = stLawLevels["maskinongeLevel"]
        data["troisrivieresLevel"][t] = stLawLevels["troisrivieresLevel"]
        data["batiscanLevel"][t] = stLawLevels["batiscanLevel"]

    # convert to dataframe
    data = pd.DataFrame(data)

    # -------------------------------------------------------------------------
    # freshet indicator calculator
    # -------------------------------------------------------------------------

    # SVM defines a freshet as a spring flow that starts 1.5 times bigger than the last QM flow at LSL
    # and stays a freshet until flows drop to 90% or less of the previous QM
    lsl = data.loc[:, ["Sim", "Year", "Month", "QM", "stlouisFlow"]]

    lsl["criteria1"] = lsl.loc[:, "stlouisFlow"].shift(1, fill_value=np.nan) * 1.5
    lsl["criteria2"] = lsl.loc[:, "stlouisFlow"].shift(1, fill_value=np.nan) * 0.9
    lsl["freshetIndicator"] = 0.0

    tmpLSL = lsl

    while tmpLSL.shape[0] > 0:
        # get next occurence of Lac St. Louis flow exceeding previous flow by 1.5 and set freshet indicator to 1
        ind1 = tmpLSL.loc[tmpLSL["stlouisFlow"] > tmpLSL["criteria1"], "Sim"].min()

        # added in break to account for if the freshet conditions are never met
        if np.isnan(ind1):
            break

        # find next occurence where Lac St. Louis flow falls below previous flow by 0.9
        ind2 = tmpLSL.loc[tmpLSL["stlouisFlow"] < tmpLSL["criteria2"], "Sim"].min()

        # assign freshet indicator to rows between [ind1, ind2)
        lsl.loc[((lsl["Sim"] >= ind1) & (lsl["Sim"] < ind2)), "freshetIndicator"] = 1.0

        # filter out remaining rows
        tmpLSL = tmpLSL.loc[tmpLSL["Sim"] > ind2]

    data["freshetIndicator"] = lsl["freshetIndicator"]

    return data


# calls simulation and objective functions to return aggregate PI measures
def optimization(
    formatDecisionVariables,
    decisionVariables,
    dataName,
    releaseFunInputs,
    getReleaseFunctionInputs,
    releaseFunction,
    septemberRule,
    getPlanLimitsInputs,
    planLimits,
    getStLawrenceRoutingInputs,
    stLawrenceRouting,
    objectiveFunctions,
    *vars
):
    # -----------------------------------------------------------------------------
    # format decision variables from Borg
    # -----------------------------------------------------------------------------

    # join dvs from Borg into list
    vars = list(vars)

    # if the dvs are normalized, backtransform for simulation
    if str(decisionVariables["normalized"]) == True:
        bounds = {k: decisionVariables[k] for k in ("lowerBounds", "upperBounds")}
        ranges = decisionVariables["normalizedRange"]
        # dvs = list(vars)
        for i in range(len(vars)):
            vars[i] = minmaxNorm(
                vars[i], [x[i] for x in bounds.values()], ranges, method="backtransform"
            )

    # format decision variables from Borg into dictionary
    pars = formatDecisionVariables(vars, **releaseFunInputs)

    # -----------------------------------------------------------------------------
    # regulation plan simulation
    # -----------------------------------------------------------------------------

    # load input time series to optimize over
    data = pd.read_table("input/" + dataName + ".txt")

    # filter out last year to account for incomplete perfect forecast years
    data = data.loc[data["Year"] < max(data.Year), :].reset_index(drop=True)

    startTimeSim = datetime.now()
    outSim = simulation(
        data,
        releaseFunInputs,
        getReleaseFunctionInputs,
        releaseFunction,
        septemberRule,
        getPlanLimitsInputs,
        planLimits,
        getStLawrenceRoutingInputs,
        stLawrenceRouting,
        pars
        # **pars
    )

    endTimeSim = datetime.now()

    # -----------------------------------------------------------------------------
    #
    # objective function simulation
    #
    # run objective functions for upstream coastal, downstream coastal, commercial
    # naviation, hydropower, meadow marsh, muskrat house density,and recreational
    # boating. returns annual average for each objective
    #
    # -----------------------------------------------------------------------------

    startTimeObj = datetime.now()

    # filter out first year of spinup data from time series
    data = outSim.loc[outSim["Year"] > min(data.Year), :].reset_index(drop=True)

    # convert data frame to dictionary for faster computation
    data = {x: data[x].values for x in data}

    # initialize output
    nobjs = 7
    objs = [0.0] * nobjs

    # run models
    (
        objs[0],
        objs[1],
        objs[2],
        objs[3],
        objs[4],
        objs[5],
        objs[6],
    ) = objectiveFunctions.objectiveSimulation(
        data,
        output="netAnnualAverage",
    )

    endTimeObj = datetime.now()

    # print time output
    print(
        "sim:",
        (endTimeSim - startTimeSim).total_seconds(),
        "- obj:",
        (endTimeObj - startTimeObj).total_seconds(),
    )

    # return objectives to borg
    return objs
