#!/bin/bash
#SBATCH --job-name=mpi_emcee_new

# set the partition
#SBATCH --partition=dark

#SBATCH --nodes=9                       ## 4 Here you specify how many nodes you need

#SBATCH --ntasks=257

##SBATCH --ntasks-per-node=32            ## 16 Here you specify that you only want one core

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

N_REPEATS=4 # zero-indexed
MAX_CPU_ITERS=8 # zero-indexed
SEARCH_NAME=Emcee
POOL_TYPE=SneakierPool

echo $(mpiexec --version)

for ((i=0;i<=N_REPEATS;i++))
do
    echo "Starting repeat $i..."
    echo ""
    for ((j=0;j<=MAX_CPU_ITERS;j++))
    do
        
        let N_CPU=2**$j
        export MPI4PY_FUTURES_MAX_WORKERS=$N_CPU

        echo "Using $N_CPU CPUS.."
        echo "MPI4PY max workers: $MPI4PY_FUTURES_MAX_WORKERS"
        echo ""

        mpiexec -n 1 python -m mpi4py.futures \
        test_parallel_search.py \
        search_name=$SEARCH_NAME \
        pool_type=$POOL_TYPE \
        parallelization_scheme="mpi" \
        max_cpu_iters=$MAX_CPU_ITERS \
        cpu_index=$j \
        n_repeats=$N_REPEATS \
        repeat_index=$i 

        echo ""
    done
    echo ""
done      