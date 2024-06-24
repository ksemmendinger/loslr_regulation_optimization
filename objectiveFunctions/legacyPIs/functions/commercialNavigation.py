#!/usr/bin/env python3

import numpy as np
import pandas as pd

# -----------------------------------------------------------------------------
# commercial navigation costs ($)
# -----------------------------------------------------------------------------

# load loading cost databases
ontarioLoadingCostDatabase = pd.read_csv(
    "objectiveFunctions/legacyPIs/data/cnOntarioLoadingCosts.csv"
)
ontarioLoadingCostDatabase = {
    x: ontarioLoadingCostDatabase[x].values for x in ontarioLoadingCostDatabase
}

seawayLoadingCostDatabase = pd.read_csv(
    "objectiveFunctions/legacyPIs/data/cnSeawayLoadingCosts.csv"
)
seawayLoadingCostDatabase = {
    x: seawayLoadingCostDatabase[x].values for x in seawayLoadingCostDatabase
}

montrealLoadingCostDatabase = pd.read_csv(
    "objectiveFunctions/legacyPIs/data/cnMontrealLoadingCosts.csv"
)
montrealLoadingCostDatabase = {
    x: montrealLoadingCostDatabase[x].values for x in montrealLoadingCostDatabase
}


# returns total transportation cost for Lake Ontario, the Seaway, and Montreal in USD
def piModel(
    qm,
    ontLevel,
    kingstonLevel,
    ogdensburgLevel,
    cardinalLevel,
    iroquoishwLevel,
    iroquoistwLevel,
    morrisburgLevel,
    longsaultLevel,
    summerstownLevel,
    ptclaireLevel,
    stlambertLevel,
    jetty1Level,
    jettyChange,
    sorelLevel,
    troisrivieresLevel,
    ontFlow,
    iceInd,
    freshetIndicator,
    freshetIndicatorPrevious,
    rPW,
    conPW,
    prevconPW,
    ontarioLoadingCostDatabase,
    seawayLoadingCostDatabase,
    montrealLoadingCostDatabase,
):
    # qm: quarter month (int)
    # ontLevel: final lake ontario level (float)
    # kingstonLevel: final kingston level (float)
    # ogdensburgLevel: final ogdensburg level (float)
    # cardinalLevel: final cardinal level (float)
    # iroquoishwLevel: final iroquois headwaters level (float)
    # iroquoistwLevel: final iroquois tailwaters level (float)
    # morrisburgLevel: final morrisburg level (float)
    # longsaultLevel: final long sault level (float)
    # summerstownLevel: final summerstown level (float)
    # ptclaireLevel: final pointe-claire level (float)
    # stlambertLevel: final st. lambert level (float)
    # jetty1Level: final montreal harbour level (float)
    # jettyChange: change from previous qm's jetty level (float)
    # sorelLevel: final sorel level (float)
    # troisrivieresLevel: final trois rivieres level (float)
    # ontFlow: final moses-saunders release (float)
    # iceInd: ice status (int)
    # freshetIndicator: freshet indicator (float)
    # freshetIndicatorPrevious: previous freshet indicator (float)
    # rPW: rounded percent waiting (float) - calculated in for loop
    # conPW: constrained waiting percentage (float) - calculated in for loop
    # prevconPW: previous constrained waiting percentage (float) - calculated in for loop
    # ontarioLoadingCostDatabase: loading costs on Lake Ontario by water level and quartermonth (dict)
    # seawayLoadingCostDatabase: loading costs on the Seaway by water level and quartermonth (dict)
    # montrealLoadingCostDatabase: loading costs downstream of Montreal by water level and quartermonth (dict)

    # constant for conversions
    daysperQM = 7.609

    # set navigation season status based on qm
    # if qm <= 12 or qm == 48:
    if qm < 12:  # changed nav season for Phase 2 to QM [12, 48] inclusive
        navStatus = 0
    else:
        navStatus = 1

    # calculate available gage depths for each location (exclude downstream of pt. claire)
    ontGage = ontLevel - 74.27
    ogdensburgGage = ogdensburgLevel - 73.9
    cardinalGage = cardinalLevel - 73.45
    iroquoishwGage = iroquoishwLevel - 73.26
    morrisburgGage = morrisburgLevel - 72.79
    longsaultGage = longsaultLevel - 72.5
    summerstownGage = summerstownLevel - 46.58
    ptclaireGage = ptclaireLevel - 20.6
    stlambertGage = stlambertLevel - 4.87
    jetty1Gage = jetty1Level - 5.55
    sorelGage = sorelLevel - 3.78
    troisrivieresGage = troisrivieresLevel - 2.9

    # calculate control depths
    ontarioControlDepth = round(
        min(
            ontGage,
            ogdensburgGage,
            cardinalGage,
            iroquoishwGage,
            morrisburgGage,
            longsaultGage,
            summerstownGage,
            ptclaireGage,
            stlambertGage,
        ),
        2,
    )
    montrealControlDepth = round(min(jetty1Gage, sorelGage, troisrivieresGage), 2)

    # ---------------------------------
    # loading cost
    # ---------------------------------

    # loading costs are stored in a database with the control depth as rows
    # and quarter-month as columns. in excel, the prior qm is used for lake
    # ontario, but the same qm is used for the seaway and montreal

    # lake ontario
    if qm == 1:
        ontarioLookupQM = 48
    else:
        ontarioLookupQM = qm - 1

    gageInd = np.argmin(
        # abs(ontarioControlDepth - np.asarray(ontarioLoadingCostDatabase["gageDepth"]))
        abs(ontarioControlDepth - ontarioLoadingCostDatabase["gageDepth"])
    )

    ontarioLoadingCost = (
        navStatus * ontarioLoadingCostDatabase[str(ontarioLookupQM)][gageInd]
    )

    # seaway
    gageInd = np.argmin(
        # abs(ontarioControlDepth - np.asarray(seawayLoadingCostDatabase["gageDepth"]))
        abs(ontarioControlDepth - seawayLoadingCostDatabase["gageDepth"])
    )
    seawayLoadingCost = navStatus * seawayLoadingCostDatabase[str(qm)][gageInd]

    # montreal
    gageInd = np.argmin(
        # abs(montrealControlDepth - np.asarray(montrealLoadingCostDatabase["gageDepth"]))
        abs(montrealControlDepth - montrealLoadingCostDatabase["gageDepth"])
    )
    montrealLoadingCost = montrealLoadingCostDatabase[str(qm)][gageInd]

    # ---------------------------------
    # gradient cost calculations [seaway only]
    # ---------------------------------

    # set GC equal to 1 to include gradient costs
    GC = 1

    # morrisburg to long sault dam
    aGradient = morrisburgLevel - longsaultLevel
    if aGradient < 0.3101:
        aGradientPercent = 0
    elif aGradient <= 0.4401:
        aGradientPercent = -2.2 + (7.26 * aGradient)
    else:
        aGradientPercent = 1

    # cardinal to iroquois hw
    bGradient = cardinalLevel - iroquoishwLevel
    if bGradient < 0.2501:
        bGradientPercent = 0
    elif bGradient <= 0.2901:
        bGradientPercent = -4.57 + (18.6 * bGradient)
    else:
        bGradientPercent = 1

    # ogdensburg to cardinal
    cGradient = ogdensburgLevel - cardinalLevel
    if cGradient < 0.6901:
        cGradientPercent = 0
    elif cGradient <= 0.8201:
        cGradientPercent = -4.83 + (7.06 * cGradient)
    else:
        cGradientPercent = 1

    # morrisburg to iroquois tw
    dGradient = morrisburgLevel - iroquoistwLevel
    if dGradient >= (0.4601 - 0.017):
        dGradientPercent = 0.125
    else:
        dGradientPercent = 0

    # gradient percent for the seaway
    if ontFlow > 1105:
        seawayGradientPercent = 1
    elif ontFlow > 1070:
        seawayGradientPercent = 0.784286
    elif ontFlow > 991:
        seawayGradientPercent = 0.285714
    elif max(aGradientPercent, bGradientPercent, cGradientPercent, dGradientPercent) < (
        1 / daysperQM
    ):
        seawayGradientPercent = 0
    else:
        seawayGradientPercent = min(
            (2 / daysperQM),
            max(aGradientPercent, bGradientPercent, cGradientPercent, dGradientPercent),
        )

    if GC == 1:
        if seawayGradientPercent > 0:
            adjFactor = 0.25
        else:
            adjFactor = 1
    else:
        adjFactor = 1

    # delay costs per quarter-month
    delayCostsbyQM = [
        14121,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        14796,
        387887,
        1020838,
        915520,
        2016446,
        1183890,
        1568582,
        1046195,
        1950220,
        1506857,
        1520650,
        986641,
        2160791,
        1540279,
        1554758,
        1004954,
        2079677,
        1659694,
        1605915,
        952509,
        2169973,
        1761208,
        1835476,
        1028129,
        2161385,
        1598640,
        1837194,
        1286616,
        2500019,
        2040167,
        2080052,
        1235638,
        2751089,
        1675603,
        2010125,
        1036886,
        1983077,
        133317,
    ]

    # seaway gradient costs calculation
    if GC == 1:
        if iceInd > 0:
            seawayGradientCost = 0
        else:
            seawayGradientCost = (
                0.5
                * seawayGradientPercent
                * delayCostsbyQM[qm - 1]
                * daysperQM
                * navStatus
            )
    else:
        seawayGradientCost = 0

    # ---------------------------------
    # waiting costs
    # ---------------------------------

    # ----------
    # estimate additional ship rental time because of waiting delays

    # % of ships delayable at 8 metres
    if qm < 16 or qm > 40:
        perShipsDelayable = 0.45
    else:
        perShipsDelayable = 0.58

    # additional % of ships delayable below 8 metres
    if ontarioControlDepth > 0:
        addShipsDelayable = 0
    elif ontarioControlDepth > -0.1001:
        addShipsDelayable = 0.04
    elif ontarioControlDepth > -0.2001:
        addShipsDelayable = 0.07
    elif ontarioControlDepth > -0.3001:
        addShipsDelayable = 0.09
    elif ontarioControlDepth > -0.4001:
        addShipsDelayable = 0.11
    elif ontarioControlDepth > -0.5001:
        addShipsDelayable = 0.2
    elif ontarioControlDepth > -0.6001:
        addShipsDelayable = 0.26
    elif ontarioControlDepth > -0.7001:
        addShipsDelayable = 0.33
    else:
        addShipsDelayable = 1 - perShipsDelayable

    # % ships delayable: assumption was made and accepted by Nav TWG based on
    # Lauga model that only half of ships that could be delayed actually are
    # delayed, so the count = one-half times the numberof ships times the %
    # that could be delayed
    shipsDelayable = (perShipsDelayable + addShipsDelayable) * 0.5

    # seaway ship count each QM (data series)
    shipCountperQM = [
        0.4,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        1.2,
        15,
        37,
        33.6,
        80.8,
        48,
        64.2,
        39.8,
        81.4,
        60.6,
        61.2,
        37,
        87.8,
        61.4,
        61.4,
        39,
        85.6,
        65,
        63,
        39.2,
        89.4,
        70.8,
        71.2,
        41.4,
        87.4,
        65.6,
        73.8,
        51,
        98,
        82.4,
        83,
        51.8,
        118.6,
        73,
        81.8,
        40.2,
        80.6,
        4.4,
    ]

    # count of delayed ships
    delayedShips = shipsDelayable * shipCountperQM[qm - 1]

    # total seaway waiting costs
    if prevconPW > 0:
        seawayWaitingCost = 0
    else:
        seawayWaitingCost = (
            navStatus * delayCostsbyQM[qm - 1] * conPW * shipsDelayable * adjFactor
        )

    # prevconPW = conPW

    # ----------
    # estimate costs to move cargo on smaller ships if the wait is longer than 2 days

    # number of ships unloaded
    if round(conPW, 5) == round((2 / daysperQM), 5):
        shipsUnloaded = rPW * shipCountperQM[qm - 1] * shipsDelayable
    else:
        shipsUnloaded = 0

    # port call ($)
    portCall = shipsUnloaded * 10000

    # reloading costs
    reloadingCosts = 6321 * shipsUnloaded * 0.05 * 60

    # total reshipment costs
    if seawayWaitingCost == 0:
        seawayReshipmentCosts = 0
    else:
        seawayReshipmentCosts = navStatus * (portCall + reloadingCosts)

    # add waiting and reship costs
    seawayDelayCosts = seawayWaitingCost + seawayReshipmentCosts

    # ----------
    # montreal delay costs

    # if ts == 1:
    #     jettyChange = 0
    # else:
    # jettyChange = jetty1Level - jetty1LevelPrevious

    if jettyChange < 0.15:
        montrealDelay = 0
    elif montrealControlDepth > 1:
        montrealDelay = 0
    elif montrealControlDepth < -0.6:
        montrealDelay = 0
    elif freshetIndicator == 1 and freshetIndicatorPrevious == 0:
        montrealDelay = 0
    else:
        montrealDelay = 1

    # montreal delay costs
    montrealDelayCosts = montrealDelay * 75000

    # ---------------------------------
    # speed costs [seaway only]
    # ---------------------------------

    # seaway speed warning costs
    if ontarioControlDepth < 0.5 or ontarioControlDepth > 2:
        seawaySpeedCost = float(0.04 * navStatus * seawayLoadingCost)
    else:
        seawaySpeedCost = 0

    # ----------
    # total costs by reach

    # lake ontario
    ontarioTotalCost = round(float(ontarioLoadingCost), 0)

    # seaway
    seawayTotalCost = round(
        float(
            seawayLoadingCost + seawayDelayCosts + seawaySpeedCost + seawayGradientCost
        ),
        0,
    )

    # montreal
    montrealTotalCost = round(float(montrealLoadingCost + montrealDelayCosts), 0)

    # sum up costs
    totalTransportationCost = ontarioTotalCost + seawayTotalCost + montrealTotalCost
    totalTransportationCost = float(totalTransportationCost)

    return totalTransportationCost, ontarioTotalCost, seawayTotalCost, montrealTotalCost


def runModel(data):
    # returns total transportation cost for Lake Ontario and the Seaway in USD
    keys = [
        "Sim",
        "Year",
        "Month",
        "QM",
        "ontLevel",
        "kingstonLevel",
        "ogdensburgLevel",
        "cardinalLevel",
        "iroquoishwLevel",
        "iroquoistwLevel",
        "morrisburgLevel",
        "longsaultLevel",
        "summerstownLevel",
        "ptclaireLevel",
        "stlambertLevel",
        "jetty1Level",
        "sorelLevel",
        "troisrivieresLevel",
        "ontFlow",
        "iceInd",
        "freshetIndicator",
    ]
    # cn = pd.DataFrame(dict((k, data[k]) for k in keys if k in data))
    piOutput = dict((k, data[k]) for k in keys if k in data)

    # calculate the difference in jetty1 levels between qms
    piOutput["jettyChange"] = np.diff(
        piOutput["jetty1Level"], prepend=piOutput["jetty1Level"][0]
    )

    # get previous freshet values
    piOutput["freshetIndicatorPrevious"] = np.roll(piOutput["freshetIndicator"], 1)
    piOutput["freshetIndicatorPrevious"][0] = np.nan

    # initialize rows
    timesteps = len(piOutput["Sim"])
    piOutput["rPW"] = np.array([np.nan] * timesteps)
    piOutput["conPW"] = np.array([np.nan] * timesteps)

    # convert to dictionary for faster lookup
    # cn = {x: cn[x].values for x in cn}

    # constant for conversions
    daysperQM = 7.609

    for i in range(timesteps):
        # kingstonLevel = cn.loc[i, "kingstonLevel"]
        # ogdensburgLevel = cn.loc[i, "ogdensburgLevel"]
        # cardinalLevel = cn.loc[i, "cardinalLevel"]
        # iroquoishwLevel = cn.loc[i, "iroquoishwLevel"]
        # iroquoistwLevel = cn.loc[i, "iroquoistwLevel"]
        # morrisburgLevel = cn.loc[i, "morrisburgLevel"]
        # longsaultLevel = cn.loc[i, "longsaultLevel"]
        # summerstownLevel = cn.loc[i, "summerstownLevel"]
        # ptclaireLevel = cn.loc[i, "ptclaireLevel"]

        kingstonLevel = piOutput["kingstonLevel"][i]
        ogdensburgLevel = piOutput["ogdensburgLevel"][i]
        cardinalLevel = piOutput["cardinalLevel"][i]
        iroquoishwLevel = piOutput["iroquoishwLevel"][i]
        iroquoistwLevel = piOutput["iroquoistwLevel"][i]
        morrisburgLevel = piOutput["morrisburgLevel"][i]
        longsaultLevel = piOutput["longsaultLevel"][i]
        summerstownLevel = piOutput["summerstownLevel"][i]
        ptclaireLevel = piOutput["ptclaireLevel"][i]

        # ----------
        # waiting percentage for depth at each seaway gage

        # kingston
        if kingstonLevel > 74.3801:
            kingstonWaitingPercentage = 0
        elif kingstonLevel >= 74.0101:
            kingstonWaitingPercentage = 2.581 * (74.39 - kingstonLevel)
        else:
            kingstonWaitingPercentage = 1

        # ogdensburg
        if ogdensburgLevel > 74.0501:
            ogdensburgWaitingPercentage = 0
        elif ogdensburgLevel >= 73.7201:
            ogdensburgWaitingPercentage = 2.906 * (74.06 - ogdensburgLevel)
        else:
            ogdensburgWaitingPercentage = 1

        # cardinal
        if cardinalLevel > 73.5701:
            cardinalWaitingPercentage = 0
        elif cardinalLevel >= 73.2901:
            cardinalWaitingPercentage = 3.421 * (73.58 - cardinalLevel)
        else:
            cardinalWaitingPercentage = 1

        # iroquois
        if iroquoishwLevel > 73.4701:
            iroquoisWaitingPercentage = 0
        elif iroquoishwLevel >= 73.1101:
            iroquoisWaitingPercentage = 7.63 * pow((73.47 - iroquoishwLevel), 2)
        else:
            iroquoisWaitingPercentage = 1

        # morrisburg
        if morrisburgLevel > 73.1001:
            morrisburgWaitingPercentage = 0
        elif morrisburgLevel >= 72.6801:
            morrisburgWaitingPercentage = 13.5 * pow((73.1 - morrisburgLevel), 3)
        else:
            morrisburgWaitingPercentage = 1

        # long sault
        if longsaultLevel > 72.9001:
            longsaultWaitingPercentage = 0
        elif longsaultLevel >= 72.4301:
            longsaultWaitingPercentage = 19.78 * pow((72.9 - longsaultLevel), 4)
        else:
            longsaultWaitingPercentage = 1

        # summerstown
        if summerstownLevel > 46.6401:
            summerstownWaitingPercentage = 0
        elif summerstownLevel >= 46.5101:
            summerstownWaitingPercentage = 7.763 * (46.64 - summerstownLevel)
        else:
            summerstownWaitingPercentage = 1

        # lac st. louis
        if ptclaireLevel > 20.6501:
            lacstlouisWaitingPercentage = 0
        elif ptclaireLevel >= 20.5301:
            lacstlouisWaitingPercentage = 8.55 * (20.65 - ptclaireLevel)
        else:
            lacstlouisWaitingPercentage = 1

        # ----------
        # what % of the QM will there be restrictive depths?

        # unconstrained percentage quarter-month waiting
        uncPW = max(
            kingstonWaitingPercentage,
            ogdensburgWaitingPercentage,
            cardinalWaitingPercentage,
            iroquoisWaitingPercentage,
            morrisburgWaitingPercentage,
            longsaultWaitingPercentage,
            summerstownWaitingPercentage,
            lacstlouisWaitingPercentage,
        )

        # rounded unconstrained percentage quarter-month waiting
        if abs(100 * uncPW) - 0.5 == int(abs(100 * uncPW)):
            if (int(100 * uncPW) % 2) == 0:
                rPW = int(100 * uncPW) / 100
            else:
                rPW = (int(100 * uncPW) + 1) / 100
        else:
            rPW = round(uncPW, 2)

        # constrained % of quarter-months waiting for depth each QM
        conPW = min(rPW, 2 / daysperQM)

        # cn.loc[i, "rPW"] = rPW
        # cn.loc[i, "conPW"] = conPW
        piOutput["rPW"][i] = rPW
        piOutput["conPW"][i] = conPW

    # cn = pd.DataFrame(cn)
    piOutput["prevconPW"] = np.roll(piOutput["conPW"], 1)
    piOutput["prevconPW"][0] = 0

    piOutput = pd.DataFrame(piOutput)

    piOutput[
        [
            "totalCommercialNavigation",
            "ontarioCommercialNavigation",
            "seawayCommercialNavigation",
            "montrealCommercialNavigation",
        ]
    ] = np.array(
        [
            piModel(
                qm,
                ontLevel,
                kingstonLevel,
                ogdensburgLevel,
                cardinalLevel,
                iroquoishwLevel,
                iroquoistwLevel,
                morrisburgLevel,
                longsaultLevel,
                summerstownLevel,
                ptclaireLevel,
                stlambertLevel,
                jetty1Level,
                jettyChange,
                sorelLevel,
                troisrivieresLevel,
                ontFlow,
                iceInd,
                freshetIndicator,
                freshetIndicatorPrevious,
                rPW,
                conPW,
                prevconPW,
                ontarioLoadingCostDatabase,
                seawayLoadingCostDatabase,
                montrealLoadingCostDatabase,
            )
            for (
                qm,
                ontLevel,
                kingstonLevel,
                ogdensburgLevel,
                cardinalLevel,
                iroquoishwLevel,
                iroquoistwLevel,
                morrisburgLevel,
                longsaultLevel,
                summerstownLevel,
                ptclaireLevel,
                stlambertLevel,
                jetty1Level,
                jettyChange,
                sorelLevel,
                troisrivieresLevel,
                ontFlow,
                iceInd,
                freshetIndicator,
                freshetIndicatorPrevious,
                rPW,
                conPW,
                prevconPW,
            ) in zip(
                piOutput["QM"],
                piOutput["ontLevel"],
                piOutput["kingstonLevel"],
                piOutput["ogdensburgLevel"],
                piOutput["cardinalLevel"],
                piOutput["iroquoishwLevel"],
                piOutput["iroquoistwLevel"],
                piOutput["morrisburgLevel"],
                piOutput["longsaultLevel"],
                piOutput["summerstownLevel"],
                piOutput["ptclaireLevel"],
                piOutput["stlambertLevel"],
                piOutput["jetty1Level"],
                piOutput["jettyChange"],
                piOutput["sorelLevel"],
                piOutput["troisrivieresLevel"],
                piOutput["ontFlow"],
                piOutput["iceInd"],
                piOutput["freshetIndicator"],
                piOutput["freshetIndicatorPrevious"],
                piOutput["rPW"],
                piOutput["conPW"],
                piOutput["prevconPW"],
            )
        ]
    )

    piOutput = piOutput[
        [
            "Sim",
            "Year",
            "Month",
            "QM",
            "totalCommercialNavigation",
            "ontarioCommercialNavigation",
            "seawayCommercialNavigation",
            "montrealCommercialNavigation",
        ]
    ]

    return piOutput
