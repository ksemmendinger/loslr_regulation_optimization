### Input Data

Input hydrologic files are provided for the historic supply data from 1900 - 2020 (`input/historic/hydro`). The following are required inputs to simulate a hydrologic time series:

<details closed>
<summary><code>Supply Data</code></summary>
<br>

| Variable Name | Description |
| --- | --- |
| Sim | Simulation time step |
| Year | Simulation year |
| Month | Simulation month |
| QM | Simulation quarter-month |
| ontLevelMOQ | Lake Ontario mean-of-quarter water level. 1-year of spinup required.|
| ontNBS | True Ontario net basin supply. 1-year of spinup required. |
| erieOut | True Lake Erie outflows. 1-year of spinup required. |
| stlouisontOut | True Lac St. Louis - Lake Ontario flows [abstraction of Ottawa River + other tributary inflows]. Also known as SLON. 1-year of spinup required.|
| ontNTS | True Ontario net total supply. 1-year of spinup required. |
| desprairiesOut | Flows out of Des Praries River |
| stfrancoisOut | Flows out of St. Francois River |
| richelieuOut | Flows out of Richelieu River |

</details>

<details closed>
<summary><code>Forecast Information</code></summary>
<br>

| Variable Name | Description |
| --- | --- |
| forNTS | Forecast annual average Ontario net total supply over the next 48 quarter-months from long-term forecast |
| indicator | Whether forNTS is wet (1), dry (-1), or neither (0) |
| confidence | Confidence in how wet or dry forNTS is [1 = not confident, 2= average confidence, 3 = very confident] |
| ontNBS_QM1 | First (of four) quarter-month forecast of Ontario net basin supply from short-term forecast |
| ontNBS_QM2 | Second (of four) quarter-month forecast of Ontario net basin supply from short-term forecast |
| ontNBS_QM3 | Third (of four) quarter-month forecast of Ontario net basin supply from short-term forecast |
| ontNBS_QM4 | Fourth (of four) quarter-month forecast of Ontario net basin supply from short-term forecast |
| erieOut_QM1 | First (of four) quarter-month forecast of Lake Erie outflows from short-term forecast |
| erieOut_QM2 | Second (of four) quarter-month forecast of Lake Erie outflows from short-term forecast |	
| erieOut_QM3 | Third (of four) quarter-month forecast of Lake Erie outflows from short-term forecast |
| erieOut_QM4 | Fourth (of four) quarter-month forecast of Lake Erie outflows from short-term forecast |
| ontNTS_QM1 | First (of four) quarter-month forecast of Ontario net total supply (Ontario net basin supply + Lake Erie outflows) from short-term forecast |
| ontNTS_QM2 | Second (of four) quarter-month forecast of Ontario net total supply (Ontario net basin supply + Lake Erie outflows) from short-term forecast |
| ontNTS_QM3 | Third (of four) quarter-month forecast of Ontario net total supply (Ontario net basin supply + Lake Erie outflows) from short-term forecast |
| ontNTS_QM4 | Fourth (of four) quarter-month forecast of Ontario net total supply (Ontario net basin supply + Lake Erie outflows) from short-term forecast |
| slonFlow_QM1 | First (of four) quarter-month forecast of Lac St. Louis - Lake Ontario flows [abstraction of Ottawa River flows] from short-term forecast |
| slonFlow_QM2 | Second (of four) quarter-month forecast of Lac St. Louis - Lake Ontario flows [abstraction of Ottawa River flows] from short-term forecast |
| slonFlow_QM3 | Third (of four) quarter-month forecast of Lac St. Louis - Lake Ontario flows [abstraction of Ottawa River flows] from short-term forecast |
| slonFlow_QM4 | Fourth (of four) quarter-month forecast of Lac St. Louis - Lake Ontario flows [abstraction of Ottawa River flows] from short-term forecast |

</details>

<details closed>
<summary><code>Indicator Variables</code></summary>
<br>

| Variable Name | Description |
| --- | --- |
| iceInd | Ice indicator [0 = no ice, 1 = formed/stable ice, 2 = unstable/forming ice] |
| tidalInd | Tidal signal |
| foreInd | Perfect forecast indicator [whether to use forecasted or observed SLON values] |

</details>

<details closed>
<summary><code>Roughness Coefficients</code></summary>
<br>

| Variable Name | Description |
| --- | --- |
| longsaultR | Roughness coefficient at Long Sault Dam |
| saundershwR | Roughness coefficient at the headwaters of Moses-Saunders Dam |
| ptclaireR | Roughness coefficient at Pointe-Claire |
| ogdensburgR | Roughness coefficient at Ogdensburg |
| cardinalR | Roughness coefficient at Cardinal |
| iroquoishwR | Roughness coefficient at the headwaters of Iroquois Dam |
| iroquoistwR | Roughness coefficient at the tailwaters of Iroquois Dam |
| morrisburgR | Roughness coefficient at Morrisburg |
| saunderstwR | Roughness coefficient at the tailwaters of Moses-Saunders Dam |
| cornwallR | Roughness coefficient at Cornwall |
| summerstownR | Roughness coefficient at Summerstown |
| jetty1R | Roughness coefficient at Jetty 1 |
| varennesR | Roughness coefficient at Varennes |
| sorelR | Roughness coefficient at Sorel |
| stpierreR	 | 	Roughness coefficient at Saint-Pierre |
| threeriversR | Roughness coefficient at Trois-Rivières |
| batiscanR | Roughness coefficient at Batiscan |

</details>