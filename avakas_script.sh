#!/usr/bin/env bash

#############################
# Your job name (displayed by the queue)
#PBS -N kw-simulation

#change output file's name
#PBS -e /home/anioche/aurelien/KW-master/logs/KW-simulation.err

#PBS -o /home/anioche/aurelien/KW-master/logs/KW-simulation.log


# Specify the working directory
#PBS -d /home/anioche/aurelien/KW-master/KW

# walltime (hh:mm::ss)
#PBS -l walltime=01:00:00

# Specify the number of nodes(nodes=) and the number of cores per nodes(ppn=) to be used
#PBS -l nodes=1:ppn=6

# Specify physical memory: kb for kilobytes, mb for megabytes, gb for gigabytes
#PBS -l mem=1gb

#PBS -m abe
#PBS -M clusterresultssimulation@gmail.com

# fin des directives PBS
#############################

module purge # modules cleaning
module add torque
pyenv local 3.5.2

# useful informations to print
echo "#############################"
echo "User:" ${USER}
echo "Date:" `date`
echo "Host:" `hostname`
echo "Directory:" `pwd`
echo "PBS_JOBID:" ${PBS_JOBID}
echo "PBS_O_WORKDIR:" ${PBS_O_WORKDIR}
echo "PBS_NODEFILE: " `cat ${PBS_NODEFILE} | uniq`
echo "#############################"

#############################

mkdir ../logs

# What you actually want to launch
echo "Start the job"
echo main.py

# launch python script
python running_script.py

echo "#############################"
echo "Date:" `date`
echo "Job finished"
echo "#############################"
