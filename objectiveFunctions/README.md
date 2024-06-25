# Objective Functions

The `objectiveFunctions/` folder is structured to easily switch between objective function (i.e. performance indicators (PI)) formulations and models. Formulations are stored within named folders in the `objectiveFunctions/` directory. For example, objective functions based on the legacy PI model formulations are stored within the `objectiveFunctions/legacyPIs/` directory. Individual objective functions are stored in the `functions/` directory of the formulation folder. Non-hydrologic input data for the objective functions are stored in the `data/` directory of the formulation folder.

Each objective function script has 3 major components:

1. Reading in non-hydrologic input data (*if applicable*)
2. Calculating the PI value at each time step
3. Running the PI model for the full time series of water levels and flows


```python
# non-hydrologic input data or parameters for the PI model
pars = pd.read_csv("non-hydrologic_inputs.csv")

# calculates the impact at a given timestep
def piModel(input_t, pars):

  return pi_t

# calls piModel() for the entire time series, data, returned from `simulation()`
def runModel(data):

  pi = []
  for t in data:
    input_t = data[t]
    pi_t = piModel(input_t, pars)
    pi.append(pi_t)

  return pi

```

This folder contains data and code for the objective functions used to assess plan performance. Objective functions can be run in `optimization` or `simulation` mode. In **optimization** model, aggregate metrics for each objective function are used as the metric to represent overall policy performance. The default aggregate metric is the **net annual average**. In **simulation** mode, data frames of **time series** are returned for the quarter-monthly or annual performance values for the simulated hydrologic trace.

There are 7 PI models included in the repository:

1) [Upstream Flooding Impacts](#upstream-flooding-impacts)
2) [Downstream Flooding Impacts](#downstream-flooding-impacts)
3) [Commercial Navigation Costs](#commercial-navigation-costs)
4) [Hydropower Production](#hydropower-production)
5) [Meadow Marsh Area](#meadow-marsh-area)
6) [Muskrat Wintertime Lodge Viability](#muskrat-lodge-viability)
7) [Recreational Boating Costs](#recreational-boating-costs)

These models are primarily based on the legacy PI models used in the LOSLR Study (with some minor updates). The PIs are described in more detail [below](#legacy-pi-models).

<br>

### Legacy PI Models

#### Upstream Flooding Impacts

  - *Unit:* Number of homes flooded
  - *Timestep:* Quarter-monthly
  - *Location:* Lake Ontario, Alexandria Bay (NY), Cardinal (ON)
  - *Inputs:* Month, Lake Ontario level, Alexandria Bay level, Cardinal level

The number of homes flooded at certain water level were obtained from the [Decision Support Tool](../resources/Phase1Report_GLAM.pdf) developed by the US Army Corps of Engineers for the Board of Control. Impacts are based on static water levels for locations on the St. Lawrence River (Alexandria Bay and Cardinal). Lake Ontario impacts are based on static water levels as well as expected dynamic impacts driven by storm-related process depending on the time of year (i.e., month). 

**Optimization**: In a given time step, the impacts across the three locations are summed, and the net annual average over the simulation period is used as the reporting metric (float)

**Simulation**: Spatially disaggregated impacts over the simulation period (dataframe) with output:

  - Aggregated Upstream: `upstreamCoastal`
  - Lake Ontario: `ontarioCoastal`
  - Alexandria Bay: `alexbayCoastal`
  - Cardinal: `cardinalCoastal`

#### Downstream Flooding Impacts

  - *Unit:* Number of homes flooded
  - *Timestep:* Quarter-monthly
  - *Location:* Lery-Beauharnois (QC), Pointe-Claire (QC), Maskinonge (QC), Sorel (QC), Lac St. Pierre (QC), Trois-Rivieres (QC)
  - *Inputs:* Lery-Beauharnois level, Pointe-Claire level, Maskinonge level, Sorel level, Lac St. Pierre level, Trois-Rivieres level
  
The number of homes flooded at certain water level were obtained from the [Decision Support Tool](../resources/Phase1Report_GLAM.pdf) developed by the US Army Corps of Engineers for the Board of Control. Impacts are based on static water levels for all locations along the St. Lawrence River. 

**Optimization**: In a given time step, the impacts across the six locations are summed, and the net annual average over the simulation period is used as the reporting metric (float)

**Simulation**: Spatially disaggregated impacts over the simulation period (dataframe) with output:

  - Aggregated Downstream: `downstreamCoastal`
  - Lery-Beauharnois: `lerybeauharnoisCoastal`
  - Pointe-Claire: `ptclaireCoastal`
  - Maskinonge: `maskinongeCoastal`
  - Sorel: `lacstpierreCoastal`
  - Lac St. Pierre: `sorelCoastal`
  - Trois-Rivieres: `troisrivieresCoastal`

#### Commercial Navigation Costs
  - *Unit:* USD
  - *Timestep:* Quarter-monthly
  - *Location:* Lake Ontario, the Seaway (Upper St. Lawrence to Montreal), downstream of Montreal
  - *Inputs:* Quarter-month, Lake Ontario level, Kingston level, Ogdensburg level, Cardinal level, Iroquois headwaters level, Iroquois tailwaters level, Morrisburg level, Long Sault level, Summerstown level, Pointe-Claire level, St. Lambert level, Jetty1 level, Sorel level, Trois-Rivieres level, Lake Ontario release, ice indicator, freshet indicator

Commercial navigation is split into three geographic regions: across Lake Ontario, through the St. Lawrence Seaway, and Montreal downstream to Quebec City. Cost estimates are based on the original PI models used in Plan 2014 evaluation, which calculate loading costs, gradient costs (Seaway only), waiting costs, delay costs (Montreal only), and speed costs (Seaway only). The cost tables were updated during the the [2018 Review](../resources/2018_GLAM_Review.pdf). Commercial navigation has first overall operating precedence in the Boundary Waters Treaty of 1909.

**Optimization**: In a given time step, the impacts across the three locations are summed, and the net annual average over the simulation period is used as the reporting metric (float)

**Simulation**: Spatially disaggregated impacts over the simulation period (dataframe) with output:

  - Aggregated Costs: `totalCommercialNavigation`
  - Lake Ontario: `ontarioCommercialNavigation`
  - St. Lawrence Seaway: `seawayCommercialNavigation`
  - Downstream of Montreal: `montrealCommercialNavigation`

#### Hydropower Production
  - *Unit:* USD
  - *Timestep:* Quarter-monthly
  - *Location:* Moses-Saunders Dam and Niagara Power Generation Station
  - *Inputs:* Quarter-month, Lake Ontario release, Lake Erie outflow, Lake Ontario level, Moses-Saunders headwaters level, Moses-Saunders tailwaters level

Hydropower at the Moses-Saunders and Niagara Power Generation Station is generated by Ontario Power Generation (OPG) and New York Power Authority (NYPA). Production value estimates are based on the original PI models used in Plan 2014 evaluation and were updated during the the [2018 Review](../resources/2018_GLAM_Review.pdf). Hydropower has second overall operating precedence in the Boundary Waters Treaty of 1909.

**Optimization**: In a given time step, the impacts across the two locations and both companies are summed, and the net annual average over the simulation period is used as the reporting metric (float)

**Simulation**: Spatially disaggregated impacts over the simulation period (dataframe) with output:

  - Aggregated Production Value: `totalEnergyValue`
  - OPG @ Moses-Saunders: `opgMosesSaundersEnergyValue`
  - NYPA @ Moses-Saunders: `nypaMosesSaundersEnergyValue`
  - Peaking Value at Moses-Saunders: `peakingMosesSaundersValue`
  - OPG @ Niagara: `opgNiagaraEnergyValue`
  - NYPA @ Niagara: `nypaNiagaraEnergyValue`

#### Meadow Marsh Area
  - *Unit:* Hectares
  - *Timestep:* Annually
  - *Location:* Lake Ontario
  - *Inputs:* Lake Ontario level, Lake Ontario net total supply

Meadow marsh presence is calculated following the methodology outlined in [Wilcox et al. 2005](../resources/Wetlands_2005.pdf). Net total supply is used to identify years of low supplies, which drive meadow marsh formation and persistence. During Plan 2014 evaluation, meadow marsh was identified as a fair proxy for overall wetland health.

**Optimization**: The annual average over the simulation period is used as the reporting metric (float)

**Simulation**: Annual meadow marsh coverage over the simulation period (dataframe) with output:

  - Meadow Marsh Area: `mmArea`
  - Low Supply Indicator: `mmLowSupply`

#### Muskrat Lodge Viability
  - *Unit:* Probability
  - *Timestep:* Annually
  - *Location:* Thousand Islands Region in the Upper St. Lawrence River (Alexandria Bay, NY)
  - *Inputs:* Alexandria Bay water level

Muskrat wintertime house density is used as a proxy for emergent marsh presence, which is a critical habitat zone for many species-at-risk. Lodge viability estimates are based on a 1D PI model provided by the GLAM Phase 2 ISEE technical working team.

**Optimization**: The annual average over the simulation period is used as the reporting metric (float)

**Simulation**: Annual muskrat house density over the simulation period (dataframe) with output:

  - Muskrat Lodge Viability: `muskratProbLodgeViability`

#### Recreational Boating Costs
  - *Unit:* USD
  - *Timestep:* Quarter-monthly
  - *Location:* Lake Ontario, Alexandria Bay (NY), Brockville (ON), Ogdensburg (NY), Long Sault (ON), Pointe-Claire (QC), Varennes (QC), Sorel (QC)
  - *Inputs:* Quarter-month, Lake Ontario level, Alexandria Bay level, Ogdensburg level, Brockville level, Long Sault level, Pointe-Claire level, Varennes level, Sorel level

Recreational boating is a key driver of local tourism in the region. Cost estimates are based on the original PI models used in Plan 2014 evaluation, which costs only accruing during boating season for extremely high and low water levels. The cost tables were updated during the the [2018 Review](../resources/2018_GLAM_Review.pdf). 
**Optimization**: In a given time step, the impacts across the eight locations are summed, and the net annual average over the simulation period is used as the reporting metric (float)

**Simulation**: Spatially disaggregated impacts over the simulation period (dataframe) with output:

  - Aggregated Costs: `totalRecBoating`
  - Lake Ontario: `ontarioRecBoating`
  - Alexandria Bay: `alexbayRecBoating`
  - Brockville: `brockvilleRecBoating`
  - Ogdensburg: `ogdensburgRecBoating`
  - Long Sault: `longsaultRecBoating`
  - Pointe-Claire: `ptclaireRecBoating`
  - Varennes: `varennesRecBoating`
  - Sorel: `sorelRecBoating`