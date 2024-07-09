FROM rocker/shiny-verse:4.4.1

RUN Rscript -e \
    'install.packages(c("shiny", "shinyWidgets", "shinythemes", "shinycssloaders", "DT", "RcppTOML", "tidyverse", "gridExtra", "paletteer"), repos="https://cloud.r-project.org")'
