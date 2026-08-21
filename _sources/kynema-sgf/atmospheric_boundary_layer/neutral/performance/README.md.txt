# AMR-Wind code performance

## Overview  (Grid C)

The relevant code versions are

- AMR-Wind version: [32811b18af31e7b54f7e5cb23c6ead424f21f1f0](https://github.com/Exawind/amr-wind/commit/32811b18af31e7b54f7e5cb23c6ead424f21f1f0)

The job was run on the NREL's [Kestrel](https://nrel.github.io/HPC/Documentation/Systems/) HPC cluster, on CPU nodes, using the following resources:

| Parameter       | Value |
|---              |---  |
| Number of nodes | 20   |
| Number of CPUs  | 2080 |
| Wall-time       | 144 hours|
| CPU-hours       | 299520     |

The overall simulation parameters

| Parameter              | Value |
|---                     |---    |
| Total simulation time  | 125000.0 sec |
| Simulation timestep    | 0.5 sec |
| Total mesh size        | 48,234,496 |
| Num mesh elements/rank | 23,190 |

Average time spent every iteration in the following categories:

|Category| Time [s]|
|---            | --- |
|Pre-processing | 0.0041|
|Solve          | 2.23|
|Post-processing| 0.024|
|**Total**      | 2.257 |

### Log file
**Header**

```
==============================================================================
                AMR-Wind (https://github.com/exawind/amr-wind)

  AMR-Wind version :: v3.1.5-11-g32811b18
  AMR-Wind Git SHA :: 32811b18af31e7b54f7e5cb23c6ead424f21f1f0
  AMReX version    :: 24.09-45-g6d9c25b989f1

  Exec. time       :: Thu Oct 24 18:32:32 2024
  Build time       :: Oct 14 2024 08:26:23
  C++ compiler     :: IntelLLVM 2023.2.0

  MPI              :: ON    (Num. ranks = 2080)
  GPU              :: OFF
  OpenMP           :: OFF

  Enabled third-party libraries:
    NetCDF    4.9.2
    HYPRE     2.31.0

           This software is released under the BSD 3-clause license.
 See https://github.com/Exawind/amr-wind/blob/development/LICENSE for details.
------------------------------------------------------------------------------
```

## Grid Refinement Study  (Grid D)

The relevant code versions are

- AMR-Wind version: [b3cf40a884f79c9127bb2d7fa0381995a2893f99](https://github.com/Exawind/amr-wind/commit/b3cf40a884f79c9127bb2d7fa0381995a2893f99)

The job was run on the Sandia Flight HPC cluster using the following resources: 

| Parameter       | Value |
|---              |---  |
| Number of nodes | 64   |
| Number of CPUs  | 7168 |
| Wall-time       | 177.68 hours|
| CPU-hours       | 1273610.24 | 

with the following machine specifications: 

| Parameter           | Value |
|---                  |---  |
| CPU processor type  | Intel(R) Xeon(R) Platinum 8480+ |
| CPU processor speed | 3800 Mhz |
| Node interconnects  | Cornelis Omni-Path high-speed interconnect |

The overall simulation parameters 

| Parameter              | Value |
|---                     |---    |
| Total simulation time  | 125000 sec | 
| Simulation timestep    | 0.25 sec | 
| Total mesh size        | 385,875,968 |
| Num mesh elements/rank | 53,833 |

Average time spent every iteration in the following categories:  

|Category| Time [s]|
|---            | --- |
|Pre-processing | 0.0055|
|Solve          | 1.0803|
|Post-processing| 0.2070|
|**Total**      | 1.2929|


### Log file
**Header**

```
==============================================================================
                AMR-Wind (https://github.com/exawind/amr-wind)

  AMR-Wind version :: v3.4.0-1-gb3cf40a8
  AMR-Wind Git SHA :: b3cf40a884f79c9127bb2d7fa0381995a2893f99
  AMReX version    :: 25.01-16-g92d35c2c8163

  Exec. time       :: Mon Feb 24 07:43:25 2025
  Build time       :: Feb 11 2025 18:58:02
  C++ compiler     :: GNU 12.1.0

  MPI              :: ON    (Num. ranks = 7168)
  GPU              :: OFF
  OpenMP           :: OFF

  Enabled third-party libraries: 
    NetCDF    4.9.2
    OpenFAST  

           This software is released under the BSD 3-clause license.           
 See https://github.com/Exawind/amr-wind/blob/development/LICENSE for details. 
------------------------------------------------------------------------------
```

