# Optimization of Lake Ontario - St. Lawrence River Flow Regulation

This repo contains code to optimize the Lake Ontario - St. Lawrence River (LOSLR) flow regulation. 

## Plan 2014 Control Policy

The current control policy, [Plan 2014](resources/Plan_2014_Report.pdf), prescribes releases based on a sliding rule curve function and adjusts the rule curve release via embedded flow constraints. 

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

## Many-Objective Evolutionary Algorithm

Before any runs, you will need to download and compile the many-objective evolutionary algorithm, Borg. A two-part tutorial on setup (with an example) is available [here](https://waterprogramming.wordpress.com/2015/06/25/basic-borg-moea-use-for-the-truly-newbies-part-12/) by the Reed Lab at Cornell University.

Once you have compiled Borg, you can introduce new simulation and evaluation problems.

In this example, the plan2014_wrapper.py script talks to Borg. In the wrapper script, you can specify the number of decision variables and their ranges, the number of objectives, the epsilon of significance for each objective value, and other parameters of the Borg MOEA.

The wrapper script points to an external simulation-evaluation function, in this case plan2014_optim.py. The simulation function takes in an array of decision variables, simulates the time series of water levels and flows over a given supply sequence, calculates objective performance over the time series, and returns an array of length n, where n is the number of objectives, to Borg.

You'll need to move the borg.c, borg.py, and libborg.so to the directory with your wrapper script.

![workflow](resources/workflow.png)
