"""Generate the supported laminar channel-flow verification matrix.

The generated directories are solver-ready and intentionally contain only a
small override input that includes one of the checked-in base inputs. A JSON
manifest records the full study and is consumed by ``analyze.py``.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


CASE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = CASE_ROOT / "cases"
IB_RESOLUTIONS = (32, 64, 128, 256, 512, 1024)
REFERENCE_RESOLUTIONS = (32, 64, 128, 256)
IB_GEOMETRIES = ("flat", "slanted")
IB_IMPLEMENTATIONS = ("default", "original")


@dataclass(frozen=True)
class CaseDefinition:
    """One runnable input in the verification study."""

    name: str
    geometry: str
    implementation: str | None
    resolution: int
    base_input: str
    input_file: str


def parse_csv_values(value: str, valid: Iterable[str], option: str) -> tuple[str, ...]:
    """Parse a comma-separated option and reject unsupported values."""

    requested = tuple(item.strip() for item in value.split(",") if item.strip())
    allowed = set(valid)
    invalid = sorted(set(requested) - allowed)
    if invalid:
        choices = ", ".join(sorted(allowed))
        raise argparse.ArgumentTypeError(
            f"{option} contains unsupported value(s): {', '.join(invalid)}. "
            f"Choose from: {choices}."
        )
    return requested


def parse_resolutions(value: str) -> tuple[int, ...]:
    """Parse positive, unique comma-separated grid resolutions."""

    try:
        resolutions = tuple(int(item.strip()) for item in value.split(",") if item.strip())
    except ValueError as error:
        raise argparse.ArgumentTypeError("resolutions must be comma-separated integers") from error

    if not resolutions or any(resolution <= 0 for resolution in resolutions):
        raise argparse.ArgumentTypeError("resolutions must be positive integers")
    if len(set(resolutions)) != len(resolutions):
        raise argparse.ArgumentTypeError("resolutions must not contain duplicates")
    return resolutions


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--geometries",
        default=",".join((*IB_GEOMETRIES, "reference")),
        help="Comma-separated subset of flat, slanted, reference (default: all).",
    )
    parser.add_argument(
        "--implementations",
        default=",".join(IB_IMPLEMENTATIONS),
        help="Comma-separated subset of default, original for IB cases (default: all).",
    )
    parser.add_argument(
        "--resolutions",
        default=None,
        help=(
            "Optional comma-separated resolutions for IB cases. The no-IB reference "
            "always uses 32,64,128,256."
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory for generated cases (default: {DEFAULT_OUTPUT_DIR}).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace an existing generated case directory and manifest.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the selected matrix without writing files.",
    )
    return parser


def build_case_definitions(
    geometries: tuple[str, ...], implementations: tuple[str, ...], ib_resolutions: tuple[int, ...]
) -> list[CaseDefinition]:
    """Return the selected canonical run matrix."""

    definitions: list[CaseDefinition] = []
    base_inputs = {
        "flat": "cases/flat-ib.inp",
        "slanted": "cases/slanted.inp",
        "reference": "cases/flat-no-ib.inp",
    }

    for geometry in geometries:
        if geometry == "reference":
            for resolution in REFERENCE_RESOLUTIONS:
                name = f"flat-no-ib-n{resolution}"
                definitions.append(
                    CaseDefinition(
                        name=name,
                        geometry=geometry,
                        implementation=None,
                        resolution=resolution,
                        base_input=base_inputs[geometry],
                        input_file="inputs.inp",
                    )
                )
            continue

        for implementation in implementations:
            for resolution in ib_resolutions:
                name = f"{geometry}-{implementation}-n{resolution}"
                definitions.append(
                    CaseDefinition(
                        name=name,
                        geometry=geometry,
                        implementation=implementation,
                        resolution=resolution,
                        base_input=base_inputs[geometry],
                        input_file="inputs.inp",
                    )
                )
    return definitions


def input_contents(case: CaseDefinition, case_directory: Path) -> str:
    """Build the minimal solver override input for one case."""

    shared_base_path = CASE_ROOT / "cases/base.inp"
    geometry_base_path = CASE_ROOT / case.base_input
    relative_shared_base = Path(os.path.relpath(shared_base_path, case_directory)).as_posix()
    relative_geometry_base = Path(os.path.relpath(geometry_base_path, case_directory)).as_posix()
    z_cells = case.resolution if case.geometry != "reference" else case.resolution // 2
    lines = [
        "# Generated by python/generate_cases.py",
        f"FILE = {relative_shared_base}",
        f"FILE = {relative_geometry_base}",
        f"amr.n_cell = {case.resolution} 4 {z_cells}",
    ]
    if case.implementation == "original":
        lines.extend(
            (
                "DragForcing.terrain_use_original_implementation = true",
                "DragForcing.terrain_use_temporal_limiter = false",
            )
        )
    if case.geometry == "slanted" and case.resolution >= 128:
        smoothers = round(4 * (1 + math.log2(case.resolution / 128.0)))
        lines.extend(
            (
                f"mac_proj.num_pre_smooth = {smoothers}",
                f"mac_proj.num_post_smooth = {smoothers}",
            )
        )
    return "\n".join(lines) + "\n"


def write_case(case: CaseDefinition, output_directory: Path, overwrite: bool) -> None:
    """Create a case directory without replacing user simulation data by default."""

    case_directory = output_directory / case.name
    if case_directory.exists():
        if not overwrite:
            raise FileExistsError(
                f"{case_directory} already exists. Use --overwrite only after preserving "
                "any simulation output that should be kept."
            )
        shutil.rmtree(case_directory)

    case_directory.mkdir(parents=True)
    (case_directory / case.input_file).write_text(
        input_contents(case, case_directory), encoding="utf-8"
    )


def write_manifest(cases: list[CaseDefinition], output_directory: Path, overwrite: bool) -> Path:
    """Write the analyzer contract for the generated matrix."""

    manifest_path = output_directory / "manifest.json"
    if manifest_path.exists() and not overwrite:
        raise FileExistsError(
            f"{manifest_path} already exists. Use --overwrite to replace the generated matrix."
        )
    manifest = {
        "schema_version": 1,
        "case_root": str(CASE_ROOT),
        "cases": [asdict(case) for case in cases],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest_path


def main() -> int:
    parser = build_argument_parser()
    args = parser.parse_args()
    try:
        geometries = parse_csv_values(args.geometries, (*IB_GEOMETRIES, "reference"), "--geometries")
        implementations = parse_csv_values(
            args.implementations, IB_IMPLEMENTATIONS, "--implementations"
        )
        resolutions = parse_resolutions(args.resolutions) if args.resolutions else IB_RESOLUTIONS
        cases = build_case_definitions(geometries, implementations, resolutions)

        if not cases:
            parser.error("The selected options do not produce any cases.")

        print(f"Selected {len(cases)} case(s):")
        for case in cases:
            print(f"  {case.name}")

        if args.dry_run:
            print("Dry run: no files were written.")
            return 0

        output_directory = args.output_dir.resolve()
        if output_directory.exists() and not args.overwrite:
            existing = [output_directory / case.name for case in cases]
            existing.append(output_directory / "manifest.json")
            conflicts = [path for path in existing if path.exists()]
            if conflicts:
                raise FileExistsError(
                    "Refusing to overwrite generated content: "
                    + ", ".join(str(path) for path in conflicts)
                    + ". Re-run with --overwrite after preserving simulation output."
                )

        output_directory.mkdir(parents=True, exist_ok=True)
        for case in cases:
            write_case(case, output_directory, args.overwrite)
        manifest_path = write_manifest(cases, output_directory, args.overwrite)
        print(f"Wrote {len(cases)} case(s) and manifest: {manifest_path}")
        return 0
    except (argparse.ArgumentTypeError, FileExistsError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())