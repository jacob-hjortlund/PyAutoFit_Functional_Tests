#!/bin/bash
#SBATCH --job-name=mpi

# set the partition
#SBATCH --partition=dark

#SBATCH --nodes=4                       ## 4 Here you specify how many nodes you need

#SBATCH --ntasks=256

##SBATCH --ntasks-per-node=1            ## 16 Here you specify that you only want one core

#SBATCH --cpus-per-task=1

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

NP1_REPEATS=0
MAX_CPU_ITERS=8
SEARCH_NAME=Emcee
POOL_TYPE=SneakierPool

for ((i=0;i<=NP1_REPEATS;i++))
do
    echo "Starting repeat $i..."
    echo ""
    for ((j=0;j<=MAX_CPU_ITERS;j++))
    do
        
        let N_CPU=2**$j

        echo "Using $N_CPU CPUS.."
        echo ""

        mpiexec -n $N_CPU python -m mpi4py.futures \
        test_parallel_search.py \
        search_name=$SEARCH_NAME \
        pool_type=$POOL_TYPE \
        parallelization_scheme="mpi" \
        max_cpu_iters=$MAX_CPU_ITERS \
        cpu_index=$j \
        n_repeats=$NP1_REPEATS \
        repeat_index=$i 

        echo ""
    done
    echo ""
done      