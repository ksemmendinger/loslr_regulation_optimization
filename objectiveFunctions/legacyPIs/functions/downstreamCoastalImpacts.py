#!/usr/bin/env python3

# import libraries
import numpy as np
import pandas as pd


# -----------------------------------------------------------------------------
# coastal impacts to buildings [upstream and downstream] (#)
# -----------------------------------------------------------------------------

staticBeauImpacts = pd.read_csv(
    "objectiveFunctions/legacyPIs/data/coastalBeauStaticImpacts.csv"
)
staticBeauImpacts = {x: staticBeauImpacts[x].values for x in staticBeauImpacts}

staticPtClaireImpacts = pd.read_csv(
    "objectiveFunctions/legacyPIs/data/coastalPtClaireStaticImpacts.csv"
)
staticPtClaireImpacts = {
    x: staticPtClaireImpacts[x].values for x in staticPtClaireImpacts
}

staticMaskinongeImpacts = pd.read_csv(
    "objectiveFunctions/legacyPIs/data/coastalMaskinongeStaticImpacts.csv"
)
staticMaskinongeImpacts = {
    x: staticMaskinongeImpacts[x].values for x in staticMaskinongeImpacts
}

staticLacStPierreImpacts = pd.read_csv(
    "objectiveFunctions/legacyPIs/data/coastalLacStPierreStaticImpacts.csv"
)
staticLacStPierreImpacts = {
    x: staticLacStPierreImpacts[x].values for x in staticLacStPierreImpacts
}

staticSorelImpacts = pd.read_csv(
    "objectiveFunctions/legacyPIs/data/coastalSorelStaticImpacts.csv"
)
staticSorelImpacts = {x: staticSorelImpacts[x].values for x in staticSorelImpacts}

staticTroisRivieresImpacts = pd.read_csv(
    "objectiveFunctions/legacyPIs/data/coastalTroisRivieresStaticImpacts.csv"
)
staticTroisRivieresImpacts = {
    x: staticTroisRivieresImpacts[x].values for x in staticTroisRivieresImpacts
}


# returns the number of buildings impacted downstream
def piModel(
    lerybeauharnoisLevel,
    ptclaireLevel,
    maskinongeLevel,
    sorelLevel,
    lacstpierreLevel,
    troisrivieresLevel,
    staticBeauImpacts,
    staticPtClaireImpacts,
    staticMaskinongeImpacts,
    staticLacStPierreImpacts,
    staticSorelImpacts,
    staticTroisRivieresImpacts,
):
    # month: month (int)
    # lerybeauharnoisLevel: final beauharnois level (float)
    # ptclaireLevel: final pointe-claire level (float)
    # maskinongeLevel: final maskinonge level (float)
    # sorelLevel: final sorel level (float)
    # lacstpierreLevel: final lac st. pierre level (float)
    # troisrivieresLevel: final trois rivieres level (float)
    # staticXXXImpacts: expected impacts by water level for each location (dict)

    # -----------------------
    # for each location, find the index of the closest water level (levels below min,
    # use min - levels above max, use max). extract number of buildings impacted at index
    # additionally, for lake ontario, find dynamic impacts with the closest water level and month
    # -----------------------

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
    downstreamImpacts = (
        lerybeauharnoisDamages
        + ptclaireDamages
        + maskinongeDamages
        + lacstpierreDamages
        + sorelDamages
        + troisrivieresDamages
    )

    return (
        downstreamImpacts,
        lerybeauharnoisDamages,
        ptclaireDamages,
        maskinongeDamages,
        lacstpierreDamages,
        sorelDamages,
        troisrivieresDamages,
    )


def runModel(data):
    # coastal impacts (returns the number of buildings impacted upstream and downstream)
    keys = [
        "Sim",
        "Year",
        "Month",
        "QM",
        "lerybeauharnoisLevel",
        "ptclaireLevel",
        "maskinongeLevel",
        "sorelLevel",
        "lacstpierreLevel",
        "troisrivieresLevel",
    ]

    piOutput = pd.DataFrame(dict((k, data[k]) for k in keys if k in data))

    piOutput[
        [
            "downstreamCoastal",
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
                piModel(
                    lerybeauharnoisLevel,
                    ptclaireLevel,
                    maskinongeLevel,
                    sorelLevel,
                    lacstpierreLevel,
                    troisrivieresLevel,
                    staticBeauImpacts,
                    staticPtClaireImpacts,
                    staticMaskinongeImpacts,
                    staticLacStPierreImpacts,
                    staticSorelImpacts,
                    staticTroisRivieresImpacts,
                )
                for (
                    lerybeauharnoisLevel,
                    ptclaireLevel,
                    maskinongeLevel,
                    sorelLevel,
                    lacstpierreLevel,
                    troisrivieresLevel,
                ) in zip(
                    piOutput["lerybeauharnoisLevel"],
                    piOutput["ptclaireLevel"],
                    piOutput["maskinongeLevel"],
                    piOutput["sorelLevel"],
                    piOutput["lacstpierreLevel"],
                    piOutput["troisrivieresLevel"],
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
            "downstreamCoastal",
            "lerybeauharnoisCoastal",
            "ptclaireCoastal",
            "maskinongeCoastal",
            "lacstpierreCoastal",
            "sorelCoastal",
            "troisrivieresCoastal",
        ]
    ]
    return piOutput
