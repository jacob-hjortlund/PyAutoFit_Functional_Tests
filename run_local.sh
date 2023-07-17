#!/bin/bash

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1

NP1_REPEATS=0
MAX_CPU_ITERS=2
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