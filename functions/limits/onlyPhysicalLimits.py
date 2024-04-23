"""
-------------------------------------------------------------------------------
only flow limits not intrinsically represented in the objective function models
are included. this script includes the I-limit and the MH-limit.
-------------------------------------------------------------------------------
"""

# import custom function for engineering rounding
import sys

sys.path.append(".")
from functions.utils import round_d


def getPlanLimitsInputs(data, t):
    x = dict()
    x["QM"] = data["QM"][t]
    x["iceInd"] = data["iceInd"][t]
    x["iceIndPrev"] = data["iceInd"][t - 1]
    x["obsontNTS"] = data["ontNTS"][t]
    x["ontLevelStart"] = data["ontLevelBOQ"][t]
    x["kingLevelStart"] = data["kingstonLevel"][t - 1]
    x["longsaultR"] = data["longsaultR"][t]
    x["saundershwR"] = data["saundershwR"][t]
    x["saunderstwR"] = data["saunderstwR"][t]

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
    # ontLevel = prelimLevel
    ontFlow = prelimFlow
    ontRegime = prelimRegime
    iceInd = x["iceInd"]
    iceIndPrev = x["iceIndPrev"]
    obsontNTS = x["obsontNTS"]
    ontLevelStart = x["ontLevelStart"]
    kingLevelStart = ontLevelStart - 0.03
    longsaultR = x["longsaultR"]
    saundershwR = x["saundershwR"]
    saunderstwR = x["saunderstwR"]

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

    # if release function flow is greater than I-limit, set flow to I-limit
    if iLimFlow != 0:  # does not apply if zero
        if ontFlow > iLimFlow:
            ontFlow = iLimFlow
            ontRegime = iRegime

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
        ontFlow = flow_MH
        ontRegime = "MH"

    if output == "gov":
        return {"ontFlow": ontFlow, "ontRegime": ontRegime}
    elif output == "all":
        return {
            "ontFlow": ontFlow,
            "ontRegime": ontRegime,
            "iFlow": iLimFlow,
            "mhFlow": flow_MH,
        }
