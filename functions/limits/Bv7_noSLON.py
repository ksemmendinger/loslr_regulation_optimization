# import libraries
import numpy as np

# import slonCalculation


# takes in supplies and calculates releases/levels
def limitCheck(
    ontLevel,  # preliminary level from release function
    slonNotOttawa,
    carillonFlow,
    chateauguayFlow,
    # if slonValue == FALSE, carillonFlow and chateauguayFlow must be passted for slonCalculation
    iceInd,
    iceIndPrev,
    kingLevelStart,
    qm,
    longsaultR,
    ontFlowPrev,
    ontLevelStart,
    obsontNTS,
    foreInd,
    ptclaireR,
    saundershwR,
    saunderstwR,
    sfSupplyNTS,
    output="gov",
):
    # -----------------------------------------------------------------------------
    #
    # I limit - ice stability
    #
    # maximum i-limit flow check. ice status of 0, 1, and 2 correspond to no ice,
    # stable ice formed, and unstable ice forming
    #
    # -----------------------------------------------------------------------------

    if iceInd == 2 or iceIndPrev == 2:
        iLimFlow = 704  # updated 4/9 for GLAM Phase 2

    # elif iceInd == 1 or (qm < 13 or qm > 47):
    elif iceInd == 1 or (qm < 12):  # changed nav season 4/9 for GLAM Phase 2
        # calculate release to keep long sault level above 71.8 m
        con1 = (kingLevelStart - 62.40) ** 2.2381
        con2 = ((kingLevelStart - 71.80) / longsaultR) ** 0.3870
        qx = (22.9896 * con1 * con2) * 0.10
        iLimFlow = round(qx, 0)

        # added from iceReg
        if iceInd == 1:
            if iLimFlow > 943.0:
                iLimFlow = 943.0

        else:
            if iLimFlow > 991.0:
                iLimFlow = 991.0

    else:
        iLimFlow = 0

    iRegime = "I"

    # -----------------------------------------------------------------------------
    #
    # L limit - navigation and channel capacity check
    #
    # maximum l-limit flow check - primarily based on level. applied during
    # the navigation season (qm 13 - qm 47) and during non-navigation season.
    # reference table b3 in compendium report
    #
    # -----------------------------------------------------------------------------

    lFlow = 0

    # navigation season
    # if qm >= 13 and qm <= 47:
    if qm >= 12:  # changed 4/9 for GLAM Phase 2
        lRegime = "LN"

        if ontLevel <= 74.22:
            lFlow = 595.0

        elif ontLevel <= 74.34:
            lFlow = 595.0 + 133.3 * (ontLevel - 74.22)

        elif ontLevel <= 74.54:
            lFlow = 611.0 + 910 * (ontLevel - 74.34)

        elif ontLevel <= 74.70:
            lFlow = 793.0 + 262.5 * (ontLevel - 74.54)

        elif ontLevel <= 75.13:
            lFlow = 835.0 + 100.0 * (ontLevel - 74.70)

        elif ontLevel <= 75.44:
            lFlow = 878.0 + 364.5 * (ontLevel - 75.13)

        elif ontLevel <= 75.70:
            lFlow = 991.0

        elif ontLevel <= 76.0:
            lFlow = 1020.0

        else:
            lFlow = 1070.0

        # check minimum long sault level - calculate the ontFlow to keeplong sault level above lstd_mlv_min
        if ontLevel >= 74.20:
            longSaultmin = 72.60
        else:
            longSaultmin = 72.60 - (74.20 - ontLevel)

        kingstonLevel = ontLevel - 0.03
        a = 2.29896
        b = 62.4
        c = 2.2381
        d = 0.387
        lFlow2 = (
            a
            * ((kingstonLevel - b) ** c)
            * (((kingstonLevel - longSaultmin) / round(longsaultR, 3)) ** d)
        )

        lFlow2 = round(lFlow2, 0)
        # lFlow2 = engRound(lFlow2, 1)

        if lFlow2 < lFlow:
            lRegime = "LS"
            lFlow = lFlow2

    # non-navigation season
    else:
        lRegime = "LM"
        lFlow = 1150.0

    # channel capacity check
    lFlow3 = (747.2 * (ontLevel - 69.10) ** 1.47) / 10.0
    if lFlow3 < lFlow:
        lFlow = lFlow3
        lRegime = "LC"

    lLimFlow = round(lFlow, 0)

    # -----------------------------------------------------------------------------
    #
    # M limit -  low level balance
    #
    # minimum m-limit flow check. minimum limit flows to balance low levels of
    # lake ontario and lac st. louis primarily for seaway navigation interests
    #
    # -----------------------------------------------------------------------------

    if str(slonNotOttawa) == "True":
        # compute crustal adjustment factor, fixed for year 2010
        adj = 0.0014 * (2010 - 1985)
        slope = 55.5823

        # this part borrowed from 58DD to prevent too low St. Louis levels
        if ontLevel > 74.20:
            mq = 680.0 - (slonFlow * 0.1)

        elif ontLevel > 74.10 and ontLevel <= 74.20:
            mq = 650.0 - (slonFlow * 0.1)

        elif ontLevel > 74.00 and ontLevel <= 74.10:
            mq = 620.0 - (slonFlow * 0.1)

        elif ontLevel > 73.60 and ontLevel <= 74.00:
            mq = 610.0 - (slonFlow * 0.1)

        else:
            # mq1 = 577.0 - (slonFlow * 0.1)
            mq2 = slope * (ontLevel - adj - 69.474) ** 1.5
            # mq = min(mq1, mq2)
            mq = mq2

        mLimFlow = round(mq, 0)
        mRegime = "M"

    # stochastic version of M limit to prevent too low of flows, route Ottawa River flows
    else:
        # m-limit by quarter-month
        qmLimFlow = np.hstack(
            [
                [595] * 4,
                [586] * 4,
                [578] * 4,
                [532] * 8,
                [538] * 4,
                [547] * 12,
                [561] * 8,
                [595] * 4,
            ]
        )

        mFlow = qmLimFlow[qm - 1]

        if ontLevel > 74.20:
            Qsplit = mFlow
            limQ = 680.0

            diff = 999
            QOnt1 = Qsplit

            k = 1
            maxIterations = 9999

            while k < maxIterations:
                tmp = slonCalculation(Qsplit, carillonFlow, chateauguayFlow)
                Qstl_Ont = tmp["slonFlow"]
                Q_Ontlimit = limQ - (Qstl_Ont / 10)
                if Q_Ontlimit < 0.0:
                    Q_Ontlimit = 0.0
                diff = abs(Q_Ontlimit - QOnt1)
                QOnt1 = Q_Ontlimit

                if diff <= 1.0:
                    break

            Q_Ontlimit = round(Q_Ontlimit, 0)
            Qsplit = Q_Ontlimit

        elif ontLevel > 74.10 and ontLevel <= 74.20:
            Qsplit = mFlow
            limQ = 650.0

            diff = 999
            QOnt1 = Qsplit

            k = 1
            maxIterations = 9999

            while k < maxIterations:
                tmp = slonCalculation(Qsplit, carillonFlow, chateauguayFlow)
                Qstl_Ont = tmp["slonFlow"]
                Q_Ontlimit = limQ - (Qstl_Ont / 10)
                if Q_Ontlimit < 0.0:
                    Q_Ontlimit = 0.0
                diff = abs(Q_Ontlimit - QOnt1)
                QOnt1 = Q_Ontlimit

                if diff <= 1.0:
                    break

            Q_Ontlimit = round(Q_Ontlimit, 0)
            Qsplit = Q_Ontlimit

        elif ontLevel > 74.00 and ontLevel <= 74.10:
            Qsplit = mFlow
            limQ = 620.0

            diff = 999
            QOnt1 = Qsplit

            k = 1
            maxIterations = 9999

            while k < maxIterations:
                tmp = slonCalculation(Qsplit, carillonFlow, chateauguayFlow)
                Qstl_Ont = tmp["slonFlow"]
                Q_Ontlimit = limQ - (Qstl_Ont / 10)
                if Q_Ontlimit < 0.0:
                    Q_Ontlimit = 0.0
                diff = abs(Q_Ontlimit - QOnt1)
                QOnt1 = Q_Ontlimit

                if diff <= 1.0:
                    break

            Q_Ontlimit = round(Q_Ontlimit, 0)
            Qsplit = Q_Ontlimit

        elif ontLevel > 73.60 and ontLevel <= 74.00:
            Qsplit = mFlow
            limQ = 610.0

            diff = 999
            QOnt1 = Qsplit

            k = 1
            maxIterations = 9999

            while k < maxIterations:
                tmp = slonCalculation(Qsplit, carillonFlow, chateauguayFlow)
                Qstl_Ont = tmp["slonFlow"]
                Q_Ontlimit = limQ - (Qstl_Ont / 10)
                if Q_Ontlimit < 0.0:
                    Q_Ontlimit = 0.0
                diff = abs(Q_Ontlimit - QOnt1)
                QOnt1 = Q_Ontlimit

                if diff <= 1.0:
                    break

            Q_Ontlimit = round(Q_Ontlimit, 0)
            Qsplit = Q_Ontlimit

        else:
            Qsplit = mFlow
            limQ = 577.0

            diff = 999
            QOnt1 = Qsplit

            k = 1
            maxIterations = 9999

            while k < maxIterations:
                tmp = slonCalculation(Qsplit, carillonFlow, chateauguayFlow)
                Qstl_Ont = tmp["slonFlow"]
                Q_Ontlimit = limQ - (Qstl_Ont / 10)
                if Q_Ontlimit < 0.0:
                    Q_Ontlimit = 0.0
                diff = abs(Q_Ontlimit - QOnt1)
                QOnt1 = Q_Ontlimit

                if diff <= 1.0:
                    break

            Q_Ontlimit = round(Q_Ontlimit, 0)
            Qsplit1 = Q_Ontlimit

            # compute crustal adjustment factor, fixed for year 2010
            adj = 0.0014 * (2010 - 1985)
            slope = 55.5823

            if ontLevel >= (adj + 69.474):  # added to account for levels below 69.474
                Qsplit2 = slope * (ontLevel - adj - 69.474) ** 1.5

            else:
                Qsplit2 = np.nan

            Qsplit = min(Qsplit1, Qsplit2)

        mFlow = Qsplit

        mLimFlow = round(mFlow, 0)
        mRegime = "M"

    # -----------------------------------------------------------------------------
    #
    # J limit - stability check
    #
    # j-limit stability flow check. adjusts large changes between flow for coming
    # week and actual flow last week. can be min or max limit.
    #
    # -----------------------------------------------------------------------------

    # difference between rc flow and last week's actual flow
    flowdif = abs(ontFlow - ontFlowPrev)

    # flow change bounds
    jdn = 70
    jup = 70

    # increase upper j-limit if high lake ontario level and no ice
    if ontLevel > 75.20 and iceInd == 0 and iceIndPrev < 2:
        jup = 142

    # if flow difference is positive, check if maxJ applies
    if ontFlow >= ontFlowPrev:
        # upper J limit applies
        if flowdif > jup:
            jFlow = ontFlowPrev + jup
            if jup == 70:
                jRegime = "J+"
            else:
                jRegime = "J*"

        # no jlim is applied, flow is RC flow
        else:
            jFlow = ontFlow
            jRegime = ontRegime

    # if the flow difference is negative, check if minJ applies
    else:
        # lower J limit applies
        if flowdif > jdn:
            jFlow = ontFlowPrev - jdn
            jRegime = "J-"

        # no jlim is applied, flow is RC flow
        else:
            jFlow = ontFlow
            jRegime = ontRegime

    jLimFlow = round(jFlow, 0)

    # -----------------------------------------------------------------------------
    # limit comparison
    # -----------------------------------------------------------------------------

    # this is either the J-limit (if applied) or the RC flow and regime
    maxLimFlow = jLimFlow
    maxLimRegime = jRegime

    # get the smallest of the maximum limits (L and I)
    maxLim = -9999

    if lLimFlow != 0:
        if maxLim < 0:
            maxLim = lLimFlow
            maxRegime = lRegime

    if iLimFlow != 0:
        if maxLim < 0 or iLimFlow < maxLim:
            maxLim = iLimFlow
            maxRegime = iRegime

    # compare rc flow or j limit with maximum limits (RC or J with L and I)
    if maxLim > 0 and maxLimFlow > maxLim:
        maxLimFlow = maxLim
        maxLimRegime = maxRegime

    # get the biggest of the minimum limits (M)
    minLimFlow = mLimFlow
    minLimRegime = mRegime

    # compare the maximum and minimum limits
    if maxLimFlow > minLimFlow:
        limFlow = maxLimFlow
        limRegime = maxLimRegime

    # if the limit reaches to this point, then take the minimum limit
    else:
        # if the M limit is greater than the smaller of the I/L limit, take the M limit
        if minLimFlow > maxLim:
            if minLimRegime == mRegime:
                limFlow = minLimFlow
                limRegime = minLimRegime
            else:
                if maxLim > minLimFlow:
                    limFlow = maxLim
                    limRegime = maxRegime
                else:
                    limFlow = minLimFlow
                    limRegime = mRegime
        else:
            limFlow = minLimFlow
            limRegime = minLimRegime

    # update ontFlow and ontRegime post limit check
    ontFlow = limFlow
    ontRegime = limRegime

    # compute averaged quarter-monthly release using forecasted nts
    dif1 = round((sfSupplyNTS / 10 - ontFlow) / 2970, 6)
    ontLevelEOQ = round(ontLevelStart + dif1, 2)

    # -----------------------------------------------------------------------------
    #
    # F limit - downstream flooding
    #
    # f-limit levels check. calculate lac st. louis flow at levels at pt. claire
    # to determine if downstream flooding needs to be mitigated
    #
    # -----------------------------------------------------------------------------

    # determine "action level" to apply at pointe claire
    if ontLevelStart < 75.3:
        actionlev = 22.10
        c1 = 11523.848
    elif ontLevelStart < 75.37:
        actionlev = 22.20
        c1 = 11885.486
    elif ontLevelStart < 75.50:
        actionlev = 22.33
        c1 = 12362.610
    elif ontLevelStart < 75.60:
        actionlev = 22.40
        c1 = 12622.784
    else:
        actionlev = 22.48
        c1 = 12922.906

    if str(slonNotOttawa) == "True":
        # flows through lac st louis from slon value
        stlouisFlow = ontFlow * 10.0 + slonFlow

        # calculate pointe claire level
        ptclaireLevel = round(16.57 + ((ptclaireR * stlouisFlow / 604.0) ** 0.58), 2)

        # estimate flow required to maintain pointe claire below action level
        if ptclaireLevel > actionlev:
            flimFlow = round((c1 / ptclaireR - slonFlow) / 10.0, 0)

            if flimFlow < ontFlow:
                ontFlow = flimFlow
                ontRegime = "F"

    else:
        if foreInd == 1:
            tmp = slonCalculation(ontFlow, carillonFlow, chateauguayFlow)
            slonFlow = tmp["slonFlow"]
            fFlow = round((c1 / ptclaireR - slonFlow) / 10.0, 0)

        else:
            Qsplit = ontFlow
            limQ = (c1 / ptclaireR) / 10.0

            diff = 999
            QOnt1 = Qsplit

            k = 1
            maxIterations = 9999

            while k < maxIterations:
                tmp = slonCalculation(Qsplit, carillonFlow, chateauguayFlow)
                Qstl_Ont = tmp["slonFlow"]
                Q_Ontlimit = limQ - (Qstl_Ont / 10)
                if Q_Ontlimit < 0.0:
                    Q_Ontlimit = 0.0
                diff = abs(Q_Ontlimit - QOnt1)
                QOnt1 = Q_Ontlimit

                if diff <= 1.0:
                    break

            Q_Ontlimit = round(Q_Ontlimit, 0)
            fFlow = Q_Ontlimit

        flimFlow = round(fFlow, 0)

        if flimFlow < ontFlow:
            ontFlow = flimFlow
            ontRegime = "F"

    # -----------------------------------------------------------------------------
    #
    # Minimum Head Limit - ADDED 4/9 FOR GLAM PHASE 2 EFFORTS
    #
    # from Halya: Given the 2020 experience with minimum NYPA net head, add a
    # constraint that limits the minimum net head to 22.5m on a quarter-monthly mean
    # basis. Previously, operational adjustments were made to reflect the minimum head
    # required by NYPA. This would be a last check after the near-final flow is
    # calculated and will be applied to both Bv7 and Plan 2014. Note that Bv7 does not
    # reach this limit in the historical “basis of comparison” dataset so this will not
    # affect the Orders tests.
    #
    # -----------------------------------------------------------------------------

    # ontFlow is semi-final flow - calculate level difference with observed NTS
    dif2 = round(((obsontNTS / 10) - ontFlow) / 2970, 6)
    ontLevel_EOQ_unrounded = round(ontLevelStart + dif2, 6)
    ontLevel_MLV = round((ontLevelStart + ontLevel_EOQ_unrounded) * 0.5, 2)

    # set constants
    iters = 12
    head_min = 22.50
    tolerence = 0.02  # tolerence for difference between head and min head
    flw_increment = 300  # 300 cms flow change ~ 0.02m headwater change

    # initialize variables
    flw_new = ontFlow
    ont_mlv_new = ontLevel_MLV
    dif = dif2

    for i in range(iters):
        # flow to maintain minimum head is calculated iteratively
        # iterate until satisfactory flow found or 'iters' iterations
        # kingston level
        king_new = ont_mlv_new - 0.03

        # calculate Saunders headwater level
        saundershwLevel1 = round(
            king_new
            - (
                saundershwR
                * pow(
                    (flw_new * 10) / (21.603 * pow(dif, 2.2586)),
                    (1 / 0.3749),
                )
            ),
            2,
        )

        if saundershwLevel1 > 73.87:
            if iceInd == 2 or iceIndPrev == 2:
                sahw_new = saundershwLevel1
            else:
                sahw_new = 73.783
        else:
            sahw_new = saundershwLevel1

        # calculate interational tailwater level
        intw_level_new = round(
            44.50 + 0.006338 * pow((saunderstwR * flw_new * 10), 0.7158),
            2,
        )

        # calculate head for this iteration
        head_new = sahw_new - intw_level_new

        if head_new < (head_min - tolerence):
            flw_loop = flw_new + flw_increment * (head_new - head_min) / 10
            flw_loop = round(flw_loop, 0)
            dif = round(((obsontNTS / 10) - flw_loop) / 2970, 6)
            ont_elv_loop = ontLevelStart + dif
            ont_mlv_new = (ontLevelStart + ont_elv_loop) * 0.5
            ont_mlv_new = round(ont_mlv_new, 2)
            flw_new = flw_loop
        else:
            flow_MH = flw_new
            break

        flow_MH = flw_loop

    if ontFlow > flow_MH:
        MH_applies = True
    else:
        MH_applies = False

    # Compare minimum head limit
    if MH_applies:
        ontFlow = flow_MH
        ontRegime = "MH"

    if output == "gov":
        return {"ontFlow": ontFlow, "ontRegime": ontRegime}
    elif output == "all":
        return {
            "ontFlow": ontFlow,
            "ontRegime": ontRegime,
            "iFlow": iLimFlow,
            "lFlow": lLimFlow,
            "lRegime": lRegime,
            "mFlow": mLimFlow,
            "jFlow": jLimFlow,
            "jRegime": jRegime,
            "fFlow": flimFlow,
            "mhFlow": flow_MH,
        }
