rm(list=ls())
gc()

options(scipen = 999)

# load libraries
library(tidyverse)

args <- commandArgs(trailingOnly = TRUE)
# args <- c("mac_ext", "flowANN_Bv7_12month_sqAR_61dv_7obj_historic_100000nfe", "5", 100000)

# [1] location
# [2] experiment name
# [3] number of seeds
# [4] version (historic or stochastic)
# [5] skill (sq, [0, 1])
# [6] number of function evaluations
# [7] number of objectives
# [8] number of decision variables

loc <- args[1]
folderName <- args[2]
seeds <- as.numeric(args[3])
# seeds <- as.numeric(args[2])
# leadtime <- args[3]
# skill <- args[4]
nfe <- as.numeric(str_remove(grep("nfe", str_split(folderName, "_")[[1]], value = TRUE), "nfe"))
# nvars <- as.numeric(args[6])
# 
# # experiment name for directory
# if (last(args) == "RBF") {
#   folderName <- paste0("RBF_", leadtime, "_", skill, "_", nfe, "nfe_", nvars, "dvs")
# } else {
#   folderName <- paste0(leadtime, "_", skill, "_", nfe, "nfe_", nvars, "dvs")
# }

# set working directory
if (args[1] == "mac_ext") { 
  wd <- "/Volumes/ky_backup/dps/output"
}
setwd(paste0(wd, "/data/", folderName))

# create new folder for plots
dir.create("moeaFramework/plots", showWarnings = FALSE)

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
  freq <- read.delim(paste0("clean/runtime_S", i, ".txt"),
                     sep = ",", check.names = FALSE) %>%
    select(NFE) %>%
    unique() %>%
    deframe()
  
  # load runtime performance
  rt <- read.delim(paste0("moeaFramework/metrics/runtime_S", i, ".metrics"), sep = " ") %>%
    setNames(c("Hypervolume", "Generational Distance", 
               "Inverted Generational Distance", "Spacing", 
               "Epsilon Indicator", "Maximum Pareto Front Error")) %>%
    mutate(NFE = freq, .before = 1)
  
  # load final performance
  final <- read.delim(paste0("moeaFramework/metrics/final_S", i, ".metrics"), sep = " ") %>%
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

png(paste0("moeaFramework/plots/borgPerformance.png"), height = 11, width = 17, units = "in", res = 330)
print(plt)
dev.off()
