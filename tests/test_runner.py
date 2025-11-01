#!/usr/bin/env python3
"""Utility script for running strategy test suites with common options."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
STRATEGY_TEST_DIR = PROJECT_ROOT / "tests"


def run_command(cmd: List[str]) -> int:
    """Execute a command and return the exit status."""

    banner = "=" * 70
    print(f"\n{banner}\nRunning: {' '.join(cmd)}\n{banner}\n")
    return subprocess.run(cmd, check=False).returncode


def expand_file_option(selected: str) -> List[str]:
    """Translate the file selection flag into concrete pytest targets."""

    if selected == "all":
        return [str(STRATEGY_TEST_DIR)]

    pattern_map = {
        "factory": "test_strategy_factory_*.py",
        "run_strategies": "test_run_strategies_*.py",
    }

    pattern = pattern_map[selected]
    matches = sorted(STRATEGY_TEST_DIR.glob(pattern))
    if not matches:
        raise FileNotFoundError(
            f"No tests matched pattern '{pattern}' in '{STRATEGY_TEST_DIR}'."
        )
    return [str(match) for match in matches]


def build_markers(args: argparse.Namespace) -> str | None:
    """Combine requested marker expressions into a single pytest -m value."""

    markers: List[str] = []
    if args.markers:
        markers.append(args.markers)
    if args.quick:
        markers.append("not slow")
    if not markers:
        return None
    return " and ".join(markers)


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run strategy-related unit tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose pytest output")
    parser.add_argument(
        "-c",
        "--coverage",
        action="store_true",
        help="Generate coverage reports (requires pytest-cov)",
    )
    parser.add_argument(
        "-m",
        "--markers",
        type=str,
        help="Run tests matching the given pytest marker expression",
    )
    parser.add_argument(
        "-f",
        "--file",
        choices=["factory", "run_strategies", "all"],
        default="all",
        help="Target a specific subset of strategy tests",
    )
    parser.add_argument(
        "-p",
        "--parallel",
        action="store_true",
        help="Run tests in parallel using pytest-xdist",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Exclude tests marked as slow",
    )

    args = parser.parse_args(argv)

    cmd: List[str] = [sys.executable, "-m", "pytest"]

    if args.verbose:
        cmd.append("-v")

    if args.coverage:
        cmd.extend(["--cov=src", "--cov-report=html", "--cov-report=term"])

    marker_expr = build_markers(args)
    if marker_expr:
        cmd.extend(["-m", marker_expr])

    if args.parallel:
        cmd.extend(["-n", "auto"])

    cmd.extend(expand_file_option(args.file))

    exit_code = run_command(cmd)

    banner = "=" * 70
    print(f"\n{banner}")
    print("All tests passed!" if exit_code == 0 else "Some tests failed!")
    print(f"{banner}\n")

    if args.coverage:
        print("Coverage report: htmlcov/index.html")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())

