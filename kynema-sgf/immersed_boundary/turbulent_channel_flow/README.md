<!-- This file is compiled into the website through .website_src. -->

# Turbulent channel flow with immersed boundaries

This validation case compares wall-resolved large-eddy simulations (LES) of
pressure-driven turbulent channel flow with direct numerical simulation (DNS)
data at friction Reynolds numbers $Re_\tau = 180$ and $Re_\tau = 395$. The
channel walls are represented with `ChannelBuilder` immersed boundaries (IB)
and the `DragForcing` wall model. A channel with no-slip domain walls and no
IB provides a solver reference at $Re_\tau = 180$.

## Contents

- [Channel configurations](#channel-configurations)
- [Validation matrix](#validation-matrix)
- [Reference data](#reference-data)
- [Statistics](#statistics)
- [Prerequisites](#prerequisites)
- [Run the solver](#run-the-solver)
- [Analyze statistics](#analyze-statistics)
- [Outputs](#outputs)
- [Results](#results)

## Channel configurations

Flow is in the $x$ direction, $y$ is spanwise, and $z$ is wall-normal. The
DNS coordinate system uses $y$ as the wall-normal direction and $z$ as the
spanwise direction, so the DNS $v$ and $w$ components correspond to the
Kynema-SGF $w$ and $v$ components, respectively.

![Coordinate systems](figures/CoordinateSystem.png)

The walls are located at $z = \pm\delta$, where $\delta$ is the channel
half-height. The domain is periodic in $x$ and $y$. In the no-IB case, the
walls are the no-slip domain boundaries at $z = \pm\delta$. In the IB cases,
the domain is extended in $z$ and the `ChannelBuilder` walls at
$z = \pm\delta$ coincide with level 0 cell faces. Flow is driven by a uniform
body force equal to $-\frac{1}{\rho}\frac{dp}{dx}$.

The fluid is air at 101325 Pa and 750 K:

| Property | Value |
| --- | --- |
| Density, $\rho$ | 0.468793 kg/m$^3$ |
| Dynamic viscosity, $\mu$ | 3.57816e-5 Pa s |
| Subgrid model | Smagorinsky, $C_s = 0.1$ |

The flow characteristics follow from
$u_\tau = Re_\tau\,\mu / (\rho\,\delta)$,
$\frac{dp}{dx} = -\rho u_\tau^2 / \delta$, and
$t^* = \delta / u_\tau$:

| Quantity | $Re_\tau = 180$ | $Re_\tau = 395$ |
| --- | --- | --- |
| Half-height, $\delta$ | 0.005 m | 0.01 m |
| Domain, $L_x \times L_y$ | $6.24\delta \times 3.12\delta$ | $6.24\delta \times 3.12\delta$ |
| Friction velocity, $u_\tau$ | 2.7478 m/s | 3.0149 m/s |
| Pressure gradient, $dp/dx$ | -709.79 Pa/m | -426.121 Pa/m |
| Body force | 1514.08 m/s$^2$ | 908.975 m/s$^2$ |
| Viscous time, $t^*$ | 1.8197e-3 s | 3.3168e-3 s |
| Spin-up | $20t^*$ (0.036393 s) | $30t^*$ (0.099505 s) |
| Statistics | $10t^*$ (to 0.054590 s) | $10t^*$ (to 0.132674 s) |

Each mesh uses one level of refinement near each wall. Grid spacing in wall
units is:

| Mesh | $Re_\tau = 180$ | $Re_\tau = 395$ |
| --- | --- | --- |
| Level 0 cells, no IB | $192 \times 96 \times 56$ | N/A |
| Level 0 cells, IB | $192 \times 96 \times 64$ | $200 \times 96 \times 72$ |
| Level 0 $\Delta x^+, \Delta y^+, \Delta z^+$ | 5.85, 5.85, 6.43 | 12.32, 12.84, 12.34 |
| Level 1 $\Delta x^+, \Delta y^+, \Delta z^+$ | 2.93, 2.93, 3.21 | 6.16, 6.42, 6.17 |
| Level 1 extent from each wall | $z^+ \leq 45$ | $z^+ \leq 111$ |

In the IB cases, level 1 also covers the solid cells between the wall and the
domain boundary.

## Validation matrix

| Case | $Re_\tau$ | Walls | Directory |
| --- | --- | --- | --- |
| No IB | 180 | No-slip domain boundaries | `cases/re180-no-ib` |
| IB (`default`) | 180 | `ChannelBuilder` with `DragForcing` | `cases/re180-default` |
| IB (`default`) | 395 | `ChannelBuilder` with `DragForcing` | `cases/re395-default` |

The `default` configuration uses the current `DragForcing` implementation,
with `DragForcing.terrain_use_original_implementation = false`,
`DragForcing.terrain_use_original_limiter = false`, and
`DragForcing.bc_forcing_time_factor = 1`. The IB cases set
`ABL.surface_roughness_z0 = 0.00001`. The $Re_\tau = 395$ case also sets
`ChannelBuilder.initialize_drag_cells = true`.

Shared solver settings are in `cases/base.inp`. Each case directory contains:

- `inputs.inp`, which includes `base.inp` and sets the domain, forcing, walls,
  mesh, stop time, and the plane sampler used to collect statistics. Sampling
  starts after the spin-up time through `sampling.output_time_delay`.

## Reference data

The reference data in `data/` are DNS profiles from:

- $Re_\tau = 180$: Kim, J., Moin, P., and Moser, R. (1987). Turbulence
  statistics in fully developed channel flow at low Reynolds number.
  *Journal of Fluid Mechanics*, 177, 133-166.
- $Re_\tau = 395$: Moser, R. D., Kim, J., and Mansour, N. N. (1999). Direct
  numerical simulation of turbulent channel flow up to $Re_\tau = 590$.
  *Physics of Fluids*, 11(4), 943-945.

`Re<Re_tau>_MeanVelocity.csv` contains $u^+$ versus $y^+$. The
`Re<Re_tau>_RMS_<component>.csv` files contain RMS velocity in wall units
using the Kynema-SGF orientation: `U` is streamwise, `V` is spanwise, and
`W` is wall-normal.

## Statistics

The `channel_stats` plane sampler writes velocity on planes parallel to the
walls every $0.1t^*$ (`sampling.output_time_interval`), starting at the end of
the spin-up (`sampling.output_time_delay`). This gives 100 samples over the
$10t^*$ statistics window. The planes are located at level 1 and level 0 cell
centers between $z = -\delta$ and $z = \delta$.

For each plane, the analyzer accumulates the sample count, sum, and sum of
squares of each velocity component over all sampled points and all sampler
outputs. It combines planes with the same distance from the nearest wall,
$y = \delta - |z|$, and computes

$$
\langle u_i \rangle = \frac{1}{N}\sum u_i,
\qquad
u_{i,\mathrm{rms}} = \sqrt{\frac{1}{N}\sum u_i^2 - \langle u_i \rangle^2}.
$$

Profiles are scaled with $y^+ = \rho u_\tau y / \mu$, $u^+ = \langle u \rangle / u_\tau$,
and $u_{i,\mathrm{rms}}^+ = u_{i,\mathrm{rms}} / u_\tau$. By default, the
friction velocity is computed from the imposed pressure gradient,

$$
u_\tau = \sqrt{-\frac{\delta}{\rho}\frac{dp}{dx}}.
$$

With `--utau-source gradU`, it is instead computed from the wall shear stress
$\tau_w = \mu\,|dU/dy|_{y=0}$, where the wall gradient comes from a quadratic
fit through the wall and the two planes nearest to it:

$$
\left.\frac{dU}{dy}\right|_{y=0} = \frac{U_0 y_1^2 - U_1 y_0^2}{y_0 y_1 (y_1 - y_0)},
\qquad
u_\tau = \sqrt{\tau_w / \rho}.
$$

## Prerequisites

Use the `kynema-sgf-env` conda environment shared by the immersed boundary
cases. It contains the Python, NumPy, and Matplotlib dependencies required by
the analyzer.

From this directory, create the environment when necessary and activate it:

```bash
conda env create -f ../kynema-sgf-env.yml
conda activate kynema-sgf-env
```

An available Kynema-SGF executable is also required. Solver launch and
resource selection are controlled by the user or the target HPC system.

## Run the solver

Each case runs in a single job from its case directory. The run spins up the
turbulence from a perturbed initial condition and then continues to the stop
time; the sampler begins writing statistics data at the end of the spin-up.
For example:

```bash
cd cases/re180-default
srun -N 2 --ntasks-per-node=50 kynema_sgf inputs.inp
```

The run writes sampler outputs in `post_processing/sampling*/`. Samples taken
before the spin-up time are not written.

## Analyze statistics

After the runs complete, run from this directory:

```bash
python python/analyze.py
```

The analyzer reads every completed sampler output in each case's
`post_processing/` directory with a particle reader adapted from
Kynema-SGF's `tools/amrex_particle.py`. Cases without sampler output are
reported and skipped. Options:

- `--cases re180-no-ib,re180-default` analyzes a subset of cases.
- `--utau-source gradU` computes $u_\tau$ from the wall velocity gradient.
- `--output-dir PATH` changes the output directory.

## Outputs

Analysis results are written to `cases/analysis/` by default:

- `<case>_profiles.csv` contains the wall distance $y$, $y^+$, $u^+$, and the
  streamwise, spanwise, and wall-normal RMS velocity in wall units.
- `re<Re_tau>_mean_velocity.png` compares $u^+$ with the DNS data, the
  viscous sublayer $u^+ = y^+$, and the log law $u^+ = 2.5\ln y^+ + 5.5$.
- `re<Re_tau>_rms_velocity.png` compares RMS velocity components with the
  DNS data.

The analyzer also prints the number of sampler outputs averaged and the
friction velocity used for each case.

## Results

Results will be added after these cases are run with a current Kynema-SGF
release.
