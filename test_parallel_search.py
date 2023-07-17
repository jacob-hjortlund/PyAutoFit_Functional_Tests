import os
import hydra
import omegaconf
import numpy as np
import autofit as af
import autofit.plot as aplt
import matplotlib.pyplot as plt

import src as cosmo

from autoconf import conf
from pyprojroot import here

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

@hydra.main(
    version_base=None, config_path="config", config_name="hydra"
)
def main(hydra_cfg: omegaconf.DictConfig) -> None:

    pool_type = hydra_cfg['pool_type']
    search_name = hydra_cfg["search_name"]
    parallelization_scheme = hydra_cfg["parallelization_scheme"]
    
    cpu_index= int(hydra_cfg["cpu_index"])
    max_cpu_iters = int(hydra_cfg["max_cpu_iters"]) + 1
    n_cpus = int(2**cpu_index) 

    n_repeats = int(hydra_cfg["n_repeats"]) + 1
    repeat_index = int(hydra_cfg["repeat_index"])

    search_cfg = omegaconf.OmegaConf.to_container(hydra_cfg["search_cfg"])

    # Set Paths

    root_path = str(here())

    dataset_path = os.path.join(
        root_path,
        "dataset",
        "cosmology"
    )

    save_path = os.path.join(
        root_path,
        "results",
        search_name
    )
    os.makedirs(save_path, exist_ok=True)

    output_filename = os.path.join(
        save_path,
        f"{pool_type}_{parallelization_scheme}_{max_cpu_iters}_walltimes.npy"
    )

    if os.path.exists(output_filename):
        output = np.load(file=output_filename)
    else:
        output = np.zeros((n_repeats, max_cpu_iters))
        np.save(file=output_filename, arr=output)

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
    mass.mass = af.UniformPrior(lower_limit=1.0, upper_limit=2.0)

    lens = af.Model(
        cosmo.Galaxy, redshift=0.5, light_profile_list=[light], mass_profile_list=[mass]
    )

    # Build Source Model

    light = af.Model(cosmo.lp.LightExponential)

    light.centre.centre_0 = af.GaussianPrior(mean=-0.25, sigma=0.1)
    light.centre.centre_1 = af.GaussianPrior(mean=0.33, sigma=0.1)
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

    # Create Search

    search_function = getattr(af, search_name)

    search = search_function(
        number_of_cores=n_cpus,
        iterations_per_update=int(1e6),
        **search_cfg
    )
    result = search.fit(model=model, analysis=analysis)
    time = result.samples.time
    output[repeat_index, cpu_index] = float(time)
    
    np.save(file=output_filename, arr=output)

if __name__ == "__main__":
    main() 