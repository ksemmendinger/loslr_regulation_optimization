rm(list=ls())
gc()

# load libraries
library(tidyverse)

options(scipen = 999)
options(dplyr.summarise.inform = FALSE)

args <- commandArgs(trailingOnly = TRUE)
# args <- c("mac_loc", "12month", "0", "50000", "14")

loc <- args[1]
leadtime <- args[2]
skill <- args[3]
nfe <- as.numeric(args[4])
nvars <- as.numeric(args[5])

# experiment name for directory
folderName <- paste0(leadtime, "_", skill, "_", nfe, "nfe_", nvars, "dvs")

# set working directory
if (args[1] == "mac_loc") { 
  wd <- "/Users/kylasemmendinger/Box/Plan_2014/optimization/output"
}
setwd(paste0(wd, "/data/", folderName))

# names of objectives
pis <- c("Coastal Impacts: Upstream Buildings Impacted (#)", "Coastal Impacts: Downstream Buildings Impacted (#)", "Commercial Navigation: Ontario + Seaway + Montreal Transportation Costs ($)", "Hydropower: Moses-Saunders + Niagara Energy Value ($)", "Meadow Marsh: Area (ha)", "Recreational Boating: Impact Costs ($)")

# plotting color palette
blues <- c("#00429d", "#3761ab", "#5681b9", "#73a2c6", "#93c4d2", "#b9e5dd")
getBluePal <- colorRampPalette(blues)
yellow <- "#EECC66"
reds <- rev(c("#ffd3bf", "#ffa59e", "#f4777f", "#dd4c65", "#be214d", "#93003a"))
getRedPal <- colorRampPalette(reds)
fullPal <- c(blues, rev(reds))
getPal <- colorRampPalette(fullPal)

# -----------------------------------------------------------------------------
# load data
# -----------------------------------------------------------------------------

# load data
factorRanking <- read.csv("postAnalysis/scenarioDiscovery/dynamicFactorRanking.txt", check.names = FALSE, sep = "\t")
robustDynamic <- read.csv("postAnalysis/scenarioDiscovery/dynamicRobustness.txt", check.names = FALSE, sep = "\t")
robustStatic <- read.csv("postAnalysis/scenarioDiscovery/staticRobustness.txt", check.names = FALSE, sep = "\t")
exoHydro <- read.csv("postAnalysis/scenarioDiscovery/exogenousHydro.txt", check.names = FALSE, sep = "\t")

output <- list()
labels <- list()
count <- 1

# make plots
plans <- unique(robustDynamic$Policy)
for (p in plans) {
  
  # filter objective by plan
  obj <- robustDynamic %>%
    filter(Policy == p) %>% 
    # select(-Policy) %>%
    pivot_longer(cols = all_of(pis), names_to = "PI", values_to = "Robust Score") %>%
    select(Policy, SOW, PI, `Robust Score`)
  
  # get top two factors for each plan
  hydro <- factorRanking %>%
    filter(Policy == p) %>% 
    # select(-Policy) %>%
    pivot_longer(cols = - c(Policy, PI), names_to = "Variable", values_to = "Value") %>% 
    mutate(Value = Value * 100) %>%
    arrange(desc(Value)) %>% 
    group_by(PI) %>%
    slice(1:2)
  
  x <- hydro %>%
    slice(1) %>%
    setNames(c("Policy", "PI", "X Variable", "X Importance")) %>%
    ungroup()
  
  y <- hydro %>%
    slice(-1) %>%
    setNames(c("Policy", "PI", "Y Variable", "Y Importance")) %>%
    ungroup()
  
  featureImportance <- full_join(x, y, by = c("Policy", "PI"))
  
  for (i in 1:length(pis)) {
    
    poi <- pis[i]
    
    xVar <- featureImportance %>%
      filter(PI == poi) %>%
      select(`X Variable`) %>%
      deframe()
    
    yVar <- featureImportance %>%
      filter(PI == poi) %>%
      select(`Y Variable`) %>%
      deframe()
    
    tmp <- exoHydro %>%
      filter(Policy == p) %>%
      select(Policy, SOW, xVar, yVar) %>%
      setNames(c("Policy", "SOW", "X", "Y"))
    
    tmp2 <- obj %>%
      filter(PI == poi) %>%
      left_join(., tmp, by = c("Policy", "SOW"))
    
    output[[count]] <- tmp2
    
    tmpLabel <- featureImportance %>%
      mutate(Label = paste0("X: ", `X Variable`, " (", round(`X Importance`, 2), "%)", "\nY: ", `Y Variable`, " (", round(`Y Importance`, 2), "%)"),
             Policy = p) %>%
      select(Policy, PI, Label)
    
    labels[[count]] <- tmpLabel
      
    count <- count + 1
    
  }
  
}

pltLabels <- bind_rows(labels)

data <- bind_rows(output) %>%
  mutate(`SOW Group` = case_when(
           str_detect(SOW, "Historic") ~ "Historic",
           str_detect(SOW, "Stochastic") ~ "Stochastic",
           str_detect(SOW, "ssp") ~ "Climate Scenario",
           TRUE ~ "NA"),
         Robust = case_when(`Robust Score` == 1 ~ "Robust",
                            `Robust Score` == 0 ~ "Fails",
                            TRUE ~ "NA"),
         Policy = factor(Policy, levels = c("Plan 2014", as.character(plans[plans != "Plan 2014"]))),
         PI = factor(PI, levels = pis)) %>%
  left_join(., pltLabels, by = c("Policy", "PI"))

# # plot
# plt <- ggplot(data = data, aes(x = X, y = Y, fill = Robust)) +
#   ggh4x::facet_grid2(rows = vars(PI), cols = vars(Policy), scales = "free", independent = "all",
#                      labeller = label_wrap_gen(width = 30, multi_line = TRUE)) +
#   geom_point(size = 1, color = "gray", shape = 21, data = ~subset(., (`SOW Group` == "Stochastic"))) + 
#   geom_point(size = 1, color = "gray", shape = 23, data = ~subset(., (`SOW Group` == "Climate Scenario"))) +   
#   geom_point(size = 5, color = "gray", shape = 24, data = ~subset(., (`SOW Group` == "Historic"))) +
#   geom_text(aes(label = Label), x = -Inf, y = Inf, hjust = 0, vjust = 1) +
#   theme_bw() +
#   scale_fill_manual(values = getPal(2)) +
#   theme(text = element_text(family = "Arial", color = "black", size = 18),
#         title = element_blank(),
#         axis.title = element_blank(),
#         axis.text.y = element_text(size = 12),
#         axis.text.x = element_text(size = 12),
#         legend.position = "bottom",
#         legend.title = element_blank())
# 
# png("postAnalysis/scenarioDiscovery.png",
#     res = 330, width = 18, height = 22, units = "in")
# plt
# dev.off()

# plot
for (i in 1:length(pis)) {
  
  plt <- ggplot(data = data %>% filter(PI == pis[i]), aes(x = X, y = Y, fill = Robust)) +
    facet_wrap(~ Policy, scales = "free", nrow = 2) + 
    # ggh4x::facet_grid2(rows = vars(PI), cols = vars(Policy), scales = "free", independent = "all",
    #                    labeller = label_wrap_gen(width = 30, multi_line = TRUE)) +
    geom_point(size = 2, stroke = 0.1, alpha = 0.9, color = "black", shape = 21, data = ~subset(., (`SOW Group` == "Stochastic"))) + 
    geom_point(size = 2, stroke = 0.1, alpha = 0.9, color = "black", shape = 23, data = ~subset(., (`SOW Group` == "Climate Scenario"))) +   
    geom_point(size = 5, stroke = 1, alpha = 0.9, color = "black", shape = 24, data = ~subset(., (`SOW Group` == "Historic"))) +
    geom_text(aes(label = Label), x = -Inf, y = Inf, hjust = - 0.1, vjust = 1.2, size = 2) +
    theme_bw() +
    scale_fill_manual(values = c(reds[1], blues[5])) +
    scale_x_continuous(labels = function(x) format(x, scientific = TRUE), guide = guide_axis(n.dodge=2)) + 
    scale_y_continuous(labels = function(x) format(x, scientific = TRUE)) + 
    theme(text = element_text(family = "Arial", color = "black", size = 18),
          title = element_blank(),
          axis.title = element_blank(),
          # axis.text.y = element_text(size = 12),
          # axis.text.x = element_text(size = 12),
          legend.position = "bottom",
          legend.title = element_blank())
  
  png(paste0("postAnalysis/scenarioDiscovery/plots/", pis[i], ".png"),
      res = 330, width = 11, height = 8.5, units = "in")
  print(plt)
  dev.off()
  
}
