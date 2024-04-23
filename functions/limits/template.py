"""
-------------------------------------------------------------------------------

this script contains a template for the `getPlanLimitsInputs` and `planLimits`
functions

-------------------------------------------------------------------------------
"""


"""
-------------------------------------------------------------------------------

# import custom function for engineering rounding
import sys
sys.path.append(".")
from functions.utils import round_d

# extracts timestep inputs for `planLimits`
def getPlanLimitsInputs(data, t):
    
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
    

    # code to extract, calculate, or format needed inputs for `planLimits`....


    return x

def planLimits(
    qm,
    prelimLevel,
    prelimFlow,
    prelimRegime,
    x,
    septemberRule,
    ):

    # INPUTS
    # qm: quarter-month from simulation for loop
    # prelimLevel: release function calculated preliminary water level
    # prelimFlow: release function calculated preliminary flow
    # prelimRegime: release function calculated preliminary regime
    # x: dictionary output from `getPlanLimitsInputs`
    # septemberRule: "off" or the septemberRule function

    # OUTPUTS
    # dictionary with named key value pairs "ontFlow" and "ontRegime"
    
    # extract outputs from x
    variable = x["variable"]


    # code to check against flow limits here....

    
    return {"ontFlow": ontFlow, "ontRegime": ontRegime}

-------------------------------------------------------------------------------
"""
