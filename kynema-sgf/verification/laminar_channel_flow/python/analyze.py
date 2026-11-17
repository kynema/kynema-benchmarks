"""Analyze generated laminar channel-flow verification cases.

The script reads the matrix manifest created by ``generate_cases.py``, loads
the final AMReX plot file for every selected case, compares axial velocity to
the analytical Poiseuille solution, and writes summaries and convergence
plots. It requires the case-specific ``kynema-sgf-env`` environment,
including yt.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence

import matplotlib.pyplot as plt
import numpy as np
import yt


CASE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = CASE_ROOT / "cases" / "manifest.json"
PLOT_PATTERN = re.compile(r"^plt(?:\d+)?$")
PROFILE_RESOLUTION = 512
PROFILE_FRACTIONS = (0.25, 0.5, 0.75)
FIELD_CANDIDATES = {
    "x": ("velocity_x", "x_velocity", "velocityx", "velx", "u"),
    "y": ("velocity_y", "y_velocity", "velocityy", "vely", "v"),
    "z": ("velocity_z", "z_velocity", "velocityz", "velz", "w"),
}


class AnalysisError(RuntimeError):
    """A validation failure that should stop the analysis."""


class IncompleteCaseError(AnalysisError):
    """A selected case has not produced the output required for analysis."""


@dataclass(frozen=True)
class CaseRecord:
    name: str
    geometry: str
    implementation: str | None
    resolution: int
    base_input: Path
    input_file: str


@dataclass(frozen=True)
class ChannelParameters:
    viscosity: float
    forcing: tuple[float, float, float]
    height: float
    start_point: tuple[float, float, float]
    end_point: tuple[float, float, float]

    @property
    def flow_direction(self) -> tuple[float, float]:
        dx = self.end_point[0] - self.start_point[0]
        dz = self.end_point[2] - self.start_point[2]
        length = math.hypot(dx, dz)
        if length == 0:
            raise AnalysisError("Channel segment start and end points must not coincide.")
        return (dx / length, dz / length)

    @property
    def maximum_velocity(self) -> float:
        direction_x, direction_z = self.flow_direction
        axial_forcing = self.forcing[0] * direction_x + self.forcing[2] * direction_z
        if axial_forcing <= 0:
            raise AnalysisError(
                "Body-force projection along the channel direction must be positive; "
                f"received {axial_forcing:g}."
            )
        return axial_forcing * self.height**2 / (8.0 * self.viscosity)


@dataclass(frozen=True)
class ProfileColumn:
    """Axial-velocity profile along z at one x location on the channel centerline."""

    label: str
    z: np.ndarray
    numerical: np.ndarray
    analytical: np.ndarray


@dataclass
class AnalysisResult:
    name: str
    geometry: str
    implementation: str
    resolution: int
    cell_size: float
    plot_file: str
    samples: int
    absolute_linf_error: float
    relative_linf_error: float
    observed_order: float | None = None
    profiles: list[ProfileColumn] = field(default_factory=list)


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help=f"Generator manifest to analyze (default: {DEFAULT_MANIFEST}).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory for CSV summaries and plots (default: <manifest directory>/analysis).",
    )
    parser.add_argument(
        "--geometries",
        default="flat,slanted,reference",
        help="Comma-separated subset of flat, slanted, reference (default: all).",
    )
    parser.add_argument(
        "--implementations",
        default="default,original",
        help="Comma-separated subset of default, original for IB cases (default: all).",
    )
    return parser


def parse_subset(value: str, valid: Iterable[str], option: str) -> set[str]:
    selected = {item.strip() for item in value.split(",") if item.strip()}
    invalid = selected - set(valid)
    if invalid:
        raise AnalysisError(
            f"{option} contains unsupported value(s): {', '.join(sorted(invalid))}."
        )
    if not selected:
        raise AnalysisError(f"{option} must select at least one value.")
    return selected


def load_manifest(manifest_path: Path) -> tuple[Path, list[CaseRecord]]:
    """Load and validate the generator manifest before opening any output files."""

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise AnalysisError(f"Manifest not found: {manifest_path}") from error
    except json.JSONDecodeError as error:
        raise AnalysisError(f"Manifest is not valid JSON: {manifest_path}: {error}") from error

    if manifest.get("schema_version") != 1:
        raise AnalysisError("Manifest schema_version must be 1.")
    raw_cases = manifest.get("cases")
    if not isinstance(raw_cases, list) or not raw_cases:
        raise AnalysisError("Manifest must contain a non-empty cases list.")

    case_root = Path(manifest.get("case_root", CASE_ROOT)).resolve()
    records: list[CaseRecord] = []
    required_keys = {"name", "geometry", "implementation", "resolution", "base_input", "input_file"}
    for raw_case in raw_cases:
        if not isinstance(raw_case, dict) or required_keys - raw_case.keys():
            raise AnalysisError("Every manifest case must contain all generator fields.")
        base_input = Path(raw_case["base_input"])
        if not base_input.is_absolute():
            base_input = case_root / base_input
        records.append(
            CaseRecord(
                name=str(raw_case["name"]),
                geometry=str(raw_case["geometry"]),
                implementation=(
                    raw_case["implementation"]
                    if raw_case["implementation"] is None
                    else str(raw_case["implementation"])
                ),
                resolution=int(raw_case["resolution"]),
                base_input=base_input.resolve(),
                input_file=str(raw_case["input_file"]),
            )
        )
    return case_root, records


def parse_vector(value: str, key: str) -> tuple[float, float, float]:
    values = tuple(float(item) for item in value.split())
    if len(values) != 3:
        raise AnalysisError(f"{key} must have exactly three values, received {value!r}.")
    return values


def read_input_values(
    input_path: Path, included_paths: frozenset[Path] = frozenset()
) -> dict[str, str]:
    """Read an input file, resolving its ``FILE`` includes in order."""

    resolved_path = input_path.resolve()
    if resolved_path in included_paths:
        raise AnalysisError(f"Recursive input include detected: {resolved_path}")

    try:
        lines = resolved_path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError as error:
        raise AnalysisError(f"Input file not found: {resolved_path}") from error

    values: dict[str, str] = {}
    for line in lines:
        content = line.split("#", 1)[0].strip()
        if "=" not in content:
            continue
        key, value = (part.strip() for part in content.split("=", 1))
        if key == "FILE":
            include_path = resolved_path.parent / value.strip().strip('"\'')
            values.update(read_input_values(include_path, included_paths | {resolved_path}))
        else:
            values[key] = value
    return values


def parse_input_parameters(input_path: Path) -> ChannelParameters:
    """Read the physical values needed by the analytical solution."""

    values = read_input_values(input_path)

    required = {
        "transport.viscosity",
        "BodyForce.magnitude",
        "ChannelBuilder.s1.height_start",
        "ChannelBuilder.s1.segment_start_point",
        "ChannelBuilder.s1.segment_end_point",
    }
    missing = sorted(required - values.keys())
    if missing:
        raise AnalysisError(f"{input_path} is missing required values: {', '.join(missing)}.")

    viscosity = float(values["transport.viscosity"])
    height = float(values["ChannelBuilder.s1.height_start"])
    if viscosity <= 0 or height <= 0:
        raise AnalysisError("Channel viscosity and height must be positive.")
    return ChannelParameters(
        viscosity=viscosity,
        forcing=parse_vector(values["BodyForce.magnitude"], "BodyForce.magnitude"),
        height=height,
        start_point=parse_vector(
            values["ChannelBuilder.s1.segment_start_point"],
            "ChannelBuilder.s1.segment_start_point",
        ),
        end_point=parse_vector(
            values["ChannelBuilder.s1.segment_end_point"],
            "ChannelBuilder.s1.segment_end_point",
        ),
    )


def plot_sort_key(path: Path) -> tuple[int, str]:
    digits = "".join(character for character in path.name if character.isdigit())
    return (int(digits) if digits else -1, path.name)


def latest_plot_file(case_directory: Path) -> Path:
    try:
        candidates = [
            path
            for path in case_directory.iterdir()
            if PLOT_PATTERN.fullmatch(path.name)
            and (path.is_dir() or path.is_file())
            # Step-0 output is only the initial condition, not a solved state.
            and plot_sort_key(path)[0] != 0
        ]
    except FileNotFoundError as error:
        raise IncompleteCaseError(f"Case directory not found: {case_directory}") from error
    if not candidates:
        raise IncompleteCaseError(
            f"No solved AMReX plot files (step > 0) matching plt* were found in {case_directory}. "
            "Run the solver before analyzing this case."
        )
    return max(candidates, key=plot_sort_key)


def select_velocity_field(ds: Any, component: str) -> Any:
    """Select one unambiguous yt field for the requested velocity component."""

    candidates = set(FIELD_CANDIDATES[component])
    matches = [field for field in ds.field_list if field[1].lower() in candidates]
    if not matches:
        available = ", ".join(f"{kind}:{name}" for kind, name in ds.field_list)
        raise AnalysisError(
            f"Could not find a {component}-velocity field. Available fields: {available}."
        )
    if len(matches) == 1:
        return matches[0]

    preferred = [field for field in matches if field[0].lower() in {"boxlib", "amrex", "gas"}]
    if len(preferred) == 1:
        return preferred[0]
    formatted = ", ".join(f"{kind}:{name}" for kind, name in matches)
    raise AnalysisError(
        f"Ambiguous {component}-velocity fields: {formatted}. Update FIELD_CANDIDATES explicitly."
    )


def as_numpy(values: Any) -> np.ndarray:
    """Convert yt arrays to ndarray without retaining unit wrappers."""

    if hasattr(values, "to_value"):
        return np.asarray(values.to_value())
    return np.asarray(values)


def analytical_axial_velocity(
    radial_distance: np.ndarray, maximum_velocity: float, height: float
) -> np.ndarray:
    """Return the Poiseuille profile, with zero velocity outside the channel."""

    profile = maximum_velocity * (1.0 - (2.0 * radial_distance / height) ** 2)
    return np.maximum(profile, 0.0)


def analysis_mask(case: CaseRecord, radial_distance: np.ndarray, height: float) -> np.ndarray:
    """Select the comparison region used by the established post-processors."""

    if case.geometry == "slanted":
        # Retain the small surrounding region used for the periodic slanted
        # channel so that velocity leakage outside the physical channel is
        # measured against the zero analytical velocity.
        return radial_distance <= 0.6 * height
    return radial_distance <= 0.5 * height


def extract_profile_columns(
    x: np.ndarray,
    z: np.ndarray,
    mask: np.ndarray,
    simulated: np.ndarray,
    exact: np.ndarray,
    parameters: ChannelParameters,
) -> list[ProfileColumn]:
    """Sample z-profiles at fixed fractions of the centerline on the mid-y slice."""

    j_mid = x.shape[1] // 2
    x_line = x[:, j_mid, 0]
    columns: list[ProfileColumn] = []
    for fraction in PROFILE_FRACTIONS:
        x_target = parameters.start_point[0] + fraction * (
            parameters.end_point[0] - parameters.start_point[0]
        )
        i_location = int(np.argmin(np.abs(x_line - x_target)))
        in_region = mask[i_location, j_mid, :]
        columns.append(
            ProfileColumn(
                label=f"{fraction:.2f}L",
                z=z[i_location, j_mid, in_region],
                numerical=simulated[i_location, j_mid, in_region],
                analytical=exact[i_location, j_mid, in_region],
            )
        )
    return columns


def analyze_case(case: CaseRecord, case_directory: Path) -> AnalysisResult:
    """Compute error metrics for the final output of one generated case."""

    plot_file = latest_plot_file(case_directory)
    parameters = parse_input_parameters(case_directory / case.input_file)
    try:
        dataset = yt.load(str(plot_file))
    except Exception as error:  # yt raises multiple backend-specific exception classes.
        raise AnalysisError(f"Unable to load {plot_file} with yt: {error}") from error

    try:
        grid = dataset.covering_grid(
            level=0,
            left_edge=dataset.domain_left_edge,
            dims=dataset.domain_dimensions,
        )
        x_velocity = as_numpy(grid[select_velocity_field(dataset, "x")])
        y_velocity = as_numpy(grid[select_velocity_field(dataset, "y")])
        z_velocity = as_numpy(grid[select_velocity_field(dataset, "z")])
        x = as_numpy(grid[("index", "x")])
        z = as_numpy(grid[("index", "z")])
    except AnalysisError:
        raise
    except Exception as error:  # yt grid access errors vary by frontend/version.
        raise AnalysisError(f"Failed to read velocity or coordinate data from {plot_file}: {error}") from error

    expected_shape = tuple(int(value) for value in dataset.domain_dimensions)
    arrays = {"u": x_velocity, "v": y_velocity, "w": z_velocity, "x": x, "z": z}
    mismatched = [name for name, array in arrays.items() if array.shape != expected_shape]
    if mismatched:
        raise AnalysisError(
            f"Unexpected level-0 data shape in {plot_file}; expected {expected_shape}, "
            f"mismatched arrays: {', '.join(mismatched)}."
        )
    if not np.all(np.isfinite(x_velocity)) or not np.all(np.isfinite(z_velocity)):
        raise AnalysisError(f"Velocity data in {plot_file} contain non-finite values.")
    if not np.all(np.isfinite(y_velocity)):
        raise AnalysisError(f"Transverse velocity data in {plot_file} contain non-finite values.")

    direction_x, direction_z = parameters.flow_direction
    normal_x, normal_z = -direction_z, direction_x
    radial_distance = np.abs(
        (x - parameters.start_point[0]) * normal_x
        + (z - parameters.start_point[2]) * normal_z
    )
    interior_mask = analysis_mask(case, radial_distance, parameters.height)
    samples = int(np.count_nonzero(interior_mask))
    if samples == 0:
        raise AnalysisError(
            f"No cells lie inside the error mask for {case.name}; check the channel geometry."
        )

    maximum_velocity = parameters.maximum_velocity
    exact_axial_velocity = analytical_axial_velocity(
        radial_distance, maximum_velocity, parameters.height
    )
    simulated_axial_velocity = x_velocity * direction_x + z_velocity * direction_z
    absolute_linf_error = float(
        np.max(np.abs(simulated_axial_velocity[interior_mask] - exact_axial_velocity[interior_mask]))
    )
    profiles: list[ProfileColumn] = []
    if case.geometry == "slanted" and case.resolution <= PROFILE_RESOLUTION:
        profiles = extract_profile_columns(
            x, z, interior_mask, simulated_axial_velocity, exact_axial_velocity, parameters
        )
    return AnalysisResult(
        name=case.name,
        geometry=case.geometry,
        implementation=case.implementation or "reference",
        resolution=case.resolution,
        cell_size=float(
            (dataset.domain_right_edge[0] - dataset.domain_left_edge[0]).to_value()
            / dataset.domain_dimensions[0]
        ),
        plot_file=str(plot_file),
        samples=samples,
        absolute_linf_error=absolute_linf_error,
        relative_linf_error=absolute_linf_error / maximum_velocity,
        profiles=profiles,
    )


def add_observed_orders(results: Sequence[AnalysisResult]) -> None:
    """Add adjacent-grid observed orders to each homogeneous study series."""

    groups: dict[tuple[str, str], list[AnalysisResult]] = {}
    for result in results:
        groups.setdefault((result.geometry, result.implementation), []).append(result)
    for series in groups.values():
        ordered = sorted(series, key=lambda item: item.resolution)
        for coarse, fine in zip(ordered, ordered[1:]):
            if coarse.absolute_linf_error <= 0 or fine.absolute_linf_error <= 0:
                fine.observed_order = None
                continue
            fine.observed_order = math.log(
                coarse.absolute_linf_error / fine.absolute_linf_error
            ) / math.log(fine.resolution / coarse.resolution)


def write_summary(results: Sequence[AnalysisResult], output_directory: Path) -> list[Path]:
    """Write stable tabular data for review and downstream plotting.

    The flat summary also holds the no-IB reference series, matching the flat plot.
    """

    output_paths: list[Path] = []
    for geometry, members in (
        ("flat", ("flat", "reference")),
        ("slanted", ("slanted",)),
    ):
        subset = [result for result in results if result.geometry in members]
        if subset:
            output_paths.append(write_summary_file(subset, output_directory / f"{geometry}_error_summary.csv"))
    return output_paths


def write_summary_file(results: Sequence[AnalysisResult], output_path: Path) -> Path:
    columns = (
        "name",
        "geometry",
        "implementation",
        "resolution",
        "plot_file",
        "samples",
        "absolute_linf_error",
        "relative_linf_error",
        "observed_order",
    )
    with output_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        for result in sorted(
            results, key=lambda item: (item.geometry, item.implementation, item.resolution)
        ):
            writer.writerow(
                {
                    "name": result.name,
                    "geometry": result.geometry,
                    "implementation": result.implementation,
                    "resolution": result.resolution,
                    "plot_file": result.plot_file,
                    "samples": result.samples,
                    "absolute_linf_error": f"{result.absolute_linf_error:.16e}",
                    "relative_linf_error": f"{result.relative_linf_error:.16e}",
                    "observed_order": "" if result.observed_order is None else f"{result.observed_order:.6f}",
                }
            )
    return output_path


def print_summary(results: Sequence[AnalysisResult]) -> None:
    print("\nError convergence summary")
    print("geometry   implementation  N       relative L_inf       observed order")
    print("---------  --------------  ------  -------------------  --------------")
    for result in sorted(
        results, key=lambda item: (item.geometry, item.implementation, item.resolution)
    ):
        order = "-" if result.observed_order is None else f"{result.observed_order:.3f}"
        print(
            f"{result.geometry:<9}  {result.implementation:<14}  {result.resolution:>6}  "
            f"{result.relative_linf_error:>19.6e}  {order:>14}"
        )


def save_convergence_plot(results: Sequence[AnalysisResult], geometry: str, output_path: Path) -> None:
    selected = [result for result in results if result.geometry == geometry]
    # The no-IB reference is a flat channel, so overlay it on the flat plot when available.
    has_reference = geometry == "flat" and any(result.geometry == "reference" for result in results)
    if has_reference:
        selected.extend(result for result in results if result.geometry == "reference")
    if not selected:
        return

    figure, axis = plt.subplots(figsize=(7, 5))
    groups: dict[str, list[AnalysisResult]] = {}
    for result in selected:
        label = "no-IB reference" if result.geometry == "reference" else result.implementation
        groups.setdefault(label, []).append(result)
    label_order = ["original", "default", "no-IB reference"]
    ordered_labels = sorted(
        groups, key=lambda name: (label_order.index(name) if name in label_order else len(label_order), name)
    )
    for label in ordered_labels:
        series = groups[label]
        series.sort(key=lambda item: item.cell_size)
        axis.loglog(
            [item.cell_size for item in series],
            [item.relative_linf_error for item in series],
            marker="o",
            label=label,
        )

    # Anchor reference slopes at the coarsest cell size, using the geometric
    # mean of the errors there so the lines start among the plotted data.
    cell_sizes = np.array([item.cell_size for item in selected])
    errors = np.array([item.relative_linf_error for item in selected])
    positive = errors > 0
    if np.unique(cell_sizes).size > 1 and np.any(positive):
        coarsest = cell_sizes.max()
        anchor_errors = errors[(cell_sizes == coarsest) & positive]
        if anchor_errors.size == 0:
            anchor_errors = errors[positive]
        anchor = float(np.exp(np.mean(np.log(anchor_errors))))
        trend = np.logspace(np.log10(cell_sizes.min()), np.log10(coarsest), 50)
        reference_slopes = [(0.5, ":"), (1.0, "-.")]
        if has_reference:
            reference_slopes.append((2.0, "--"))
        for slope, style in reference_slopes:
            axis.loglog(
                trend,
                anchor * (trend / coarsest) ** slope,
                linestyle=style,
                color="black",
                linewidth=1.5,
                label=f"Slope: {slope:g}",
            )

    title = "Flat channel convergence" if geometry == "flat" else "Slanted channel convergence"
    axis.set_title(title)
    axis.set_xlabel("Cell Size (h)")
    axis.set_ylabel(r"Relative $L_\infty$ velocity error")
    axis.grid(True, which="both", linestyle=":", linewidth=0.7)
    axis.legend()
    figure.tight_layout()
    figure.savefig(output_path, dpi=200)
    plt.close(figure)


def save_profile_plot(result: AnalysisResult, output_path: Path) -> None:
    """Plot axial-velocity profiles and their error at several centerline locations."""

    errors = [column.numerical - column.analytical for column in result.profiles]
    max_error = max(float(np.max(error)) for error in errors if error.size)
    min_error = min(float(np.min(error)) for error in errors if error.size)
    padding = 0.1 * max(abs(max_error), abs(min_error))
    limits = (min(min_error, -abs(max_error) / 8.0) - padding, max(max_error, 0.0) + padding)

    figure, axes = plt.subplots(len(result.profiles), 2, figsize=(14, 12), squeeze=False)
    for row, (column, error) in enumerate(zip(result.profiles, errors)):
        profile_axis, error_axis = axes[row]
        profile_axis.plot(
            column.analytical, column.z, "o", color="tab:red", markersize=5, label="Analytical"
        )
        profile_axis.plot(
            column.numerical, column.z, "-", color="tab:blue", linewidth=3, label="Numerical"
        )
        profile_axis.set_xlabel("Axial Velocity (m/s)")
        profile_axis.set_ylabel("z (m)")
        profile_axis.set_title(f"Axial Velocity Profile at {column.label}")
        handles, labels = profile_axis.get_legend_handles_labels()
        profile_axis.legend(handles[::-1], labels[::-1])
        profile_axis.grid(True, alpha=0.3)

        error_axis.plot(error, column.z, "-", color="tab:green", linewidth=3)
        error_axis.axvline(x=0, color="k", linestyle="--", alpha=0.5)
        error_axis.set_xlabel("Error in Axial Velocity (m/s)")
        error_axis.set_ylabel("z (m)")
        error_axis.set_title(r"$u_r^{sim} - u_r^{exact}$ at " + column.label)
        error_axis.set_xlim(*limits)
        error_axis.grid(True, alpha=0.3)

    figure.suptitle(
        f"Slanted channel, {result.implementation} implementation, N = {result.resolution}"
    )
    figure.tight_layout()
    figure.savefig(output_path, dpi=150)
    plt.close(figure)


def main() -> int:
    parser = build_argument_parser()
    args = parser.parse_args()
    try:
        selected_geometries = parse_subset(
            args.geometries, ("flat", "slanted", "reference"), "--geometries"
        )
        selected_implementations = parse_subset(
            args.implementations, ("default", "original"), "--implementations"
        )
        manifest_path = args.manifest.resolve()
        _, records = load_manifest(manifest_path)
        records = [
            record
            for record in records
            if record.geometry in selected_geometries
            and (record.geometry == "reference" or record.implementation in selected_implementations)
        ]
        if not records:
            raise AnalysisError("The selected geometry and implementation filters match no manifest cases.")

        output_directory = (args.output_dir or manifest_path.parent / "analysis").resolve()
        output_directory.mkdir(parents=True, exist_ok=True)
        results: list[AnalysisResult] = []
        skipped_cases: list[str] = []
        for record in records:
            try:
                results.append(analyze_case(record, manifest_path.parent / record.name))
            except IncompleteCaseError as error:
                print(f"warning: Skipping {record.name}: {error}", file=sys.stderr)
                skipped_cases.append(record.name)

        if not results:
            raise AnalysisError("None of the selected cases has an AMReX plot file to analyze.")

        add_observed_orders(results)
        summary_paths = write_summary(results, output_directory)
        print_summary(results)

        if "flat" in selected_geometries:
            save_convergence_plot(results, "flat", output_directory / "flat_convergence.png")
        if "slanted" in selected_geometries:
            save_convergence_plot(results, "slanted", output_directory / "slanted_convergence.png")
            for implementation in sorted(
                {result.implementation for result in results if result.profiles}
            ):
                finest = max(
                    (r for r in results if r.profiles and r.implementation == implementation),
                    key=lambda item: item.resolution,
                )
                save_profile_plot(
                    finest,
                    output_directory / f"slanted_{implementation}_velocity_profiles.png",
                )
        if skipped_cases:
            print(f"\nSkipped {len(skipped_cases)} incomplete case(s): {', '.join(skipped_cases)}")
        for summary_path in summary_paths:
            print(f"\nWrote summary: {summary_path}")
        print(f"Wrote plots to: {output_directory}")
        return 0
    except (AnalysisError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())