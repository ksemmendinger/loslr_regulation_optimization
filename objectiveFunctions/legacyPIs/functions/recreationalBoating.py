#!/usr/bin/env python3

# import libraries
import numpy as np
import pandas as pd

# -----------------------------------------------------------------------------
# recreational boating costs ($)
# -----------------------------------------------------------------------------

# load recreational boating costs for all locations
rbOntarioImpacts = pd.read_csv("objectiveFunctions/legacyPIs/data/rbOntarioImpacts.csv")
rbOntarioImpacts = {x: rbOntarioImpacts[x].values for x in rbOntarioImpacts}

rbAlexBayImpacts = pd.read_csv("objectiveFunctions/legacyPIs/data/rbAlexBayImpacts.csv")
rbAlexBayImpacts = {x: rbAlexBayImpacts[x].values for x in rbAlexBayImpacts}

rbOgdensburgImpacts = pd.read_csv(
    "objectiveFunctions/legacyPIs/data/rbOgdensburgImpacts.csv"
)
rbOgdensburgImpacts = {x: rbOgdensburgImpacts[x].values for x in rbOgdensburgImpacts}

rbBrockvilleImpacts = pd.read_csv(
    "objectiveFunctions/legacyPIs/data/rbBrockvilleImpacts.csv"
)
rbBrockvilleImpacts = {x: rbBrockvilleImpacts[x].values for x in rbBrockvilleImpacts}

rbLongSaultImpacts = pd.read_csv(
    "objectiveFunctions/legacyPIs/data/rbLongSaultImpacts.csv"
)
rbLongSaultImpacts = {x: rbLongSaultImpacts[x].values for x in rbLongSaultImpacts}

rbPtClaireImpacts = pd.read_csv(
    "objectiveFunctions/legacyPIs/data/rbPtClaireImpacts.csv"
)
rbPtClaireImpacts = {x: rbPtClaireImpacts[x].values for x in rbPtClaireImpacts}

rbVarennesImpacts = pd.read_csv(
    "objectiveFunctions/legacyPIs/data/rbVarennesImpacts.csv"
)
rbVarennesImpacts = {x: rbVarennesImpacts[x].values for x in rbVarennesImpacts}

rbSorelImpacts = pd.read_csv("objectiveFunctions/legacyPIs/data/rbSorelImpacts.csv")
rbSorelImpacts = {x: rbSorelImpacts[x].values for x in rbSorelImpacts}


# returns the recreational boating impacts in USD
def piModel(
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


def runModel(data):
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
    piOutput = pd.DataFrame(dict((k, data[k]) for k in keys if k in data))

    piOutput[
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
            piModel(
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
                piOutput["QM"],
                piOutput["Month"],
                piOutput["ontLevel"],
                piOutput["alexbayLevel"],
                piOutput["ogdensburgLevel"],
                piOutput["brockvilleLevel"],
                piOutput["longsaultLevel"],
                piOutput["ptclaireLevel"],
                piOutput["varennesLevel"],
                piOutput["sorelLevel"],
            )
        ]
    )

    piOutput = piOutput[
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

    return piOutput
