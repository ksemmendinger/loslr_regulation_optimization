# import libraries
import numpy as np


# custom normalization function
def minmaxNorm(x, xRange, normRange, method="transform"):
    # normalization range bounds
    a = np.min(normRange)
    b = np.max(normRange)

    # minimum and maximum variables bounds
    xMin = np.min(xRange)
    xMax = np.max(xRange)

    # transform or backtransform
    if method == "transform":
        val = (b - a) * ((x - xMin) / (xMax - xMin)) + a

    elif method == "backtransform":
        val = (x - a) * ((xMax - xMin) / (b - a)) + xMin

    else:
        val = np.nan

    return val


def round_d(x, k):
    K = 10**k
    temp = abs(x * K)
    remainder = int(temp) % 2
    if remainder == 0:
        newval = temp + 0.4999999
    else:
        newval = temp + 0.5000001
    if x >= 0:
        result = int(newval) / K
    else:
        result = -int(newval) / K
    return result


# # shape ANN decision variables for the number of neurons (N), inputs (M), and outputs (K)
# def formatDVs(N, M, K, vars):
#     # first elements (# neurons x # inputs) - weights to 1st hidden layer
#     w1 = np.array(vars[0 : (N * M)]).reshape(N, M)

#     # next elements (# neurons x 1) - neuron biases of 1st hidden layer
#     b1 = np.array(vars[(N * M) : (N * M + N)]).reshape(N, 1)

#     # next elements (# outputs x # neurons) - weights to output layer
#     w2 = np.array(vars[(N * M + N) : (len(vars) - K)]).reshape(K, N)

#     # last elements (# outputs x 1) - output layer biases
#     b2 = np.array(vars[-K:]).reshape(K, 1)

#     pars = {}
#     pars["w1"] = w1
#     pars["b1"] = b1
#     pars["w2"] = w2
#     pars["b2"] = b2

#     return pars


# # ANN policy takes in input vector, x, and optimized weight/biases, pars
# def annPolicy(x, pars):
#     # optimized decision variables
#     w1 = pars["w1"]
#     b1 = pars["b1"]
#     w2 = pars["w2"]
#     b2 = pars["b2"]

#     # input layer to hidden layer (W * X + B)
#     hiddenLayer = w1.dot(x) + b1

#     # # activation function on hidden layer output - sigmoid
#     # hiddenLayer = 1 / (1 + np.exp(-hiddenLayer1))

#     # activation function on hidden layer output - tanh
#     hiddenLayerAct = 2 / (1 + np.exp(-2 * hiddenLayer)) - 1

#     # hidden layer to output layer (W * H + B)
#     outputLayer = w2.dot(hiddenLayerAct) + b2

#     # # activation function on output layer - sigmoid
#     # outputLayer = 1 / (1 + np.exp(-outputLayer))

#     # activation function on output layer - tanh
#     outputLayerAct = 2 / (1 + np.exp(-2 * outputLayer)) - 1

#     # convert output array to list
#     # output = outputLayerAct.tolist()
#     output = outputLayerAct

#     return output
