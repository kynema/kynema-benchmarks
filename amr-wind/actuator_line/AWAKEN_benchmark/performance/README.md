# AMR-Wind code performance

## Overview

The relevant code versions are

- AMR-Wind version: v3.4.1-35-geee722c0 [eee722c091b56c9a345c29b77442393b722d8bec](https://github.com/Exawind/amr-wind/commit/eee722c091b56c9a345c29b77442393b722d8bec)

- OpenFAST version: [OpenFAST-v3.5.5](https://github.com/OpenFAST/openfast/releases/tag/v3.5.5)

- ROSCO version: ROSCO-v2.9.0

The initial job (1 of 4) was run on the Sandia Flight HPC cluster using the following resources: 

| Parameter       | Value |
|---              |---  |
| Number of nodes | 48   |
| Number of CPUs  | 5376 |
| Wall-time       | 55.5 hours|
| CPU-hours       | 298368.0    | 

with the following machine specifications: 

| Parameter           | Value |
|---                  |---  |
| CPU processor type  | Intel(R) Xeon(R) Platinum 8480+ |
| CPU processor speed | 3800 Mhz |
| Node interconnects  | Cornelis Omni-Path high-speed interconnect |

The overall simulation parameters 

| Parameter              | Value |
|---                     |---    |
| Total simulation time  | 2503 sec | 
| Simulation timestep    | 0.1 sec | 
| Total mesh size        | 625,748,480 | 
| Num mesh elements/rank | 116,397 |

Average time spent every iteration in the following categories:  

|Category| Time [s]|
|---            | --- |
|Pre-processing | 1.32849 |
|Solve          | 5.6406  |
|Post-processing| 1.00343 |
|**Total**      | 7.97255 |

## Log file
**Header**

```
==============================================================================
                AMR-Wind (https://github.com/exawind/amr-wind)

  AMR-Wind version :: v3.4.1-35-geee722c0
  AMR-Wind Git SHA :: eee722c091b56c9a345c29b77442393b722d8bec
  AMReX version    :: 25.05-22-gd3798de0bd81

  Exec. time       :: Sun Jul  6 00:05:40 2025
  Build time       :: Jun  5 2025 19:18:59
  C++ compiler     :: GNU 12.1.0

  MPI              :: ON    (Num. ranks = 5376)
  GPU              :: OFF
  OpenMP           :: OFF

  Enabled third-party libraries: 
    NetCDF    4.9.2
    OpenFAST  

           This software is released under the BSD 3-clause license.           
 See https://github.com/Exawind/amr-wind/blob/development/LICENSE for details. 
------------------------------------------------------------------------------
```
