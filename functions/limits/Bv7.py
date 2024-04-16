# import libraries
import sys
import numpy as np

sys.path.append(".")
from functions.utils import round_d


def getPlanLimitsInputs(data, t):
    x = dict()
    x["QM"] = data["QM"][t]
    x["iceInd"] = data["iceInd"][t]
    x["iceIndPrev"] = data["iceInd"][t - 1]
    x["ontFlowPrev"] = data["ontFlow"][t - 1]
    x["obsontNTS"] = data["ontNTS"][t]
    x["sfSupplyNTS"] = data["ontNTS_QM1"][t]
    x["ontLevelStart"] = data["ontLevelBOQ"][t]
    x["kingLevelStart"] = data["kingstonLevel"][t - 1]
    x["ptclaireR"] = data["ptclaireR"][t]
    x["longsaultR"] = data["longsaultR"][t]
    x["saundershwR"] = data["saundershwR"][t]
    x["saunderstwR"] = data["saunderstwR"][t]
    x["foreInd"] = data["foreInd"][t]
    x["sfSlonFlow"] = data["slonFlow_QM1"][t]
    x["slonFlow"] = data["stlouisontOut"][t]

    return x


# takes in supplies and calculates releases/levels
def planLimits(
    qm,
    prelimLevel,
    prelimFlow,
    prelimRegime,
    x,
    septemberRule,
    conv=2970,
    navSeasonStart=12,
    navSeasonEnd=48,
    output="gov",
):
    ontLevel = prelimLevel
    ontFlow = prelimFlow
    ontRegime = prelimRegime
    iceInd = x["iceInd"]
    iceIndPrev = x["iceIndPrev"]
    slonFlow = x["slonFlow"]
    ontFlowPrev = x["ontFlowPrev"]
    obsontNTS = x["obsontNTS"]
    sfSupplyNTS = x["sfSupplyNTS"]
    ontLevelStart = x["ontLevelStart"]
    # kingLevelStart = x["kingLevelStart"]
    kingLevelStart = ontLevelStart - 0.03
    ptclaireR = x["ptclaireR"]
    longsaultR = x["longsaultR"]
    saundershwR = x["saundershwR"]
    saunderstwR = x["saunderstwR"]
    foreInd = x["foreInd"]
    sfSlonFlow = x["sfSlonFlow"]

    # -----------------------------------------------------------------------------
    #
    # I limit - ice stability
    #
    # maximum i-limit flow check. ice status of 0, 1, and 2 correspond to no ice,
    # stable ice formed, and unstable ice forming
    #
    # -----------------------------------------------------------------------------

    iLimFlow = 0

    if iceInd == 2 or iceIndPrev == 2:
        iLimFlow = 704  # updated 4/9 for GLAM Phase 2
        # iLimFlow = 623

    elif iceInd == 1 or (qm < navSeasonStart or qm > navSeasonEnd):
        # calculate release to keep long sault level above 71.8 m
        con1 = (kingLevelStart - 62.40) ** 2.2381
        con2 = ((kingLevelStart - 71.80) / longsaultR) ** 0.3870
        qx = (22.9896 * con1 * con2) * 0.10
        iLimFlow = round_d(qx, 0)

    # added from iceReg
    if iceInd == 1:
        if iLimFlow > 943.0:
            iLimFlow = 943.0
    elif iceInd == 0 and iceIndPrev == 1 and (qm > navSeasonStart or qm < navSeasonEnd):
        # else:
        if iLimFlow > 991.0:
            iLimFlow = 991.0

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
    if qm >= navSeasonStart and qm <= navSeasonEnd:
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
            * (((kingstonLevel - longSaultmin) / round_d(longsaultR, 3)) ** d)
        )

        lFlow2 = round_d(lFlow2, 0)
        # lFlow2 = engRound(lFlow2, 1)

        if lFlow2 < lFlow:
            lRegime = "LS"
            lFlow = lFlow2

    # non-navigation season
    else:
        lRegime = "LM"
        lFlow = 1150.0

    # channel capacity check
    lFlow3 = (747.2 * (ontLevel - 69.10) ** 1.47) / 10.0
    if lFlow3 < lFlow:
        lFlow = lFlow3
        lRegime = "LC"

    lLimFlow = round_d(lFlow, 0)

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

    mq = 0
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
        # mq1 = 577.0 - (slonFlow * 0.1)
        mq2 = slope * (ontLevel - adj - 69.474) ** 1.5
        # mq = min(mq1, mq2)
        mq = mq2

    mLimFlow = round_d(mq, 0)
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

    jLimFlowUpper = 9999
    jLimFlowLower = -9999

    # increase upper j-limit if high lake ontario level and no ice
    if ontLevel > 75.20 and iceInd == 0 and iceIndPrev < 2:
        jup = 142

    # if flow difference is positive, check if maxJ applies
    if ontFlow >= ontFlowPrev:
        # upper J limit applies
        if flowdif > jup:
            jLimFlowUpper = ontFlowPrev + jup
            jFlow = jLimFlowUpper
            if jup == 70:
                jRegime = "J+"
            else:
                jRegime = "J*"

        # no jlim is applied, flow is RC flow
        else:
            jFlow = ontFlow
            jRegime = ontRegime

    # if the flow difference is negative, check if minJ applies
    else:
        # lower J limit applies
        if flowdif > jdn:
            jLimFlowLower = ontFlowPrev - jdn
            jFlow = jLimFlowLower
            jRegime = "J-"

        # no jlim is applied, flow is RC flow
        else:
            jFlow = ontFlow
            jRegime = ontRegime

    # jLimFlow = round(jFlow, 0)
    jLimFlow = jFlow

    # -----------------------------------------------------------------------------
    # limit comparison
    # -----------------------------------------------------------------------------

    # this is either the J-limit (if applied) or the RC flow and regime
    limFlow = jLimFlow
    limRegime = jRegime

    # compare I Limit (MAX)
    if iLimFlow != 0:  # does not apply if zero
        if limFlow > iLimFlow:
            limFlow = iLimFlow
            limRegime = "I"

    # compare L limit (MAX)
    if limFlow > lLimFlow:
        limFlow = lLimFlow
        if septemberRule != "off" and lRegime == "LN":
            limRegime = "L+"
        else:
            limRegime = lRegime

    # compare M Limit (MIN)
    if limFlow < mLimFlow:
        if iLimFlow != 0:
            ont_flw_plan = min(
                max(mLimFlow, jLimFlowLower), iLimFlow, jLimFlowUpper, lLimFlow
            )

            if ont_flw_plan == iLimFlow:
                limFlow = iLimFlow
                limRegime = iRegime

            if ont_flw_plan == mLimFlow:
                limFlow = mLimFlow
                limRegime = mRegime

            if ont_flw_plan == lLimFlow:
                limFlow = mLimFlow
                limRegime = mRegime

        else:
            limFlow = mLimFlow
            limRegime = mRegime

    # update ontFlow and ontRegime post limit check
    ontFlow = limFlow
    ontRegime = limRegime

    # compute averaged quarter-monthly release using forecasted nts
    # dif1 = round((sfSupplyNTS / 10 - ontFlow) / conv, 6)
    # ontLevelEOQ = round(ontLevelStart + dif1, 2)

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
    # calculate pointe claire level
    # estimate flow required to maintain pointe claire below action level

    if foreInd == 1:
        stlouisFlow = ontFlow * 10.0 + sfSlonFlow
        ptclaireLevel = round_d(16.57 + ((ptclaireR * stlouisFlow / 604.0) ** 0.58), 2)
        flimFlow = round_d((c1 / ptclaireR - sfSlonFlow) / 10.0, 0)
    else:
        stlouisFlow = ontFlow * 10.0 + slonFlow
        ptclaireLevel = round_d(16.57 + ((ptclaireR * stlouisFlow / 604.0) ** 0.58), 2)
        flimFlow = round_d((c1 / ptclaireR - slonFlow) / 10.0, 0)

    if (ptclaireLevel > actionlev) and (ontFlow > flimFlow):
        # if flimFlow < ontFlow:
        ontFlow = flimFlow
        ontRegime = "F"

    # -----------------------------------------------------------------------------
    #
    # Minimum Head Limit - ADDED 4/9 FOR GLAM PHASE 2 EFFORTS
    # from : https://github.com/cc-hydrosub/GLRRM-Ontario/blob/main/glrrm/ontario/plan2014/strategies/min_head_limit_strategies.py
    # from Halya: Given the 2020 experience with minimum NYPA net head, add a
    # constraint that limits the minimum net head to 22.5m on a quarter-monthly mean
    # basis. Previously, operational adjustments were made to reflect the minimum head
    # required by NYPA. This would be a last check after the near-final flow is
    # calculated and will be applied to both Bv7 and Plan 2014. Note that Bv7 does not
    # reach this limit in the historical “basis of comparison” dataset so this will not
    # affect the Orders tests.
    #
    # -----------------------------------------------------------------------------

    # ontFlow is semi-final flow - calculate level difference with observed NTS
    dif2 = ((obsontNTS / 10) - ontFlow) / conv
    ontLevel_EOQ_unrounded = ontLevelStart + dif2
    ontLevel_MLV = round_d((ontLevelStart + ontLevel_EOQ_unrounded) * 0.5, 2)

    # set constants
    iters = 12
    head_min = 22.50
    tolerence = 0.02  # tolerence for difference between head and min head
    flw_increment = 300  # 300 cms flow change ~ 0.02m headwater change

    # initialize variables
    flw_new = ontFlow
    ont_mlv_new = ontLevel_MLV
    dif = dif2

    for i in range(iters):
        # flow to maintain minimum head is calculated iteratively iterate until
        # satisfactory flow found or 'iters' iterations kingston level
        king_new = ont_mlv_new - 0.03
        difLev = king_new - 62.40

        # calculate Saunders headwater level
        saundershwLevel1 = round_d(
            king_new
            - (
                saundershwR
                * pow(
                    (flw_new * 10) / (21.603 * pow(difLev, 2.2586)),
                    (1 / 0.3749),
                )
            ),
            2,
        )

        if saundershwLevel1 > 73.87:
            if iceInd == 2 or iceIndPrev == 2:
                sahw_new = saundershwLevel1
            else:
                sahw_new = 73.783
        else:
            sahw_new = saundershwLevel1

        # calculate interational tailwater level
        intw_level_new = round_d(
            44.50 + 0.006338 * pow((saunderstwR * flw_new * 10), 0.7158),
            2,
        )

        # calculate head for this iteration
        head_new = sahw_new - intw_level_new

        if head_new < (head_min - tolerence):
            flw_loop = flw_new + flw_increment * (head_new - head_min) / 10
            flw_loop = round_d(flw_loop, 0)
            dif = ((obsontNTS / 10) - flw_loop) / conv
            ont_elv_loop = ontLevelStart + dif
            ont_mlv_new = round((ontLevelStart + ont_elv_loop) * 0.5, 2)
            flw_new = flw_loop
        else:
            flow_MH = flw_new
            break

        flow_MH = flw_loop

    if ontFlow > flow_MH:
        #     MH_applies = True
        # else:
        #     MH_applies = False

        # # Compare minimum head limit
        # if MH_applies:
        ontFlow = flow_MH
        ontRegime = "MH"

    if output == "gov":
        return {"ontFlow": ontFlow, "ontRegime": ontRegime}
    elif output == "all":
        return {
            "ontFlow": ontFlow,
            "ontRegime": ontRegime,
            "iFlow": iLimFlow,
            "lFlow": lLimFlow,
            "lRegime": lRegime,
            "mFlow": mLimFlow,
            "jFlow": jLimFlow,
            "jRegime": jRegime,
            "fFlow": flimFlow,
            "mhFlow": flow_MH,
        }
