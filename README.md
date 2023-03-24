# Plan 2014 Optimization
**Framework to optimize and simulate the Plan 2014 control policy with system objectives**

This repo contains code for the optimization wrapper, simulation model, and objective functions to optimize the Plan 2014 control policy.

Before any runs, you will need to download and compile the many-objective evolutionary algorithm, Borg. A two-part tutorial on setup (with a simple example) is available [here](https://waterprogramming.wordpress.com/2015/06/25/basic-borg-moea-use-for-the-truly-newbies-part-12/) by the Reed Lab at Cornell University.

The plan2014_wrapper.py script sets up the optimization problem, sets the decision variables, number of objectives, and points Borg to the simulation model. The plan2014_optim.py script takes in decision variable values from Borg, simulates water levels and flows over the 120 year historic record, calculates aggregate performance indicator scores over the simulation period for each of the 6 objectives, and returns the objective scores to Borg. 
