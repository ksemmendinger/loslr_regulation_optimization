# Plan Simulation and Optimization Dashboard

This folder contains code for the visual analytics to support rapid plan comparison and evaluation. Results are presented in a R Shiny dashboard. Library requirements for the R environment are available in the `requirements.txt` file.

For efficient load-times, the results from scripts in the `postScripts/` are loaded, formatted, and compressed in the `dataRetrieval.py` file and stored in a `data/` directory in the same folder.

To run the dashboard, you can launch from R Studio or from the terminal using `shiny::runApp()`.

## Running with Docker

In some cases it may be easiest to setup a suitable R environment using Docker.
The following instructions assume you have docker installed and a local cloned copy of the repository.

At a high level, the provided `Dockerfile` contains the instructions for installing the necessary R dependencies required to run the dashboard.
The provided `docker-compose.yml` file contains configuration information used by the `docker` command line utility for both building the docker image running the dashboard.
When the dashboard is run using docker, your local cloned copy of this repository will be mounted into the docker container at `/data`.
Likewise, the shiny app is mounted into the container at `/app/app.R`.
The dashboard is exposed on the local host loopback device on port 8080 (connect at http://localhost:8080).

Instructions are provided in the `docker-compose.yml` file if there is a need to run the dashboard container for develop / debugging purposes.

### Building Docker image

```shell
# run from this directory
docker compose build
```

> [!NOTE]
> If you are running on arm architecture (e.g. M-series mac) you may need to build the image using the following command instead:
> `DOCKER_DEFAULT_PLATFORM=linux/amd64 docker compose build`

### Running Dashboard

```shell
# run from this directory
docker compose up

# use ctrl+c to stop the container

# remove the container using
docker compose down
```

Connect to the dashboard at http://localhost:8080.
