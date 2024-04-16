# only used for montreal routing if SLON is not available
def slonCalculation(ontFlow, carillonFlow, chateauguayFlow):
    # convert ontFlow to cms from 10*cms
    ontFlow10 = ontFlow * 10

    # ----------------------------------------
    # flows through sainte-anne
    # ----------------------------------------

    # constants
    c1 = 585.40
    c2 = 0.2733
    c3 = -0.05017
    c4 = -20.95
    c5 = -125.00
    c6 = 0.2986
    c7 = 0.02046
    c8 = -13.54

    # flow limits
    ontLim = 7800.0001
    cariLim = 300.0001

    # flow comparisons
    stanne1 = (
        c1 + (c2 * carillonFlow) + (c3 * ontFlow10) + (c4 * ontFlow10 / carillonFlow)
    )
    stanne2 = (
        c5 + (c6 * carillonFlow) + (c7 * ontFlow10) + (c8 * ontFlow10 / carillonFlow)
    )

    if ontFlow10 <= ontLim:
        if carillonFlow <= cariLim:
            stanneFlow = 0.0
        else:
            if stanne2 > 0.0:
                stanneFlow = stanne2
            else:
                stanneFlow = 0.0
    elif ontFlow10 > ontLim:
        if carillonFlow <= cariLim:
            stanneFlow = stanne1
        else:
            if stanne1 >= stanne2:
                stanneFlow = stanne2
            else:
                stanneFlow = stanne1

    # ----------------------------------------
    # flows through vaudreuil
    # ----------------------------------------

    # constants
    c1 = 787.40
    c2 = 0.3479
    c3 = -0.1336
    c4 = -0.9374
    c5 = -61.00
    c6 = 0.2975
    c7 = -0.0356
    c8 = 16.77
    c9 = 24.2
    c10 = 0.295
    c11 = -0.01885
    c12 = -0.0954

    # flow limits
    ontLim = 6600.0001
    cariLim1 = 300.0001
    cariLim2 = 900.0001
    diffOntCariLim = 7100.0001
    ratioOntCariLim = 35000.0001

    # flow comparisons
    vaud1 = c1 + (c2 * carillonFlow) + (c3 * ontFlow10) + (c4 * chateauguayFlow)
    vaud2 = (
        c5 + (c6 * carillonFlow) + (c7 * ontFlow10) + (c8 * ontFlow10 / carillonFlow)
    )
    vaud3 = (
        c9
        + (c10 * carillonFlow)
        + (c11 * ontFlow10)
        + c12 * (ontFlow10 - carillonFlow) * carillonFlow / ontFlow10
    )

    if ontFlow10 <= ontLim:
        if carillonFlow <= cariLim1:
            vaudreuilFlow = 0.0
        elif carillonFlow > cariLim1:
            if vaud3 < 0.0:
                vaudreuilFlow = 0.0
            elif vaud3 >= 0.0:
                if carillonFlow < cariLim2:
                    vaudreuilFlow = vaud3
                elif carillonFlow >= cariLim2:
                    if vaud2 > 0.0:
                        vaudreuilFlow = vaud2
                    else:
                        vaudreuilFlow = 0.0
    elif ontFlow10 > ontLim:
        if carillonFlow <= cariLim1:
            if vaud1 < 0.0:
                vaudreuilFlow = vaud1
            else:
                vaudreuilFlow = 0.0
        elif carillonFlow > cariLim1:
            diffOntCari = ontFlow10 - carillonFlow
            ratioOntCari = ontFlow10 / carillonFlow

            if (
                diffOntCari > diffOntCariLim
                and (diffOntCari * ratioOntCari) > ratioOntCariLim
            ):
                vaudreuilFlow = vaud1
            else:
                if carillonFlow < cariLim2:
                    if vaud1 >= vaud3:
                        vaudreuilFlow = vaud3
                    else:
                        vaudreuilFlow = vaud1
                else:
                    if vaud1 > vaud2:
                        vaudreuilFlow = vaud2
                    else:
                        vaudreuilFlow = vaud1

    # ----------------------------------------
    # flows through des prairies & mille iles
    # ----------------------------------------

    # constants
    c1 = 107.20
    c2 = 0.7418
    c3 = -0.6588
    dpmiFlow = c1 + (c2 * carillonFlow) + (c3 * vaudreuilFlow)

    # ----------------------------------------
    # flows through lac st. louis
    # ----------------------------------------

    # constants
    c1 = -877.40
    c2 = 1.1652
    c3 = 4.367
    c4 = 1.3956
    c5 = 0.8137
    c6 = 2751.0
    c7 = 0.7977
    c8 = 3.381
    c9 = 2.091
    ontLim = 9000.0001

    if ontFlow10 < ontLim:
        lacstlouisFlow = (
            c1
            + c2 * ontFlow10
            + c3 * chateauguayFlow
            + c4 * vaudreuilFlow
            + c5 * stanneFlow
        )
    else:
        lacstlouisFlow = (
            c6 + (c7 * ontFlow10) + (c8 * chateauguayFlow) + (c9 * vaudreuilFlow)
        )

    lacstlouisFlow = round(lacstlouisFlow, 0)

    # finally, get SLON flow (in cms)
    slonFlow = lacstlouisFlow - ontFlow10

    return {
        "stanneFlow": stanneFlow,
        "vaudreuilFlow": vaudreuilFlow,
        "dpmiFlow": dpmiFlow,
        "lacstlouisFlow": lacstlouisFlow,
        "slonFlow": slonFlow,
    }
