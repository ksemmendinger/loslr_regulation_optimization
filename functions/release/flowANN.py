# import libraries
import sys
import math
import numpy as np
from typing import List, Dict, Union

sys.path.append(".")
from functions.utils import minmaxNorm, round_d


# shape ANN decision variables for the number of neurons (N), inputs (M), and outputs (K)
def formatDecisionVariables(vars: List[float], **args) -> Dict[str, float]:
    N = args["nNeurons"]
    M = args["nInputs"]
    K = args["nOutputs"]

    # first elements (# neurons x # inputs) - weights to 1st hidden layer
    w1 = np.array(vars[0 : (N * M)]).reshape(N, M)

    # next elements (# neurons x 1) - neuron biases of 1st hidden layer
    b1 = np.array(vars[(N * M) : (N * M + N)]).reshape(N, 1)

    # next elements (# outputs x # neurons) - weights to output layer
    w2 = np.array(vars[(N * M + N) : (len(vars) - K)]).reshape(K, N)

    # last elements (# outputs x 1) - output layer biases
    b2 = np.array(vars[-K:]).reshape(K, 1)

    pars = {}
    pars["w1"] = w1
    pars["b1"] = b1
    pars["w2"] = w2
    pars["b2"] = b2

    return pars


# take in dict of hydrologic data and timeslice, output list of inputs for releaseFunction
def getReleaseFunctionInputs(
    data: Dict[str, np.ndarray], t: int, **args
) -> Dict[str, float]:
    x = dict()

    # normalize hydrologic inputs based on ranges supplied in config file - these could change
    nvar = len(args["normalizedVars"])
    for i in range(nvar):
        var = args["normalizedVars"][i]
        value = data[var][t]
        valRange = [args["minValRange"][i], args["maxValRange"][i]]
        normRange = [args["minNormRange"][i], args["maxNormRange"][i]]
        normVal = minmaxNorm(value, valRange, normRange)
        x[var] = normVal

    # calculate harmonics from quarter-month
    qm = data["QM"][t]
    x["cosQM"] = round(
        np.cos(((2 * math.pi) / 48) * (qm - 2.5)), 6
    )  # respresetation of winter [1] - summer [-1] cycle
    x["sinQM"] = round(
        np.sin(((2 * math.pi) / 48) * (qm - 2.5)), 6
    )  # respresetation of spring [1] - fall [-1] cycle

    return x


# ANN policy takes in input vector, x, and optimized weight/biases, pars
def releaseFunction(x, pars, **args):
    # reshape input vector
    x = np.array(list(x.values())).reshape(args["nInputs"], 1)

    w1 = pars["w1"]
    b1 = pars["b1"]
    w2 = pars["w2"]
    b2 = pars["b2"]

    # input layer to hidden layer (W * X + B)
    hiddenLayer = w1.dot(x) + b1

    # # activation function on hidden layer output - sigmoid
    # hiddenLayer = 1 / (1 + np.exp(-hiddenLayer1))

    # activation function on hidden layer output - tanh
    hiddenLayerAct = 2 / (1 + np.exp(-2 * hiddenLayer)) - 1

    # hidden layer to output layer (W * H + B)
    outputLayer = w2.dot(hiddenLayerAct) + b2

    # # activation function on output layer - sigmoid
    # outputLayer = 1 / (1 + np.exp(-outputLayer))

    # activation function on output layer - tanh
    outputLayerAct = 2 / (1 + np.exp(-2 * outputLayer)) - 1

    # convert output array to list
    annOutput = outputLayerAct.flatten().tolist()[0]

    # backcalculate adjustment to cms
    adjRange = args["outputRange"]
    normRange = [-1, 1]  # --> from tanh activation funciton
    release = minmaxNorm(annOutput, adjRange, normRange, method="backtransform")
    ontFlow = round_d(release, 0)
    ontRegime = "RF"

    # return all the relevant outputs to save in dataframe
    # outputs = dict()
    # outputs["ontFlow"] = ontFlow
    # outputs["ontRegime"] = ontRegime

    outputs = dict()
    outputs["rfFlow"] = ontFlow
    outputs["rfRegime"] = ontRegime
    outputs["pprFlow"] = np.nan
    outputs["rfOutput"] = release

    return outputs
