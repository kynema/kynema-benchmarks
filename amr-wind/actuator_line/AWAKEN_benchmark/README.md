<!-- This file is automatically compiled into the website. Please copy linked files into .website_src/ paths to enable website rendering -->

# Actuator disk wind farm run with mesoscale forcing matching measured data.

This benchmark problem describes an AMR-Wind simulation which was set up to match the conditions and measurements corresponding to the [AWAKEN benchmark](https://awaken-benchmark.readthedocs.io/en/latest/) exercise conducted as a part of the American Wake Experiment (AWAKEN).  In that field campaign, measurements of five wind plants in northern Oklahoma were taken, including data for the atmospheric inflow, wind turbine performance, and wake behavior, using a variety of instrumentation and measurement methods.  A simulation was then set up to correspond to specific measured conditions and then the wind farm performance and wake behavior were compared to observations.


**Contents**

- [Simulation description and setup](#simulation-description-and-setup)
- [Postprocessing](#postprocessing)
- [Code performance](#code-performance)
- [Results](#results)

## Simulation description and setup

The full details of the AWAKEN benchmark simulation using AMR-Wind are provided in [**setup documentation**](setup/README.md).  In this phase of benchmarking exercise, the simulation focused on the operation of the King Plains wind farm during the time period of 05:00 - 07:00 UTC on August 24, 2023.

The size of the computational domain was 24km x 17.6km x 0.8 km, with a background mesh resolution of 10m and total mesh size of 625.7M elements.  The GE 2.8-127 turbines at the King Plains wind farm was represented using 85 actuator disk models, coupled to AMR-Wind through OpenFAST.  A schematic of the domain, including the turbine locations and the virtual measurement locations, is shown below.

![domain](setup/KP_Domain_lidar.png)

Running this simulation requires setting up a precursor ABL calculation to match the measured inflow, and then adding the turbines to the actual wind farm simulation itself.  The precursor ABL calculation is done using a meso/microscale coupling (MMC) approach which uses a direct data assimilation method to incorporate measured wind speed and temperature profiles into the simulation forcing.  The forcing terms and boundary data is then used in the wind farm simulation itself.  In the [setup documentation](setup/README.md) page, we describe how the measurement data is processed, the MMC precursor is created, and the wind farm simulation is set up.

## Code performance

Full details provided in [**performance documentation**](performance/README.md).

The job was run on an HPC cluster using 48 nodes/5376 CPU's in multiple segments.  The first segment for 2500 seconds used these resources:

| Parameter       | Value |
|---              |---  |
| Number of nodes | 48   |
| Number of CPUs  | 5376 |
| Wall-time       | 55.5 hours|
| CPU-hours       | 298368.0    | 



## Postprocessing

Full details of the postprocessing methods used in the benchmark simulation are provided in the [**postprocessing documentation**](postprocessing/README.md).

A number of scripts and notebooks are provided which should extract the 
- turbine performance time history
- virtual lidar measurements
- time averaged hub-height velocity field
- instantaneous velocity field

![King Plains animation](results/images/KP_z090hh.gif)

## Results

Full details of the results and comparisons with measured data are provided in [**results documentation**](results/README.md).
