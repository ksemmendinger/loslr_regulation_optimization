# -----------------------------------------------------------------------------
# script setup
# -----------------------------------------------------------------------------

# set working directory
setwd("/Users/kylasemmendinger/Library/CloudStorage/Box-Box/Plan_2014/optimization/output/dashboard")

# clean up
rm(list=ls())
gc()

# load libraries
library(shiny)
library(arrow)
library(DT)
library(stringr) 
library(shinyWidgets)
library(shinycssloaders)
library(arrow)
library(tidyverse)
library(gridExtra)
# library(ggborderline)
library(patchwork)
library(ggtext)
library(ggrepel)
library(ggtips)
library(gtools)
library(ggh4x)
library(reactable)
library(extrafont)
library(reactablefmtr)
library(htmltools)
library(htmlwidgets)
library(webshot)
library(shinybrowser)

# load fonts
# font_import(paths = "/Library/Fonts", pattern = "Arial", prompt = FALSE)
# loadfonts(device = "postscript")

# set number of SOWs
nSOWS <- 1 + 159 + 500

# hide warnings to keep console clean
options(dplyr.summarise.inform = FALSE)

# color palette
blues <- c("#00429d", "#3761ab", "#5681b9", "#73a2c6", "#93c4d2", "#b9e5dd")
getBluePal <- colorRampPalette(blues)
yellow <- "#EECC66"
reds <- rev(c("#ffd3bf", "#ffa59e", "#f4777f", "#dd4c65", "#be214d", "#93003a"))
getRedPal <- colorRampPalette(reds)
fullPal <- c(blues, yellow, rev(reds))
getPal <- colorRampPalette(fullPal)
getRBPal <- colorRampPalette(c(blues, rev(reds)))

status_badge <- function(color = "#aaa", width = "0.55rem", height = width) {
  span(style = list(
    display = "inline-block",
    marginRight = "0.5rem",
    width = width,
    height = height,
    backgroundColor = color,
    borderRadius = "50%"
  ))
}

hTableTheme <- espn()

# -----------------------------------------------------------------------------
# file directory setup and loading
# -----------------------------------------------------------------------------

# set names and paths to output files
filelist <- data.frame(stringsAsFactors = FALSE,
                       "varname" = c("annualObjs", "hydroStats", "h1", "h2", "h3", "h4", "h6", "h7", "h14", "impactZones", "dynamicRob", "dynamicNorm", "staticRob", "staticNorm", "factorRank", "exoHydro"),
                       # "dirname" = c("annualObjectives/annualValues.txt", "hydroStatistics/hydroStatistics.txt", "hCriteria/h1.txt", "hCriteria/h2.txt", "hCriteria/h3.txt", "hCriteria/h4.txt", "hCriteria/h6.txt", "hCriteria/h7.txt", "hCriteria/h14.txt", "impactZones/impactZoneExceedances.txt", "scenarioDiscovery/dynamicRobustness.txt", "scenarioDiscovery/dynamicNormalized.txt", "scenarioDiscovery/staticRobustness.txt", "scenarioDiscovery/staticNormalized.txt", "scenarioDiscovery/dynamicFactorRanking.txt", "scenarioDiscovery/exogenousHydro.txt"),
                       "dirname" = c("annualObjectives/annualValues.feather", "hydroStatistics/hydroStatistics.feather", "hCriteria/h1.feather", "hCriteria/h2.feather", "hCriteria/h3.feather", "hCriteria/h4.feather", "hCriteria/h6.feather", "hCriteria/h7.feather", "hCriteria/h14.feather", "impactZones/impactZoneExceedances.feather", "scenarioDiscovery/dynamicRobustness.feather", "scenarioDiscovery/dynamicNormalized.feather", "scenarioDiscovery/staticRobustness.feather", "scenarioDiscovery/staticNormalized.feather", "scenarioDiscovery/dynamicFactorRanking.feather", "scenarioDiscovery/exogenousHydro.feather"),
                       "polCol" = c(0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0))

# impact zone description and thresholds (m)
impactZonesContext <- read.csv("../postScripts/impactZones.csv", check.names = FALSE, stringsAsFactors = FALSE)

# app descriptive text - blank for now
# description <- read_file("description.txt")

# -----------------------------------------------------------------------------
# pi and variable setup
# -----------------------------------------------------------------------------

print("... setting pi names ...")

# names of objectives
pis <- c("Coastal Impacts: Upstream Buildings Impacted (#)", 
         "Coastal Impacts: Downstream Buildings Impacted (#)", 
         "Commercial Navigation: Ontario + Seaway + Montreal Transportation Costs ($)", 
         "Hydropower: Moses-Saunders + Niagara Energy Value ($)", 
         "Meadow Marsh: Area (ha)", 
         "Muskrat House Density (%)",
         "Recreational Boating: Impact Costs ($)")
piPlotNames <- c("Coastal Impacts (Upstream)", 
                 "Coastal Impacts (Downstream)", 
                 "Commercial Navigation", 
                 "Hydropower Production", 
                 "Wetland Health & Services", 
                 "Muskrat House Density", 
                 "Recreational Boating")
names(piPlotNames) <- pis
piAbbNames <- c("UC", "DC", "CN", "HP", "WH", "MD", "RB")
names(piAbbNames) <- pis

# pis to maximize
maxPIs <- c("Hydropower: Moses-Saunders + Niagara Energy Value ($)", "Meadow Marsh: Area (ha)", "Muskrat House Density (%)")

# pis to minimize
minPIs <- c("Coastal Impacts: Upstream Buildings Impacted (#)", "Coastal Impacts: Downstream Buildings Impacted (#)", "Commercial Navigation: Ontario + Seaway + Montreal Transportation Costs ($)", "Recreational Boating: Impact Costs ($)")

# pi levels
piLevels <- data.frame(check.names = FALSE, stringsAsFactors = FALSE,
                       "PI" = c("upstreamCoastal", "ontarioCoastal", "alexbayCoastal", "cardinalCoastal", "downstreamCoastal", "lerybeauharnoisCoastal", "ptclaireCoastal", "sorelCoastal", "lacstpierreCoastal", "maskinongeCoastal", "troisrivieresCoastal", "totalCommercialNavigation", "ontarioCommercialNavigation", "seawayCommercialNavigation", "montrealCommercialNavigation", "totalEnergyValue", "nypaMosesSaundersEnergyValue", "opgMosesSaundersEnergyValue", "peakingMosesSaundersValue", "nypaNiagaraEnergyValue", "opgNiagaraEnergyValue", "totalRecBoating", "ontarioRecBoating", "alexbayRecBoating", "brockvilleRecBoating", "ogdensburgRecBoating", "longsaultRecBoating", "ptclaireRecBoating", "varennesRecBoating", "sorelRecBoating", "mmArea", "mmLowSupply", "muskratHouseDensity"),
                       "PI Name" = c("Upstream Coastal Impacts", "Lake Ontario Coastal Impacts", "Alexandria Bay Coastal Impacts", "Cardinal Coastal Impacts", "Downstream Coastal Impacts", "Lery Beauharnois Coastal Impacts", "Pointe-Claire Coastal Impacts", "Sorel Coastal Impacts", "Lac St. Pierre Coastal Impacts", "Maskinonge Coastal Impacts", "Trois Rivieres Coastal Impacts", "Total Commercial Navigation", "Lake Ontario Commercial Navigation", "Seaway Commercial Navigation", "Montreal Commercial Navigation", "Total Energy Value", "NYPA @ Moses-Saunders Hydropower Energy Value", "OPG @ Moses-Saunders Hydropower Energy Value", "Moses-Saunders Hydropower Peaking Value", "NYPA @ Niagara Hydropower Energy Value", "OPG @ Niagara Hydropower Energy Value", "Total Recreational Boating", "Lake Ontario Recreational Boating", "Alexandria Bay Recreational Boating", "Brockville Recreational Boating", "Ogdensburg Recreational Boating", "Long Sault Recreational Boating", "Pointe-Claire Recreational Boating", "Varennes Recreational Boating", "Sorel Recreational Boating", "Meadow Marsh Acreage", "Meadow Marsh Low Supply Year", "Muskrat House Density"),
                       "PI Location" = c("Aggregate", "Lake Ontario", "Alexandria Bay", "Cardinal", "Aggregate", "Lery Beauharnois", "Pointe-Claire", "Sorel", "Lac St. Pierre", "Maskinonge", "Trois Rivieres", "Aggregate", "Lake Ontario", "Seaway", "Montreal", "Aggregate", "NYPA @ Moses-Saunders Energy Value", "OPG @ Moses-Saunders Energy Value", "Moses-Saunders Peaking Value", "NYPA @ Niagara Energy Value", "OPG @ Niagara Energy Value", "Aggregate", "Lake Ontario", "Alexandria Bay", "Brockville", "Ogdensburg", "Long Sault", "Pointe-Claire", "Varennes", "Sorel", "Meadow Marsh Acreage", "Meadow Marsh Low Supply Year", "Muskrat House Density"),
                       "PI Group" = c(rep("Coastal Impacts", 11), rep("Commercial Navigation", 4), rep("Hydropower", 6), rep("Recreational Boating", 9), rep("Wetland Health & Services", 3)),
                       "Individual Group" = c(rep("Upstream Coastal Impacts", 4), rep("Downstream Coastal Impacts", 7), rep("Commercial Navigation", 4), rep("Hydropower", 6), rep("Recreational Boating", 9), rep("Wetland Health & Services", 2), rep("Muskrat House Density", 1))) %>%
  mutate(`PI Name` = factor(`PI Name`, levels = c(unique(`PI Name`))),
         `PI Location` = factor(`PI Location`, levels = c(unique(`PI Location`))),# levels = c("Aggregate", "Lake Ontario", "Alexandria Bay", "Brockville", "Ogdensburg", "Cardinal", "Long Sault", "Lery Beauharnois", "Pointe-Claire", "Varennes", "Sorel", "Maskinonge", "Lac St. Pierre", "Trois Rivieres","Seaway", "Montreal", "NYPA @ Moses-Saunders Energy Value", "OPG @ Moses-Saunders Energy Value", "Moses-Saunders Peaking Value", "NYPA @ Niagara Energy Value", "OPG @ Niagara Energy Value", "Meadow Marsh Acreage", "Meadow Marsh Low Supply Year")),
         `PI Group` = factor(`PI Group`, levels = c(unique(`PI Group`))),# levels = c("Coastal Impacts", "Commercial Navigation", "Hydropower", "Recreational Boating", "Wetland Health & Services")),
         `Individual Group` = factor(`Individual Group`, levels = c(unique(`Individual Group`))))# factor(`Individual Group`, levels = c("Upstream Coastal Impacts", "Downstream Coastal Impacts", "Commercial Navigation", "Hydropower", "Recreational Boating", "Wetland Health & Services")))

# sets geographic order of variables from lake ontario down to batiscan
hydroLevels <- data.frame(
  "Variable" = c("ontLevel", "ontFlow", "stlouisFlow", "kingstonLevel", "alexbayLevel", "brockvilleLevel", "ogdensburgLevel", "cardinalLevel", "iroquoishwLevel", "iroquoistwLevel", "morrisburgLevel", "longsaultLevel", "saundershwLevel", "saunderstwLevel", "cornwallLevel", "summerstownLevel", "lerybeauharnoisLevel", "ptclaireLevel", "jetty1Level", "stlambertLevel", "varennesLevel", "sorelLevel", "lacstpierreLevel", "maskinongeLevel", "troisrivieresLevel", "batiscanLevel"), 
  "Name" = c("Lake Ontario Level", "Lake Ontario Flow", "Lac St. Louis Flow", "Kingston Level", "Alexandria Bay Level", "Brockville Level", "Ogdensburg Level", "Cardinal Level", "Iroquois Headwaters Level", "Iroquois Tailwaters Level", "Morrisburg Level", "Long Sault Level", "Saunders Headwaters Level", "Saunders Tailwaters Level", "Cornwall Level", "Summerstown Level", "Lery Beauharnois Level", "Pointe-Claire Level", "Jetty1 Level", "St. Lambert Level", "Varennes Level", "Sorel Level", "Lac St. Pierre Level", "Maskinonge Level", "Trois Rivieres Level", "Batiscan Level")) %>%
  mutate(Location = trimws(str_remove(Name, "Level|Flow")),
         Hydro = trimws(str_remove(Name, Location)),
         Hydro = ifelse(Hydro == "Level", "Level (m)", "Flow (cms)"),
         Units = paste(Location, Hydro),
         Location = factor(Location, levels = c("Lake Ontario", "Kingston", "Alexandria Bay", "Brockville", "Ogdensburg", "Cardinal", "Iroquois Headwaters", "Iroquois Tailwaters", "Morrisburg", "Long Sault", "Saunders Headwaters", "Saunders Tailwaters", "Cornwall", "Summerstown", "Lery Beauharnois", "Lac St. Louis", "Pointe-Claire", "Jetty1", "St. Lambert", "Varennes", "Sorel", "Lac St. Pierre", "Maskinonge", "Trois Rivieres", "Batiscan")))

# satisficing criteria agreed upon by glam and the board 
piFilter <- data.frame("Group" = c("Upstream Coastal Impacts", "Downstream Coastal Impacts", "Commercial Navigation", "Hydropower", "Wetland Health & Services", "Muskrat House Density", "Recreational Boating"),
                       "PI" = pis,
                       "lowerBounds" = c(0, 0, 0, -0.5, 0, 0, -10),
                       "roundDecimal" = c(0, 0, 2, 2, 0, 2, 0))

forecastLevels <- c("Plan 2014 Baseline", "12-month Perfect", "12-month Status Quo", "6-month Perfect", "6-month Status Quo", "3-month Perfect", "3-month Status Quo", "1-month Perfect", "1-month Status Quo") 

# -----------------------------------------------------------------------------
# pareto front data
# -----------------------------------------------------------------------------

print("... loading pareto front data ...")

# load in baseline objective performance
paretoBaseline <- read.csv("../data/baseline/NonDominatedPolicies.txt", sep = "\t", header = TRUE, check.names = FALSE, stringsAsFactors = FALSE) %>%
  dplyr::select(Experiment, `Lead-Time`, Skill, Policy, all_of(pis)) %>%
  mutate_at(vars(all_of(pis)), as.numeric)

# create levels for the baseline performance and optimized seeds
baselinePolicies <- paretoBaseline$Policy

# set lead-time and skill options
leadtimeOptions <- c("1-month", "3-month", "6-month", "12-month")
skillOptions <- unique(paretoBaseline$Skill)[!is.na(unique(paretoBaseline$Skill))]

# set up handles to database tables on app start
runInfo <- data.frame("fn" = grep("_", list.files("../data"), value = TRUE)) %>%
  mutate(lt = unlist(lapply(str_split(fn, "_"), "[[", 1)),
         lt_pretty = paste0(unlist(strsplit(lt, "month")), "-month"),
         sk = unlist(lapply(str_split(fn, "_"), "[[", 2)),
         sk_pretty = case_when(sk == "sqAR" ~ "Status Quo (AR)", sk == "sqLM" ~ "Status Quo (LM)", sk == "0" ~ "Perfect", TRUE ~ as.character(sk)), 
         Policy = paste(lt_pretty, sk_pretty))

# ADD FOR NOW TEMP
runInfo <- runInfo %>% filter(fn == "12month_sqAR_75000nfe_17dvs")

# load pareto front for each experiment
paretoByForecast <- list()

for (j in 1:nrow(runInfo)) {
  
  tmp <- data.table::fread(paste0("../data/", runInfo[j, "fn"], "/NonDominatedPolicies.txt")) %>%
    mutate(fn = runInfo[j, "fn"],
           Policy = paste0("Seed", Policy, "_Policy", ID)) %>%
    dplyr::select(fn, Experiment, `Lead-Time`, Skill, Policy, all_of(pis))
  
  paretoByForecast[[runInfo[j, "fn"]]] <- tmp
  
}

paretoByForecast <- bind_rows(paretoByForecast) %>%
  mutate(.before = 1, searchID = 1:nrow(.)) %>%
  mutate_at(vars(all_of(pis)), as.numeric)

# load overall pareto front across all experiments
paretoOverall <- data.table::fread("../data/NonDominatedPolicies.txt", sep = "\t", header = TRUE, check.names = FALSE) %>%
  mutate(Policy = paste0("Seed", Policy, "_Policy", ID)) %>%
  select(Experiment, `Lead-Time`, Skill, Policy, all_of(pis))

# match identifier of individual pareto fronts to overall pareto front
matchID <- paretoByForecast %>% 
  select(searchID, fn, Experiment, Policy)

paretoOverall <- paretoOverall %>%
  left_join(matchID, by = c("Experiment", "Policy")) %>%
  select(searchID, fn, everything()) %>%
  mutate_at(vars(all_of(pis)), as.numeric)

# -----------------------------------------------------------------------------
# post-processing results
# -----------------------------------------------------------------------------

print("... loading post-processing data ...")

st <- Sys.time()

for (i in 1:nrow(filelist)) {

  print(paste("... loading", filelist[i, "varname"]))
  tmp <- arrow::read_feather(paste0("data/", filelist[i, "dirname"]))
  assign(filelist[i, "varname"], tmp)
  
}

et <- Sys.time()
print(et - st)

# -----------------------------------------------------------------------------
# ui
# -----------------------------------------------------------------------------

print("starting ui")

totalwidth <- 12
sidebarWidth <- 3
mainbarWidth <- totalwidth - sidebarWidth

ui <- fluidPage(
  
  # get browser dimensions for plot scaling
  shinybrowser::detect(),
  
  # set theme for overall web app
  theme = shinythemes::shinytheme("yeti"),
  
  # create the main tabset
  navbarPage(
    
    # app title
    "Policy Analysis",
    
    # first tab in main tab set
    tabPanel(
      
      # first tab title
      "Exploration",
      
      sidebarPanel(
        
        # side panel parameters
        style = "height: 95vh; overflow-y: auto; background-color: #F5F5F5; border-radius: 8px; border-width: 0px", 
        width = sidebarWidth,
        
        # side panel visuals
        h4("Policy Infomation"),
        selectInput(inputId = "mode", label = "Analysis", choices = c("Forecast-Specific Pareto Front", "Pareto Front Across All Forecasts"), multiple = FALSE, selected = "Forecast-Specific Pareto Front"),
        conditionalPanel(
          "input.mode == 'Pareto Front Across All Forecasts'",
          selectInput(inputId = "basePol", label = "Policy for Normalization", multiple = FALSE, choices = baselinePolicies, selected = "Plan 2014 Baseline"),
        ),
        conditionalPanel(
          "input.mode == 'Forecast-Specific Pareto Front'",
          selectInput(inputId = "leadtime", label = "Forecast Lead-Time", choices = unique(runInfo$lt_pretty), multiple = FALSE, selected = "12-Month"),
          selectInput(inputId = "skill", label = "Forecast Skill", choices = unique(runInfo$sk_pretty), multiple = FALSE, selected = "Status Quo (LM)"),
          selectInput(inputId = "basePol", label = "Policy for Normalization", multiple = FALSE, choices = baselinePolicies, selected = "Plan 2014 Baseline"),
        ),
        br(),
        h4("Policy Filtering"),
        selectInput(inputId = "filterMethod", label = "Filtering Method", multiple = FALSE, choices = c("Satisficing Criteria", "Manual Filtering", "Improvements Across All PIs"), selected = "Satisficing Criteria"),
        conditionalPanel(
          "input.filterMethod == 'Satisficing Criteria'",
          numericRangeInput(inputId = "cuNumeric", label = h5("Coastal Impacts: Upstream Buildings Impacted (#)"), value = c(0, 100)),
          numericRangeInput(inputId = "cdNumeric", label = h5("Coastal Impacts: Downstream Buildings Impacted (#)"), value = c(0, 100)),
          numericRangeInput(inputId = "cnNumeric", label = h5("Commercial Navigation: Ontario + Seaway + Montreal Transportation Costs ($)"), value = c(0, 100)),
          numericRangeInput(inputId = "hpNumeric", label = h5("Hydropower: Moses-Saunders + Niagara Energy Value ($)"), value = c(-0.5, 100)),
          numericRangeInput(inputId = "mmNumeric", label = h5("Meadow Marsh: Area (ha)"), value = c(0, 100)),
          numericRangeInput(inputId = "mdNumeric", label = h5("Muskrat House Density (%)"), value = c(0, 100)),
          numericRangeInput(inputId = "rbNumeric", label = h5("Recreational Boating: Impact Costs ($)"), value = c(-10, 100))
        ),
        conditionalPanel(
          "input.filterMethod == 'Manual Filtering'",
          sliderInput(inputId = "cuSlider", label = "Coastal Impacts: Upstream Buildings Impacted (#)", min = -100, max = 100, value = c(-100, 100), step = 1, dragRange = TRUE),
          sliderInput("cdSlider", "Coastal Impacts: Downstream Buildings Impacted (#)", -100, 100, c(-100, 100), step = 1, dragRange = TRUE),
          sliderInput("cnSlider", "Commercial Navigation: Ontario + Seaway + Montreal Transportation Costs ($)", -100, 100, c(-100, 100), step = 0.1, dragRange = TRUE),
          sliderInput("hpSlider", "Hydropower: Moses-Saunders + Niagara Energy Value ($)", -100, 100, c(-100, 100), step = 0.1, dragRange = TRUE),
          sliderInput("mmSlider", "Meadow Marsh: Area (ha)", -100, 100, c(-100, 100), step = 1, dragRange = TRUE),
          sliderInput("mdSlider", "Muskrat House Density (%)", -100, 100, c(-100, 100), step = 1, dragRange = TRUE),
          sliderInput("rbSlider", "Recreational Boating: Impact Costs ($)", -100, 100, c(-100, 100), step = 1, dragRange = TRUE)
        )
        
      ),
      
      mainPanel(
        
        # main panel parameters
        width = mainbarWidth,
        
        # main panel visuals 
        fluidRow(
          column(12,
                 column(11,h3(textOutput("plotTitle"))),
                 column(1, dropdownButton(
                   br(),
                   # plot settings
                   selectInput(inputId = "plotPol", label = "Policies to Display", multiple = TRUE, choices = baselinePolicies, selected = c("Plan 2014 Baseline")), # selected = c("12-month Status Quo (AR)")),
                   selectInput(inputId = "labelUnits", label = "Plot Label Units", multiple = FALSE, choices = c("Percent Change from Baseline", "Original PI Units"), selected = "Original PI Units"),
                   selectInput(inputId = "filterTable", label = "Table Units", multiple = FALSE, choices = c("Percent Change from Baseline", "Original PI Units"), selected = "Percent Change from Baseline"),
                   br(),
                   # plot save settings
                   h5("Save Settings"),
                   textInput(inputId = "filterPlotName", label = "Name", value = "parallelAxisPlot"),
                   textInput(inputId = "filterPlotType", label = "Kind", value = "png"),
                   numericInput(inputId = "filterPlotWidth", label = "Width", value = 17*1.5),
                   numericInput(inputId = "filterPlotHeight", label = "Height", value = 11*1.5),
                   textInput(inputId = "filterPlotUnits", label = "Units", value = "in"),
                   numericInput(inputId = "filterPlotRes", label = "Resolution", value = 330),
                   downloadButton(outputId = "filterPlotDownload", label = "Save Plot"),
                   br(),
                   circle = TRUE, icon = icon("gear"), width = "300px", right = TRUE, margin = "20px",
                   tooltip = tooltipOptions(title = "Click to See Display Options", placement = "left")))
          )
          
        ),
        # plotOutput("filterPlot", brush = brushOpts(id = "plotBrush")),
        # plotOutput("filterPlot", height = "1200px", width = "1000px", brush = brushOpts(id = "plotBrush")),
        uiOutput("filterPlot"),
        br(),
        h4("Table of Pareto Optimal Policy Performance"),
        DT::dataTableOutput("filteredTable"),
        br(),
        
      )
      
    ),
    
    # second tab in main tab set
    tabPanel(
      
      # first tab title
      "Robustness Summary",
      
      sidebarPanel(
        # side panel parameters
        style = "overflow-y: auto; background-color: #F5F5F5; border-radius: 8px; border-width: 0px", 
        width = sidebarWidth,
      ),
      
      mainPanel(
        # main panel parameters
        width = mainbarWidth,
        # tabset in main panel
        tabsetPanel(
          # first panel in tabset
          tabPanel(
            "Summary Plot",
            br(),
            # main panel visuals 
            fluidRow(
              column(12,
                     column(11,h3("Candidate Policies Across Forecast Attribute and State-of-the-World")),
                     column(1, dropdownButton(
                       br(),
                       # plot save settings
                       h5("Save Settings"),
                       textInput(inputId = "summaryRobustName", label = "Name", value = "summaryRobustnessPlot"),
                       textInput(inputId = "summaryRobustType", label = "Kind", value = "png"),
                       numericInput(inputId = "summaryRobustWidth", label = "Width", value = 17),
                       numericInput(inputId = "summaryRobustHeight", label = "Height", value = 11),
                       textInput(inputId = "summaryRobustUnits", label = "Units", value = "in"),
                       numericInput(inputId = "summaryRobustRes", label = "Resolution", value = 330),
                       downloadButton(outputId = "summaryRobustDownload", label = "Save Plot"),
                       br(),
                       circle = TRUE, icon = icon("gear"), width = "300px", right = TRUE, margin = "20px",
                       tooltip = tooltipOptions(title = "Click to See Display Options", placement = "left")))
              )
            ),
            br(),
            plotOutput("summaryRobustPlot", height = 1000, width = 1000),
            br(),
          ),
          # first panel in tabset
          tabPanel(
            "Summary Table",
            br(),
            DT::dataTableOutput("summaryRobustTable"),
            br(),
          ),
        ),
      ),
    ),
    
    # second tab in main tab set
    tabPanel(
      
      # second tab title
      "Reevaluation",
      
      sidebarPanel(
        
        # side panel parameters
        style = "overflow-y: auto; background-color: #F5F5F5; border-radius: 8px; border-width: 0px", 
        width = sidebarWidth,
        
        # side panel visuals
        h4("Policy Infomation"),
        selectInput(inputId = "runData", label = "Reassessment Dataset", choices = c("All SOW Traces", "Historic", "Stochastic", "Climate Scenarios"), multiple = FALSE, selected = "All SOW Traces"),
        selectInput(inputId = "policySelection", label = "Policy Selection", choices = c("Select from Table", "Select by searchID"), multiple = FALSE, selected = "Select from Table"),
        conditionalPanel(
          "input.policySelection == 'Select by searchID'",
          searchInput(inputId = "evalPoliciesManual", label = "Enter policies by searchID (separated with a comma):", placeholder = NULL, btnSearch = icon("magnifying-glass"), width = "100%")
        ),
        conditionalPanel(
          "input.policySelection == 'Select from Table'",
          pickerInput(inputId = "evalPolicies", label = "Policies to Evaluate", choices = NULL, multiple = TRUE, options = list(`actions-box` = TRUE)))
        
      ),
      
      mainPanel(
        
        # main panel parameters
        width = mainbarWidth,
        
        # tabset in main panel
        tabsetPanel(
          
          # first panel in tabset
          tabPanel(
            "Robustness",
            br(),
            h4(textOutput("robustTitle")),
            br(),
            DT::dataTableOutput("robustnessTable") %>% withSpinner(color = blues[3], proxy.height = 200),
            br(),
            tabsetPanel(
              tabPanel("Robustness",
                       # main panel visuals 
                       br(),
                       fluidRow(
                         column(12,
                                column(11, h3("Robustness Across Selected Candidate Policies and States-of-the-World")),
                                column(1, dropdownButton(
                                  br(),
                                  selectInput(inputId = "robustDef", label = "Definition of Robustness", multiple = FALSE, choices = c("Static", "Dynamic"), selected = "Dynamic"),
                                  br(),
                                  # plot save settings
                                  h5("Save Settings"),
                                  textInput(inputId = "robustPlotName", label = "Name", value = "summaryRobustnessPlot"),
                                  textInput(inputId = "robustPlotType", label = "Kind", value = "png"),
                                  numericInput(inputId = "robustPlotWidth", label = "Width", value = (17 * 1.5)),
                                  numericInput(inputId = "robustPlotHeight", label = "Height", value = (11 * 1.5)),
                                  textInput(inputId = "robustPlotUnits", label = "Units", value = "in"),
                                  numericInput(inputId = "robustPlotRes", label = "Resolution", value = 330),
                                  downloadButton(outputId = "robustPlotDownload", label = "Save Plot"),
                                  br(),
                                  circle = TRUE, icon = icon("gear"), width = "300px", right = TRUE, margin = "20px",
                                  tooltip = tooltipOptions(title = "Click to See Display Options", placement = "left")))
                         )
                       ),
                       br(),
                       plotOutput("robustPlot", width = 1000, height = 1100) %>% withSpinner(color = blues[3], proxy.height = 200)
                  ),
              tabPanel("Factor Mapping",
                       # main panel visuals 
                       fluidRow(
                         column(12,
                                column(11, h3("Factor Maps")),
                                column(1, dropdownButton(
                                  br(),
                                  # display settings
                                  uiOutput("factorMapPlanSelector"),
                                  # selectInput(inputId = "factorMapPlanInput", label = "Plans to Display", multiple = TRUE, choices = "Plan 2014", selected = "Plan 2014"),
                                  selectInput(inputId = "factorMapPIInput", label = "PIs to Display", multiple = TRUE, choices = pis, selected = c()),
                                  # plot save settings
                                  h5("Save Settings"),
                                  textInput(inputId = "factorMapName", label = "Name", value = "factorMaps"),
                                  textInput(inputId = "factorMapType", label = "Kind", value = "png"),
                                  numericInput(inputId = "factorMapWidth", label = "Width", value = 17 * 3.5),
                                  numericInput(inputId = "factorMapHeight", label = "Height", value = 11 * 3.5),
                                  textInput(inputId = "factorMapUnits", label = "Units", value = "in"),
                                  numericInput(inputId = "factorMapRes", label = "Resolution", value = 330),
                                  downloadButton(outputId = "factorMapDownload", label = "Save Plot"),
                                  br(),
                                  circle = TRUE, icon = icon("gear"), width = "300px", right = TRUE, margin = "20px",
                                  tooltip = tooltipOptions(title = "Click to See Display Options", placement = "left")))
                         )
                       ),
                       br(),
                       plotOutput("factorMapPlot", width = 1000, height = 1200) %>% withSpinner(color = blues[3], proxy.height = 200),
              ),
              # tabPanel("Static Robustness",
              #          br(),
              #          plotOutput("staticRobustPlot", width = 1000, height = 1100) %>% withSpinner(color = blues[3], proxy.height = 200)
              # ),
            ),
            br(),
          ),
          
          tabPanel(
            "Spatial Disaggregation",
            br(),
            fluidRow(
              column(12,
                     column(11, h4("Performance Indicator by Interest/Use Group")),
                     column(1, 
                            dropdownButton(
                              br(),
                              selectInput(inputId = "boxplot", label = "Annual Statistic", choices = c("Net Annual Average", "Net Annual Minimum", "Net Annual Maximum", "Net Annual Total"), multiple = FALSE, selected = "Net Annual Average"),
                              selectInput(inputId = "mmboxplot", label = "Meadow Marsh Supply Type", choices = c("All Years", "Low Supply Years"), multiple = FALSE, selected = "All Years"),
                              # plot save settings
                              h5("Save Settings"),
                              textInput(inputId = "candidatePolicyName", label = "Name", value = "spatialDisaggregation"),
                              textInput(inputId = "candidatePolicyType", label = "Kind", value = "png"),
                              numericInput(inputId = "candidatePolicyWidth", label = "Width", value = (17 * 1.5)),
                              numericInput(inputId = "candidatePolicyHeight", label = "Height", value = (11 * 1.5)),
                              textInput(inputId = "candidatePolicyUnits", label = "Units", value = "in"),
                              numericInput(inputId = "candidatePolicyRes", label = "Resolution", value = 330),
                              downloadButton(outputId = "candidatePolicyDownload", label = "Save Plot"),
                              br(),
                              circle = TRUE, icon = icon("gear"), width = "300px", right = TRUE, margin = "20px",
                              tooltip = tooltipOptions(title = "Click to See Display Options", placement = "left")))
              )
            ),
            br(),
            plotOutput("candidatePolicyPlots", width = 1000, height = 2000) %>% withSpinner(color = blues[3], proxy.height = 200),
            br(),
            h4("Historic Performance"),
            DT::dataTableOutput("candidatePolicyTable") %>% withSpinner(color = blues[3], proxy.height = 200),
            br(),
            h4("Stochastic Performance"),
            DT::dataTableOutput("reevaluationTable") %>% withSpinner(color = blues[3], proxy.height = 200),
          ),
          
          # second panel in tabset
          tabPanel(
            "Impact Zones",
            br(),
            fluidRow(
              column(12,
                     column(11, h4("Frequency Spent in Each Impact Zone Category")),
                     column(1, 
                            dropdownButton(
                              br(),
                              # plot save settings
                              h5("Save Settings"),
                              textInput(inputId = "impactzoneName", label = "Name", value = "impactZones"),
                              textInput(inputId = "impactzoneType", label = "Kind", value = "png"),
                              numericInput(inputId = "impactzoneWidth", label = "Width", value = 17),
                              numericInput(inputId = "impactzoneHeight", label = "Height", value = 11),
                              textInput(inputId = "impactzoneUnits", label = "Units", value = "in"),
                              numericInput(inputId = "impactzoneRes", label = "Resolution", value = 330),
                              downloadButton(outputId = "impactzoneDownload", label = "Save Plot"),
                              br(),
                              circle = TRUE, icon = icon("gear"), width = "300px", right = TRUE, margin = "20px",
                              tooltip = tooltipOptions(title = "Click to See Display Options", placement = "left")))
              )
            ),
            br(),
            h4("Simulated Frequency in Each Impact Zone"),
            plotOutput("impactzonePlot", width = 1000, height = 2000) %>% withSpinner(color = blues[3], proxy.height = 200),
            br(),
            h4("Impact Zone Descriptions"),
            DT::dataTableOutput("impactZoneDescription") %>% withSpinner(color = blues[3], proxy.height = 200),
            br(),
            h4("Impact Zone Categories"),
            DT::dataTableOutput("impactZoneTable") %>% withSpinner(color = blues[3], proxy.height = 200),
          ),
          
          # third panel in tabset
          tabPanel(
            "H1-H7 Criteria",
            br(),
            reactableOutput("hTable") %>% withSpinner(color = blues[3], proxy.height = 200),
            # DT::dataTableOutput("hTable") %>% withSpinner(color = blues[3], proxy.height = 200),
            br(),
            downloadButton(outputId = "hTableDownload", label = "Save Table"),
            br(),
            br(),
            tabsetPanel(
              tabPanel("H1",
                       br(),
                       h5("The regulated outflow from Lake Ontario shall be such as not to increase the frequency of low levels or reduce the minimum level of Montreal Harbour below those which would have occurred with the supplies of the past as adjusted."),
                       # DT::dataTableOutput("h1Table") %>% withSpinner(color = blues[3], proxy.height = 200),
                       reactableOutput("h1Table") %>% withSpinner(color = blues[3], proxy.height = 200),
                       br(),
                       downloadButton(outputId = "h1TableDownload", label = "Save Table"),
                       br(),
              ),
              tabPanel("H2",
                       br(),
                       h5("The regulated outflow from Lake Ontario shall be such as not to increase the frequency of low levels or reduce the minimum level of Lake St. Louis below those listed in the table below which would have occurred with the supplies of the past as adjusted."),
                       # DT::dataTableOutput("h2Table") %>% withSpinner(color = blues[3], proxy.height = 200),
                       reactableOutput("h2Table") %>% withSpinner(color = blues[3], proxy.height = 200),
                       br(),
                       downloadButton(outputId = "h2TableDownload", label = "Save Table"),
                       br(),
              ),
              tabPanel("H3",
                       br(),
                       h5("The regulated outflow from Lake Ontario shall be such that the frequencies of occurrence of high water levels on Lake St. Louis as measured at the Pointe Claire gauge are not greater than those listed below with supplies of the past as adjusted."),
                       # DT::dataTableOutput("h3Table") %>% withSpinner(color = blues[3], proxy.height = 200),
                       reactableOutput("h3Table") %>% withSpinner(color = blues[3], proxy.height = 200),
                       br(),
                       downloadButton(outputId = "h3TableDownload", label = "Save Table"),
                       br(),
              ),
              tabPanel("H4",
                       br(),
                       h5("The regulated monthly mean level of Lake Ontario shall not exceed elevations (IGLD85) in the corresponding months with the supplies of the past as adjusted."),
                       # DT::dataTableOutput("h4Table") %>% withSpinner(color = blues[3], proxy.height = 200),
                       reactableOutput("h4Table") %>% withSpinner(color = blues[3], proxy.height = 200),
                       br(),
                       downloadButton(outputId = "h4TableDownload", label = "Save Table"),
                       br(),
              ),
              tabPanel("H6",
                       br(),
                       h5("Under regulation, the frequency of occurrences of monthly mean elevations of approximately 75.07 meters (m), 246.3 feet (ft) IGLD 1985 and higher on Lake Ontario shall not be greater than would have occurred with supplies of the past as adjusted and with pre-project conditions."),
                       # DT::dataTableOutput("h6Table") %>% withSpinner(color = blues[3], proxy.height = 200),
                       reactableOutput("h6Table") %>% withSpinner(color = blues[3], proxy.height = 200),
                       br(),
                       downloadButton(outputId = "h6TableDownload", label = "Save Table"),
                       br(),
              ),
              tabPanel("H7",
                       br(),
                       h5("The regulated monthly mean water levels of Lake Ontario, with supplies of the past as adjusted shall not be less than the following elevations (IGLD 1985) in the corresponding months."),
                       # DT::dataTableOutput("h7Table") %>% withSpinner(color = blues[3], proxy.height = 200),
                       reactableOutput("h7Table") %>% withSpinner(color = blues[3], proxy.height = 200),
                       br(),
                       downloadButton(outputId = "h7TableDownload", label = "Save Table"),
                       br(),
              ),
            ),
            br(),
          ),
          
          # third panel in tabset
          tabPanel(
            "H14 Criteria",
            br(),
            fluidRow(
              column(12,
                     column(11, h4("Quarter-Months Exceeding H14 Criteria Water Levels")),
                     column(1, 
                            dropdownButton(
                              br(),
                              # plot save settings
                              h5("Save Settings"),
                              textInput(inputId = "h14PlotName", label = "Name", value = "h14"),
                              textInput(inputId = "h14PlotType", label = "Kind", value = "png"),
                              numericInput(inputId = "h14PlotWidth", label = "Width", value = 17),
                              numericInput(inputId = "h14PlotHeight", label = "Height", value = 11),
                              textInput(inputId = "h14PlotUnits", label = "Units", value = "in"),
                              numericInput(inputId = "h14PlotRes", label = "Resolution", value = 330),
                              downloadButton(outputId = "h14PlotDownload", label = "Save Plot"),
                              br(),
                              circle = TRUE, icon = icon("gear"), width = "300px", right = TRUE, margin = "20px",
                              tooltip = tooltipOptions(title = "Click to See Display Options", placement = "left")))
              )
            ),
            br(),
            h5("In the event that Lake Ontario water levels reach or exceed high levels, the works in the International Rapids Section shall be operated to provide all possible relief to the riparian owners upstream and downstream. In the event that Lake Ontario levels reach or fall below low levels the works in the International Rapids Section shall be operated to provide all possible relief to municipal water intakes, navigation and power purposes, upstream and downstream. The high and low water levels at which this criterion applies, and any revisions to these levels, shall be subject to the concurrence of Canada and the United States and shall be set out in a Commission directive to the Board. "),
            plotOutput("h14Plot", width = 1000, height = 1000) %>% withSpinner(color = blues[3], proxy.height = 200),
            br(),
          ),
          
          # fourth panel in tabset
          tabPanel(
            "Water Level Statistics",
            br(),
            fluidRow(
              column(12,
                     column(11, h4("Water Level Statistics by Month and Location")),
                     column(1, 
                            dropdownButton(
                              br(),
                              selectInput(inputId = "summaryStatistic", label = "Select Summary Statistic", choices = c("Monthly Mean", "Monthly Maximum", "Monthly Minimum"), multiple = FALSE, selected = "Mean"), # choices = c("Minimum", "Mean", "Median", "Maximum", "Variance"), multiple = FALSE, selected = "Mean"),
                              # plot save settings
                              h5("Save Settings"),
                              textInput(inputId = "waterLevelStatsPlotName", label = "Name", value = "waterLevelStats"),
                              textInput(inputId = "waterLevelStatsPlotType", label = "Kind", value = "png"),
                              numericInput(inputId = "waterLevelStatsPlotWidth", label = "Width", value = 17),
                              numericInput(inputId = "waterLevelStatsPlotHeight", label = "Height", value = 11),
                              textInput(inputId = "waterLevelStatsPlotUnits", label = "Units", value = "in"),
                              numericInput(inputId = "waterLevelStatsPlotRes", label = "Resolution", value = 330),
                              downloadButton(outputId = "waterLevelStatsPlotDownload", label = "Save Plot"),
                              br(),
                              circle = TRUE, icon = icon("gear"), width = "300px", right = TRUE, margin = "20px",
                              tooltip = tooltipOptions(title = "Click to See Display Options", placement = "left")))
              )
            ),
            br(),
            plotOutput("waterLevelStatsPlot", width = 1000, height = 1000) %>% withSpinner(color = blues[3], proxy.height = 200),
            br(),
          ),
          
          # fifth panel in tabset
          tabPanel(
            "Time Series",
            br(),
            fluidRow(
              column(12,
                     column(11, h4("Time Series by Year and Location")),
                     column(1, 
                            dropdownButton(
                              br(),
                              # selectInput(inputId = "summaryStatistic", label = "Select Summary Statistic", choices = c("Monthly Mean", "Monthly Maximum", "Monthly Minimum"), multiple = FALSE, selected = "Mean"), # choices = c("Minimum", "Mean", "Median", "Maximum", "Variance"), multiple = FALSE, selected = "Mean"),
                              selectInput(inputId = "tsDataInput", label = "Select Hydrologic Traces", multiple = TRUE, choices = c("Historic"), selected = c("Historic")),
                              selectInput(inputId = "tsVarInput", label = "Select Hydrologic Variables", multiple = TRUE, choices = c("ontFlow", "ontLevel", "ptclaireLevel"), selected = c("ontFlow", "ontLevel", "ptclaireLevel")),
                              # plot save settings
                              h5("Save Settings"),
                              textInput(inputId = "timeSeriesPlotName", label = "Name", value = "waterLevelStats"),
                              textInput(inputId = "timeSeriesPlotType", label = "Kind", value = "png"),
                              numericInput(inputId = "timeSeriesPlotWidth", label = "Width", value = 17),
                              numericInput(inputId = "timeSeriesPlotHeight", label = "Height", value = 11),
                              textInput(inputId = "timeSeriesPlotUnits", label = "Units", value = "in"),
                              numericInput(inputId = "timeSeriesPlotRes", label = "Resolution", value = 330),
                              downloadButton(outputId = "timeSeriesPlotDownload", label = "Save Plot"),
                              br(),
                              circle = TRUE, icon = icon("gear"), width = "300px", right = TRUE, margin = "20px",
                              tooltip = tooltipOptions(title = "Click to See Display Options", placement = "left")))
              )
            ),
            br(),
            plotOutput("timeSeriesPlot", width = 1000, height = 1000) %>% withSpinner(color = blues[3], proxy.height = 200),
            br(),
          )
          
        )
        
      )
      
    ),
    
  )
  
)

print("done ui")

# -----------------------------------------------------------------------------
# server
# -----------------------------------------------------------------------------

print("starting server")

server <- function(input, output, session) {

  mode <- reactive({input$mode})
  
  # forecast leadtime and skill for input data selection
  leadtime <- reactive({
    input$leadtime
  })
  
  # forecast leadtime and skill for input data selection
  skill <- reactive({
    input$skill
  })
  
  # update forecast skill options based on lead-times
  observeEvent(leadtime(), {
    
    new_skills <- runInfo %>% 
      filter(lt_pretty == leadtime()) %>%
      arrange(factor(Policy, levels = baselinePolicies)) %>%
      select(sk_pretty) %>%
      unique() %>%
      deframe()
    
    updateSelectInput(session, "skill", choices = new_skills, selected = last(new_skills))

  })
  
  # policies for normalization and plotting
  basePol <- reactive({input$basePol})
  plotPol <- reactive({input$plotPol})
  
  fm <- reactive({input$filterMethod})
  
  cuUpper <- reactive({
    if (fm() == "Improvements Across All PIs") return(input$cuNumeric[2])
    if (fm() == "Satisficing Criteria") return(input$cuNumeric[2])
    if (fm() == "Manual Filtering") return(input$cuSlider[2])
  })
  
  cuLower <- reactive({
    if (fm() == "Improvements Across All PIs") return(0)
    if (fm() == "Satisficing Criteria") return(input$cuNumeric[1])
    if (fm() == "Manual Filtering") return(input$cuSlider[1])
  })
  
  cdUpper <- reactive({
    if (fm() == "Improvements Across All PIs") return(input$cdNumeric[2])
    if (fm() == "Satisficing Criteria") return(input$cdNumeric[2])
    if (fm() == "Manual Filtering") return(input$cdSlider[2])
  })
  
  cdLower <- reactive({
    if (fm() == "Improvements Across All PIs") return(0)
    if (fm() == "Satisficing Criteria") return(input$cdNumeric[1])
    if (fm() == "Manual Filtering") return(input$cdSlider[1])
  })
  
  cnUpper <- reactive({
    if (fm() == "Improvements Across All PIs") return(input$cnNumeric[2])
    if (fm() == "Satisficing Criteria") return(input$cnNumeric[2])
    if (fm() == "Manual Filtering") return(input$cnSlider[2])
  })
  
  cnLower <- reactive({
    if (fm() == "Improvements Across All PIs") return(0)
    if (fm() == "Satisficing Criteria") return(input$cnNumeric[1])
    if (fm() == "Manual Filtering") return(input$cnSlider[1])
  })
  
  hpUpper <- reactive({
    if (fm() == "Improvements Across All PIs") return(input$hpNumeric[2])
    if (fm() == "Satisficing Criteria") return(input$hpNumeric[2])
    if (fm() == "Manual Filtering") return(input$hpSlider[2])
  })
  
  hpLower <- reactive({
    if (fm() == "Improvements Across All PIs") return(0)
    if (fm() == "Satisficing Criteria") return(input$hpNumeric[1])
    if (fm() == "Manual Filtering") return(input$hpSlider[1])
  })
  
  mmUpper <- reactive({
    if (fm() == "Improvements Across All PIs") return(input$mmNumeric[2])
    if (fm() == "Satisficing Criteria") return(input$mmNumeric[2])
    if (fm() == "Manual Filtering") return(input$mmSlider[2])
  })
  
  mmLower <- reactive({
    if (fm() == "Improvements Across All PIs") return(0)
    if (fm() == "Satisficing Criteria") return(input$mmNumeric[1])
    if (fm() == "Manual Filtering") return(input$mmSlider[1])
  })
  
  mdUpper <- reactive({
    if (fm() == "Improvements Across All PIs") return(input$mdNumeric[2])
    if (fm() == "Satisficing Criteria") return(input$mdNumeric[2])
    if (fm() == "Manual Filtering") return(input$mdSlider[2])
  })
  
  mdLower <- reactive({
    if (fm() == "Improvements Across All PIs") return(0)
    if (fm() == "Satisficing Criteria") return(input$mdNumeric[1])
    if (fm() == "Manual Filtering") return(input$mdSlider[1])
  })
  
  rbUpper <- reactive({
    if (fm() == "Improvements Across All PIs") return(input$rbNumeric[2])
    if (fm() == "Satisficing Criteria") return(input$rbNumeric[2])
    if (fm() == "Manual Filtering") return(input$rbSlider[2])
  })
  
  rbLower <- reactive({
    if (fm() == "Improvements Across All PIs") return(0)
    if (fm() == "Satisficing Criteria") return(input$rbNumeric[1])
    if (fm() == "Manual Filtering") return(input$rbSlider[1])
  })
  
  # update sliding tickers
  observe({
    
    pols <- normalizedParetoFront()
    
    if (fm() == 'Satisficing Criteria') {
      maxValue <- max(pols$`Coastal Impacts: Upstream Buildings Impacted (#)`)
      updateNumericRangeInput(session, "cuNumeric", value = c(0, maxValue))
      maxValue <- max(pols$`Coastal Impacts: Downstream Buildings Impacted (#)`)
      updateNumericRangeInput(session, "cdNumeric", value = c(0, maxValue))
      maxValue <- max(pols$`Commercial Navigation: Ontario + Seaway + Montreal Transportation Costs ($)`)
      updateNumericRangeInput(session, "cnNumeric", value = c(0, maxValue))
      maxValue <- max(pols$`Hydropower: Moses-Saunders + Niagara Energy Value ($)`)
      updateNumericRangeInput(session, "hpNumeric", value = c(-0.5, maxValue))
      maxValue <- max(pols$`Meadow Marsh: Area (ha)`)
      updateNumericRangeInput(session, "mmNumeric", value = c(0, maxValue))
      maxValue <- max(pols$`Muskrat House Density (%)`)
      updateNumericRangeInput(session, "mdNumeric", value = c(0, maxValue))
      maxValue <- max(pols$`Recreational Boating: Impact Costs ($)`)
      updateNumericRangeInput(session, "rbNumeric", value = c(-10, maxValue))
    } 
    
    if (fm() == 'Manual Filtering') {
      minSlider <- floor(min(pols$`Coastal Impacts: Upstream Buildings Impacted (#)`)/10) * 10
      maxSlider <- ceiling(max(pols$`Coastal Impacts: Upstream Buildings Impacted (#)`)/10) * 10
      valueSlider <- c(minSlider, maxSlider)
      updateSliderInput(session, "cuSlider", min = minSlider, max = maxSlider, value = valueSlider)
      minSlider <- floor(min(pols$`Coastal Impacts: Downstream Buildings Impacted (#)`)/10) * 10
      maxSlider <- ceiling(max(pols$`Coastal Impacts: Downstream Buildings Impacted (#)`)/10) * 10
      valueSlider <- c(minSlider, maxSlider)
      updateSliderInput(session, "cdSlider", min = minSlider, max = maxSlider, value = valueSlider)
      minSlider <- floor(min(pols$`Commercial Navigation: Ontario + Seaway + Montreal Transportation Costs ($)`)/10) * 10
      maxSlider <- ceiling(max(pols$`Commercial Navigation: Ontario + Seaway + Montreal Transportation Costs ($)`)/10) * 10
      valueSlider <- c(minSlider, maxSlider)
      updateSliderInput(session, "cnSlider", min = minSlider, max = maxSlider, value = valueSlider)
      minSlider <- floor(min(pols$`Hydropower: Moses-Saunders + Niagara Energy Value ($)`)/10) * 10
      maxSlider <- ceiling(max(pols$`Hydropower: Moses-Saunders + Niagara Energy Value ($)`)/10) * 10
      valueSlider <- c(minSlider, maxSlider)
      updateSliderInput(session, "hpSlider", min = minSlider, max = maxSlider, value = valueSlider)
      minSlider <- floor(min(pols$`Meadow Marsh: Area (ha)`)/10) * 10
      maxSlider <- ceiling(max(pols$`Meadow Marsh: Area (ha)`)/10) * 10
      valueSlider <- c(minSlider, maxSlider)
      updateSliderInput(session, "mdSlider", min = minSlider, max = maxSlider, value = valueSlider)
      minSlider <- floor(min(pols$`Muskrat House Density (%)`)/10) * 10
      maxSlider <- ceiling(max(pols$`Muskrat House Density (%)`)/10) * 10
      valueSlider <- c(minSlider, maxSlider)
      updateSliderInput(session, "mdSlider", min = minSlider, max = maxSlider, value = valueSlider)
      minSlider <- floor(min(pols$`Recreational Boating: Impact Costs ($)`)/10) * 10
      maxSlider <- ceiling(max(pols$`Recreational Boating: Impact Costs ($)`)/10) * 10
      valueSlider <- c(minSlider, maxSlider)
      updateSliderInput(session, "rbSlider", min = minSlider, max = maxSlider, value = valueSlider)
    }    
    
  })
  
  # switch dataset based on input
  dataInput <- reactive({
    
    if (mode() == "Pareto Front Across All Forecasts") {
      
      data <- paretoOverall
      
    } else if (mode() == "Forecast-Specific Pareto Front") {
      
      data <- paretoByForecast %>%
        filter(`Lead-Time` == leadtime() & Skill == skill())
      
    } 
    
    data
    
  })
  
  # get all policies
  levelColumn <- reactive({
    
    if (mode() == "Pareto Front Across All Forecasts") return("Experiment")
    if (mode() == "Forecast-Specific Pareto Front") return("Policy")
    
  })
  
  baselineColumn <- reactive({
    
    if (mode() == "Pareto Front Across All Forecasts") return("Policy")
    if (mode() == "Forecast-Specific Pareto Front") return("Policy")
    
  })
  
  # get all policies/experiments for factor levels
  plottingLevels <- reactive({
    
    basePol <- basePol()
    plotPol <- plotPol()
    data <- dataInput()
    levelColumn <- levelColumn()
    
    levs <- data %>%
      select(all_of(levelColumn)) %>%
      unique() %>%
      deframe()
    
    if (mode() == "Pareto Front Across All Forecasts") {
      
      baseLevs <- "Plan 2014 Baseline"
      
    } else if (mode() == "Forecast-Specific Pareto Front") {
      
      baseLevs <- c(basePol, plotPol[- which(plotPol == basePol)])
      
    }
    
    c(baseLevs, levs)
    
  })
  
  # join pareto front with baseline policies
  paretoFront <- reactive({    
    
    plotPol <- plotPol()
    basePol <- basePol()
    plottingLevels <- plottingLevels()
    data <- dataInput()
    levelColumn <- levelColumn()
    
    # only keep baseline policies that match checkboxes from ui
    bline <- paretoBaseline %>%
      mutate(.before = 1, searchID = (max(data$searchID) + 1):(max(data$searchID) + nrow(.))) %>%
      filter(Policy %in% plotPol)
    
    # find baseline policy of interest and move it to the last row for normalization
    baseInd <- which(as.character(bline$Experiment) == basePol)
    bline <- rbind(bline %>% slice(- baseInd), bline %>% slice(baseInd))
    
    data <- data %>%
      select(-fn) %>%
      bind_rows(bline) %>%
      mutate(across(as.name(levelColumn), ~ factor(., levels = plottingLevels)))
    
    data 
    
  })
  
  # normalize values from policies around baseline policy
  normalizedParetoFront <- reactive({
    
    data <- paretoFront()
    
    # calculate % change from baseline policy of interest and filter by dynamic panel
    data <- data %>%
      mutate(across(all_of(maxPIs), ~ (.x - last(.x)) / last(.x) * 100),
             across(all_of(minPIs), ~ (.x - last(.x)) / last(.x) * -100),
             across(all_of(pis), ~ round(.x, 2)))
    
    data
    
  })
  
  # policies based on input from ui (manual filtering or brushing/clicking)
  selectedPolicies <- reactive({
    
    plotPol <- plotPol()
    data <- normalizedParetoFront()
    baselineColumn <- baselineColumn()
    
    if (!is.null(input$plotBrush)) {
      
      minmax <- data %>%
        pivot_longer(cols = all_of(pis), names_to = "PI", values_to = "Score") %>%
        group_by(PI) %>%
        mutate(Score = (Score - min(Score)) / (max(Score) - min(Score))) %>%
        ungroup(PI) %>%
        mutate(Skill = case_when(str_detect(Skill, "Status Quo") ~ "Status Quo", TRUE ~ as.character(Skill)))
      
      tmp <- brushedPoints(minmax, input$plotBrush, allRows = FALSE) %>%
        select(searchID)
      
      data <- data %>% 
        mutate(.before = 1, 
               Scenario = case_when(
                 .data[[baselineColumn]] %in% plotPol ~ paste(.data[[baselineColumn]]),
                 searchID %in% unique(tmp$searchID) ~ "Brushed Policy", 
                 TRUE ~ "Set"),
               Scenario = factor(Scenario, levels = c(plotPol, "Brushed Policy", "Set"))) %>%
        arrange(Scenario)
      
    } else {
      
      cuUpper <- cuUpper()
      cuLower <- cuLower()
      cdUpper <- cdUpper()
      cdLower <- cdLower()
      cnUpper <- cnUpper()
      cnLower <- cnLower()
      hpUpper <- hpUpper()
      hpLower <- hpLower()
      mmUpper <- mmUpper()
      mmLower <- mmLower()
      rbUpper <- rbUpper()
      rbLower <- rbLower()
      
      data <- data %>%
        mutate(.before = 1, Scenario = case_when(
          .data[[baselineColumn]] %in% plotPol ~ paste(.data[[baselineColumn]]),
          (`Coastal Impacts: Upstream Buildings Impacted (#)` >= cuLower
           & `Coastal Impacts: Upstream Buildings Impacted (#)` <= cuUpper
           & `Coastal Impacts: Downstream Buildings Impacted (#)` >= cdLower
           & `Coastal Impacts: Downstream Buildings Impacted (#)` <= cdUpper
           & `Commercial Navigation: Ontario + Seaway + Montreal Transportation Costs ($)` >= cnLower
           & `Commercial Navigation: Ontario + Seaway + Montreal Transportation Costs ($)` <= cnUpper
           & `Hydropower: Moses-Saunders + Niagara Energy Value ($)` >= hpLower
           & `Hydropower: Moses-Saunders + Niagara Energy Value ($)` <= hpUpper
           & `Meadow Marsh: Area (ha)` >= mmLower
           & `Meadow Marsh: Area (ha)` <= mmUpper
           & `Recreational Boating: Impact Costs ($)` >= rbLower
           & `Recreational Boating: Impact Costs ($)` <= rbUpper
           ) ~ "Policy Improvement",
          TRUE ~ "Set")) %>%
        mutate(Scenario = factor(Scenario, levels = c(plotPol, "Policy Improvement", "Set"))) %>%
        arrange(Scenario)
      
      # data <- data %>%
      #   mutate(.before = 1, Scenario = case_when(
      #     .data[[baselineColumn]] %in% plotPol ~ paste(.data[[baselineColumn]]),
      #     (`Coastal Impacts: Upstream Buildings Impacted (#)` >= 0
      #      & `Coastal Impacts: Downstream Buildings Impacted (#)` >= 0
      #      & `Commercial Navigation: Ontario + Seaway + Montreal Transportation Costs ($)` >= 0
      #      & `Hydropower: Moses-Saunders + Niagara Energy Value ($)` >= -0.5
      #      & `Meadow Marsh: Area (ha)` >= -5
      #      & `Recreational Boating: Impact Costs ($)` >= -20
      #     ) ~ "Policy Improvement",
      #     TRUE ~ "Set")) %>%
      #   mutate(Scenario = factor(Scenario, levels = c(plotPol, "Policy Improvement", "Set"))) %>%
      #   arrange(Scenario)

    }
    
    data
    
  })
  
  # plot labels 
  plotLabels <- reactive({
    
    if (input$labelUnits == "Original PI Units") {
      
      data <- paretoFront() %>%
        mutate(across(all_of(pis), ~ (last(.x) - .x)), across(all_of(pis), ~ round(.x, 2)))
      
    } else if (input$labelUnits == "Percent Change from Baseline") { 
      
      data <- normalizedParetoFront() %>%
        mutate(across(all_of(pis), ~ round(.x, 2)))
      
    }
    
    if (mode() == "Pareto Front Across All Forecasts") {
      
      lbl <- data %>%
        pivot_longer(cols = - c(searchID, Experiment, `Lead-Time`, Skill, Policy), names_to = "PI", values_to = "Value") %>%
        mutate(Skill = case_when(str_detect(Skill, "Status Quo") ~ "Status Quo",
                                 str_detect(Skill, "Perfect") ~ "Perfect",
                                 TRUE ~ as.character(Skill))) %>%
        group_by(PI, Skill) %>%
        summarise(Min = min(Value), Max = max(Value)) %>%
        pivot_longer(cols = - c(Skill, PI), names_to = "Range", values_to = "Value")
      
    } else if (mode() == "Forecast-Specific Pareto Front") {
      
      lbl <- data %>%
        pivot_longer(cols = - c(searchID, Experiment, `Lead-Time`, Skill, Policy), names_to = "PI", values_to = "Value") %>%
        group_by(PI) %>%
        summarise(Min = min(Value), Max = max(Value)) %>%
        pivot_longer(cols = - PI, names_to = "Range", values_to = "Value")
      
    }
    
    if (input$labelUnits == "Original PI Units") { 
      
      lbl <- lbl %>%
        mutate(Y = ifelse(Range == "Min", -0.05, 1.05),
               Value = formatC(abs(Value), format = "d", big.mark = ","),
               Value = ifelse(Range == "Min", paste("-", Value), paste("+", Value)))
      
    } else if (input$labelUnits == "Percent Change from Baseline") { 
      
      lbl <- lbl %>%
        mutate(Y = ifelse(Range == "Min", -0.05, 1.05),
               Value = ifelse(abs(Value) >= 1, round(Value, 0), Value),
               Value = ifelse(Range == "Min", paste("-", abs(Value), "%"), paste("+", abs(Value), "%")))
    }
    
    lbl
    
  })
  
  # plot title
  output$plotTitle <- renderText(({
    
    if (mode() == "Pareto Front Across All Forecasts") {
      
      paste("Pareto Front Across All Forecast Lead-Times and Skills")
      
    } else if (mode() == "Forecast-Specific Pareto Front") {
      
      paste("Improvement over Plan 2014 with a", leadtime(), skill(), "Forecast")
      
    }
    
  }))
  
  # use selected tables from table on previous tab as which stochastic runs to load
  tableSelection <- reactive({
    
    if (is.null(input$filteredTable_rows_selected)) return(NULL)
    
    data <- selectedPolicies() %>% 
      arrange(Scenario, Experiment, `Lead-Time`, Skill, Policy, searchID) %>%
      slice(as.numeric(input$filteredTable_rows_selected)) %>%
      select(searchID) %>%
      deframe()
    
  })
  
  # plot that corresponds to sidebar filters
  filterPlot <- reactive({
    
    plotPol <- plotPol()
    plotLabels <- plotLabels()
    data <- selectedPolicies()
    tableSelection <- tableSelection()
    
    if (is.null(tableSelection)) {
      
      if (mode() == "Forecast-Specific Pareto Front") {
        
        # color palette for plotting
        bluePal <- getBluePal(1)
        redPal <- getRedPal(length(plotPol))
        cols <- c(redPal, bluePal, "gray")
        
        if (!is.null(input$plotBrush)) {
          
          scenarioLevels <- c(plotPol, "Brushed Policy", "Set")
          names(cols) <- scenarioLevels
          
        } else {
          
          scenarioLevels <- c(plotPol, "Policy Improvement", "Set")
          names(cols) <- c(plotPol, "Policy Improvement", "Set")
          
        }
        
        minmax <- data %>%
          pivot_longer(cols = all_of(pis), names_to = "PI", values_to = "Score") %>%
          group_by(PI) %>%
          mutate(Score = (Score - min(Score)) / (max(Score) - min(Score))) %>%
          ungroup(PI) %>%
          mutate(PI = factor(PI, levels = pis),
                 Scenario = factor(Scenario, levels = scenarioLevels))
        
        plt <- ggplot(data = minmax, aes(x = PI, y = Score, group = searchID, color = Scenario)) +
          geom_point(alpha = 0.5) +
          geom_path(size = 1, alpha = 0.25, data = ~subset(., Scenario == "Set")) +
          geom_path(size = 2, alpha = 0.75, data = ~subset(., (Scenario != "Set" & !(Scenario %in% plotPol)))) +
          geom_path(size = 2, data = ~subset(., Scenario %in% plotPol)) +
          geom_label(data = plotLabels, aes(x = as.factor(PI), y = Y, label = Value), inherit.aes = FALSE, family = "Arial", size = 5) +
          theme_bw() +
          scale_color_manual(values = cols, limits = names(cols)) +
          scale_y_continuous(position = "right") +
          ylab("Min-Max Normalized Performance\n(Darkest Red Line = Baseline)\n") +
          theme(text = element_text(family = "Arial", color = "black", size = 18),
                title = element_blank(),
                axis.title.x = element_blank(),
                axis.text.x = element_text(size = 16),
                axis.title.y = element_text(size = 18),
                legend.title = element_blank(),
                legend.position = "top",
                legend.text = element_text(size = 15),
                legend.box = "vertical",
                legend.margin = ggplot2::margin())  +
          scale_x_discrete(labels = function(x) str_wrap(str_replace_all(x, "pf" , " "), width = 15))
        
      } else if (mode() == "Pareto Front Across All Forecasts") {
        
        forecastPareto <- data %>%
          pivot_longer(cols = all_of(pis), names_to = "PI", values_to = "Score") %>%
          group_by(PI) %>%
          mutate(Score = (Score - min(Score)) / (max(Score) - min(Score))) %>%
          ungroup(PI) %>%
          mutate(PI = factor(PI, levels = pis),
                 `Lead-Time` = factor(`Lead-Time`, rev(leadtimeOptions)),
                 Skill = case_when(str_detect(Skill, "Status Quo") ~ "Status Quo", TRUE ~ as.character(Skill)),
                 plotSK = case_when(Scenario == "Plan 2014 Baseline" ~ "Plan 2014 Baseline", Scenario == "Set" ~ "Set", TRUE ~ as.character(Skill)),
                 plotSK = factor(plotSK, levels = c("Plan 2014 Baseline", "Status Quo", "Perfect", "Set"))) %>%
          arrange(desc(plotSK))
        
        # color palette for plotting
        cols <- c(reds[1], blues[5], blues[1], "gray")
        names(cols) <- c("Plan 2014 Baseline", "Status Quo", "Perfect", "Set")
        
        # linetypes for plotting
        lts <- c("solid", "twodash", "dashed", "solid")
        names(lts) <- c("Plan 2014 Baseline", "Status Quo", "Perfect", "Set")
        
        grayLines <- forecastPareto %>% select(searchID, PI, Score)
        scPolicies <- forecastPareto %>% filter(Scenario == "Policy Improvement")
        plan2014 <- forecastPareto %>% filter(Policy == "Plan 2014 Baseline") %>% select(searchID, PI, Score)
        
        plt <- ggplot() +
          geom_line(data = grayLines, aes(x = PI, y = Score, group = fct_inorder(as.character(searchID))), alpha = 0.1, color = "gray", inherit.aes = FALSE) + 
          geom_line(data = scPolicies, aes(x = PI, y = Score, group = fct_inorder(as.character(searchID)), color = plotSK), alpha = 0.9, size = 2) +
          geom_line(data = plan2014, aes(x = PI, y = Score, group = fct_inorder(as.character(searchID))), alpha = 0.9, color = reds[1], size = 2, inherit.aes = FALSE) +
          geom_label(data = plotLabels, aes(x = as.factor(PI), y = Y, label = Value), inherit.aes = FALSE,  family = "Arial", size = 5) +
          facet_wrap(~ `Lead-Time`, ncol = 1) +
          theme_bw() +
          scale_color_manual(values = cols, limits = names(cols), drop = FALSE) + 
          scale_linetype_manual(values = c("dotted", "solid")) +
          guides(color = guide_legend(nrow = 1, keywidth = unit(1, "cm"), override.aes = list(size = 2)), 
                 linetype = guide_legend(keywidth = unit(2, "cm"))) +
          scale_x_discrete(breaks = pis, labels = str_wrap(piPlotNames, width = 13)) + 
          scale_y_continuous(name = "Normalized Performance (Min - Max)", n.breaks = 5) +
          theme(
            text = element_text(color = "black", family = "Arial", size = 18),
            title = element_blank(),
            strip.text = element_text(face = "bold", size = 18),
            axis.title.x = element_blank(),
            axis.title.y = element_text(face = "bold", size = 18),
            axis.text.x = element_text(face = "bold", size = 16),
            axis.text.y = element_text(size = 18, angle = 90, vjust = 0, hjust = 0.5),
            legend.title = element_blank(),
            legend.position = "top",
            legend.box = "vertical", 
            legend.text = element_text(size = 18),
            legend.margin = ggplot2::margin()
          )

      }
      
      
    } else {

      if (mode() == "Forecast-Specific Pareto Front") {

        # color palette for plotting
        bluePal <- getBluePal(1)
        redPal <- getRedPal(length(plotPol))
        cols <- c(redPal, yellow, bluePal, "gray")

        if (!is.null(input$plotBrush)) {

          scenarioLevels <- c(plotPol, "Selected Policy", "Brushed Policy", "Set")
          names(cols) <- scenarioLevels

        } else {

          scenarioLevels <- c(plotPol, "Selected Policy", "Policy Improvement", "Set")
          names(cols) <- scenarioLevels

        }

        minmax <- data %>%
          pivot_longer(cols = all_of(pis), names_to = "PI", values_to = "Score") %>%
          group_by(PI) %>%
          mutate(Score = (Score - min(Score)) / (max(Score) - min(Score))) %>%
          ungroup(PI) %>%
          mutate(PI = factor(PI, levels = pis),
                 Selected = ifelse(searchID %in% tableSelection, "Selected Policy", as.character(Scenario)),
                 Selected = factor(Selected, levels = scenarioLevels))

        plt <- ggplot(data = minmax, aes(x = PI, y = Score, group = searchID, color = Selected)) +
          geom_point(alpha = 0.5) +
          geom_path(size = 1, alpha = 0.25, data = ~subset(., Selected == "Set")) +
          geom_path(size = 1, alpha = 0.75, data = ~subset(., (Selected != "Set" & !(Selected %in% plotPol)))) +
          geom_path(size = 1.5, alpha = 1.0, data = ~subset(., (Selected == "Selected Policy"))) +
          geom_path(size = 2, data = ~subset(., Selected %in% plotPol)) +
          geom_label(data = plotLabels, aes(x = as.factor(PI), y = Y, label = Value), inherit.aes = FALSE, family = "Arial", size = 5) +
          theme_bw() +
          scale_color_manual(values = cols, limits = names(cols)) +
          scale_y_continuous(position = "right") +
          ylab("Min-Max Normalized Performance\n(Darkest Red Line = Baseline)\n") +
          theme(text = element_text(family = "Arial", color = "black", size = 18),
                title = element_blank(),
                axis.title.x = element_blank(),
                axis.text.x = element_text(size = 16),
                axis.title.y = element_text(size = 18),
                legend.title = element_blank(),
                legend.position = "top",
                legend.text = element_text(size = 15),
                legend.box = "vertical",
                legend.margin = ggplot2::margin())  +
          scale_x_discrete(labels = function(x) str_wrap(str_replace_all(x, "pf" , " "), width = 15))

      } else if (mode() == "Pareto Front Across All Forecasts") {

        # color palette for plotting
        cols <- c(reds[1], yellow, blues[4], blues[1], "gray")
        names(cols) <- c("Plan 2014 Baseline", "Selected Policy", "Status Quo", "Perfect", "Set")
      
        forecastPareto <- data %>%
          pivot_longer(cols = all_of(pis), names_to = "PI", values_to = "Score") %>%
          group_by(PI) %>%
          mutate(Score = (Score - min(Score)) / (max(Score) - min(Score))) %>%
          ungroup(PI) %>%
          mutate(PI = factor(PI, levels = pis),
                 `Lead-Time` = factor(`Lead-Time`, rev(leadtimeOptions)),
                 Skill = case_when(str_detect(Skill, "Status Quo") ~ "Status Quo", TRUE ~ as.character(Skill)),
                 plotSK = case_when(Scenario == "Plan 2014 Baseline" ~ "Plan 2014 Baseline", Scenario == "Set" ~ "Set", TRUE ~ as.character(Skill)),
                 plotSK = factor(plotSK, levels = c("Plan 2014 Baseline", "Status Quo", "Perfect", "Set")),
                 Selected = case_when(searchID %in% tableSelection ~ "Selected Policy",
                                      Scenario %in% plotPol ~ as.character(Scenario),
                                      Scenario == "Set" ~ as.character(Scenario),
                                      TRUE ~ as.character(plotSK)),
                 Selected = factor(Selected, levels = names(cols)),
                 plotLT = case_when(searchID %in% tableSelection ~ paste("Selected Policy:", Skill),
                                              TRUE ~ NA_character_)) %>%
          arrange(desc(Selected))

        grayLines <- forecastPareto %>% select(searchID, PI, Score)
        scPolicies <- forecastPareto %>% filter(Scenario == "Policy Improvement" & Selected != "Selected Policy")
        plan2014 <- forecastPareto %>% filter(Policy == "Plan 2014 Baseline") %>% select(searchID, PI, Score)
        selectedPols <- forecastPareto %>% filter(Selected == "Selected Policy")
        
        plt <- ggplot() +
          geom_line(data = grayLines, aes(x = PI, y = Score, group = fct_inorder(as.character(searchID))), alpha = 0.1, color = "gray", inherit.aes = FALSE) + 
          geom_line(data = scPolicies, aes(x = PI, y = Score, group = fct_inorder(as.character(searchID)), color = Selected), alpha = 0.9, size = 2) +
          geom_line(data = selectedPols, aes(x = PI, y = Score, group = fct_inorder(as.character(searchID)), linetype = plotLT), color = yellow, alpha = 0.9, size = 2) +
          geom_line(data = plan2014, aes(x = PI, y = Score, group = fct_inorder(as.character(searchID))), alpha = 0.9, color = reds[1], size = 2, inherit.aes = FALSE) +
          geom_label(data = plotLabels, aes(x = as.factor(PI), y = Y, label = Value), inherit.aes = FALSE,  family = "Arial", size = 5) +
          facet_wrap(~ `Lead-Time`, ncol = 1) +
          theme_bw() +
          scale_color_manual(values = cols, limits = names(cols), drop = FALSE) + 
          scale_linetype_manual(values = c("dotted", "solid")) +
          guides(color = guide_legend(nrow = 1, keywidth = unit(1, "cm"), override.aes = list(size = 2)), 
                 linetype = guide_legend(keywidth = unit(2, "cm"))) +
          scale_x_discrete(breaks = pis, labels = str_wrap(piPlotNames, width = 13)) + 
          scale_y_continuous(name = "Normalized Performance (Min - Max)", n.breaks = 5) +
          theme(
            text = element_text(color = "black", family = "Arial", size = 18),
            title = element_blank(),
            strip.text = element_text(face = "bold", size = 18),
            axis.title.x = element_blank(),
            axis.title.y = element_text(face = "bold", size = 18),
            axis.text.x = element_text(face = "bold", size = 16),
            axis.text.y = element_text(size = 18, angle = 90, vjust = 0, hjust = 0.5),
            legend.title = element_blank(),
            legend.position = "top",
            legend.box = "vertical", 
            legend.text = element_text(size = 18),
            legend.margin = ggplot2::margin()
          )
        
      }

    }

    plt 
    
  })
  
  output$filterPlot <- renderUI({
    output$plt <- renderPlot({
        filterPlot()
      })
    if (mode() == "Forecast-Specific Pareto Front") {
      plotOutput("plt", height = "700px", width = "1000px", brush = brushOpts(id = "plotBrush"))
    } else if (mode() == "Pareto Front Across All Forecasts") {
      plotOutput("plt", height = "1200px", width = "1000px", brush = brushOpts(id = "plotBrush"))
    }
  })

  # download button
  output$filterPlotDownload <- downloadHandler(
    filename = function() { paste(input$filterPlotName, input$filterPlotType, sep = ".") },
    content = function(file) {
      if (input$filterPlotType == "pdf") {
        args <- list(file, width = input$filterPlotWidth, height = input$filterPlotHeight)
      } else {
        args <- list(file, width = input$filterPlotWidth, height = input$filterPlotHeight, units = input$filterPlotUnits, res = input$filterPlotRes)
      }
      do.call(input$filterPlotType, args)
      print(filterPlot())
      dev.off()
    }
  )
  
  # table that corresponds to policies
  output$filteredTable <- DT::renderDataTable({

    plotPol <- plotPol()
    selectedPolicies <- selectedPolicies()
    paretoFront <- paretoFront()

    if (input$filterTable == "Percent Change from Baseline") {

      data <- selectedPolicies

    } else if (input$filterTable == "Original PI Units") {

      data <- paretoFront %>%
        left_join(., selectedPolicies %>% select(Scenario, searchID, Experiment, `Lead-Time`, Skill, Policy),
                  by = c("searchID", "Experiment", "Lead-Time", "Skill", "Policy"))

    }

    data %>%
      arrange(Scenario, Experiment, `Lead-Time`, Skill, Policy, searchID) %>%
      select(Scenario, `Lead-Time`, Skill, Policy, all_of(pis), searchID)

  },
  options = list(
    language = list(lengthMenu = "_MENU_"),
    search = list(regex = TRUE, caseInsensitive = TRUE),
    scrollX = TRUE,
    scrollY = TRUE,
    paging = TRUE,
    pageLength = 15,
    lengthChange = FALSE,
    width = 1000,
    sDom  = '<"top">rt<"bottom">ifp'
  ),
  rownames = FALSE,
  filter = list(position = 'bottom'),
  caption = 'Note: Hold shift and click to order by multiple columns.')

  # ---
  # summary plots
  # ---
  
  summaryRobustness <- reactive({
    
    selectedPolicies <- selectedPolicies()
    
    # filter out policy improvements and get searchIDs
    indPolicies <- selectedPolicies %>%
      filter(Scenario == "Policy Improvement") %>%
      select(searchID) %>%
      deframe()
  
    fullDF <- paretoByForecast %>%
      filter(searchID %in% indPolicies) %>%
      mutate(.before = 1, Lookup = paste0(`Lead-Time`, " ", Skill, " (", searchID, ")")) %>%
      select(searchID, Lookup, `Lead-Time`, Skill, Policy, all_of(pis))

    filterCrit <- fullDF %>%
      select(searchID, Lookup, `Lead-Time`, Skill, Policy)

    supplies <- exoHydro %>%
      select(SOW, ontNTS) %>%
      distinct() %>%
      arrange(ontNTS) %>%
      mutate(Rank = 1:nrow(.)) %>%
      select(SOW, Rank)
    
    data <- dynamicRob %>%
      inner_join(filterCrit, ., by = c("Lead-Time", "Skill", "Policy")) %>%
      mutate(`Robust Objectives` = rowSums(select(., contains(pis))),
             `Robust Policy` = ifelse(`Robust Objectives` == 6, 1, 0)) %>%
      
      # filter(!(`Lead-Time` == "12-month" & Skill == "Status Quo (LM)" & SOW == "Historic")) %>%
      mutate(Skill = case_when(str_detect(Skill, "Status Quo") ~ "Status Quo", TRUE ~ as.character(Skill)),
             Forecast = paste(`Lead-Time`, Skill),
             Forecast = factor(Forecast, levels = forecastLevels)) %>%
      
      group_by(Forecast, SOW) %>%
      summarise(`# Robust Policies` = sum(`Robust Policy`)) %>%
      ungroup() %>%
      
      left_join(., supplies, by = "SOW") %>%
      mutate(SOW = case_when(str_detect(SOW, "ssp") ~ "Climate Change", str_detect(SOW, "Stochastic") ~ "Stochastic", str_detect(SOW, "Historic") ~ "Historic", TRUE ~ "NA"))

    data
    
  })
  
  output$summaryRobustTable <- renderDataTable({
    
    summaryRobustness() %>%
      select(Rank, SOW,Forecast, `# Robust Policies`) %>%
      pivot_wider(id_cols = c(Rank, SOW), names_from = "Forecast", values_from = "# Robust Policies", values_fn = sum) %>%
      arrange(Rank) %>%
      select(Rank, SOW, any_of(forecastLevels))
    
  }, options = list(
    language = list(lengthMenu = "_MENU_"), 
    search = list(regex = TRUE, caseInsensitive = TRUE),
    scrollX = TRUE, 
    scrollY = TRUE, 
    paging = TRUE,
    pageLength = 15,
    lengthChange = FALSE,
    width = 1000,
    sDom  = '<"top">rt<"bottom">ifp'
  ),
  rownames = FALSE)
  
  summaryRobustPlot <- reactive({
    
    data <- summaryRobustness()
    
    ggplot(data = data, aes(x = Forecast, y = `# Robust Policies`, group = Forecast)) +
      geom_point(aes(fill = Rank, shape = SOW, size = SOW), position = position_jitterdodge(jitter.width = 0.5), color = "gray", alpha = 0.5) +
      geom_boxplot(outlier.shape = NA, fill = NA, size = 1.5) +
      scale_shape_manual(values = c(23, 24, 21)) +
      scale_size_manual(values = c(2, 5, 2)) +
      scale_fill_gradientn(colors = rev(c(blues, rev(reds))), labels = NULL) +
      theme_bw() +
      xlab("\nForecast Type") +
      ylab("Number of Satisficing Policies\n") +
      scale_x_discrete(labels = function(x) str_wrap(x, width = 12)) +
      guides(size = "none",
             fill = guide_colourbar(title = "State-of-the-World (Drier → Wetter)", title.position = "top", ticks = FALSE),
             shape = guide_legend(title = "Supply Dataset", title.position = "top", override.aes = list(size = 5, stroke = 1.5, color = "black"))) +
      theme(text = element_text(family = "Arial", color = "black", size = 18),
            title = element_blank(),
            axis.title = element_text(size = 18),
            axis.text.y = element_text(size = 18, angle = 90, hjust = 0.5),
            axis.text.x = element_text(size = 18),
            legend.position = "top",
            legend.title = element_text(size = 18),
            legend.margin = ggplot2::margin(),
            legend.spacing.x = unit(0.25, "cm"),
            legend.key.width = unit(3, "cm"))
    
  })
  
  output$summaryRobustPlot <- renderPlot({
    
    summaryRobustPlot()
    
  })
  
  # download button
  output$summaryRobustDownload <- downloadHandler(
    filename = function() { paste(input$summaryRobustName, input$summaryRobustType, sep = ".") },
    content = function(file) {
      if (input$summaryRobustType == "pdf") {
        args <- list(file, width = input$summaryRobustWidth, height = input$summaryRobustHeight)
      } else {
        args <- list(file, width = input$summaryRobustWidth, height = input$summaryRobustHeight, units = input$summaryRobustUnits, res = input$summaryRobustRes)
      }
      do.call(input$summaryRobustType, args)
      print(summaryRobustPlot())
      dev.off()
    }
  )
  
  # ---
  # stochastic/climate reanalysis
  # ---
  
  # use selected tables from table on previous tab as which stochastic runs to load
  candidateIndex <- reactive({
    input$filteredTable_rows_selected
  })
  
  policySelection <- reactive({input$policySelection})
  
  # update policies to reevaluate
  observeEvent(candidateIndex(), {
    
    if (policySelection() == "Select from Table") {
      
      data <- selectedPolicies() %>%
        arrange(Scenario, Experiment, `Lead-Time`, Skill, Policy, searchID) %>%
        slice(as.numeric(candidateIndex())) %>%
        select(searchID) %>%
        deframe()
      
      updatePickerInput(session, "evalPolicies", choices = data, selected = data)
      
    }
    
  })
  
  candidatePolicies <- reactive({
    
    if (is.null(input$evalPolicies) & is.null(input$evalPoliciesManual)) return()
    
    if (policySelection() == "Select from Table") {
      
      pols <- as.numeric(input$evalPolicies)
      
    } else if (policySelection() == "Select by searchID") {
      
      pols <- as.numeric(trimws(str_split(input$evalPoliciesManual, ",")[[1]]))
      
    }
    
    pols
    
  })
  
  runData <- reactive({
    
    dataType <- input$runData
    
    dataFilter <- ifelse(dataType == "Historic", "Historic",
                         ifelse(dataType == "Stochastic", "Stochastic",
                                ifelse(dataType == "Climate Scenarios", "ssp", "All SOW Traces")))
    dataFilter
    
  })
  
  runPolicies <- reactive({
    
    if(length(candidatePolicies()) == 0 || is.na(candidatePolicies())) return()
    
    indPolicies <- candidatePolicies()
    
    data <- paretoByForecast %>%
      filter(searchID %in% indPolicies) %>%
      mutate(.before = 1, Lookup = paste0(`Lead-Time`, " ", Skill, " (", searchID, ")")) %>%
      select(searchID, Lookup, `Lead-Time`, Skill, Policy, all_of(pis))
    
    bline <- paretoBaseline %>%
      filter(Policy == "Plan 2014 Baseline") %>%
      mutate(.before = 1, searchID = 0, Lookup = "Plan 2014") %>%
      select(searchID, Lookup, `Lead-Time`, Skill, Policy, all_of(pis))
    
    # print(paste(data$searchID, collapse = ","))
    tmp <- rbind(data, bline)
    tmp
    
  })
  
  output$candidatePolicyTable <- renderDataTable({
    
    if(length(candidatePolicies()) == 0 || is.na(candidatePolicies())) return()
    
    runPolicies()
    
  },
  options = list(
    scrollX = TRUE,
    searching = FALSE,
    sDom  = '<"top">rt',
    width = 1000
  ),
  rownames = FALSE)
  
  filterCrit <- reactive({
    
    runPolicies() %>% select(searchID, Lookup, `Lead-Time`, Skill, Policy)
    
  })
  
  polLevels <- reactive({
    
    filterCrit <- filterCrit()
    pols <- filterCrit$Lookup
    c(pols[pols == "Plan 2014"], mixedsort(pols[pols != "Plan 2014"], decreasing = TRUE))
    
    
  })
  
  # ---
  # measures of robustness
  # ---
  
  output$robustTitle <- reactive({
    
    if(length(candidatePolicies()) == 0 || is.na(candidatePolicies())) return()
    
    n <- nSOWS
    paste0("Measure of Robustness (n = ", n, " Traces)")
    
  })
  
  # performance based on Plan 2014 with historic supplies (STATIC)
  staticRobustness <- reactive({
    
    if(length(candidatePolicies()) == 0 || is.na(candidatePolicies())) return()
    
    filterCrit <- filterCrit()
    runData <- runData()
    
    data <- staticRob %>%
      inner_join(filterCrit, ., by = c("Lead-Time", "Skill", "Policy"), multiple = "all") %>%
      filter(if (runData != "All SOW Traces") str_detect(SOW, runData) else TRUE) %>%
      mutate(`Robust Objectives` = rowSums(select(., contains(pis))),
             `Robust Policy` = ifelse(`Robust Objectives` == 6, 1, 0))
    
    data
    
  })
  
  # performance based on Plan 2014 with historic supplies (STATIC)
  staticNormalized <- reactive({
    
    if(length(candidatePolicies()) == 0 || is.na(candidatePolicies())) return()
    
    filterCrit <- filterCrit()
    runData <- runData()
    
    data <- staticNorm %>%
      inner_join(filterCrit, ., by = c("Lead-Time", "Skill", "Policy"), multiple = "all") %>%
      filter(if (runData != "All SOW Traces") str_detect(SOW, runData) else TRUE)
    
    data
    
  })
  
  # performance based on Plan 2014 with same stochastic trace of supplies (DYNAMIC)
  dynamicRobustness <- reactive({
    
    if(length(candidatePolicies()) == 0 || is.na(candidatePolicies())) return()
    
    filterCrit <- filterCrit()
    runData <- runData()
    
    data <- dynamicRob %>%
      inner_join(filterCrit, ., by = c("Lead-Time", "Skill", "Policy"), multiple = "all") %>%
      filter(if (runData != "All SOW Traces") str_detect(SOW, runData) else TRUE) %>%
      mutate(`Robust Objectives` = rowSums(select(., contains(pis))),
             `Robust Policy` = ifelse(`Robust Objectives` == 6, 1, 0))
    
    data
    
  })
  
  # performance based on Plan 2014 with same stochastic trace of supplies (DYNAMIC)
  dynamicNormalized <- reactive({
    
    if(length(candidatePolicies()) == 0 || is.na(candidatePolicies())) return()
    
    filterCrit <- filterCrit()
    runData <- runData()
    
    data <- dynamicNorm %>%
      inner_join(filterCrit, ., by = c("Lead-Time", "Skill", "Policy"), multiple = "all") %>%
      filter(if (runData != "All SOW Traces") str_detect(SOW, runData) else TRUE)
    
    data
    
  })
  
  # see what exogenous variables affect pi robustness
  factorRanking <- reactive({
    
    if(length(candidatePolicies()) == 0 || is.na(candidatePolicies())) return()
    
    filterCrit <- filterCrit()
    runData <- runData()
    
    data <- factorRank %>%
      inner_join(filterCrit, ., by = c("Lead-Time", "Skill", "Policy"), multiple = "all") %>%
      filter(if (runData != "All SOW Traces") str_detect(SOW, runData) else TRUE) %>%
      filter(Policy != "Plan 2014 Baseline")
    
    data
    
  })
  
  # see what exogenous variables affect pi robustness
  exogenousHydro <- reactive({
    
    if(length(candidatePolicies()) == 0 || is.na(candidatePolicies())) return()
    
    filterCrit <- filterCrit()
    runData <- runData()
    
    data <- exoHydro %>%
      inner_join(filterCrit, ., by = c("Lead-Time", "Skill", "Policy"), multiple = "all") %>%
      filter(if (runData != "All SOW Traces") str_detect(SOW, runData) else TRUE) %>%
      filter(Policy != "Plan 2014 Baseline")
    
    
    data
    
  })
  
  output$robustnessTable <- renderDataTable({
    
    if(length(candidatePolicies()) == 0 || is.na(candidatePolicies())) return()
    
    staticRobustness <- staticRobustness()
    dynamicRobustness <- dynamicRobustness()
    polLevels <- polLevels()
    
    static <- staticRobustness %>%
      group_by(searchID, Lookup, `Lead-Time`, Skill, Policy) %>%
      summarise(`Robust SOWs` = sum(`Robust Policy`),
                `Total SOWs` = nSOWS,
                `Robustness Score` = round((`Robust SOWs` / `Total SOWs`) * 100, 2)) %>%
      ungroup() %>%
      select(Lookup, `Robust SOWs`, `Robustness Score`) %>%
      setNames(c("Lookup", "Robust SOWs (Static)", "Robustness Score (Static)"))
    
    dynamic <- dynamicRobustness %>%
      group_by(searchID, Lookup, `Lead-Time`, Skill, Policy) %>%
      summarise(`Robust SOWs` = sum(`Robust Policy`),
                `Total SOWs` = nSOWS,
                `Robustness Score` = round((`Robust SOWs` / `Total SOWs`) * 100, 2)) %>%
      ungroup() %>%
      select(Lookup, `Robust SOWs`, `Robustness Score`) %>%
      setNames(c("Lookup", "Robust SOWs (Dynamic)", "Robustness Score (Dynamic)"))
    
    dynamicByObj <- dynamicRobustness %>%
      select(searchID, Lookup, `Lead-Time`, Skill, Policy, `Robust Objectives`) %>%
      mutate(`Robust Objectives` = 6 - `Robust Objectives`,
             `Robust Objectives` = paste(`Robust Objectives`, "PI Failures")) %>%
      arrange(`Robust Objectives`) %>%
      pivot_wider(id_cols = c(searchID, Lookup, `Lead-Time`, Skill, Policy), 
                  names_from = "Robust Objectives", values_from = "Robust Objectives", values_fn = length) %>%
      select(Lookup, contains("PI Failures"))
    
    full_join(static, dynamic, by = c("Lookup")) %>%
      full_join(., dynamicByObj, by = c("Lookup")) %>% 
      mutate(Lookup = factor(Lookup, levels = polLevels)) %>%
      arrange(Lookup)
    
    # full_join(static, dynamic, by = c("Lookup")) %>%
    #   mutate(Lookup = factor(Lookup, levels = polLevels))
    
  },
  options = list(
    sDom  = '<"top">t',
    width = 1000
  ),
  rownames = FALSE)
  
  robustnessDef <- reactive({
    input$robustDef
  })
  
  robustPlot <- reactive({
    
    if(length(candidatePolicies()) == 0 || is.na(candidatePolicies())) return()
    
    robustnessDef <-robustnessDef()
    
    if (robustnessDef == "Static") {
      
      robustness <- staticRobustness()
      normalized <- staticNormalized()
      
    } else if (robustnessDef == "Dynamic") {
      
      robustness <- dynamicRobustness()
      normalized <- dynamicNormalized()
      
    }
    
    exogenousHydro <- exogenousHydro()
    polLevels <- polLevels()
    
    tmp <- exogenousHydro %>%
      select(Lookup, SOW, ontNTS) %>%
      arrange(ontNTS) %>%
      mutate(Label = case_when(str_detect(SOW, "Historic") ~ "Historic", str_detect(SOW, "Stochastic") ~ paste("ST", str_remove(SOW, "Stochastic Century ")), str_detect(SOW, "ssp") ~ "CC", TRUE ~ "NA"))
    
    # get severity of failures for coloring
    failColor <- normalized %>%
      select(Lookup, SOW, all_of(pis)) %>%
      setNames(c("Lookup", "SOW", pis)) %>%
      pivot_longer(cols = -c(Lookup, SOW), names_to = "PI", values_to = "Severity")
    
    # make matrix for portrait plot of rules
    portrait <- robustness %>%
      select(Lookup, SOW, all_of(pis)) %>%
      setNames(c("Lookup", "SOW", pis)) %>%
      pivot_longer(cols = -c(Lookup, SOW), names_to = "PI", values_to = "Value") %>%
      left_join(., tmp %>% select(Lookup, SOW, Label), by = c("Lookup", "SOW")) %>%
      left_join(., failColor, by = c("Lookup", "SOW", "PI")) %>%
      mutate(Value = ifelse(Value == 1, "Satisficing", "Fails")) %>%
      # group_by(Lookup, PI, Value) %>%
      group_by(PI, Value) %>%
      mutate(normSev = case_when(Value == "Satisficing" ~ NaN, TRUE ~ (Severity - min(Severity)) / (max(Severity) - min(Severity)))) %>%
      ungroup() %>%
      left_join(., data.frame(piPlotNames, "PI" = names(piPlotNames)), by = "PI") %>%
      rename("piName" = "piPlotNames") %>%
      left_join(., data.frame(piAbbNames, "PI" = names(piAbbNames)), by = "PI") %>%
      rename("piCode" = "piAbbNames") %>%
      mutate(piName = paste0(piCode, ": ", piName),
             piName = factor(piName, levels = rev(paste0(piAbbNames, ": ", piPlotNames))),
             Lookup = factor(Lookup, levels = polLevels),
             SOW = factor(SOW, levels = unique(tmp$SOW)),
             Label = case_when(str_detect(SOW, "Historic") ~ "Historic", str_detect(SOW, "Stochastic") ~ "Stochastic", str_detect(SOW, "ssp") ~ "Climate Change", TRUE ~ "NA"),
             Label = factor(Label, levels = c("Historic", "Stochastic", "Climate Change")))
    
    if (robustnessDef == "Dynamic") { portrait <- portrait %>% filter(Lookup != "Plan 2014") }
    
    plt <-
      ggplot(data = portrait, aes(x = SOW, y = PI)) +
      facet_wrap(~ Lookup, ncol = 1, scales = "free_y") +
      geom_tile(aes(color = "Satisficing", fill = normSev)) +
      geom_tile(data = portrait %>% filter(SOW == "Historic"), aes(x = SOW, y = PI), fill = NA, linewidth = 0.75, color = "black", inherit.aes = FALSE) +
      theme_bw() +
      xlab("\nState-of-the-World (Drier → Wetter)") +
      ylab("Performance Indicator \n") + 
      scale_fill_gradientn(name = "Policy Performance", colors = rev(reds), na.value = blues[1], breaks = c(0, 1), labels = c("0 (Mild Failure)", "1 (Severe Failure)"), guide = guide_legend(direction = "horizontal")) +
      scale_color_manual(name = " ", values = "white") +
      guides(fill = guide_colorbar(order = 1, title.position = "top", ticks = FALSE, label.hjust = c(-0.05, 1.01)),
             color = guide_legend(label.position = "bottom", title.position = "top", override.aes = list(fill = blues[1]))) +
      scale_x_discrete(labels = "", breaks = "") +
      scale_y_discrete(limits = rev(pis), labels = rev(c("UpCoast", "DownCoast", "CommNav", "Hydro", "EcoHealth", "Muskrat", "RecBoat"))) +
      theme(text = element_text(family = "Arial", color = "black", size = 18),
            # title = element_blank(),
            axis.title = element_text(size = 18),
            axis.text = element_text(size = 18),
            # axis.text.x = element_text(size = 18),
            legend.position = "top",
            # legend.title = element_blank(),
            legend.margin = ggplot2::margin(),
            legend.key.width = unit(3, "cm")
      )
    
    plt
    
  })
  
  output$robustPlot <- renderPlot({
    robustPlot()
  })
  
  # download button
  output$robustPlotDownload <- downloadHandler(
    filename = function() { paste(input$robustPlotName, input$robustPlotType, sep = ".") },
    content = function(file) {
      if (input$robustPlotType == "pdf") {
        args <- list(file, width = input$robustPlotWidth, height = input$robustPlotHeight)
      } else {
        args <- list(file, width = input$robustPlotWidth, height = input$robustPlotHeight, units = input$robustPlotUnits, res = input$robustPlotRes)
      }
      do.call(input$robustPlotType, args)
      print(robustPlot())
      dev.off()
    }
  )
  
  output$factorMapPlanSelector <- renderUI({
    
    newPols <- filterCrit() %>% select(Lookup) %>% deframe()
    selectInput(inputId = "factorMapPlanInput", label = "Plans to Display", multiple = TRUE, choices = newPols, selected = c())
    
  })
  
  plotPlan <- reactive({
    input$factorMapPlanInput
  })
  
  plotPI <- reactive({
    input$factorMapPIInput
  })

  factorMapPlot <- reactive({
    
    if(is.null(plotPlan())) return()
  
    factorRanking <- factorRanking()
    dynamicRobustness <- dynamicRobustness()
    dynamicNormalized <- dynamicNormalized()
    exogenousHydro <- exogenousHydro()
    polLevels <- polLevels()
    plotPlan <- plotPlan()
    plotPI <- plotPI()
    
    print(plotPlan)
    
    # filter based on input
    polLevels <- polLevels[polLevels %in% plotPlan]
    piLevs <- pis[pis %in% plotPI]
    
    output <- list()
    labels <- list()
    count <- 1
    
    # get severity of failures for coloring
    failColor <- dynamicNormalized %>%
      select(Lookup, SOW, all_of(piLevs)) %>%
      pivot_longer(cols = -c(Lookup, SOW), names_to = "PI", values_to = "Severity")
    
    # set naming and coloring conventions
    plotCols <- data.frame("Variable" = c("ontNTS", "ontNTSSpring", "ontNTSSummer", "ontNTSFall", "ontNTSWinter", "stlouisontOut", "stlouisontOutSpring", "stlouisontOutSummer", "stlouisontOutFall", "stlouisontOutWinter", "unstableIce"),
                           "fullName" = c("Upstream Supply", "Upstream Supply (Spring)", "Upstream Supply (Summer)", "Upstream Supply (Fall)", "Upstream Supply (Winter)", "Downstream Supply", "Downstream Supply (Spring)", "Downstream Supply (Summer)", "Downstream Supply (Fall)", "Downstream Supply (Winter)", "Unstable Ice"),
                           "varColor" = c(getBluePal(5), getRedPal(5), yellow)) %>%
      mutate(varCode = letters[1:nrow(.)],
             legendName = paste0(varCode, ": ", fullName))
    
    # get plot labels
    plans <- polLevels[polLevels != "Plan 2014"]
    for (p in plans) {
      
      # filter objective by plan
      obj <- dynamicRobustness %>%
        filter(Lookup == p) %>%
        pivot_longer(cols = all_of(piLevs), names_to = "PI", values_to = "Robust Score") %>%
        select(Lookup, SOW, PI, `Robust Score`)
      
      # get top two factors for each plan
      hydro <- factorRanking %>%
        filter(Lookup == p) %>%
        select(-c(`Lead-Time`, Skill, Policy)) %>%
        pivot_longer(cols = - c(searchID, Lookup, PI), names_to = "Variable", values_to = "Value") %>%
        mutate(Value = Value * 100) %>%
        arrange(desc(Value)) %>%
        group_by(PI) %>%
        slice(1:2)
      
      x <- hydro %>%
        slice(1) %>%
        ungroup() %>%
        left_join(., plotCols, by = "Variable") %>%
        select(searchID, Lookup, PI, Variable, fullName, Value) %>%
        setNames(c("searchID", "Lookup", "PI", "X Var Code", "X Variable", "X Importance"))
      
      y <- hydro %>%
        slice(-1) %>%
        ungroup() %>%
        left_join(., plotCols, by = "Variable") %>%
        select(searchID, Lookup, PI, Variable, fullName, Value) %>%
        setNames(c("searchID", "Lookup", "PI", "Y Var Code", "Y Variable", "Y Importance"))
      
      featureImportance <- full_join(x, y, by = c("searchID", "Lookup", "PI"))
      
      for (i in 1:length(piLevs)) {
        
        poi <- piLevs[i]
        
        xVar <- featureImportance %>%
          filter(PI == poi) %>%
          select(`X Var Code`) %>%
          deframe()
        
        yVar <- featureImportance %>%
          filter(PI == poi) %>%
          select(`Y Var Code`) %>%
          deframe()
        
        tmp <- exogenousHydro %>%
          filter(Lookup == p) %>%
          select(Lookup, SOW, all_of(xVar), all_of(yVar)) %>%
          setNames(c("Lookup", "SOW", "X", "Y"))
        
        tmp2 <- obj %>%
          filter(PI == poi) %>%
          left_join(., tmp, by = c("Lookup", "SOW"))
        
        output[[count]] <- tmp2
        
        tmpLabel <- featureImportance %>%
          mutate(xLabel = paste0(`X Variable`, ": ", round(`X Importance`, 0), "%"),
                 yLabel = paste0(`Y Variable`, ": ", round(`Y Importance`, 0), "%"),
                 Lookup = p) %>%
          select(Lookup, PI, xLabel, yLabel)
        
        labels[[count]] <- tmpLabel
        
        count <- count + 1
        
      }
      
    }
    
    data <- bind_rows(output) %>%
      mutate(Dataset = case_when(str_detect(SOW, "Historic") ~ "Historic",
                                 str_detect(SOW, "Stochastic") ~ "Stochastic",
                                 str_detect(SOW, "ssp") ~ "Climate Scenario",
                                 TRUE ~ "NA"),
             Robust = case_when(`Robust Score` == 1 ~ "Robust",
                                `Robust Score` == 0 ~ "Fails",
                                TRUE ~ "NA")) %>%
      left_join(., failColor, by = c("Lookup", "SOW", "PI")) %>%
      group_by(Lookup, PI, Robust) %>%
      mutate(normSev = case_when(Robust == "Robust" ~ NaN, TRUE ~ (Severity - min(Severity)) / (max(Severity) - min(Severity))),
             Lookup = factor(Lookup, levels = polLevels),
             PI = factor(PI, levels = piLevs),
             Dataset = factor(Dataset, levels = c("Historic", "Stochastic", "Climate Scenario"))) %>%
      arrange(desc(Dataset))
    
    pltLabels <- bind_rows(labels) %>%
      distinct() %>%
      mutate(Lookup = factor(Lookup, levels = polLevels),
             PI = factor(PI, levels = piLevs))
    
    # ggplot(data = data, aes(x = X, y = Y, fill = normSev, size = Dataset, shape = Dataset, alpha = Dataset)) +
    #   ggh4x::facet_grid2(rows = vars(PI), cols = vars(Lookup), scales = "free", independent = "all", labeller = label_wrap_gen(width = 22, multi_line = TRUE)) +
    #   geom_point(aes(color = "Robust"), stroke = 0.5) +
    #   scale_fill_gradientn(colors = rev(reds), na.value = blues[1], breaks = c(0, 1), labels = c("Mild Failure", "Severe Failure"), guide = guide_legend(direction = "horizontal", title.position = "bottom")) +
    #   scale_shape_manual(values = c(24, 21, 23)) +
    #   scale_alpha_manual(values = c(1.0, 0.75, 0.75)) +
    #   scale_size_manual(values = c(5, 2, 2)) + 
    #   scale_color_manual(values = c("gray")) +
    #   coord_trans(clip = "off") +
    #   scale_x_continuous(guide = guide_axis(check.overlap = TRUE)) + 
    #   scale_y_continuous(guide = guide_axis(check.overlap = TRUE)) +
    #   guides(size = "none", alpha = "none",
    #          shape = guide_legend(order = 1, override.aes = list(size = 5, color = "gray")),
    #           color = guide_legend(order = 2, override.aes = list(size = 5, color = blues[1])),
    #          fill = guide_colorbar()) +
    #   geom_text(size = 3, family = "Arial", data = pltLabels, aes(label = xLabel), inherit.aes = FALSE, x = Inf, y = -Inf, hjust = 1.05, vjust = -0.5, color = "black") +
    #   geom_text(size = 3, family = "Arial", data = pltLabels, aes(label = yLabel), inherit.aes = FALSE, x = -Inf, y = Inf, angle = 90, hjust = 1.05, vjust = 1.5, color = "black") +
    #   theme_bw() +
    #   theme(text = element_text(color = "black", family = "Arial", size = 18),
    #         title = element_blank(),
    #         axis.title = element_blank(),
    #         axis.text.y = element_text(angle = 90, size = 10, hjust = 0.5),
    #         axis.text.x = element_text(size = 10, hjust = 0.5),
    #         legend.position = "top",
    #         legend.title = element_blank(),
    #         legend.box = "horizontal", 
    #         legend.margin = ggplot2::margin(),
    #         legend.key.width = unit(1, "cm"),
    #         legend.justification = "center",
    #         panel.spacing = unit(1.25, "lines"))
    
    # lists to store plots
    plots <- list()
    piLabels <- list()
    
    # plot aesthetics
    piLabelSize <- 10
    piLabelWrap <- 20
    piLabelHeight <- 5
    rowSpacing <- 1
    planLabelSize <- 10
    planLabelWrap <- 10
    planLabelHeight <- 5
    pltHeight <- 10
    pltWidth <- 10
    axisTextSize <- 18
    overallTextSize <- 18
    
    # make plots
    for (j in 1:length(plans)) {
      
      p <- plans[j]
      colPlots <- list()
      
      for (i in 1:length(piLevs)) {
        
        poi <- piLevs[i]
        
        tmpHydro <- factorRanking %>%
          filter(Lookup == p) %>% 
          select(-c(`Lead-Time`, Skill, Policy)) %>%
          pivot_longer(cols = - c(searchID, Lookup, PI), names_to = "Variable", values_to = "Value") %>% 
          mutate(Value = Value * 100) %>%
          filter(PI == poi) %>%
          left_join(., plotCols, by = "Variable") %>%
          arrange(desc(Value)) %>%
          mutate(varCode = factor(varCode, levels = (unique(varCode)))) %>%
          drop_na()
        
        tmpData <- data %>%
          filter(Lookup == p & PI == poi)
        
        tmpLabels <- pltLabels %>%
          filter(Lookup == p & PI == poi)
        
        # make side by side plots
        if (nrow(tmpHydro) > 0) { 
          
          plt1 <- ggplot(data = tmpHydro, aes(x = varCode, y = Value, fill = legendName)) +
            geom_col(color = "black") +
            geom_text(aes(label = paste0(round(Value, 0), "%")), vjust = -0.5) +
            scale_fill_manual(breaks = plotCols$legendName, values = plotCols$varColor) +
            ylab("Relative Feature Importance") + 
            xlab("Hydrologic Variable") + 
            theme_bw() +
            theme(text = element_text(color = "black", family = "Arial", size = overallTextSize),
                  title = element_blank(),
                  axis.title = element_text(),
                  axis.text.y = element_text(angle = 90, size = axisTextSize, hjust = 0.5),
                  axis.text.x = element_text(size = axisTextSize, hjust = 0.5))
          
          plt2 <- ggplot(data = tmpData, aes(x = X, y = Y, fill = normSev, size = Dataset, shape = Dataset, alpha = Dataset)) + 
            geom_point(aes(color = "Robust"), stroke = 0.5) +
            scale_fill_gradientn(colors = rev(reds), na.value = blues[1], breaks = c(0, 1), labels = c("Mild Failure", "Severe Failure"), guide = guide_legend(direction = "horizontal", title.position = "bottom")) +
            scale_shape_manual(values = c(24, 21, 23)) +
            scale_alpha_manual(values = c(1.0, 0.75, 0.75)) +
            scale_size_manual(values = c(5, 2, 2)) +
            scale_color_manual(values = c("gray")) +
            scale_x_continuous(guide = guide_axis(check.overlap = TRUE)) + 
            scale_y_continuous(guide = guide_axis(check.overlap = TRUE)) + 
            guides(size = "none", alpha = "none",
                   shape = guide_legend(order = 1, override.aes = list(size = 5, stroke = 1.25, color = "gray")),
                   color = guide_legend(order = 2, override.aes = list(size = 5, color = blues[1])), 
                   fill = guide_colorbar()) +
            xlab(tmpLabels$xLabel) + 
            ylab(tmpLabels$yLabel) + 
            theme_bw() +
            theme(text = element_text(color = "black", size = overallTextSize),
                  title = element_blank(),
                  axis.title = element_text(),
                  axis.text.y = element_text(angle = 90, size = axisTextSize, hjust = 0.5),
                  axis.text.x = element_text(size = axisTextSize, hjust = 0.5))
          
        } else { 
          
          plt1 <- ggplot(data = tmpHydro, aes(x = varCode, y = Value)) +
            geom_blank() +
            annotate("label", size = 6, label.padding = unit(0.5, "cm"), x = max(tmpData$X) * 0.5, y = max(tmpData$Y) * 0.5, label = "No Failures\nAcross SOWs") + 
            scale_x_continuous(labels = c("", ""), breaks = c(0, max(tmpData$X)), limits = c(0, max(tmpData$X))) +
            scale_y_continuous(labels = c("", ""), breaks = c(0, max(tmpData$Y)), limits = c(0, max(tmpData$Y))) +
            ylab("Relative Feature Importance") + 
            xlab("Hydrologic Variable") + 
            theme_bw() +
            theme(text = element_text(color = "black", family = "Arial", size = overallTextSize),
                  title = element_blank(),
                  axis.title = element_text(),
                  axis.text.y = element_text(angle = 90, size = axisTextSize, hjust = 0.5),
                  axis.text.x = element_text(size = axisTextSize, hjust = 0.5))
          
          plt2 <- ggplot(data = tmpData, aes(x = X, y = Y)) +
            geom_blank() +
            scale_x_continuous(labels = c("", ""), breaks = c(0, max(tmpData$X)), limits = c(0, max(tmpData$X))) +
            scale_y_continuous(labels = c("", ""), breaks = c(0, max(tmpData$Y)), limits = c(0, max(tmpData$Y))) +
            annotate("label", size = 6, label.padding = unit(0.5, "cm"), x = max(tmpData$X) * 0.5, y = max(tmpData$Y) * 0.5, label = "No Failures\nAcross SOWs") + 
            xlab("") +
            ylab("") +
            theme_bw() +
            theme(text = element_text(color = "black", size = overallTextSize),
                  title = element_blank(),
                  axis.title = element_text(),
                  axis.text.y = element_text(angle = 90, size = axisTextSize, hjust = 0.5),
                  axis.text.x = element_text(size = axisTextSize, hjust = 0.5))
          
        }
        
        colPlots[[i]] <- (plt1 | plt2) +
          plot_layout(heights = unit(pltHeight, 'cm'))
        
        # save pi label for later
        if (j == 1) {
          
          piLabels[[i]] <- ggplot(data = tibble(x = 0.5, y = 0.5, label = piLevs[i]), aes(x = x, y = y, label = label)) +
            geom_textbox(fontface = "bold", size = piLabelSize, box.color = NA, fill = NA, halign = 0.5, valign = 0.5, width = unit(piLabelWrap, "cm"), hjust = 0.5, vjust = 0.5) +
            scale_x_continuous(limits = c(0, 1), expand = c(0, 0)) +
            scale_y_continuous(limits = c(0, 1), expand = c(0, 0)) +
            theme_void() +
            theme(plot.margin = ggplot2::margin(0, 0, 0, 0))
          
        }
        
      }
      
      # make first column for plan names
      textPlot <- ggplot(data = tibble(x = 0.5, y = 0.5, label = p), aes(x = x, y = y, label = label)) +
        geom_textbox(orientation = "left-rotated", size = planLabelSize, box.color = NA, fill = NA, halign = 0.5, valign = 0.5, width = unit(planLabelWrap, "cm"), hjust = 0.5, vjust = 0.5) +
        scale_x_continuous(limits = c(0, 1), expand = c(0, 0)) +
        scale_y_continuous(limits = c(0, 1), expand = c(0, 0)) +
        theme_void() +
        theme(plot.margin = ggplot2::margin(0, 0, 0, 0))
      
      blankSpace <- ggplot(data = tibble(x = 0.5, y = 0.5, label = ""), aes(x = x, y = y, label = label)) +
        geom_textbox(orientation = "left-rotated", size = planLabelSize, box.color = NA, fill = NA, halign = 0.5, valign = 0.5, width = unit(planLabelWrap, "cm"), hjust = 0.5, vjust = 0.5) +
        scale_x_continuous(limits = c(0, 1), expand = c(0, 0)) +
        scale_y_continuous(limits = c(0, 1), expand = c(0, 0)) +
        theme_void() +
        theme(plot.margin = ggplot2::margin(0, 0, 0, 0))
      
      textPlot <- blankSpace / textPlot + 
        plot_layout(heights = unit(c(rowSpacing, pltHeight), c('cm', 'cm')))
      
      fullPlot <- wrap_plots(colPlots, nrow = 1)
      plots[[j]] <- (textPlot | fullPlot) + 
        plot_layout(widths = unit(c(planLabelHeight, 1), c('cm', 'null')))
      
    }
    
    # add blank space to start of pi labels to account for plan labels
    blankSpace <- ggplot() +
      geom_blank() +
      theme_void() +
      theme(plot.margin = ggplot2::margin(0, 0, 0, 0))
    
    # put together first row for pi names
    piLabels <- wrap_plots(piLabels, nrow = 1)
    piLabels <- (blankSpace | piLabels) + 
      plot_layout(widths = unit(c(planLabelHeight, 1), c('cm', 'null')))
    
    # wrap plots (already including plan names)
    p <- wrap_plots(plots, ncol = 1, guides = "collect") &
      theme(legend.position = "right",
            legend.text = element_text(size = 30))
    
    # stack pi row on top of the rest of the plot
    plt <- (piLabels / p) + 
      plot_layout(heights = unit(c(piLabelHeight, 1), c('cm', 'null')))
    
    plt
    
    # # set plot dimensions based on number of plans and pis
    # saveHeight <- piLabelHeight + (pltHeight * length(plans)) + (rowSpacing * length(plans)) * 1.75
    # saveWidth <- planLabelHeight + (pltWidth * length(pis) * 2) * 1.5
    # 
    # # save plot
    # png("plots.png", width = saveWidth, height = saveHeight, units = "cm", res = 330)
    # plt
    # dev.off()
    
  })
  
  output$factorMapPlot <- renderPlot({
    factorMapPlot()
  })
  
  output$factorMapDownload <- downloadHandler(
    filename = function() { paste(input$factorMapName, input$factorMapType, sep = ".") },
    content = function(file) {
      if (input$factorMapType == "pdf") {
        args <- list(file, width = input$factorMapWidth, height = input$factorMapHeight)
      } else {
        args <- list(file, width = input$factorMapWidth, height = input$factorMapHeight, units = input$factorMapUnits, res = input$factorMapRes)
      }
      do.call(input$factorMapType, args)
      print(factorMapPlot())
      dev.off()
    }
  )
  
  # ---
  # spatially disaggregated pis
  # ---
  
  # statistic selections  
  boxplotDisplay <- reactive({input$boxplot})
  mmSupplyType <- reactive({input$mmboxplot})
  
  spatialPlotData <- reactive({
    
    if(length(candidatePolicies()) == 0 || is.na(candidatePolicies())) return()
    
    filterCrit <- filterCrit()
    runData <- runData()
    
    data <- annualObjs %>%
      inner_join(filterCrit, ., by = c("Lead-Time", "Skill", "Policy")) %>%
      filter(if (runData != "All SOW Traces") str_detect(SOW, runData) else TRUE) %>%
      left_join(., piLevels, by = "PI") %>%
      mutate(Value = case_when(`PI Group` %in% c("Hydropower", "Wetland Health & Services") ~ Value * 1,
                               `PI Group` %in% c("Coastal Impacts", "Commercial Navigation", "Recreational Boating") ~ Value * -1,
                               TRUE ~ Value))
    
    statFilter <- ifelse(boxplotDisplay() == "Net Annual Average", "annualAverage",
                         ifelse(boxplotDisplay() == "Net Annual Minimum", "annualMinimum",
                                ifelse(boxplotDisplay() == "Net Annual Maximum", "annualMaximum",
                                       ifelse(boxplotDisplay() == "Net Annual Total", "annualTotal", NA))))
    
    mmYears <- ifelse(mmSupplyType() == "All Years", paste0(statFilter, ""), paste0(statFilter, "LowSupply"))
    
    
    data <- data %>%
      filter((PI == "mmArea" & statType == mmYears) | (PI != "mmArea" & statType == statFilter))
    
    data
    
  })
  
  candidatePolicyPlots <- reactive({
    
    plt <- spatialPlotData()
    polLevels <- polLevels()
    
    plt <- plt %>%
      filter(`PI Location` != "Aggregate") %>%
      group_by(PI) %>%
      mutate(NormScore = (Value - min(Value)) / (max(Value) - min(Value))) %>%
      ungroup() %>%
      mutate(`PI Name` = factor(`PI Name`, levels = piLevels$`PI Name`),
             # Policy = factor(Policy, levels = c("Plan 2014 Baseline", unique(plt$Policy)[which(unique(plt$Policy) != "Plan 2014 Baseline")])),
             Lookup = factor(Lookup, levels = polLevels),
             Dataset = case_when(str_detect(SOW, "Historic") ~ "Historic",
                                 str_detect(SOW, "Stochastic") ~ "Stochastic",
                                 str_detect(SOW, "ssp") ~ "Climate Scenario",
                                 TRUE ~ "NA"),
             Dataset = factor(Dataset, levels = c("Historic", "Stochastic", "Climate Scenario"))) %>%
      arrange(desc(Dataset))
    
    ggplot(data = plt, aes(x = `PI Name`, y = NormScore, color = Lookup)) +
      facet_wrap(~ `Individual Group`, scales = "free", ncol = 1) +
      geom_boxplot(outlier.shape = NA) +
      geom_point(aes(group = Lookup, fill = Dataset, shape = Dataset, alpha = Dataset), position = position_jitterdodge(jitter.width = 0.3)) +
      theme_bw() +
      scale_shape_manual(values = c(21, 21, 24)) +
      scale_alpha_manual(values = c(1.0, 0.3, 0.3)) +
      scale_fill_manual(values = c("black", "gray", "gray")) +
      scale_color_manual(values = c(first(reds), getBluePal(length(unique(plt$Lookup)) - 1))) +
      ylab("Normalized Score (Better Performance = Higher Scores)") +
      theme(text = element_text(family = "Arial", color = "black", size = 18),
            title = element_blank(),
            axis.title.x = element_blank(),
            axis.text = element_text(size = 16),
            legend.position = "top",
            legend.title = element_blank(),
            legend.box = "vertical", 
            legend.margin = ggplot2::margin()) +
      scale_x_discrete(labels = function(x) str_wrap(str_replace_all(x, "pf" , " "), width = 12))
    
  })
  
  output$candidatePolicyPlots <- renderPlot({
    if(length(candidatePolicies()) == 0 || is.na(candidatePolicies())) return()
    candidatePolicyPlots()
  })
  
  output$candidatePolicyDownload <- downloadHandler(
    filename = function() { paste(input$candidatePolicyName, input$candidatePolicyType, sep = ".") },
    content = function(file) {
      if (input$candidatePolicyType == "pdf") {
        args <- list(file, width = input$candidatePolicyWidth, height = input$candidatePolicyHeight)
      } else {
        args <- list(file, width = input$candidatePolicyWidth, height = input$candidatePolicyHeight, units = input$candidatePolicyUnits, res = input$candidatePolicyRes)
      }
      do.call(input$candidatePolicyType, args)
      sprint(candidatePolicyPlots())
      dev.off()
    }
  )
  
  output$reevaluationTable <- renderDataTable({
    
    if(length(candidatePolicies()) == 0 || is.na(candidatePolicies())) return()
    
    tmp <- spatialPlotData() %>%
      select(searchID, Lookup, SOW, PI, Value)
    
    tmp
  },
  options = list(
    scrollX = TRUE,
    scrollY = TRUE,
    sDom  = '<"top">rt<"bottom">ip',
    width = 1000
  ),
  rownames = FALSE,
  filter = list(position = 'bottom'))
  
  # ---
  # impact zones
  # ---
  
  impactzoneData <- reactive({
    
    if(length(candidatePolicies()) == 0 || is.na(candidatePolicies())) return()
    
    filterCrit <- filterCrit()
    runData <- runData()
    
    data <- impactZones %>%
      inner_join(filterCrit, ., by = c("Lead-Time", "Skill", "Policy")) %>%
      filter(if (runData != "All SOW Traces") str_detect(SOW, runData) else TRUE) %>%
      pivot_longer(cols = -c(searchID, Lookup, `Lead-Time`, Skill, Policy, SOW, impactZone), names_to = "Impact Category", values_to = "Frequency")
    
  })
  
  impactzonePlot <- reactive({
    
    if(length(candidatePolicies()) == 0 || is.na(candidatePolicies())) return()
    
    plt <- impactzoneData()
    polLevels <- polLevels()
    
    plt <- plt %>%
      mutate(impactZone = factor(impactZone, levels = unique(impactZonesContext$`Impact Location`)),
             `Impact Category` = factor(`Impact Category`, levels = c("Extreme", "Severe", "Major", "Moderate", "Low Concern")),
             # Policy = factor(Policy, levels = c("Plan 2014 Baseline", unique(plt$Policy)[which(unique(plt$Policy) != "Plan 2014 Baseline")])),
             Lookup = factor(Lookup, levels = polLevels),
             Dataset = case_when(str_detect(SOW, "Historic") ~ "Historic",
                                 str_detect(SOW, "Stochastic") ~ "Stochastic",
                                 str_detect(SOW, "ssp") ~ "Climate Scenario",
                                 TRUE ~ "NA"),
             Dataset = factor(Dataset, levels = c("Historic", "Stochastic", "Climate Scenario"))) %>%
      arrange(desc(Dataset))
    
    ggplot(data = plt, aes(x = `Impact Category`, y = Frequency, color = Lookup)) +
      facet_wrap(~ impactZone, ncol = 2, scales = "free") +
      geom_point(aes(group = Lookup, fill = Dataset, shape = Dataset, alpha = Dataset), position = position_jitterdodge(jitter.width = 0.3)) +
      geom_boxplot(outlier.shape = NA, fill = NA) +
      theme_bw() +
      scale_shape_manual(values = c(21, 21, 24)) +
      scale_alpha_manual(values = c(1.0, 0.3, 0.3)) +
      scale_fill_manual(values = c("black", "gray", "gray")) +
      scale_color_manual(values = c(first(reds), getBluePal(length(unique(plt$Lookup)) - 1))) +
      scale_y_continuous(breaks = c(0.01, 0.1, 1, 5, 10, 25, 50, 100)) +
      coord_trans(y = 'log10') +
      ylab("% of QMs in Category (Log)") +
      theme(text = element_text(family = "Arial", color = "black", size = 18),
            title = element_blank(),
            axis.title.x = element_blank(),
            axis.text = element_text(size = 16),
            legend.position = "top",
            legend.title = element_blank(),
            legend.box = "vertical", 
            legend.margin = ggplot2::margin()) +
      scale_x_discrete(labels = function(x) str_wrap(str_replace_all(x, "pf" , " "), width = 5))
    
  })
  
  output$impactzonePlot <- renderPlot({
    impactzonePlot()
  })
  
  output$impactzoneDownload <- downloadHandler(
    filename = function() { paste(input$impactzoneName, input$impactzoneType, sep = ".") },
    content = function(file) {
      if (input$impactzoneType == "pdf") {
        args <- list(file, width = input$impactzoneWidth, height = input$impactzoneHeight)
      } else {
        args <- list(file, width = input$impactzoneWidth, height = input$impactzoneHeight, units = input$impactzoneUnits, res = input$impactzoneRes)
      }
      do.call(input$impactzoneType, args)
      print(impactzonePlot())
      dev.off()
    }
  )
  
  output$impactZoneDescription <- renderDataTable({
    impactZonesContext %>%
      filter(Category == "Context") %>%
      select(`Impact Location`, contains("Narrative"))
  },
  options = list(
    columnDefs = list(list(width = '10px', targets = c(0)), list(width = '250px', targets = c(1, 2, 3, 4))),
    scrollX = TRUE,
    scrollY = TRUE,
    paging = TRUE,
    width = 1000,
    sDom  = '<"top">rt<"bottom">ip'
  ), rownames = FALSE)
  
  output$impactZoneTable <- renderDataTable({
    impactZonesContext %>%
      filter(Category != "Context")
  },
  options = list(
    scrollX = TRUE,
    scrollY = TRUE,
    paging = TRUE,
    width = 1000,
    sDom  = '<"top">rt<"bottom">ip'
  ), rownames = FALSE)
  
  # ---
  # deviations
  # ---
  
  # H1 CRITERIA
  h1Data <- reactive({
    
    if(length(candidatePolicies()) == 0 || is.na(candidatePolicies())) return()
    
    filterCrit <- filterCrit()
    
    tmp <- h1 %>%
      inner_join(filterCrit, ., by = c("Lead-Time", "Skill", "Policy")) %>%
      group_by(Lookup) %>%
      mutate(`Policy Performance` = case_when(all(Performance == "Pass") ~ "Pass", TRUE ~ "Fail")) %>%
      ungroup() %>%
      mutate(`Policy Performance` = paste0(Lookup, "\n(", `Policy Performance`, ")")) %>%
      select(`Water Level Bin (m)`, `Plan 2014 Exceedances`, `Policy Performance`, `Simulated Exceedances`) %>%
      pivot_wider(id_cols = c(`Water Level Bin (m)`, `Plan 2014 Exceedances`), names_from = `Policy Performance`, values_from = `Simulated Exceedances`) %>%
      rename("Criteria Exceedance" = "Plan 2014 Exceedances") %>%
      select(`Water Level Bin (m)`, `Criteria Exceedance`, contains("Plan 2014"), everything())
    
    tmp
    
  })
  
  h1Table <- reactive({
    
    htab <- h1Data()
    reactable(htab, theme = hTableTheme, # columns = colDefs,
              # compact = TRUE, 
              pagination = FALSE, highlight = FALSE, striped = FALSE, sortable = FALSE, wrap = TRUE)
    
  })
  
  output$h1Table <- renderReactable({
    
    if(length(candidatePolicies()) == 0 || is.na(candidatePolicies())) return()
    h1Table()
      
  })
  
  output$h1TableDownload <- downloadHandler(
    filename = "h1Table.pdf",
    content = function(file) {
      html <- "h1Table.html"
      saveWidget(h1Table(), html)
      webshot(html, file)
    }
  )
  
  # H2 CRITERIA
  h2Data <- reactive({
    
    if(length(candidatePolicies()) == 0 || is.na(candidatePolicies())) return()
    
    filterCrit <- filterCrit()
    
    tmp <- h2 %>%
      inner_join(filterCrit, ., by = c("Lead-Time", "Skill", "Policy")) %>%
      # filter(Policy != "Plan 2014 Baseline") %>%
      group_by(Lookup) %>%
      mutate(`Policy Performance` = case_when(all(Performance == "Pass") ~ "Pass", TRUE ~ "Fail")) %>%
      ungroup() %>%
      mutate(`Policy Performance` = paste0(Lookup, "\n(", `Policy Performance`, ")")) %>%
      select(`Water Level Bin (m)`, `Plan 2014 Exceedances`, `Policy Performance`, `Simulated Exceedances`) %>%
      pivot_wider(id_cols = c(`Water Level Bin (m)`, `Plan 2014 Exceedances`), names_from = `Policy Performance`, values_from = `Simulated Exceedances`) %>%
      rename("Criteria Exceedance" = "Plan 2014 Exceedances") %>%
      select(`Water Level Bin (m)`, `Criteria Exceedance`, contains("Plan 2014"), everything())
    
    tmp
    
  })
  
  h2Table <- reactive({
    
    htab <- h2Data()
    reactable(htab, theme = hTableTheme, # columns = colDefs,
              # compact = TRUE, 
              pagination = FALSE, highlight = FALSE, striped = FALSE, sortable = FALSE, wrap = TRUE)
    
  })
  
  output$h2Table <- renderReactable({
    
    if(length(candidatePolicies()) == 0 || is.na(candidatePolicies())) return()
    h2Table()
    
  })
  
  output$h2TableDownload <- downloadHandler(
    filename = "h2Table.pdf",
    content = function(file) {
      html <- "h2Table.html"
      saveWidget(h2Table(), html)
      webshot(html, file)
    }
  )
  
  # H3 CRITERIA
  h3Data <- reactive({
    
    if(length(candidatePolicies()) == 0 || is.na(candidatePolicies())) return()
    
    filterCrit <- filterCrit()
    
    tmp <- h3 %>%
      inner_join(filterCrit, ., by = c("Lead-Time", "Skill", "Policy")) %>%
      # filter(Policy != "Plan 2014 Baseline") %>%
      group_by(Lookup) %>%
      mutate(`Policy Performance` = case_when(all(Performance == "Pass") ~ "Pass", TRUE ~ "Fail")) %>%
      ungroup() %>%
      mutate(`Policy Performance` = paste0(Lookup, "\n(", `Policy Performance`, ")")) %>%
      select(`Water Level Bin (m)`, `Plan 2014 Exceedances`, `Policy Performance`, `Simulated Exceedances`) %>%
      pivot_wider(id_cols = c(`Water Level Bin (m)`, `Plan 2014 Exceedances`), names_from = `Policy Performance`, values_from = `Simulated Exceedances`) %>%
      rename("Criteria Exceedance" = "Plan 2014 Exceedances") %>%
      select(`Water Level Bin (m)`, `Criteria Exceedance`, contains("Plan 2014"), everything())
    
    
    tmp
    
  })
  
  h3Table <- reactive({
    
    htab <- h3Data()
    reactable(htab, theme = hTableTheme, # columns = colDefs,
              # compact = TRUE, 
              pagination = FALSE, highlight = FALSE, striped = FALSE, sortable = FALSE, wrap = TRUE)
    
  })
  
  output$h3Table <- renderReactable({
    
    if(length(candidatePolicies()) == 0 || is.na(candidatePolicies())) return()
    h3Table()
    
  })
  
  output$h3TableDownload <- downloadHandler(
    filename = "h3Table.pdf",
    content = function(file) {
      html <- "h3Table.html"
      saveWidget(h3Table(), html)
      webshot(html, file)
    }
  )
  
  # H4 CRITERIA
  h4Data <- reactive({
    
    if(length(candidatePolicies()) == 0 || is.na(candidatePolicies())) return()
    
    filterCrit <- filterCrit()
    
    tmp <- h4 %>%
      inner_join(filterCrit, ., by = c("Lead-Time", "Skill", "Policy")) %>%
      replace(is.na(.), 0) %>%
      group_by(Lookup) %>%
      mutate(# Text = paste("Pass:", Pass, "\nFail:", Fail),
        Text = paste(Fail, "/", as.character(Pass + Fail)),
        `Policy Performance` = case_when(all(Fail == 0) ~ "Pass", TRUE ~ "Fail")) %>%
      ungroup() %>%
      mutate(Lookup = paste0(Lookup, "\n(", `Policy Performance`, ")")) %>%
      select(Lookup, Month, Text) %>%
      pivot_wider(id_cols = Month, names_from = Lookup, values_from = Text) %>%
      select(Month, contains("Plan 2014"), everything())
    
    
    tmp
    
  })
  
  h4Table <- reactive({
    
    htab <- h4Data()
    reactable(htab, theme = hTableTheme, # columns = colDefs,
              # compact = TRUE, 
              pagination = FALSE, highlight = FALSE, striped = FALSE, sortable = FALSE, wrap = TRUE)
    
  })
  
  output$h4Table <- renderReactable({
    
    if(length(candidatePolicies()) == 0 || is.na(candidatePolicies())) return()
    h4Table()
    
  })
  
  output$h4TableDownload <- downloadHandler(
    filename = "h4Table.pdf",
    content = function(file) {
      html <- "h4Table.html"
      saveWidget(h4Table(), html)
      webshot(html, file)
    }
  )
  
  # H6 CRITERIA
  h6Data <- reactive({
    
    if(length(candidatePolicies()) == 0 || is.na(candidatePolicies())) return()
    
    filterCrit <- filterCrit()
    
    tmp <- h6 %>%
      inner_join(filterCrit, ., by = c("Lead-Time", "Skill", "Policy")) %>%
      replace(is.na(.), 0) %>%
      group_by(Lookup) %>%
      mutate(Text = paste(Fail, "/", as.character(Pass + Fail)),
             `Policy Performance` = case_when(all(Fail == 0) ~ "Pass", TRUE ~ "Fail")) %>%
      ungroup() %>%
      mutate(Lookup = paste0(Lookup, "\n(", `Policy Performance`, ")")) %>%
      select(Lookup, Month, Text) %>%
      pivot_wider(id_cols = Month, names_from = Lookup, values_from = Text) %>%
      select(Month, contains("Plan 2014"), everything())
    
    tmp
    
  })
  
  h6Table <- reactive({
    
    htab <- h6Data()
    reactable(htab, theme = hTableTheme, # columns = colDefs,
              # compact = TRUE, 
              pagination = FALSE, highlight = FALSE, striped = FALSE, sortable = FALSE, wrap = TRUE)
    
  })
  
  output$h6Table <- renderReactable({
    
    if(length(candidatePolicies()) == 0 || is.na(candidatePolicies())) return()
    h6Table()
    
  })
  
  output$h6TableDownload <- downloadHandler(
    filename = "h6Table.pdf",
    content = function(file) {
      html <- "h6Table.html"
      saveWidget(h6Table(), html)
      webshot(html, file)
    }
  )
  
  # H7 CRITERIA
  h7Data <- reactive({
    
    if(length(candidatePolicies()) == 0 || is.na(candidatePolicies())) return()
    
    filterCrit <- filterCrit()
    
    tmp <- h7 %>%
      inner_join(filterCrit, ., by = c("Lead-Time", "Skill", "Policy")) %>%
      replace(is.na(.), 0) %>%
      group_by(Lookup) %>%
      mutate(Text = paste(Fail, "/", as.character(Pass + Fail)),
             `Policy Performance` = case_when(all(Fail == 0) ~ "Pass", TRUE ~ "Fail")) %>%
      ungroup() %>%
      mutate(Lookup = paste0(Lookup, "\n(", `Policy Performance`, ")")) %>%
      select(Lookup, Month, Text) %>%
      pivot_wider(id_cols = Month, names_from = Lookup, values_from = Text) %>%
      select(Month, contains("Plan 2014"), everything())
    
    tmp
    
  })
  
  h7Table <- reactive({
    
    htab <- h7Data()
    reactable(htab, theme = hTableTheme, # columns = colDefs,
              Compact = TRUE, 
              pagination = FALSE, highlight = FALSE, striped = FALSE, sortable = FALSE, wrap = TRUE)
    
  })
  
  output$h7Table <- renderReactable({
    
    if(length(candidatePolicies()) == 0 || is.na(candidatePolicies())) return()
    h7Table()
    
  })
  
  output$h7TableDownload <- downloadHandler(
    filename = "h7Table.pdf",
    content = function(file) {
      html <- "h7Table.html"
      saveWidget(h7Table(), html)
      webshot(html, file)
    }
  )
  
  # H CRITERIA OVERVIEW
  hTable <- reactive({
    
    h1Data <- h1Data()
    h2Data <- h2Data()
    h3Data <- h3Data()
    h4Data <- h4Data()
    h6Data <- h6Data()
    h7Data <- h7Data()
    
    # htab <- data.frame('x' = 1:2, "y" = 3:4)
    # reactable(htab)
    
    htab <- data.frame("Criteria" = c("H1", "H2", "H3", "H4", "H6", "H7"))
    htab[1, unlist(lapply(str_split(colnames(h1Data)[str_detect(colnames(h1Data), "Pass|Fail")], "\n"), "[[", 1))] <- str_remove_all(unlist(lapply(str_split(colnames(h1Data)[str_detect(colnames(h1Data), "Pass|Fail")], "\n"), "[[", 2)), "[()]")
    htab[2, unlist(lapply(str_split(colnames(h2Data)[str_detect(colnames(h2Data), "Pass|Fail")], "\n"), "[[", 1))] <- str_remove_all(unlist(lapply(str_split(colnames(h2Data)[str_detect(colnames(h2Data), "Pass|Fail")], "\n"), "[[", 2)), "[()]")
    htab[3, unlist(lapply(str_split(colnames(h3Data)[str_detect(colnames(h3Data), "Pass|Fail")], "\n"), "[[", 1))] <- str_remove_all(unlist(lapply(str_split(colnames(h3Data)[str_detect(colnames(h3Data), "Pass|Fail")], "\n"), "[[", 2)), "[()]")
    htab[4, unlist(lapply(str_split(colnames(h4Data)[str_detect(colnames(h4Data), "Pass|Fail")], "\n"), "[[", 1))] <- str_remove_all(unlist(lapply(str_split(colnames(h4Data)[str_detect(colnames(h4Data), "Pass|Fail")], "\n"), "[[", 2)), "[()]")
    htab[5, unlist(lapply(str_split(colnames(h6Data)[str_detect(colnames(h6Data), "Pass|Fail")], "\n"), "[[", 1))] <- str_remove_all(unlist(lapply(str_split(colnames(h6Data)[str_detect(colnames(h6Data), "Pass|Fail")], "\n"), "[[", 2)), "[()]")
    htab[6, unlist(lapply(str_split(colnames(h7Data)[str_detect(colnames(h7Data), "Pass|Fail")], "\n"), "[[", 1))] <- str_remove_all(unlist(lapply(str_split(colnames(h7Data)[str_detect(colnames(h7Data), "Pass|Fail")], "\n"), "[[", 2)), "[()]")

    colDefs <- vector("list", ncol(htab))
    colDefs[[1]] <- colDef(align = "center", maxWidth = 75)
    for (i in 2:ncol(htab)) {
      colDefs[[i]] <- colDef(
        cell = function(value) {
          color <- switch(
            value,
            Pass = first(blues),
            Fail = first(reds),
          )
          badge <- status_badge(color = color)
          tagList(badge, value)
        }
      )
    }
    names(colDefs) <- colnames(htab)

    reactable(htab, theme = hTableTheme, columns = colDefs,
              pagination = FALSE, highlight = FALSE, striped = FALSE, sortable = FALSE, wrap = TRUE)

  })
  
  output$hTable <- renderReactable({
    
    if(length(candidatePolicies()) == 0 || is.na(candidatePolicies())) return()
    hTable()

  })
  
  output$hTableDownload <- downloadHandler(
    filename = "hTable.pdf",
    content = function(file) {
      html <- "hTable.html"
      saveWidget(hTable(), html, title = "title")
      webshot(html, file)
    }
  )
  
  h14Plot <- reactive({
    
    if(length(candidatePolicies()) == 0 || is.na(candidatePolicies())) return()
    
    filterCrit <- filterCrit()
    
    tmp <- h14 %>%
      inner_join(filterCrit, ., by = c("Lead-Time", "Skill", "Policy")) %>%
      pivot_longer(cols = -c(searchID, Lookup, `Lead-Time`, Skill, Policy, QM, `High Threshold (m)`, `Low Threshold (m)`), names_to = "Condition", values_to = "Count") %>%
      group_by(Lookup, QM) %>%
      mutate(Freq = Count / sum(Count)) %>%
      ungroup() %>%
      mutate(Condition = factor(Condition, levels = rev(c("2014 Applied - Okay", "58DD Applied - Okay", "2014 Applied - High", "58DD Applied - Still High", "2014 Applied - Low", "58DD Applied - Still Low"))))
    
    ggplot(data = tmp, aes(x = QM, y = Freq, fill = Condition)) +
      facet_wrap(~ Lookup, ncol = 2, scales = "free") +
      geom_col() +
      theme_bw() +
      scale_fill_manual(values = c(getBluePal(2), getRedPal(2), "orange", yellow)) +
      scale_x_continuous(breaks = seq(1, 48, by = 4), limits = c(1, 48)) +
      scale_y_continuous(labels = scales::percent_format()) + 
      xlab("Quarter-Month") +
      ylab("Frequency of Quarter-Months") +
      theme(text = element_text(family = "Arial", color = "black", size = 18),
            title = element_blank(),
            axis.title = element_text(size = 18),
            axis.text.x = element_text(size = 16),
            legend.title = element_blank(),
            legend.position = "top",
            legend.text = element_text(size = 15),
            legend.box = "vertical",
            legend.margin = ggplot2::margin())
    
  })
  
  output$h14Plot <- renderPlot({
    h14Plot()
  })
  
  output$h14PlotDownload <- downloadHandler(
    filename = function() { paste(input$h14PlotName, input$h14PlotType, sep = ".") },
    content = function(file) {
      if (input$h14PlotType == "pdf") {
        args <- list(file, width = input$h14PlotWidth, height = input$h14PlotHeight)
      } else {
        args <- list(file, width = input$h14PlotWidth, height = input$h14PlotHeight, units = input$h14PlotUnits, res = input$h14PlotRes)
      }
      do.call(input$h14PlotType, args)
      print(h14Plot())
      dev.off()
    }
  )
  
  # ---
  # water level statistics
  # ---
  
  summaryStatistic <- reactive({input$summaryStatistic})
  
  summaryData <- reactive({
    
    filterCrit <- filterCrit()
    runData <- runData()
    
    data <- hydroStats %>%
      inner_join(filterCrit, ., by = c("Lead-Time", "Skill", "Policy")) %>%
      filter(if (runData != "All SOW Traces") str_detect(SOW, runData) else TRUE)
    
    statFilter <- ifelse(summaryStatistic() == "Monthly Mean", "monthlyMean",
                         ifelse(summaryStatistic() == "Monthly Minimum", "monthlyMin",
                                ifelse(summaryStatistic() == "Monthly Maximum", "monthlyMax", NA)))
    
    data <- data %>%
      filter(statType == statFilter) %>%
      mutate(Month = month.name[Month],
             Month = factor(Month, levels = month.name)) %>%
      # pivot_longer(cols = c(ontFlow, ontLevel, ptclaireLevel), names_to = "Variable", values_to = "Value") %>%
      mutate(Variable = case_when(Variable == "ontFlow" ~ "Lake Ontario Release (10*cms)",
                                  Variable == "ontLevel" ~ "Lake Ontario Water Level (m)",
                                  Variable == "ptclaireLevel" ~ "Pointe-Claire Water Level (m)",
                                  TRUE ~ "NA"))
    
    data
    
  })
  
  waterLevelStatsPlot <- reactive({
    
    if(length(candidatePolicies()) == 0 || is.na(candidatePolicies())) return()
    
    sumstat <- summaryStatistic()
    plt <- summaryData()
    polLevels <- polLevels()
    
    plt <- plt %>%
      mutate(# Policy = factor(Policy, levels = c("Plan 2014 Baseline", unique(plt$Policy)[which(unique(plt$Policy) != "Plan 2014 Baseline")])),
        Lookup = factor(Lookup, levels = polLevels),
        Dataset = case_when(str_detect(SOW, "Historic") ~ "Historic",
                            str_detect(SOW, "Stochastic") ~ "Stochastic",
                            str_detect(SOW, "ssp") ~ "Climate Scenario",
                            TRUE ~ "NA"),
        Dataset = factor(Dataset, levels = c("Historic", "Stochastic", "Climate Scenario"))) %>%
      arrange(desc(Dataset))
    
    ggplot(data = plt, aes(x = Month, y = Value, color = Lookup)) +
      facet_wrap(~ Variable, ncol = 1, scales = "free") +
      geom_boxplot(outlier.shape = NA) +
      geom_point(aes(group = Lookup, fill = Dataset, shape = Dataset, alpha = Dataset), position = position_jitterdodge(jitter.width = 0.3)) +
      scale_shape_manual(values = c(21, 21, 24)) +
      scale_alpha_manual(values = c(1.0, 0.3, 0.3)) +
      scale_fill_manual(values = c("black", "gray", "gray")) +
      scale_color_manual(values = c(first(reds), getBluePal(length(unique(plt$Lookup)) - 1))) +
      theme_bw() +
      ylab("Monthly Summary Statistic Value\n") +
      theme(text = element_text(family = "Arial", color = "black", size = 18),
            axis.title.x = element_blank(),
            axis.text = element_text(size = 16),
            legend.position = "top",
            legend.title = element_blank(),
            legend.box = "vertical", 
            legend.margin = ggplot2::margin())
    
  })
  
  output$waterLevelStatsPlot <- renderPlot({
    waterLevelStatsPlot()
  })
  
  output$waterLevelStatsPlotDownload <- downloadHandler(
    filename = function() { paste(input$waterLevelStatsPlotName, input$waterLevelStatsPlotType, sep = ".") },
    content = function(file) {
      if (input$waterLevelStatsPlotType == "pdf") {
        args <- list(file, width = input$waterLevelStatsPlotWidth, height = input$waterLevelStatsPlotHeight)
      } else {
        args <- list(file, width = input$waterLevelStatsPlotWidth, height = input$waterLevelStatsPlotHeight, units = input$waterLevelStatsPlotUnits, res = input$waterLevelStatsPlotRes)
      }
      do.call(input$waterLevelStatsPlotType, args)
      print(waterLevelStatsPlot())
      dev.off()
    }
  )
  
  # ---
  # time series
  # ---
  
  tsDataInput <- reactive({
    tolower(input$tsDataInput)
  })
  
  tsVarInput <- reactive({
    input$tsVarInput
  })
  
  tsTimeInput <- reactive({
    
    tmp <- c(2017, 2019)
    tmp
    
  })
  
  tsData <- reactive({
    
    filterCrit <- filterCrit()
    tsDataInput <- tsDataInput()

    fileLookup <- paretoOverall %>%
      filter(searchID %in% filterCrit$searchID) %>%
      select(searchID, fn, Policy)
    
    ts <- list()
  
    # load in individual time series to avoid bogging down load in time
    for (i in 1:nrow(fileLookup)) {
      
      tmpDir <- as.character(fileLookup[i, "fn"])
      tmpName <- as.character(fileLookup[i, "Policy"])
      
      tmpList <- list.files(paste0("../data/", tmpDir, "/simulation"), pattern = tmpName, recursive = TRUE)
      tmpList <- tmpList[str_detect(tmpList, tsDataInput)]
      
      output <- list()
      
      for (j in 1:length(tmpList)) {
      
      tmp <- read_parquet(paste0("../data/", tmpDir, "/simulation/", tmpList[j])) %>%
        mutate(sim = tmpList[j])
      output[[j]] <- tmp
      
      }
      
      ts[[i]] <- bind_rows(output) %>%
        mutate(fn = tmpDir, 
               Policy = tmpName, 
               searchID = as.integer(fileLookup[i, "searchID"]))
    
    }
    
    output <- bind_rows(ts)
    
    # read in baseline data
    tmpList <- list.files(paste0("../data/baseline/simulation"), pattern = "Plan_2014", recursive = TRUE)
    tmpList <- tmpList[str_detect(tmpList, tsDataInput)]
    bs <- list()
    for (j in 1:length(tmpList)) {
      
      tmp <- read_parquet(paste0("../data/baseline/simulation/", tmpList[j])) %>%
        mutate(sim = tmpList[j])
      bs[[j]] <- tmp
      
    }

    bs <- bind_rows(bs) %>%
      mutate(fn = "baseline", 
             Policy = "Plan 2014 Baseline", 
             searchID = 0)
    
    rbind(bs, output)
    
  })
  
  tsPlot <- reactive({
    
    filterCrit <- filterCrit()
    polLevels <- polLevels()
    tsData <- tsData()
    tsVarInput <- tsVarInput()
    tsTimeInput <- tsTimeInput()
    
    plt <- tsData %>%
      left_join(., filterCrit, by = c("searchID", "Policy")) %>%
      select(Lookup, searchID, Sim, Year, Month, QM, all_of(tsVarInput)) %>%
      filter(Year >= min(tsTimeInput) & Year <= max(tsTimeInput)) %>%
      pivot_longer(cols = -c(Lookup, searchID, Sim, Year, Month, QM), names_to = "Variable", values_to = "Value") %>%
      mutate(Lookup = factor(Lookup, levels = polLevels))
    
    simBreak <- seq(min(plt$Sim), max(plt$Sim) + 48, by = 48)
    yrBreak <-  seq(min(plt$Year), max(plt$Year) + 1, by = 1)
    
    ggplot(data = plt, aes(x = Sim, y = Value, color = Lookup)) +
      facet_wrap(~ Variable, ncol = 1, scales = "free") +
      geom_line() +
      scale_color_manual(values = c(first(reds), getBluePal(length(unique(plt$Lookup)) - 1))) +
      scale_x_continuous(breaks = simBreak, labels = yrBreak) +
      theme_bw() +
      theme(text = element_text(family = "Arial", color = "black", size = 18),
            axis.title = element_blank(),
            axis.text = element_text(size = 16),
            legend.position = "top",
            legend.title = element_blank(),
            legend.box = "vertical", 
            legend.margin = ggplot2::margin())
    
  })
  
  output$timeSeriesPlot <- renderPlot({
    tsPlot()
  })
  
  output$timeSeriesPlotDownload <- downloadHandler(
    filename = function() { paste(input$timeSeriesPlotName, input$timeSeriesPlotType, sep = ".") },
    content = function(file) {
      if (input$timeSeriesPlotType == "pdf") {
        args <- list(file, width = input$timeSeriesPlotWidth, height = input$timeSeriesPlotHeight)
      } else {
        args <- list(file, width = input$timeSeriesPlotWidth, height = input$timeSeriesPlotHeight, units = input$timeSeriesPlotUnits, res = input$timeSeriesPlotRes)
      }
      do.call(input$timeSeriesPlotType, args)
      print(timeSeriesPlot())
      dev.off()
    }
  )
  
  session$onSessionEnded(function() {
    stopApp()
  })
  
}

shinyApp(ui, server)

