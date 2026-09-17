#!/usr/bin/env python3
"""Run the package's dependency-free release checks."""

from __future__ import annotations

import argparse
import json
import py_compile
import re
import subprocess
import sys
from pathlib import Path


SCRIPT_INTERFACE = "cli"
SCRIPT_INTERFACE_REASON = "Runs local, dependency-free route, syntax, and package-shape checks before release."
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TARGETS = ["route-contract", "python-compile", "package-shape", "runtime-package", "runtime-package-state", "revision-state", "discussion-state"]


def route_contract() -> None:
    entry = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    front = entry.split("---", 2)
    if len(front) != 3 or front[0].strip():
        raise AssertionError("SKILL.md frontmatter is missing")
    if "name: agent-team-work" not in front[1]:
        raise AssertionError("SKILL.md name does not match the package")
    if not re.search(r"^description:\s*.+$", front[1], re.MULTILINE):
        raise AssertionError("SKILL.md description is missing")
    for rel in [
        "references/workflow.md",
        "references/codex-tools.md",
        "references/team-protocol.md",
        "scripts/validate_team_state.py",
    ]:
        if rel not in entry and not (ROOT / rel).exists():
            raise AssertionError(f"required route resource is missing: {rel}")


def python_compile() -> None:
    paths = sorted((ROOT / "scripts").glob("*.py")) + sorted((ROOT / "evals").glob("*.py"))
    for path in paths:
        py_compile.compile(str(path), doraise=True)


def package_shape() -> None:
    required = ["SKILL.md", "README.md", "LICENSE", "manifest.json", "agents/interface.yaml", "dist/agent-team-work.zip"]
    missing = [rel for rel in required if not (ROOT / rel).is_file()]
    if missing:
        raise AssertionError("missing release files: " + ", ".join(missing))
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("name") != "agent-team-work" or manifest.get("version") != "0.2.0":
        raise AssertionError("manifest identity does not match the release")


def revision_state() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "evals" / "revision_cycle_state_test.py")],
        cwd=ROOT,
        check=False,
    )
    if result.returncode:
        raise AssertionError("revision-cycle-state regression tests failed")


def discussion_state() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "evals" / "discussion_round_state_test.py")],
        cwd=ROOT,
        check=False,
    )
    if result.returncode:
        raise AssertionError("discussion-round-state regression tests failed")


def runtime_package() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "runtime_package_check.py"), str(ROOT), "--package-dir", str(ROOT / "dist")],
        cwd=ROOT,
        check=False,
    )
    if result.returncode:
        raise AssertionError("runtime-only package check failed")


def runtime_package_state() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "evals" / "runtime_package_state_test.py")],
        cwd=ROOT,
        check=False,
    )
    if result.returncode:
        raise AssertionError("runtime-package-state regression tests failed")


CHECKS = {
    "route-contract": route_contract,
    "python-compile": python_compile,
    "package-shape": package_shape,
    "runtime-package": runtime_package,
    "runtime-package-state": runtime_package_state,
    "revision-state": revision_state,
    "discussion-state": discussion_state,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run dependency-free agent-team-work release checks.")
    parser.add_argument("targets", nargs="*")
    args = parser.parse_args()
    targets = args.targets or DEFAULT_TARGETS
    invalid = [target for target in targets if target not in CHECKS]
    if invalid:
        parser.error("unknown target(s): " + ", ".join(invalid))
    for target in targets:
        CHECKS[target]()
        print(f"PASS {target}")
    print(f"Completed {len(targets)} CI checks.")


if __name__ == "__main__":
    main()
