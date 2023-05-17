# Optimization of Lake Ontario Flow Regulation

This repo contains code to generate water supply forecasts, optimize flow regulation plans, assess policy robustness across plausible climate scenarios, and explore results in an interactive dashboard.

![workflow](resources/workflow.png)

<br>

# Table of Contents

- [Overview](#overview)
    - [Plan 2014 Control Policy](#plan-2014-control-policy)
- [Getting Started](#getting-started) 

<br>

# Overview

<!-- <details>
<summary><h2>Overview</h2></summary>
</details> -->

This section describes the current flow regulation plan of the LOSLR system, key decision variables that are optimized within Plan 2014 to discover new, alternative control policies, and objective functions that measure system performance for alternative control policies.

## Plan 2014

The current control policy, [Plan 2014](resources/Plan_2014_Report.pdf), takes in the current water level of Lake Ontario, $Level_{Ont}$, and a forecasted supply index, $NTS_{fcst}$, and prescribes releases based on a sliding rule curve function and adjusts the rule curve release via embedded flow constraints. 

The forecasted supply index, $NTS_{fcst}$, at any given quarter-month, $q$, is calculated by inputing the rolling average annual net total supply calculated into an autoregressive time series model:

$$ NTS_{prev} = \overline {NTS_{q - 49} : NTS_{q - 1}} $$
$$ NTS_{fcst} = AR_{1}(NTS_{prev}) $$

The sliding rule curve function is based on the pre-project release, $R_{pp}$, conditions, which is calculated using the open-water stage-discharge relationship:

$$ 
R_{pp} = 555.823 * (Level_{Ont} - 0.035 - 69.474)^{1.5} 
$$

The $R_{pp}$ flow amount is adjusted based on recent supply conditions to get the rule curve release, $R_{rc}$, amount:

$$ 
R_{rc} =  \left\{
\begin{array}{ll}
R_{pp} + \displaystyle \left[ \frac {NTS_{fcst} - NTS_{avg}} {NTS_{max} - NTS_{avg}} \right] ^ {P_1} * C_1 & NTS_{fcst} \ge NTS_{avg} \\
\\
R_{pp} - \displaystyle \left[ \frac {NTS_{avg} - NTS_{fcst}} {NTS_{avg} - NTS_{min}} \right] ^ {P_2} * C_2 & NTS_{fcst} \lt NTS_{avg} \\
\end{array} 
\right. 
$$

The $R_{rc}$ prescribed flow is then checked against a series of flow limits, which are embedded within Plan 2014 to protect various system needs and interests. For example, the I-limit constrains flows during ice formation to prevent an ice jam and the L-limit constrains flows during navigation season to maintain safe velocities for ship navigability. More information on flow limits can be found in the [Plan 2014 Compendium Report](resources/Plan2014_CompendiumReport.pdf).

## Control Policy Optimization
Given legal and regulatory operating requirement, we optimize key decision variable in the rule curve function and leave the flow limits as is. 

## Objective functions
Write-up of objective functions

<br>

# Getting Started

## Many-Objective Evolutionary Algorithm

Before any runs, you will need to download and compile the many-objective evolutionary algorithm, Borg. A two-part tutorial on setup (with an example) is available [here](https://waterprogramming.wordpress.com/2015/06/25/basic-borg-moea-use-for-the-truly-newbies-part-12/) by the Reed Lab at Cornell University. Once you have compiled Borg, you can introduce new simulation and evaluation problems.

## Demo run
In this example, the `plan2014_wrapper.py` script talks to Borg. In the wrapper script, you can specify the number of decision variables and their ranges, the number of objectives, the epsilon of significance for each objective value, and other parameters of the Borg MOEA.

The wrapper script points to an external simulation-evaluation function, in this case `plan2014_optim.py`. The simulation function takes in an array of decision variables, simulates the time series of water levels and flows over a given supply sequence, calculates objective performance over the time series, and returns an array of length n, where n is the number of objectives, to Borg.

You'll need to move the `borg.c`, `borg.py`, and `libborg.so` to the directory with your wrapper script.


