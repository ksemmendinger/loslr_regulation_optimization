"""
-------------------------------------------------------------------------------

this script contains a template for the `formatDecisionVariables`, 
`getReleaseFunctionInputs`, and `releaseFunction` functions

-------------------------------------------------------------------------------
"""

"""
-------------------------------------------------------------------------------

# import libraries
import numpy as np

# import custom function for engineering rounding
import sys
sys.path.append(".")
from functions.utils import round_d

# format raw decision variables from optimization algorithm
def formatDecisionVariables(vars, **args):

    # INPUTS
    # vars: list of decision variable values returned from the Borg MOEA
    # args: dict of optional release function inputs from config["releaseFunction"]


    # OUTPUTS
    # pars: dict with key value pairs of decision variable names and values

    pars = dict()
    pars["decisionVariable1"] = vars[0]
    pars["decisionVariable2"] = vars[1]

    return pars


# extracts timestep inputs for `releaseFunction`
def getReleaseFunctionInputs(data, t, **args):

    # INPUTS
    # data: dictionary of input time series from main simulation function
    # keys are variable names and values are np.arrays of the time series of 
    # the variable values
    # t: timestep from simulation for loop
    # args: dict of optional release function inputs from config["releaseFunction"]

    # OUTPUTS
    # x: dictionary with named key value pairs of hydrologic inputs at the
    # timestep of interest, calculated or formatted as needed

    x = dict()
    x["variable1"] = data["variable1"][t]
    x["variable2"] = np.mean(data["variable2"][(t - 48) : (t)])

    
    # code to extract, calculate, or format needed inputs for `releaseFunction`....


    return x


# takes in output from formatDecisionVariables and getInputs, outputs release and flow regime
def releaseFunction(x, pars, **args):
    
    # INPUTS
    # x: dict that is output from `getReleaseFunctionInputs`
    # pars: dict that is output from `formatDecisionVariables`
    # args: dict of optional release function inputs from config["releaseFunction"]

    # OUTPUTS
    # dictionary with named key value pairs "ontFlow" and "ontRegime", "pprFlow", and "rfOutput"
    
    # extract outputs from x
    variable1 = x["variable1"]
    variable2 = x["variable2"]

    # extract decision variables from pars
    decisionVariable1 = pars["decisionVariable1"]
    decisionVariable2 = pars["decisionVariable2"]

    
    # code for release function here....


    # return all the relevant outputs to save in dataframe
    outputs = dict()
    outputs["rfFlow"] = ontFlow
    outputs["rfRegime"] = ontRegime
    outputs["pprFlow"] = preproj flow or np.nan
    outputs["rfOutput"] = output from release function (could be the same as ontFlow)

    return outputs

-------------------------------------------------------------------------------
"""
