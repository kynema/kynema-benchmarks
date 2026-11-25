"""Check for drift in the bulk velocity during a case's statistics window.

Compares the bulk velocity averaged over the first and last quarters of the
sampler outputs. Cases are processed one after another; within a case, the
sampler outputs are read in parallel, one per worker process, so peak memory
scales with the number of workers.

Usage (from the turbulent_channel_flow directory):
    python python/drift.py --cases re180-default --nprocs 16
"""

from __future__ import annotations

import argparse
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from functools import partial

import numpy as np

import analyze as a


def bulk_velocity(case: a.Case, particle_dir) -> float:
    """Return the bulk velocity of one sampler output, integrating wall to wall."""

    z, velocity = a.read_snapshot(particle_dir)
    planes, inverse = np.unique(np.round(z, a.PLANE_DECIMALS), return_inverse=True)
    u_mean = np.bincount(inverse, weights=velocity[:, 0]) / np.bincount(inverse)
    zz = np.r_[-case.delta, planes, case.delta]
    uu = np.r_[0.0, u_mean, 0.0]
    return float(np.sum(0.5 * (uu[1:] + uu[:-1]) * np.diff(zz)) / (2 * case.delta))


def check_case(case: a.Case, nprocs: int) -> bool:
    try:
        outputs = a.sampling_outputs(a.CASE_ROOT / "cases" / case.name)
    except a.AnalysisError as error:
        print(f"{case.name}: {error}", file=sys.stderr)
        return False
    if len(outputs) < 4:
        print(f"{case.name}: need at least 4 sampler outputs, found {len(outputs)}.",
              file=sys.stderr)
        return False

    workers = min(nprocs, len(outputs))
    print(f"{case.name}: reading {len(outputs)} sampler outputs with {workers} worker(s), "
          f"{outputs[0].parent.name} to {outputs[-1].parent.name}", flush=True)
    with ProcessPoolExecutor(max_workers=workers) as executor:
        # map() preserves the time order of the outputs.
        ub = np.array(list(executor.map(partial(bulk_velocity, case), outputs)))
    n = len(ub) // 4
    first, last = ub[:n].mean(), ub[-n:].mean()
    print(f"{case.name}: U_b {first:.2f} -> {last:.2f} m/s "
          f"({100 * (last / first - 1):+.1f}%) over the first and last {n} outputs",
          flush=True)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cases", default=",".join(a.CASES),
        help=f"Comma-separated subset of {', '.join(a.CASES)} (default: all).",
    )
    parser.add_argument(
        "--nprocs", type=int,
        default=int(os.environ.get("SLURM_CPUS_PER_TASK", os.cpu_count() or 1)),
        help="Number of worker processes (default: $SLURM_CPUS_PER_TASK, "
             "else the number of CPUs).",
    )
    args = parser.parse_args()

    names = [name.strip() for name in args.cases.split(",") if name.strip()]
    unknown = sorted(set(names) - set(a.CASES))
    if unknown:
        print(f"Unknown case(s): {', '.join(unknown)}", file=sys.stderr)
        return 2

    results = [check_case(a.CASES[name], max(args.nprocs, 1)) for name in names]
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
