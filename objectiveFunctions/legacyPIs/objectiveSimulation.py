#!/usr/bin/env python3

# import numpy as np
# import pandas as pd

# -----------------------------------------------------------------------------
# evaluate objective functions over simulation output and return time series
# -----------------------------------------------------------------------------


def objectiveSimulation(
    data,  # dataframe of simulated water levels and flows
    piModels,  # list of pi modules loaded in `optimizationWrapper`
    output,  # simulation, netAnnualAverage, percentDiff
):
    piOutput = []
    for pi in piModels:
        tmpOutput = pi.runModel(data)
        piOutput.append(tmpOutput)

    # save each pi output as its own data frame
    uc = piOutput[0]
    dc = piOutput[1]
    cn = piOutput[2]
    hydro = piOutput[3]
    totalArea = piOutput[4]
    muskrat = piOutput[5]
    rb = piOutput[6]

    # return timeseries over simulation period of PI values
    if output == "simulation":
        return uc, dc, cn, hydro, totalArea, muskrat, rb

    # return the net annual average PI values (sum up each year, take the mean of the yearly values)
    elif output == "netAnnualAverage":
        objs = [
            uc.groupby("Year")["upstreamCoastal"].sum().mean(),
            dc.groupby("Year")["downstreamCoastal"].sum().mean(),
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

    else:
        return "invalid output selected"
