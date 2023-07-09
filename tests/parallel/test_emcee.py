import os
import numpy as np
import autofit as af
import autofit.plot as aplt
import matplotlib.pyplot as plt

from autoconf import conf
from pyprojroot import here
from .. import src as cosmo

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

def power_two(n):
    return int(np.log2(n))

def main():

    # CPU Settings TODO: Make this a CLI arg or config based

    n_repeats = 1
    n_cpus_available = 4
    n_cpus_arr = np.array(
        [
            2**i for i in range(power_two(n_cpus_available) + 1)
        ]
    )
    n_cpus = len(n_cpus_arr)

    # Set Paths

    root_path = str(here())

    dataset_path = os.path.join(
        root_path, "dataset", "cosmology"
    )

    save_path = os.path.join(
        root_path, "tests", "parallel", "results",
        f"n_cpus_{n_cpus_available}_repeats_{n_repeats}"
    )
    os.makedirs(save_path, exist_ok=True)

    output_filename = os.path.join(
        save_path, "emcee_mp_walltimes.npy"
    )
    if os.path.exists(output_filename):
        output = np.load(file=output_filename)
    else:
        output = np.zeros((n_repeats, n_cpus))

    config_path = os.path.join(
        root_path, "config"
    )
    conf.instance.push(new_path=config_path)

    # Load Datasets

    data = np.load(file=os.path.join(dataset_path, "data.npy"))
    noise_map = np.load(file=os.path.join(dataset_path, "noise_map.npy"))
    psf = np.load(file=os.path.join(dataset_path, "psf.npy"))
    grid = np.load(file=os.path.join(dataset_path, "grid.npy"))

    # Build Lens Model

    light = af.Model(cosmo.lp.LightDeVaucouleurs)

    light.centre = (0.0, 0.0)
    light.axis_ratio = af.UniformPrior(lower_limit=0.6, upper_limit=1.0)
    light.angle = af.UniformPrior(lower_limit=0.0, upper_limit=180.0)
    light.intensity = af.LogUniformPrior(lower_limit=1e-4, upper_limit=1e4)
    light.effective_radius = af.UniformPrior(lower_limit=0.0, upper_limit=5.0)

    mass = af.Model(cosmo.mp.MassIsothermal)

    mass.centre = (0.0, 0.0)
    mass.axis_ratio = af.UniformPrior(lower_limit=0.6, upper_limit=1.0)
    mass.angle = af.UniformPrior(lower_limit=0.0, upper_limit=180.0)
    mass.mass = af.UniformPrior(lower_limit=1.0, upper_limit=2.0) # This is a prior I know from previous analysis

    lens = af.Model(
        cosmo.Galaxy, redshift=0.5, light_profile_list=[light], mass_profile_list=[mass]
    )

    # Build Source Model

    light = af.Model(cosmo.lp.LightExponential)

    light.centre.centre_0 = af.GaussianPrior(mean=-0.25, sigma=0.1) # This is a prior I know from previous analysis
    light.centre.centre_1 = af.GaussianPrior(mean=0.33, sigma=0.1) # This is a prior I know from previous analysis
    light.axis_ratio = af.UniformPrior(lower_limit=0.7, upper_limit=1.0)
    light.angle = af.UniformPrior(lower_limit=0.0, upper_limit=180.0)
    light.intensity = af.LogUniformPrior(lower_limit=1e-4, upper_limit=1e4)
    light.effective_radius = af.UniformPrior(lower_limit=0.0, upper_limit=1.0)

    source = af.Model(
        cosmo.Galaxy, redshift=1.0, light_profile_list=[light]
    )

    # Create Strong Lens Model

    model = af.Collection(galaxies=af.Collection(lens=lens, source=source))

    # Create Analysis

    analysis = cosmo.Analysis(
        data=data, noise_map=noise_map, psf=psf, grid=grid
    )

    # Run Search Over N cpus

    wall_times = np.zeros((n_repeats, n_cpus))

    for i in range(n_repeats):

        print(f"\nRepeat {i+1} of {n_repeats}\n")

        for j in range(n_cpus):

            print(f"\nNumber of CPUs = {n_cpus_arr[j]}")
            n_cpus_to_use = n_cpus_arr[j]
            search = af.Emcee(
                number_of_cores=n_cpus_to_use,
            )
            result = search.fit(model=model, analysis=analysis)
            time = result.samples.time
            output[i, j] = float(time)
            print("\n")
        
    np.save(file=output_filename, arr=output)

if __name__ == "__main__":
    main()