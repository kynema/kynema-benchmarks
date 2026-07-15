# Setting up the neutral ABL case in AMR-Wind

**Contents**

- [Prerequisites](#prerequisites)
- [Step 1: create the run directory](#step-1-create-the-run-directory)
- [Step 2: edit the input files](#step-2-edit-the-input-files-optional)
- [Step 3: submit the run](#step-3-submit-the-run)
- [Appendix: Grid refinement study](#appendix-grid-refinement-study)

## Prerequisites

1.  Download the benchmarks repository

	```bash
	$ git clone --recursive git@github.com:Exawind/exawind-benchmarks.git BENCHMARKDIR
	```
    
    Here the optional argument `BENCHMARKDIR` is the location where you'd like the 
    benchmark repository to be cloned.  If it not provided, then the repo will be cloned into `exawind-benchmarks` in the current directory.

2. This case is run using AMR-Wind. Please see the [AMR-Wind documentation page](https://exawind.github.io/amr-wind/) for further instructions on how to compile and use the code. 

## Step 1: create the run directory

Prepare a location where this case can be run.  This will likely be a location on the HPC where larger jobs can be run, and where lots of data (many gigabytes) can be stored.  First create the directory: 

```bash
$ mkdir RUNDIR
```

Note that `RUNDIR` can be an arbitrary name or location chosen to be convenient for the user or HPC system.  Then copy the necessary input files into `RUNDIR`

```bash
$ cp BENCHMARKDIR/amr-wind/atmospheric_boundary_layer/neutral/input_files/abl_neutral.inp RUNDIR
$ cp BENCHMARKDIR/amr-wind/atmospheric_boundary_layer/neutral/input_files/abl_neutral_sampling.inp RUNDIR
```

## Step 2: edit the input files (optional)

This case requires two input files: 

- [abl_neutral.inp](https://github.com/Exawind/exawind-benchmarks/blob/main/amr-wind/atmospheric_boundary_layer/neutral/abl_neutral.inp): This file initializes the ABL simulation from scratch and runs for a total simulation time of 120,000s. 

- [abl_neutral_sampling.inp](https://github.com/Exawind/exawind-benchmarks/blob/main/amr-wind/atmospheric_boundary_layer/neutral/abl_neutral_sampling.inp): This file continues the ABL simulation for an additional 5,000s and collecting data from the XY sampling planes.  

Note that an ABL statistics file will be generated for the entire run. 

To modify the time interval over which sampling planes are collected, follow these steps: 

1. Update the `time.stop_time` parameter in [abl_neutral.inp](https://github.com/Exawind/exawind-benchmarks/blob/main/amr-wind/atmospheric_boundary_layer/neutral/abl_neutral.inp) to the desired time at which sampling plane should first be collected. 

2. Update the `io.restart_file = chk240000` parameter to reference the checkpoint file that corresponds to the time specified in step 1. 

Additionally, the sampling planes themselves can be adjusted by editing the `incflo.post_processing` line of the [abl_neutral_sampling.inp](https://github.com/Exawind/exawind-benchmarks/blob/main/amr-wind/atmospheric_boundary_layer/neutral/abl_neutral_sampling.inp) input file and the subsequent parameters that follow.

## Step 3: submit the run

On many HPC platforms, a submission script needs to used to launch the case.  For slurm based systems, a submit script like this `submit.sh` file is used:
```bash
#!/bin/bash
#SBATCH --nodes=20              
#SBATCH --time=47:59:59        # Wall clock time (HH:MM:SS) - once the job exceeds this time, the job will be terminated (default is 5 minutes)
#SBATCH --job-name=ABL # Name of job
#SBATCH --partition=batch      # partition/queue name: short or batch
#SBATCH --qos=normal           # Quality of Service: long, large, priority or normal 
export nodes=$SLURM_JOB_NUM_NODES

# Load any required modules here
#module purge
#module load ...

export EXE=/projects/wind_uq/lcheung/AMRWindBuilds/hfm.20250211/amr-wind/build/amr_wind

# Number MPI processes to run on each node (a.k.a. PPN)
export cores=112
export ncpus=$((nodes * cores))
export OMP_PROC_BIND=spread 
export OMP_PLACES=threads

time mpiexec --bind-to core --npernode $cores --n $ncpus $EXE abl_neutral.inp
```

Then, for slurm based queueing systems, submit the run with a command like:  
```
$ sbatch submit.sh
```

Once this case has finished, re-submit the job but change the input file to point to [abl_neutral_sampling.inp](https://github.com/Exawind/exawind-benchmarks/blob/main/amr-wind/atmospheric_boundary_layer/neutral/abl_neutral_sampling.inp):

`time mpiexec --bind-to core --npernode $cores --n $ncpus $EXE abl_neutral_sampling.inp`

## Appendix: grid refinement study

To run the finer grid case detailed in the [main documentation](../README.md) (grid D), follow the same procedure outline here, but use the [abl_neutral_D_grid.inp](https://github.com/Exawind/exawind-benchmarks/blob/main/amr-wind/atmospheric_boundary_layer/neutral/abl_neutral_D_grid.inp) and [abl_neutral_D_grid_sampling.inp](https://github.com/Exawind/exawind-benchmarks/blob/main/amr-wind/atmospheric_boundary_layer/neutral/abl_neutral_D_grid_sampling.inp) input files.
