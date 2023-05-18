# Objective Function Formulation

This folder contains data and code for the objective functions used to assess plan performance. There are 7 objective functions used to measure policy performance:

1) Flooding impacts upstream of the dam
2) Flooding impacts downstream of the dam
3) Commercial navigation costs downstream of Montreal, through the Seaway, and on Lake Ontario
4) Hydropower production at the Moses-Saunders Dam and the Niagara Power Generation Station
5) Meadow marsh contribution to wetland area on Lake Ontario
6) Muskrat house density on the Upper St. Lawrence River
7) Recreational boating costs on Lake Ontario and the St. Lawrence River




For efficient load-times, the results from scripts in the `postScripts/` are loaded, formatted, and compressed in the `dataRetrieval.py` file and stored in a `data/` directory in the same folder.

To run the dashboard, you can deploy directly from R Studio or from the terminal using `shiny::runApp()`.
