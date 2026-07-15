

# TU Delft DU00-W-212 airfoil

Validation of the transition model is conducted for the DU00-W-212 wind turbine airfoil using Nalu-Wind with the 1-equation gamma transition model. A full angle-of-attack sweep was performed, and the results are compared against the experimental data[1] and fully tubulent simulation results.

## Simulation Conditions

- Test airfoil: DU00-W-212 airfoil with a thickness of 21% 
- Flow Condition: M=0.1, Re=3million, Tu=0.0864%
   - $U_\infty$=34.1m/s, $\rho$=1.225kg/m<sup>3</sup>, $\mu_t/\mu$=1
   - $k_\infty$=0.0013020495206400003, $\omega_\infty$=114.54981120000002
- CFD mesh generated using Pointwise 
   - 2-D structured O-type mesh, with a resolution equivalent to the "Fine" resolution of the AIAA mesh used in the [NLF1-0416 case](../NLF1-0416/README.md).
- Turbulence / Transition model: SST-2003 with the 1-eq Gamma transition model
- Nalu-Wind version: [f3cecafbdc05e61d0550ff41a30307425ef8197b](https://github.com/Exawind/nalu-wind/commit/f3cecafbdc05e61d0550ff41a30307425ef8197b)

## Running the simulation 

1.  Download the benchmarks repository

	```bash
	$ git clone --recursive git@github.com:Exawind/exawind-benchmarks.git BENCHMARKDIR
	```
    
    Here `BENCHMARKDIR` is the location where you'd like the benchmark repository to be cloned and cases to be run.  After cloning, download the meshes using [DVC](https://dvc.org/doc/start).
    
2.  Run the AOA=0 case
	```bash
    $ cd BENCHMARKDIR/nalu-wind/2D_airfoil_Transition/DU00-W-212/aoa_0/input_files/
    
    # Load any modules/libraries necessary for ExaWind/Nalu-Wind
    
    $ mpirun -np NCPU naluX -i du00w212_F_aoa_0.0.yaml
    ```
    Here `NCPU` is the number of ranks to use in the simulation.  Note the exact `mpirun` command to launch the case may differ between platforms, and might require a submission script to run on various clusters.

3.  Run the AOA=5 case
	```bash
    $ cd BENCHMARKDIR/nalu-wind/2D_airfoil_Transition/DU00-W-212/aoa_5/input_files/
    
    # Load any modules/libraries necessary for ExaWind/Nalu-Wind
    
    $ mpirun -np NCPU naluX -i du00w212_F_aoa_5.0.yaml
    ```
    
## Results: Angle of Attack Sweep

### Comparison of the lift, drag, and pitching moment
<!-- <img src="figures_and_scripts/du_rey_3M.png" alt="Cf" width="1000"> -->
![Cf](figures_and_scripts/du_rey_3M.png)

The figures above show comparisons of the lift, drag, and pitching moment from the experiment, fully turbulent simulations, and transition simulations.  The lift, drag, and pitching moment coefficients are calculated using this jupyter notebook: [clcd_cfd_total.ipynb](figures_and_scripts/clcd_cfd_total.ipynb).

For the lift coefficient, both the fully turbulent and transition simulations show good agreement with the experimental data in the linear range. The transition simulation predicts a slightly higher lift curve slope than the fully turbulent simulation in this range, but the differences are minor. However, neither the transition nor turbulent simulations accurately predict the stall angle of attack due to the limitations of RANS modeling under strong adverse pressure gradients.

For the drag coefficient, the transition simulation captures the laminar drag bucket very well, whereas the fully turbulent simulation overpredicts drag across the entire linear range. At AoA = 0°, the errors in the predicted drag coefficient for the transition and turbulent simulations are -4.35% and 58.81%, respectively. Without the transition model, the drag is over-predicted by almost 60%.

Regarding the pitching moment, the transition simulations show better correlation with the experimental data compared to the fully turbulent simulations in the linear range of the lift curve. After the stall AoA, due to the limitations of the RANS turbulence model, neither simulation captures the pitching moment trends accurately, with both under-predicting the magnitude in the post-stall region.

In summary, the transition model significantly improves the prediction of the aerodynamic coefficeints in the linear range.

In this simulation, each case took approximately 30 minutes to 10,000 iterations, using 4 Picard iterations per time step, on 26 cores of NREL's [Kestrel HPC cluster](https://nrel.github.io/HPC/Documentation/Systems/). It should be noted that the number of cores per case was not determined by Nalu-Wind’s scalability on Kestrel, but simply to accommodate 4 cases on a single node of Kestrel. For more details, refer to the Nalu-Wind log files in the run directory.

## References
[1] Ceyhan Ozlem, Pires Oscar, Munduate Xabier, AVATAR HIGH REYNOLDS NUMBER TESTS ON AIRFOIL DU00-W-212 [https://zenodo.org/records/439827](https://zenodo.org/records/439827)
