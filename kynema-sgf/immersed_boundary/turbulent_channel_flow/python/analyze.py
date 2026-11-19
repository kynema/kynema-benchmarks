"""Analyze the turbulent channel-flow validation cases.

The script reads the native AMReX particle output written by the
``channel_stats`` plane sampler during each case's statistics run. It
averages velocity over the periodic directions and all sampled times, folds
the lower and upper halves of the channel, scales the profiles to wall units,
and compares them with DNS reference data.
"""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


CASE_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = CASE_ROOT / "data"
DENSITY = 0.468793  # kg/m^3, air at 101325 Pa and 750 K
VISCOSITY = 3.57816e-5  # Pa s
VELOCITY_FIELDS = ("velocityx", "velocityy", "velocityz")
PLANE_DECIMALS = 9
DNS_LABELS = {180: "DNS, Kim et al. (1987)", 395: "DNS, Moser et al. (1999)"}


@dataclass(frozen=True)
class Case:
    name: str
    re_tau: int
    delta: float
    dpdx: float
    label: str


CASES = {
    case.name: case
    for case in (
        Case("re180-no-ib", 180, 0.005, -709.79, "Kynema-SGF, no IB"),
        Case("re180-default", 180, 0.005, -709.79, "Kynema-SGF, IB (default)"),
        Case("re395-default", 395, 0.01, -426.121, "Kynema-SGF, IB (default)"),
    )
}


class AnalysisError(RuntimeError):
    """A failure that prevents a case from being analyzed."""


# The particle reader below is adapted from AmrexParticleFile in Kynema-SGF
# tools/amrex_particle.py. Only the real-valued data are loaded, without
# pandas or YAML dependencies.
def parse_header(pdir: Path) -> dict:
    """Parse the header of an AMReX native particle directory."""

    with open(pdir / "Header") as fh:
        fh.readline()  # version string
        ndim = int(fh.readline().strip())
        num_reals = int(fh.readline().strip())
        real_var_names = [fh.readline().strip() for _ in range(num_reals)]
        num_ints = int(fh.readline().strip())
        for _ in range(num_ints):
            fh.readline()
        fh.readline()  # checkpoint flag
        num_particles = int(fh.readline().strip())
        fh.readline()  # next particle ID
        finest_level = int(fh.readline().strip())
        num_grids = [int(fh.readline().strip()) for _ in range(finest_level + 1)]
        grid_info = [
            [[int(ix) for ix in fh.readline().strip().split()] for _ in range(count)]
            for count in num_grids
        ]
    return {
        "ndim": ndim,
        "real_var_names": real_var_names,
        "num_ints": num_ints,
        "num_particles": num_particles,
        "grid_info": grid_info,
    }


def load_real_data(pdir: Path, header: dict) -> np.ndarray:
    """Read particle positions and real-valued fields into one array."""

    nints = header["num_ints"] + 2
    nreals = header["ndim"] + len(header["real_var_names"])
    chunks = []
    for lev, ginfo in enumerate(header["grid_info"]):
        for idx, npts, offset in ginfo:
            if npts < 1:
                continue
            with open(pdir / f"Level_{lev}" / f"DATA_{idx:05d}", "rb") as fh:
                fh.seek(offset + np.dtype(np.int32).itemsize * nints * npts)
                rvals = np.fromfile(fh, dtype=float, count=nreals * npts)
            chunks.append(rvals.reshape(npts, nreals))
    return np.concatenate(chunks)


def read_snapshot(pdir: Path) -> tuple[np.ndarray, np.ndarray]:
    """Return particle z-coordinates and velocity vectors for one output."""

    header = parse_header(pdir)
    names = header["real_var_names"]
    missing = [name for name in VELOCITY_FIELDS if name not in names]
    if missing:
        raise AnalysisError(f"{pdir} is missing fields: {', '.join(missing)}")
    data = load_real_data(pdir, header)
    if len(data) != header["num_particles"]:
        raise AnalysisError(
            f"{pdir}: read {len(data)} particles, header lists {header['num_particles']}."
        )
    columns = [header["ndim"] + names.index(name) for name in VELOCITY_FIELDS]
    return data[:, 2], data[:, columns]


def sampling_outputs(case_dir: Path) -> list[Path]:
    """Return complete sampler outputs, ordered by time step."""

    root = case_dir / "post_processing"
    outputs = [
        path / "particles"
        for path in sorted(root.glob("sampling*"))
        if (path / "sampling_info.yaml").exists() and (path / "particles" / "Header").exists()
    ]
    if not outputs:
        raise AnalysisError(f"No completed sampling output found in {root}.")
    return outputs


def accumulate_statistics(case: Case) -> dict[str, np.ndarray]:
    """Average velocity over x, y, time, and both channel halves."""

    outputs = sampling_outputs(CASE_ROOT / "cases" / case.name)
    print(f"{case.name}: averaging {len(outputs)} sampler outputs")
    planes = None
    for particle_dir in outputs:
        z, velocity = read_snapshot(particle_dir)
        z_planes, inverse = np.unique(np.round(z, PLANE_DECIMALS), return_inverse=True)
        if planes is None:
            planes = z_planes
            counts = np.zeros(len(planes))
            sums = np.zeros((len(planes), 3))
            squares = np.zeros((len(planes), 3))
        elif not np.array_equal(planes, z_planes):
            raise AnalysisError(f"{particle_dir}: sampling planes differ between outputs.")
        counts += np.bincount(inverse, minlength=len(planes))
        for component in range(3):
            values = velocity[:, component]
            sums[:, component] += np.bincount(inverse, weights=values, minlength=len(planes))
            squares[:, component] += np.bincount(
                inverse, weights=values * values, minlength=len(planes)
            )

    wall_distance = np.round(case.delta - np.abs(planes), PLANE_DECIMALS)
    y, fold = np.unique(wall_distance, return_inverse=True)
    folded_counts = np.bincount(fold, weights=counts)
    mean = np.column_stack(
        [np.bincount(fold, weights=sums[:, i]) for i in range(3)]
    ) / folded_counts[:, None]
    mean_square = np.column_stack(
        [np.bincount(fold, weights=squares[:, i]) for i in range(3)]
    ) / folded_counts[:, None]
    rms = np.sqrt(np.maximum(mean_square - mean**2, 0.0))
    return {"y": y, "u_mean": mean[:, 0], "rms": rms}


def friction_velocity(case: Case, stats: dict[str, np.ndarray], source: str) -> float:
    """Compute u_tau from the imposed pressure gradient or the wall gradient."""

    if source == "gradP":
        return float(np.sqrt(-case.dpdx * case.delta / DENSITY))
    y0, y1 = stats["y"][:2]
    u0, u1 = stats["u_mean"][:2]
    # Quadratic U(y) = a y + b y^2 through the wall and the two nearest planes.
    wall_gradient = (u0 * y1**2 - u1 * y0**2) / (y0 * y1 * (y1 - y0))
    return float(np.sqrt(VISCOSITY * abs(wall_gradient) / DENSITY))


def read_reference(name: str) -> np.ndarray:
    return np.genfromtxt(DATA_DIR / f"{name}.csv", delimiter=",", skip_header=1)


def plot_mean_velocity(re_tau: int, results: list[dict], output: Path) -> None:
    reference = read_reference(f"Re{re_tau}_MeanVelocity")
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.semilogx(
        reference[::2, 0], reference[::2, 1], "ko", fillstyle="none", markersize=8,
        label=DNS_LABELS[re_tau],
    )
    for result in results:
        ax.semilogx(result["y_plus"], result["U_plus"], "-", linewidth=2, label=result["label"])
    y_ref = reference[:, 0]
    viscous = y_ref[y_ref < 13.4]
    log_region = y_ref[y_ref > 9]
    ax.semilogx(viscous, viscous, "k--", alpha=0.6, label="$u^+ = y^+$")
    ax.semilogx(
        log_region, 2.5 * np.log(log_region) + 5.5, "k:", alpha=0.6,
        label=r"$u^+ = 2.5 \ln(y^+) + 5.5$",
    )
    ax.set_xlabel("$y^+$", fontsize=16)
    ax.set_ylabel("$u^+$", fontsize=16)
    ax.set_title(rf"Mean velocity, Re$_\tau$ = {re_tau}", fontsize=16)
    ax.set_xlim(1, max(200.0, y_ref.max()))
    ax.set_ylim(0, 20 if re_tau == 180 else 25)
    ax.tick_params(labelsize=14)
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=11, loc="upper left")
    fig.tight_layout()
    fig.savefig(output, dpi=150)
    plt.close(fig)


def plot_rms_velocity(re_tau: int, results: list[dict], output: Path) -> None:
    # The reference RMS files are stored in Kynema-SGF orientation:
    # U is streamwise, V is spanwise, and W is wall-normal.
    components = (
        ("U", "urms_plus", "$u'^+$ (streamwise)"),
        ("V", "vrms_plus", "$v'^+$ (spanwise)"),
        ("W", "wrms_plus", "$w'^+$ (wall-normal)"),
    )
    fig, ax = plt.subplots(figsize=(8, 6))
    colors = {}
    y_max = 0.0
    for component, _, label in components:
        reference = read_reference(f"Re{re_tau}_RMS_{component}")
        y_max = max(y_max, reference[:, 0].max())
        line = ax.plot(
            reference[:, 0], reference[:, 1], "o", fillstyle="none", markersize=8,
            label=f"{DNS_LABELS[re_tau]}, {label}",
        )
        colors[component] = line[0].get_color()
    linestyles = ("-", "--", "-.", ":")
    for index, result in enumerate(results):
        style = linestyles[index % len(linestyles)]
        for component, key, _ in components:
            ax.plot(result["y_plus"], result[key], style, color=colors[component])
        ax.plot([], [], style, color="k", label=result["label"])
    ax.set_xlabel("$y^+$", fontsize=16)
    ax.set_ylabel("RMS velocity in wall units", fontsize=16)
    ax.set_title(rf"RMS velocity, Re$_\tau$ = {re_tau}", fontsize=16)
    ax.set_xlim(0, 1.02 * y_max)
    ax.set_ylim(0, 3)
    ax.tick_params(labelsize=14)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10, loc="upper right")
    fig.tight_layout()
    fig.savefig(output, dpi=150)
    plt.close(fig)


def write_profiles(result: dict, output: Path) -> None:
    keys = ("y", "y_plus", "U_plus", "urms_plus", "vrms_plus", "wrms_plus")
    with output.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(keys)
        writer.writerows(zip(*(result[key] for key in keys)))


def analyze_case(case: Case, utau_source: str) -> dict:
    stats = accumulate_statistics(case)
    u_tau = friction_velocity(case, stats, utau_source)
    viscous_length = VISCOSITY / (DENSITY * u_tau)
    print(f"{case.name}: u_tau = {u_tau:.5g} m/s ({utau_source}), "
          f"Re_tau = {case.delta / viscous_length:.1f}")
    return {
        "label": case.label,
        "re_tau": case.re_tau,
        "u_tau": u_tau,
        "y": stats["y"],
        "y_plus": stats["y"] / viscous_length,
        "U_plus": stats["u_mean"] / u_tau,
        "urms_plus": stats["rms"][:, 0] / u_tau,
        "vrms_plus": stats["rms"][:, 1] / u_tau,
        "wrms_plus": stats["rms"][:, 2] / u_tau,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cases", default=",".join(CASES),
        help=f"Comma-separated subset of {', '.join(CASES)} (default: all).",
    )
    parser.add_argument(
        "--utau-source", choices=("gradP", "gradU"), default="gradP",
        help="Friction velocity from the imposed pressure gradient (gradP, default) "
             "or a quadratic fit of the wall velocity gradient (gradU).",
    )
    parser.add_argument(
        "--output-dir", type=Path, default=CASE_ROOT / "cases" / "analysis",
        help="Directory for CSV and PNG outputs (default: cases/analysis).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    names = [name.strip() for name in args.cases.split(",") if name.strip()]
    unknown = sorted(set(names) - set(CASES))
    if unknown:
        print(f"Unknown case(s): {', '.join(unknown)}", file=sys.stderr)
        return 2

    args.output_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for name in names:
        try:
            result = analyze_case(CASES[name], args.utau_source)
        except AnalysisError as error:
            print(f"Skipping {name}: {error}", file=sys.stderr)
            continue
        write_profiles(result, args.output_dir / f"{name}_profiles.csv")
        results.append(result)

    if not results:
        print("No cases were analyzed.", file=sys.stderr)
        return 1
    for re_tau in sorted({result["re_tau"] for result in results}):
        selected = [result for result in results if result["re_tau"] == re_tau]
        plot_mean_velocity(re_tau, selected, args.output_dir / f"re{re_tau}_mean_velocity.png")
        plot_rms_velocity(re_tau, selected, args.output_dir / f"re{re_tau}_rms_velocity.png")
    print(f"Wrote analysis outputs to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
