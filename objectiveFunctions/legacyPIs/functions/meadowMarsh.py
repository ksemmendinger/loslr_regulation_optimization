#!/usr/bin/env python3

# import libraries
import numpy as np
import pandas as pd

# -----------------------------------------------------------------------------
# meadow marsh area (hectares)
# -----------------------------------------------------------------------------

# load area contours for meadow marsh area calculations
contours = pd.read_csv("objectiveFunctions/legacyPIs/data/mmContourAreas.csv")


def piModel(levels, nts, contours):
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


def runModel(data):
    # meadow marsh area (returns data frame of meadow marsh area in low supply years)
    keys = ["Sim", "Year", "Month", "QM", "ontLevel"]
    mmLevels = pd.DataFrame(dict((k, data[k]) for k in keys if k in data))

    keys = ["Sim", "Year", "Month", "QM", "ontNTS"]
    mmNTS = pd.DataFrame(dict((k, data[k]) for k in keys if k in data))

    piOutput = piModel(mmLevels, mmNTS, contours)

    piOutput.columns = ["Year", "mmArea", "mmLowSupply"]
    piOutput["QM"] = [48] * piOutput.shape[0]

    return piOutput
