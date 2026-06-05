#!/usr/bin/env python3
"""
compare_wrf_vars.py
-------------------
Compare variable names in wrf2d and wrf3d output files
between a pre-restart file (before 2-20) and a post-restart
file (from the resumed simulation at 3-1).

Usage:
    python compare_wrf_vars.py \
        --pre2d  /path/to/wrf2d_d01_1984-02-19_00:00:00 \
        --pre3d  /path/to/wrf3d_d01_1984-02-19_00:00:00 \
        --post2d /path/to/wrf2d_d01_1984-03-01_00:00:00 \
        --post3d /path/to/wrf3d_d01_1984-03-01_00:00:00

Or edit the FILE PATHS section below and run without arguments.
"""

import argparse
import sys
from netCDF4 import Dataset

# ── FILE PATHS (edit these if not using CLI arguments) ─────────────────────────
PRE_2D  = "/path/to/wrf2d_d01_1984-02-19_00:00:00"   # last file before 2-20
PRE_3D  = "/path/to/wrf3d_d01_1984-02-19_00:00:00"
POST_2D = "/path/to/wrf2d_d01_1984-03-01_00:00:00"   # first file after resume
POST_3D = "/path/to/wrf3d_d01_1984-03-01_00:00:00"
# ──────────────────────────────────────────────────────────────────────────────


def get_vars(filepath):
    """Return sorted list of variable names in a NetCDF file."""
    try:
        with Dataset(filepath, "r") as ds:
            return sorted(ds.variables.keys())
    except FileNotFoundError:
        print(f"  [ERROR] File not found: {filepath}")
        sys.exit(1)
    except Exception as e:
        print(f"  [ERROR] Could not open {filepath}: {e}")
        sys.exit(1)


def compare(label, pre_file, post_file):
    """Compare variable lists between two files and print a clear report."""
    print(f"\n{'='*65}")
    print(f"  Comparing {label} variables")
    print(f"{'='*65}")
    print(f"  PRE  (before 2-20) : {pre_file}")
    print(f"  POST (resumed 3-1) : {post_file}")
    print()

    pre_vars  = set(get_vars(pre_file))
    post_vars = set(get_vars(post_file))

    only_in_pre  = pre_vars  - post_vars
    only_in_post = post_vars - pre_vars
    common       = pre_vars  & post_vars

    # ── Summary ────────────────────────────────────────────────────────────────
    print(f"  Variables in PRE  file : {len(pre_vars)}")
    print(f"  Variables in POST file : {len(post_vars)}")
    print(f"  Variables in common    : {len(common)}")

    # ── Result ─────────────────────────────────────────────────────────────────
    if not only_in_pre and not only_in_post:
        print(f"\n  ✅  IDENTICAL — all variable names match perfectly.\n")
    else:
        print(f"\n  ❌  MISMATCH detected!\n")
        if only_in_pre:
            print(f"  Variables ONLY in PRE (missing after resume) [{len(only_in_pre)}]:")
            for v in sorted(only_in_pre):
                print(f"      - {v}")
        if only_in_post:
            print(f"\n  Variables ONLY in POST (new after resume) [{len(only_in_post)}]:")
            for v in sorted(only_in_post):
                print(f"      + {v}")

    print(f"\n  All shared variables ({len(common)}):")
    for v in sorted(common):
        print(f"      {v}")

    return len(only_in_pre) == 0 and len(only_in_post) == 0


def parse_args():
    p = argparse.ArgumentParser(description="Compare WRF output variable names across a restart.")
    p.add_argument("--pre2d",  default=None, help="wrf2d file BEFORE restart (e.g. 1984-02-19)")
    p.add_argument("--pre3d",  default=None, help="wrf3d file BEFORE restart")
    p.add_argument("--post2d", default=None, help="wrf2d file AFTER  restart (e.g. 1984-03-01)")
    p.add_argument("--post3d", default=None, help="wrf3d file AFTER  restart")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()

    pre2d  = args.pre2d  or PRE_2D
    pre3d  = args.pre3d  or PRE_3D
    post2d = args.post2d or POST_2D
    post3d = args.post3d or POST_3D

    ok2d = compare("wrf2d", pre2d, post2d)
    ok3d = compare("wrf3d", pre3d, post3d)

    print(f"\n{'='*65}")
    print("  FINAL RESULT")
    print(f"{'='*65}")
    print(f"  wrf2d : {'✅ MATCH' if ok2d else '❌ MISMATCH'}")
    print(f"  wrf3d : {'✅ MATCH' if ok3d else '❌ MISMATCH'}")

    if ok2d and ok3d:
        print("\n  ✅ Both wrf2d and wrf3d variable sets are identical across")
        print("     the restart boundary. Safe to proceed!\n")
    else:
        print("\n  ❌ One or more files have variable mismatches. Review the")
        print("     output above and check your namelist.input settings.\n")

    sys.exit(0 if (ok2d and ok3d) else 1)
