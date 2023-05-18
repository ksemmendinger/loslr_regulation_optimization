# import libraries
import os
import sys
import numpy as np
import pandas as pd

# set variables from command line input
args = sys.argv
# args = ["", "mac_loc", "12month", "sqAR", "100", "17"]
# args = ["", "mac_loc", "baseline"]

# set working directory
if args[1] == "mac_loc":
    wd = "/Users/kylasemmendinger/Library/CloudStorage/Box-Box/Plan_2014/optimization/output"
elif args[1] == "hopper":
    wd = "/home/fs02/pmr82_0001/kts48/optimization/output"
os.chdir(wd)

if args[2] == "baseline":

    # folder name
    folderName = "baseline"

else:

    # forecast lead-time
    leadtime = args[2]

    # forecast skill
    skill = args[3]

    # number of function evaluations
    nfe = int(args[4])

    # number of decision variables
    nvars = int(args[5])

    # folder name
    folderName = (
        leadtime + "_" + str(skill) + "_" + str(nfe) + "nfe_" + str(nvars) + "dvs"
    )

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

# create folder for clean decision variable and objective files
newpath = "data/" + folderName + "/postAnalysis/hCriteria"
if not os.path.exists(newpath):
    os.makedirs(newpath)

# -----------------------------------------------------------------------------
# re-simulate each policy using basis of comparison hydrology
# -----------------------------------------------------------------------------

# load in policies that make up the pareto front
pop = pd.read_csv("data/" + folderName + "/NonDominatedPolicies.txt", sep="\t")

totalH1 = []
totalH2 = []
totalH3 = []
totalH4 = []
totalH6 = []
totalH7 = []
totalH14 = []

for i in range(pop.shape[0]):

    print(str(i) + "/" + str(pop.shape[0]))
    # print(pop.loc[i, "Experiment"])

    # load input data for given experiment
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

    inputData = pd.read_csv(
        "postScripts/basis_of_comparison/" + leadtime + "_" + skill + ".txt",
        sep="\t",
    )

    # set decision variables
    rcWetC = pop.loc[i, "Rule Curve Wet Multiplier"]
    rcWetConfC = pop.loc[i, "Rule Curve Confident Wet Multiplier"]
    rcDryC = pop.loc[i, "Rule Curve Dry Multiplier"]
    rcWetP = pop.loc[i, "Rule Curve Wet Power"]
    rcDryP = pop.loc[i, "Rule Curve Dry Power"]
    rcThreshold = pop.loc[i, "Rule Curve Threshold"]
    rcWetAdjustment = pop.loc[i, "Rule Curve Wet Adjustment"]
    rcDryAdjustment = pop.loc[i, "Rule Curve Dry Adjustment"]
    rcDryLevel = pop.loc[i, "Rule Curve Low Level Threshold"]
    rcDryFlowAdj = pop.loc[i, "Rule Curve Low Level Flow Adjustment"]
    lfWetThreshold = pop.loc[i, "Long Forecast Wet Threshold"]
    lfDryThreshold = pop.loc[i, "Long Forecast Dry Threshold"]
    lf50Conf = pop.loc[i, "Long Forecast 50% Confidence Interval"]
    lf99Conf = pop.loc[i, "Long Forecast 99% Confidence Interval"]
    limSepThreshold = pop.loc[i, "R+ Threshold"]
    limSepThresholdQM1 = pop.loc[i, "R+ Starting Quarter-Month"]
    limSepThresholdQM2 = pop.loc[i, "R+ Ending Quarter-Month"]

    # manually set and omit from optimization
    limSepThreshold = 74.80

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

    data = inputData

    # format output by adding output columns and converting to dict for speed
    data["flowRegime"] = "NA"
    data["stlouisFlow"] = np.nan
    data["ptclaireLevel"] = np.nan
    data["jetty1Level"] = np.nan

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
    # timesteps = len(data["forNTS"][s:][~np.isnan(data["forNTS"][s:])])
    timesteps = len(data["forNTS"])

    for t in range(s, timesteps):

        # quarter month and year
        qm = data["QM"][t]
        year = data["Year"][t]

        # -------------------------------------------------------------------------
        # starting state variables for time step, t
        # -------------------------------------------------------------------------

        # ontario water level
        ontLevelStart = data["ontLevel"][t - 1]

        # kingston water level
        kingLevelStart = ontLevelStart - 0.03

        # average level of previous 48 quarter-months
        annavgLevel = np.mean(data["ontLevel"][(t - 48) : (t)])

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

        # -------------------------------------------------------------------------
        # long-term supply forecasts
        # -------------------------------------------------------------------------

        # ontario basin supply
        lfSupply = data["forNTS"][t]

        # -------------------------------------------------------------------------
        # state indicators
        # -------------------------------------------------------------------------

        # ice status
        iceInd = data["iceInd"][t]

        # true versus forecasted slon
        foreInd = 1
        if foreInd == 1:
            slonFlow = data["slonFlow_QM1"][t]
        elif foreInd == 0:
            slonFlow = data["stlouisontOut"][t]

        # true nts
        obsontNTS = data["ontNTS"][t]

        # flow, level, and flag if september levels are dangerously high
        if qm <= 32:

            qm32Flow = np.nan
            qm32Level = np.nan

        elif qm > 32:

            # take the flow and level from the current year
            qm32Flow = data["ontFlow"][data["Year"] == year][32 - 1]
            qm32Level = data["ontLevel"][data["Year"] == year][32 - 1]

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

        # -------------------------------------------------------------------------
        # rule curve release regime
        # -------------------------------------------------------------------------

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
                preproj = slope * (ontLevelStart - adj - 69.474) ** 1.5

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
                        + ((lfSupply - rcThreshold) / rcWetAdjustment) ** rcWetP * c1
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
                        - ((rcThreshold - lfSupply) / rcDryAdjustment) ** rcDryP * c2
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

            # try to keep ontario level up in dry periods
            if annavgLevel <= rcDryLevel:

                # adjust release
                release = release - rcDryFlowAdj

                # set flow regime
                sy = sy + "-"

            sfFlow.append(release)
            sfpreprojFlow.append(preproj)
            sfRegime.append(sy)

            # compute water level change using forecasted supply and flow
            dif1 = round((sfSupplyNTS[k] / 10 - sfFlow[k]) / conv, 6)
            endLev.append(startLev[k] + dif1)

            # update intial conditions
            if k < list(range(nforecasts))[-1]:
                startLev.append(endLev[k])

        # compute averaged quarter-monthly release using forecasted nts
        ontFlow = round(sum(sfFlow) / nforecasts, 0)
        dif1 = round((sfSupplyNTS[0] / 10 - ontFlow) / conv, 6)
        ontLevel = round(ontLevelStart + dif1, 2)
        ontRegime = sfRegime[0]

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

        # only applies starting QM32
        if qm >= limSepThresholdQM1 or qm <= limSepThresholdQM2:

            # only applies if the QM32 level is greater than the September threshold
            if qm32Level > limSepThreshold:

                # adjust if the starting ontario level is greater than the September threshold
                if ontLevelStart > limSepThreshold:

                    if qm <= 46:
                        flowadj = ((ontLevelStart - limSepThreshold) * conv) / (
                            46 - qm + 1
                        )
                    else:
                        flowadj = ((ontLevelStart - limSepThreshold) * conv) / (
                            48 - qm + 1
                        )

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

        # calculate average water level
        avgCheck = (ontLevelStart + ontLevel) * 0.5

        # get high and low limits for the qm
        qmHighPctLevel = ontHighPctLevel[qm - 1]
        qmLowPctLevel = ontLowPctLevel[qm - 1]

        if avgCheck <= qmHighPctLevel and avgCheck >= qmLowPctLevel:

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
                con2 = ((kingLevelStart - 71.80) / data["lsdamR"][t]) ** 0.3870
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
                        ((kingstonLevel - longSaultmin) / round(data["lsdamR"][t], 3))
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

                    # compute crustal adjustment factor, fixed for year 2010
                    adj = 0.0014 * (2010 - 1985)
                    slope = 55.5823

                    mq2 = slope * (ontLevel - adj - 69.474) ** 1.5

                else:
                    mq2 = np.nan

                mq = min(mq1, mq2)

            mLimFlow = round(mq, 0)
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
            else:
                actionlev = 22.48
                c1 = 12922.906

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

        # -----------------------------------------------------------------------------
        # 58DD limits
        # -----------------------------------------------------------------------------

        else:

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
                con2 = ((kingLevelStart - 71.80) / data["lsdamR"][t]) ** 0.3870
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
                    flim991 = (flow_878 - flow_113) / (lev_031) * (ontLevel - lev_7513)

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
                        ((kingstonLevel - longSaultmin) / round(data["lsdamR"][t], 3))
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

                    # compute crustal adjustment factor, fixed for year 2010
                    adj = 0.0014 * (2010 - 1985)
                    slope = 55.5823

                    mq2 = slope * (ontLevel - adj - 69.474) ** 1.5

                else:
                    mq2 = np.nan

                mq = min(mq1, mq2)

            mLimFlow = round(mq, 0)
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

            ontRegime = ontRegime + "-58DD"

        # -------------------------------------------------------------------------
        # ontario and st. lawrence level and flow calculations
        # -------------------------------------------------------------------------

        # calculate final ontario water level after limits applied, this is the true level using observed nts
        dif2 = round(((obsontNTS / 10) - ontFlow) / conv, 6)
        ontLevel = round(ontLevelStart + dif2, 2)

        # save ontario output for next iteration
        data["ontLevel"][t] = ontLevel
        data["ontFlow"][t] = ontFlow
        data["flowRegime"][t] = ontRegime

        # calculate st. lawrence levels
        stlouisFlow = (ontFlow * 10) + slonFlow
        data["stlouisFlow"][t] = stlouisFlow

        # pointe-claire (lac st. louis)
        ptclaireLevel = round(
            16.57 + pow((data["ptclaireR"][t] * stlouisFlow / 604), 0.58), 2
        )

        jetty1Level = (
            pow(
                data["jetty1R"][t]
                * (
                    (0.001757 * stlouisFlow)
                    + (0.000684 * data["desprairiesOut"][t])
                    + (0.001161 * data["stfrancoisOut"][t])
                    + (0.000483 * data["stmauriceOut"][t])
                ),
                0.6587,
            )
            + (0.9392 * data["tidalInd"][t])
        )

        data["ptclaireLevel"][t] = ptclaireLevel
        data["jetty1Level"][t] = jetty1Level

    df = pd.DataFrame(data)

    # -----------------------------------------------------------------------------
    # h1 - montreal harbor low levels
    # -----------------------------------------------------------------------------

    # get h1 criteria
    H1 = pd.read_excel("postScripts/hCriteria.xlsx", sheet_name="H1", engine="openpyxl")
    H1 = (
        H1.loc[:, ["Threshold", "Threshold Exceedance"]]
        .sort_values(by="Threshold")
        .reset_index(drop=True)
    )

    # extract levels and add lower bound of 0
    levsH1 = [0.0] + list(H1.loc[:, "Threshold"].dropna())

    # bin the simulated water levels
    countH1 = (
        pd.cut(df["jetty1Level"], levsH1, right=True)
        .value_counts()
        .sort_index()
        .reset_index()
    )

    countH1.columns = ["Water Level Bin (m)", "Simulated Exceedances"]
    countH1["Plan 2014 Exceedances"] = H1["Threshold Exceedance"]
    countH1["Performance"] = np.select(
        [
            countH1["Simulated Exceedances"] <= countH1["Plan 2014 Exceedances"],
            countH1["Simulated Exceedances"] > countH1["Plan 2014 Exceedances"],
        ],
        ["Pass", "Fail"],
    )

    # -----------------------------------------------------------------------------
    # h2 - pt claire low levels
    # -----------------------------------------------------------------------------

    # get h1 criteria
    H2 = pd.read_excel("postScripts/hCriteria.xlsx", sheet_name="H2", engine="openpyxl")
    H2 = (
        H2.loc[:, ["Threshold", "Threshold Exceedance"]]
        .sort_values(by="Threshold")
        .reset_index(drop=True)
    )

    # extract levels and add lower bound of 0
    levsH2 = [0.0] + list(H2.loc[:, "Threshold"].dropna())

    # bin the simulated water levels
    countH2 = (
        pd.cut(df["ptclaireLevel"], levsH2, right=True)
        .value_counts()
        .sort_index()
        .reset_index()
    )

    countH2.columns = ["Water Level Bin (m)", "Simulated Exceedances"]
    countH2["Plan 2014 Exceedances"] = H2["Threshold Exceedance"]
    countH2["Performance"] = np.select(
        [
            countH2["Simulated Exceedances"] <= countH2["Plan 2014 Exceedances"],
            countH2["Simulated Exceedances"] > countH2["Plan 2014 Exceedances"],
        ],
        ["Pass", "Fail"],
    )

    # -----------------------------------------------------------------------------
    # h3 - pt claire high levels
    # -----------------------------------------------------------------------------

    # get h1 criteria
    H3 = pd.read_excel("postScripts/hCriteria.xlsx", sheet_name="H3", engine="openpyxl")
    H3 = (
        H3.loc[:, ["Threshold", "Threshold Exceedance"]]
        .sort_values(by="Threshold")
        .reset_index(drop=True)
    )

    # extract levels and add upper bound of inf
    levsH3 = list(H3.loc[:, "Threshold"].dropna()) + [np.inf]

    # bin the simulated water levels
    countH3 = (
        pd.cut(df["ptclaireLevel"], levsH3, right=True)
        .value_counts()
        .sort_index()
        .reset_index()
    )

    countH3.columns = ["Water Level Bin (m)", "Simulated Exceedances"]
    countH3["Plan 2014 Exceedances"] = H3["Threshold Exceedance"]
    countH3["Performance"] = np.select(
        [
            countH3["Simulated Exceedances"] <= countH3["Plan 2014 Exceedances"],
            countH3["Simulated Exceedances"] > countH3["Plan 2014 Exceedances"],
        ],
        ["Pass", "Fail"],
    )

    # -----------------------------------------------------------------------------
    # h4 - monthly mean high ontario levels
    # -----------------------------------------------------------------------------

    # get h4 criteria
    H4 = pd.read_excel("postScripts/hCriteria.xlsx", sheet_name="H4", engine="openpyxl")
    H4 = H4.loc[:, ["Month", "Threshold"]]

    # get monthly mean simulated water levels
    levsH4 = (
        df.loc[:, ["Year", "Month", "ontLevel"]]
        .groupby(["Year", "Month"])
        .agg("mean")
        .droplevel(0)
        .merge(H4, on="Month")
    )

    # compare to monthly thresholds
    levsH4["Performance"] = np.select(
        [
            levsH4["ontLevel"] <= levsH4["Threshold"],
            levsH4["ontLevel"] > levsH4["Threshold"],
        ],
        ["Pass", "Fail"],
    )

    # count occurences of passes/fails
    countH4 = (
        levsH4.groupby(["Month", "Performance"])["Performance"]
        .count()
        .unstack()
        .reset_index()
        .rename_axis(None, axis=1)
    )

    countH4.insert(1, "Threshold (m)", H4.Threshold)

    # -----------------------------------------------------------------------------
    # h6 - monthly mean freq of high ontario levels
    # -----------------------------------------------------------------------------

    # get h6 criteria
    H6 = pd.read_excel("postScripts/hCriteria.xlsx", sheet_name="H6", engine="openpyxl")
    H6 = H6.loc[:, ["Month", "Threshold"]]

    # get monthly mean simulated water levels
    levsH6 = (
        df.loc[:, ["Year", "Month", "ontLevel"]]
        .groupby(["Year", "Month"])
        .agg("mean")
        .droplevel(0)
        .merge(H6, on="Month")
    )

    # compare to monthly thresholds
    levsH6["Performance"] = np.select(
        [
            levsH6["ontLevel"] <= levsH6["Threshold"],
            levsH6["ontLevel"] > levsH6["Threshold"],
        ],
        ["Pass", "Fail"],
    )

    # count occurences of passes/fails
    countH6 = (
        levsH6.groupby(["Month", "Performance"])["Performance"]
        .count()
        .unstack()
        .reset_index()
        .rename_axis(None, axis=1)
    )

    countH6.insert(1, "Threshold (m)", H6.Threshold)

    # -----------------------------------------------------------------------------
    # h7 - monthly mean low ontario levels
    # -----------------------------------------------------------------------------

    # get h7 criteria
    H7 = pd.read_excel("postScripts/hCriteria.xlsx", sheet_name="H7", engine="openpyxl")
    H7 = H7.loc[:, ["Month", "Threshold"]]

    # get monthly mean simulated water levels
    levsH7 = (
        df.loc[:, ["Year", "Month", "ontLevel"]]
        .groupby(["Year", "Month"])
        .agg("mean")
        .droplevel(0)
        .merge(H7, on="Month")
    )

    # compare to monthly thresholds
    levsH7["Performance"] = np.select(
        [
            levsH7["ontLevel"] >= levsH7["Threshold"],
            levsH7["ontLevel"] < levsH7["Threshold"],
        ],
        ["Pass", "Fail"],
    )

    # count occurences of passes/fails
    countH7 = (
        levsH7.groupby(["Month", "Performance"])["Performance"]
        .count()
        .unstack()
        .reset_index()
        .rename_axis(None, axis=1)
        .replace(np.nan, 0)
        .astype(int)
    )

    countH7.insert(1, "Threshold (m)", H7.Threshold)

    # -----------------------------------------------------------------------------
    # h14 - quartermonthly highs and lows
    # -----------------------------------------------------------------------------

    # get h4 criteria
    H14 = pd.read_excel(
        "postScripts/hCriteria.xlsx", sheet_name="H14", engine="openpyxl"
    )
    H14 = H14.loc[:, ["QM", "highTrigger", "lowTrigger"]]

    # get monthly mean simulated water levels
    levsH14 = df.loc[:, ["QM", "ontLevel", "flowRegime"]].merge(H14, on="QM")

    # set conditions of exceedances
    conditions = [
        # 58DD rules applied and rules brought level within h14 criteria
        (
            (levsH14["flowRegime"].str.contains("58DD"))
            & (levsH14["ontLevel"] < levsH14["highTrigger"])
            & (levsH14["ontLevel"] > levsH14["lowTrigger"])
        ),
        # 58DD rules applied but levels were still above h14 criteria
        (
            (levsH14["flowRegime"].str.contains("58DD"))
            & (levsH14["ontLevel"] >= levsH14["highTrigger"])
        ),
        # 58DD rules applied but levels were still below h14 criteria
        (
            (levsH14["flowRegime"].str.contains("58DD"))
            & (levsH14["ontLevel"] <= levsH14["lowTrigger"])
        ),
        # plan 2014 levels within h14 criteria
        (
            (~levsH14["flowRegime"].str.contains("58DD"))
            & (levsH14["ontLevel"] < levsH14["highTrigger"])
            & (levsH14["ontLevel"] > levsH14["lowTrigger"])
        ),
        # plan 2014 levels above h14 criteria
        (
            (~levsH14["flowRegime"].str.contains("58DD"))
            & (levsH14["ontLevel"] >= levsH14["highTrigger"])
        ),
        # plan 2014 levels below h14 criteria
        (
            (~levsH14["flowRegime"].str.contains("58DD"))
            & (levsH14["ontLevel"] <= levsH14["lowTrigger"])
        ),
    ]

    # set identifying values
    choices = [
        "58DD Applied - Okay",
        "58DD Applied - Still High",
        "58DD Applied - Still Low",
        "2014 Applied - Okay",
        "2014 Applied - High",
        "2014 Applied - Low",
    ]

    # find exceedances
    levsH14["Performance"] = np.select(conditions, choices, default="na")

    # count occurences of passes/fails
    countH14 = (
        levsH14.groupby(["QM", "Performance"])["Performance"]
        .count()
        .unstack()
        .reset_index()
        .rename_axis(None, axis=1)
        .replace(np.nan, 0)
        .astype(int)
    )

    countH14.insert(1, "Low Threshold (m)", H14.lowTrigger)
    countH14.insert(1, "High Threshold (m)", H14.highTrigger)

    # -----------------------------------------------------------------------------
    # save h criteria
    # -----------------------------------------------------------------------------

    idCols = ["Experiment", "Lead-Time", "Skill", "ID", "Policy"]
    countH1[idCols] = pop.loc[i, idCols].to_list()
    countH1 = countH1[idCols + (countH1.columns.drop(idCols).tolist())]
    countH2[idCols] = pop.loc[i, idCols].to_list()
    countH2 = countH2[idCols + (countH2.columns.drop(idCols).tolist())]
    countH3[idCols] = pop.loc[i, idCols].to_list()
    countH3 = countH3[idCols + (countH3.columns.drop(idCols).tolist())]
    countH4[idCols] = pop.loc[i, idCols].to_list()
    countH4 = countH4[idCols + (countH4.columns.drop(idCols).tolist())]
    countH6[idCols] = pop.loc[i, idCols].to_list()
    countH6 = countH6[idCols + (countH6.columns.drop(idCols).tolist())]
    countH7[idCols] = pop.loc[i, idCols].to_list()
    countH7 = countH7[idCols + (countH7.columns.drop(idCols).tolist())]
    countH14[idCols] = pop.loc[i, idCols].to_list()
    countH14 = countH14[idCols + (countH14.columns.drop(idCols).tolist())]

    totalH1.append(countH1)
    totalH2.append(countH2)
    totalH3.append(countH3)
    totalH4.append(countH4)
    totalH6.append(countH6)
    totalH7.append(countH7)
    totalH14.append(countH14)

h1 = pd.concat(totalH1)
h2 = pd.concat(totalH2)
h3 = pd.concat(totalH3)
h4 = pd.concat(totalH4)
h6 = pd.concat(totalH6)
h7 = pd.concat(totalH7)
h14 = pd.concat(totalH14)

h1.to_csv(
    "data/" + folderName + "/postAnalysis/hCriteria/h1.txt", sep="\t", index=False
)
h2.to_csv(
    "data/" + folderName + "/postAnalysis/hCriteria/h2.txt", sep="\t", index=False
)
h3.to_csv(
    "data/" + folderName + "/postAnalysis/hCriteria/h3.txt", sep="\t", index=False
)
h4.to_csv(
    "data/" + folderName + "/postAnalysis/hCriteria/h4.txt", sep="\t", index=False
)
h6.to_csv(
    "data/" + folderName + "/postAnalysis/hCriteria/h6.txt", sep="\t", index=False
)
h7.to_csv(
    "data/" + folderName + "/postAnalysis/hCriteria/h7.txt", sep="\t", index=False
)
h14.to_csv(
    "data/" + folderName + "/postAnalysis/hCriteria/h14.txt", sep="\t", index=False
)
