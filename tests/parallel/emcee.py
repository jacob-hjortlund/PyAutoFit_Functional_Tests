import autofit as af
import autofit.plot as aplt
import numpy as np
import matplotlib.pyplot as plt

import os
from os import path
from autoconf import conf

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

def power_two(n):
    return int(np.log2(n))

n_skip = 0
n_repeats = 1
n_available_cpus = 4
n_cpus_arr = np.array(
    [
        2**i for i in range(power_two(n_available_cpus) + 1)
    ]
)[n_skip:]
n_cpus = len(n_cpus_arr)

pwd = path.abspath(path.dirname(__file__))
dataset_path = path.join(pwd, "dataset", "example_1d", "gaussian_x2")
data = af.util.numpy_array_from_json(file_path=path.join(dataset_path, "data.json"))
noise_map = af.util.numpy_array_from_json(
    file_path=path.join(dataset_path, "noise_map.json")
)

xvalues = np.arange(data.shape[0])

model = af.Collection(gaussian_0=af.ex.Gaussian)
print(model.info)
analysis = af.ex.Analysis(data=data, noise_map=noise_map)

times = np.zeros((n_repeats, n_cpus))

for i in range(n_repeats):
    for j in range(n_cpus):
        n_cpus_to_use = n_cpus_arr[j]
        search = af.Emcee(
            number_of_cores=n_cpus_to_use,
            nwalkers=512,
            nsteps=1000,
            iterations_per_update=3000,
        )

        result = search.fit(model=model, analysis=analysis)
        time = result.samples.time
        times[i, j] = float(time)

initial_time = times[:, 0]
#speed_ups = initial_time[:, None] / times

file_name = "sneakier_pool_mp"
np.save(file=path.join(pwd, file_name + "_times.npy"), arr=times)
np.save(file=path.join(pwd, file_name + "_n_cpus.npy"), arr=n_cpus_arr)