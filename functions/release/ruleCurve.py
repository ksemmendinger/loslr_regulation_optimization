import sys
import numpy as np
from typing import List, Dict, Union

sys.path.append(".")
from functions.utils import round_d


# take in list, output dict with keys as parameter names
def formatDecisionVariables(vars: List[float], **args) -> Dict[str, float]:
    # create empty dictionary to save formatted dvs
    pars = dict()

    # long forecast decision variables
    pars["wetIndicatorThreshold"] = vars[0]
    pars["wetConfidenceThreshold"] = vars[1]

    # wet rule curve decision variables
    pars["C1"] = vars[2]
    pars["C1*"] = vars[2] + vars[3]
    pars["P1"] = vars[4]

    # dry rule curve decision variables
    pars["C2"] = vars[5]
    pars["P2"] = vars[6]

    # dry flow adjustment decision variables
    pars["dryLevelThreshold"] = vars[7]
    pars["dryFlowAdjustment"] = vars[8]

    return pars


# take in dict of hydrologic data and timeslice, output list of inputs for releaseFunction
def getReleaseFunctionInputs(
    data: Dict[str, np.ndarray], t: int, **args
) -> Dict[str, float]:
    # extract hydrologic variables from input dictionary
    lfSupply = data["forNTS"][t]
    ontLevelBOQ = data["ontLevelBOQ"][t]
    # annavgLevel = round_d(np.mean(data["ontLevelMOQ"][(t - 48) : (t)]), 2)
    annavgLevel = np.mean(data["ontLevelMOQ"][(t - 48) : (t)])
    sfSupplyNTS = [
        data["ontNTS_QM1"][t],
        data["ontNTS_QM2"][t],
        data["ontNTS_QM3"][t],
        data["ontNTS_QM4"][t],
    ]

    x = dict()
    x["forNTS"] = lfSupply
    x["ontLevelBOQ"] = ontLevelBOQ
    x["annavgLevel"] = annavgLevel
    x["sfSupplyNTS"] = sfSupplyNTS

    return x


# takes in output from formatDecisionVariables and getInputs, outputs release and flow regime
def releaseFunction(
    x: Dict[str, float],
    pars: Dict[str, float],
    conv=2970,
    **args,
) -> Dict[str, Union[float, str]]:
    # extract hydrologic variables from input dictionary
    lfSupply = x["forNTS"]
    ontLevelBOQ = x["ontLevelBOQ"]
    annavgLevel = x["annavgLevel"]
    sfSupplyNTS = x["sfSupplyNTS"]

    # -------------------------------------------------------------------------
    # set forecast indicator and confidence [long forecast subroutine]
    # -------------------------------------------------------------------------

    # simplified formulation to determine if wet and confident
    wet = pars["wetIndicatorThreshold"]
    low99limit = lfSupply - pars["wetConfidenceThreshold"]

    lfInd = np.nan
    lfCon = np.nan

    # if the supply index is greater than the wet threshold
    if lfSupply > wet:
        lfInd = 1
        # if lower confidence interval is greater than the wet threshold
        if low99limit >= wet:
            lfCon = 3
    # else:
    #     lfInd = np.nan
    #     lfCon = np.nan

    # -------------------------------------------------------------------------
    # rule curve [short forecast and balance subroutine]
    # -------------------------------------------------------------------------

    # calculate rule curve release for each forecasted quarter-month (1 - 4)
    nforecasts = 4
    startLev = []
    startLev.append(ontLevelBOQ)
    endLev = []
    sfFlow = []
    sfpreprojFlow = []
    sfRegime = []
    ruleCurveAdj = []

    for k in range(nforecasts):
        # set constants and indicators
        slope = 55.5823
        ice = 0
        adj = 0.0014 * (2010 - 1985)
        epsolon = 0.0001

        # while loop and break variables
        iters = 10
        lastflow = 0

        ont_blv = startLev[k]
        for i in range(iters):
            # only exits loop once a convergence threshold (epsolon) is met or 10
            # iterations exceeded. adjust the preproject relationship by how much the
            # long-term supply forecast varies from average

            # pre-project flows
            preproj = slope * (ont_blv - adj - 69.474) ** 1.5

            # above average supplies
            if lfSupply >= 7011.0:
                # set c1 coefficients based on how confident forecast is in wet
                if lfInd == 1 and lfCon == 3:
                    c1 = pars["C1*"]
                    sy = "RCW*"
                else:
                    c1 = pars["C1"]
                    sy = "RCW"
                p1 = pars["P1"]

                # rule curve release
                rc = c1 * ((lfSupply - 7011.0) / (8552.0 - 7011.0)) ** p1
                flow = preproj + rc

            # below average supplies
            if lfSupply < 7011.0:
                # set c2 coefficient
                c2 = pars["C2"]
                p2 = pars["P2"]
                sy = "RCD"

                # rule curve release
                rc = c2 * ((7011.0 - lfSupply) / (7011.0 - 5717.0)) ** p2
                flow = preproj - rc

            # adjust release for any ice
            # release = round(flow - ice, 0)
            release = round_d(flow, 0)

            if abs(release - lastflow) <= epsolon:
                break

            # compute water level change using forecasted supply and flow
            # dif1 = (sfSupplyNTS[k] / 10 - release) / conv
            endLev_new = startLev[k] + (sfSupplyNTS[k] / 10 - release) / conv
            meanLev_new = round_d(((startLev[k] + endLev_new) * 0.5), 2)
            ont_blv = meanLev_new  # GLRRM uses mean level for period but i don't think that is right

            # stability check
            lastflow = release

        # try to keep ontario level up in dry periods
        if annavgLevel <= pars["dryLevelThreshold"]:
            release = release + pars["dryFlowAdjustment"]
            sy = sy + "-"

        sfFlow.append(release)
        sfpreprojFlow.append(preproj)
        ruleCurveAdj.append(rc)
        sfRegime.append(sy)

        # compute water level change using forecasted supply and flow
        dif1 = round_d((sfSupplyNTS[k] / 10 - release) / conv, 6)
        endLev1 = round_d(startLev[k] + dif1, 6)
        endLev.append(endLev1)

        # update intial conditions for next iteration
        if k < list(range(nforecasts))[-1]:
            startLev.append(endLev1)

    # calculate rule curve flow as average of each relase in short forecast
    ontFlow = round_d(sum(sfFlow) / nforecasts, 0)
    ontRegime = sy

    # return all the relevant outputs to save in dataframe
    outputs = dict()
    outputs["rfFlow"] = ontFlow
    outputs["rfRegime"] = ontRegime
    outputs["pprFlow"] = sfpreprojFlow[0]
    outputs["rfOutput"] = ruleCurveAdj[0]

    return outputs
