#!/bin/bash

#SBATCH --account=enterYourAccountHereIfApplicable
#SBATCH --mail-user=enterYourEmailHereIfApplicable
#SBATCH --nodes=5 # can set equal to the number of seeds
#SBATCH --tasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=1G
#SBATCH --time=1-00:00:00 # the optimization typically takes ~10seconds per function evaluation, use this guide to calculate a realistic wall time
#SBATCH --partition=standard
#SBATCH --export=ALL
#SBATCH --mail-type=BEGIN,END,FAIL

loc="$1"                # home directory for the optimization code
config="$2"             # path to config file from home directory
nseeds="$3"              # number of random seeds to run optimization

logFile=`basename ${config}`

source /home/kylasr/venv/bin/activate

SEEDS=$(seq 1 ${nseeds})
echo ${SEEDS}
for S in ${SEEDS}
do
srun --exclusive --nodes=1 --ntasks=1 --cpus-per-task=1 --mem-per-cpu=1G python optimizationWrapper.py ${loc} ${config} ${S}> logs/${logFile}_output_seed${S}.txt 2> logs/${logFile}_error_seed${S}.txt &
done
wait < <(jobs -p)