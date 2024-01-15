# -----------------------------------------------------------------------------
# script setup
# -----------------------------------------------------------------------------

print("... setting up script ...")

# set working directory
setwd("/Volumes/ky_backup/dps")

# # clean up
# rm(list=ls())
# gc()

# load libraries
library(shiny)
library(shinyWidgets)
library(shinycssloaders)
library(RcppTOML)
library(tidyverse)
library(DT)

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

# -----------------------------------------------------------------------------
# load pareto front data across experiments in output/data directory
# -----------------------------------------------------------------------------

print("... loading pareto front data ...")

# baseline data - all results are displayed as improvements over some baseline policy
baselinePolicies <- list.files("output/data/baseline")
# baselinePolicies <- baselinePolicies[baselinePolicies != "simulation"]
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

ui <- fluidPage(

  # set theme for overall web app
  theme = shinythemes::shinytheme("yeti"),
  
  # create the main tabset
  navbarPage(
    
    "Optimization Dashboard",
    
    tabPanel(
      
      # first tab title
      "Exploration",
      
      sidebarPanel(
    
        # side panel parameters
        style = "height: 95vh; overflow-y: auto; background-color: #F5F5F5; border-radius: 8px; border-width: 0px", 
        width = sidebarWidth,
        
        # side panel visuals
        h3("Policy Information"),
        pickerInput(
          inputId = "expPol", label = h4("Experiment"), choices = names(paretoByExperiment), selected = NA, multiple = TRUE,
          options = list(`live-search` = TRUE, size = 5, `actions-box` = TRUE, `title` = "Select Policies for Plotting")
        ),
        br(),
        column(12, align = "center", offset = 0, actionButton("go", "Generate Parallal Axis Plot", icon("chart-line"), width="66.7%")),
        br(),
        br(),
        br(),
        h4(textOutput("filterPols")),
        uiOutput("rangeOutput")
      ),
      
      mainPanel(
        
        # main panel parameters
        width = mainbarWidth,
        
        # main panel visuals
        fluidRow(
          column(12,
                 # column(11, h3("Parallel Axis Plot")),
                 column(11, h3(textOutput("plotTitle"))),
                 column(1, dropdownButton(
                   br(),
                   # plot settings
                   selectInput(inputId = "basePol", label = "Baseline Policy for Normalization", multiple = FALSE, choices = baselinePolicies, selected = first(baselinePolicies)),
                   selectInput(inputId = "plotPol", label = "Policies to Display", multiple = TRUE, choices = baselinePolicies, selected = first(baselinePolicies)),
                   selectInput(inputId = "labelUnits", label = "Plot Label Units", multiple = FALSE, choices = c("Percent Change from Baseline", "Original PI Units"), selected = "Percent Change from Baseline"),
                   selectInput(inputId = "filterTable", label = "Table Units", multiple = FALSE, choices = c("Percent Change from Baseline", "Original PI Units"), selected = "Percent Change from Baseline"),
                   br(),
                   # save settings
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
        
        br(),
        plotOutput("filterPlot", width = "100%", height = "1000px", brush = brushOpts(id = "plotBrush", delay = 5000)) %>% withSpinner(color = blues[3], proxy.height = 200),
        # uiOutput("filterPlot"),
        br(),
        
        br(),
        fluidRow(
          column(12,
                 column(10, h3(textOutput("tableTitle"))),
                 column(2, uiOutput("tableSave"))
          )
        ),
        # h4("Table of Pareto Optimal Policy Performance"),
        DT::dataTableOutput("filteredTable") %>% withSpinner(color = blues[3], proxy.height = 200),
        br(),
        
      )
      
    )
    
  )
  
)


# -----------------------------------------------------------------------------
# server
# -----------------------------------------------------------------------------

print("starting server")

server <- function(input, output, session) {
  
  # experiments to load pareto fronts - user specified
  expPol <- eventReactive(input$go, ignoreInit = TRUE, {
    input$expPol
  })
 
  # policies for normalization and plotting
  basePol <- reactive({input$basePol})
  plotPol <- reactive({input$plotPol})
  
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
  
  # create slider for sidebar
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
  
  # create expression string to trigger eventReactive for filterBounds
  abbrv <- reactive({
    basePol <- basePol()
    bline <- baselineExperiment[[basePol]]
    abbrv <- tolower(bline$performanceIndicators$abbrv)
    paste0("rep(", paste(paste0("input$", abbrv, "Numeric"), collapse = "|"), ")")
  })
  
  # filtering criteria specified in side panel
  filterBounds <- eventReactive(eval(parse(text = abbrv())), ignoreNULL = TRUE, ignoreInit = TRUE, {

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
    pis
    
  })
  
  # minimum performance indicators
  minPIs <- reactive({  
    
    if (runCheck() == TRUE) return(NULL)
    basePol <- basePol()
    ind <- which(baselineExperiment[[basePol]][["performanceIndicators"]][["direction"]] == "min")
    minPIs <- baselineExperiment[[basePol]][["performanceIndicators"]][["piName"]][ind]
    minPIs
    
  })
  
  # minimum performance indicators
  maxPIs <- reactive({
    
    if (runCheck() == TRUE) return(NULL)
    basePol <- basePol()
    ind <- which(baselineExperiment[[basePol]][["performanceIndicators"]][["direction"]] == "max")
    maxPIs <- baselineExperiment[[basePol]][["performanceIndicators"]][["piName"]][ind]
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
      bind_rows(., paretoBaseline) %>%
      mutate(plotID = 1:nrow(.))
    
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
    
    selectedPolicies
    
  })
  
  # use selected tables from table on previous tab as which stochastic runs to load
  values <- reactiveValues()
  values$tableSelection <- NULL
  observeEvent(input$filteredTable_rows_selected, ignoreNULL = TRUE, {
    
      tableIDs <- input$filteredTable_rows_selected
      print(tableIDs)

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
    
    plt
    
  })
  
  output$filterPlot <- renderPlot({
    if (runCheck() == TRUE) return(NULL)
    filterPlot()
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
      select(Scenario, Experiment, ID, Seed, all_of(pis), plotID)
    
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
    # if (length(expPol()) != 1) return(NULL)
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
  
  observeEvent(
    input$tableDownload, {
    
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
    }
    
  )
  
  # table that corresponds to policies
  output$filteredTable <- DT::renderDataTable(
    outputTable(),
    server = FALSE,
    rownames = FALSE,
    filter = list(position = 'bottom'),
    caption = 'Note: Hold shift and click to order by multiple columns.',
    options = list(
      dom = '<"top"f>t<"bottom"ip>',
      search = list(regex = TRUE, caseInsensitive = TRUE),
      scrollX = TRUE,
      scrollY = TRUE,
      paging = TRUE,
      pageLength = 20,
      lengthChange = FALSE,
      width = 1000
    )
  )
  
  # kill r command when browser closes
  session$onSessionEnded(function() {
    stopApp()
  })
  
}

shinyApp(ui, server)



