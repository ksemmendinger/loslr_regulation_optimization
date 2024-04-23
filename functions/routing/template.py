"""
-------------------------------------------------------------------------------

this script contains a template for the `getStLawrenceRoutingInputs` and 
`stLawrenceRouting` functions

-------------------------------------------------------------------------------
"""


"""
-------------------------------------------------------------------------------

# import custom function for engineering rounding
import sys
sys.path.append(".")
from functions.utils import round_d

# extracts timestep inputs for `stLawrenceRouting`
def getStLawrenceRoutingInputs(data, t):
    
    # INPUTS
    # data: dictionary of input time series from main simulation function
    # keys are variable names and values are np.arrays of the time series of 
    # the variable values
    # t: timestep from simulation for loop

    # OUTPUTS
    # x: dictionary with named key value pairs of hydrologic inputs at the
    # timestep of interest
    
    x = dict()
    x["variable"] = data["variable"][t]
    

    # code to extract, calculate, or format needed inputs for `stLawrenceRouting`....


    return x

# routes final outflow through system to calculate levels/flows along the St. Lawrence River
def stLawrenceRouting(ontLevel, ontFlow, x):

    # INPUTS
    # ontLevel: water level calculated with observed NTS and final release
    # ontFlow: final outflow for timestep
    # x: dictionary output from `getStLawrenceRoutingInputs`

    # OUTPUTS
    # dictionary with named key value pairs for relevant locations along the st. lawrence river (see below for all locations)
    
    # extract outputs from x
    variable = x["variable"]


    # code to calculate st. lawrence levels and flows ....

    
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

-------------------------------------------------------------------------------
"""
