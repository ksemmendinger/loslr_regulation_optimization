#!/usr/bin/env python3

# import libraries
import numpy as np
import pandas as pd

# -----------------------------------------------------------------------------
# coastal impacts to buildings [upstream and downstream] (#)
# -----------------------------------------------------------------------------

# load building impacts for upstream and downstream coastal locations
staticOntarioImpacts = pd.read_csv(
    "objectiveFunctions/legacyPIs/data/coastalOntarioStaticImpacts.csv"
)
staticOntarioImpacts = {x: staticOntarioImpacts[x].values for x in staticOntarioImpacts}

dynamicOntarioImpacts = pd.read_csv(
    "objectiveFunctions/legacyPIs/data/coastalOntarioDynamicImpacts.csv"
)
dynamicOntarioImpacts = {
    x: dynamicOntarioImpacts[x].values for x in dynamicOntarioImpacts
}

staticAlexBayImpacts = pd.read_csv(
    "objectiveFunctions/legacyPIs/data/coastalAlexBayStaticImpacts.csv"
)
staticAlexBayImpacts = {x: staticAlexBayImpacts[x].values for x in staticAlexBayImpacts}

staticCardinalImpacts = pd.read_csv(
    "objectiveFunctions/legacyPIs/data/coastalCardinalStaticImpacts.csv"
)
staticCardinalImpacts = {
    x: staticCardinalImpacts[x].values for x in staticCardinalImpacts
}


# returns the number of buildings impacted upstream
def piModel(
    month,
    ontLevel,
    alexbayLevel,
    cardinalLevel,
    staticOntarioImpacts,
    staticAlexBayImpacts,
    staticCardinalImpacts,
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

    # add upstream and downstream impacts
    upstreamImpacts = ontarioDamages + alexbayDamages + cardinalDamages

    return (
        upstreamImpacts,
        ontarioDamages,
        alexbayDamages,
        cardinalDamages,
    )


def runModel(data):
    # coastal impacts (returns the number of buildings impacted upstream and downstream)
    keys = [
        "Sim",
        "Year",
        "Month",
        "QM",
        "ontLevel",
        "alexbayLevel",
        "cardinalLevel",
    ]

    piOutput = pd.DataFrame(dict((k, data[k]) for k in keys if k in data))

    piOutput[
        [
            "upstreamCoastal",
            "ontarioCoastal",
            "alexbayCoastal",
            "cardinalCoastal",
        ]
    ] = pd.DataFrame(
        pd.Series(
            [
                piModel(
                    month,
                    ontLevel,
                    alexbayLevel,
                    cardinalLevel,
                    staticOntarioImpacts,
                    staticAlexBayImpacts,
                    staticCardinalImpacts,
                    dynamicOntarioImpacts,
                )
                for (
                    month,
                    ontLevel,
                    alexbayLevel,
                    cardinalLevel,
                ) in zip(
                    piOutput["Month"],
                    piOutput["ontLevel"],
                    piOutput["alexbayLevel"],
                    piOutput["cardinalLevel"],
                )
            ]
        ).tolist(),
        index=piOutput.index,
    )

    piOutput = piOutput[
        [
            "Sim",
            "Year",
            "Month",
            "QM",
            "upstreamCoastal",
            "ontarioCoastal",
            "alexbayCoastal",
            "cardinalCoastal",
        ]
    ]

    return piOutput
