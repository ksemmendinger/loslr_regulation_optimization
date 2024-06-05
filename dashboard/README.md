# Plan Simulation and Optimization Dashboard

This folder contains code for the visual analytics to support rapid plan comparison and evaluation. Results are presented in a R Shiny dashboard. Library requirements for the R environment are available in the `requirements.txt` file.

For efficient load-times, the results from scripts in the `postScripts/` are loaded, formatted, and compressed in the `dataRetrieval.py` file and stored in a `data/` directory in the same folder.

To run the dashboard, you can launch from R Studio or from the terminal using `shiny::runApp()`.