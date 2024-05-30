#!/usr/bin/env python3

# import libraries
import os
import math
import numpy as np
import pandas as pd

# os.chdir("/Volumes/ky_backup/dps")

# # import test data
# data = pd.read_csv(
#     "/Volumes/ky_backup/dps/output/data/baseline/Bv7/simulation/historic/Bv7/formattedOutput.csv",
#     sep="\t",
# )
# data = pd.read_csv(
#     "/Users/kylasemmendinger/Documents/github/Plan-2014-Python/simulation_model/output/historic/12month/sqAR/historic/S1.txt",
#     sep="\t",
# )
# data = data.drop(labels=["confidence", "indicator"], axis=1)
# data = data.dropna(axis=0).reset_index(drop=True)
# data = {x: data[x].values for x in data}

# load in baseline data for weighting by location
bv7 = pd.read_csv("objectiveFunctions/baselineValues.csv")

# -----------------------------------------------------------------------------
# coastal impacts to buildings [upstream and downstream] (#)
# -----------------------------------------------------------------------------

# load building impacts for upstream and downstream coastal locations
staticOntarioImpacts = pd.read_csv("objectiveFunctions/coastalOntarioStaticImpacts.csv")
staticOntarioImpacts = {x: staticOntarioImpacts[x].values for x in staticOntarioImpacts}

dynamicOntarioImpacts = pd.read_csv(
    "objectiveFunctions/coastalOntarioDynamicImpacts.csv"
)
dynamicOntarioImpacts = {
    x: dynamicOntarioImpacts[x].values for x in dynamicOntarioImpacts
}

staticAlexBayImpacts = pd.read_csv("objectiveFunctions/coastalAlexBayStaticImpacts.csv")
staticAlexBayImpacts = {x: staticAlexBayImpacts[x].values for x in staticAlexBayImpacts}

staticCardinalImpacts = pd.read_csv(
    "objectiveFunctions/coastalCardinalStaticImpacts.csv"
)
staticCardinalImpacts = {
    x: staticCardinalImpacts[x].values for x in staticCardinalImpacts
}

staticBeauImpacts = pd.read_csv("objectiveFunctions/coastalBeauStaticImpacts.csv")
staticBeauImpacts = {x: staticBeauImpacts[x].values for x in staticBeauImpacts}

staticPtClaireImpacts = pd.read_csv(
    "objectiveFunctions/coastalPtClaireStaticImpacts.csv"
)
staticPtClaireImpacts = {
    x: staticPtClaireImpacts[x].values for x in staticPtClaireImpacts
}

staticMaskinongeImpacts = pd.read_csv(
    "objectiveFunctions/coastalMaskinongeStaticImpacts.csv"
)
staticMaskinongeImpacts = {
    x: staticMaskinongeImpacts[x].values for x in staticMaskinongeImpacts
}

staticLacStPierreImpacts = pd.read_csv(
    "objectiveFunctions/coastalLacStPierreStaticImpacts.csv"
)
staticLacStPierreImpacts = {
    x: staticLacStPierreImpacts[x].values for x in staticLacStPierreImpacts
}

staticSorelImpacts = pd.read_csv("objectiveFunctions/coastalSorelStaticImpacts.csv")
staticSorelImpacts = {x: staticSorelImpacts[x].values for x in staticSorelImpacts}

staticTroisRivieresImpacts = pd.read_csv(
    "objectiveFunctions/coastalTroisRivieresStaticImpacts.csv"
)
staticTroisRivieresImpacts = {
    x: staticTroisRivieresImpacts[x].values for x in staticTroisRivieresImpacts
}


# returns the number of buildings impacted upstream and downstream
def coastalImpacts(
    month,
    ontLevel,
    alexbayLevel,
    cardinalLevel,
    lerybeauharnoisLevel,
    ptclaireLevel,
    maskinongeLevel,
    sorelLevel,
    lacstpierreLevel,
    troisrivieresLevel,
    staticOntarioImpacts,
    staticAlexBayImpacts,
    staticCardinalImpacts,
    staticBeauImpacts,
    staticPtClaireImpacts,
    staticMaskinongeImpacts,
    staticLacStPierreImpacts,
    staticSorelImpacts,
    staticTroisRivieresImpacts,
    dynamicOntarioImpacts,
):
    # month: month (int)
    # ontLevel: final lake ontario level (float)
    # alexbayLevel: final alexandria bay level (float)
    # cardinalLevel: final cardinal level (float)
    # lerybeauharnoisLevel: final beauharnois level (float)
    # ptclaireLevel: final pointe-claire level (float)
    # maskinongeLevel: final maskinonge level (float)
    # sorelLevel: final sorel level (float)
    # lacstpierreLevel: final lac st. pierre level (float)
    # troisrivieresLevel: final trois rivieres level (float)
    # staticXXXImpacts: expected impacts by water level for each location (dict)
    # dynamicOntarioImpacts: expected impacts by water level, location, and month (dict)

    # -----------------------
    # for each location, find the index of the closest water level (levels below min,
    # use min - levels above max, use max). extract number of buildings impacted at index
    # additionally, for lake ontario, find dynamic impacts with the closest water level and month
    # -----------------------

    # lake ontario static
    ind = np.argmin(abs(ontLevel - staticOntarioImpacts["waterLevel"]))
    ontarioStaticDamages = staticOntarioImpacts["buildingsImpacted"][ind]

    # lake ontario dynamic
    indLev = staticOntarioImpacts["waterLevel"][ind]
    lookupString = str(indLev).rstrip(".0") + "_" + str(month)
    ind = dynamicOntarioImpacts["matchString"].tolist().index(lookupString)
    ontarioDynamicDamages = dynamicOntarioImpacts["buildingsImpacted"][ind]

    # total lake ontario impacts
    ontarioDamages = ontarioStaticDamages + ontarioDynamicDamages

    # alexandria bay
    ind = np.argmin(abs(alexbayLevel - staticAlexBayImpacts["waterLevel"]))
    alexbayDamages = staticAlexBayImpacts["buildingsImpacted"][ind]

    # cardinal
    ind = np.argmin(abs(cardinalLevel - staticCardinalImpacts["waterLevel"]))
    cardinalDamages = staticCardinalImpacts["buildingsImpacted"][ind]

    # lery beauharnois
    ind = np.argmin(abs(lerybeauharnoisLevel - staticBeauImpacts["waterLevel"]))
    lerybeauharnoisDamages = staticBeauImpacts["buildingsImpacted"][ind]

    # pointe - claire
    ind = np.argmin(abs(ptclaireLevel - staticPtClaireImpacts["waterLevel"]))
    ptclaireDamages = staticPtClaireImpacts["buildingsImpacted"][ind]

    # maskinonge
    ind = np.argmin(abs(maskinongeLevel - staticMaskinongeImpacts["waterLevel"]))
    maskinongeDamages = staticMaskinongeImpacts["buildingsImpacted"][ind]

    # lac st. pierre
    ind = np.argmin(abs(lacstpierreLevel - staticLacStPierreImpacts["waterLevel"]))
    lacstpierreDamages = staticLacStPierreImpacts["buildingsImpacted"][ind]

    # sorel
    ind = np.argmin(abs(sorelLevel - staticSorelImpacts["waterLevel"]))
    sorelDamages = staticSorelImpacts["buildingsImpacted"][ind]

    # trois rivieres
    ind = np.argmin(abs(troisrivieresLevel - staticTroisRivieresImpacts["waterLevel"]))
    troisrivieresDamages = staticTroisRivieresImpacts["buildingsImpacted"][ind]

    # add upstream and downstream impacts
    upstreamImpacts = ontarioDamages + alexbayDamages + cardinalDamages
    downstreamImpacts = (
        lerybeauharnoisDamages
        + ptclaireDamages
        + maskinongeDamages
        + lacstpierreDamages
        + sorelDamages
        + troisrivieresDamages
    )

    return (
        upstreamImpacts,
        downstreamImpacts,
        ontarioDamages,
        alexbayDamages,
        cardinalDamages,
        lerybeauharnoisDamages,
        ptclaireDamages,
        maskinongeDamages,
        lacstpierreDamages,
        sorelDamages,
        troisrivieresDamages,
    )


# -----------------------------------------------------------------------------
# commercial navigation costs ($)
# -----------------------------------------------------------------------------

# load loading cost databases
ontarioLoadingCostDatabase = pd.read_csv("objectiveFunctions/cnOntarioLoadingCosts.csv")
ontarioLoadingCostDatabase = {
    x: ontarioLoadingCostDatabase[x].values for x in ontarioLoadingCostDatabase
}

seawayLoadingCostDatabase = pd.read_csv("objectiveFunctions/cnSeawayLoadingCosts.csv")
seawayLoadingCostDatabase = {
    x: seawayLoadingCostDatabase[x].values for x in seawayLoadingCostDatabase
}

montrealLoadingCostDatabase = pd.read_csv(
    "objectiveFunctions/cnMontrealLoadingCosts.csv"
)
montrealLoadingCostDatabase = {
    x: montrealLoadingCostDatabase[x].values for x in montrealLoadingCostDatabase
}


# returns total transportation cost for Lake Ontario, the Seaway, and Montreal in USD
def commercialNavigation(
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


# -----------------------------------------------------------------------------
# hydropower production value ($)
# -----------------------------------------------------------------------------


def hydropower(qm, ontFlow, erieOut, ontLevel, saundershwLevel, saunderstwLevel):
    # qm: quarter month (int)
    # ontFlow: release (float)
    # erieOut: lake erie outflows into lake ontario (float)
    # ontLevel: final lake ontario level (float)
    # saundershwLevel: saunders headwaters level (float)
    # saunderstwLevel: saunders tailwaters level (float)

    # set available generating units for opg and nypa
    opgUnits = 16
    nypaUnits = 16
    daysPerQM = 7.609

    # flow to opg and nypa (divide by 2 for split between OPG and NYPA - multiple by 10 to get cms)
    flow = ontFlow * 10 / 2

    # calculate station head
    if saundershwLevel - saunderstwLevel < 15:
        stationHead = 0
    else:
        stationHead = saundershwLevel - saunderstwLevel

    # ---------------------------------
    # ontario power generator calculations at Moses-Saunders
    # ---------------------------------

    # calculate OPG best flow and efficiency
    opgBestFlow = (
        -0.200768589170985 * pow(min(stationHead, 26.9723842267373), 2)
        + 11.2212829453861 * min(stationHead, 26.9723842267373)
        + 137.103100753584
    )

    opgBestEfficiency = (
        -0.0000507474686395653 * pow(min(stationHead, 26.9723842267373), 2)
        + 0.0114091120517272 * min(stationHead, 26.9723842267373)
        - 0.0358835196134448
    )

    # class 1 flow
    flowClassOne = opgBestFlow * opgUnits

    # calculate max flow and efficiency
    opgMaxFlow = (
        0.0349958407611678 * pow(min(stationHead, 25.8632227463708), 2)
        + 1.81520817689294 * min(stationHead, 25.8632227463708)
        + 248.145236417559
    )
    opgMaxEfficiency = (
        0.0000476160776591079 * pow(min(stationHead, 25.8632227463708), 2)
        + 0.00547943539251766 * min(stationHead, 25.8632227463708)
        + 0.0430730607896427
    )

    # class 2 flow
    flowClassTwo = opgMaxFlow * opgUnits

    # opg power
    if flow < flowClassOne:
        opgPower = opgBestEfficiency * flow
    elif flow > flowClassTwo:
        opgPower = opgMaxEfficiency * flowClassTwo
    else:
        opgPower = flow * (
            opgBestEfficiency
            + (opgMaxEfficiency - opgBestEfficiency)
            * (flow - flowClassOne)
            / (opgUnits * (opgMaxFlow - opgBestFlow))
        )

    # opg energy
    opgEnergy = opgPower * 24 * daysPerQM

    # opg prices
    opgEnergyPrice = [
        61.92,
        62.40,
        62.67,
        62.78,
        62.66,
        62.26,
        61.48,
        60.34,
        58.91,
        57.25,
        55.34,
        52.95,
        50.41,
        48.13,
        46.39,
        44.79,
        43.59,
        43.19,
        44.07,
        46.49,
        49.62,
        52.53,
        54.40,
        55.64,
        56.51,
        57.18,
        57.83,
        58.58,
        59.08,
        59.00,
        57.90,
        55.56,
        52.71,
        50.19,
        48.69,
        47.72,
        47.25,
        47.36,
        48.22,
        50.11,
        52.50,
        54.75,
        56.34,
        57.54,
        58.51,
        59.38,
        60.22,
        61.00,
    ]

    # opg energy value
    opgEnergyValue = opgEnergy * opgEnergyPrice[qm - 1]

    # ---------------------------------
    # new york power authority calculations at Moses-Saunders
    # ---------------------------------

    # nypa max flow
    nypaMaxFlow = 73.3668 + 15.6074 * stationHead - 0.235229 * pow(stationHead, 2)

    # nypa power
    if flow / nypaUnits <= 250:
        nypaPower = (
            0.00981
            * flow
            * stationHead
            * (0.7231 + 0.0141374 * stationHead - 0.000269745 * pow(stationHead, 2))
        )
    elif flow / nypaUnits > nypaMaxFlow:
        nypaPower = nypaUnits * (
            -29.4562 + 4.10228 * stationHead - 0.014773 * pow(stationHead, 2)
        )
    else:
        nypaPower = 0.00981 * flow * stationHead * (
            0.723104 + 0.0141374 * stationHead - 0.000269745 * pow(stationHead, 2)
        ) + nypaUnits * (
            -30.6239
            - 1.04109 * stationHead
            + (0.380326 + 0.00415784 * stationHead) * flow / nypaUnits
            - 0.00103134 * pow((flow / nypaUnits), 2)
        )

    # nypa energy
    nypaEnergy = nypaPower * 24 * daysPerQM

    # nypa prices
    nypaEnergyPrice = [
        55.56,
        57.39,
        59.65,
        60.70,
        60.74,
        60.33,
        59.94,
        58.93,
        58.61,
        57.66,
        56.30,
        54.60,
        52.52,
        49.82,
        48.40,
        47.75,
        47.04,
        45.86,
        43.71,
        42.76,
        42.47,
        42.44,
        44.26,
        46.60,
        48.43,
        50.19,
        53.84,
        57.70,
        57.53,
        57.71,
        56.14,
        53.05,
        50.69,
        49.96,
        50.10,
        51.15,
        51.02,
        52.63,
        54.32,
        55.34,
        54.32,
        52.94,
        52.99,
        54.33,
        55.57,
        55.41,
        54.74,
        50.36,
    ]

    # nypa energy value
    nypaEnergyValue = nypaEnergy * nypaEnergyPrice[qm - 1]

    # ---------------------------------
    # power calculations at Niagara River
    # ---------------------------------

    # niagara basin flow by month (each four times for quarter-monthly values)
    niagaraBasinFlow = [
        87.78,
        87.78,
        87.78,
        87.78,
        79.29,
        79.29,
        79.29,
        79.29,
        99.11,
        99.11,
        99.11,
        99.11,
        -8.5,
        -8.5,
        -8.5,
        -8.5,
        -116.1,
        -116.1,
        -116.1,
        -116.1,
        -127.43,
        -127.43,
        -127.43,
        -127.43,
        -124.59,
        -124.59,
        -124.59,
        -124.59,
        -127.43,
        -127.43,
        -127.43,
        -127.43,
        -118.93,
        -118.93,
        -118.93,
        -118.93,
        -116.1,
        -116.1,
        -116.1,
        -116.1,
        -96.28,
        -96.28,
        -96.28,
        -96.28,
        -33.98,
        -33.98,
        -33.98,
        -33.98,
    ]

    niagaraFlow = erieOut - niagaraBasinFlow[qm - 1] - 195.39

    # scenic flow by quarter-month
    scenicFlow = [
        1432.832438,
        1432.832438,
        1432.832438,
        1432.832438,
        1432.832438,
        1432.832438,
        1432.832438,
        1432.832438,
        1432.832438,
        2258.740463,
        2258.740463,
        2258.740463,
        2258.740463,
        2258.740463,
        2258.740463,
        2258.740463,
        2258.740463,
        2258.740463,
        2258.740463,
        2258.740463,
        2258.740463,
        2258.740463,
        2258.740463,
        2258.740463,
        2258.740463,
        2258.740463,
        2258.740463,
        2258.740463,
        2258.740463,
        2258.740463,
        2258.740463,
        2258.740463,
        2258.740463,
        2258.740463,
        2140.753602,
        2140.753602,
        2140.753602,
        2140.753602,
        2140.753602,
        2140.753602,
        1432.832438,
        1432.832438,
        1432.832438,
        1432.832438,
        1432.832438,
        1432.832438,
        1432.832438,
        1432.832438,
    ]

    # flow to opg
    opgShare = 0.5 * (niagaraFlow - scenicFlow[qm - 1] + (-1900) * pow(0.3048, 3))

    # flow to nypa
    nypaShare = 0.5 * (niagaraFlow - scenicFlow[qm - 1] - (-1900) * pow(0.3048, 3))

    # beck tailwater part 1
    beckPart1 = niagaraFlow / (1000 * pow(0.3048, 3)) - 140

    # beck tailwater term 1
    beckTerm1 = (
        246.0663
        + 0.0245372 * beckPart1
        + 0.0000845267 * pow(beckPart1, 2)
        + 0.000000209902 * pow(beckPart1, 3)
    )

    # beck tailwater term 2
    beckTerm2 = (
        247.7059
        + 0.021292 * beckPart1
        + 0.0000855841 * pow(beckPart1, 2)
        + 0.00000021885 * pow(beckPart1, 3)
    )

    # beck tailwater term 3
    beckTerm3 = (
        246.0663
        + 0.0245372 * beckPart1
        + 0.0000845267 * pow(beckPart1, 2)
        + 0.000000209902 * pow(beckPart1, 3)
    )

    # beck tailwater term 4
    beckTerm4 = ((ontLevel / 0.3048) - 244) / 2

    # beck tailwater elevation
    beckTWElev = 0.3048 * (beckTerm1 + (beckTerm2 - beckTerm3) * beckTerm4)

    # niagara opg power
    opgNiagaraPower = (
        min(opgShare, 2270)
        * (23 / pow(0.3048, 3))
        / 1000
        * ((538 * 0.3048) - beckTWElev)
        / (290.9 * 0.3048)
    )

    # niagara opg energy
    opgNiagaraEnergy = opgNiagaraPower * 24 * daysPerQM

    # moses tailwater at niagara
    mosesNiagaraTW = 0.3048 * (
        65.7001 + 0.000050985 * (niagaraFlow * 35.3147) + 0.712332 * (ontLevel / 0.3048)
    )

    # niagara nypa power
    nypaNiagaraPower = (
        (min(nypaShare, 2860) * 35.3147)
        * 62.4
        * (
            (561.5 - pow((min(nypaShare, 2860) * 35.3147 / 1000), 2) / 420)
            - mosesNiagaraTW / 0.3048
        )
        * 0.92
        * 1.356
        * pow(10, -6)
    )

    # niagara nypa energy
    nypaNiagaraEnergy = nypaNiagaraPower * 24 * daysPerQM

    # energy value
    opgNiagaraEnergyValue = opgNiagaraEnergy * opgEnergyPrice[qm - 1]
    nypaNiagaraEnergyValue = nypaNiagaraEnergy * nypaEnergyPrice[qm - 1]

    # peaking value
    dailyPeakingValue = 50000

    if ontFlow <= 708:
        peakingStatus = 1
    elif ontFlow >= 793:
        peakingStatus = 0
    else:
        peakingStatus = 1 - (ontFlow - 708) / (793 - 708)

    peakingValue = peakingStatus * daysPerQM * dailyPeakingValue

    hydroTotalValue = (
        opgEnergyValue
        + nypaEnergyValue
        + opgNiagaraEnergyValue
        + nypaNiagaraEnergyValue
        + peakingValue
    )

    return (
        hydroTotalValue,
        opgEnergyValue,
        nypaEnergyValue,
        opgNiagaraEnergyValue,
        nypaNiagaraEnergyValue,
        peakingValue,
    )


# -----------------------------------------------------------------------------
# meadow marsh area (hectares)
# -----------------------------------------------------------------------------

# load area contours for meadow marsh area calculations
mmAreaContours = pd.read_csv("objectiveFunctions/mmContourAreas.csv")


def meadowMarsh(levels, nts, contours):
    # levels: dataframe of water level time series over the full simulation period
    #   ["Sim", "Year", "QM", "ontLevel"]
    # nts: dataframe of nts time series over the full simulation period
    #   ["Sim", "Year", "QM", "ontNTS"]
    # contours: dataframe of areas associated with water levels contours for the four wetland types

    # define inner functions
    def createDatabase(x):
        # creates databases for last flooded and last dewatered calculations (highest
        # peak, minimum of four peaks surrounding highest peak, and highest growing
        # season peak) from time series of quarter-monthly water levels

        # -----------------------------------------------------------------------------
        # last flooded database
        # -----------------------------------------------------------------------------

        # now we find the maximum water level for each year by taking the minumum of
        # the peak water level and the surrounding four levels

        lfDB = pd.DataFrame(x["Year"].unique(), columns=["Year"])

        for i in range(lfDB.shape[0]):
            yoi = lfDB["Year"][i]

            # filter by year of interest
            tmp = x.loc[x["Year"] == yoi].reset_index(drop=True)
            tmp = tmp.reindex(range(-3, 51))

            # get index of maximum water level
            max_index = tmp["ontLevel"].idxmax()

            # get surrounding four qm water levels
            v1 = np.array(
                [
                    tmp["ontLevel"][max_index],
                    tmp["ontLevel"][max_index + 1],
                    tmp["ontLevel"][max_index + 2],
                    tmp["ontLevel"][max_index + 3],
                ]
            )
            v2 = np.array(
                [
                    tmp["ontLevel"][max_index - 1],
                    tmp["ontLevel"][max_index],
                    tmp["ontLevel"][max_index + 1],
                    tmp["ontLevel"][max_index + 2],
                ]
            )
            v3 = np.array(
                [
                    tmp["ontLevel"][max_index - 2],
                    tmp["ontLevel"][max_index - 1],
                    tmp["ontLevel"][max_index],
                    tmp["ontLevel"][max_index + 1],
                ]
            )
            v4 = np.array(
                [
                    tmp["ontLevel"][max_index - 3],
                    tmp["ontLevel"][max_index - 2],
                    tmp["ontLevel"][max_index - 1],
                    tmp["ontLevel"][max_index],
                ]
            )
            v = [np.nanmin(v1), np.nanmin(v2), np.nanmin(v3), np.nanmin(v4)]

            # save values
            lfDB.loc[i, "PeakLevel"] = np.nanmax(tmp["ontLevel"])
            lfDB.loc[i, "MinPeakLevel"] = np.nanmax(v)

        # -----------------------------------------------------------------------------
        # last detwatered database
        # -----------------------------------------------------------------------------

        # now we find the lowest growing season peak water level for each year
        dwDB = pd.DataFrame(x["Year"].unique(), columns=["Year"])

        # define growing season in quarter-months [May QM 1 - October QM 4]
        # growingseason = np.arange(17, 45, 1)

        for i in range(dwDB.shape[0]):
            yoi = dwDB["Year"][i]

            # filter by year of interest
            tmp = x.loc[(x["Year"] == yoi)].reset_index(drop=True)

            # tmp = x.loc[(x["Year"] == yoi) & (x["QM"].isin(growingseason))].reset_index(
            #     drop=True
            # )

            # get max level of growing season levels
            dwDB.loc[i, "PeakLevel"] = tmp["ontLevel"].max()

        output = dict()
        output["lfDB"] = lfDB
        output["dwDB"] = dwDB

        return output

    def levelClassification(x, flooded, dewatered):
        # takes in quarter-monthly water levels (x), last flooded database (y), and
        # last dewatered database (z). returns elevations associated with each
        # classification (U, ABC, D, EF, and G)

        # -----------------------------------------------------------------------------
        # water level classification
        # -----------------------------------------------------------------------------

        # create a database to save the levels corresponding to each wetland class
        results = pd.DataFrame(x["Year"].unique(), columns=["Year"])
        results = results.sort_values(by="Year", ascending=False).reset_index(drop=True)

        for i in range(results.shape[0]):
            # year of interest
            yoi = results["Year"][i]

            # -----------------------------------------------------------------------------
            # last dewatered designations
            # -----------------------------------------------------------------------------

            # filter to only include years before the year of interest, y
            tmpWL = dewatered.loc[dewatered["Year"] < yoi]

            # account for early years by appending data to the top of data frame
            if yoi - results["Year"].min() <= 40:
                ind = int(40 - (yoi - results["Year"].min()))
                app = pd.DataFrame(dewatered.tail(ind)).reset_index(drop=True)
                app.loc[:, "Year"] = np.sort(
                    results["Year"].min() - np.arange(1, ind + 1, 1)
                )
                tmpWL = pd.concat([app, tmpWL]).reset_index(drop=True)
                # tmpWL = tmpWL.reset_index(drop=True)

            # get minimum peak level for G classification
            gWL = tmpWL["PeakLevel"].min()
            gYR = tmpWL.loc[tmpWL["PeakLevel"].idxmin(), "Year"]

            # data frame to save peak years, levels, and classifications
            tmpDW = pd.DataFrame(
                {
                    "Year": [gYR],
                    "Level": [gWL],
                    "NumYears": ["Forever"],
                    "Classification": ["G"],
                }
            )

            # filter by years since the lowest growing season peak
            tmpWL = tmpWL.loc[tmpWL["Year"] > gYR]

            # set counter to refer to previous peak year
            count = 1

            while tmpWL.shape[0] > 0:
                # get minimum level and corresponding year
                tmpDW.loc[count, "Level"] = tmpWL["PeakLevel"].min()
                tmpDW.loc[count, "Year"] = tmpWL.loc[
                    tmpWL["PeakLevel"].idxmin(), "Year"
                ]

                # how long ago was level last dewatered
                dw = yoi - tmpDW.loc[(count - 1), "Year"]
                tmpDW.loc[count, "NumYears"] = dw

                # depending on the years since dewatering, assign class
                if dw >= 40:
                    tmpDW.loc[count, "Classification"] = "G"
                if dw > 20 and dw < 40:
                    tmpDW.loc[count, "Classification"] = "F"
                if dw > 3 and dw <= 20:
                    tmpDW.loc[count, "Classification"] = "E"
                if dw <= 3:
                    tmpDW.loc[count, "Classification"] = "D"

                tmpWL = tmpWL.loc[tmpWL["Year"] > tmpDW.loc[count, "Year"]]

                count = count + 1

            # -----------------------------------------------------------------------------
            # last flooded designations
            # -----------------------------------------------------------------------------

            # filter to only include years before the year of interest, y
            tmpWL = flooded.loc[flooded["Year"] < yoi]

            # account for early years by appending data to the top of data frame
            if yoi - results["Year"].min() < 30:
                ind = int(30 - (yoi - results["Year"].min()))
                app = pd.DataFrame(flooded.tail(ind)).reset_index(drop=True)
                app.loc[:, "Year"] = np.sort(
                    results["Year"].min() - np.arange(1, ind + 1, 1)
                )
                tmpWL = pd.concat([app, tmpWL]).reset_index(drop=True)

            # get peak level for upland classification
            uWL = tmpWL["MinPeakLevel"].max()
            uYR = tmpWL.loc[tmpWL["MinPeakLevel"].idxmax(), "Year"]

            # data frame to save peak years, levels, and classifications
            tmpLF = pd.DataFrame(
                {
                    "Year": [uYR],
                    "Level": [uWL],
                    "NumYears": ["Forever"],
                    "Classification": ["A"],
                }
            )

            # filter by years since the upland peak
            tmpWL = tmpWL.loc[tmpWL["Year"] > uYR]

            # set counter to refer to previous peak year
            count = 1

            while tmpWL.shape[0] > 0:
                # get minimum level and corresponding year
                tmpLF.loc[count, "Level"] = tmpWL["MinPeakLevel"].max()
                tmpLF.loc[count, "Year"] = tmpWL.loc[
                    tmpWL["MinPeakLevel"].idxmax(), "Year"
                ]

                # how long ago was level last dewatered
                lf = yoi - tmpLF.loc[(count - 1), "Year"]
                tmpLF.loc[count, "NumYears"] = lf

                # depending on the years since dewatering, assign class
                if lf >= 30:
                    tmpLF.loc[count, "Classification"] = "A"
                if lf >= 10 and lf < 30:
                    tmpLF.loc[count, "Classification"] = "B"
                if lf >= 5 and lf < 10:
                    tmpLF.loc[count, "Classification"] = "C"
                if lf < 5:
                    tmpLF.loc[count, "Classification"] = "D"

                tmpWL = tmpWL.loc[tmpWL["Year"] > tmpLF.loc[count, "Year"]]

                # last peak check
                if tmpWL.shape[0] == 0:
                    # if last peak happened less than 5 years ago and was less than most
                    # recent dewatered level, use max peak rather than the min peak
                    if (
                        yoi - tmpLF.loc[count, "Year"] < 5
                        and tmpLF.loc[count, "Level"]
                        < tmpDW.loc[tmpDW.shape[0] - 1, "Level"]
                    ):
                        lp = flooded.loc[flooded["Year"] == tmpLF.loc[count, "Year"]]
                        tmpLF.loc[count, "Level"] = lp["PeakLevel"].max()

                count = count + 1

            # assign water levels to each last flooded and dewatered classification
            # take the minimum water levels for last flooded and maximum for last
            # dewatered classification
            aWL = tmpLF.loc[tmpLF["Classification"] == "A", "Level"].min()
            bWL = tmpLF.loc[tmpLF["Classification"] == "B", "Level"].min()
            cWL = tmpLF.loc[tmpLF["Classification"] == "C", "Level"].min()
            dflWL = tmpLF.loc[tmpLF["Classification"] == "D", "Level"].min()
            ddwWL = tmpDW.loc[tmpDW["Classification"] == "D", "Level"].max()
            eWL = tmpDW.loc[tmpDW["Classification"] == "E", "Level"].max()
            fWL = tmpDW.loc[tmpDW["Classification"] == "F", "Level"].max()
            gWL = tmpDW.loc[tmpDW["Classification"] == "G", "Level"].max()

            # get the max of last flooded and last dewatered D
            if np.isnan([dflWL, ddwWL]).all() == False:
                dWL = np.nanmax([dflWL, ddwWL])
            else:
                dWL = np.nan

            # check for if the highest dewatered elevation (usually D) is greater than any
            # of the last flooded elevations
            maxDewateredElevation = np.nanmax([dWL, eWL, fWL, gWL])
            if cWL < maxDewateredElevation:
                cWL = maxDewateredElevation
            if bWL < maxDewateredElevation:
                bWL = maxDewateredElevation
            if aWL < maxDewateredElevation:
                aWL = maxDewateredElevation

            # cleaned up classification
            results.loc[i, "Top"] = 75.75
            results.loc[i, "A"] = aWL
            results.loc[i, "B"] = bWL
            results.loc[i, "C"] = cWL
            results.loc[i, "D"] = dWL
            results.loc[i, "E"] = eWL
            results.loc[i, "F"] = fWL
            results.loc[i, "G"] = gWL
            results.loc[i, "Bottom"] = 73.00

        return results

    def percentClassification(x, contours):
        # takes in elevations associated with each classification (U, ABC, D, EF,
        # and G) and convert them to percentage of wetland areas

        # -----------------------------------------------------------------------------
        # percent of modeled area calculations
        # -----------------------------------------------------------------------------

        # set wetland types
        wetlandTypes = ["BB", "DRM", "OB", "PB"]
        lfClasses = ["A", "B", "C", "D"]
        dwClasses = ["D", "E", "F", "G"]

        # empty list to store results
        output = dict()

        for j in wetlandTypes:
            # calculate cumulative sum to interpolate for wetland type
            contAreas = contours.loc[
                contours["wetlandType"] == j,
                ["minElevation", "maxElevation", "areaFraction"],
            ]

            # data frame to save results
            tmp = pd.DataFrame(x["Year"])
            tmp[["A", "B", "C", "D", "E", "F", "G"]] = np.nan

            for i in range(tmp.shape[0]):
                # classification levels
                levs = x.loc[i, ["Top", "A", "B", "C", "D", "E", "F", "G", "Bottom"]]
                cleanlevs = levs.dropna()

                for k in range(1, len(cleanlevs) - 1):
                    tmpClass = cleanlevs.index[k]

                    # # get the elevation upper and lower elevation for the classification
                    if tmpClass == "D":
                        maxElevation = cleanlevs[k - 1]
                        minElevation = cleanlevs[k + 1]
                    elif tmpClass in lfClasses:
                        maxElevation = cleanlevs[k - 1]
                        minElevation = cleanlevs[k]
                    elif tmpClass in dwClasses:
                        maxElevation = cleanlevs[k]
                        minElevation = cleanlevs[k + 1]

                    # filter the elevations between the min and max elevation bounds
                    elevs = contAreas.loc[
                        (contAreas["minElevation"] < maxElevation)
                        & (contAreas["minElevation"] >= minElevation),
                    ]

                    # sum up the area fractions
                    areaFraction = elevs.loc[:, "areaFraction"].sum()

                    # save
                    tmp.loc[i, tmpClass] = areaFraction

            # save wetland type
            tmp["Wetland Type"] = j

            # format
            tmp = tmp[["Wetland Type", "Year", "A", "B", "C", "D", "E", "F", "G"]]

            # save
            output[j] = tmp

        output = pd.concat(output).reset_index(drop=True)

        return output

    def areaCalculation(x):
        # load in wetland area by type
        wetlandAreas = pd.DataFrame(
            {
                "Classification": ["BB", "DRM", "OB", "PB"],
                "totalArea": [7903, 8628, 6457, 8664],
            }
        )

        # wetlandAreas = pd.read_csv("models/wetland_areas.csv")
        # wetlandAreas.columns = ["Name", "County", "Unit", "Type", "Area"]

        # specify types of wetlands
        # wetlandTypes = x["Wetland Type"].unique()

        # format
        df = pd.melt(
            x,
            id_vars=["Year", "Wetland Type"],
            value_vars=["A", "BC", "D", "EF", "G"],
            var_name="Classification",
            value_name="PercentArea",
        )

        # # create column to store areas
        # df["PercentArea"] = abs(df["PercentArea"])
        df["Area"] = np.nan

        for i in range(wetlandAreas.shape[0]):
            # wetland type of interest
            wetlandType = wetlandAreas.loc[i, "Classification"]

            # get areas in hectares for wetland of interest
            totalArea = wetlandAreas.loc[i, "totalArea"]

            # sum total area for wetland types
            # totalArea = sum(tmpAreas["Area"])

            # multiply wetland type across all percentages
            df["Area"] = np.where(
                df["Wetland Type"] == wetlandType,
                df["PercentArea"] * totalArea,
                df["Area"],
            )

        sumArea = df.groupby(["Year", "Classification"], as_index=False)[["Area"]].sum()

        return sumArea

    def lowSupplyYears(nts):
        lowT = 7100
        highT = 8000

        # filter out january - june data and find annual average
        growingSeasonNTS = nts.loc[nts["QM"] <= 24, :]
        growingSeasonNTS = growingSeasonNTS.groupby("Year", as_index=False)[
            "ontNTS"
        ].mean()

        # pad 4 years at the beginning and end of the dataframe
        # endData = growingSeasonNTS.iloc[:4, ].reset_index(drop=True)
        # endData.loc[:3, "Year"] = growingSeasonNTS.loc[growingSeasonNTS.shape[0] - 1, "Year"] + [1, 2, 3, 4]
        # counter = growingSeasonNTS.append(endData).reset_index(drop=True)
        counter = growingSeasonNTS

        # list to store low supply years
        years = []

        while counter.shape[0] > 0:
            if counter["ontNTS"].min() < lowT:
                # find first occurence of average nts below the threshold
                yearStart = counter.loc[counter["ontNTS"] < lowT, "Year"].reset_index(
                    drop=True
                )[0]

                # filter growing season dataframe after the first year
                counter = counter.loc[counter["Year"] > yearStart, :].reset_index(
                    drop=True
                )

                # accounts for if the last timestep is the one below the threshold
                if counter.shape[0] > 0:
                    # check if any of the next 4 values exceed the higher threshold
                    if all(counter.loc[:3, "ontNTS"] < highT):
                        if counter["ontNTS"].max() > highT:
                            # find first occurence of average nts below the threshold
                            yearEnd = counter.loc[
                                counter["ontNTS"] > highT, "Year"
                            ].reset_index(drop=True)[0]
                            yearList = list(range(yearStart + 4, yearEnd))
                            years.append(yearList)

                            # filter years
                            counter = counter.loc[
                                counter["Year"] > yearEnd, :
                            ].reset_index(drop=True)

                        else:
                            # take the rest of the years, since upper threshold is never exceeded
                            yearEnd = int(counter["Year"][-1:])
                            yearList = list(range(yearStart + 4, yearEnd + 1))
                            years.append(yearList)

                            # filter years
                            counter = counter.loc[
                                counter["Year"] > yearEnd, :
                            ].reset_index(drop=True)

                else:
                    break

            else:
                break

        years = sum(years, [])

        return years

    # create last flooded and last dewatered databases
    DBs = createDatabase(levels)

    # classify elevations as U, ABC, D, EF, or G
    wlClass = levelClassification(levels, DBs["lfDB"], DBs["dwDB"])

    # convert elevations to percent areas
    classArea = percentClassification(wlClass, contours)

    # group areas by similar vegetation type
    groupedAreas = classArea.loc[:, ["Wetland Type", "Year"]]
    groupedAreas["A"] = classArea["A"].fillna(0)
    groupedAreas["BC"] = classArea["B"].fillna(0) + classArea["C"].fillna(0)
    groupedAreas["D"] = classArea["D"].fillna(0)
    groupedAreas["EF"] = classArea["E"].fillna(0) + classArea["F"].fillna(0)
    groupedAreas["G"] = classArea["G"].fillna(0)

    # convert percent areas to total areas
    totalArea = areaCalculation(groupedAreas)

    # get net total supply to check for period of low supplies
    yearInd = lowSupplyYears(nts)

    # extract years that meet supply criteria
    # lowSupply = totalArea.loc[(totalArea["Year"].isin(yearInd))]

    # return marker of low supply year or not
    lowSupply = totalArea
    lowSupply.loc[(lowSupply["Year"].isin(yearInd)), "lowSupplyYear"] = 1

    # get meadow marsh in low supply years
    lowSupply = lowSupply.loc[
        lowSupply["Classification"] == "BC", ["Year", "Area", "lowSupplyYear"]
    ].reset_index(drop=True)

    return lowSupply


# -----------------------------------------------------------------------------
# probability of muskrat lodge viability (%)
# -----------------------------------------------------------------------------


# file with the various lodge (HUT) configurations (min, median and maximum) -> "PLV_HUT_3_375", "PLV_HUT_3_39", "PLV_HUT_3_51"
muskratCoefficients = pd.read_csv("objectiveFunctions/muskratCoefficients.csv")


def muskratHouseViability(levels, locs, pd_meta):
    # hut config to report - MEDIAN
    hutPI = "HUT_3_39"

    data = []

    for l in range(locs.shape[0]):
        #  select columns for location of interest
        levs = levels.loc[
            :,
            (["Sim", "Year", "QM"] + [locs.loc[l, "Gage"]]),
        ]

        levs.columns = ["Sim", "Year", "QM", "waterLevel"]

        # data frame for results
        output = (
            pd.DataFrame({"Year": levs.loc[:, "Year"].unique()})
            .sort_values("Year", ascending=True)
            .reset_index(drop=True)
        )

        # first year calculation starts mid-winter (winter of year 1 gets jan/feb of year 2)
        for i in range(output.shape[0]):
            # year of interest
            y = output.loc[i, "Year"]
            # print(y)

            # # skip first year of calculation
            # if i == 0:
            #     output.loc[i, "probLodgeViability"] = np.nan

            # else:

            # winter (dec (current year) - feb (next year)) quarter-monthly water levels
            winterLevels = pd.concat(  # np.array (
                [
                    levs.loc[
                        (levs["Year"] == y) & (levs["QM"] >= 45),
                        ["Year", "QM", "waterLevel"],
                    ],
                    levs.loc[
                        (levs["Year"] == (y + 1)) & (levs["QM"] <= 13),
                        ["Year", "QM", "waterLevel"],
                    ],
                ]
            )

            # hut install of current year
            winterLevels["meanLevel"] = winterLevels.loc[
                (levs["Year"] == y) & (levs["QM"] >= 45), "waterLevel"
            ].mean()
            winterLevels["deltaLevel"] = (
                winterLevels["waterLevel"] - winterLevels["meanLevel"]
            )

            tmp = []

            for h in range(pd_meta.shape[0]):
                tmpDF = winterLevels.copy()

                conditions = [
                    (tmpDF["deltaLevel"] < pd_meta.loc[h, "LIM_LOW"]),
                    (pd_meta.loc[h, "LIM_LOW"] <= tmpDF["deltaLevel"])
                    & (tmpDF["deltaLevel"] < pd_meta.loc[h, "LIM_1"]),
                    (pd_meta.loc[h, "LIM_1"] <= tmpDF["deltaLevel"])
                    & (tmpDF["deltaLevel"] < pd_meta.loc[h, "LIM_2"]),
                    (pd_meta.loc[h, "LIM_2"] <= tmpDF["deltaLevel"])
                    & (tmpDF["deltaLevel"] < pd_meta.loc[h, "LIM_HIGH"]),
                    (tmpDF["deltaLevel"] > pd_meta.loc[h, "LIM_HIGH"]),
                ]

                choices = [
                    (pd_meta.loc[h, "RES_LOW"]),
                    (
                        (pd_meta.loc[h, "RES_0_COEF"] * tmpDF["deltaLevel"])
                        + pd_meta.loc[h, "RES_0_MOD"]
                    ),
                    (
                        (pd_meta.loc[h, "RES_1_COEF"] * tmpDF["deltaLevel"])
                        + pd_meta.loc[h, "RES_1_MOD"]
                    ),
                    (
                        (pd_meta.loc[h, "RES_2_COEF"] * tmpDF["deltaLevel"])
                        + pd_meta.loc[h, "RES_2_MOD"]
                    ),
                    (pd_meta.loc[h, "RES_HIGH"]),
                ]

                tmpDF["hutID"] = pd_meta.loc[h, "META_ID"]
                tmpDF["PLV"] = np.select(conditions, choices, default="np.nan")
                tmpDF["PLV"] = tmpDF["PLV"].astype("float")

                tmp.append(tmpDF)

            df = pd.concat(tmp).reset_index(drop=True)
            minPLV = round(df.loc[df["hutID"] == hutPI, "PLV"].min(), 4)
            output.loc[i, "probLodgeViability"] = minPLV

        output["Location"] = locs.loc[l, "Location"]
        data.append(output)

    data = pd.concat(data)

    return data


# -----------------------------------------------------------------------------
# recreational boating costs ($)
# -----------------------------------------------------------------------------

# load recreational boating costs for all locations
rbOntarioImpacts = pd.read_csv("objectiveFunctions/rbOntarioImpacts.csv")
rbOntarioImpacts = {x: rbOntarioImpacts[x].values for x in rbOntarioImpacts}

rbAlexBayImpacts = pd.read_csv("objectiveFunctions/rbAlexBayImpacts.csv")
rbAlexBayImpacts = {x: rbAlexBayImpacts[x].values for x in rbAlexBayImpacts}

rbOgdensburgImpacts = pd.read_csv("objectiveFunctions/rbOgdensburgImpacts.csv")
rbOgdensburgImpacts = {x: rbOgdensburgImpacts[x].values for x in rbOgdensburgImpacts}

rbBrockvilleImpacts = pd.read_csv("objectiveFunctions/rbBrockvilleImpacts.csv")
rbBrockvilleImpacts = {x: rbBrockvilleImpacts[x].values for x in rbBrockvilleImpacts}

rbLongSaultImpacts = pd.read_csv("objectiveFunctions/rbLongSaultImpacts.csv")
rbLongSaultImpacts = {x: rbLongSaultImpacts[x].values for x in rbLongSaultImpacts}

rbPtClaireImpacts = pd.read_csv("objectiveFunctions/rbPtClaireImpacts.csv")
rbPtClaireImpacts = {x: rbPtClaireImpacts[x].values for x in rbPtClaireImpacts}

rbVarennesImpacts = pd.read_csv("objectiveFunctions/rbVarennesImpacts.csv")
rbVarennesImpacts = {x: rbVarennesImpacts[x].values for x in rbVarennesImpacts}

rbSorelImpacts = pd.read_csv("objectiveFunctions/rbSorelImpacts.csv")
rbSorelImpacts = {x: rbSorelImpacts[x].values for x in rbSorelImpacts}


# returns the recreational boating impacts in USD
def recreationalBoating(
    qm,
    month,
    ontLevel,
    alexbayLevel,
    ogdensburgLevel,
    brockvilleLevel,
    longsaultLevel,
    ptclaireLevel,
    varennesLevel,
    sorelLevel,
    rbOntarioImpacts,
    rbAlexBayImpacts,
    rbOgdensburgImpacts,
    rbBrockvilleImpacts,
    rbLongSaultImpacts,
    rbPtClaireImpacts,
    rbVarennesImpacts,
    rbSorelImpacts,
):
    # qm: quarter month (int)
    # month: month (int)
    # ontLevel: final lake ontario level (float)
    # alexbayLevel: final alexandria bay level (float)
    # ogdensburgLevel: final ogdensburg level (float)
    # brockvilleLevel: final brockville level (float)
    # longsaultLevel: final long sault level (float)
    # ptclaireLevel: final pointe-claire level (float)
    # varennesLevel: final varennes level (float)
    # sorelLevel: final sorel level (float)
    # rbXXXImpacts: costs by water level and month for each location (dictionary)

    # if not in rb season, set the costs to zero
    if qm < 15 or qm > 42:
        totalCosts = 0
        ontarioCosts = 0
        alexbayCosts = 0
        ogdensburgCosts = 0
        brockvilleCosts = 0
        longsaultCosts = 0
        ptclaireCosts = 0
        varennesCosts = 0
        sorelCosts = 0

    # else find the index of the water level and the associated cost
    # if water level is below/above the min/max in the impact tables,
    # take the min/max cost
    else:
        # lake ontario
        ind = np.argmin(abs(ontLevel - rbOntarioImpacts["waterLevel"]))
        ontarioCosts = rbOntarioImpacts[str(month)][ind]

        # alexandria bay
        ind = np.argmin(abs(alexbayLevel - rbAlexBayImpacts["waterLevel"]))
        alexbayCosts = rbAlexBayImpacts[str(month)][ind]

        # ogdensburg
        ind = np.argmin(abs(ogdensburgLevel - rbOgdensburgImpacts["waterLevel"]))
        ogdensburgCosts = rbOgdensburgImpacts[str(month)][ind]

        # brockville
        ind = np.argmin(abs(brockvilleLevel - rbBrockvilleImpacts["waterLevel"]))
        brockvilleCosts = rbBrockvilleImpacts[str(month)][ind]

        # long sault
        ind = np.argmin(abs(longsaultLevel - rbLongSaultImpacts["waterLevel"]))
        longsaultCosts = rbLongSaultImpacts[str(month)][ind]

        # pointe - claire
        ind = np.argmin(abs(ptclaireLevel - rbPtClaireImpacts["waterLevel"]))
        ptclaireCosts = rbPtClaireImpacts[str(month)][ind]

        # varennes
        ind = np.argmin(abs(varennesLevel - rbVarennesImpacts["waterLevel"]))
        varennesCosts = rbVarennesImpacts[str(month)][ind]

        # sorel
        ind = np.argmin(abs(sorelLevel - rbSorelImpacts["waterLevel"]))
        sorelCosts = rbSorelImpacts[str(month)][ind]

        totalCosts = (
            float(ontarioCosts)
            + float(alexbayCosts)
            + float(ogdensburgCosts)
            + float(brockvilleCosts)
            + float(longsaultCosts)
            + float(ptclaireCosts)
            + float(varennesCosts)
            + float(sorelCosts)
        )

    # return total recreational boating costs
    return (
        totalCosts,
        ontarioCosts,
        alexbayCosts,
        ogdensburgCosts,
        brockvilleCosts,
        longsaultCosts,
        ptclaireCosts,
        varennesCosts,
        sorelCosts,
    )


# -----------------------------------------------------------------------------
# evaluate objective functions over simulation output from optimization algorithm
# -----------------------------------------------------------------------------


# returns annual average of each objective
def objectiveEvaluation(
    data,  # dataframe of water levels and flows (output of simulation model)
    # output = "netAnnualAverage",  # ts, netAnnualAverage, piWeighting
):
    # ---------------------------------
    # coastal impacts
    # ---------------------------------

    # coastal impacts (returns the number of buildings impacted upstream and downstream)
    keys = [
        "Sim",
        "Year",
        "Month",
        "QM",
        "ontLevel",
        "alexbayLevel",
        "cardinalLevel",
        "lerybeauharnoisLevel",
        "ptclaireLevel",
        "maskinongeLevel",
        "sorelLevel",
        "lacstpierreLevel",
        "troisrivieresLevel",
    ]

    ci = pd.DataFrame(dict((k, data[k]) for k in keys if k in data))

    ci[["upstream", "downstream"]] = pd.DataFrame(
        pd.Series(
            [
                coastalImpacts(
                    month,
                    ontLevel,
                    alexbayLevel,
                    cardinalLevel,
                    lerybeauharnoisLevel,
                    ptclaireLevel,
                    maskinongeLevel,
                    sorelLevel,
                    lacstpierreLevel,
                    troisrivieresLevel,
                    staticOntarioImpacts,
                    staticAlexBayImpacts,
                    staticCardinalImpacts,
                    staticBeauImpacts,
                    staticPtClaireImpacts,
                    staticMaskinongeImpacts,
                    staticLacStPierreImpacts,
                    staticSorelImpacts,
                    staticTroisRivieresImpacts,
                    dynamicOntarioImpacts,
                )[:2]
                for (
                    month,
                    ontLevel,
                    alexbayLevel,
                    cardinalLevel,
                    lerybeauharnoisLevel,
                    ptclaireLevel,
                    maskinongeLevel,
                    sorelLevel,
                    lacstpierreLevel,
                    troisrivieresLevel,
                ) in zip(
                    ci["Month"],
                    ci["ontLevel"],
                    ci["alexbayLevel"],
                    ci["cardinalLevel"],
                    ci["lerybeauharnoisLevel"],
                    ci["ptclaireLevel"],
                    ci["maskinongeLevel"],
                    ci["sorelLevel"],
                    ci["lacstpierreLevel"],
                    ci["troisrivieresLevel"],
                )
            ]
        ).tolist(),
        index=ci.index,
    )

    # ---------------------------------
    # commercial navigation
    # ---------------------------------

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
    cn = dict((k, data[k]) for k in keys if k in data)

    # calculate the difference in jetty1 levels between qms
    cn["jettyChange"] = np.diff(cn["jetty1Level"], prepend=cn["jetty1Level"][0])

    # get previous freshet values
    cn["freshetIndicator"] = cn["freshetIndicator"].astype(float)
    cn["freshetIndicatorPrevious"] = np.roll(cn["freshetIndicator"], 1)
    cn["freshetIndicatorPrevious"] = cn["freshetIndicatorPrevious"].astype(float)
    cn["freshetIndicatorPrevious"][0] = np.nan

    # initialize rows
    timesteps = len(cn["Sim"])
    cn["rPW"] = np.array([np.nan] * timesteps)
    cn["conPW"] = np.array([np.nan] * timesteps)

    # constant for conversions
    daysperQM = 7.609

    for i in range(timesteps):
        kingstonLevel = cn["kingstonLevel"][i]
        ogdensburgLevel = cn["ogdensburgLevel"][i]
        cardinalLevel = cn["cardinalLevel"][i]
        iroquoishwLevel = cn["iroquoishwLevel"][i]
        iroquoistwLevel = cn["iroquoistwLevel"][i]
        morrisburgLevel = cn["morrisburgLevel"][i]
        longsaultLevel = cn["longsaultLevel"][i]
        summerstownLevel = cn["summerstownLevel"][i]
        ptclaireLevel = cn["ptclaireLevel"][i]

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
        cn["rPW"][i] = rPW
        cn["conPW"][i] = conPW

    # cn = pd.DataFrame(cn)
    cn["prevconPW"] = np.roll(cn["conPW"], 1)
    cn["prevconPW"][0] = 0

    cn = pd.DataFrame(cn)

    cn["value"] = np.array(
        [
            commercialNavigation(
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
            )[0]
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
                cn["QM"],
                cn["ontLevel"],
                cn["kingstonLevel"],
                cn["ogdensburgLevel"],
                cn["cardinalLevel"],
                cn["iroquoishwLevel"],
                cn["iroquoistwLevel"],
                cn["morrisburgLevel"],
                cn["longsaultLevel"],
                cn["summerstownLevel"],
                cn["ptclaireLevel"],
                cn["stlambertLevel"],
                cn["jetty1Level"],
                cn["jettyChange"],
                cn["sorelLevel"],
                cn["troisrivieresLevel"],
                cn["ontFlow"],
                cn["iceInd"],
                cn["freshetIndicator"],
                cn["freshetIndicatorPrevious"],
                cn["rPW"],
                cn["conPW"],
                cn["prevconPW"],
            )
        ]
    )

    # ---------------------------------
    # hydropower
    # ---------------------------------

    # returns the value of hydropower production in USD
    keys = [
        "Sim",
        "Year",
        "Month",
        "QM",
        "ontFlow",
        "erieOut",
        "ontLevel",
        "saundershwLevel",
        "saunderstwLevel",
    ]

    hydro = pd.DataFrame(dict((k, data[k]) for k in keys if k in data))

    hydro["value"] = np.array(
        [
            hydropower(
                qm, ontFlow, erieOut, ontLevel, saundershwLevel, saunderstwLevel
            )[0]
            for (
                qm,
                ontFlow,
                erieOut,
                ontLevel,
                saundershwLevel,
                saunderstwLevel,
            ) in zip(
                hydro["QM"],
                hydro["ontFlow"],
                hydro["erieOut"],
                hydro["ontLevel"],
                hydro["saundershwLevel"],
                hydro["saunderstwLevel"],
            )
        ]
    )

    # ---------------------------------
    # meadow marsh
    # ---------------------------------

    # meadow marsh area (returns data frame of meadow marsh area in low supply years)
    keys = ["Sim", "Year", "Month", "QM", "ontLevel"]
    mmLevels = pd.DataFrame(dict((k, data[k]) for k in keys if k in data))

    keys = ["Sim", "Year", "Month", "QM", "ontNTS"]
    mmNTS = pd.DataFrame(dict((k, data[k]) for k in keys if k in data))

    mm = meadowMarsh(mmLevels, mmNTS, mmAreaContours)

    # only keep years of low supplies
    mm = mm.loc[mm["lowSupplyYear"] == 1]

    # ---------------------------------
    # muskrat house viability (%)
    # ---------------------------------

    # locations to calculate with gage name
    locs = pd.DataFrame(
        {
            "Location": ["Alexandria Bay"],  # ["Lake St. Pierre", "Lake St. Louis"],
            "Gage": ["alexbayLevel"],  # ["lacstpierreLevel", "ptclaireLevel"],
        }
    )

    # muskrat house density (returns data frame of annual muskrat house density)
    keys = ["Sim", "Year", "Month", "QM"] + locs.loc[:, "Gage"].to_list()
    muskratLevels = pd.DataFrame(dict((k, data[k]) for k in keys if k in data))

    muskrat = muskratHouseViability(muskratLevels, locs, muskratCoefficients)

    # ---------------------------------
    # recreational boating
    # ---------------------------------

    # returns the recreational boating impacts in USD
    keys = [
        "Sim",
        "Year",
        "Month",
        "QM",
        "ontLevel",
        "alexbayLevel",
        "ogdensburgLevel",
        "brockvilleLevel",
        "longsaultLevel",
        "ptclaireLevel",
        "varennesLevel",
        "sorelLevel",
    ]

    rb = pd.DataFrame(dict((k, data[k]) for k in keys if k in data))

    rb["value"] = np.array(
        [
            recreationalBoating(
                qm,
                month,
                ontLevel,
                alexbayLevel,
                ogdensburgLevel,
                brockvilleLevel,
                longsaultLevel,
                ptclaireLevel,
                varennesLevel,
                sorelLevel,
                rbOntarioImpacts,
                rbAlexBayImpacts,
                rbOgdensburgImpacts,
                rbBrockvilleImpacts,
                rbLongSaultImpacts,
                rbPtClaireImpacts,
                rbVarennesImpacts,
                rbSorelImpacts,
            )[0]
            for (
                qm,
                month,
                ontLevel,
                alexbayLevel,
                ogdensburgLevel,
                brockvilleLevel,
                longsaultLevel,
                ptclaireLevel,
                varennesLevel,
                sorelLevel,
            ) in zip(
                rb["QM"],
                rb["Month"],
                rb["ontLevel"],
                rb["alexbayLevel"],
                rb["ogdensburgLevel"],
                rb["brockvilleLevel"],
                rb["longsaultLevel"],
                rb["ptclaireLevel"],
                rb["varennesLevel"],
                rb["sorelLevel"],
            )
        ]
    )

    # # aggregation
    # if metricWeighting == "netAnnualAverage":
    objs = [
        ci.groupby("Year")["upstream"].sum().mean(),
        ci.groupby("Year")["downstream"].sum().mean(),
        cn.groupby("Year")["value"].sum().mean(),
        -hydro.groupby("Year")["value"].sum().mean(),
        -mm.groupby("Year")["Area"].sum().mean(),
        # -muskrat.groupby("Year")["houseDensity"].sum().mean(),
        -muskrat.groupby("Year")["probLodgeViability"].sum().mean(),
        rb.groupby("Year")["value"].sum().mean(),
    ]
    # elif metricWeighting == "weightedLocation":
    #     objs = [
    #         ci.groupby("Year")["upstream"].sum().mean(),
    #     ci.groupby("Year")["downstream"].sum().mean(),
    #     cn.groupby("Year")["value"].sum().mean(),
    #     -hydro.groupby("Year")["value"].sum().mean(),
    #     -mm.groupby("Year")["Area"].sum().mean(),
    #     # -muskrat.groupby("Year")["houseDensity"].sum().mean(),
    #     -muskrat.groupby("Year")["probLodgeViability"].sum().mean(),
    #     rb.groupby("Year")["value"].sum().mean()
    #     ]

    return objs


# -----------------------------------------------------------------------------
# evaluate objective functions over simulation output and return time series
# -----------------------------------------------------------------------------


# returns annual average of each objective
def objectiveSimulation(
    data,  # dataframe of simulated output
    output,  # simulation, netAnnualAverage, percentDiff
):
    # ---------------------------------
    # coastal impacts
    # ---------------------------------

    # coastal impacts (returns the number of buildings impacted upstream and downstream)
    keys = [
        "Sim",
        "Year",
        "Month",
        "QM",
        "ontLevel",
        "alexbayLevel",
        "cardinalLevel",
        "lerybeauharnoisLevel",
        "ptclaireLevel",
        "maskinongeLevel",
        "sorelLevel",
        "lacstpierreLevel",
        "troisrivieresLevel",
    ]

    ci = pd.DataFrame(dict((k, data[k]) for k in keys if k in data))

    ci[
        [
            "upstreamCoastal",
            "downstreamCoastal",
            "ontarioCoastal",
            "alexbayCoastal",
            "cardinalCoastal",
            "lerybeauharnoisCoastal",
            "ptclaireCoastal",
            "maskinongeCoastal",
            "lacstpierreCoastal",
            "sorelCoastal",
            "troisrivieresCoastal",
        ]
    ] = pd.DataFrame(
        pd.Series(
            [
                coastalImpacts(
                    month,
                    ontLevel,
                    alexbayLevel,
                    cardinalLevel,
                    lerybeauharnoisLevel,
                    ptclaireLevel,
                    maskinongeLevel,
                    sorelLevel,
                    lacstpierreLevel,
                    troisrivieresLevel,
                    staticOntarioImpacts,
                    staticAlexBayImpacts,
                    staticCardinalImpacts,
                    staticBeauImpacts,
                    staticPtClaireImpacts,
                    staticMaskinongeImpacts,
                    staticLacStPierreImpacts,
                    staticSorelImpacts,
                    staticTroisRivieresImpacts,
                    dynamicOntarioImpacts,
                )
                for (
                    month,
                    ontLevel,
                    alexbayLevel,
                    cardinalLevel,
                    lerybeauharnoisLevel,
                    ptclaireLevel,
                    maskinongeLevel,
                    sorelLevel,
                    lacstpierreLevel,
                    troisrivieresLevel,
                ) in zip(
                    ci["Month"],
                    ci["ontLevel"],
                    ci["alexbayLevel"],
                    ci["cardinalLevel"],
                    ci["lerybeauharnoisLevel"],
                    ci["ptclaireLevel"],
                    ci["maskinongeLevel"],
                    ci["sorelLevel"],
                    ci["lacstpierreLevel"],
                    ci["troisrivieresLevel"],
                )
            ]
        ).tolist(),
        index=ci.index,
    )

    # ---------------------------------
    # commercial navigation
    # ---------------------------------

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
    cn = dict((k, data[k]) for k in keys if k in data)

    # calculate the difference in jetty1 levels between qms
    cn["jettyChange"] = np.diff(cn["jetty1Level"], prepend=cn["jetty1Level"][0])

    # get previous freshet values
    cn["freshetIndicatorPrevious"] = np.roll(cn["freshetIndicator"], 1)
    cn["freshetIndicatorPrevious"][0] = np.nan

    # initialize rows
    timesteps = len(cn["Sim"])
    cn["rPW"] = np.array([np.nan] * timesteps)
    cn["conPW"] = np.array([np.nan] * timesteps)

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

        kingstonLevel = cn["kingstonLevel"][i]
        ogdensburgLevel = cn["ogdensburgLevel"][i]
        cardinalLevel = cn["cardinalLevel"][i]
        iroquoishwLevel = cn["iroquoishwLevel"][i]
        iroquoistwLevel = cn["iroquoistwLevel"][i]
        morrisburgLevel = cn["morrisburgLevel"][i]
        longsaultLevel = cn["longsaultLevel"][i]
        summerstownLevel = cn["summerstownLevel"][i]
        ptclaireLevel = cn["ptclaireLevel"][i]

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
        cn["rPW"][i] = rPW
        cn["conPW"][i] = conPW

    # cn = pd.DataFrame(cn)
    cn["prevconPW"] = np.roll(cn["conPW"], 1)
    cn["prevconPW"][0] = 0

    cn = pd.DataFrame(cn)

    cn[
        [
            "totalCommercialNavigation",
            "ontarioCommercialNavigation",
            "seawayCommercialNavigation",
            "montrealCommercialNavigation",
        ]
    ] = np.array(
        [
            commercialNavigation(
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
                cn["QM"],
                cn["ontLevel"],
                cn["kingstonLevel"],
                cn["ogdensburgLevel"],
                cn["cardinalLevel"],
                cn["iroquoishwLevel"],
                cn["iroquoistwLevel"],
                cn["morrisburgLevel"],
                cn["longsaultLevel"],
                cn["summerstownLevel"],
                cn["ptclaireLevel"],
                cn["stlambertLevel"],
                cn["jetty1Level"],
                cn["jettyChange"],
                cn["sorelLevel"],
                cn["troisrivieresLevel"],
                cn["ontFlow"],
                cn["iceInd"],
                cn["freshetIndicator"],
                cn["freshetIndicatorPrevious"],
                cn["rPW"],
                cn["conPW"],
                cn["prevconPW"],
            )
        ]
    )

    # --------------------------------
    # hydropower
    # ---------------------------------

    # returns the value of hydropower production in USD
    keys = [
        "Sim",
        "Year",
        "Month",
        "QM",
        "ontFlow",
        "erieOut",
        "ontLevel",
        "saundershwLevel",
        "saunderstwLevel",
    ]
    hydro = pd.DataFrame(dict((k, data[k]) for k in keys if k in data))

    hydro[
        [
            "totalEnergyValue",
            "opgMosesSaundersEnergyValue",
            "nypaMosesSaundersEnergyValue",
            "opgNiagaraEnergyValue",
            "nypaNiagaraEnergyValue",
            "peakingMosesSaundersValue",
        ]
    ] = np.array(
        [
            hydropower(qm, ontFlow, erieOut, ontLevel, saundershwLevel, saunderstwLevel)
            for (
                qm,
                ontFlow,
                erieOut,
                ontLevel,
                saundershwLevel,
                saunderstwLevel,
            ) in zip(
                hydro["QM"],
                hydro["ontFlow"],
                hydro["erieOut"],
                hydro["ontLevel"],
                hydro["saundershwLevel"],
                hydro["saunderstwLevel"],
            )
        ]
    )

    # ---------------------------------
    # meadow marsh
    # ---------------------------------

    # meadow marsh area (returns data frame of meadow marsh area in low supply years)
    keys = ["Sim", "Year", "Month", "QM", "ontLevel"]
    mmLevels = pd.DataFrame(dict((k, data[k]) for k in keys if k in data))

    keys = ["Sim", "Year", "Month", "QM", "ontNTS"]
    mmNTS = pd.DataFrame(dict((k, data[k]) for k in keys if k in data))

    totalArea = meadowMarsh(mmLevels, mmNTS, mmAreaContours)

    # # ---------------------------------
    # # muskrat house density - OLD PI, returned weird results replaced with house viability PI from ISEE team
    # # ---------------------------------

    # # muskrat house density (returns data frame of annual muskrat house density)
    # keys = ["Sim", "Year", "Month", "QM", "alexbayLevel"]
    # mmLevels = pd.DataFrame(dict((k, data[k]) for k in keys if k in data))

    # keys = ["Sim", "Year", "QM", "airTemp", "freezingDiff"]
    # mmAirTemps = pd.DataFrame(dict((k, data[k]) for k in keys if k in data))

    # muskrat = muskratDensity(mmLevels, mmAirTemps, mmElevZones)

    # ---------------------------------
    # muskrat house viability (%)
    # ---------------------------------

    # locations to calculate with gage name
    locs = pd.DataFrame(
        {
            "Location": ["Alexandria Bay"],  # ["Lake St. Pierre", "Lake St. Louis"],
            "Gage": ["alexbayLevel"],  # ["lacstpierreLevel", "ptclaireLevel"],
        }
    )

    # muskrat house density (returns data frame of annual muskrat house density)
    keys = ["Sim", "Year", "Month", "QM"] + locs.loc[:, "Gage"].to_list()
    muskratLevels = pd.DataFrame(dict((k, data[k]) for k in keys if k in data))

    muskrat = muskratHouseViability(muskratLevels, locs, muskratCoefficients)

    # ---------------------------------
    # recreational boating
    # ---------------------------------

    # returns the recreational boating impacts in USD
    keys = [
        "Sim",
        "Year",
        "Month",
        "QM",
        "ontLevel",
        "alexbayLevel",
        "ogdensburgLevel",
        "brockvilleLevel",
        "longsaultLevel",
        "ptclaireLevel",
        "varennesLevel",
        "sorelLevel",
    ]
    rb = pd.DataFrame(dict((k, data[k]) for k in keys if k in data))

    rb[
        [
            "totalRecBoating",
            "ontarioRecBoating",
            "alexbayRecBoating",
            "ogdensburgRecBoating",
            "brockvilleRecBoating",
            "longsaultRecBoating",
            "ptclaireRecBoating",
            "varennesRecBoating",
            "sorelRecBoating",
        ]
    ] = np.array(
        [
            recreationalBoating(
                qm,
                month,
                ontLevel,
                alexbayLevel,
                ogdensburgLevel,
                brockvilleLevel,
                longsaultLevel,
                ptclaireLevel,
                varennesLevel,
                sorelLevel,
                rbOntarioImpacts,
                rbAlexBayImpacts,
                rbOgdensburgImpacts,
                rbBrockvilleImpacts,
                rbLongSaultImpacts,
                rbPtClaireImpacts,
                rbVarennesImpacts,
                rbSorelImpacts,
            )
            for (
                qm,
                month,
                ontLevel,
                alexbayLevel,
                ogdensburgLevel,
                brockvilleLevel,
                longsaultLevel,
                ptclaireLevel,
                varennesLevel,
                sorelLevel,
            ) in zip(
                rb["QM"],
                rb["Month"],
                rb["ontLevel"],
                rb["alexbayLevel"],
                rb["ogdensburgLevel"],
                rb["brockvilleLevel"],
                rb["longsaultLevel"],
                rb["ptclaireLevel"],
                rb["varennesLevel"],
                rb["sorelLevel"],
            )
        ]
    )

    # -----------------------------------------------------
    # format for ouput
    # -----------------------------------------------------

    ci = ci[
        [
            "Sim",
            "Year",
            "Month",
            "QM",
            "upstreamCoastal",
            "downstreamCoastal",
            "ontarioCoastal",
            "alexbayCoastal",
            "cardinalCoastal",
            "lerybeauharnoisCoastal",
            "ptclaireCoastal",
            "maskinongeCoastal",
            "lacstpierreCoastal",
            "sorelCoastal",
            "troisrivieresCoastal",
        ]
    ]

    cn = cn[
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

    hydro = hydro[
        [
            "Sim",
            "Year",
            "Month",
            "QM",
            "totalEnergyValue",
            "opgMosesSaundersEnergyValue",
            "nypaMosesSaundersEnergyValue",
            "opgNiagaraEnergyValue",
            "nypaNiagaraEnergyValue",
            "peakingMosesSaundersValue",
        ]
    ]

    totalArea.columns = ["Year", "mmArea", "mmLowSupply"]
    totalArea["QM"] = [48] * totalArea.shape[0]

    muskrat.columns = ["Year", "muskratProbLodgeViability", "Location"]
    muskrat["QM"] = [48] * muskrat.shape[0]

    rb = rb[
        [
            "Sim",
            "Year",
            "Month",
            "QM",
            "totalRecBoating",
            "ontarioRecBoating",
            "alexbayRecBoating",
            "ogdensburgRecBoating",
            "brockvilleRecBoating",
            "longsaultRecBoating",
            "ptclaireRecBoating",
            "varennesRecBoating",
            "sorelRecBoating",
        ]
    ]

    # return timeseries over simulation period of PI values
    if output == "simulation":
        return ci, cn, hydro, totalArea, muskrat, rb

    # return the net annual average PI values (sum up each year, take the mean of the yearly values)
    elif output == "netAnnualAverage":
        objs = [
            ci.groupby("Year")["upstreamCoastal"].sum().mean(),
            ci.groupby("Year")["downstreamCoastal"].sum().mean(),
            cn.groupby("Year")["totalCommercialNavigation"].sum().mean(),
            -hydro.groupby("Year")["totalEnergyValue"].sum().mean(),
            -totalArea.loc[totalArea["mmLowSupply"] == 1]
            .groupby("Year")["mmArea"]
            .sum()
            .mean(),
            -muskrat.groupby("Year")["muskratProbLodgeViability"].sum().mean(),
            rb.groupby("Year")["totalRecBoating"].sum().mean(),
        ]

        return objs

    # return location weighted PI values (normalize each PI location by the baseline Bv7 value)
    elif output == "percentDiff":
        # join for easier calling
        ts = (
            ci.merge(cn, on=["Sim", "Year", "Month", "QM"], how="outer")
            .merge(hydro, on=["Sim", "Year", "Month", "QM"], how="outer")
            .merge(totalArea, on=["Year", "QM"], how="outer")
            .merge(
                muskrat.loc[:, ["Year", "QM", "muskratProbLodgeViability"]],
                on=["Year", "QM"],
                how="outer",
            )
            .merge(rb, on=["Sim", "Year", "Month", "QM"], how="outer")
        ).sort_values("Sim")

        # upstream coastal impacts
        ucLocs = ["ontarioCoastal", "alexbayCoastal", "cardinalCoastal"]
        ucObjs = (
            ts.loc[:, ["Year", "QM"] + ucLocs]
            .melt(id_vars=["Year", "QM"], var_name="Loc", value_name="PI")
            .groupby(["Year", "Loc"], as_index=False)["PI"]
            .sum()
            .groupby("Loc", as_index=False)["PI"]
            .mean()
        )

        # downstream coastal impacts
        dcLocs = [
            "lerybeauharnoisCoastal",
            "ptclaireCoastal",
            "maskinongeCoastal",
            "lacstpierreCoastal",
            "sorelCoastal",
            "troisrivieresCoastal",
        ]
        dcObjs = (
            ts.loc[:, ["Year", "QM"] + dcLocs]
            .melt(id_vars=["Year", "QM"], var_name="Loc", value_name="PI")
            .groupby(["Year", "Loc"], as_index=False)["PI"]
            .sum()
            .groupby("Loc", as_index=False)["PI"]
            .mean()
        )

        # commercial navigation costs
        cnLocs = [
            "ontarioCommercialNavigation",
            "seawayCommercialNavigation",
            "montrealCommercialNavigation",
        ]
        cnObjs = (
            ts.loc[:, ["Year", "QM"] + cnLocs]
            .melt(id_vars=["Year", "QM"], var_name="Loc", value_name="PI")
            .groupby(["Year", "Loc"], as_index=False)["PI"]
            .sum()
            .groupby("Loc", as_index=False)["PI"]
            .mean()
        )

        # hydropower production value
        hpLocs = [
            "opgMosesSaundersEnergyValue",
            "nypaMosesSaundersEnergyValue",
            "opgNiagaraEnergyValue",
            "nypaNiagaraEnergyValue",
            "peakingMosesSaundersValue",
        ]
        hpObjs = (
            ts.loc[:, ["Year", "QM"] + hpLocs]
            .melt(id_vars=["Year", "QM"], var_name="Loc", value_name="PI")
            .groupby(["Year", "Loc"], as_index=False)["PI"]
            .sum()
            .groupby("Loc", as_index=False)["PI"]
            .mean()
        )

        # meadow marsh area
        # filter by low supply years and average
        mmLocs = ["ontarioMeadowMarsh"]
        mmObjs = pd.DataFrame(
            {
                "Loc": mmLocs,
                "PI": [ts.loc[ts["mmLowSupply"] == 1, "mmArea"].mean()],
            }
        )

        # muskrat house viability
        mkLocs = ["alexbayMuskratViability"]
        mkObjs = pd.DataFrame(
            {
                "Loc": mkLocs,
                "PI": [ts.loc[:, "muskratProbLodgeViability"].dropna().mean()],
            }
        )

        # recreational boating costs
        rbLocs = [
            "ontarioRecBoating",
            "alexbayRecBoating",
            "ogdensburgRecBoating",
            "brockvilleRecBoating",
            "longsaultRecBoating",
            "ptclaireRecBoating",
            "varennesRecBoating",
            "sorelRecBoating",
        ]
        rbObjs = (
            ts.loc[:, ["Year", "QM"] + rbLocs]
            .melt(id_vars=["Year", "QM"], var_name="Loc", value_name="PI")
            .groupby(["Year", "Loc"], as_index=False)["PI"]
            .sum()
            .groupby("Loc", as_index=False)["PI"]
            .mean()
        )

        # group net annual averages and join with baseline values
        naa = (
            pd.concat([ucObjs, dcObjs, cnObjs, hpObjs, mmObjs, mkObjs, rbObjs])
            .reset_index(drop=True)
            .merge(bv7, on="Loc")
        )
        naa["normPI"] = ((naa["PI"] - naa["Bv7"]) / naa["Bv7"]) * 100

        objs = [
            naa.loc[naa["Loc"].isin(ucLocs), "normPI"].mean(),
            naa.loc[naa["Loc"].isin(dcLocs), "normPI"].mean(),
            naa.loc[naa["Loc"].isin(cnLocs), "normPI"].mean(),
            naa.loc[naa["Loc"].isin(hpLocs), "normPI"].mean() * -1,
            naa.loc[naa["Loc"].isin(mmLocs), "normPI"].mean() * -1,
            naa.loc[naa["Loc"].isin(mkLocs), "normPI"].mean() * -1,
            naa.loc[naa["Loc"].isin(rbLocs), "normPI"].mean(),
        ]

        return objs

    else:
        return "invalid output selected"
