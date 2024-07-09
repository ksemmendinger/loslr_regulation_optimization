rm(list=ls())
gc()

options(scipen = 999)

# load libraries
library(tidyverse)
library(RcppTOML)

args <- commandArgs(trailingOnly = TRUE)
# args <-c(
#   "/Users/kylasemmendinger/Documents/github/loslr_regulation_optimization",
#   # "flowANN_onlyPhysicalLimits_offSepRule_netAnnualAverage_12month_sqLM_91dv_7obj_1900_2020_75000nfe",
#   "adjANN_Bv7_offSepRule_netAnnualAverage_6month_0_91dv_7obj_historic_75000nfe",
#   "5"
# )

# print(args)

# [1]: path to working directory
loc <- args[1]
setwd(loc)

# [2]: folder name of experiment
folderName <- args[2]

# [3]: number of seeds
seeds <- as.numeric(args[3])

# load configuration file
config <- parseTOML(paste0("output/data/", folderName, "/config.toml"))
# nfe <- as.numeric(config$optimizationParameters$nfe)
nfe <- as.numeric(config$optimizationParameters$nfe)

# create new folder for plots
dir.create(paste0("output/data/", folderName, "/moeaFramework/plots"), showWarnings = FALSE)

# colors for plotting seeds
seedPal <- c("#00429d", "#3761ab", "#5681b9", "#73a2c6", "#93c4d2", "#b9e5dd")
getSeedPal <- colorRampPalette(seedPal)
seedCol <- getSeedPal(seeds)

# colors for plotting baseline (removed: "#ffd3bf" from position 1)
basePal <- rev(c("#ffd3bf", "#ffa59e", "#f4777f", "#dd4c65", "#be214d", "#93003a"))
getBasePal <- colorRampPalette(basePal)
baseCol <- getBasePal(4)

# -----------------------------------------------------------------------------
# hypervolume & convergence plots
# -----------------------------------------------------------------------------

hyp <- list()

for (i in 1:seeds) {
  
  # load nfe frequency
  freq <- read.delim(paste0("output/data/", folderName, "/clean/runtime_S", i, ".txt"),
                     sep = ",", check.names = FALSE) %>%
    select(NFE) %>%
    unique() %>%
    deframe()
  
  # load runtime performance
  rt <- read.delim(paste0("output/data/", folderName, "/moeaFramework/metrics/runtime_S", i, ".metrics"), sep = " ") %>%
    setNames(c("Hypervolume", "Generational Distance", 
               "Inverted Generational Distance", "Spacing", 
               "Epsilon Indicator", "Maximum Pareto Front Error")) %>%
    mutate(NFE = freq, .before = 1)
  
  # load final performance
  final <- read.delim(paste0("output/data/", folderName, "/moeaFramework/metrics/final_S", i, ".metrics"), sep = " ") %>%
    setNames(c("Hypervolume", "Generational Distance", 
               "Inverted Generational Distance", "Spacing", 
               "Epsilon Indicator", "Maximum Pareto Front Error")) %>%
    mutate(NFE = nfe, .before = 1)
  
  # join data
  dyn <- rbind(rt, final) %>%
    mutate(Seed = paste("Seed", i), .before = 1)
  
  hyp[[i]] <- dyn
  
}

dyn <- bind_rows(hyp) %>%
  pivot_longer(cols = - c(Seed, NFE), 
               names_to = "Metric", values_to = "Value")

plt <- ggplot(data = dyn, aes(x = NFE, y = Value, color = as.factor(Seed))) + 
  geom_line(size = 1.5) + 
  facet_wrap(~ Metric, scales = "free", ncol = 2) +
  theme_bw() + 
  scale_color_manual(values = seedCol) +
  ggtitle("Borg Performance Metrics") +
  ylab("Metric Value") +
  theme(text = element_text(family = "Times", color = "black", size = 30),
        axis.title.x = element_blank(),
        legend.title = element_blank(),
        legend.position = "bottom",
        legend.text = element_text(size = 25)) +
  guides(color = guide_legend(nrow = 1, override.aes = list(size = 1.5)))

png(paste0("output/data/", folderName, "/moeaFramework/plots/borgPerformance.png"), height = 11, width = 17, units = "in", res = 330)
print(plt)
dev.off()
