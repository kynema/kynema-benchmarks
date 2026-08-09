# Postprocessing AWAKEN benchmark results

**Contents**

- [Plot instantaneous hub-height planes](#plot-instantaneous-hub-height-planes)
- [OpenFAST turbine results](#openfast-turbine-results)
- [Averaged lidar results](#averaged-lidar-results)

**Note**: In many of the python scripts and Jupyter notebooks provided, the path to the [AMR-Wind front end](https://github.com/Exawind/amr-wind-frontend) library must be provided.  If necessary, download the library and edit the lines in the python code which define `amrwindfedirs` to include any locations of that library.
```python
# Add any possible locations of amr-wind-frontend here
amrwindfedirs = ['/projects/wind_uq/lcheung/amrwind-frontend/',
                 '/ccs/proj/cfd162/lcheung/amrwind-frontend/']
import sys, os, shutil, io
for x in amrwindfedirs: sys.path.insert(1, x)
```

Adding those paths to the system search path will enable the notebooks to find the AMR-Wind frontend postprocessing engine.

## Plot instantaneous hub-height planes

The notebook [Plot_Hubheight_Instantaneous.ipynb](Plot_Hubheight_Instantaneous.ipynb) creates instantaneous hub-height snapshots of the King Plains wind farm.  Change the times specified in the yaml input:

```yaml
  times: [7300, 8000, 8500, 9000, 9500, 10000, 10500, 11000, 12000, 13000, 14000]
```

to extract the desired snapshots.

Note that due to computational resources, the simulation was run in 4 sections, each section in a different directory, so in cell 3, these directories are specified:
```python
replacedict={'RUNDIRA':'/tscratch/lcheung/AWAKEN/Benchmark1/Phase3/FarmRuns/BM3_FarmRunProd1_runA/',
             'RUNDIR_A1':'/tscratch/lcheung/AWAKEN/Benchmark1/Phase3/FarmRuns/BM3_FarmRunProd1_runA1/',
             'RUNDIR_A2':'/tscratch/lcheung/AWAKEN/Benchmark1/Phase3/FarmRuns/BM3_FarmRunProd1_runA2/',
             'RUNDIR_A3':'/tscratch/lcheung/AWAKEN/Benchmark1/Phase3/FarmRuns/BM3_FarmRunProd1_runA3/',
             'NCPREFIX':'KP_z090hh',
            }

```

In the second section of this notebook, it creates a gif animation of the wind farm simulation:

![King Plains animation](../results/images/KP_z090hh.gif)

## OpenFAST turbine results

The output of the King Plains turbines is extracted in the [Extract_OF_Results.ipynb](Extract_OF_Results.ipynb) notebook.

The locations of the run directories and the results directories should be given in the `replacedict` dictionary:

```python
replacedict={'RUNDIRA':'/tscratch/lcheung/AWAKEN/Benchmark1/Phase3/FarmRuns/BM3_FarmRunProd1_runA/',
             'RUNDIR_A1':'/tscratch/lcheung/AWAKEN/Benchmark1/Phase3/FarmRuns/BM3_FarmRunProd1_runA1/',
             'RUNDIR_A2':'/tscratch/lcheung/AWAKEN/Benchmark1/Phase3/FarmRuns/BM3_FarmRunProd1_runA2/',
             'RUNDIR_A3':'/tscratch/lcheung/AWAKEN/Benchmark1/Phase3/FarmRuns/BM3_FarmRunProd1_runA3/',
             'RESULTSDIRA':'../results/OFRESULTS_RUNA',
             'RESULTSDIR_A1':'../results/OFRESULTS_RUNA1',
             'RESULTSDIR_A2':'../results/OFRESULTS_RUNA2',
             'RESULTSDIR_A3':'../results/OFRESULTS_RUNA3',
            }

```

And the variables to be extracted from the OpenFAST file are given in the `vars` section of each yaml input:

```yaml
  vars: 
  - Time
  - NacYaw
  - GenPwr
  - Wind1VelX
  - Wind1VelY
  - Wind1VelZ
```

## Averaged lidar results

The notebook [AVG_Lidar.ipynb](AVG_Lidar.ipynb) computes the time-averaged 1st order and 2nd order velocity statistics from the sampled lidar locations for comparison with the field measurements.  Note that the list of all netcdf files to be included in the averaging process should be specified in the `nclist` anchor.

```yaml
filelist: &nclist [RUNDIRA/post_processing/lidar_14400.nc, RUNDIR_A1/post_processing/lidar_37800.nc, RUNDIR_A2/post_processing/lidar_54000.nc, RUNDIR_A3/post_processing/lidar_72900.nc]
```


## Averaged hub-height planes

The notebook [AVG_HH_Planes.ipynb](AVG_HH_Planes.ipynb) computes the time-averaged hub-height planes from the King Plains wind farm.  Currently it computes the 10-min averages at specific times, although this can be changed by modifying the `tavg` field:

```yaml
tavg: [8400, 9000]
```

An example of the averaged horizontal hub-height planes is shown here:
![AVG horizontal velocity](../results/images/KP_HH_AVG_Uh_09000.png)

