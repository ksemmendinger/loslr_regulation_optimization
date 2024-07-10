# Plan Simulation and Optimization Dashboard

This folder contains code for the visual analytics to support rapid plan comparison and evaluation. Results are presented in a R Shiny dashboard. Library requirements for the R environment are available in the `requirements.txt` file.

To run the dashboard, you can launch directly from R Studio by running the `app.R` script or from the terminal, shown below:

```bash
conda activate r-shiny      # activate shiny specific conda environment
cd dashboard/               # navigate to folder where dashboard script is stored
r                           # launch r
shiny::runApp()             # launch app
```

The first page of the dashboard displays the parallel axis plot for the user-selected experiment(s).

![workflow](dashboard/resources/1_select_experiment.mov)

Users may update the satisficing criteria using the filters on the left side of the page to screen out selected policies. Users may also brush out policies by selecting them directly from the parallel axis plot. 

To export the policies to simulate, press `Export Table` and `satisficingPolicies.csv` will automatically be saved to the experiment directory.






 By default, results are displayed in comparison to GLRRM-simulated Plan 2014 Basis of Comparison (`Plan2014_GLRRM`). Users may also select to display results normalized by the GLRRM-simulated Bv7 module by toggling the gear at the top-left of the parallel axis plot and selecting `Bv7_GLRRM`.

<!-- For efficient load-times, the results from scripts in the `postScripts/` are loaded, formatted, and compressed in the `output/dataPrep.py` file and stored in a `data/` directory in the same folder. -->

