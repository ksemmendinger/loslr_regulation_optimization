# import libraries
import sys

sys.path.append(".")
from functions.utils import round_d


def septemberRule(
    qm,
    # prelimLevel,
    ontLevelStart,
    prelimFlow,
    prelimRegime,
    qm32Level,
    qm32Flow,
    conv=2970,
):
    ontFlow = prelimFlow
    ontRegime = prelimRegime
    if qm > 32 and qm <= 48:  # and flowflag == 1 and ontLevel > 74.80:
        if qm32Level > 74.80:
            if ontLevelStart > 74.80:
                if qm <= 46:
                    flowadj = ((ontLevelStart - 74.80) * conv) / (46 - qm + 1)
                else:
                    flowadj = ((ontLevelStart - 74.80) * conv) / (48 - qm + 1)

                # adjust rule curve flow
                ontFlow = ontFlow + flowadj

                # if qm == 33:
                #     ontFlow = min(ontFlow, qm32Flow)

                # # adjust rule curve flow
                # ontFlow = round(ontFlow, 0)

                # # calculate resulting water level
                # dif1 = round((sfSupplyNTS[0] / 10 - ontFlow) / conv, 6)
                # ontLevel = round(ontLevel + dif1, 2)

                # adjust rule curve flow regime
                ontRegime = "R+"

    # rFlow = ontFlow
    if ontRegime == "R+":
        if qm == 33:
            ontFlow = min(ontFlow, qm32Flow)

        if ontLevelStart <= 75.13:
            if ontFlow > (835.0 + 100.0 * (ontLevelStart - 74.7)):
                ontFlow = 835.0 + 100.0 * (ontLevelStart - 74.7)
                ontRegime = "L1"
        elif ontLevelStart <= 75.44:
            if ontFlow > (878.0 + 364.5 * (ontLevelStart - 75.13)):
                ontFlow = 878.0 + 364.5 * (ontLevelStart - 75.13)
                ontRegime = "L1"
        elif ontLevelStart <= 75.70:
            if ontFlow > 991.0:
                ontFlow = 991.0
                ontRegime = "L1"
        elif ontLevelStart <= 76.0:
            if ontFlow > 1070.0:
                ontFlow = 1070.0
                ontRegime = "L1"
        else:
            if ontFlow > 1150.0:
                ontFlow = 1150.0
                ontRegime = "L1"

        ontFlow = round_d(ontFlow, 0)
    return ontFlow, ontRegime
