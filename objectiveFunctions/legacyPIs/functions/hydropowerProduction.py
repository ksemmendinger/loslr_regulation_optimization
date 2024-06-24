#!/usr/bin/env python3

# import libraries
import numpy as np
import pandas as pd

# -----------------------------------------------------------------------------
# hydropower production value ($)
# -----------------------------------------------------------------------------


def piModel(qm, ontFlow, erieOut, ontLevel, saundershwLevel, saunderstwLevel):
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


def runModel(data):
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
    piOutput = pd.DataFrame(dict((k, data[k]) for k in keys if k in data))

    piOutput[
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
            piModel(qm, ontFlow, erieOut, ontLevel, saundershwLevel, saunderstwLevel)
            for (
                qm,
                ontFlow,
                erieOut,
                ontLevel,
                saundershwLevel,
                saunderstwLevel,
            ) in zip(
                piOutput["QM"],
                piOutput["ontFlow"],
                piOutput["erieOut"],
                piOutput["ontLevel"],
                piOutput["saundershwLevel"],
                piOutput["saunderstwLevel"],
            )
        ]
    )

    piOutput = piOutput[
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

    return piOutput
