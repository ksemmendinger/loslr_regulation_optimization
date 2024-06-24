#!/usr/bin/env python3

# import libraries
import numpy as np
import pandas as pd

# -----------------------------------------------------------------------------
# probability of muskrat lodge viability (%)
# -----------------------------------------------------------------------------


# file with the various lodge (HUT) configurations (min, median and maximum) -> "PLV_HUT_3_375", "PLV_HUT_3_39", "PLV_HUT_3_51"
pd_meta = pd.read_csv("objectiveFunctions/legacyPIs/data/muskratCoefficients.csv")


def piModel(levels, locs, pd_meta):
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


def runModel(data):
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

    piOutput = piModel(muskratLevels, locs, pd_meta)

    piOutput.columns = ["Year", "muskratProbLodgeViability", "Location"]
    piOutput["QM"] = [48] * piOutput.shape[0]

    return piOutput
