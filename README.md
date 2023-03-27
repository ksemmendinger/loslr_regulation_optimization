# Plan 2014 Optimization

This repo contains code for the optimization wrapper, simulation model, and objective functions to optimize the Plan 2014 control policy.

Before any runs, you will need to download and compile the many-objective evolutionary algorithm, Borg. A two-part tutorial on setup (with an example) is available [here](https://waterprogramming.wordpress.com/2015/06/25/basic-borg-moea-use-for-the-truly-newbies-part-12/) by the Reed Lab at Cornell University.

Once you have compiled Borg, you can introduce new simulation and evaluation problems.

In this example, the plan2014_wrapper.py script talks to Borg. In the wrapper script, you can specify the number of decision variables and their ranges, the number of objectives, the epsilon of significance for each objective value, and other parameters of the Borg MOEA.

The wrapper script points to an external simulation-evaluation function, in this case plan2014_optim.py. The simulation function takes in an array of decision variables, simulates the time series of water levels and flows over a given supply sequence, calculates objective performance over the time series, and returns an array of length n, where n is the number of objectives, to Borg.

You'll need to move the borg.c, borg.py, and libborg.so to the directory with your wrapper script.
