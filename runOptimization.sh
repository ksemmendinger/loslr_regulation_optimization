#!/bin/bash

#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --time=14-00:00:00
#SBATCH --partition=normal
#SBATCH --export=ALL

loc="$1"
version="$2"
leadtime="$3"
skill="$4"
nfe="$5"
expName=${leadtime}_${skill}

source /home/fs02/pmr82_0001/kts48/venv/bin/activate

SEEDS=$(seq 1 5)
for S in ${SEEDS}
do
python plan2014_wrapper.py ${loc} ${version} ${leadtime} ${skill} ${S} ${nfe} 100 1000 0.75 17 > logs/${expName}_output_seed${S}.txt 2> logs/${expName}_error_seed${S}.txt &
done
wait < <(jobs -p)