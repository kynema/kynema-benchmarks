<!-- This file is automatically compiled into the website. Please copy linked files into .website_src/ paths to enable website rendering -->

<style>
    img,
    .whitebackground img {
        color: #ffffff !important;
    }

    h1,h2,h3 {
        margin-top: 30px;
    }
</style>

# NREL 5MW Rotor in Atmospheric Boundary Layer With Rigid Bodies and Constant Rotation
This benchmark contains a geometry and boundary-layer resolved model of the NREL 5MW reference turbine [1] in a developed near-neutral convective atmospheric boundary layer with a mean hub-height streamwise velocity of 11.4m/s.

- Hub-height: 90m
- Blade Radius: 63m
- Rated Power: 5 MW
- Type: Upwind 3 Blade

<i>Note on run-time: Current results are for 125s simulation time, but by the time of benchmark release, a minimum of 360s will be posted.</i>

## Simulation Setup
- ExaWind driver SHA: [cba5259fc43ddeca67329630d3c84faad90e91bb](https://github.com/Exawind/exawind-driver/commit/cba5259fc43ddeca67329630d3c84faad90e91bb)
- Nalu-Wind SHA: [b9e4ae654b646ecd0501dd6391dc7537239c82db](https://github.com/Exawind/nalu-wind/commit/b9e4ae654b646ecd0501dd6391dc7537239c82db)
- AMR-Wind SHA: [091b07fa3840af98925792290fb8788696290a5e](https://github.com/Exawind/amr-wind/commit/091b07fa3840af98925792290fb8788696290a5e) 

## Freestream Conditions
A near-neutral convective boundary layer precursor was run to feed the domain for this case. Full details are posted here: [Convective ABL for NREL5MW](../../../amr-wind/atmospheric_boundary_layer/convective_abl_nrel5mw/README.md)

10 minute flow statistics:
- Hub-height streamwise velocity: 11.63 m/s
- Hub-height flow direction: ~240.0 degrees

<img src="../../../amr-wind/atmospheric_boundary_layer/convective_abl_nrel5mw/results/avgmetmast_0600.png" alt="10-Minute Average Virtual Met-mast Precursor Results" style="width:800px; background-color: #ffffff;"/>

## CFD Mesh

<img src="figures_and_scripts/mesh-nrel5mw-abl.png" alt="Mesh layout" style="width:800px; background-color: #ffffff;"/>

**Total number of cells: 177,729,426**

The near-body (Nalu-Wind) mesh was created using PGL, pyHyp, and Pointwise. Three blades are connected at the hub, and a tower is included.
- Structured hex mesh
- Cell count: 15,593,362

Off-body (AMR-Wind) mesh was generated using the built-in capability of AMR-Wind. Off-body mesh information is summarized below 
- Mesh topology: Cartesian with AMR
- Domain in x= 0 to 5000m, y=0m to 5000m, z=0m to 1000m
- Initial grid size: 10m
- Finest cell size: 0.625m with 4 AMR levels
- Cell count: 162,136,064

## Results

<img src="figures_and_scripts/rigid_constant_exawind_summary.png" alt="Force and Moment Output" style="width:800px; background-color: #ffffff;"/>

<img src="figures_and_scripts/rigid_constant_exawind_spanwise.png" alt="Force and Moment Output" style="width:800px; background-color: #ffffff;"/>


## Simulation Timings

This benchmark was run on Sandia National Laboratories' machine "Flight" which is comprised of 112 Intel(R) Xeon(R) Platinum 8480+ CPU cores per node. 

### Processor Decomposition: 
- Nalu-Wind: 672 ranks
- AMR-Wind: 6496 ranks

### Timings:
- Mean wall-clock time per timestep for entire simulation: 7.35s 
- Mean wall-clock time per timestep per cell 4.135e-08s

## References

[1]: Jonkman, J. et al, "Definition of a 5-MW Reference Wind Turbine for Offshore System Development" NREL/TP-500-38060, 2009. https://www.nrel.gov/docs/fy09osti/38060.pdf