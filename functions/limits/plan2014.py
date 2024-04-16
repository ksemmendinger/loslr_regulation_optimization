# import libraries
import os
import sys
import math
import numpy as np
import pandas as pd
from datetime import datetime

# os.chdir("/Volumes/ky_backup/dps")
# os.chdir("/Users/kylasemmendinger/Library/CloudStorage/GoogleDrive-kylasr@umich.edu/My Drive/loslrRegulation")

# import objective functions
sys.path.insert(1, os.getcwd() + "/objectiveFunctions")
import objectiveFunctions

# # for testing - BASELINE RUN
# with open("/Volumes/ky_backup/dps/output/data/baseline/Bv7/config.toml", "r") as f:
#     import toml
#     config = toml.load(f)
#     dvInfo = config["decisionVariables"]
#     plan = config["experimentalDesign"]["limitType"]
#     releaseFun = config["experimentalDesign"]["releaseFunction"]
#     septemberRule = config["experimentalDesign"]["septemberRule"]
#     v = config["experimentalDesign"]["trace"]
#     trace = config["experimentalDesign"]["trace"]
#     skill = config["experimentalDesign"]["forecastSkill"]
#     leadtime = config["experimentalDesign"]["forecastLeadTime"]
#     expName = v + "/" + v + "/" + leadtime + "_" + skill
#     vars = config["decisionVariables"]["normalizedValue"]

# # for testing - OPTIMIZATION RUN
# with open("/Volumes/ky_backup/dps/output/data/adjANN_Bv7_offSepRule_netAnnualAverage_6month_0_91dv_7obj_historic_75000nfe/config.toml", "r") as f:
#     import toml
#     config = toml.load(f)
#     dvInfo = config["decisionVariables"]
#     plan = config["experimentalDesign"]["limitType"]
#     releaseFun = config["experimentalDesign"]["releaseFunction"]
#     septemberRule = config["experimentalDesign"]["septemberRule"]
#     v = config["experimentalDesign"]["trace"]
#     trace = config["experimentalDesign"]["trace"]
#     skill = config["experimentalDesign"]["forecastSkill"]
#     leadtime = config["experimentalDesign"]["forecastLeadTime"]
#     expName = v + "/" + v + "/" + leadtime + "_" + skill
#     piWeighting = config["performanceIndicators"]['metricWeighting']

# vars = "2.880104203	1.291094971	3.266485085	-3.721932987	0.874296032	0.651930722	-2.249631469	-7.996912197	2.827316774	2.017274441	-3.015259944	-3.07775327	-6.141324873	-2.178844932	-6.223279324	-1.926483324	2.927152463	0.101363981	3.442968725	-7.450148917	-2.209088931	-9.958333269	1.391311458	2.940303959	-0.278451242	7.717047259	-1.865223949	1.357797455	-1.520520193	2.016449229	-1.081568434	-0.106897737	-4.080141777	-7.227909419	0.206446081	-1.873387591	2.743256082	1.303251539	1.661593974	-2.371070751	-4.896376177	-4.54390074	-10	6.224977212	-0.548525075	2.233226878	0.273731693	-6.947320044	-2.101355486	-1.487149417	0.488337413	-9.507909195	-5.028586079	3.006869362	1.060309077	2.769377812	1.162106343	-1.626363944	6.693639391	-4.777764875	1.661564112	-0.638409405	-0.693827615	4.483955594	4.368157782	-0.525721686	-3.630874389	-3.668167602	2.399273684	-5.427119656	-4.779052396	3.947073117	-1.165189061	1.202207693	0.751555564	3.654106135	2.014710267	0.157803388	-0.302524844	0.729097688	-2.308795361	4.186303643	3.583454298	-5.452775978	-0.499775745	-3.758594491	-1.979742319	-3.668765135	-1.137088734	-2.910951921	6.225834501"
# vars = "50.49641442	75.62000485	119.8317394	1.339067132	1.466265498	6926.179989	1635.782914	1329.809127	76.75910247	25.00506349	143.2502325	5.685663948	6454.576399	7300.620078"
# vars = vars.split("\t")
# vars = [float(x) for x in vars]
# vars = [1] * len(dvInfo["dvName"])

# -----------------------------------------------------------------------------
# simulation and objective evaluation
# -----------------------------------------------------------------------------


# only used for montreal routing if SLON is not available
def slonCalculation(ontFlow, carillonFlow, chateauguayFlow):
    # convert ontFlow to cms from 10*cms
    ontFlow10 = ontFlow * 10

    # ----------------------------------------
    # flows through sainte-anne
    # ----------------------------------------

    # constants
    c1 = 585.40
    c2 = 0.2733
    c3 = -0.05017
    c4 = -20.95
    c5 = -125.00
    c6 = 0.2986
    c7 = 0.02046
    c8 = -13.54

    # flow limits
    ontLim = 7800.0001
    cariLim = 300.0001

    # flow comparisons
    stanne1 = (
        c1 + (c2 * carillonFlow) + (c3 * ontFlow10) + (c4 * ontFlow10 / carillonFlow)
    )
    stanne2 = (
        c5 + (c6 * carillonFlow) + (c7 * ontFlow10) + (c8 * ontFlow10 / carillonFlow)
    )

    if ontFlow10 <= ontLim:
        if carillonFlow <= cariLim:
            stanneFlow = 0.0
        else:
            if stanne2 > 0.0:
                stanneFlow = stanne2
            else:
                stanneFlow = 0.0
    elif ontFlow10 > ontLim:
        if carillonFlow <= cariLim:
            stanneFlow = stanne1
        else:
            if stanne1 >= stanne2:
                stanneFlow = stanne2
            else:
                stanneFlow = stanne1

    # ----------------------------------------
    # flows through vaudreuil
    # ----------------------------------------

    # constants
    c1 = 787.40
    c2 = 0.3479
    c3 = -0.1336
    c4 = -0.9374
    c5 = -61.00
    c6 = 0.2975
    c7 = -0.0356
    c8 = 16.77
    c9 = 24.2
    c10 = 0.295
    c11 = -0.01885
    c12 = -0.0954

    # flow limits
    ontLim = 6600.0001
    cariLim1 = 300.0001
    cariLim2 = 900.0001
    diffOntCariLim = 7100.0001
    ratioOntCariLim = 35000.0001

    # flow comparisons
    vaud1 = c1 + (c2 * carillonFlow) + (c3 * ontFlow10) + (c4 * chateauguayFlow)
    vaud2 = (
        c5 + (c6 * carillonFlow) + (c7 * ontFlow10) + (c8 * ontFlow10 / carillonFlow)
    )
    vaud3 = (
        c9
        + (c10 * carillonFlow)
        + (c11 * ontFlow10)
        + c12 * (ontFlow10 - carillonFlow) * carillonFlow / ontFlow10
    )

    if ontFlow10 <= ontLim:
        if carillonFlow <= cariLim1:
            vaudreuilFlow = 0.0
        elif carillonFlow > cariLim1:
            if vaud3 < 0.0:
                vaudreuilFlow = 0.0
            elif vaud3 >= 0.0:
                if carillonFlow < cariLim2:
                    vaudreuilFlow = vaud3
                elif carillonFlow >= cariLim2:
                    if vaud2 > 0.0:
                        vaudreuilFlow = vaud2
                    else:
                        vaudreuilFlow = 0.0
    elif ontFlow10 > ontLim:
        if carillonFlow <= cariLim1:
            if vaud1 < 0.0:
                vaudreuilFlow = vaud1
            else:
                vaudreuilFlow = 0.0
        elif carillonFlow > cariLim1:
            diffOntCari = ontFlow10 - carillonFlow
            ratioOntCari = ontFlow10 / carillonFlow

            if (
                diffOntCari > diffOntCariLim
                and (diffOntCari * ratioOntCari) > ratioOntCariLim
            ):
                vaudreuilFlow = vaud1
            else:
                if carillonFlow < cariLim2:
                    if vaud1 >= vaud3:
                        vaudreuilFlow = vaud3
                    else:
                        vaudreuilFlow = vaud1
                else:
                    if vaud1 > vaud2:
                        vaudreuilFlow = vaud2
                    else:
                        vaudreuilFlow = vaud1

    # ----------------------------------------
    # flows through des prairies & mille iles
    # ----------------------------------------

    # constants
    c1 = 107.20
    c2 = 0.7418
    c3 = -0.6588
    dpmiFlow = c1 + (c2 * carillonFlow) + (c3 * vaudreuilFlow)

    # ----------------------------------------
    # flows through lac st. louis
    # ----------------------------------------

    # constants
    c1 = -877.40
    c2 = 1.1652
    c3 = 4.367
    c4 = 1.3956
    c5 = 0.8137
    c6 = 2751.0
    c7 = 0.7977
    c8 = 3.381
    c9 = 2.091
    ontLim = 9000.0001

    if ontFlow10 < ontLim:
        lacstlouisFlow = (
            c1
            + c2 * ontFlow10
            + c3 * chateauguayFlow
            + c4 * vaudreuilFlow
            + c5 * stanneFlow
        )
    else:
        lacstlouisFlow = (
            c6 + (c7 * ontFlow10) + (c8 * chateauguayFlow) + (c9 * vaudreuilFlow)
        )

    lacstlouisFlow = round(lacstlouisFlow, 0)

    # finally, get SLON flow (in cms)
    slonFlow = lacstlouisFlow - ontFlow10

    return {
        "stanneFlow": stanneFlow,
        "vaudreuilFlow": vaudreuilFlow,
        "dpmiFlow": dpmiFlow,
        "lacstlouisFlow": lacstlouisFlow,
        "slonFlow": slonFlow,
    }


def minmaxNorm(x, xRange, normRange, method="transform"):
    # get range bounds to normalize within - flexible to be [0, 1] or [-1, 1]
    a = min(normRange)
    b = max(normRange)

    if method == "transform":
        val = (b - a) * ((x - xRange[0]) / (xRange[1] - xRange[0])) + a

    elif method == "backtransform":
        val = (x - a) * ((xRange[1] - xRange[0]) / (b - a)) + xRange[0]

    else:
        val = np.nan

    return val


def annPolicy(x, pars):
    # ANN policy takes in input vector, x, and optimized weight/biases, pars

    # input layer to hidden layer (W * X + B)
    hiddenLayer1 = pars["inputLayer2hiddenLayer"].dot(x) + pars["hiddenLayerBias"]

    # # activation function on hidden layer output - sigmoid
    # hiddenLayer = 1 / (1 + np.exp(-hiddenLayer1))

    # activation function on hidden layer output - tanh
    hiddenLayer = 2 / (1 + np.exp(-2 * hiddenLayer1)) - 1

    # hidden layer to output layer (W * H + B)
    outputLayer = (
        pars["hiddenLayer2outputLayer"].dot(hiddenLayer) + pars["outputLayerBias"]
    )

    # # activation function on output layer - sigmoid
    # outputLayer = 1 / (1 + np.exp(-outputLayer))

    # activation function on output layer - tanh
    outputLayer = 2 / (1 + np.exp(-2 * outputLayer)) - 1

    # convert output array to list
    output = outputLayer.tolist()

    return output


# takes in supplies and calculates releases/levels
def simulation(data, version, plan, septemberRule, releaseFun, **pars):
    # -----------------------------------------------------------------------------
    # take in decision variables (i.e. parameters) and format
    # -----------------------------------------------------------------------------

    if releaseFun == "RC":
        lf50Conf = pars["lf50Conf"]
        lf99Conf = lf50Conf + pars["lf99Conf"]
        lfDryThreshold = pars["lfDryThreshold"]
        lfWetThreshold = pars["lfWetThreshold"]
        rcWetC = pars["C1"]
        rcWetConfC = rcWetC + pars["addC1"]
        rcDryC = pars["C2"]
        rcWetP = pars["P1"]
        rcDryP = pars["P2"]
        rcThreshold = pars["rcThreshold"]
        wetDenominator = pars["wetDenominator"]
        dryDenominator = pars["dryDenominator"]
        adjLevel = pars["adjLevel"]
        adjFlow = pars["adjFlow"]
    elif releaseFun == "RC2":
        # lf50Conf = pars["lf50Conf"]
        lf99Conf = pars["lf99Conf"]
        lfDryThreshold = pars["lfDryThreshold"]
        lfWetThreshold = pars["lfDryThreshold"] + pars["lfWetThreshold"]
        rcWetC = pars["C1"]
        rcWetConfC = pars["C1"] + pars["addC1"]
        rcDryC = pars["C2"]
        rcWetP = pars["P1"]
        rcDryP = pars["P2"]
        rcThreshold = pars["rcThreshold"]
        wetScaling = pars["wetScaling"] + pars["rcThreshold"]
        dryScaling = pars["rcThreshold"] - pars["dryScaling"]
        adjLevel = pars["adjLevel"]
        adjFlow = pars["adjFlow"]

    # -----------------------------------------------------------------------------
    # define H14 criteria - only for Plan 2014
    # -----------------------------------------------------------------------------

    if plan == "2014":
        # lake ontario 90% exceedence level using Planbv7_ml_10cm
        ontLowPctLevel = [
            74.28,
            74.28,
            74.28,
            74.27,
            74.27,
            74.27,
            74.26,
            74.27,
            74.29,
            74.31,
            74.35,
            74.41,
            74.48,
            74.54,
            74.60,
            74.64,
            74.67,
            74.70,
            74.72,
            74.74,
            74.75,
            74.76,
            74.76,
            74.76,
            74.76,
            74.75,
            74.74,
            74.72,
            74.70,
            74.68,
            74.65,
            74.62,
            74.59,
            74.57,
            74.54,
            74.50,
            74.47,
            74.44,
            74.42,
            74.39,
            74.36,
            74.35,
            74.34,
            74.32,
            74.32,
            74.31,
            74.30,
            74.28,
        ]

        # lake ontario high pct level Bv7DP 2% exceedence sto
        ontHighPctLevel = [
            75.03,
            75.07,
            75.10,
            75.13,
            75.14,
            75.14,
            75.13,
            75.14,
            75.16,
            75.18,
            75.22,
            75.27,
            75.33,
            75.40,
            75.45,
            75.50,
            75.53,
            75.56,
            75.60,
            75.62,
            75.63,
            75.62,
            75.60,
            75.59,
            75.57,
            75.54,
            75.50,
            75.47,
            75.43,
            75.39,
            75.34,
            75.30,
            75.26,
            75.20,
            75.15,
            75.10,
            75.06,
            75.01,
            74.97,
            74.95,
            74.94,
            74.92,
            74.91,
            74.92,
            74.93,
            74.93,
            74.95,
            75.00,
        ]

    # -----------------------------------------------------------------------------
    # data formatting
    # -----------------------------------------------------------------------------

    # format output by adding output columns and converting to dict for speed
    data["flowRegime"] = str(np.nan)
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
    data["freshetIndicator"] = np.nan
    data["confidence"] = np.nan
    data["indicator"] = np.nan
    data["rfFlow"] = np.nan
    data["annOutput"] = np.nan
    data["ontLevelBOQ"] = np.nan
    data["ontLevelEOQ"] = np.nan
    data["ontFlow"] = np.nan
    data["ontLevel"] = np.nan
    # data["ontLevelMOQ"] = np.nan

    # initialize previous QM's flow, EOQ level, and ice status
    data.loc[48, "ontLevelBOQ"] = 74.55
    data.loc[47, "ontFlow"] = 595
    data.loc[47, "iceInd"] = 2

    # initialize columns for slon and other ottsplit flow calculations
    if version == "stochastic":
        data["stlouisontOut"] = np.nan
        data["vaudreuilFlow"] = np.nan
        data["stanneFlow"] = np.nan
        data["dpmiFlow"] = np.nan

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
    timesteps = len(data["forNTS"][~np.isnan(data["forNTS"])])

    for t in range(s, timesteps):
        # quarter month and year
        qm = data["QM"][t]
        year = data["Year"][t]

        # -------------------------------------------------------------------------
        # starting state variables for time step, t
        # -------------------------------------------------------------------------

        # ontario water level
        ontLevelStart = data["ontLevelBOQ"][t]

        # kingston water level
        kingLevelStart = ontLevelStart - 0.03

        # average level of previous 48 quarter-months
        annavgLevel = round(np.mean(data["ontLevelMOQ"][(t - 48) : (t)]), 2)

        # moses-saunders release
        ontFlowPrev = data["ontFlow"][t - 1]

        # ice status
        iceIndPrev = data["iceInd"][t - 1]
        iceInd2Prev = data["iceInd"][t - 2]

        # -------------------------------------------------------------------------
        # short-term supply forecasts over next 4 quarter-months
        # -------------------------------------------------------------------------

        # ontario net total supply (ontario nbs + erie outflows)
        sfSupplyNTS = [
            data["ontNTS_QM1"][t],
            data["ontNTS_QM2"][t],
            data["ontNTS_QM3"][t],
            data["ontNTS_QM4"][t],
        ]

        # lac st. louis flows - lake ontario flows (ottawa river flows)
        sfSupplySLON = [
            data["slonFlow_QM1"][t],
            data["slonFlow_QM2"][t],
            data["slonFlow_QM3"][t],
            data["slonFlow_QM4"][t],
        ]

        # -------------------------------------------------------------------------
        # long-term supply forecasts
        # -------------------------------------------------------------------------

        # ontario basin supply
        lfSupply = data["forNTS"][t]
        # lfCon = data["confidence"][t]
        # lfInd = data["indicator"][t]

        # -------------------------------------------------------------------------
        # state indicators
        # -------------------------------------------------------------------------

        # ice status
        iceInd = data["iceInd"][t]

        # true versus forecasted slon
        if version == "historic" or version == "climate_scenarios":
            foreInd = 1
            if foreInd == 1:
                slonFlow = data["slonFlow_QM1"][t]
            elif foreInd == 0:
                slonFlow = data["stlouisontOut"][t]
        elif version == "stochastic":
            foreInd = 0
            carillonFlow = data["carillonFlow"][t]
            chateauguayFlow = data["chateauguayFlow"][t]

        # true nts
        obsontNTS = data["ontNTS"][t]

        # flow, level, and flag if september levels are dangerously high
        if qm <= 32:
            flowflag = 0
            qm32Flow = np.nan
            qm32Level = np.nan

        elif qm > 32:
            qm32Flow = data["ontFlow"][data["Year"] == year][32 - 1]
            qm32Level = data["ontLevel"][data["Year"] == year][32 - 1]
            if qm32Level > 74.8:
                flowflag = 1
            else:
                flowflag = 0

        # -------------------------------------------------------------------------
        # format inputs and call release function [rule curve or ann]
        # -------------------------------------------------------------------------

        if releaseFun == "RC":
            # -------------------------------------------------------------------------
            # long forecast generator [indicator and confidence]
            # -------------------------------------------------------------------------

            # upper and lower limits based on antecedent conditions
            up99limit = lfSupply + lf99Conf
            up50limit = lfSupply + lf50Conf
            low99limit = lfSupply - lf99Conf
            low50limit = lfSupply - lf50Conf

            # conditions for wet and dry indicators
            dry = lfDryThreshold
            wet = lfWetThreshold

            # define indicator of wet (1), dry (-1), or neither (0) for supply
            if lfSupply > wet:
                lfInd = 1
            elif lfSupply >= dry and lfSupply <= wet:
                lfInd = 0
            else:
                lfInd = -1

            # compute the confidence level
            if lfInd == 1:
                if low99limit >= wet:
                    lfCon = 3
                elif low50limit >= wet:
                    lfCon = 2
                elif low50limit < wet:
                    lfCon = 1
                else:
                    lfCon = np.nan

            if lfInd == 0:
                if low99limit >= dry and up99limit <= wet:
                    lfCon = 3
                elif low50limit >= dry and up50limit <= wet:
                    lfCon = 2
                elif low50limit < dry or up50limit > wet:
                    lfCon = 1
                else:
                    lfCon = np.nan

            if lfInd == -1:
                if up99limit <= dry:
                    lfCon = 3
                elif up50limit <= dry:
                    lfCon = 2
                elif up50limit > dry:
                    lfCon = 1
                else:
                    lfCon = np.nan

            data["indicator"] = lfInd
            data["confidence"] = lfCon

            # calculate rule curve release for each forecasted quarter-month (1 - 4)
            nforecasts = 4
            startLev = []
            startLev.append(ontLevelStart)
            endLev = []
            sfFlow = []
            sfpreprojFlow = []
            sfRegime = []

            for k in range(nforecasts):
                # function of levels and long-term forecast of supplies
                slope = 55.5823

                # set indicators
                ice = 0
                adj = 0.0014 * (2010 - 1985)
                epsolon = 0.0001

                # while loop and break variables
                flg = 1
                ct = 0
                lastflow = 0

                while flg == 1:
                    # only exits loop once a convergence threshold (epsolon) is met or 10
                    # iterations exceeded. adjust the preproject relationship by how much the
                    # long-term supply forecast varies from average

                    # pre-project flows
                    preproj = slope * (startLev[k] - adj - 69.474) ** 1.5

                    # above average supplies
                    if lfSupply >= rcThreshold:
                        # set c1 coefficients based on how confident forecast is in wet
                        if lfInd == 1 and lfCon == 3:
                            c1 = rcWetConfC
                        else:
                            c1 = rcWetC

                        # rule curve release
                        flow = (
                            preproj
                            + ((lfSupply - rcThreshold) / wetDenominator) ** rcWetP * c1
                        )

                        # set rc flow regime
                        if lfInd == 1 and lfCon == 3:
                            sy = "RCW+"
                        else:
                            sy = "RCW"

                    # below average supplies
                    if lfSupply < rcThreshold:
                        # set c2 coefficient
                        c2 = rcDryC

                        # rule curve release
                        flow = (
                            preproj
                            - ((rcThreshold - lfSupply) / dryDenominator) ** rcDryP * c2
                        )

                        # set rc flow regime
                        sy = "RCD"

                    # adjust release for any ice
                    release = round(flow - ice, 0)
                    # release = engRound(flow - ice, 1)

                    if abs(release - lastflow) <= epsolon:
                        break

                    # stability check
                    lastflow = release
                    ct = ct + 1

                    if ct == 10:
                        break

                # # try to keep ontario level up in dry periods
                # if annavgLevel <= adjLevel:
                #     release = release + adjFlow
                #     sy = sy + "-"

                sfFlow.append(release)
                sfpreprojFlow.append(preproj)
                sfRegime.append(sy)

                # compute water level change using forecasted supply and flow
                dif1 = round((sfSupplyNTS[k] / 10 - sfFlow[k]) / conv, 6)
                endLev.append(startLev[k] + dif1)
                meanLev = round(((startLev[k] + endLev[k]) * 0.5), 2)

                # update intial conditions
                if k < list(range(nforecasts))[-1]:
                    # startLev.append(endLev[k])
                    startLev.append(meanLev)

            release = sum(sfFlow) / nforecasts

            # try to keep ontario level up in dry periods
            if annavgLevel <= adjLevel:
                release = release + adjFlow
                sy = sy + "-"

        if releaseFun == "RC2":
            # -------------------------------------------------------------------------
            # long forecast generator [indicator and confidence]
            # -------------------------------------------------------------------------

            # upper and lower limits based on antecedent conditions
            # up99limit = lfSupply + lf99Conf
            # up50limit = lfSupply + lf50Conf
            low99limit = lfSupply - lf99Conf
            # low50limit = lfSupply - lf50Conf

            # conditions for wet and dry indicators
            dry = lfDryThreshold
            wet = lfWetThreshold

            # define indicator of wet (1), dry (-1), or neither (0) for supply
            if lfSupply > wet:
                lfInd = 1
            elif lfSupply >= dry and lfSupply <= wet:
                lfInd = 0
            else:
                lfInd = -1

            # compute the confidence level
            if lfInd == 1:
                if low99limit >= wet:
                    lfCon = 3
                # elif low50limit >= wet:
                #     lfCon = 2
                # elif low50limit < wet:
                #     lfCon = 1
                else:
                    lfCon = np.nan
            else:
                lfCon = np.nan

            # if lfInd == 0:
            #     if low99limit >= dry and up99limit <= wet:
            #         lfCon = 3
            #     elif low50limit >= dry and up50limit <= wet:
            #         lfCon = 2
            #     elif low50limit < dry or up50limit > wet:
            #         lfCon = 1
            #     else:
            #         lfCon = np.nan

            # if lfInd == -1:
            #     if up99limit <= dry:
            #         lfCon = 3
            #     elif up50limit <= dry:
            #         lfCon = 2
            #     elif up50limit > dry:
            #         lfCon = 1
            #     else:
            #         lfCon = np.nan

            data["indicator"] = lfInd
            data["confidence"] = lfCon

            # calculate rule curve release for each forecasted quarter-month (1 - 4)
            nforecasts = 4
            startLev = []
            startLev.append(ontLevelStart)
            endLev = []
            sfFlow = []
            sfpreprojFlow = []
            sfRegime = []

            for k in range(nforecasts):
                # function of levels and long-term forecast of supplies
                slope = 55.5823

                # set indicators
                ice = 0
                adj = 0.0014 * (2010 - 1985)
                epsolon = 0.0001

                # while loop and break variables
                flg = 1
                ct = 0
                lastflow = 0

                while flg == 1:
                    # only exits loop once a convergence threshold (epsolon) is met or 10
                    # iterations exceeded. adjust the preproject relationship by how much the
                    # long-term supply forecast varies from average

                    # pre-project flows
                    preproj = slope * (startLev[k] - adj - 69.474) ** 1.5

                    # above average supplies
                    if lfSupply >= rcThreshold:
                        # set c1 coefficients based on how confident forecast is in wet
                        if lfInd == 1 and lfCon == 3:
                            c1 = rcWetConfC
                        else:
                            c1 = rcWetC

                        # rule curve release
                        flow = (
                            preproj
                            + ((lfSupply - rcThreshold) / (wetScaling - rcThreshold))
                            ** rcWetP
                            * c1
                        )

                        # set rc flow regime
                        if lfInd == 1 and lfCon == 3:
                            sy = "RCW+"
                        else:
                            sy = "RCW"

                    # below average supplies
                    if lfSupply < rcThreshold:
                        # set c2 coefficient
                        c2 = rcDryC

                        # rule curve release
                        flow = (
                            preproj
                            - ((rcThreshold - lfSupply) / (rcThreshold - dryScaling))
                            ** rcDryP
                            * c2
                        )

                        # set rc flow regime
                        sy = "RCD"

                    # adjust release for any ice
                    release = round(flow - ice, 0)
                    # release = engRound(flow - ice, 1)

                    if abs(release - lastflow) <= epsolon:
                        break

                    # stability check
                    lastflow = release
                    ct = ct + 1

                    if ct == 10:
                        break

                # # try to keep ontario level up in dry periods
                # if annavgLevel <= adjLevel:
                #     release = release + adjFlow
                #     sy = sy + "-"

                sfFlow.append(release)
                sfpreprojFlow.append(preproj)
                sfRegime.append(sy)

                # compute water level change using forecasted supply and flow
                dif1 = round((sfSupplyNTS[k] / 10 - sfFlow[k]) / conv, 6)
                endLev.append(startLev[k] + dif1)
                meanLev = round(((startLev[k] + endLev[k]) * 0.5), 2)

                # update intial conditions
                if k < list(range(nforecasts))[-1]:
                    # startLev.append(endLev[k])
                    startLev.append(meanLev)

            release = sum(sfFlow) / nforecasts

            # try to keep ontario level up in dry periods
            if annavgLevel <= adjLevel:
                release = release + adjFlow
                sy = sy + "-"

        elif releaseFun == "fANN":
            # set normalization range for inputs
            normRange = [-1, 1]

            # normalize inputs
            supplyRange = [4000, 10000]
            x1 = minmaxNorm(lfSupply, supplyRange, normRange)
            levelRange = [70, 80]
            x2 = minmaxNorm(ontLevelStart, levelRange, normRange)
            # formulation of seasonality
            x3cos = round(
                np.cos(((2 * math.pi) / 48) * (qm - 2.5)), 6
            )  # respresetation of winter [1] - summer [-1] cycle
            x3sin = round(
                np.sin(((2 * math.pi) / 48) * (qm - 2.5)), 6
            )  # respresetation of spring [1] - fall [-1] cycle

            # join inputs into array to send to ANN policy
            x = [x1, x2, x3cos, x3sin]
            # print(x)

            # call policy
            annFlow = annPolicy(x, pars)
            # print(annFlow)

            # backcalculate output to cms
            releaseRange = [0, 1500]
            release = minmaxNorm(
                annFlow[0], releaseRange, normRange, method="backtransform"
            )

            # save into time series for record
            data["annOutput"][t] = release

        elif releaseFun == "adjANN":
            # set normalization range for inputs
            normRange = [-1, 1]

            # normalize inputs
            supplyRange = [4000, 10000]
            x1 = minmaxNorm(lfSupply, supplyRange, normRange)
            levelRange = [70, 80]
            x2 = minmaxNorm(ontLevelStart, levelRange, normRange)
            # formulation of seasonality
            x3cos = round(
                np.cos(((2 * math.pi) / 48) * (qm - 2.5)), 6
            )  # respresetation of winter [1] - summer [-1] cycle
            x3sin = round(
                np.sin(((2 * math.pi) / 48) * (qm - 2.5)), 6
            )  # respresetation of spring [1] - fall [-1] cycle

            # join inputs into array to send to ANN policy
            x = [x1, x2, x3cos, x3sin]
            # print(x)

            # call policy
            annFlow = annPolicy(x, pars)

            # backcalculate adjustment to cms
            adjRange = [-250, 500]
            adjustFlow = minmaxNorm(
                annFlow[0], adjRange, normRange, method="backtransform"
            )

            # save into time series for record
            data["annOutput"][t] = adjustFlow

            # pre-project flows
            slope = 55.5823
            adj = 0.0014 * (2010 - 1985)
            preproj = slope * (ontLevelStart - adj - 69.474) ** 1.5

            # adjust pre-project flow
            release = preproj + adjustFlow

        # compute averaged quarter-monthly release using forecasted nts
        ontFlow = round(release, 0)
        dif1 = round((sfSupplyNTS[0] / 10 - ontFlow) / conv, 6)
        ontLevel = round(ontLevelStart + dif1, 6)
        ontRegime = "RF"
        data["rfFlow"][t] = ontFlow

        # -----------------------------------------------------------------------------
        # limit check
        # -----------------------------------------------------------------------------

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

        if septemberRule == "on":
            if qm > 32 and flowflag == 1 and ontLevel > 74.80:
                if qm <= 46:
                    flowadj = ((ontLevel - 74.80) * conv) / (46 - qm + 1)
                else:
                    flowadj = ((ontLevel - 74.80) * conv) / (48 - qm + 1)

                # adjust rule curve flow
                ontFlow = ontFlow + flowadj

                if qm == 33:
                    ontFlow = min(ontFlow, qm32Flow)

                # adjust rule curve flow
                ontFlow = round(ontFlow, 0)

                # calculate resulting water level
                dif1 = round((sfSupplyNTS[0] / 10 - ontFlow) / conv, 6)
                ontLevel = round(ontLevel + dif1, 2)

                # adjust rule curve flow regime
                ontRegime = "R+"

        if plan == "2014":
            # -----------------------------------------------------------------------------
            #
            # 1st L limit check
            #
            # added L limit code to limit to prevent unrealistically high flows
            # also added symbol to indicate if this applies
            # if fall lake levels are dangerously high for the coming year MAX flow = L limits DF
            #
            # -----------------------------------------------------------------------------

            if ontLevelStart <= 75.13:
                lFlow = 835.0 + 100.0 * (ontLevelStart - 74.70)
            elif ontLevelStart <= 75.44:
                lFlow = 878.0 + 364.5 * (ontLevelStart - 75.13)
            elif ontLevelStart <= 75.70:
                lFlow = 991.0
            elif ontLevelStart <= 76.0:
                lFlow = 1070.0
            else:
                lFlow = 1150.0

            if ontFlow > lFlow:
                ontFlow = round(lFlow, 0)
                # ontFlow = engRound(lFlow, 1)
                ontRegime = "L1"

            # compute averaged quarter-monthly release using forecasted nts
            dif1 = round((sfSupplyNTS[0] / 10 - ontFlow) / conv, 6)
            ontLevel = round(ontLevelStart + dif1, 2)

        # -----------------------------------------------------------------------------
        #
        # high and low pct level check
        #
        # if lake ontario level is wihtin normal limits, use Bv7 limits
        # else use 58DD limits
        #
        # -----------------------------------------------------------------------------

        if plan == "2014":
            # calculate average water level
            avgCheck = (ontLevelStart + ontLevel) * 0.5

            # get high and low limits for the qm
            qmHighPctLevel = ontHighPctLevel[qm - 1]
            qmLowPctLevel = ontLowPctLevel[qm - 1]

        # -----------------------------------------------------------------------------
        # Bv7 limits
        # -----------------------------------------------------------------------------

        if (plan == "Bv7") or (
            plan == "2014"
            and (avgCheck <= qmHighPctLevel and avgCheck >= qmLowPctLevel)
        ):
            # -----------------------------------------------------------------------------
            #
            # I limit - ice stability
            #
            # maximum i-limit flow check. ice status of 0, 1, and 2 correspond to no ice,
            # stable ice formed, and unstable ice forming
            #
            # -----------------------------------------------------------------------------

            if iceInd == 2 or iceIndPrev == 2:
                iLimFlow = 623

            elif iceInd == 1 or (qm < 13 or qm > 47):
                # calculate release to keep long sault level above 71.8 m
                con1 = (kingLevelStart - 62.40) ** 2.2381
                con2 = ((kingLevelStart - 71.80) / data["longsaultR"][t]) ** 0.3870
                qx = (22.9896 * con1 * con2) * 0.10
                iLimFlow = round(qx, 0)

                # added from iceReg
                if iceInd == 1:
                    if iLimFlow > 943.0:
                        iLimFlow = 943.0

                else:
                    if iLimFlow > 991.0:
                        iLimFlow = 991.0

            else:
                iLimFlow = 0

            iRegime = "I"

            # -----------------------------------------------------------------------------
            #
            # L limit - navigation and channel capacity check
            #
            # maximum l-limit flow check - primarily based on level. applied during
            # the navigation season (qm 13 - qm 47) and during non-navigation season.
            # reference table b3 in compendium report
            #
            # -----------------------------------------------------------------------------

            lFlow = 0

            # navigation season
            if qm >= 13 and qm <= 47:
                lRegime = "LN"

                if ontLevel <= 74.22:
                    lFlow = 595.0

                elif ontLevel <= 74.34:
                    lFlow = 595.0 + 133.3 * (ontLevel - 74.22)

                elif ontLevel <= 74.54:
                    lFlow = 611.0 + 910 * (ontLevel - 74.34)

                elif ontLevel <= 74.70:
                    lFlow = 793.0 + 262.5 * (ontLevel - 74.54)

                elif ontLevel <= 75.13:
                    lFlow = 835.0 + 100.0 * (ontLevel - 74.70)

                elif ontLevel <= 75.44:
                    lFlow = 878.0 + 364.5 * (ontLevel - 75.13)

                elif ontLevel <= 75.70:
                    lFlow = 991.0

                elif ontLevel <= 76.0:
                    lFlow = 1020.0

                else:
                    lFlow = 1070.0

                # check minimum long sault level - calculate the ontFlow to keeplong sault level above lstd_mlv_min
                if ontLevel >= 74.20:
                    longSaultmin = 72.60
                else:
                    longSaultmin = 72.60 - (74.20 - ontLevel)

                kingstonLevel = ontLevel - 0.03
                a = 2.29896
                b = 62.4
                c = 2.2381
                d = 0.387
                lFlow2 = (
                    a
                    * ((kingstonLevel - b) ** c)
                    * (
                        (
                            (kingstonLevel - longSaultmin)
                            / round(data["longsaultR"][t], 3)
                        )
                        ** d
                    )
                )

                lFlow2 = round(lFlow2, 0)
                # lFlow2 = engRound(lFlow2, 1)

                if lFlow2 < lFlow:
                    lRegime = "LS"
                    lFlow = lFlow2

            # non-navigation season
            else:
                lRegime = "LM"
                lFlow = 1150.0

            # channel capacity check
            # lFlow1 = lFlow
            # if (
            #     ontLevel >= 69.10
            # ):  # added if statement to account for really low water levels and negative values
            #     lFlow2 = (747.2 * (ontLevel - 69.10) ** 1.47) / 10.0
            # else:
            #     lFlow2 = np.nan
            lFlow3 = (747.2 * (ontLevel - 69.10) ** 1.47) / 10.0
            if lFlow3 < lFlow:
                lFlow = lFlow3
                lRegime = "LC"

            lLimFlow = round(lFlow, 0)

            # -----------------------------------------------------------------------------
            #
            # M limit -  low level balance
            #
            # minimum m-limit flow check. minimum limit flows to balance low levels of
            # lake ontario and lac st. louis primarily for seaway navigation interests
            #
            # -----------------------------------------------------------------------------

            if version == "historic" or version == "climate_scenarios":
                # compute crustal adjustment factor, fixed for year 2010
                adj = 0.0014 * (2010 - 1985)
                slope = 55.5823

                # this part borrowed from 58DD to prevent too low St. Louis levels
                if ontLevel > 74.20:
                    mq = 680.0 - (slonFlow * 0.1)

                elif ontLevel > 74.10 and ontLevel <= 74.20:
                    mq = 650.0 - (slonFlow * 0.1)

                elif ontLevel > 74.00 and ontLevel <= 74.10:
                    mq = 620.0 - (slonFlow * 0.1)

                elif ontLevel > 73.60 and ontLevel <= 74.00:
                    mq = 610.0 - (slonFlow * 0.1)

                else:
                    mq1 = 577.0 - (slonFlow * 0.1)

                    # if ontLevel >= (
                    #     adj + 69.474
                    # ):  # added to account for levels below 69.474
                    #     mq2 = slope * (ontLevel - adj - 69.474) ** 1.5

                    # else:
                    #     mq2 = np.nan
                    mq2 = slope * (ontLevel - adj - 69.474) ** 1.5
                    # mq = min(mq1, mq2)
                    mq = mq2

                mLimFlow = round(mq, 0)
                # mLimFlow = engRound(mq, 1)
                mRegime = "M"

            # stochastic version of M limit to prevent too low of flows
            elif version == "stochastic":
                # start M-limit calculation
                # m-limit by quarter-month
                qmLimFlow = np.hstack(
                    [
                        [595] * 4,
                        [586] * 4,
                        [578] * 4,
                        [532] * 8,
                        [538] * 4,
                        [547] * 12,
                        [561] * 8,
                        [595] * 4,
                    ]
                )

                mFlow = qmLimFlow[qm - 1]

                if ontLevel > 74.20:
                    Qsplit = mFlow
                    limQ = 680.0

                    diff = 999
                    QOnt1 = Qsplit

                    k = 1
                    maxIterations = 9999

                    while k < maxIterations:
                        tmp = slonCalculation(Qsplit, carillonFlow, chateauguayFlow)
                        Qstl_Ont = tmp["slonFlow"]
                        Q_Ontlimit = limQ - (Qstl_Ont / 10)
                        if Q_Ontlimit < 0.0:
                            Q_Ontlimit = 0.0
                        diff = abs(Q_Ontlimit - QOnt1)
                        QOnt1 = Q_Ontlimit

                        if diff <= 1.0:
                            break

                    Q_Ontlimit = round(Q_Ontlimit, 0)
                    Qsplit = Q_Ontlimit

                elif ontLevel > 74.10 and ontLevel <= 74.20:
                    Qsplit = mFlow
                    limQ = 650.0

                    diff = 999
                    QOnt1 = Qsplit

                    k = 1
                    maxIterations = 9999

                    while k < maxIterations:
                        tmp = slonCalculation(Qsplit, carillonFlow, chateauguayFlow)
                        Qstl_Ont = tmp["slonFlow"]
                        Q_Ontlimit = limQ - (Qstl_Ont / 10)
                        if Q_Ontlimit < 0.0:
                            Q_Ontlimit = 0.0
                        diff = abs(Q_Ontlimit - QOnt1)
                        QOnt1 = Q_Ontlimit

                        if diff <= 1.0:
                            break

                    Q_Ontlimit = round(Q_Ontlimit, 0)
                    Qsplit = Q_Ontlimit

                elif ontLevel > 74.00 and ontLevel <= 74.10:
                    Qsplit = mFlow
                    limQ = 620.0

                    diff = 999
                    QOnt1 = Qsplit

                    k = 1
                    maxIterations = 9999

                    while k < maxIterations:
                        tmp = slonCalculation(Qsplit, carillonFlow, chateauguayFlow)
                        Qstl_Ont = tmp["slonFlow"]
                        Q_Ontlimit = limQ - (Qstl_Ont / 10)
                        if Q_Ontlimit < 0.0:
                            Q_Ontlimit = 0.0
                        diff = abs(Q_Ontlimit - QOnt1)
                        QOnt1 = Q_Ontlimit

                        if diff <= 1.0:
                            break

                    Q_Ontlimit = round(Q_Ontlimit, 0)
                    Qsplit = Q_Ontlimit

                elif ontLevel > 73.60 and ontLevel <= 74.00:
                    Qsplit = mFlow
                    limQ = 610.0

                    diff = 999
                    QOnt1 = Qsplit

                    k = 1
                    maxIterations = 9999

                    while k < maxIterations:
                        tmp = slonCalculation(Qsplit, carillonFlow, chateauguayFlow)
                        Qstl_Ont = tmp["slonFlow"]
                        Q_Ontlimit = limQ - (Qstl_Ont / 10)
                        if Q_Ontlimit < 0.0:
                            Q_Ontlimit = 0.0
                        diff = abs(Q_Ontlimit - QOnt1)
                        QOnt1 = Q_Ontlimit

                        if diff <= 1.0:
                            break

                    Q_Ontlimit = round(Q_Ontlimit, 0)
                    Qsplit = Q_Ontlimit

                else:
                    Qsplit = mFlow
                    limQ = 577.0

                    diff = 999
                    QOnt1 = Qsplit

                    k = 1
                    maxIterations = 9999

                    while k < maxIterations:
                        tmp = slonCalculation(Qsplit, carillonFlow, chateauguayFlow)
                        Qstl_Ont = tmp["slonFlow"]
                        Q_Ontlimit = limQ - (Qstl_Ont / 10)
                        if Q_Ontlimit < 0.0:
                            Q_Ontlimit = 0.0
                        diff = abs(Q_Ontlimit - QOnt1)
                        QOnt1 = Q_Ontlimit

                        if diff <= 1.0:
                            break

                    Q_Ontlimit = round(Q_Ontlimit, 0)
                    Qsplit1 = Q_Ontlimit

                    # compute crustal adjustment factor, fixed for year 2010
                    adj = 0.0014 * (2010 - 1985)
                    slope = 55.5823

                    if ontLevel >= (
                        adj + 69.474
                    ):  # added to account for levels below 69.474
                        Qsplit2 = slope * (ontLevel - adj - 69.474) ** 1.5

                    else:
                        Qsplit2 = np.nan

                    Qsplit = min(Qsplit1, Qsplit2)

                mFlow = Qsplit

                mLimFlow = round(mFlow, 0)
                mRegime = "M"

            # -----------------------------------------------------------------------------
            #
            # J limit - stability check
            #
            # j-limit stability flow check. adjusts large changes between flow for coming
            # week and actual flow last week. can be min or max limit.
            #
            # -----------------------------------------------------------------------------

            # difference between rc flow and last week's actual flow
            flowdif = abs(ontFlow - ontFlowPrev)

            # flow change bounds
            jdn = 70
            jup = 70

            # increase upper j-limit if high lake ontario level and no ice
            if ontLevel > 75.20 and iceInd == 0 and iceIndPrev < 2:
                jup = 142

            # if flow difference is positive, check if maxJ applies
            if ontFlow >= ontFlowPrev:
                # upper J limit applies
                if flowdif > jup:
                    jFlow = ontFlowPrev + jup
                    if jup == 70:
                        jRegime = "J+"
                    else:
                        jRegime = "JM"

                # no jlim is applied, flow is RC flow
                else:
                    jFlow = ontFlow
                    jRegime = ontRegime

            # if the flow difference is negative, check if minJ applies
            else:
                # lower J limit applies
                if flowdif > jdn:
                    jFlow = ontFlowPrev - jdn
                    jRegime = "J-"

                # no jlim is applied, flow is RC flow
                else:
                    jFlow = ontFlow
                    jRegime = ontRegime

            jLimFlow = round(jFlow, 0)

            # -----------------------------------------------------------------------------
            # limit comparison
            # -----------------------------------------------------------------------------

            # this is either the J-limit (if applied) or the RC flow and regime
            maxLimFlow = jLimFlow
            maxLimRegime = jRegime

            # get the smallest of the maximum limits (L and I)
            maxLim = -9999

            if lLimFlow != 0:
                if maxLim < 0:
                    maxLim = lLimFlow
                    maxRegime = lRegime

            if iLimFlow != 0:
                if maxLim < 0 or iLimFlow < maxLim:
                    maxLim = iLimFlow
                    maxRegime = iRegime

            # compare rc flow or j limit with maximum limits (RC or J with L and I)
            if maxLim > 0 and maxLimFlow > maxLim:
                maxLimFlow = maxLim
                maxLimRegime = maxRegime

            # get the biggest of the minimum limits (M)
            minLimFlow = mLimFlow
            minLimRegime = mRegime

            # compare the maximum and minimum limits
            if maxLimFlow > minLimFlow:
                limFlow = maxLimFlow
                limRegime = maxLimRegime

            # if the limit reaches to this point, then take the minimum limit
            else:
                # if the M limit is greater than the smaller of the I/L limit, take the M limit
                if minLimFlow > maxLim:
                    if minLimRegime == mRegime:
                        limFlow = minLimFlow
                        limRegime = minLimRegime
                    else:
                        if maxLim > minLimFlow:
                            limFlow = maxLim
                            limRegime = maxRegime
                        else:
                            limFlow = minLimFlow
                            limRegime = mRegime
                else:
                    limFlow = minLimFlow
                    limRegime = minLimRegime

            # update ontFlow and ontRegime post limit check
            ontFlow = limFlow
            ontRegime = limRegime

            # compute averaged quarter-monthly release using forecasted nts
            dif1 = round((sfSupplyNTS[0] / 10 - ontFlow) / conv, 6)
            ontLevel = round(ontLevelStart + dif1, 2)

            # -----------------------------------------------------------------------------
            #
            # F limit - downstream flooding
            #
            # f-limit levels check. calculate lac st. louis flow at levels at pt. claire
            # to determine if downstream flooding needs to be mitigated
            #
            # -----------------------------------------------------------------------------

            # determine "action level" to apply at pointe claire
            if ontLevelStart < 75.3:
                actionlev = 22.10
                c1 = 11523.848
            elif ontLevelStart < 75.37:
                actionlev = 22.20
                c1 = 11885.486
            elif ontLevelStart < 75.50:
                actionlev = 22.33
                c1 = 12362.610
            elif ontLevelStart < 75.60:
                actionlev = 22.40
                c1 = 12622.784
            else:
                actionlev = 22.48
                c1 = 12922.906

            if version == "historic" or version == "climate_scenarios":
                # flows through lac st louis from slon value
                stlouisFlow = ontFlow * 10.0 + slonFlow

                # calculate pointe claire level
                ptclaireLevel = round(
                    16.57 + ((data["ptclaireR"][t] * stlouisFlow / 604.0) ** 0.58), 2
                )

                # estimate flow required to maintain pointe claire below action level
                if ptclaireLevel > actionlev:
                    flimFlow = round((c1 / data["ptclaireR"][t] - slonFlow) / 10.0, 0)

                    if flimFlow < ontFlow:
                        ontFlow = flimFlow
                        ontRegime = "F"

            elif version == "stochastic":
                if foreInd == 1:
                    tmp = slonCalculation(ontFlow, carillonFlow, chateauguayFlow)
                    slonFlow = tmp["slonFlow"]
                    fFlow = round((c1 / data["ptclaireR"][t] - slonFlow) / 10.0, 0)

                else:
                    Qsplit = ontFlow
                    limQ = (c1 / data["ptclaireR"][t]) / 10.0

                    diff = 999
                    QOnt1 = Qsplit

                    k = 1
                    maxIterations = 9999

                    while k < maxIterations:
                        tmp = slonCalculation(Qsplit, carillonFlow, chateauguayFlow)
                        Qstl_Ont = tmp["slonFlow"]
                        Q_Ontlimit = limQ - (Qstl_Ont / 10)
                        if Q_Ontlimit < 0.0:
                            Q_Ontlimit = 0.0
                        diff = abs(Q_Ontlimit - QOnt1)
                        QOnt1 = Q_Ontlimit

                        if diff <= 1.0:
                            break

                    Q_Ontlimit = round(Q_Ontlimit, 0)
                    fFlow = Q_Ontlimit

                flimFlow = round(fFlow, 0)

                if flimFlow < ontFlow:
                    ontFlow = flimFlow
                    ontRegime = "F"

        # -----------------------------------------------------------------------------
        # deviations - Plan 58DD limits
        # -----------------------------------------------------------------------------

        elif plan == "2014" and (avgCheck > qmHighPctLevel or avgCheck < qmLowPctLevel):
            # -----------------------------------------------------------------------------
            #
            # I limit - ice stability
            #
            # maximum i-limit flow check. ice status of 0, 1, and 2 correspond to no ice,
            # stable ice formed, and unstable ice forming
            #
            # -----------------------------------------------------------------------------

            if iceInd == 2 or iceIndPrev == 2:
                iLimFlow = 623.0

            elif iceInd == 1 or (qm < 13 or qm > 47):
                # calculate release to keep long sault level above 71.8 m
                con1 = (kingLevelStart - 62.40) ** 2.2381
                con2 = ((kingLevelStart - 71.80) / data["longsaultR"][t]) ** 0.3870
                qx = (22.9896 * con1 * con2) * 0.1
                iLimFlow = round(qx, 0)

            else:
                iLimFlow = 9999

            if iceInd == 1:
                if iLimFlow > 943.0:
                    iLimFlow = 943.0
            elif iceInd == 0:
                if iLimFlow > 1150.0:
                    iLimFlow = 1150.0

            if iceInd == 0 and iceIndPrev == 1:
                if iLimFlow > 950.0:
                    iLimFlow = 950.0

            elif iceInd == 0 and iceIndPrev == 0 and iceInd2Prev == 1:
                if iLimFlow > 1000.0:
                    iLimFlow = 1000.0

            iRegime = "I"

            # -----------------------------------------------------------------------------
            #
            # L limit - navigation and channel capacity check
            #
            # maximum l-limit flow check - primarily based on level. applied during
            # the navigation season (qm 13 - qm 47) and during non-navigation season.
            # reference table b3 in compendium report
            #
            # -----------------------------------------------------------------------------

            # navigation season
            if qm >= 13 and qm <= 47:
                lRegime = "LN"

                # from Flimit991 subroutine
                lev_7422 = 74.22
                lev_7434 = 74.34
                lev_7443 = 74.43
                lev_7454 = 74.54
                lev_757 = 75.7
                lev_758 = 75.8
                lev_747 = 74.7
                lev_7513 = 75.13
                lev_7544 = 75.44
                lev_031 = 0.31
                flow_595 = 595.0
                flow_623 = 623.0
                flow_611 = 611.0
                flow_113 = 113.0
                flow_793 = 793.0
                flow_835 = 835.0
                flow_878 = 878.0
                flow_991 = 991.0
                flow_1020 = 1020.0
                flow_1070 = 1070.0

                if ontLevel <= lev_7422:
                    flim991 = flow_595

                elif ontLevel > lev_7422 and ontLevel <= lev_7434:
                    flim991 = (flow_595 - flow_623) / (lev_7422 - lev_7443) * (
                        ontLevel - lev_7422
                    ) + flow_595

                elif ontLevel > lev_7434 and ontLevel <= lev_7454:
                    flim991 = (flow_611 - flow_793) / (lev_7434 - lev_7454) * (
                        ontLevel - lev_7434
                    ) + flow_611

                elif ontLevel > lev_7454 and ontLevel <= lev_747:
                    flim991 = (flow_793 - flow_835) / (lev_7454 - lev_747) * (
                        ontLevel - lev_7454
                    ) + flow_793

                elif ontLevel > lev_747 and ontLevel <= lev_7513:
                    flim991 = (flow_835 - flow_878) / (lev_747 - lev_7513) * (
                        ontLevel - lev_747
                    ) + flow_835

                elif ontLevel > lev_7513 and ontLevel <= lev_7544:
                    flim991 = flow_878 - flow_113 / (lev_031) * (ontLevel - lev_7513)

                elif ontLevel > lev_7544 and ontLevel <= lev_757:
                    flim991 = flow_991

                elif ontLevel > lev_757 and ontLevel <= lev_758:
                    flim991 = flow_1020

                else:
                    flim991 = flow_1070

                lFlow = round(flim991, 0)
                # lFlow = engRound(flim991, 1)

                # check minimum long sault level - calculate the ontFlow to keeplong sault level above lstd_mlv_min
                if ontLevel >= 74.20:
                    longSaultmin = 72.60
                else:
                    longSaultmin = 72.60 - (74.20 - ontLevel)

                kingstonLevel = ontLevel - 0.03
                a = 2.29896
                b = 62.4
                c = 2.2381
                d = 0.387
                lFlow2 = (
                    a
                    * ((kingstonLevel - b) ** c)
                    * (
                        (
                            (kingstonLevel - longSaultmin)
                            / round(data["longsaultR"][t], 3)
                        )
                        ** d
                    )
                )
                lFlow2 = round(lFlow2, 0)

                if lFlow2 < lFlow:
                    lRegime = "LS"
                    lFlow = lFlow2

            # non-navigation season
            else:
                lRegime = "LM"
                lFlow = 1150.0

            # channel capacity check
            lFlow1 = lFlow
            if (
                ontLevel >= 69.10
            ):  # added if statement to account for really low water levels and negative values
                lFlow2 = (747.2 * (ontLevel - 69.10) ** 1.47) / 10.0
            else:
                lFlow2 = np.nan

            if lFlow2 < lFlow1:
                lFlow = lFlow2
                lRegime = "LC"

            lLimFlow = round(lFlow, 0)

            # -----------------------------------------------------------------------------
            #
            # M limit -  low level balance
            #
            # minimum m-limit flow check. minimum limit flows to balance low levels of
            # lake ontario and lac st. louis primarily for seaway navigation interests
            #
            # -----------------------------------------------------------------------------

            # compute crustal adjustment factor, fixed for year 2010
            adj = 0.0014 * (2010 - 1985)
            slope = 55.5823

            if version == "historic" or version == "climate_scenarios":
                # this part borrowed from 58DD to prevent too low St. Louis levels
                if ontLevel > 74.20:
                    mq = 680.0 - (slonFlow * 0.1)

                elif ontLevel > 74.10 and ontLevel <= 74.20:
                    mq = 650.0 - (slonFlow * 0.1)

                elif ontLevel > 74.00 and ontLevel <= 74.10:
                    mq = 620.0 - (slonFlow * 0.1)

                elif ontLevel > 73.60 and ontLevel <= 74.00:
                    mq = 610.0 - (slonFlow * 0.1)

                else:
                    mq1 = 577.0 - (slonFlow * 0.1)

                    if ontLevel >= (
                        adj + 69.474
                    ):  # added to account for levels below 69.474
                        # # compute crustal adjustment factor, fixed for year 2010
                        # adj = 0.0014 * (2010 - 1985)
                        # slope = 55.5823

                        mq2 = slope * (ontLevel - adj - 69.474) ** 1.5

                    else:
                        mq2 = np.nan

                    mq = min(mq1, mq2)

                mLimFlow = round(mq, 0)
                mRegime = "M"

            # stochastic version of M limit to prevent too low of flows
            elif version == "stochastic":
                # start M-limit calculation
                # m-limit by quarter-month
                qmLimFlow = np.hstack(
                    [
                        [595] * 4,
                        [586] * 4,
                        [578] * 4,
                        [532] * 8,
                        [538] * 4,
                        [547] * 12,
                        [561] * 8,
                        [595] * 4,
                    ]
                )

                mFlow = qmLimFlow[qm - 1]

                if ontLevel > 74.20:
                    Qsplit = mFlow
                    limQ = 680.0

                    diff = 999
                    QOnt1 = Qsplit

                    k = 1
                    maxIterations = 9999

                    while k < maxIterations:
                        tmp = slonCalculation(Qsplit, carillonFlow, chateauguayFlow)
                        Qstl_Ont = tmp["slonFlow"]
                        Q_Ontlimit = limQ - (Qstl_Ont / 10)

                        if Q_Ontlimit < 0.0:
                            Q_Ontlimit = 0.0

                        diff = abs(Q_Ontlimit - QOnt1)
                        QOnt1 = Q_Ontlimit

                        if diff <= 1.0:
                            break

                    Q_Ontlimit = round(Q_Ontlimit, 0)
                    Qsplit = Q_Ontlimit

                elif ontLevel > 74.10 and ontLevel <= 74.20:
                    Qsplit = mFlow
                    limQ = 650.0

                    diff = 999
                    QOnt1 = Qsplit

                    k = 1
                    maxIterations = 9999

                    while k < maxIterations:
                        tmp = slonCalculation(Qsplit, carillonFlow, chateauguayFlow)
                        Qstl_Ont = tmp["slonFlow"]
                        Q_Ontlimit = limQ - (Qstl_Ont / 10)

                        if Q_Ontlimit < 0.0:
                            Q_Ontlimit = 0.0

                        diff = abs(Q_Ontlimit - QOnt1)
                        QOnt1 = Q_Ontlimit

                        if diff <= 1.0:
                            break

                    Q_Ontlimit = round(Q_Ontlimit, 0)
                    Qsplit = Q_Ontlimit

                elif ontLevel > 74.00 and ontLevel <= 74.10:
                    Qsplit = mFlow
                    limQ = 620.0

                    diff = 999
                    QOnt1 = Qsplit

                    k = 1
                    maxIterations = 9999

                    while k < maxIterations:
                        tmp = slonCalculation(Qsplit, carillonFlow, chateauguayFlow)
                        Qstl_Ont = tmp["slonFlow"]
                        Q_Ontlimit = limQ - (Qstl_Ont / 10)
                        if Q_Ontlimit < 0.0:
                            Q_Ontlimit = 0.0
                        diff = abs(Q_Ontlimit - QOnt1)
                        QOnt1 = Q_Ontlimit

                        if diff <= 1.0:
                            break

                    Q_Ontlimit = round(Q_Ontlimit, 0)
                    Qsplit = Q_Ontlimit

                elif ontLevel > 73.60 and ontLevel <= 74.00:
                    Qsplit = mFlow
                    limQ = 610.0

                    diff = 999
                    QOnt1 = Qsplit

                    k = 1
                    maxIterations = 9999

                    while k < maxIterations:
                        tmp = slonCalculation(Qsplit, carillonFlow, chateauguayFlow)
                        Qstl_Ont = tmp["slonFlow"]
                        Q_Ontlimit = limQ - (Qstl_Ont / 10)
                        if Q_Ontlimit < 0.0:
                            Q_Ontlimit = 0.0
                        diff = abs(Q_Ontlimit - QOnt1)
                        QOnt1 = Q_Ontlimit

                        if diff <= 1.0:
                            break

                    Q_Ontlimit = round(Q_Ontlimit, 0)
                    Qsplit = Q_Ontlimit

                else:
                    Qsplit = mFlow
                    limQ = 577.0

                    diff = 999
                    QOnt1 = Qsplit

                    k = 1
                    maxIterations = 9999

                    while k < maxIterations:
                        tmp = slonCalculation(Qsplit, carillonFlow, chateauguayFlow)
                        Qstl_Ont = tmp["slonFlow"]
                        Q_Ontlimit = limQ - (Qstl_Ont / 10)
                        if Q_Ontlimit < 0.0:
                            Q_Ontlimit = 0.0
                        diff = abs(Q_Ontlimit - QOnt1)
                        QOnt1 = Q_Ontlimit

                        if diff <= 1.0:
                            break

                    Q_Ontlimit = round(Q_Ontlimit, 0)
                    Qsplit1 = Q_Ontlimit

                    # compute crustal adjustment factor, fixed for year 2010
                    adj = 0.0014 * (2010 - 1985)
                    slope = 55.5823

                    if ontLevel >= (
                        adj + 69.474
                    ):  # added to account for levels below 69.474
                        Qsplit2 = slope * (ontLevel - adj - 69.474) ** 1.5

                    else:
                        Qsplit2 = np.nan

                    Qsplit = min(Qsplit1, Qsplit2)

                mFlow = Qsplit

                mLimFlow = round(mFlow, 0)
                mRegime = "M"

            # -----------------------------------------------------------------------------
            #
            # J limit - stability check
            #
            # j-limit stability flow check. adjusts large changes between flow for coming
            # week and actual flow last week. can be min or max limit.
            #
            # -----------------------------------------------------------------------------

            # difference between rc flow and last week's actual flow
            flowdif = abs(ontFlow - ontFlowPrev)

            # flow change bounds
            jdn = 70
            jup = 70

            # increase upper j-limit if high lake ontario level and no ice
            if ontLevel > 75.20 and iceInd == 0 and iceIndPrev < 2:
                jup = 142

            # if flow difference is positive, check if maxJ applies
            if ontFlow >= ontFlowPrev:
                # upper J limit applies
                if flowdif > jup:
                    jFlow = ontFlowPrev + jup
                    if jup == 70:
                        jRegime = "J+"
                    else:
                        jRegime = "JJ"

                # no jlim is applied, flow is RC flow
                else:
                    jFlow = ontFlow
                    jRegime = ontRegime

            # if the flow difference is negative, check if minJ applies
            else:
                # lower J limit applies
                if flowdif > jdn:
                    jFlow = ontFlowPrev - jdn
                    jRegime = "J-"

                # no jlim is applied, flow is RC flow
                else:
                    jFlow = ontFlow
                    jRegime = ontRegime

            jLimFlow = round(jFlow, 0)

            # -----------------------------------------------------------------------------
            # limit comparison
            # -----------------------------------------------------------------------------

            # this is either the J-limit (if applied) or the RC flow and regime
            maxLimFlow = jLimFlow
            maxLimRegime = jRegime

            # get the smallest of the maximum limits (L and I)
            maxLim = -9999

            if lLimFlow != 0:
                if maxLim < 0:
                    maxLim = lLimFlow
                    maxRegime = lRegime

            if iLimFlow != 0:
                if maxLim < 0 or iLimFlow < maxLim:
                    maxLim = iLimFlow
                    maxRegime = iRegime

            # compare rc flow or j limit with maximum limits (RC or J with L and I)
            if maxLim > 0 and maxLimFlow > maxLim:
                maxLimFlow = maxLim
                maxLimRegime = maxRegime

            # get the biggest of the minimum limits (M)
            minLimFlow = mLimFlow
            minLimRegime = mRegime

            # compare the maximum and minimum limits
            if maxLimFlow > minLimFlow:
                limFlow = maxLimFlow
                limRegime = maxLimRegime

            # if the limit reaches to this point, then take the minimum limit
            else:
                # if the M limit is greater than the smaller of the I/L limit, take the M limit
                if minLimFlow > maxLim:
                    if minLimRegime == mRegime:
                        limFlow = minLimFlow
                        limRegime = minLimRegime
                    else:
                        if maxLim > minLimFlow:
                            limFlow = maxLim
                            limRegime = maxRegime
                        else:
                            limFlow = minLimFlow
                            limRegime = mRegime
                else:
                    limFlow = minLimFlow
                    limRegime = minLimRegime

            # update ontFlow and ontRegime post limit check
            ontFlow = limFlow
            ontRegime = limRegime

            # compute averaged quarter-monthly release using forecasted nts
            dif1 = round((sfSupplyNTS[0] / 10 - ontFlow) / conv, 6)
            ontLevel = round(ontLevelStart + dif1, 2)

            # -----------------------------------------------------------------------------
            #
            # F limit - downstream flooding
            #
            # f-limit levels check. calculate lac st. louis flow at levels at pt. claire
            # to determine if downstream flooding needs to be mitigated
            #
            # -----------------------------------------------------------------------------

            # determine "action level" to apply at pointe claire
            if ontLevelStart < 75.3:
                actionlev = 22.10
                c1 = 11523.848
            elif ontLevelStart < 75.37:
                actionlev = 22.20
                c1 = 11885.486
            elif ontLevelStart < 75.50:
                actionlev = 22.33
                c1 = 12362.610
            elif ontLevelStart < 75.60:
                actionlev = 22.40
                c1 = 12622.784
            elif ontLevelStart < 75.75:
                actionlev = 22.48
                c1 = 12922.906
            else:
                actionlev = max(22.48, (0.476 * ontLevelStart - 13.589))
                c1 = max(12922.906, 604.0 * (actionlev - 16.57) ** (1.0 / 0.58))

            if version == "historic" or version == "climate_scenarios":
                # flows through lac st louis from slon value
                stlouisFlow = ontFlow * 10.0 + slonFlow

                # calculate pointe claire level
                ptclaireLevel = round(
                    16.57 + ((data["ptclaireR"][t] * stlouisFlow / 604.0) ** 0.58), 2
                )

                # estimate flow required to maintain pointe claire below action level
                if ptclaireLevel > actionlev:
                    flimFlow = round((c1 / data["ptclaireR"][t] - slonFlow) / 10.0, 0)

                    if flimFlow < ontFlow:
                        ontFlow = flimFlow
                        ontRegime = "F"

            elif version == "stochastic":
                if foreInd == 1:
                    fFlow = round((c1 / data["ptclaireR"][t] - slonFlow) / 10.0, 0)

                else:
                    Qsplit = ontFlow
                    limQ = (c1 / data["ptclaireR"][t]) / 10.0

                    diff = 999
                    QOnt1 = Qsplit

                    k = 1
                    maxIterations = 9999

                    while k < maxIterations:
                        tmp = slonCalculation(Qsplit, carillonFlow, chateauguayFlow)
                        Qstl_Ont = tmp["slonFlow"]
                        Q_Ontlimit = limQ - (Qstl_Ont / 10)
                        if Q_Ontlimit < 0.0:
                            Q_Ontlimit = 0.0
                        diff = abs(Q_Ontlimit - QOnt1)
                        QOnt1 = Q_Ontlimit

                        if diff <= 1.0:
                            break

                    Q_Ontlimit = round(Q_Ontlimit, 0)
                    fFlow = Q_Ontlimit

                flimFlow = round(fFlow, 0)

                if flimFlow < ontFlow:
                    ontFlow = flimFlow
                    ontRegime = "F"

            if avgCheck > qmHighPctLevel:
                ontRegime = ontRegime + "8+"
            elif avgCheck < qmLowPctLevel:
                ontRegime = ontRegime + "8-"

        # -----------------------------------------------------------------------------
        # no limits
        # -----------------------------------------------------------------------------

        elif plan == "none":
            # only calculate winter ice limit to avoid ice jam (not represented in objective functions)
            if iceInd == 2 or iceIndPrev == 2:
                iLimFlow = 623

            elif iceInd == 1 or (qm < 13 or qm > 47):
                # calculate release to keep long sault level above 71.8 m
                con1 = (kingLevelStart - 62.40) ** 2.2381
                con2 = ((kingLevelStart - 71.80) / data["longsaultR"][t]) ** 0.3870
                qx = (22.9896 * con1 * con2) * 0.10
                iLimFlow = round(qx, 0)

                # added from iceReg
                if iceInd == 1:
                    if iLimFlow > 943.0:
                        iLimFlow = 943.0

                else:
                    if iLimFlow > 991.0:
                        iLimFlow = 991.0

            else:
                iLimFlow = 0

            iRegime = "I"

            if iLimFlow < ontFlow:
                ontFlow = iLimFlow
                ontRegime = iRegime
            else:
                ontFlow = ontFlow
                ontRegime = ontRegime

        # -------------------------------------------------------------------------
        # ontario and st. lawrence level and flow calculations
        # -------------------------------------------------------------------------

        # calculate final ontario water level after limits applied, this is the true level using observed nts
        dif2 = round(((obsontNTS / 10) - ontFlow) / conv, 6)
        ontLevel_EOQ_unrounded = round(ontLevelStart + dif2, 6)
        # ontLevel = round(ontLevelStart + dif2, 2)

        # save ontario output for next iteration
        # data["ontLevel"][t] = ontLevel
        data["ontFlow"][t] = ontFlow
        data["flowRegime"][t] = ontRegime

        data["ontLevelBOQ"][t + 1] = ontLevel_EOQ_unrounded
        data["ontLevelEOQ"][t] = round(ontLevel_EOQ_unrounded, 2)

        MEANontLevel = (ontLevel_EOQ_unrounded + ontLevelStart) * 0.5
        data["ontLevelMOQ"][t] = round(MEANontLevel, 2)
        data["ontLevel"][t] = MEANontLevel

        # for now, use MEAN ontario level to calculate the objective functions
        ontLevel = MEANontLevel

        if version == "historic" or version == "climate_scenarios":
            # calculate st. lawrence levels
            stlouisFlow = ontFlow + (slonFlow / 10)
            data["stlouisFlow"][t] = stlouisFlow

        elif version == "stochastic":
            tmp = slonCalculation(ontFlow, carillonFlow, chateauguayFlow)

            stlouisFlow = tmp["lacstlouisFlow"] / 10
            slonFlow = tmp["slonFlow"]

            data["stlouisFlow"][t] = stlouisFlow
            data["stlouisontOut"][t] = slonFlow
            data["vaudreuilFlow"][t] = tmp["vaudreuilFlow"]
            data["stanneFlow"][t] = tmp["stanneFlow"]
            data["dpmiFlow"][t] = tmp["dpmiFlow"]

        # kingston
        kingstonLevel = ontLevel - 0.03
        difLev = kingstonLevel - 62.40

        # ogdensburg
        ogdensburgLevel = round(
            kingstonLevel
            - data["ogdensburgR"][t]
            * pow(ontFlow / (6.328 * pow(difLev, 2.0925)), (1 / 0.4103)),
            2,
        )

        # alexandria bay
        alexbayLevel = round(
            kingstonLevel - 0.39 * (kingstonLevel - ogdensburgLevel), 2
        )

        # brockville
        brockvilleLevel = round(
            kingstonLevel - 0.815 * (kingstonLevel - ogdensburgLevel), 2
        )

        # cardinal
        cardinalLevel = round(
            kingstonLevel
            - data["cardinalR"][t]
            * pow(ontFlow / (1.94908 * pow(difLev, 2.3981)), (1 / 0.4169)),
            2,
        )

        # iroquois headwaters
        iroquoishwLevel = round(
            kingstonLevel
            - data["iroquoishwR"][t]
            * pow(ontFlow / (2.36495 * pow(difLev, 2.2886)), (1 / 0.4158)),
            2,
        )

        # saunders headwaters
        saundershwLevel1 = round(
            kingstonLevel
            - (
                data["saundershwR"][t]
                * pow(
                    (ontFlow * 10) / (21.603 * pow(difLev, 2.2586)),
                    (1 / 0.3749),
                )
            ),
            2,
        )

        if saundershwLevel1 > 73.87:
            if iceInd == 2:
                saundershwLevel = saundershwLevel1
            else:
                saundershwLevel = 73.783
        else:
            saundershwLevel = saundershwLevel1

        # iroquois tailwaters (dependent saunders headwaters level)
        iroquoistwLevel1 = round(
            kingstonLevel
            - data["iroquoistwR"][t]
            * pow(ontFlow / (2.42291 * pow(difLev, 2.2721)), (1 / 0.4118)),
            2,
        )

        iroquoistwLevel2 = round(
            73.78 + pow((ontFlow * 10), 1.841) / pow((73.78 - 55), 5.891), 2
        )

        if saundershwLevel == 73.783:
            iroquoistwLevel = iroquoistwLevel2
        else:
            iroquoistwLevel = iroquoistwLevel1

        # morrisburg (dependent saunders headwaters level)
        morrisburgLevel1 = round(
            kingstonLevel
            - (
                data["morrisburgR"][t]
                * (ontFlow / (2.39537 * (difLev**2.245))) ** (1 / 0.3999)
            ),
            2,
        )

        morrisburgLevel2 = round(
            73.78 + 6.799 * pow((ontFlow * 10), 1.913) / 811896440.84868, 2
        )

        if saundershwLevel == 73.783:
            morrisburgLevel = morrisburgLevel2
        else:
            morrisburgLevel = morrisburgLevel1

        # long sault (dependent saunders headwaters level)
        longsaultLevel1 = round(
            kingstonLevel
            - (
                data["longsaultR"][t]
                * (ontFlow / (2.29896 * (difLev**2.2381))) ** (1 / 0.3870)
            ),
            2,
        )

        longsaultLevel2 = round(
            73.78 + 1408000 * pow((ontFlow * 10), 2.188) / 12501578154791700, 2
        )

        if saundershwLevel == 73.783:
            longsaultLevel = round(longsaultLevel2, 2)
        else:
            longsaultLevel = longsaultLevel1

        # saunders tailwaters
        saunderstwLevel = round(
            44.50 + 0.006338 * pow((data["saunderstwR"][t] * ontFlow * 10), 0.7158),
            2,
        )

        # cornwall
        cornwallLevel = round(
            45.00 + 0.0756 * pow((data["cornwallR"][t] * ontFlow * 10), 0.364),
            2,
        )

        # summerstown
        summerstownLevel = round(
            46.10 + 0.0109 * pow((data["summerstownR"][t] * ontFlow * 10), 0.451),
            2,
        )

        # pointe-claire (lac st. louis)
        ptclaireLevel = round(
            16.57 + pow((data["ptclaireR"][t] * stlouisFlow / 60.4), 0.58), 2
        )

        # lery beauharnois (uses pointe-claire level)
        lerybeauharnoisLevel = ptclaireLevel

        # keep regressions for climate scenarios without tributary inflows
        if version == "climate_scenarios":
            # jetty 1 (montreal harbor)
            jetty1Level = round((ptclaireLevel * 1.657) + (-28.782), 2)

            # st. lambert
            stlambertLevel = round((ptclaireLevel * 1.583) + (-27.471), 2)

            # varennes
            varennesLevel = round((ptclaireLevel * 1.535) + (-26.943), 2)

            # sorel
            sorelLevel = round((ptclaireLevel * 1.337) + (-23.616), 2)

            # lac st. pierre
            lacstpierreLevel = round((ptclaireLevel * 1.366) + (-24.620), 2)

            # maskinonge (uses lac st pierre level)
            maskinongeLevel = lacstpierreLevel

            # troisrivieres
            troisrivieresLevel = round((ptclaireLevel * 1.337) + (-24.425), 2)

            # batiscan
            batiscanLevel = round((ptclaireLevel * 1.105) + (-20.269), 2)

        else:
            # tributary flows for downstream level
            if version == "historic":
                desprairiesOut = data["desprairiesOut"][t]
                richelieuOut = data["richelieuOut"][t]
                stfrancoisOut = data["stfrancoisOut"][t]
                stmauriceOut = data["stmauriceOut"][t]
                tidalInd = data["tidalInd"][t]
                stlouisFlowcms = data["stlouisFlow"][t] * 10

            if version == "stochastic":
                desprairiesOut = data["dpmiFlow"][t]
                richelieuOut = data["richelieuFlow"][t]
                stfrancoisOut = data["stfrancoisFlow"][t]
                stmauriceOut = data["stmauriceFlow"][t]
                tidalInd = data["tidalInd"][t]
                stlouisFlowcms = data["stlouisFlow"][t] * 10

            # jetty 1 (montreal harbor)
            lstl_flw_fctr = 0.001757 * stlouisFlowcms
            dpmi_flw_fctr = 0.000684 * desprairiesOut
            stfr_flw_fctr = 0.001161 * stfrancoisOut
            stmc_flw_fctr = 0.000483 * stmauriceOut
            flw_sum = lstl_flw_fctr + dpmi_flw_fctr + stfr_flw_fctr + stmc_flw_fctr
            jetty1R = data["jetty1R"][t]
            jetty1Level = round(((flw_sum) * jetty1R) ** 0.6587 + 0.9392 * tidalInd, 2)
            # jetty1Level = round((ptclaireLevel * 1.657) + (-28.782), 2)

            # st. lambert
            stlambertLevel = round((ptclaireLevel * 1.583) + (-27.471), 2)

            # varennes
            lstl_flw_fctr = 0.001438 * stlouisFlowcms
            dpmi_flw_fctr = 0.001377 * desprairiesOut
            stfr_flw_fctr = 0.001442 * stfrancoisOut
            stmc_flw_fctr = 0.000698 * stmauriceOut
            flw_sum = lstl_flw_fctr + dpmi_flw_fctr + stfr_flw_fctr + stmc_flw_fctr
            varennesR = data["varennesR"][t]
            varennesLevel = round(
                ((flw_sum) * varennesR) ** 0.6373 + 1.0578 * tidalInd, 2
            )
            # varennesLevel = round((ptclaireLevel * 1.535) + (-26.943), 2)

            # sorel
            lstl_flw_fctr = 0.001075 * stlouisFlowcms
            dpmi_flw_fctr = 0.001126 * desprairiesOut
            stfr_flw_fctr = 0.001854 * stfrancoisOut
            stmc_flw_fctr = 0.000882 * stmauriceOut
            flw_sum = lstl_flw_fctr + dpmi_flw_fctr + stfr_flw_fctr + stmc_flw_fctr
            sorelR = data["sorelR"][t]
            sorelLevel = round(((flw_sum) * sorelR) ** 0.6331 + 1.277 * tidalInd, 2)
            # sorelLevel = round((ptclaireLevel * 1.337) + (-23.616), 2)

            # lac st. pierre
            lstl_flw_fctr = 0.000807 * stlouisFlowcms
            dpmi_flw_fctr = 0.001199 * desprairiesOut
            stfr_flw_fctr = 0.001954 * stfrancoisOut
            stmc_flw_fctr = 0.000976 * stmauriceOut
            flw_sum = lstl_flw_fctr + dpmi_flw_fctr + stfr_flw_fctr + stmc_flw_fctr
            stpierreR = data["stpierreR"][t]
            lacstpierreLevel = round(
                ((flw_sum) * stpierreR) ** 0.6529 + 1.4772 * tidalInd, 2
            )
            # lacstpierreLevel = round((ptclaireLevel * 1.366) + (-24.620), 2)

            # maskinonge (uses lac st pierre level)
            maskinongeLevel = lacstpierreLevel

            # troisrivieres
            lstl_flw_fctr = 0.000584 * stlouisFlowcms
            dpmi_flw_fctr = 0.000690 * desprairiesOut
            rich_flw_fctr = 0.000957 * richelieuOut
            stfr_flw_fctr = 0.001197 * stfrancoisOut
            stmc_flw_fctr = 0.000787 * stmauriceOut
            flw_sum = (
                lstl_flw_fctr
                + dpmi_flw_fctr
                + rich_flw_fctr
                + stfr_flw_fctr
                + stmc_flw_fctr
            )
            troisrivieresR = data["threeriversR"][t]
            troisrivieresLevel = round(
                ((flw_sum) * troisrivieresR) ** 0.7042 + 1.5895 * tidalInd, 2
            )
            # troisrivieresLevel = round((ptclaireLevel * 1.337) + (-24.425), 2)

            # batiscan
            lstl_flw_fctr = 0.000422 * stlouisFlowcms
            dpmi_flw_fctr = 0.000553 * desprairiesOut
            rich_flw_fctr = 0.000903 * richelieuOut
            stfr_flw_fctr = 0.001023 * stfrancoisOut
            stmc_flw_fctr = 0.000682 * stmauriceOut
            flw_sum = (
                lstl_flw_fctr
                + dpmi_flw_fctr
                + rich_flw_fctr
                + stfr_flw_fctr
                + stmc_flw_fctr
            )
            batiscanR = data["batiscanR"][t]
            batiscanLevel = round(
                ((flw_sum) * batiscanR) ** 0.6941 + 1.8303 * tidalInd, 2
            )
            # batiscanLevel = round((ptclaireLevel * 1.105) + (-20.269), 2)

        data["kingstonLevel"][t] = kingstonLevel
        data["alexbayLevel"][t] = alexbayLevel
        data["brockvilleLevel"][t] = brockvilleLevel
        data["ogdensburgLevel"][t] = ogdensburgLevel
        data["cardinalLevel"][t] = cardinalLevel
        data["iroquoishwLevel"][t] = iroquoishwLevel
        data["iroquoistwLevel"][t] = iroquoistwLevel
        data["morrisburgLevel"][t] = morrisburgLevel
        data["longsaultLevel"][t] = longsaultLevel
        data["saundershwLevel"][t] = saundershwLevel
        data["saunderstwLevel"][t] = saunderstwLevel
        data["cornwallLevel"][t] = cornwallLevel
        data["summerstownLevel"][t] = summerstownLevel
        data["lerybeauharnoisLevel"][t] = lerybeauharnoisLevel
        data["ptclaireLevel"][t] = ptclaireLevel
        data["jetty1Level"][t] = jetty1Level
        data["stlambertLevel"][t] = stlambertLevel
        data["varennesLevel"][t] = varennesLevel
        data["sorelLevel"][t] = sorelLevel
        data["lacstpierreLevel"][t] = lacstpierreLevel
        data["maskinongeLevel"][t] = maskinongeLevel
        data["troisrivieresLevel"][t] = troisrivieresLevel
        data["batiscanLevel"][t] = batiscanLevel

        # defines a freshet as a spring flow that starts 1.5 times bigger than the last QM flow at LSL
        # and stays a freshet until flows drop to 90% or less of the previous QM
        # not sure how to calculate, hard set to 1,
        # data["freshetIndicator"][t] = 1

        # convert back to a dataframe and return

    # convert to dataframe
    data = pd.DataFrame(data)

    # calculate freshet indicator based on Lac St. Louis flows
    # SVM defines a freshet as a spring flow that starts 1.5 times bigger than the last QM flow at LSL
    # and stays a freshet until flows drop to 90% or less of the previous QM
    lsl = data.loc[:, ["Sim", "Year", "Month", "QM", "stlouisFlow"]]
    # lsl = lsl.dropna()

    lsl["criteria1"] = lsl.loc[:, "stlouisFlow"].shift(1, fill_value=np.nan) * 1.5
    lsl["criteria2"] = lsl.loc[:, "stlouisFlow"].shift(1, fill_value=np.nan) * 0.9
    # lsl["criteria1"] = lsl["criteria2"]
    lsl["freshetIndicator"] = 0

    tmpLSL = lsl

    while tmpLSL.shape[0] > 0:
        # get first occurence of Lac St. Louis flow exceeding previous flow by 1.5 and set freshet indicator to 1
        ind1 = tmpLSL.loc[tmpLSL["stlouisFlow"] > tmpLSL["criteria1"], "Sim"].min()

        # find next occurence where Lac St. Louis flow falls below previous flow by 0.9
        ind2 = tmpLSL.loc[tmpLSL["stlouisFlow"] < tmpLSL["criteria2"], "Sim"].min()

        # assign freshet indicator to rows between [ind1, ind2)
        lsl.loc[(lsl["Sim"] >= ind1) & (lsl["Sim"] < ind2), "freshetIndicator"] = 1

        # filter out remaining rows
        tmpLSL = tmpLSL.loc[tmpLSL["Sim"] > ind2]

    data["freshetIndicator"] = lsl["stlouisFlow"]

    return data


# calls simulation and objective functions to return aggregate PI measures
def optimization(
    expName, v, plan, septemberRule, releaseFun, dvInfo, piWeighting, *vars
):
    # print(vars)
    # # load data by experiment name
    # if loc == "glhpc":
    #     data = pd.read_table("/tmpssd/input/" + expName + ".txt")
    # else:
    data = pd.read_table("input/" + expName + ".txt")

    # extract decision variable bounds and convert into units
    bounds = {k: dvInfo[k] for k in ("lowerBounds", "upperBounds")}
    ranges = dvInfo["normalizedRange"]
    dvs = list(vars)
    for i in range(len(dvs)):
        dvs[i] = minmaxNorm(
            dvs[i], [x[i] for x in bounds.values()], ranges, method="backtransform"
        )

    # format decision variables
    if "ANN" in releaseFun:
        # number of neurons, inputs, and outputs
        neurons = 15
        inputs = 4
        output = 1

        # # set decision variables
        # dvs = vars

        # first n elements (# neurons x # inputs) - reshape weights to neuron (rows) x input (cols)
        inputLayer2hiddenLayer = np.reshape(
            dvs[0 : (neurons * inputs)], (neurons, inputs)
        )

        # the next n elements (# neurons) after weights are the neuron biases
        hiddenLayerBias = np.array(
            dvs[(neurons * inputs) : (neurons * inputs + neurons)]
        )

        # the next n elements (# neurons x # outputs)
        hiddenLayer2outputLayer = np.reshape(
            dvs[(neurons * inputs + neurons) : (len(dvs) - output)], (output, neurons)
        )

        # last n elements are output layer biases (# outputs)
        outputLayerBias = np.array(dvs[-output:])

        pars = {}
        pars["inputLayer2hiddenLayer"] = inputLayer2hiddenLayer
        pars["hiddenLayerBias"] = hiddenLayerBias
        pars["hiddenLayer2outputLayer"] = hiddenLayer2outputLayer
        pars["outputLayerBias"] = outputLayerBias

    elif "RC" in releaseFun:
        pars = dict(zip(dvInfo["dvName"], dvs))

    # -----------------------------------------------------------------------------
    # plan 2014 simulation
    # -----------------------------------------------------------------------------

    startTimeSim = datetime.now()
    outSim = simulation(data, v, plan, septemberRule, releaseFun, **pars)
    endTimeSim = datetime.now()

    # -----------------------------------------------------------------------------
    # objective function evaluation
    # -----------------------------------------------------------------------------

    # run objective functions for upstream coastal, downstream coastal, commercial
    # naviation, hydropower, meadow marsh, muskrat house density,and recreational
    # boating. returns annual average for each objective

    # convert data frame to dictionary for faster computation
    startTimeObj = datetime.now()
    data = outSim.loc[(outSim["Year"] > 1899) & (outSim["Year"] < 2020), :]
    data = {x: data[x].values for x in data}

    # data = outSim.dropna().reset_index(drop=True)
    # data = {x: data[x].values for x in data}

    # na_counts = outSim.isna().sum(axis=1)
    # data = outSim.drop(na_counts[na_counts > 10].index, axis=0)
    # data = {x: data[x].values for x in data}

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
    ) = objectiveFunctions.objectiveSimulation(data, piWeighting)

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
