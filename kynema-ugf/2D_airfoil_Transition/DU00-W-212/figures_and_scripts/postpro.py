# Collection of utilities to read and process nalu-wind output data for airfoil
# simulations

import yaml, json, glob, sys
from pathlib import Path
import numpy as np
import pandas as pd
import math

u_infty= 341*0.1
rho    = 1.225

def read_static_case(
    af_name,
    aoa,
    rey,
):
    """Read the airfoil performance data for simulation of flow past an airfoil
    using k-w-SST turbulence model

    Args:
        af_name (string):
        aoa (double): Angle of attack in degrees
        rey (double): Reynolds number
        u_infty (double): Free-stream velocity (in m/s)
        rho (double): Free-stream density of air (in kg/m^3)

    Returns:
        [cl, cd, cm]: Array of lift, drag and moment coefficient

    """


    results_file = "{}/rey_{:08d}/aoa_{}/results/forces.dat".format(
        af_name, int(rey), aoa
    )
    print(results_file)

    if not Path(results_file).exists():
        print(
            "Results file ", results_file, " doesn't exist. Please check this directory"
        )
        return [-1, -1, -1]

    data = pd.read_csv(
        results_file,
        sep="\s+",
        #header=None,
        skiprows=1,
        names=[
            "Time",
            "Fpx",
            "Fpy",
            "Fpz",
            "Fvx",
            "Fvy",
            "Fvz",
            "Mtx",
            "Mty",
            "Mtz",
            "Y+min",
            "Y+max",
        ],
    ).iloc[-1000:-1]
    dyn_pres = 0.5 * rho * (u_infty ** 2)
    cfz = (data["Fpy"] + data["Fvy"]) / dyn_pres
    cfx = (data["Fpx"] + data["Fvx"]) / dyn_pres
    cm = data["Mtz"] / dyn_pres

    cos_aoa=math.cos(math.radians(aoa))
    sin_aoa=math.sin(math.radians(aoa))

    cl = cfz*cos_aoa - cfx*sin_aoa
    cd = cfz*sin_aoa + cfx*cos_aoa
   
    cl = np.mean(cl)
    cd = np.mean(cd)
    cm = np.mean(cm)


    return [cl, cd, cm]


def read_af_cases(airfoil,rey=[3e6, 6e6, 9e6, 12e6, 15e6], aoa_range=np.linspace(0, 17, 18)):
    """Read aerodynamic performance data for static cases corresponding to
    the airfoil.
    """

    for af in airfoil:
        for re in rey:
            polar_data = np.array(
                [read_static_case(af, aoa, re) for aoa in aoa_range]
            )
    
            p_data = { af: {
                "aoa": (np.array(aoa_range)).tolist(),
                "cl": polar_data[:, 0].tolist(),
                "cd": polar_data[:, 1].tolist(),
                "cm": polar_data[:, 2].tolist(),
            } }
            yaml.dump(
                p_data,
                open("{}/{}_rey{:08d}.yaml".format(af,af,int(re)), "w"),
            )
    

if __name__ == "__main__":

    af=['du00w212_F']
    read_af_cases(af,rey=[3e6],aoa_range=[0.0, 5.0])



