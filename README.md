# Optimization and Simulation of Lake Ontario - St. Lawrence River (LOSLR) Flow Regulation

### Background

Outflows from Lake Ontario are regulated at the [Moses-Saunders Dam](https://www.google.com/maps/place/Moses-Saunders+Power+Dam,+Cornwall,+ON+K6J+5E3,+Canada/@45.0025651,-74.8008106,14z/data=!4m6!3m5!1s0x4ccc17a553817bf7:0x249b9c21d02310c4!8m2!3d45.0077955!4d-74.7923992!16s%2Fm%2F0j438n5?entry=ttu), which is located downstream on the St. Lawrence River near Cornwall, Ontario and Massena, New York. The Moses-Saunders Dam spans the border of the United States and Canada and is jointly managed by the two countries by the [International Lake Ontario - St. Lawrence River Board](https://ijc.org/en/loslrb), at the direction of the [Internation Joint Commission](https://ijc.org/en). The current flow regulation plan of the LOSLR system is [Plan 2014](./resources/Plan_2014_Report.pdf), which is the first control policy in the system to use forecasts to guide release decisions. **The repository contains a framework to identify alternative forecast-informed reservoir operating (FIRO) policies using a simulation and optimization approach.**

### Repository Overview

There are two major components to the workflow in this repository: the **[simulation and optimization](#simulation-optimization)** of alternative outflow control policies and the **[visualization and data analysis](#data-visualization-and-post-analysis)** on optimized alternatives. This repository contains code to:

1. Optimize control policies
1. Simulate plan prescribed outflows and water levels
1. Assess policy performance for system objectives
1. Explore results in an interactive dashboard
1. Perform a time-varying sensitivity analysis (and other analyses) on policy alternatives

For more information on running the policy simulation and optimization framework, see [Getting Started](#getting-started).

<!-- For forecast generation, see [this](https://github.com/ksemmendinger/Plan-2014-Python) repository. -->

<br>

![workflow](resources/workflow.png)

*Disclaimer: While the Bv7 rule curve and flow limit functions have been verified using the [Great Lakes Regulation and Routing Model](https://github.com/cc-hydrosub/GLRRM-Ontario), this repository is **not** intended to simulate official Plan 2014 prescribed outflows and simulate the resulting water levels.*

<br>

## Simulation-Optimization

There are seven major components required to simulate and optimize alternative control policies, which are described in more detail below:

1. [Configuration File](#configuration-file)
1. [Optimization Algorithm](#optimization-algorithm)
1. [Input Data File](#input-data)
1. [Release Function](#release-function)
1. [Flow Limit Function](#flow-limits)
1. [Routing Function](#routing-scheme)
1. [Objective Functions](#objective-functions)

This repository makes a **key assumption** that a control policy is made up of two modules: a ***release function*** and ***flow limits*** (or operational adjustments). The release function calculates a preliminary flow, which is then checked against a series of flow limits and modified if the preliminary flow falls outside of those flow limits. Flow limits are a major component of flow regulation in the Plan 2014 control policy (e.g. I-limit, L-limit, F-limit). See Annex B, Section B2 in the [Plan 2014 Compendium Report](resources/Plan2014_CompendiumReport.pdf) for more details. The Bv7 ruleset is included in this repository; however, this repository does not contain code to simulate Board deviations decisions under the [H14 criteria](https://www.ijc.org/en/loslrb/watershed/faq/4#:~:text=Criterion%20H14%20allows%20for%20major,water%20supplies%20to%20Lake%20Ontario.).

### Configuration File
The optimization requires several hyperparameters, decision variables, and simulation modules. These fields are specified in a user-generated configuration file. Configuration files are written using the [toml](https://toml.io/en/) file format. A template and examples of a configuration file can be found [here](config/). The variables that must be specified in a configuration file are described below.

<details closed>
<summary><span><code>[experimentalDesign]</code></span></summary>
<br>

These parameters specify the input files and functions used to guide policy simulation. Each variable should be a `str`.

``` toml
[experimentalDesign]

# file name of the release function (without .py extension)
releaseFunction = "ruleCurve" # type:str

# whether to impose the September Rule (R+) regime on the release function release ["on" or "off"]
septemberRule = "off" # type:str

# file name of the flow limit function (without .py extension)
limitType = "Bv7" # type:str

# file name of the routing function (without .py extension)
stlawRouting = "stlaw" # type:str

# folder name of the hydrologic trace that contains input data that is being optimized over
trace = "historic" # type:str

# path and file name of the input data that is being optimized over
inputFile = "1900_2020/12month_sqAR" # type:str
```

</details>

<details closed>
<summary><span><code>[optimizationParameters]</code></span></summary>
<br>

These are parameters needed to run the many-objective evolutionary algorithm, Borg. Each variable should be an `int`.

``` toml
[optimizationParameters]

# number of decision variables to optimize
numDV = 10 # type: int

# number of objectives
numObj = 7 # type: int

# number of constraints
numCon = 0 # type: int

# number of function evaluations
nfe = 200000 # type: int

# initial population size
popSize = 100 # type: int

# frequency of function evaluations to report metrics
metFreq = 100 # type: int
```

</details>

<details closed>
<summary><span><code>[decisionVariables]</code></span></summary>
<br>

These parameters specify information about the decision varibles. Each variable type is specified below.

``` toml
[decisionVariables]

# list of decision variables names - list of `str` of length of numDV
dvName = []

# list of lower bounds of decision variable ranges - list of `float` of length of numDV
lowerBounds = []

# list of upper bounds of decision variable ranges - list of `float` of length of numDV
upperBounds = []

# whether the decision variables are normalized before input to the simulation model ["True" or "False"]
normalized = ""

# if normalized is True, specify the normalization range
normalizedRange = [int, int]
```

</details>

<details closed>
<summary><span><code>[releaseFunction]</code></span></summary>
<br>

This sections contains specific inputs needed for the user specified release function. These inputs are completely dependent on the release function specified in experimentalDesign.

``` toml
[releaseFunction]

releaseFunctionVariable1 = ""
releaseFunctionVariable2 = ""
```

</details>

<details closed>
<summary><span><code>[performanceIndicators]</code></span></summary>
<br>

These parameters specify information about the performance indicators (i.e. objective functions). Each variable type is specified below.

``` toml
[performanceIndicators]

# file name of the objective function
objectiveFunction = "" # type: str
 
# aggregate metric to return to optimization algorithm
metricWeighting = "" # type: str

# list of performance indicator names - list of `str` of length numObj
piName = []

# list of thresholds of *meaningful* improvements/reductions in performance for each obejctive - list of `float` of length numObj
epsilonValue = []

# list of the direction of improvement for each objective - list of "min" or "max" of length numObj
direction = []
```

</details>

</details>

### Optimization Algorithm
A many-objective evolutionary algorithm (MOEA) is used to optimize control policies for flow regulation. The optimization algorithm used in this repository is the [Borg MOEA](https://doi.org/10.1162/EVCO_a_00075). Before any runs, you will need to download and compile Borg. A two-part tutorial on setup (with an example) is available [here](https://waterprogramming.wordpress.com/2015/06/25/basic-borg-moea-use-for-the-truly-newbies-part-12/) by the Reed Lab at Cornell University. Once you have compiled Borg, you can introduce new simulation and evaluation problems. You will need to move the `borg.c`, `borg.py`, and `libborg.so` to the directory with your wrapper script.

### Input Data

Input hydrologic files are provided for the historic supply data from 1900 - 2020 (`input/historic/hydro`). The required inputs for policy simulation and optimization are described [here](input/README.md).

### Release Function

Release function scripts should contain functions: `formatDecisionVariables` to format decision variables, `getReleaseFunctionInputs` to extract the release function inputs from the dictionary of input data, and `releaseFunction` to prescribe a preliminary flow based on the inputs. Each function's inputs and outputs are described below.

<details closed>
<summary><code>formatDecisionVariables()</code></summary>
<br>

```python
# format raw decision variables from optimization algorithm
def formatDecisionVariables(vars, **args):

    # INPUTS
    # vars: list of decision variable values returned from the Borg MOEA
    # args: dict of optional release function inputs from the configuration file in "releaseFunction" section

    # OUTPUTS
    # pars: dict with key value pairs of decision variable names and values
    
    # code to format decision variables values for `releaseFunction` ...

    return pars
```

</details>

<details closed>
<summary><code>getReleaseFunctionInputs()</code></summary>
<br>

```python
# extracts timestep inputs for `releaseFunction`
def getReleaseFunctionInputs(data, t, **args):

    # INPUTS
    # data: dictionary of input time series from main simulation function
    # keys are variable names and values are np.arrays of the time series of the variable values
    # t: timestep being simulated in for loop
    # args: dict of optional release function inputs from the configuration file in "releaseFunction" section

    # OUTPUTS
    # x: dictionary with named key value pairs of hydrologic inputs at the
    # timestep of interest, calculated or formatted as needed

    # code to extract, calculate, or format needed inputs for `releaseFunction`....

    return x

```

</details>

<details closed>
<summary><code>releaseFunction()</code></summary>
<br>

```python
# takes in output from formatDecisionVariables and getInputs, outputs release and flow regime
def releaseFunction(x, pars, **args):

    # INPUTS
    # x: dict that is output from `getReleaseFunctionInputs`
    # pars: dict that is output from `formatDecisionVariables`
    # args: dict of optional release function inputs from the configuration file in "releaseFunction" section

    # OUTPUTS
    # dictionary with named key value pairs:
    # "rfFlow": prescribed outflow
    # "rfRegime": regime that prescribed outflow follows
    # "pprFlow": preproj flow or np.nan
    # "rfOutput": output from release function (could be the same as ontFlow)

    # code for release function here....

    # return all the relevant outputs to save in dataframe
    outputs = dict()
    outputs["rfFlow"] = ontFlow
    outputs["rfRegime"] = ontRegime
    outputs["pprFlow"] = pprFlow # or np.nan
    outputs["rfOutput"] = rfOutput

    return outputs

```

</details>

Examples for the Plan 2014 rule curve and the ANN policy appoximator release functions can found [here](functions/release). A blank template of a release function can be found [here](functions/release/template.py).

### Flow Limits

Flow limit function scripts should contain functions: `getPlanLimitsInputs` to extract the limit function inputs from the dictionary of input data and `planLimits` to check the preliminary flow against the flow limits and modify if needed. Each function's inputs and outputs are described below.

<details closed>
<summary><code>getPlanLimitsInputs()</code></summary>
<br>

```python
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

    # code to extract, calculate, or format needed inputs for `planLimits`....

    return x
```

</details>

<details closed>
<summary><code>planLimits()</code></summary>
<br>

```python
# function to check (and modify) preliminary flow from release function 
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
    # x: dict that is output from `getPlanLimitsInputs`
    # septemberRule: "off" or the septemberRule function

    # OUTPUTS
    # dictionary with named key value pairs
    # "ontFlow": checked outflow (could be release function or a limit flow)
    # "ontRegime": regime that outflow follows (could be "RF" or other)

    # code to check against flow limits here....

    return {"ontFlow": ontFlow, "ontRegime": ontRegime}

```

</details>

Examples for the Bv7 or Phase 2 updated Bv7 flow limit functions can found [here](functions/limits). A blank template of a flow limit function can be found [here](functions/limits/template.py).

### Routing Scheme

Routing function scripts should contain functions: `getStLawrenceRoutingInputs` to extract the routing function inputs from the dictionary of input data and `stLawrenceRouting` to route the outflow through the system and determine water levels along Lake Ontario and the St. Lawrence River. Each function's inputs and outputs are described below.

<details closed>
<summary><code>getStLawrenceRoutingInputs()</code></summary>
<br>

```python
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

    # code to extract, calculate, or format needed inputs for `stLawrenceRouting`....

    return x
```

</details>

<details closed>
<summary><code>stLawrenceRouting()</code></summary>
<br>

```python
# routes final outflow through system to calculate levels/flows along the St. Lawrence River
def stLawrenceRouting(ontLevel, ontFlow, x):

    # INPUTS
    # ontLevel: water level calculated with observed NTS and final release
    # ontFlow: final outflow for timestep
    # x: dictionary output from `getStLawrenceRoutingInputs`

    # OUTPUTS
    # dictionary with named key value pairs for relevant locations along the st. lawrence river (see below for all locations)

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
```

</details>

Examples for the routing function using SLON flows can found [here](functions/routing/stlaw.py). A blank template of a routing function can be found [here](functions/routing/template.py).

### Objective Functions

Objective functions are simulated over the user-specified time period. Each objective is aggregated by the net annual average value, and that metric is returned to Borg to drive the optimization. More information on the objective function formulations and required inputs can be found [here](objectiveFunctions/).

<br>

## Data Visualization and Post Analysis

1. [Data Preparation](#data-preparation)
    1. [Formatting Raw Data](#formatting-raw-data)
    1. [MOEA Framework](#moea-framework)
1. [Dashboard](#dashboard)
1. [Candidate Policy Selection](#candidate-policy-selection)
1. [Policy Simulation](#policy-simulation)
1. [Secondary Analyses](#secondary-analyses)

### Data Preparation

The raw output from the Borg MOEA is stored in `output/data/**/raw`, where `**` is the folder of the experiment of interest. There will be a `pareto_front_S*.txt` and a `runtime_S*.txt` file for each seed the optimization ran. To visualize results in the dashboard, the raw data needs to be formatted and the MOEA performance metrics need to be calculated using the [MOEA Framework](http://moeaframework.org). There is a [shell script](output/dataPrep.sh) provided to [format the raw data](output/postScripts/dataFormat.py) and [run the MOEA Framework](moeaFramework/find_metrics.sh). Run the `dataPrep.sh` script from terminal and specify the following:

```bash
./dataPrep.sh ${loc} ${folderName} ${nseeds} ${nobjs}
```

1. `${loc}` : the absolute path of the user's home directory (i.e., where the code repository is located)
1. `${folderName}` : the name name of the folder that contains the raw Borg results (in the `output/` directory)
1. `${nseeds}` : the number of random seeds to use in the optimization
1. `${nobjs}` : the number of objectives for which the optimization was run

#### Formatting Raw Data

To format the raw output for the dashboard and other post analyses, run the following command and specifying the following:

```bash
python output/postScripts/dataFormat.py ${loc} ${folderName} ${nseeds} 
```

1. `${loc}` : the absolute path of the user's home directory (i.e., where the code repository is located)
1. `${folderName}` : the name name of the folder that contains the raw Borg results (in the `output/` directory)
1. `${nseeds}` : the number of random seeds to use in the optimization

The script will create and populate the `clean/` and `moeaFramework/` directories in `output/data/**`.

#### MOEA Framework

To run the MOEA Framework, download the [demo application](http://moeaframework.org/downloads.html), and move the `.jar` file to the `moeaFramework/` directory. You may need to update the version number of the `.jar` called in the `find_metrics.sh` script:

```bash
# ensure the version number [2.12] matches your download or update `JAVA_ARGS` accordingly
JAVA_ARGS="-cp MOEAFramework-2.12-Demo.jar"     
```

We recommend using the [`wfg2` method](doi.org/10.1109/TEVC.2010.2077298) to calculate the hypervolume metric. Follow the directions [here](https://github.com/MOEAFramework/Hypervolume?tab=readme-ov-file#wfg-setup) to compile the executable for the `wfg2` hypervolume calculation and move `wfg2` to the `moeaFramework/` directory. The `global.properties` file in the `moeaFramework/` directory tells the MOEA Framework to use the `wfg2` calculation for the hypervolume metric.

**Once everything is compiled and setup, ensure there are four files in the `moeaFramework/` directory: `wfg2`, `MOEAFramework-#-Demo.jar`, `global.properties`, and `find_metrics.sh`.**

The `dataPrep.sh` script calls the `find_metrics.sh` script in the `moeaFramework/` directory. The `find_metrics.sh` script will calculate the hypervolume, generational distance, inverted generational distance, spacing, epsilon indicator, and maximum pareto front error for each of the seeds. Convergence plots are saved in the `output/data/**/moeaFramework/plots` directory. 

### Dashboard

Results from the optimization and simulation of candidate plans for objective functions and *a posteriori* performance indicators are displayed in an interactive dashboard (based in an R Shiny app). First, compile the results by running the following command and specifying the following:


You can then run the dashboard by navigating to the `dashboard/` directory, activating the conda environment, and launching r:

```bash
conda activate r-shiny      # activate shiny specific conda environment
cd dashboard/               # navigate to folder where dashboard script is stored
r                           # launch r
shiny::runApp()             # launch app
```

More detail on running the dashboard is available [here](output/dashboard/README.md).

### Candidate Policy Selection

Once you launch the dashboard, you can select experiments to load in and visualize.

### Policy Re-Simulation

Borg returns the decision variables values of policy that fall on the Pareto Frontier. However, the time series of water levels and objective performance is not returned. To run the simulation model and return the time series of hydrologic attributes and performance indicators, run the `policySimulation.py` script.

### Secondary Analyses

This repository contains code to performa a time-varying sensitivity analysis on candidate policies. Users can add additional analysis scripts to the `output/` folder and call them in the postAnalysis.sh script to run.

<br>

## Getting Started

There are two scripts that drive the policy simulation and optimization: `optimizationWrapper.py` and `optimizationSimulation.py`. The `optimizationWrapper.py` script calls and interacts with the Borg MOEA. The wrapper script reads the user-generated [configuration file](configuration-file) and sets up the optimization experiment. `optimizationWrapper.py` then calls `optimizationSimulation.py` to simulate the time series of outflows, water levels, and system performance that result from the decision variables returned by Borg in each function evaluation.

You can run Borg on your local machine from the command line or on a HPC (see example [bash](./runOptimization_Local.sh) or [SLURM](./runOptimization_HPC.sh) script). Both scripts call the `optimizationWrapper.py` script, which requires three user-specified arguments:

```bash
python optimizationWrapper.py ${loc} ${config} ${S}
```

1. `${loc}` : the absolute path of the user's home directory (i.e., where the code repository is located)
1. `${config}` : the relative path to the configuration file from the home directory
1. `${S}` : the random seed to use in the optimization

To ensure convergence on the Pareto Frontier and avoid falling into local minima/maxima, it is advisable to run multiple seeds per experiment. The `runOptimization_Local.sh` and `runOptimization_HPC.sh` shell scripts are setup to take in the **number of seeds** to run per experiment rather than the **random seed**. To run the shell script locally (or submit a SLURM job on a HPC), users must specify three arguments:

```bash
./runOptimization_Local.sh ${loc} ${config} ${nseeds}
```

1. `${loc}` : the absolute path of the user's home directory (i.e., where the code repository is located)
1. `${config}` : the relative path to the configuration file from the home directory
1. `${nseeds}` : the number of random seeds to use in the optimization

<br>

---