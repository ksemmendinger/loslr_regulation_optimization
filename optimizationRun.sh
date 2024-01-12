#!/bin/bash

#SBATCH --account=yhon0
#SBATCH --nodes=5
#SBATCH --tasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=16G
#SBATCH --time=14-00:00:00
#SBATCH --partition=standard
#SBATCH --export=ALL
#SBATCH --mail-user=kylasr@umich.edu
#SBATCH --mail-type=BEGIN,END,FAIL

loc="$1"
config="$2"

source /home/kylasr/venv/bin/activate

SEEDS=$(seq 1 5)
for S in ${SEEDS}
do
srun --exclusive --nodes=1 --ntasks=1 --cpus-per-task=1 --mem-per-cpu=16G python optimizationWrapper.py ${loc} ${config} ${S}> logs/${config}_output_seed${S}.txt 2> logs/${config}_error_seed${S}.txt &
done
wait < <(jobs -p)