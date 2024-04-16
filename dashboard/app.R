# -----------------------------------------------------------------------------
# script setup
# -----------------------------------------------------------------------------

print("... setting up script ...")

# set working directory
# setwd("/Volumes/ky_backup/dps")
setwd("/Users/kylasemmendinger/Library/CloudStorage/GoogleDrive-kylasr@umich.edu/My Drive/loslrRegulation")
# 
# # clean up
# rm(list=ls())
# gc()

# load libraries
library(shiny)
library(shinyWidgets)
library(shinycssloaders)
library(DT)
library(RcppTOML)
library(tidyverse)
library(gridExtra)
library(paletteer)

# hide warnings to keep console clean
options(dplyr.summarise.inform = FALSE)

# color-blind friendly palette [blue, yellow, red]
blues <- c("#00429d", "#3761ab", "#5681b9", "#73a2c6", "#93c4d2", "#b9e5dd")
getBluePal <- colorRampPalette(blues)
yellow <- "#EECC66"
reds <- rev(c("#ffd3bf", "#ffa59e", "#f4777f", "#dd4c65", "#be214d", "#93003a"))
getRedPal <- colorRampPalette(reds)
fullPal <- c(blues, yellow, rev(reds))
getPal <- colorRampPalette(fullPal)
getRBPal <- colorRampPalette(c(blues, rev(reds)))

# plot themes
ggtheme <- 
  theme_bw() +
  theme(
    title = element_blank(),
    text = element_text(family = "Arial", color = "black", size = 18),
    strip.text = element_text(size = 20),
    axis.title.x = element_text(size = 20),
    axis.title.y = element_text(size = 20),
    axis.text.x = element_text(size = 18),
    axis.text.y = element_text(size = 18, angle = 90, hjust = 0.5),
    legend.text = element_text(size = 18),
    legend.position = "bottom", 
    legend.title = element_blank(), 
    legend.margin = ggplot2::margin())

# load variable names
varNames <- read.csv("dashboard/varNames.csv")

linebreaks <- function(n){HTML(strrep(br(), n))}

# -----------------------------------------------------------------------------
# load pareto front data across experiments in output/data directory
# -----------------------------------------------------------------------------

print("... loading pareto front data ...")

# baseline data - all results are displayed as improvements over some baseline policy
baselinePolicies <- list.files("output/data/baseline")
baselinePolicies <- baselinePolicies[1]
baselineExperiment <- list()
for (i in 1:length(baselinePolicies)) {
  baselineExperiment[[baselinePolicies[i]]] <- parseTOML(paste0("output/data/baseline/", baselinePolicies, "/config.toml"))
}

# set up handles to database tables on app start
runInfo <- data.frame("fn" = grep("_", list.files("output/data"), value = TRUE)) 

# load configuration file and pareto front for each experiment
paretoByExperiment <- list()

for (j in 1:nrow(runInfo)) {
  
  configFile <- paste0("output/data/", runInfo[j, "fn"], "/config.toml")
  paretoFile <- paste0("output/data/", runInfo[j, "fn"], "/NonDominatedPolicies.txt")
  
  # only read for complete experiment runs
  if (file.exists(configFile) & file.exists(paretoFile)) {
    config <- parseTOML(configFile)
    pf <- data.table::fread(paretoFile)
    config[["paretoFront"]] <- pf
    paretoByExperiment[[runInfo[j, "fn"]]] <- config
    
  }
  
}

# -----------------------------------------------------------------------------
# ui
# -----------------------------------------------------------------------------

print("starting ui")

totalwidth <- 12
sidebarWidth <- 3
mainbarWidth <- totalwidth - sidebarWidth

sidebarStyle <- "background-color: #F5F5F5; border-radius: 8px; border-width: 0px; padding:20px"
mainbarStyle <- "background-color: #FFFFFF; border-radius: 8px; border-width: 0px; padding:20px"

ui <- fluidPage(
  
  # set theme for overall web app
  theme = shinythemes::shinytheme("yeti"),
  
  # create the main tabset
  navbarPage(
    
    "Optimization Dashboard",
    
    # -----------------------------------
    # parallel axis plot
    # -----------------------------------
    
    tabPanel(
      
      # first tab title
      "Exploration",
      sidebarLayout(
        sidebarPanel(

          style = sidebarStyle, 
          width = sidebarWidth,
          
          h3("Policy Information"),
          pickerInput(inputId = "expPol", label = h4("Experiment"), choices = names(paretoByExperiment), selected = NA, multiple = TRUE, options = list(`live-search` = TRUE, size = 5, `actions-box` = TRUE, `title` = "Select Policies for Plotting")),
          linebreaks(1),
          column(12, align = "center", offset = 0, actionButton("go", "Generate Parallel Axis Plot", icon("chart-line"), width="75%")),
          linebreaks(3),
          h4(textOutput("filterPols")),
          uiOutput("rangeOutput"),
          linebreaks(1),
          uiOutput("rangeUpdate"),
          linebreaks(3),
        ),
        
        mainPanel(
          
          width = mainbarWidth,
          style = mainbarStyle,
          
          fluidRow(
            column(12,
                   column(11, h3(textOutput("plotTitle"))),
                   column(1, dropdownButton(
                     linebreaks(1),
                     # plot settings
                     selectInput(inputId = "basePol", label = "Baseline Policy for Normalization", multiple = FALSE, choices = baselinePolicies, selected = first(baselinePolicies)),
                     selectInput(inputId = "plotPol", label = "Policies to Display", multiple = TRUE, choices = baselinePolicies, selected = first(baselinePolicies)),
                     selectInput(inputId = "labelUnits", label = "Plot Label Units", multiple = FALSE, choices = c("Percent Change from Baseline", "Original PI Units"), selected = "Percent Change from Baseline"),
                     selectInput(inputId = "filterTable", label = "Table Units", multiple = FALSE, choices = c("Percent Change from Baseline", "Original PI Units"), selected = "Percent Change from Baseline"),
                     linebreaks(1),
                     # save settings
                     h5("Save Settings"),
                     textInput(inputId = "filterPlotName", label = "Name", value = "parallelAxisPlot"),
                     textInput(inputId = "filterPlotType", label = "Kind", value = "png"),
                     numericInput(inputId = "filterPlotWidth", label = "Width", value = 17*1.5),
                     numericInput(inputId = "filterPlotHeight", label = "Height", value = 11*1.5),
                     textInput(inputId = "filterPlotUnits", label = "Units", value = "in"),
                     numericInput(inputId = "filterPlotRes", label = "Resolution", value = 330),
                     downloadButton(outputId = "filterPlotDownload", label = "Save Plot"),
                     linebreaks(1),
                     circle = TRUE, icon = icon("gear"), width = "300px", right = TRUE, margin = "20px",
                     tooltip = tooltipOptions(title = "Click to See Display Options", placement = "left")))
            )
            
          ),
          
          linebreaks(1),
          plotOutput("filterPlot", width = "100%", height = "900px", brush = brushOpts(id = "plotBrush", delay = 5000), hover = hoverOpts(id = "papHover")) %>% withSpinner(color = blues[3], proxy.height = 200),
          linebreaks(2),
          fluidRow(column(12, 
                   column(10, h3(textOutput("tableTitle"))), 
                   column(2, uiOutput("tableSave")))
          ),
          # h4("Table of Pareto Optimal Policy Performance"),
          DT::dataTableOutput("filteredTable") %>% withSpinner(color = blues[3], proxy.height = 200),
          linebreaks(1),
          
        )
      )
    ),
    
    # -----------------------------------
    # time series analysis
    # -----------------------------------
    
    tabPanel(
      
      # second tab title
      "Time Series",
      
      sidebarLayout(
        sidebarPanel(
          # side panel parameters
          style = sidebarStyle,
          width = sidebarWidth,
          h3("Policy Information"),
          selectInput(width = "100%", inputId = "policySelection", label = "Policy Selection", choices = c("Select from Table", "Select by searchID"), multiple = FALSE, selected = "Select from Table"),
          conditionalPanel("input.policySelection == 'Select by searchID'", textInput(inputId = "evalPoliciesManual", label = "Enter policies by searchID (separated with a comma):", placeholder = NULL, width = "100%")),
          conditionalPanel("input.policySelection == 'Select from Table'", pickerInput(inputId = "evalPolicies", label = "Policies to Evaluate", choices = NULL, multiple = TRUE,  width = "100%")), #, options = list(`actions-box` = TRUE))),
          linebreaks(1),
          column(12, align = "center", offset = 0, actionButton("load_data", "Load Data", icon("chart-line"), width = "75%")),
          linebreaks(3),
        ),
        mainPanel(
          width = mainbarWidth,
          style = mainbarStyle,
          h3("Summary Table"),
          DT::dataTableOutput("summaryTable") %>% withSpinner(color = blues[3], proxy.height = 200),
          # )
        )
      ),
      linebreaks(1),
      tabsetPanel(
        tabPanel(
          "Time Series",
          linebreaks(1),
          sidebarLayout(
            sidebarPanel(
              # side panel parameters
              style = sidebarStyle,
              width = sidebarWidth,
              h4("Time Series Inputs"),
              numericRangeInput("tsYears", "Years to Plot", value = c(NA, NA)),
              linebreaks(1),
              pickerInput("tsVars", "Variables to Plot", choices = NA, selected = NA, multiple = TRUE, options = list(`live-search` = TRUE, size = 5, `actions-box` = TRUE, `title` = "Select Variables for Plotting")),
              linebreaks(1),
              column(12, align = "center", offset = 0, actionButton("ts_go", "Generate Time Series Plots", icon("chart-line"), width="75%")),
              linebreaks(3),
            ),
            mainPanel(
              style = mainbarStyle,
              style = mainbarWidth,
              tabsetPanel(
                
                id = "tabsetPanelID",
                type = "tabs",
                
                tabPanel("Time Series",
                         br(),
                         uiOutput("tsPlot"),
                ),
                tabPanel("Spaghetti Plots",
                         br(),
                         uiOutput("spaghettiPlot"),
                         
                ),
                tabPanel("Box Plots",
                         br(),
                         fluidRow(
                           column(6, align = "center", offset = 0, pickerInput("boxPlotTime", "Time Scale for Boxplots", choices = c("Quarter-Month", "Month"), selected = "Month", multiple = FALSE)),
                           column(6, align = "center", offset = 0, conditionalPanel("input.boxPlotTime == 'Month'", pickerInput("boxPlotMetric", "Summary Metric for Boxplots", choices = c("Sum", "Mean", "Median", "Min", "Max"), selected = "Sum", multiple = FALSE)))
                         ),
                         br(),
                         uiOutput("boxPlots"),
                ),
                tabPanel("Difference from Baseline",
                         br(),
                         uiOutput("diffPlot"),
                ),
              )
            )
          )
        ),
        tabPanel(
          "Time Varying Sensitivity Analysis",
          linebreaks(1),
          br(),
          uiOutput("tvsaPlot")
          # sidebarLayout(
          #   sidebarPanel(
          #     style = sidebarStyle,
          #     width = sidebarWidth,
          #     h4("TVSA"),
          #   ),
          #   
          #   mainPanel(
          #     style = mainbarStyle,
          #     style = mainbarWidth,
          #     br(),
          #     uiOutput("tvsaPlot")
          #     
          #   )
          # )
        )
      )
    )
  )
)


# -----------------------------------------------------------------------------
# server
# -----------------------------------------------------------------------------

print("starting server")

server <- function(input, output, session) {
  
  # -----------------------------------
  # parallel axis plot
  # -----------------------------------
  
  # experiments to load pareto fronts - user specified
  expPol <- eventReactive(input$go, ignoreInit = TRUE, {
    input$expPol
  })
  
  # policies for normalization and plotting
  basePol <- reactive({
    assign(x = "basePol", value = input$basePol, envir = .GlobalEnv)
    input$basePol
  })
  plotPol <- reactive({
    assign(x = "plotPol", value = input$plotPol, envir = .GlobalEnv)
    input$plotPol
  })
  
  # condition to check whether or not to run app - must select experiment, plotting
  runCheck <- reactive({
    ind <- any(is.null(expPol()) | is.null(basePol()) | is.null(plotPol()))
    ind
  })
  
  # are the pis already normalized according to Plan 2014 performance?
  normPol <- reactive({
    
    expPol <- expPol()
    normPol <- str_detect(expPol, "percentDiff")
    normPol
    
  })
  
  # create sidebar widget for filtering criteria
  output$rangeOutput <- renderUI({
    
    if (runCheck() == TRUE) return(NULL)
    
    pis <- pis()
    basePol <- basePol()
    bline <- baselineExperiment[[basePol]]
    
    piInputs <- list()
    for (i in 1:length(pis)) {
      
      piInputs[[i]] <- numericRangeInput(
        inputId = paste0(tolower(bline$performanceIndicators$abbrv[i]), "Numeric"),
        label = h5(bline$performanceIndicators$piName[i]),
        value = c(bline$performanceIndicators$satisficingCriteria[i], 100)
      )
      
    }
    
    piInputs
    
  })
  
  # update sliding tickers with ranges
  observe({
    
    if (runCheck() == TRUE) return(NULL)
    
    pis <- pis()
    basePol <- basePol()
    data <- normalizedParetoFront()
    
    bline <- baselineExperiment[[basePol]]
    
    for (i in 1:length(pis)) {
      
      piName <- bline$performanceIndicators$piName[i]
      maxValue <- max(data[[piName]])
      varName <- paste0(tolower(bline$performanceIndicators$abbrv[i]), "Numeric")
      lowerBound <- bline$performanceIndicators$satisficingCriteria[i]
      updateNumericRangeInput(session, varName, value = c(lowerBound, maxValue))
      
    }
    
  })
  
  # create text for sliders
  output$filterPols <- renderText({
    
    if (runCheck() == TRUE) return(NULL)
    "Policy Filtering"
    
  })
  
  # create sidebar action to update filtering criteria
  output$rangeUpdate <- renderUI({
    
    if (runCheck() == TRUE) return(NULL)
    column(12, align = "center", offset = 0, actionButton("updateCrit", "Update Satisficing Criteria", icon("chart-line"), width="75%"))
    
  })
  
  # # create expression string to trigger eventReactive for filterBounds
  # abbrv <- reactive({
  #   basePol <- basePol()
  #   bline <- baselineExperiment[[basePol]]
  #   abbrv <- tolower(bline$performanceIndicators$abbrv)
  #   paste0("rep(", paste(paste0("input$", abbrv, "Numeric"), collapse = "|"), ")")
  # })
  
  # filtering criteria specified in side panel
  filterBounds <- eventReactive(
    # eval(parse(text = abbrv())), ignoreNULL = TRUE, ignoreInit = TRUE, {
    input$updateCrit, ignoreNULL = FALSE, ignoreInit = TRUE, {
    
    basePol <- basePol()
    bline <- baselineExperiment[[basePol]]
    pis <- bline$performanceIndicators$piName
    abbrv <- tolower(bline$performanceIndicators$abbrv)
    
    filterBounds <- list()
    
    for (i in 1:length(abbrv)) {
      varName <- paste0(abbrv[i], "Numeric")
      vals <- input[[varName]]
      tmp <- data.frame("PI" = pis[i],
                        "lowerB" = min(vals),
                        "upperB" = max(vals)
      )
      filterBounds[[i]] <- tmp
    }
    
    bind_rows(filterBounds)
    
  })
  
  # baseline policy for nomalization
  paretoBaseline <- reactive({
    
    if (runCheck() == TRUE) return(NULL)
    basePol <- basePol()
    bline <- baselineExperiment[[basePol]]
    paretoBaseline <- data.frame(bline$performanceIndicators) %>% select(piName, baselineValue) %>% mutate(Experiment = basePol) %>% pivot_wider(names_from = "piName", values_from = baselineValue)
    paretoBaseline
    
  })
  
  # performance indicators from baseline
  pis <- reactive({
    
    if (runCheck() == TRUE) return(NULL)
    basePol <- basePol()
    pis <- baselineExperiment[[basePol]][["performanceIndicators"]][["piName"]]
    assign(x = "pis", value = pis, envir = .GlobalEnv)
    pis
    
  })
  
  # minimum performance indicators
  minPIs <- reactive({  
    
    if (runCheck() == TRUE) return(NULL)
    basePol <- basePol()
    ind <- which(baselineExperiment[[basePol]][["performanceIndicators"]][["direction"]] == "min")
    minPIs <- baselineExperiment[[basePol]][["performanceIndicators"]][["piName"]][ind]
    assign(x = "minPIs", value = minPIs, envir = .GlobalEnv)
    minPIs
    
  })
  
  # minimum performance indicators
  maxPIs <- reactive({
    
    if (runCheck() == TRUE) return(NULL)
    basePol <- basePol()
    ind <- which(baselineExperiment[[basePol]][["performanceIndicators"]][["direction"]] == "max")
    maxPIs <- baselineExperiment[[basePol]][["performanceIndicators"]][["piName"]][ind]
    assign(x = "maxPIs", value = maxPIs, envir = .GlobalEnv)
    maxPIs
    
  })
  
  # get pareto front for experiments of interest and join with baseline performance
  paretoFront <- reactive({
    
    if (runCheck() == TRUE) return(NULL)
    pis <- pis()
    expPol <- expPol()
    paretoBaseline <- paretoBaseline()
    
    pf <- list()
    
    for (i in 1:length(expPol)) {
      
      tmpExp <- paretoByExperiment[[expPol[i]]]
      tmpPF <- tmpExp$paretoFront %>%
        mutate(.before = 1, Experiment = expPol[i]) %>%
        select(Experiment, ID, Seed, all_of(pis))
      
      pf[[i]] <- tmpPF
      
    }
    
    paretoFront <- bind_rows(pf) %>%
      mutate(plotID = 1:nrow(.), plotID = as.character(plotID)) %>%
      bind_rows(., paretoBaseline %>% mutate(plotID = Experiment))
    
    assign(x = "paretoFront", value = paretoFront, envir = .GlobalEnv)
    paretoFront
    
  })
  
  # noramlize by baseline policy
  normalizedParetoFront <- reactive({
    
    if (runCheck() == TRUE) return(NULL)
    pis <- pis()
    minPIs <- minPIs()
    maxPIs <- maxPIs()
    paretoFront <- paretoFront()
    expPol <- expPol()
    normPol <- normPol()
    
    if (any(normPol)) {
      
      # temp remove already normalized policies
      polInd <- expPol[which(normPol)]
      tmp <- paretoFront %>%
        filter(Experiment == polInd) %>%
        mutate(across(all_of(maxPIs), ~ .x * 1),
               across(all_of(minPIs), ~ .x * -1),
               across(all_of(pis), ~ round(.x, 2)))
      
      # filter out normalized policies and calculate % change from Bv7
      tmp2 <- paretoFront %>%
        filter(Experiment != polInd) %>%
        mutate(across(all_of(maxPIs), ~ (.x - last(.x)) / last(.x) * 100),
               across(all_of(minPIs), ~ (.x - last(.x)) / last(.x) * -100),
               across(all_of(pis), ~ round(.x, 2)))
      
      normalizedParetoFront <- rbind(tmp, tmp2)
      
    } else {
      
      # calculate % change from Bv7
      normalizedParetoFront <- paretoFront %>%
        mutate(across(all_of(maxPIs), ~ (.x - last(.x)) / last(.x) * 100),
               across(all_of(minPIs), ~ (.x - last(.x)) / last(.x) * -100),
               across(all_of(pis), ~ round(.x, 2)))
    }
    
    assign(x = "normalizedParetoFront", value = normalizedParetoFront, envir = .GlobalEnv)
    normalizedParetoFront
    
  })
  
  # policies based on input from ui (filtering or brushing/clicking)
  selectedPolicies <- reactive({
    
    if (runCheck() == TRUE) return(NULL)
    
    pis <- pis()
    basePol <- basePol()
    plotPol <- plotPol()
    normalizedParetoFront <- normalizedParetoFront()
    filterBounds <- filterBounds()
    
    if (!is.null(input$plotBrush)) {
      
      minmax <- normalizedParetoFront %>%
        pivot_longer(cols = all_of(pis), names_to = "PI", values_to = "Score") %>%
        group_by(PI) %>%
        mutate(Score = (Score - min(Score)) / (max(Score) - min(Score))) %>%
        ungroup(PI)
      
      tmp <- brushedPoints(minmax, input$plotBrush, allRows = FALSE) %>%
        select(plotID)
      
      selectedPolicies <- normalizedParetoFront %>% 
        mutate(.before = 1, 
               Scenario = case_when(
                 Experiment %in% plotPol ~ Experiment,
                 plotID %in% unique(tmp$plotID) ~ "Colored Policy", 
                 TRUE ~ "Set"))
      
    } else {
      
      selectedPolicies <- normalizedParetoFront %>%
        pivot_longer(cols = all_of(pis), names_to = "PI", values_to = "Score") %>%
        left_join(., filterBounds, by = "PI") %>%
        mutate(.before = 1,
               Scenario = case_when(
                 Experiment == basePol ~ basePol,
                 Experiment %in% plotPol ~ plotPol,
                 (Score >= lowerB) & (Score <= upperB) ~ "Colored Policy",
                 TRUE ~ "Set")) %>%
        group_by(plotID) %>%
        mutate(Scenario = ifelse(any(Scenario == "Set"), "Set", Scenario)) %>%
        select(-lowerB, -upperB) %>%
        pivot_wider(names_from = "PI", values_from = "Score")
      
    }
    assign(x = "selectedPolicies", value = selectedPolicies, envir = .GlobalEnv)
    selectedPolicies
    
  })
  
  # use selected tables from table on previous tab as which stochastic runs to load
  values <- reactiveValues()
  values$tableSelection <- NULL
  observeEvent(input$filteredTable_rows_selected, ignoreNULL = TRUE, {
    
    tableIDs <- input$filteredTable_rows_selected
    
    data <- selectedPolicies() %>%
      ungroup() %>%
      arrange(Scenario, plotID, Experiment, ID, Seed) %>%
      slice(as.numeric(tableIDs)) %>%
      select(plotID) %>%
      deframe()
    
    values$tableSelection <- data
    
    
  })
  
  # plot labels 
  plotLabels <- reactive({
    
    if (runCheck() == TRUE) return(NULL)
    pis <- pis()
    
    if (input$labelUnits == "Original PI Units") {
      
      data <- paretoFront() %>%
        mutate(across(all_of(pis), ~ (last(.x) - .x)), across(all_of(pis), ~ round(.x, 2)))
      
    } else if (input$labelUnits == "Percent Change from Baseline") {
      
      data <- normalizedParetoFront() %>%
        mutate(across(all_of(pis), ~ round(.x, 2)))
      
    }
    
    plotLabels <- data %>%
      pivot_longer(cols = - c(Experiment, ID, Seed, plotID), names_to = "PI", values_to = "Value") %>%
      group_by(PI) %>%
      summarise(Min = min(Value), Max = max(Value)) %>%
      pivot_longer(cols = - c(PI, PI), names_to = "Range", values_to = "Value")
    
    if (input$labelUnits == "Original PI Units") { 
      
      plotLabels <- plotLabels %>%
        mutate(Y = ifelse(Range == "Min", -0.05, 1.05),
               Value = formatC(abs(Value), format = "d", big.mark = ","),
               Value = ifelse(Range == "Min", paste("-", Value), paste("+", Value)))
      
    } else if (input$labelUnits == "Percent Change from Baseline") { 
      
      plotLabels <- plotLabels %>%
        mutate(Y = ifelse(Range == "Min", -0.05, 1.05),
               Value = ifelse(abs(Value) >= 1, round(Value, 0), Value),
               Value = ifelse(Range == "Min", paste("-", abs(Value), "%"), paste("+", abs(Value), "%")))
    }
    
    plotLabels <- plotLabels %>%
      mutate(PI = factor(PI, levels = pis))
    assign(x = "plotLabels", value = plotLabels, envir = .GlobalEnv)
    
    plotLabels
    
  })
  
  # plot that corresponds to sidebar filters
  filterPlot <- reactive({
    
    if (runCheck() == TRUE) return(NULL)
    pis <- pis()
    expPol <- expPol()
    plotPol <- plotPol()
    basePol <- basePol()
    plotLabels <- plotLabels()
    data <- selectedPolicies()
    tableSelection <- values$tableSelection
    
    # order for plotting selected baseline policies
    blinePols <- c(plotPol, basePol[-which(basePol == plotPol)])
    
    # create levels for plotting
    plottingLevels <- c(blinePols, "Selected Policy", "Colored Policy", "Set")
    
    # color palette
    cols <- c(getRedPal(length(blinePols)), yellow, getBluePal(length(expPol)), "gray")
    names(cols) <- c(blinePols, "Selected Policy", expPol, "Set")
    
    # min-max data by objective
    minmax <- data %>%
      pivot_longer(cols = all_of(pis), names_to = "PI", values_to = "Score") %>%
      group_by(PI) %>%
      mutate(Score = (Score - min(Score)) / (max(Score) - min(Score))) %>%
      ungroup(PI) %>%
      mutate(PI = factor(PI, levels = pis),
             plotCol = case_when(
               plotID %in% tableSelection ~ "Selected Policy", 
               Scenario %in% plotPol ~ Scenario, 
               Scenario == "Set" ~ Scenario, 
               TRUE ~ Experiment),
             Scenario = factor(Scenario, levels = plottingLevels),
             plotCol = factor(plotCol, levels = names(cols))) %>%
      arrange(Scenario)
    
    # plot
    plt <- ggplot(data = minmax, aes(x = PI, y = Score, group = plotID, color = plotCol)) +
      # geom_point(alpha = 0.5) +
      geom_path(size = 1, alpha = 0.25, data = ~subset(., plotCol == "Set")) +
      geom_path(size = 2, alpha = 0.75, data = ~subset(., (plotCol != "Set") & (plotCol != plotPol))) +
      geom_path(size = 2, data = ~subset(., plotCol == "Selected Policy")) +
      geom_path(size = 2, data = ~subset(., plotCol == plotPol)) +
      geom_label(data = plotLabels, aes(x = as.factor(PI), y = Y, label = Value), inherit.aes = FALSE, family = "Arial", size = 5) +
      theme_bw() +
      scale_color_manual(values = cols, limits = force) +
      scale_y_continuous(position = "right") +
      ylab("Min-Max Normalized Performance\n(Darkest Red Line = Baseline)\n ") +
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
      scale_x_discrete(breaks = pis, labels = function(x) str_wrap(str_replace_all(x, "pf" , " "), width = 15)) +
      guides(colour = guide_legend(nrow = length(expPol)))
    
    
    plt
    
  })
  
  output$filterPlot <- renderPlot({
    if (runCheck() == TRUE) return(NULL)
    filterPlot()
  })
  
  # download button
  output$filterPlotDownload <- downloadHandler(filename = function() { paste(input$filterPlotName, input$filterPlotType, sep = ".") }, content = function(file) {
    if (input$filterPlotType == "pdf") {
      args <- list(file, width = input$filterPlotWidth, height = input$filterPlotHeight)
    } else {
      args <- list(file, width = input$filterPlotWidth, height = input$filterPlotHeight, units = input$filterPlotUnits, res = input$filterPlotRes)
    }
    do.call(input$filterPlotType, args)
    print(filterPlot())
    dev.off()
  })
  
  outputTable <- reactive({
    
    if (runCheck() == TRUE) return(NULL)
    
    pis <- pis()
    selectedPolicies <- selectedPolicies()
    
    if (input$filterTable == "Percent Change from Baseline") {
      
      data <- selectedPolicies
      
    } else if (input$filterTable == "Original PI Units") {
      
      paretoFront <- paretoFront()
      data <- paretoFront %>%
        left_join(., selectedPolicies %>% select(Scenario, plotID, Experiment, ID, Seed),
                  by = c("plotID", "Experiment", "ID", "Seed"))
      
    }
    
    outputTable <- data %>%
      arrange(Scenario, plotID, Experiment, ID, Seed) %>%
      select(Scenario, Experiment, ID, Seed, plotID, all_of(pis))
    
    outputTable
    
  })
  
  output$plotTitle <- reactive({
    
    if (runCheck() == TRUE) return(NULL)
    
    data <- outputTable() 
    data <- data %>%
      filter(Scenario == "Colored Policy")
    
    n <- nrow(data)
    
    paste(n, "Policies Meet Filtering Criteria")
    
  })
  
  output$tableTitle <-  reactive({
    
    if (runCheck() == TRUE) return(NULL)
    paste0("Policy Performance (Displayed as: ", input$labelUnits, ")")
    
  })
  
  # download button for table
  output$tableSave <- renderUI({
    if (runCheck() == TRUE) return(NULL)
    actionButton("tableDownload", label = "Export Table")
  })
  
  scPols <- reactive({
    
    expPol <- expPol()
    selectedPolicies <- selectedPolicies()
    
    scPols <- list()
    
    for (i in 1:length(expPol)) {
      
      ids <- selectedPolicies %>%
        ungroup() %>%
        filter(Experiment == expPol[i]) %>%
        filter(Scenario == "Colored Policy") %>%
        select(ID) %>%
        deframe()
      
      expData <- paretoByExperiment[[expPol[i]]][["paretoFront"]]
      
      tmp <- expData %>%
        filter(ID %in% ids) %>%
        mutate(.before = 1, Experiment = expPol[i])
      
      scPols[[i]] <- tmp
      
    }
    
    bind_rows(scPols)
    
  })
  
  observeEvent(input$tableDownload, {
    
    pols <- expPol()
    scPols <- scPols()
    
    for (i in 1:length(pols)) {
      tmp <- scPols %>%
        filter(Experiment == pols[i]) %>%
        select(-Experiment)
      
      fn <- paste0(getwd(), "/output/data/", pols[i], "/satisficingPolicies.csv")
      write.csv(tmp, file = fn, row.names = FALSE)
      
      print(paste("saved", fn, "table"))
      
    }
  })
  
  # table that corresponds to policies
  output$filteredTable <- DT::renderDataTable(
    outputTable(), server = FALSE, rownames = FALSE, filter = list(position = 'bottom'), caption = 'Note: Hold shift and click to order by multiple columns.',
    options = list(dom = '<"top"f>t<"bottom"ip>', search = list(regex = TRUE, caseInsensitive = TRUE), scrollX = TRUE, scrollY = TRUE, 
                   paging = TRUE, pageLength = 20, lengthChange = FALSE, width = 1000, columnDefs = list(list(className = 'dt-center', targets = "_all")))
  )
  
  # -----------------------------------
  # time series analysis
  # -----------------------------------
  
  policySelection <- reactive({input$policySelection})
  
  # update policies to reevaluate based on table selection
  observeEvent(values$tableSelection, {
    if (policySelection() == "Select from Table") {
      updatePickerInput(session, "evalPolicies", choices = values$tableSelection, selected = values$tableSelection)
    }
  })
  
  # retrieve policies from user selection
  candidatePolicies <- reactive({
    
    if (is.null(input$evalPolicies) & is.null(input$evalPoliciesManual)) return()
    
    if (policySelection() == "Select from Table") {
      
      candidatePolicies <- as.numeric(input$evalPolicies)
      
    } else if (policySelection() == "Select by searchID") {
      
      candidatePolicies <- as.numeric(trimws(str_split(input$evalPoliciesManual, ",")[[1]]))
      
    }
    print(candidatePolicies)
    assign(x = "candidatePolicies", value = candidatePolicies, envir = .GlobalEnv)
    candidatePolicies
    
  })
  
  # indicator on whether or not to retreive data
  loadData <- eventReactive(input$load_data, ignoreInit = TRUE, {
    loadData <- TRUE
    loadData
  })
  
  # load in time series data - experiments
  expData <- reactive({
    
    if (is.null(loadData())) return(NULL)
    
    paretoFront <- paretoFront()
    candidatePolicies <- candidatePolicies()
    
    output <- list()
    for (i in 1:length(candidatePolicies)) {
      
      fn <- paretoFront %>%
        filter(plotID == candidatePolicies[i]) %>%
        select(Experiment, ID, plotID)
      
      # output[[i]] <- read.delim(paste0("output/data/", fn$Experiment,"/simulation/historic/id", fn$ID,"/piOutput.csv")) %>%
      #   mutate(.before = 1, Experiment = fn$Experiment, ID = fn$ID, plotID = fn$plotID)
      
      output[[i]] <- read.csv(paste0("output/data/", fn$Experiment,"/simulation/historic/id", fn$ID,"/sim.csv")) %>%
        mutate(.before = 1, Experiment = fn$Experiment, ID = fn$ID, plotID = fn$plotID)
      
    }
    
    expData <- bind_rows(output)
    expData
  })
  
  # load in time series data - baseline
  baseData <- reactive({
    
    if (is.null(loadData())) return(NULL)
    
    paretoFront <- paretoFront()
    plotPol <- plotPol()
    output <- list()
    for (i in 1:length(plotPol)) {
      
      plotID <- paretoFront %>%
        filter(Experiment == plotPol[i]) %>%
        select(plotID) %>%
        deframe()
      
      # output[[i]] <- read.delim(paste0("output/data/baseline/", plotPol[i], "/simulation/historic/", plotPol[i],"/piOutput.csv")) %>%
      #   mutate(.before = 1, Experiment = plotPol[i], ID = NA, plotID = plotID)
      
      output[[i]] <- read.csv(paste0("output/data/baseline/", plotPol[i], "/simulation/historic/", plotPol[i],"/sim.csv")) %>%
        mutate(.before = 1, Experiment = plotPol[i], ID = NA, plotID = plotID)
      
    }
    
    baseData <- bind_rows(output)
    baseData
  })
  
  output$summaryTable <- DT::renderDataTable({
    
    if (is.null(loadData())) return(NULL)
    
    outputTable <- outputTable()
    plotPol <- plotPol()
    tsColors <- tsColors()
    candidatePolicies <- candidatePolicies()
    
    summaryTable <- outputTable %>%
      filter(Experiment == plotPol | plotID %in% candidatePolicies) %>% 
      mutate(.before = 1, `Legend Color` = " ") %>%
      select(-Scenario)
    
    datatable(summaryTable, rownames = FALSE, selection = "none", 
              options = list(scrollX = TRUE, searching = FALSE, paging = FALSE, ordering = FALSE, info = FALSE, columnDefs = list(list(className = 'dt-center', targets = "_all")))) %>%
      formatStyle("Legend Color", "plotID", backgroundColor = styleEqual(names(tsColors), tsColors))
    
  })
  
  # join baseline and experiment for plotting
  tsData <- reactive({
    expData <- expData()
    baseData <- baseData()
    tsData <- bind_rows(baseData, expData) %>%
      select(Experiment, ID, plotID, varNames$varName) %>%
      setNames(c("Experiment", "ID", "plotID", varNames$varDescription)) %>%
      group_by(plotID) %>%
      filter(Year > 1899) %>% # filter out spinup year to match up timesteps
      mutate(.before = 5, Month = as.numeric(cut(`Quarter-Month`, breaks = seq(1, 49, by = 4), include.lowest = TRUE, right = FALSE))) %>%
      group_by(plotID) %>%
      arrange(Year, Month, `Quarter-Month`) %>%
      mutate(plotSim = row_number()) %>%
      ungroup()
    
    assign(x = "tsData", value = tsData, envir = .GlobalEnv)
    tsData
  })
  
  # update inputs based on loaded data
  observeEvent(tsData(), {
    
    tsData <- tsData()
    yrs <- tsData %>% select(Year) %>% unique()
    vars <- colnames(tsData)[!str_detect(colnames(tsData),paste(c("Sim", "Year", "QM", "Month", "Experiment", "ID", "plotID"), collapse= "|"))]
    updateNumericInput(session, "tsYears", value = c(min(yrs), max(yrs)))
    updatePickerInput(session, "tsVars", choices = vars)
    
  })
  
  # user specified inputs
  tsYears <- eventReactive(input$ts_go, {
    assign(x = "tsYears", value = input$tsYears, envir = .GlobalEnv)
    input$tsYears
  })
  tsVars <- eventReactive(input$ts_go, {
    assign(x = "tsVars", value = input$tsVars, envir = .GlobalEnv)
    input$tsVars
  })
  
  makePlot <- eventReactive(input$ts_go, ignoreInit = TRUE, {
    makePlot <- TRUE
    makePlot
    
  })
  
  # define color palette for time series plots
  tsColors <- reactive({
    
    if (is.null(loadData())) return(NULL)
    
    basePol <- basePol()
    plotPol <- plotPol()
    candidatePolicies <- candidatePolicies()
    
    # order for plotting selected baseline policies
    blinePols <- c(plotPol, basePol[-which(basePol == plotPol)])
    
    # color palette
    tsColors <- c(getRedPal(length(blinePols)), getBluePal(length(candidatePolicies)))
    names(tsColors) <- c(blinePols, candidatePolicies)
    assign(x = "tsColors", value = tsColors, envir = .GlobalEnv)
    tsColors
    
  })
  
  # make time series plots
  tsPlot <- reactive({
    
    if (is.null(makePlot())) return(NULL)
    basePol <- basePol()
    plotPol <- plotPol()
    tsData <- tsData()
    tsYears <- tsYears()
    tsVars <- tsVars()
    tsVars2 <- tsVars
    tsColors <- tsColors()
    candidatePolicies <- candidatePolicies()
    
    # order for plotting selected baseline policies
    blinePols <- c(plotPol, basePol[-which(basePol == plotPol)])
    
    # extract regime and remove from array
    reg <- "Flow Regime (RC or Limit)"
    if (reg %in% tsVars) {
      
      # extract flow regime of interest
      regime <- tsData %>%
        filter(Year >= min(tsYears) & Year <= max(tsYears)) %>%
        select(plotID, plotSim, Sim, Year, `Quarter-Month`, all_of(reg)) %>%
        pivot_longer(cols = all_of(reg), names_to = "Variable", values_to = "Value") %>%
        left_join(., varNames, by = c("Variable" = "varDescription")) %>%
        mutate(plotLabel = case_when(varUnits != "" ~ paste0(Variable, " (", varUnits, ")"), TRUE ~ Variable),
               Value = case_when(str_detect(Value, "RC") ~ "RF", Value == "" ~ NA_character_, TRUE ~ Value)) %>%
        drop_na()
      
      portrait <<- regime
      tsVars2 <- tsVars[-which(tsVars == reg)]
      
    }
    
    # filter by user specified inputs
    data <- tsData %>%
      filter(Year >= min(tsYears) & Year <= max(tsYears)) %>%
      select(plotID, plotSim, Sim, Year, `Quarter-Month`, all_of(tsVars2)) %>%
      pivot_longer(cols = all_of(tsVars2), names_to = "Variable", values_to = "Value") %>%
      left_join(., varNames, by = c("Variable" = "varDescription")) %>%
      mutate(plotLabel = case_when(varUnits != "" ~ paste0(Variable, " (", varUnits, ")"), TRUE ~ Variable)) %>%
      drop_na()
    
    # color palette
    cols <- tsColors
    
    nyears <- 6 # how many labels to display for any given time interval
    yrSeq <- seq(min(tsYears), max(tsYears), by = ceiling(diff(tsYears) / nyears))
    simSeq <- data %>% filter(Year %in% yrSeq) %>% group_by(Year) %>% summarise(x = min(plotSim)) %>% select(x) %>% deframe()
    
    plotList <- list()
    
    for (i in 1:length(tsVars)) {
      
      var <- tsVars[i]
      
      if (var == reg) {
        
        ruleLevels <- c("RF", "R+", unique(regime$Value)[-which(unique(regime$Value) %in% c("RF", "R+"))])
        ruleColors <- paletteer_d("ggthemes::Classic_20", n = length(ruleLevels))
        names(ruleColors) <- ruleLevels
        
        plotList[[i]] <- 
          ggplot(data = regime, aes(x = plotSim, y = plotID, fill = Value)) +
          facet_wrap(~ plotLabel, scales = "free", ncol = 1) +
          geom_tile(color = "white") +
          scale_fill_manual(values = ruleColors, na.value = NA) +
          guides(fill = guide_legend(nrow = 1)) +
          scale_x_continuous(breaks = simSeq, labels = yrSeq) +
          ylab("") +
          xlab("") +
          ggtheme
        
      } else {
        
        tmp <- data %>% 
          filter(Variable == var)
        
        plotList[[i]] <- ggplot(data = tmp, aes(x = plotSim, y = Value, color = plotID)) +
          facet_wrap(~ plotLabel, scales = "free", ncol = 1) +
          geom_line(size = 1.25, alpha = 0.75, linetype = "dashed") +
          scale_color_manual(values = cols) +
          scale_x_continuous(breaks = simSeq, labels = yrSeq) +
          ylab("") +
          xlab("") +
          ggtheme
        
      }
      
    }
    
    grid.arrange(grobs = plotList, ncol = 1)
    
  })
  
  # render time series plot in ui
  output$tsPlot <- renderUI({
    if (is.null(makePlot())) return(NULL)
    output$plt <-renderPlot({tsPlot()})
    height <- length(tsVars()) * 400
    plotOutput("plt", width = "100%", height = paste0(height, "px")) %>% withSpinner(color = blues[3], proxy.height = 200)
  })
  
  # make spaghetti plots
  spaPlot <- reactive({ts
    
    if (is.null(makePlot())) return(NULL)
    
    basePol <- basePol()
    plotPol <- plotPol()
    tsData <- tsData()
    tsYears <- tsYears()
    tsVars <- tsVars()
    tsVars2 <- tsVars
    candidatePolicies <- candidatePolicies()
    
    # order for plotting selected  policies
    blinePols <- c(plotPol, basePol[-which(basePol == plotPol)])
    policyLevels <- c(blinePols, candidatePolicies)
    
    # extract regime and remove from array
    reg <- "Flow Regime (RC or Limit)"
    if (reg %in% tsVars) {
      
      # extract flow regime of interest
      regime <- tsData %>%
        filter(Year >= min(tsYears) & Year <= max(tsYears)) %>%
        select(plotID, plotSim, Sim, Year, `Quarter-Month`, all_of(reg)) %>%
        pivot_longer(cols = all_of(reg), names_to = "Variable", values_to = "Value") %>%
        left_join(., varNames, by = c("Variable" = "varDescription")) %>%
        mutate(plotLabel = case_when(varUnits != "" ~ paste0(Variable, " (", varUnits, ")"), TRUE ~ Variable),
               Value = case_when(str_detect(Value, "RC") ~ "RF", Value == "" ~ NA_character_, TRUE ~ Value)) %>%
        drop_na() %>%
        group_by(`plotID`, `Quarter-Month`, Value) %>% 
        summarise(count = n()) %>%
        ungroup() %>%
        mutate(plotID = factor(plotID, levels = policyLevels))
      spaRegime <<- regime
      tsVars2 <- tsVars[-which(tsVars == reg)]
      
    }
    
    # filter by user specified inputs
    data <- tsData %>%
      filter(Year >= min(tsYears) & Year <= max(tsYears)) %>%
      select(plotID, plotSim, Sim, Year, `Quarter-Month`, all_of(tsVars2)) %>%
      pivot_longer(cols = all_of(tsVars2), names_to = "Variable", values_to = "Value") %>%
      left_join(., varNames, by = c("Variable" = "varDescription")) %>%
      mutate(plotID = factor(plotID, levels = policyLevels),
             plotLabel = case_when(varUnits != "" ~ paste0(Variable, " (", varUnits, ")"), TRUE ~ "")) %>%
      drop_na()
    
    # x axis labels and breaks
    qmSeq <- seq(1, 48, by = 4)
    monthSeq <- substr(month.abb, 1, 1)
    
    plotList <- list()
    
    for (i in 1:length(tsVars)) {
      
      var <- tsVars[i]
      
      if (var == reg) {
        
        ruleLevels <- c("RF", "R+", unique(regime$Value)[-which(unique(regime$Value) %in% c("RF", "R+"))])
        
        plotList[[i]] <-
          ggplot(data = regime, aes(x = `Quarter-Month`, y = Value, fill = count)) +
          facet_wrap(~ plotID, scales = "free", nrow = 1) +
          geom_tile(color = "white") +
          scale_fill_gradientn(colours = rev(reds)) +
          scale_y_discrete(breaks = ruleLevels) +
          scale_x_continuous(breaks = qmSeq, labels = monthSeq) +
          xlab("") +
          ylab(paste(var, "\n", " ")) +
          ggtheme +
          theme(axis.text.y = element_text(angle = 0),
                legend.key.width = unit(4, "cm"))
        
      } else {
        
        tmp <- data %>% 
          filter(Variable == var)
        
        name <- tmp %>%
          select(plotLabel) %>%
          unique() %>%
          deframe()
        
        plotList[[i]] <-
          ggplot(data = tmp, aes(x = `Quarter-Month`, y = Value, group = Year, color = Year)) +
          # facet_grid(cols = vars(plotID), rows = vars(plotLabel), axis.labels = "all") +
          facet_wrap(~ plotID,  scales = "free", nrow = 1) +
          geom_line(size = 1, alpha = 0.5, linetype = "solid") +
          scale_colour_gradientn(colours = rev(blues)) + 
          scale_x_continuous(breaks = qmSeq, labels = monthSeq) +
          scale_y_continuous(limits = c(range(tmp$Value))) +
          ggtitle(paste(name, "\n", " ")) +
          xlab("") +
          ylab("") +
          # ylab(paste(name, "\n", " ")) +
          ggtheme +
          theme(plot.title = element_text(hjust = 0.5),
                legend.key.width = unit(4, "cm"))
        
      }
      
    }
    
    grid.arrange(grobs = plotList, ncol = 1)
    
  })
  
  # render spaghetti plot in ui
  output$spaghettiPlot <- renderUI({
    if (is.null(makePlot())) return(NULL)
    output$plt1 <- renderPlot({spaPlot()})
    height <- length(tsVars()) * 400
    plotOutput("plt1", width = "100%", height = paste0(height, "px")) %>% withSpinner(color = blues[3], proxy.height = 200)
  })
  
  # get user-selected summary metrics
  sumTime <- reactive({input$boxPlotTime})
  sumMetric <- reactive({input$boxPlotMetric})
  
  # make box plots to view aggregated performance
  boxPlot <- reactive({
    
    if (is.null(makePlot())) return(NULL)
    
    basePol <- basePol()
    plotPol <- plotPol()
    tsData <- tsData()
    tsYears <- tsYears()
    tsColors <- tsColors()
    tsVars <- tsVars()
    tsVars2 <- tsVars
    sumTime <- sumTime()
    
    # if (sumTime == "Month") {
    sumMetric <- sumMetric()
    evalFun <- eval(parse(text = tolower(sumMetric)))
    # }
    candidatePolicies <- candidatePolicies()
    
    # order for plotting selected  policies
    blinePols <- c(plotPol, basePol[-which(basePol == plotPol)])
    policyLevels <- c(blinePols, candidatePolicies)
    
    # extract regime and remove from array
    reg <- "Flow Regime (RC or Limit)"
    if (reg %in% tsVars) {
      
      # extract flow regime of interest
      regime <- tsData %>%
        filter(Year >= min(tsYears) & Year <= max(tsYears)) %>%
        select(plotID, plotSim, Sim, Year, Month, `Quarter-Month`, all_of(reg)) %>%
        pivot_longer(cols = all_of(reg), names_to = "Variable", values_to = "Value") %>%
        left_join(., varNames, by = c("Variable" = "varDescription")) %>%
        mutate(plotLabel = case_when(varUnits != "" ~ paste0(Variable, " (", varUnits, ")"), TRUE ~ Variable),
               Value = case_when(str_detect(Value, "RC") ~ "RF", Value == "" ~ NA_character_, TRUE ~ Value)) %>%
        drop_na() %>%
        group_by(`plotID`, across(all_of(sumTime)), Value) %>% 
        summarise(count = n()) %>%
        ungroup() %>%
        mutate(plotID = factor(plotID, levels = policyLevels))
      tsVars2 <- tsVars[-which(tsVars == reg)]
      
    }
    
    # filter by user specified inputs
    data <- tsData %>%
      filter(Year >= min(tsYears) & Year <= max(tsYears)) %>%
      select(plotID, plotSim, Sim, Year, Month, `Quarter-Month`, all_of(tsVars2)) %>%
      pivot_longer(cols = all_of(tsVars2), names_to = "Variable", values_to = "Value") %>%
      group_by(plotID, Variable, Year, across(all_of(sumTime))) %>%
      summarize(Value = evalFun(Value, na.rm = TRUE)) %>%
      left_join(., varNames, by = c("Variable" = "varDescription")) %>%
      mutate(plotID = factor(plotID, levels = policyLevels),
             plotLabel = case_when(varUnits != "" ~ paste0(Variable, " (", varUnits, ")"), TRUE ~ "")) %>%
      drop_na()
    
    # x axis labels and breaks
    if (sumTime == "Month") {
      breaks <- seq(1, 12, by = 1)
    } else {
      breaks <- seq(1, 48, by = 4)
    }
    labels <- substr(month.abb, 1, 1)
    
    plotList <- list()
    
    for (i in 1:length(tsVars)) {
      
      var <- tsVars[i]
      
      if (var == reg) {
        
        ruleLevels <- c("RF", "R+", unique(regime$Value)[-which(unique(regime$Value) %in% c("RF", "R+"))])
        
        plotList[[i]] <-
          ggplot(data = regime, aes(x = .data[[sumTime]], y = Value, fill = count)) +
          facet_wrap(~ plotID, scales = "free", nrow = 1) +
          geom_tile(color = "white") +
          scale_fill_gradientn(colours = rev(reds)) +
          scale_y_discrete(breaks = ruleLevels) +
          scale_x_continuous(breaks = breaks, labels = labels) +
          xlab("") +
          ylab(paste(var, "\n", " ")) +
          ggtheme +
          theme(axis.text.y = element_text(angle = 0),
                legend.key.width = unit(4, "cm"))
        
      } else {
        
        tmp <- data %>% 
          filter(Variable == var)
        
        plotList[[i]] <-
          ggplot(data = tmp, aes(x = as.factor(.data[[sumTime]]), y = Value, color = plotID)) +
          facet_wrap(~ plotLabel,  scales = "free", nrow = 1) +
          geom_point(alpha = 0.75, position = position_jitterdodge()) +
          geom_boxplot(fill = NA) +
          scale_colour_manual(values = tsColors) +
          scale_x_discrete(breaks = breaks, labels = labels) +
          scale_y_continuous(limits = c(range(tmp$Value))) +
          xlab("") +
          ylab("") +
          ggtheme +
          theme(legend.key.width = unit(4, "cm"))
        
      }
      
    }
    
    grid.arrange(grobs = plotList, ncol = 1)
    
  })
  
  # render box plots in ui
  output$boxPlots <- renderUI({
    if (is.null(makePlot())) return(NULL)
    output$plt2 <- renderPlot({boxPlot()})
    height <- length(tsVars()) * 400
    plotOutput("plt2", width = "100%", height = paste0(height, "px")) %>% withSpinner(color = blues[3], proxy.height = 200)
  })
  
  # make difference time series plots
  diffPlot <- reactive({
    
    if (is.null(makePlot())) return(NULL)
    
    basePol <- basePol()
    plotPol <- plotPol()
    tsData <- tsData()
    tsYears <- tsYears()
    tsVars <- tsVars()
    tsVars2 <- tsVars
    tsColors <- tsColors()
    candidatePolicies <- candidatePolicies()
    
    # order for plotting selected baseline policies
    blinePols <- c(plotPol, basePol[-which(basePol == plotPol)])
    
    # extract regime and remove from array
    reg <- "Flow Regime (RC or Limit)"
    if (reg %in% tsVars) {
      
      # extract flow regime of interest
      regime <- tsData %>%
        filter(Year >= min(tsYears) & Year <= max(tsYears)) %>%
        select(plotID, plotSim, Sim, Year, `Quarter-Month`, all_of(reg)) %>%
        pivot_longer(cols = all_of(reg), names_to = "Variable", values_to = "Value") %>%
        left_join(., varNames, by = c("Variable" = "varDescription")) %>%
        mutate(plotLabel = case_when(varUnits != "" ~ paste0(Variable, " (", varUnits, ")"), TRUE ~ Variable),
               Value = case_when(str_detect(Value, "RC") ~ "RF", Value == "" ~ NA_character_, TRUE ~ Value)) %>%
        drop_na()
      
      portrait <<- regime
      tsVars2 <- tsVars[-which(tsVars == reg)]
      
    }
    
    # filter by user specified inputs
    data <- tsData %>%
      filter(Year >= min(tsYears) & Year <= max(tsYears)) %>%
      select(plotID, plotSim, Sim, Year, `Quarter-Month`, all_of(tsVars2)) %>%
      pivot_longer(cols = all_of(tsVars2), names_to = "Variable", values_to = "Value") %>%
      pivot_wider(id_cols = c(plotSim, Year, `Quarter-Month`, Variable), names_from = plotID, values_from = Value) %>%
      mutate(across(all_of(as.character(candidatePolicies)), ~ .x - get(basePol))) %>%
      mutate(across(all_of(basePol[-which(basePol == plotPol)]), ~ .x - get(basePol))) %>%
      mutate(across(all_of(plotPol), ~ .x - get(basePol))) %>%
      pivot_longer(cols = c(all_of(blinePols), all_of(as.character(candidatePolicies))), names_to = "plotID", values_to = "Value") %>%
      left_join(., varNames, by = c("Variable" = "varDescription")) %>%
      mutate(plotLabel = case_when(varUnits != "" ~ paste0(Variable, " (", varUnits, ")"), TRUE ~ Variable)) %>%
      drop_na()
    
    # color palette
    cols <- tsColors
    
    nyears <- 6 # how many labels to display for any given time interval
    yrSeq <- seq(min(tsYears), max(tsYears), by = ceiling(diff(tsYears) / nyears))
    simSeq <- data %>% filter(Year %in% yrSeq) %>% group_by(Year) %>% summarise(x = min(plotSim)) %>% select(x) %>% deframe()
    
    plotList <- list()
    
    for (i in 1:length(tsVars)) {
      
      var <- tsVars[i]
      
      if (var == reg) {
        
        ruleLevels <- c("RF", "R+", unique(regime$Value)[-which(unique(regime$Value) %in% c("RF", "R+"))])
        ruleColors <- paletteer_d("ggthemes::Classic_20", n = length(ruleLevels))
        names(ruleColors) <- ruleLevels
        
        plotList[[i]] <- 
          ggplot(data = regime, aes(x = plotSim, y = plotID, fill = Value)) +
          facet_wrap(~ plotLabel, scales = "free", ncol = 1) +
          geom_tile(color = "white") +
          scale_fill_manual(values = ruleColors, na.value = NA) +
          guides(fill = guide_legend(nrow = 1)) +
          scale_x_continuous(breaks = simSeq, labels = yrSeq) +
          ylab("") +
          xlab("") +
          ggtheme
        
      } else {
        
        tmp <- data %>% 
          filter(Variable == var)
        
        plotList[[i]] <- ggplot(data = tmp, aes(x = plotSim, y = Value, color = plotID)) +
          facet_wrap(~ plotLabel, scales = "free", ncol = 1) +
          geom_line(size = 1.25, alpha = 0.75, linetype = "dashed") +
          scale_color_manual(values = cols) +
          scale_x_continuous(breaks = simSeq, labels = yrSeq) +
          ylab("") +
          xlab("") +
          ggtheme
        
      }
      
    }
    
    grid.arrange(grobs = plotList, ncol = 1)
    
  })
  
  # render time series plot in ui
  output$diffPlot <- renderUI({
    if (is.null(makePlot())) return(NULL)
    output$plt3 <-renderPlot({diffPlot()})
    height <- length(tsVars()) * 400
    plotOutput("plt3", width = "100%", height = paste0(height, "px")) %>% withSpinner(color = blues[3], proxy.height = 200)
  })
  
  # -----------------------------------
  # time varying sensitivity analysis
  # -----------------------------------
  
  tvsaData <- reactive({
    
    if (is.null(loadData())) return(NULL)
    
    paretoFront <- paretoFront()
    candidatePolicies <- candidatePolicies()
    plotPol <- plotPol()
    
    # # baseline TVSA data -- only numerical TVSA
    # baseTVSA <- list()
    # for (i in 1:length(plotPol)) {
    # 
    #   plotID <- paretoFront %>%
    #     filter(Experiment == plotPol[i]) %>%
    #     select(plotID) %>%
    #     deframe()
    # 
    #   baseTVSA[[i]] <- read.csv(paste0("output/data/baseline/", plotPol[i], "/postAnalysis/", plotPol[i],"/numericalTVSA.csv")) %>%
    #     mutate(.before = 1, TVSA = "Numerical", Experiment = plotPol[i], ID = NA, plotID = plotID)
    # 
    # }
    # 
    # baseTVSA <- bind_rows(baseTVSA)
    
    anTVSA <- list()
    numTVSA <- list()
    for (i in 1:length(candidatePolicies)) {
      
      fn <- paretoFront %>%
        filter(plotID == candidatePolicies[i]) %>%
        select(Experiment, ID, plotID)
      
      anTVSA[[i]] <- read.csv(paste0("output/data/", fn$Experiment,"/postAnalysis/id", fn$ID,"/analyticalTVSA.csv")) %>%
        mutate(.before = 1, TVSA = "Analytical", Experiment = fn$Experiment, ID = fn$ID, plotID = fn$plotID)
      
      numTVSA[[i]] <- read.csv(paste0("output/data/", fn$Experiment,"/postAnalysis/id", fn$ID,"/numericalTVSA.csv")) %>%
        mutate(.before = 1, TVSA = "Numerical", Experiment = fn$Experiment, ID = fn$ID, plotID = fn$plotID)
      
    }
    
    # tvsaData <- bind_rows(baseTVSA, anTVSA, numTVSA)
    tvsaData <- bind_rows(anTVSA, numTVSA)
    assign(x = "tvsaData", value = tvsaData, envir = .GlobalEnv)
    tvsaData
    
  })
  
  # make time series plots
  tvsaPlot <- reactive({
    
    if (is.null(loadData())) return(NULL)
    tvsaData <- tvsaData()
    basePol <- basePol()
    plotPol <- plotPol()
    candidatePolicies <- candidatePolicies()
    
    # order for plotting selected baseline policies
    blinePols <- c(plotPol, basePol[-which(basePol == plotPol)])

    data <- tvsaData %>%
      select(TVSA, plotID, QM, totalVar, contains("S1"), contains("S2")) %>%
      pivot_longer(cols = -c("TVSA", "plotID", "QM", "totalVar"), names_to = "SI", values_to = "Value") %>%
      mutate(SI = case_when(
        str_detect(SI, "S2") & Value >= 0 ~ "+ Interactions",
        str_detect(SI, "S2") & Value < 0 ~ "- Interactions",
        TRUE ~ SI)) %>%
      group_by(TVSA, plotID, QM, SI) %>%
      summarise(qmAverage = abs(mean(Value, rm.na = TRUE))) %>%
      group_by(TVSA, plotID, QM) %>%
      mutate(totalVar = sum(qmAverage)) %>%
      ungroup() %>%
      mutate(qmNorm = qmAverage / totalVar) %>%
      mutate(plotID = factor(plotID, c(blinePols, candidatePolicies)))
    
    # x axis labels and breaks
    qmSeq <- seq(1, 48, by = 4)
    monthSeq <- substr(month.abb, 1, 1)
    
    ggplot(data = data, aes(x = QM, y = qmNorm, fill = SI)) +
      # facet_wrap(~ TVSA + plotID) +
      facet_grid(rows = vars(TVSA), cols = vars(plotID)) +
      geom_bar(position="stack", stat="identity") +
      scale_x_continuous(breaks = qmSeq, labels = monthSeq) +
      ylab("Portion of Variance") + 
      xlab("Quarter-Month") +
      ggtheme
      
  })
  
  # render time series plot in ui
  output$tvsaPlot <- renderUI({
    if (is.null(loadData())) return(NULL)
    output$tvsaplt <-renderPlot({tvsaPlot()})
    height <- 1000
    plotOutput("tvsaplt", width = "100%", height = paste0(height, "px")) %>% withSpinner(color = blues[3], proxy.height = 200)
  })
  
  # kill r command when browser closes
  session$onSessionEnded(function() {
    stopApp()
  })
  
}

shinyApp(ui, server)
