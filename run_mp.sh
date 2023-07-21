#!/bin/bash
#SBATCH --job-name=mp_dynesty_1000

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


N_REPEATS=0 # zero-indexed

START_CPU_INDEX=0
MAX_CPU_ITERS=6 # zero-indexed

SEARCH_NAME=DynestyStatic
POOL_TYPE=SneakierPool

for ((i=0;i<=N_REPEATS;i++))
do
    echo "Starting repeat $i..."
    echo ""
    for ((j=START_CPU_INDEX;j<=MAX_CPU_ITERS;j++))
    do
        
        let N_CPU=2**$j

        echo "Using $N_CPU CPUS.."
        echo ""

        # py-spy record \
        # -s -o ./profiles/full_old_init_${j} \
        # -f speedscope \
        python test_parallel_search.py \
        search_name=$SEARCH_NAME \
        pool_type=$POOL_TYPE \
        parallelization_scheme="mp" \
        max_cpu_iters=$MAX_CPU_ITERS \
        cpu_index=$j \
        n_repeats=$N_REPEATS \
        repeat_index=$i \
        sleep=1. \
        tags=["maxiter_1000"] \
        search_cfg.nlive=256 \
        search_cfg.sample="rwalk" \
        search_cfg.maxiter=1000 \
        search_cfg.nsteps=100 \
        #search_cfg.n_effective=100
        
        
        echo ""
    done
    echo ""
done    