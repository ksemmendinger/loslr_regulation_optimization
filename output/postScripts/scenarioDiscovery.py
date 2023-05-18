satisficingCrit = [0, 0, 0, -0.5, 0, 0, -10]

# import libraries
import os
import sys
import numpy as np
import pandas as pd
from glob import glob
from functools import partial
from concurrent.futures import ProcessPoolExecutor
from sklearn.ensemble import GradientBoostingClassifier

# set variables from command line input
args = sys.argv
# args = ["", "mac_loc", "12month", "0", "100000", "14", "4"]
# args = ["", "mac_loc", "baseline", 4]

# set working directory
if args[1] == "mac_loc":
    wd = "/Users/kylasemmendinger/Library/CloudStorage/Box-Box/Plan_2014/optimization/output"
elif args[1] == "hopper":
    wd = "/home/fs02/pmr82_0001/kts48/optimization/output"
os.chdir(wd)

if args[2] == "baseline":

    # folder name
    folderName = "baseline"

    # set number of workers
    nWorkers = int(args[3])

else:

    # forecast lead-time
    leadtime = args[2]

    # forecast skill
    skill = args[3]

    # number of function evaluations
    nfe = int(args[4])

    # number of decision variables
    nvars = int(args[5])

    # folder name
    folderName = (
        leadtime + "_" + str(skill) + "_" + str(nfe) + "nfe_" + str(nvars) + "dvs"
    )

    # set number of workers
    nWorkers = int(args[6])

# names of objectives
pis = [
    "Coastal Impacts: Upstream Buildings Impacted (#)",
    "Coastal Impacts: Downstream Buildings Impacted (#)",
    "Commercial Navigation: Ontario + Seaway + Montreal Transportation Costs ($)",
    "Hydropower: Moses-Saunders + Niagara Energy Value ($)",
    "Meadow Marsh: Area (ha)",
    "Muskrat House Density (%)",
    "Recreational Boating: Impact Costs ($)",
]

# thresholds for filtering data
dataFormat = pd.DataFrame(
    {
        "PI": pis,
        "piMultiplier": [-1, -1, -1, 1, 1, 1, -1],
        "lowerBounds": satisficingCrit,
        "roundDecimal": [0, 0, 2, 2, 0, 2, 0],
    }
)

# create folder for clean decision variable and objective files
newpath = "data/" + folderName + "/postAnalysis/scenarioDiscovery"
if not os.path.exists(newpath):
    os.makedirs(newpath)

# -----------------------------------------------------------------------------
# function to read time series data and get annual averages
# -----------------------------------------------------------------------------

# load data (for parallel run)
def readData(pis, fn):

    # read file and get relevant columns
    data = pd.read_parquet(fn).loc[
        :,
        [
            "Sim",
            "Year",
            "Month",
            "QM",
            "upstreamCoastal",
            "downstreamCoastal",
            "totalCommercialNavigation",
            "totalEnergyValue",
            "mmArea",
            "mmLowSupply",
            "muskratHouseDensity",
            "totalRecBoating",
            "ontNTS",
            "stlouisontOut",
            "iceInd",
        ],
    ]

    # state SOW for grouping
    sup = fn.split("/")[3]
    if sup == "stochastic":
        data["SOW"] = "Stochastic Century " + fn.split("/")[4].split("_")[1]
    elif sup == "historic":
        data["SOW"] = "Historic"
    elif sup == "climate_scenarios":
        data["SOW"] = fn.split("/")[4]

    # drop first and/or last year with no values
    df = data.dropna(
        subset=[
            "upstreamCoastal",
            "downstreamCoastal",
            "totalCommercialNavigation",
            "totalEnergyValue",
            "mmArea",
            "mmLowSupply",
            "muskratHouseDensity",
            "totalRecBoating",
        ],
        how="all",
    )

    # get objective performance and get net annual performance
    objs = (
        # select pi columns with QM-ly values
        df.loc[
            :,
            [
                "SOW",
                "Year",
                "upstreamCoastal",
                "downstreamCoastal",
                "totalCommercialNavigation",
                "totalEnergyValue",
                "muskratHouseDensity",
                "totalRecBoating",
            ],
        ]
        # get net annual scores
        .groupby(["SOW", "Year"], as_index=False).agg(
            upstreamCoastal=("upstreamCoastal", sum),
            downstreamCoastal=("downstreamCoastal", sum),
            totalCommercialNavigation=("totalCommercialNavigation", sum),
            totalEnergyValue=("totalEnergyValue", sum),
            muskratHouseDensity=("muskratHouseDensity", sum),
            totalRecBoating=("totalRecBoating", sum),
        )
    )

    mm = (
        df.loc[
            :,
            [
                "Year",
                "mmArea",
                "mmLowSupply",
            ],
        ]
        .dropna(axis=0, subset=["mmArea"])
        .reset_index(drop=True)
    )

    mm["mmLowSupplyArea"] = np.select(
        [mm["mmLowSupply"] == 1], [mm["mmArea"]], default=np.nan
    )

    mm = mm.loc[:, ["Year", "mmLowSupplyArea"]]
    mm.columns = ["Year", "mmArea"]

    # add clause in case NO years in a SOW century meet the low supply thresholds - set all years equal to 1 (not 0 because it's divided by later on)
    if mm["mmArea"].isnull().all():
        mm["mmArea"] = 1

    objs = objs.merge(mm, on="Year").loc[
        :,
        [
            "SOW",
            "Year",
            "upstreamCoastal",
            "downstreamCoastal",
            "totalCommercialNavigation",
            "totalEnergyValue",
            "mmArea",
            "muskratHouseDensity",
            "totalRecBoating",
        ],
    ]

    # take net annual average across SOW
    objs = objs.groupby(["SOW"], as_index=False).agg(
        upstreamCoastal=("upstreamCoastal", "mean"),
        downstreamCoastal=("downstreamCoastal", "mean"),
        totalCommercialNavigation=("totalCommercialNavigation", "mean"),
        totalEnergyValue=("totalEnergyValue", "mean"),
        mmArea=("mmArea", "mean"),
        muskratHouseDensity=("muskratHouseDensity", "mean"),
        totalRecBoating=("totalRecBoating", "mean"),
    )
    objs.columns = ["SOW"] + pis
    objs.insert(0, "Policy", fn.split("/")[-1].split(".parquet.gzip")[0])

    # get nts and slon and get net annual average values
    hydro = (
        data.loc[
            :,
            [
                "SOW",
                "Year",
                "Month",
                "QM",
                "ontNTS",
                "stlouisontOut",
            ],
        ]
        .groupby(["SOW", "Year"], as_index=False)
        .agg(
            ontNTS=("ontNTS", sum),
            stlouisontOut=("stlouisontOut", sum),
        )
        .groupby(["SOW"], as_index=False)
        .agg(ontNTS=("ontNTS", "mean"), stlouisontOut=("stlouisontOut", "mean"))
    )

    hydroSeasonal = data.loc[
        :,
        [
            "SOW",
            "Year",
            "Month",
            "QM",
            "ontNTS",
            "stlouisontOut",
        ],
    ]

    hydroSeasonal["Season"] = np.select(
        [
            hydroSeasonal["Month"].between(3, 5, inclusive="both"),
            hydroSeasonal["Month"].between(6, 8, inclusive="both"),
            hydroSeasonal["Month"].between(9, 11, inclusive="both"),
            hydroSeasonal["Month"].between(1, 2, inclusive="both"),
            hydroSeasonal["Month"] == 12,
        ],
        ["Spring", "Summer", "Fall", "Winter", "Winter"],
        default="Unknown",
    )

    hydroSeasonal = (
        hydroSeasonal.groupby(["SOW", "Year", "Season"], as_index=False)
        .agg(
            ontNTS=("ontNTS", sum),
            stlouisontOut=("stlouisontOut", sum),
        )
        .groupby(["SOW", "Season"], as_index=False)
        .agg(ontNTS=("ontNTS", "mean"), stlouisontOut=("stlouisontOut", "mean"))
        .pivot_table(index="SOW", columns="Season", values=["ontNTS", "stlouisontOut"])
        .reset_index()
    )

    hydroSeasonal.columns = [f"{x}{y}" for x, y in hydroSeasonal.columns]

    # get ice ind and get net annual average values
    ice = data.loc[
        :,
        [
            "SOW",
            "Year",
            "Month",
            "QM",
            "iceInd",
        ],
    ]

    ice["ice"] = np.select(
        [
            ice["iceInd"] == 2,
            ice["iceInd"] == 1,
            ice["iceInd"] == 0,
        ],
        [1, 0, 0],
        default=0,
    )

    ice = (
        ice.groupby(["SOW", "Year"], as_index=False)
        .agg(ice=("ice", sum))
        .groupby(["SOW"], as_index=False)
        .agg(unstableIce=("ice", "mean"))
    )

    hydro = hydro.merge(hydroSeasonal, on="SOW").merge(ice, on="SOW")
    hydro.insert(0, "Policy", fn.split("/")[-1].split(".parquet.gzip")[0])

    return hydro, objs


# -----------------------------------------------------------------------------
# read time series data and get annual averages
# -----------------------------------------------------------------------------

print("... reading data ...")

# load data from specified run
path = "data/" + folderName + "/simulation/**"
filelist = [f for f in glob(path, recursive=True) if os.path.isfile(f)]

objData = []
hydroVars = []

partialReadData = partial(readData, pis)

with ProcessPoolExecutor(max_workers=nWorkers) as executor:
    for tmpHydro, tmpObjs in executor.map(partialReadData, filelist):
        objData.append(tmpObjs)
        hydroVars.append(tmpHydro)

robustData = pd.concat(objData)
hydroData = pd.concat(hydroVars)

# -----------------------------------------------------------------------------
# save baseline or load baseline
# -----------------------------------------------------------------------------

if folderName == "baseline":

    # save baseline data to new variable
    baselineObjs = robustData

    # save baseline runs for future comparison
    robustData.to_csv(
        "data/" + folderName + "/postAnalysis/scenarioDiscovery/" + "baselineObjs.txt",
        sep="\t",
        index=False,
    )
    hydroData.to_csv(
        "data/" + folderName + "/postAnalysis/scenarioDiscovery/" + "baselineHydro.txt",
        sep="\t",
        index=False,
    )


elif folderName != "baseline":
    baselineObjs = pd.read_csv(
        "data/baseline/postAnalysis/scenarioDiscovery/baselineObjs.txt", sep="\t"
    )
    baselineHydro = pd.read_csv(
        "data/baseline/postAnalysis/scenarioDiscovery/baselineHydro.txt", sep="\t"
    )

# -----------------------------------------------------------------------------
# static Robustness
# -----------------------------------------------------------------------------

print("... starting static robustness ...")

# get baseline performance to normalize by
baseline = (
    baselineObjs.loc[
        (baselineObjs["SOW"] == "Historic")
        & (baselineObjs["Policy"] == "Plan_2014_Baseline"),
        pis,
    ]
    .melt(var_name="PI", value_name="baselineScore")
    .merge(dataFormat, on="PI")
)

# static robustness
staticRobustness = robustData.melt(
    id_vars=["Policy", "SOW"], var_name="PI", value_name="Score"
).merge(baseline, on="PI")

# normalize by baseline 2014
staticRobustness["normScore"] = (
    (
        (staticRobustness["Score"] - staticRobustness["baselineScore"])
        / staticRobustness["baselineScore"]
    )
    * staticRobustness["piMultiplier"]
    * 100
)

# round by the PI-specific threshold
staticRobustness["normScore"] = staticRobustness.apply(
    lambda df: float(round(df["normScore"], df["roundDecimal"])), axis=1
)

# determine whether the meets satisficing criteria
staticRobustness["robustScore"] = np.select(
    [staticRobustness["normScore"] >= staticRobustness["lowerBounds"]],
    [1],
    default=0,
)

# format
staticNorm = staticRobustness.pivot_table(
    index=["Policy", "SOW"], columns="PI", values="normScore"
).reset_index()

# format
staticRobustness = staticRobustness.pivot_table(
    index=["Policy", "SOW"], columns="PI", values="robustScore"
).reset_index()

# -----------------------------------------------------------------------------
# dynamic robustness
# -----------------------------------------------------------------------------

print("... starting dynamic robustness ...")

traces = robustData["SOW"].unique()

dynamicNorm = []
dynamicRobustness = []

for sow in traces:

    # get baseline performance to normalize by
    baseline = (
        baselineObjs.loc[
            (baselineObjs["SOW"] == sow)
            & (baselineObjs["Policy"] == "Plan_2014_Baseline"),
            pis,
        ]
        .melt(var_name="PI", value_name="baselineScore")
        .merge(dataFormat, on="PI")
    )

    # get SOW
    tmp = (
        robustData.loc[(robustData["SOW"] == sow), :]
        .melt(id_vars=["Policy", "SOW"], var_name="PI", value_name="Score")
        .merge(baseline, on="PI")
    )

    # normalize by baseline 2014
    tmp["normScore"] = (
        ((tmp["Score"] - tmp["baselineScore"]) / tmp["baselineScore"])
        * tmp["piMultiplier"]
        * 100
    )

    # round by the PI-specific threshold
    tmp["normScore"] = tmp.apply(
        lambda df: float(round(df["normScore"], df["roundDecimal"])), axis=1
    )

    # determine whether the meets satisficing criteria
    tmp["robustScore"] = np.select(
        [tmp["normScore"] >= tmp["lowerBounds"]],
        [1],
        default=0,
    )

    # normalized
    dynamicNorm.append(
        tmp.pivot_table(index=["Policy", "SOW"], columns="PI", values="normScore")
        .reset_index()
        .rename_axis(None, axis=1)
    )

    dynamicRobustness.append(
        tmp.pivot_table(index=["Policy", "SOW"], columns="PI", values="robustScore")
        .reset_index()
        .rename_axis(None, axis=1)
    )

# format and merge with hydro data
dynamicNorm = pd.concat(dynamicNorm)
dynamicRobustness = pd.concat(dynamicRobustness)

# -----------------------------------------------------------------------------
# scenario discovery
# -----------------------------------------------------------------------------

print("... starting scenario discovery ...")

# load data
data = dynamicRobustness.merge(hydroData, on=["Policy", "SOW"])
plans = data.loc[:, "Policy"].unique()
hydroVars = data.drop(columns=["Policy", "SOW"]).drop(columns=pis).columns.to_list()

output = pd.DataFrame(data=None, index=None, columns=hydroVars)
count = 0

for p in plans:

    # separate exogenous hydrologic variables and pi robustness
    full = data.loc[data["Policy"] == p, :]

    # boosted tree classification on each objective
    for obj in pis:

        tmp = full.dropna()
        x = tmp.loc[:, hydroVars].to_numpy()
        y = tmp.loc[:, obj]

        if len(y.unique()) > 1:

            # convert to numpy
            y = y.to_numpy()

            # create a gradient boosted classifier object
            gbc = GradientBoostingClassifier(
                learning_rate=0.05, max_features=5, max_depth=2, n_estimators=32
            )

            # fit the classifier for the first pi
            gbc.fit(x, y)

            # extract the feature importances
            feature_importances = gbc.feature_importances_

            # rank the feature importances and plot
            importances_sorted_idx = np.argsort(feature_importances)
            sorted_names = [hydroVars[i] for i in importances_sorted_idx]

            output.loc[count, "Policy"] = p
            output.loc[count, "PI"] = obj
            output.loc[count, sorted_names] = feature_importances

        else:
            # print("Only 1 State of Robustness/Failure")
            output.loc[count, "Policy"] = p
            output.loc[count, "PI"] = obj

        count = count + 1

output = output.loc[:, ["Policy", "PI"] + hydroVars]

output.to_csv(
    "data/" + folderName + "/postAnalysis/scenarioDiscovery/dynamicFactorRanking.txt",
    sep="\t",
    index=False,
)
dynamicRobustness.to_csv(
    "data/" + folderName + "/postAnalysis/scenarioDiscovery/dynamicRobustness.txt",
    sep="\t",
    index=False,
)
dynamicNorm.to_csv(
    "data/" + folderName + "/postAnalysis/scenarioDiscovery/dynamicNormalized.txt",
    sep="\t",
    index=False,
)
staticRobustness.to_csv(
    "data/" + folderName + "/postAnalysis/scenarioDiscovery/staticRobustness.txt",
    sep="\t",
    index=False,
)
staticNorm.to_csv(
    "data/" + folderName + "/postAnalysis/scenarioDiscovery/staticNormalized.txt",
    sep="\t",
    index=False,
)
hydroData.to_csv(
    "data/" + folderName + "/postAnalysis/scenarioDiscovery/exogenousHydro.txt",
    sep="\t",
    index=False,
)


# # TRAINING
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import roc_curve, auc, precision_score
# from sklearn.model_selection import GridSearchCV
# import matplotlib as mpl
# import matplotlib.pyplot as plt
# from matplotlib.legend_handler import HandlerLine2D

# # separate to training and testing
# train = tmp.loc[:, [obj] + hydroVars]
# labels = train.pop(obj)
# x_train, x_test, y_train, y_test = train_test_split(
#     train, labels, test_size=0.25
# )

# # fit model
# model = GradientBoostingClassifier()
# model.fit(x_train, y_train)
# y_pred = model.predict(x_test)

# # auc metric
# # false_positive_rate, true_positive_rate, thresholds = roc_curve(y_test, y_pred)
# # roc_auc = auc(false_positive_rate, true_positive_rate)
# # roc_auc

# # precision score metric
# ps = precision_score(y_test, y_pred)
# ps

# # hyperparameter tuning
# estimator = GradientBoostingClassifier()

# parameters = {
#     "learning_rate": [1, 0.75, 0.5, 0.25, 0.1, 0.05, 0.01, 0.001],
#     "n_estimators": [1, 2, 4, 8, 16, 32, 64, 100, 200],  # range(1, 200, 5),
#     "max_depth": range(1, 32, 1),
#     "min_samples_split": [
#         0.01,
#         0.25,
#         0.5,
#         0.75,
#         1.0,
#     ],  # [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
#     "min_samples_leaf": [
#         0.01,
#         0.25,
#         0.5,
#         0.75,
#         1.0,
#     ],  # [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
#     "max_features": list(range(1, train.shape[1])),
# }

# grid_search = GridSearchCV(
#     estimator=estimator,
#     param_grid=parameters,
#     scoring="average_precision",
#     cv=5,
#     verbose=True,
#     n_jobs=4,
# )

# grid_search.fit(x_train, y_train)

# # test learning rate
# learning_rates = [1, 0.5, 0.25, 0.1, 0.05, 0.01]
# train_results = []
# test_results = []
# for eta in learning_rates:
#     model = GradientBoostingClassifier(learning_rate=eta)
#     model.fit(x_train, y_train)
#     train_pred = model.predict(x_train)
#     # false_positive_rate, true_positive_rate, thresholds = roc_curve(
#     #     y_train, train_pred
#     # )
#     # roc_auc = auc(false_positive_rate, true_positive_rate)
#     # train_results.append(roc_auc)
#     ps = precision_score(y_test, y_pred)
#     train_results.append(ps)

#     y_pred = model.predict(x_test)
#     # false_positive_rate, true_positive_rate, thresholds = roc_curve(
#     #     y_test, y_pred
#     # )
#     # roc_auc = auc(false_positive_rate, true_positive_rate)
#     # test_results.append(roc_auc)
#     ps = precision_score(y_test, y_pred)
#     test_results.append(ps)

# (line1,) = plt.plot(learning_rates, train_results, "b", label="Train AUC")
# (line2,) = plt.plot(learning_rates, test_results, "r", label="Test AUC")
# plt.legend(handler_map={line1: HandlerLine2D(numpoints=2)})
# # plt.ylabel("AUC score")
# plt.ylabel("Precision Score")
# plt.xlabel("learning rate")
# plt.show()

# n_estimators = [1, 2, 4, 8, 16, 32, 64, 100, 200]
# train_results = []
# test_results = []
# for estimator in n_estimators:
#     model = GradientBoostingClassifier(n_estimators=estimator)
#     model.fit(x_train, y_train)
#     train_pred = model.predict(x_train)
#     false_positive_rate, true_positive_rate, thresholds = roc_curve(
#         y_train, train_pred
#     )
#     roc_auc = auc(false_positive_rate, true_positive_rate)
#     train_results.append(roc_auc)
#     y_pred = model.predict(x_test)
#     false_positive_rate, true_positive_rate, thresholds = roc_curve(
#         y_test, y_pred
#     )
#     roc_auc = auc(false_positive_rate, true_positive_rate)
#     test_results.append(roc_auc)

# (line1,) = plt.plot(n_estimators, train_results, "b", label="Train AUC")
# (line2,) = plt.plot(n_estimators, test_results, "r", label="Test AUC")
# plt.legend(handler_map={line1: HandlerLine2D(numpoints=2)})
# plt.ylabel("AUC score")
# plt.xlabel("n_estimators")
# plt.show()

# max_depths = np.linspace(1, 32, 32, endpoint=True)
# train_results = []
# test_results = []
# for max_depth in max_depths:
#     model = GradientBoostingClassifier(max_depth=max_depth)
#     model.fit(x_train, y_train)
#     train_pred = model.predict(x_train)
#     false_positive_rate, true_positive_rate, thresholds = roc_curve(
#         y_train, train_pred
#     )
#     roc_auc = auc(false_positive_rate, true_positive_rate)
#     train_results.append(roc_auc)
#     y_pred = model.predict(x_test)
#     false_positive_rate, true_positive_rate, thresholds = roc_curve(
#         y_test, y_pred
#     )
#     roc_auc = auc(false_positive_rate, true_positive_rate)
#     test_results.append(roc_auc)

# (line1,) = plt.plot(max_depths, train_results, "b", label="Train AUC")
# (line2,) = plt.plot(max_depths, test_results, "r", label="Test AUC")
# plt.legend(handler_map={line1: HandlerLine2D(numpoints=2)})
# plt.ylabel("AUC score")
# plt.xlabel("Tree depth")
# plt.show()

# min_samples_splits = np.linspace(0.1, 1.0, 10, endpoint=True)
# train_results = []
# test_results = []
# for min_samples_split in min_samples_splits:
#     model = GradientBoostingClassifier(min_samples_split=min_samples_split)
#     model.fit(x_train, y_train)
#     train_pred = model.predict(x_train)
#     false_positive_rate, true_positive_rate, thresholds = roc_curve(
#         y_train, train_pred
#     )
#     roc_auc = auc(false_positive_rate, true_positive_rate)
#     train_results.append(roc_auc)
#     y_pred = model.predict(x_test)
#     false_positive_rate, true_positive_rate, thresholds = roc_curve(
#         y_test, y_pred
#     )
#     roc_auc = auc(false_positive_rate, true_positive_rate)
#     test_results.append(roc_auc)

# (line1,) = plt.plot(min_samples_splits, train_results, "b", label="Train AUC")
# (line2,) = plt.plot(min_samples_splits, test_results, "r", label="Test AUC")
# plt.legend(handler_map={line1: HandlerLine2D(numpoints=2)})
# plt.ylabel("AUC score")
# plt.xlabel("min samples split")
# plt.show()

# min_samples_leafs = np.linspace(0.1, 0.5, 5, endpoint=True)
# train_results = []
# test_results = []
# for min_samples_leaf in min_samples_leafs:
#     model = GradientBoostingClassifier(min_samples_leaf=min_samples_leaf)
#     model.fit(x_train, y_train)
#     train_pred = model.predict(x_train)
#     false_positive_rate, true_positive_rate, thresholds = roc_curve(
#         y_train, train_pred
#     )
#     roc_auc = auc(false_positive_rate, true_positive_rate)
#     train_results.append(roc_auc)
#     y_pred = model.predict(x_test)
#     false_positive_rate, true_positive_rate, thresholds = roc_curve(
#         y_test, y_pred
#     )
#     roc_auc = auc(false_positive_rate, true_positive_rate)
#     test_results.append(roc_auc)

# (line1,) = plt.plot(min_samples_leafs, train_results, "b", label="Train AUC")
# (line2,) = plt.plot(min_samples_leafs, test_results, "r", label="Test AUC")
# plt.legend(handler_map={line1: HandlerLine2D(numpoints=2)})
# plt.ylabel("AUC score")
# plt.xlabel("min samples leaf")
# plt.show()

# max_features = list(range(1, train.shape[1]))
# train_results = []
# test_results = []
# for max_feature in max_features:
#     model = GradientBoostingClassifier(max_features=max_feature)
#     model.fit(x_train, y_train)
#     train_pred = model.predict(x_train)
#     false_positive_rate, true_positive_rate, thresholds = roc_curve(
#         y_train, train_pred
#     )
#     roc_auc = auc(false_positive_rate, true_positive_rate)
#     train_results.append(roc_auc)
#     y_pred = model.predict(x_test)
#     false_positive_rate, true_positive_rate, thresholds = roc_curve(
#         y_test, y_pred
#     )
#     roc_auc = auc(false_positive_rate, true_positive_rate)
#     test_results.append(roc_auc)

# (line1,) = plt.plot(max_features, train_results, "b", label="Train AUC")
# (line2,) = plt.plot(max_features, test_results, "r", label="Test AUC")
# plt.legend(handler_map={line1: HandlerLine2D(numpoints=2)})
# plt.ylabel("AUC score")
# plt.xlabel("max features")
# plt.show()
