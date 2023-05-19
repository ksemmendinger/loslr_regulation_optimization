# Objective Function Formulation

This folder contains data and code for the objective functions used to assess plan performance. The objective functions can be run in `optimization` or `simulation` mode. There are 7 objective functions used to measure policy performance.

1) [Upstream Flooding Impacts](#upstream-flooding-impacts)
2) [Downstream Flooding Impacts](#downstream-flooding-impacts)
3) [Commercial Navigation Costs](#commercial-navigation-costs)
4) [Hydropower Production](#hydropower-production)
5) [Meadow Marsh Area](#meadow-marsh-area)
6) [Muskrat House Density](#muskrat-house-density)
7) [Recreational Boating Costs](#recreational-boating-costs)
    
In **optimization** mode (`plan2014optim.py`), the **net annual average** values for each objective function are used as the metric to represent overall policy performance. 

In **simulation** mode (`output/postScripts/policySimulation.py`), data frames or **time series** are returned for the quarter-monthly or annual performance values for the simulated hydrologic trace.

<br>

### Upstream Flooding Impacts
  - *Unit:* Number of homes flooded
  - *Timestep:* Quarter-monthly
  - *Location:* Lake Ontario, Alexandria Bay (NY), Cardinal (ON)

The number of homes flooded at certain water level were obtained from the [Decision Support Tool](../resources/Phase1Report_GLAM.pdf) developed by the US Army Corps of Engineers for the Board of Control. Impacts are based on static water levels for all locations. Additional Lake Ontario impacts are i

<br>

### Downstream Flooding Impacts
  - *Unit:* Number of homes flooded
  - *Timestep:* Quarter-monthly
  - *Location:* Lery-Beauharnois (QC), Pointe-Claire (QC), Maskinonge (QC), Sorel (QC), Lac St. Pierre (QC), Trois-Rivieres (QC)

<br>

### Commercial Navigation Costs
  - *Unit:* USD
  - *Timestep:* Quarter-monthly
  - *Location:* Lake Ontario, the Seaway (Upper St. Lawrence to Montreal), downstream of Montreal

<br>

### Hydropower Production
  - *Unit:* USD
  - *Timestep:* Quarter-monthly
  - *Location:* Moses-Saunders Dam and Niagara Power Generation Station

<br>

### Meadow Marsh Area
  - *Unit:* Hectares
  - *Timestep:* Annually
  - *Location:* Lake Ontario

<br>

### Muskrat House Density
  - *Unit:* Dimensionless
  - *Timestep:* Annually
  - *Location:* Thousand Islands Region in the Upper St. Lawrence River (Alexandria Bay, NY)

<br>

### Recreational Boating Costs
  - *Unit:* USD
  - *Timestep:* Quarter-monthly
  - *Location:* Lake Ontario, Alexandria Bay (NY), Brockville (ON), Ogdensburg (NY), Long Sault (ON), Pointe-Claire (QC), Varennes (QC), Sorel (QC)
  
<br>
