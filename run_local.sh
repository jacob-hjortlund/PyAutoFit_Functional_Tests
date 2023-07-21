#!/bin/bash

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1
export PYAUTOFIT_PARALLEL_PROFILE=1

N_REPEATS=0 # zero-indexed

START_CPU_INDEX=0
MAX_CPU_ITERS=2 # zero-indexed

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
        # -s -o profile_${j} \
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
        search_cfg.maxiter=100 \
        search_cfg.nsteps=100 \
        #search_cfg.n_effective=100
        
        
        echo ""
    done
    echo ""
done    