import sys

sys.path.append(".")
from functions.utils import round_d


def getStLawrenceRoutingInputs(data, t):
    x = dict()
    x["slonFlow"] = data["stlouisontOut"][t]
    x["iceInd"] = data["iceInd"][t]
    x["ogdensburgR"] = data["ogdensburgR"][t]
    x["cardinalR"] = data["cardinalR"][t]
    x["iroquoishwR"] = data["iroquoishwR"][t]
    x["saundershwR"] = data["saundershwR"][t]
    x["iroquoistwR"] = data["iroquoistwR"][t]
    x["morrisburgR"] = data["morrisburgR"][t]
    x["longsaultR"] = data["longsaultR"][t]
    x["saunderstwR"] = data["saunderstwR"][t]
    x["cornwallR"] = data["cornwallR"][t]
    x["summerstownR"] = data["summerstownR"][t]
    x["ptclaireR"] = data["ptclaireR"][t]
    x["batiscanR"] = data["batiscanR"][t]
    x["threeriversR"] = data["threeriversR"][t]
    x["stpierreR"] = data["stpierreR"][t]
    x["sorelR"] = data["sorelR"][t]
    x["varennesR"] = data["varennesR"][t]
    x["jetty1R"] = data["varennesR"][t]
    x["desprairiesOut"] = data["desprairiesOut"][t]
    x["richelieuOut"] = data["richelieuOut"][t]
    x["stfrancoisOut"] = data["stfrancoisOut"][t]
    x["stmauriceOut"] = data["stmauriceOut"][t]
    x["tidalInd"] = data["tidalInd"][t]

    return x


def stLawrenceRouting(ontLevel, ontFlow, x):
    slonFlow = x["slonFlow"]
    iceInd = x["iceInd"]
    ogdensburgR = x["ogdensburgR"]
    cardinalR = x["cardinalR"]
    iroquoishwR = x["iroquoishwR"]
    saundershwR = x["saundershwR"]
    iroquoistwR = x["iroquoistwR"]
    morrisburgR = x["morrisburgR"]
    longsaultR = x["longsaultR"]
    saunderstwR = x["saunderstwR"]
    cornwallR = x["cornwallR"]
    summerstownR = x["summerstownR"]
    ptclaireR = x["ptclaireR"]
    batiscanR = x["batiscanR"]
    threeriversR = x["threeriversR"]
    stpierreR = x["stpierreR"]
    sorelR = x["sorelR"]
    varennesR = x["varennesR"]
    jetty1R = x["jetty1R"]
    desprairiesOut = x["desprairiesOut"]
    richelieuOut = x["richelieuOut"]
    stfrancoisOut = x["stfrancoisOut"]
    stmauriceOut = x["stmauriceOut"]
    tidalInd = x["tidalInd"]

    stlouisFlow = ontFlow + (slonFlow / 10)

    # kingston
    kingstonLevel = ontLevel - 0.03
    kingstonLevel_rounded = round_d(kingstonLevel, 2)
    difLev = kingstonLevel - 62.40

    # ogdensburg
    ogdensburgLevel = round_d(
        kingstonLevel
        - ogdensburgR * pow(ontFlow / (6.328 * pow(difLev, 2.0925)), (1 / 0.4103)),
        2,
    )

    # alexandria bay
    alexbayLevel = round_d(kingstonLevel - 0.39 * (kingstonLevel - ogdensburgLevel), 2)

    # brockville
    brockvilleLevel = round_d(
        kingstonLevel - 0.815 * (kingstonLevel - ogdensburgLevel), 2
    )

    # cardinal
    cardinalLevel = round_d(
        kingstonLevel
        - cardinalR * pow(ontFlow / (1.94908 * pow(difLev, 2.3981)), (1 / 0.4169)),
        2,
    )

    # iroquois headwaters
    iroquoishwLevel = round_d(
        kingstonLevel
        - iroquoishwR * pow(ontFlow / (2.36495 * pow(difLev, 2.2886)), (1 / 0.4158)),
        2,
    )

    # saunders headwaters
    saundershwLevel1 = round_d(
        kingstonLevel
        - (
            saundershwR
            * pow(
                (ontFlow * 10) / (21.603 * pow(difLev, 2.2586)),
                (1 / 0.3749),
            )
        ),
        2,
    )

    if saundershwLevel1 > 73.87:
        if iceInd == 2:
            saundershwLevel = saundershwLevel1
        else:
            saundershwLevel = 73.783
    else:
        saundershwLevel = saundershwLevel1

    # iroquois tailwaters (dependent saunders headwaters level)
    iroquoistwLevel1 = round_d(
        kingstonLevel
        - iroquoistwR * pow(ontFlow / (2.42291 * pow(difLev, 2.2721)), (1 / 0.4118)),
        2,
    )

    iroquoistwLevel2 = round_d(
        73.78 + pow((ontFlow * 10), 1.841) / pow((73.78 - 55), 5.891), 2
    )

    if saundershwLevel == 73.783:
        iroquoistwLevel = iroquoistwLevel2
    else:
        iroquoistwLevel = iroquoistwLevel1

    # morrisburg (dependent saunders headwaters level)
    morrisburgLevel1 = round_d(
        kingstonLevel
        - (morrisburgR * (ontFlow / (2.39537 * (difLev**2.245))) ** (1 / 0.3999)),
        2,
    )

    morrisburgLevel2 = round_d(
        73.78 + 6.799 * pow((ontFlow * 10), 1.913) / 811896440.84868, 2
    )

    if saundershwLevel == 73.783:
        morrisburgLevel = morrisburgLevel2
    else:
        morrisburgLevel = morrisburgLevel1

    # long sault (dependent saunders headwaters level)
    longsaultLevel1 = round_d(
        kingstonLevel
        - (longsaultR * (ontFlow / (2.29896 * (difLev**2.2381))) ** (1 / 0.3870)),
        2,
    )

    longsaultLevel2 = round_d(
        73.78 + 1408000 * pow((ontFlow * 10), 2.188) / 12501578154791700, 2
    )

    if saundershwLevel == 73.783:
        longsaultLevel = round_d(longsaultLevel2, 2)
    else:
        longsaultLevel = longsaultLevel1

    # saunders tailwaters
    saunderstwLevel = round_d(
        44.50 + 0.006338 * pow((saunderstwR * ontFlow * 10), 0.7158),
        2,
    )

    # cornwall
    cornwallLevel = round_d(
        45.00 + 0.0756 * pow((cornwallR * ontFlow * 10), 0.364),
        2,
    )

    # summerstown
    summerstownLevel = round_d(
        46.10 + 0.0109 * pow((summerstownR * ontFlow * 10), 0.451),
        2,
    )

    # pointe-claire (lac st. louis)
    ptclaireLevel = round_d(16.57 + pow((ptclaireR * stlouisFlow / 60.4), 0.58), 2)

    # lery beauharnois (uses pointe-claire level)
    lerybeauharnoisLevel = ptclaireLevel

    # desprairiesOut = data["desprairiesOut"][t]
    # richelieuOut = data["richelieuOut"][t]
    # stfrancoisOut = data["stfrancoisOut"][t]
    # stmauriceOut = data["stmauriceOut"][t]
    # tidalInd = data["tidalInd"][t]
    stlouisFlowcms = stlouisFlow * 10

    # jetty 1 (montreal harbor)
    lstl_flw_fctr = 0.001757 * stlouisFlowcms
    dpmi_flw_fctr = 0.000684 * desprairiesOut
    stfr_flw_fctr = 0.001161 * stfrancoisOut
    stmc_flw_fctr = 0.000483 * stmauriceOut
    flw_sum = lstl_flw_fctr + dpmi_flw_fctr + stfr_flw_fctr + stmc_flw_fctr
    # jetty1R = data["jetty1R"][t]
    jetty1Level = round_d(((flw_sum) * jetty1R) ** 0.6587 + 0.9392 * tidalInd, 2)
    # jetty1Level = round_d((ptclaireLevel * 1.657) + (-28.782), 2)

    # st. lambert
    stlambertLevel = round_d((ptclaireLevel * 1.583) + (-27.471), 2)

    # varennes
    lstl_flw_fctr = 0.001438 * stlouisFlowcms
    dpmi_flw_fctr = 0.001377 * desprairiesOut
    stfr_flw_fctr = 0.001442 * stfrancoisOut
    stmc_flw_fctr = 0.000698 * stmauriceOut
    flw_sum = lstl_flw_fctr + dpmi_flw_fctr + stfr_flw_fctr + stmc_flw_fctr
    # varennesR = data["varennesR"][t]
    varennesLevel = round_d(((flw_sum) * varennesR) ** 0.6373 + 1.0578 * tidalInd, 2)
    # varennesLevel = round_d((ptclaireLevel * 1.535) + (-26.943), 2)

    # sorel
    lstl_flw_fctr = 0.001075 * stlouisFlowcms
    dpmi_flw_fctr = 0.001126 * desprairiesOut
    stfr_flw_fctr = 0.001854 * stfrancoisOut
    stmc_flw_fctr = 0.000882 * stmauriceOut
    flw_sum = lstl_flw_fctr + dpmi_flw_fctr + stfr_flw_fctr + stmc_flw_fctr
    # sorelR = data["sorelR"][t]
    sorelLevel = round_d(((flw_sum) * sorelR) ** 0.6331 + 1.277 * tidalInd, 2)
    # sorelLevel = round_d((ptclaireLevel * 1.337) + (-23.616), 2)

    # lac st. pierre
    lstl_flw_fctr = 0.000807 * stlouisFlowcms
    dpmi_flw_fctr = 0.001199 * desprairiesOut
    stfr_flw_fctr = 0.001954 * stfrancoisOut
    stmc_flw_fctr = 0.000976 * stmauriceOut
    flw_sum = lstl_flw_fctr + dpmi_flw_fctr + stfr_flw_fctr + stmc_flw_fctr
    # stpierreR = data["stpierreR"][t]
    lacstpierreLevel = round_d(((flw_sum) * stpierreR) ** 0.6529 + 1.4772 * tidalInd, 2)
    # lacstpierreLevel = round_d((ptclaireLevel * 1.366) + (-24.620), 2)

    # maskinonge (uses lac st pierre level)
    maskinongeLevel = lacstpierreLevel

    # troisrivieres
    lstl_flw_fctr = 0.000584 * stlouisFlowcms
    dpmi_flw_fctr = 0.000690 * desprairiesOut
    rich_flw_fctr = 0.000957 * richelieuOut
    stfr_flw_fctr = 0.001197 * stfrancoisOut
    stmc_flw_fctr = 0.000787 * stmauriceOut
    flw_sum = (
        lstl_flw_fctr + dpmi_flw_fctr + rich_flw_fctr + stfr_flw_fctr + stmc_flw_fctr
    )
    # troisrivieresR = data["threeriversR"][t]
    troisrivieresLevel = round_d(
        ((flw_sum) * threeriversR) ** 0.7042 + 1.5895 * tidalInd, 2
    )
    # troisrivieresLevel = round_d((ptclaireLevel * 1.337) + (-24.425), 2)

    # batiscan
    lstl_flw_fctr = 0.000422 * stlouisFlowcms
    dpmi_flw_fctr = 0.000553 * desprairiesOut
    rich_flw_fctr = 0.000903 * richelieuOut
    stfr_flw_fctr = 0.001023 * stfrancoisOut
    stmc_flw_fctr = 0.000682 * stmauriceOut
    flw_sum = (
        lstl_flw_fctr + dpmi_flw_fctr + rich_flw_fctr + stfr_flw_fctr + stmc_flw_fctr
    )
    # batiscanR = batiscanR
    batiscanLevel = round_d(((flw_sum) * batiscanR) ** 0.6941 + 1.8303 * tidalInd, 2)
    # batiscanLevel = round_d((ptclaireLevel * 1.105) + (-20.269), 2)

    # save timestep in dictionary
    levels = dict()
    levels["stlouisFlow"] = stlouisFlow
    levels["kingstonLevel"] = kingstonLevel_rounded
    levels["alexbayLevel"] = alexbayLevel
    levels["brockvilleLevel"] = brockvilleLevel
    levels["ogdensburgLevel"] = ogdensburgLevel
    levels["cardinalLevel"] = cardinalLevel
    levels["iroquoishwLevel"] = iroquoishwLevel
    levels["iroquoistwLevel"] = iroquoistwLevel
    levels["morrisburgLevel"] = morrisburgLevel
    levels["longsaultLevel"] = longsaultLevel
    levels["saundershwLevel"] = saundershwLevel
    levels["saunderstwLevel"] = saunderstwLevel
    levels["cornwallLevel"] = cornwallLevel
    levels["summerstownLevel"] = summerstownLevel
    levels["lerybeauharnoisLevel"] = lerybeauharnoisLevel
    levels["ptclaireLevel"] = ptclaireLevel
    levels["jetty1Level"] = jetty1Level
    levels["stlambertLevel"] = stlambertLevel
    levels["varennesLevel"] = varennesLevel
    levels["sorelLevel"] = sorelLevel
    levels["lacstpierreLevel"] = lacstpierreLevel
    levels["maskinongeLevel"] = maskinongeLevel
    levels["troisrivieresLevel"] = troisrivieresLevel
    levels["batiscanLevel"] = batiscanLevel

    return levels
