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


# custom engineering rounding function -- taken from GLRRM
# https://github.com/cc-hydrosub/GLRRM-Ontario/blob/b53112cb87bff5f1b661796e5a2ff53096cfc06c/glrrm/util/cython_funcs/cmath.py#L9
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
