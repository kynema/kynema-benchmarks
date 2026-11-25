# AMR-Wind code performance

## Overview  

The relevant code versions are

- AMR-Wind version: [f67a52dd6aa1882595d16700527470bc8097cb13](https://github.com/Exawind/amr-wind/commit/f67a52dd6aa1882595d16700527470bc8097cb13)

The initial 15,000 second precursor job was run on the Sandia Flight HPC cluster using the following resources: 

| Parameter       | Value |
|---              |---  |
| Number of nodes | 8   |
| Number of CPUs  | 896 |
| Wall-time       | 5.4 hours|
| CPU-hours       | 4821.7 |  

with the following machine specifications: 

| Parameter           | Value |
|---                  |---  |
| CPU processor type  | Intel(R) Xeon(R) Platinum 8480+ |
| CPU processor speed | 3800 Mhz |
| Node interconnects  | Cornelis Omni-Path high-speed interconnect |

The overall simulation parameters 

| Parameter              | Value |
|---                     |---    |
| Total simulation time  | 15,000 sec | 
| Simulation timestep    | 0.2 sec | 
| Total mesh size        | 50,331,648 |
| Num mesh elements/rank | 56,174 |

Average time spent every iteration in the following categories:  

|Category| Time [s]|
|---            | --- |
|Pre-processing | 0.00107678|
|Solve          | 0.554703|
|Post-processing| 0.0899544|
|**Total**      | 0.645733 |


### Log file
**Header**

```
==============================================================================
                AMR-Wind (https://github.com/exawind/amr-wind)

  AMR-Wind version :: v3.1.4-17-gf67a52dd
  AMR-Wind Git SHA :: f67a52dd6aa1882595d16700527470bc8097cb13
  AMReX version    :: 24.09-6-gde4dc974dda7

  Exec. time       :: Sat Dec 14 13:38:30 2024
  Build time       :: Sep 26 2024 23:36:43
  C++ compiler     :: GNU 12.1.0

  MPI              :: ON    (Num. ranks = 896)
  GPU              :: OFF
  OpenMP           :: OFF

  Enabled third-party libraries: 
    NetCDF    4.9.2
    OpenFAST  

           This software is released under the BSD 3-clause license.           
 See https://github.com/Exawind/amr-wind/blob/development/LICENSE for details. 
------------------------------------------------------------------------------
```

**Footer**

```
Time spent in InitData():    5.930747028
Time spent in Evolve():      19372.8704
```