#!/bin/bash
#SBATCH --job-name=dynesty_sneaky_mp

# set the partition
#SBATCH --partition=dark

#SBATCH --nodes=1                       ## 4 Here you specify how many nodes you need

#SBATCH --ntasks=1                    ## 124 248

##SBATCH --ntasks-per-node=1            ## 16 Here you specify that you only want one core

#SBATCH --cpus-per-task=64

#SBATCH --mem=0

##SBATCH --exclusive

# set max wallclock time
#SBATCH --time=10-00:00:00

# set output file location and name
#SBATCH -o ./SLURM_Outputs/%x.out

# mail alert at start, end and abortion of execution
#SBATCH --mail-type=ALL

# send mail to this address
#SBATCH --mail-user=jacob.hjortlund@gmail.com

# If not using the `mpi-selector` that ships with the Mellanox OFED
# (on machines with Mellanox InfiniBand devices), use `module` to load
# an implementation:

source /groups/dark/osman/.bashrc
mamba activate pyautofit

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1
# export MPIEXEC_UNIVERSE_SIZE=1
# export MPI4PY_FUTURES_MAX_WORKERS=1

#python test_emcee.py 
#mpiexec -n 124 python -m mpi4py.futures test_emcee.py

python test_dynesty.py
#mpiexec -n 1 python test_dynesty.py

wait