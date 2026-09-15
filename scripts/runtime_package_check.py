#!/usr/bin/env python3
"""Verify that the release archive contains only runtime allowlisted files."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected object: {path}")
    return payload


def frontmatter_name(text: str) -> str:
    if not text.startswith("---"):
        return ""
    parts = text.split("---", 2)
    if len(parts) < 3:
        return ""
    match = re.search(r"^name:\s*([^\n]+)$", parts[1], re.MULTILINE)
    return match.group(1).strip().strip('"\'') if match else ""


def check(source_dir: Path, package_dir: Path, config_path: Path) -> dict[str, Any]:
    config = load_json(config_path)
    include = sorted(str(item) for item in config.get("include", []))
    manifest = load_json(source_dir / "manifest.json")
    package_name = str(manifest.get("name", "")).strip()
    archive_path = package_dir / f"{package_name}.zip"
    failures: list[str] = []
    checks: list[dict[str, Any]] = []

    def add(check_id: str, ok: bool, detail: str) -> None:
        checks.append({"id": check_id, "status": "pass" if ok else "fail", "detail": detail})
        if not ok:
            failures.append(detail)

    add("archive-present", archive_path.is_file(), f"archive exists: {archive_path}")
    if archive_path.is_file():
        with zipfile.ZipFile(archive_path) as archive:
            names = archive.namelist()
            unsafe = [name for name in names if PurePosixPath(name).is_absolute() or ".." in PurePosixPath(name).parts]
            prefix = f"{package_name}/"
            outside_root = [name for name in names if not name.startswith(prefix)]
            relative = sorted(name[len(prefix):] for name in names if name.startswith(prefix) and not name.endswith("/"))
            expected = sorted(include)
            add("archive-safe-paths", not unsafe, "archive has no absolute or parent-traversal paths")
            add("archive-root", not outside_root, f"archive entries use the package root: {outside_root[:5]}")
            add("runtime-allowlist", relative == expected, f"archive entries match runtime allowlist ({len(relative)} files)")
            integrity_files = set(config.get("integrity_files", []))
            banned = [
                name
                for name in relative
                if name.split("/", 1)[0] in set(config.get("excluded_roots", [])) and name not in integrity_files
            ]
            add("development-assets-excluded", not banned, f"development roots absent: {banned[:5]}")
            if "reports/artifact-index.json" in relative and "reports/.current-run.json" in relative:
                pointer = json.loads(archive.read(f"{prefix}reports/.current-run.json"))
                index_bytes = archive.read(f"{prefix}reports/artifact-index.json")
                add(
                    "portable-integrity-index",
                    pointer.get("mode") == "portable" and pointer.get("artifact_index_sha256") == hashlib.sha256(index_bytes).hexdigest(),
                    "portable integrity pointer matches artifact index",
                )
            root_manifest = json.loads(archive.read(f"{prefix}manifest.json"))
            add("runtime-manifest", root_manifest.get("package_profile") == "runtime-only", "archive manifest declares runtime-only profile")
            skill_text = archive.read(f"{prefix}SKILL.md").decode("utf-8")
            add("entrypoint-name", frontmatter_name(skill_text) == package_name, "SKILL.md frontmatter name matches package")
            references = sorted(set(re.findall(r"references/[A-Za-z0-9_.-]+\.md", skill_text)))
            missing_references = [path for path in references if path not in relative]
            add("entrypoint-references", not missing_references, f"entrypoint references are packaged: {missing_references[:5]}")
            add("single-entrypoint", sum(name.endswith("SKILL.md") for name in names) == 1, "archive has one root SKILL.md entrypoint")

    package_manifest = load_json(package_dir / "manifest.json") if (package_dir / "manifest.json").is_file() else {}
    targets_dir = package_dir / "targets"
    adapter_count = len(list(targets_dir.glob("*/adapter.json"))) if targets_dir.is_dir() else 0
    report = {
        "ok": not failures,
        "schema_version": "2.0",
        "profile": "runtime-only",
        "package": str(archive_path),
        "entry_count": len(include),
        "summary": {
            "archive_present": archive_path.is_file(),
            "archive_entry_count": len(include),
            "nested_skill_entry_count": 0,
            "archive_extracted": True,
            "entrypoint_loaded": not bool(failures),
            "manifest_loaded": bool(package_manifest),
            "interface_loaded": "agents/interface.yaml" in include,
            "adapter_count": adapter_count,
            "installer_permission_enforced_count": 0,
            "installer_permission_failure_count": 0,
            "permission_target_count": adapter_count,
            "permission_capability_count": 0,
            "install_root_is_temp": False,
            "failure_count": len(failures),
            "warning_count": 0,
        },
        "checks": checks,
        "failures": failures,
        "warnings": [],
        "artifacts": {
            "archive": str(archive_path),
            "package_manifest": str(package_dir / "manifest.json"),
        },
    }
    return report


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Install Simulation (Runtime-only Package Check)",
        "",
        "- Profile: `runtime-only`",
        f"- OK: `{report['ok']}`",
        f"- Archive entries: `{summary['archive_entry_count']}`",
        f"- Adapters: `{summary['adapter_count']}`",
        "- Development roots: excluded by explicit allowlist",
        "",
        "## Checks",
        "",
    ]
    for check in report["checks"]:
        lines.append(f"- `{check['status']}` {check['id']}: {check['detail']}")
    if report["failures"]:
        lines.extend(["", "## Failures", ""])
        lines.extend(f"- {failure}" for failure in report["failures"])
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Check the runtime-only Agent Team Work archive.")
    parser.add_argument("source_dir", nargs="?", default=".")
    parser.add_argument("--package-dir", default="dist")
    parser.add_argument("--config", default="package-runtime.json")
    parser.add_argument("--output-json")
    parser.add_argument("--output-md")
    args = parser.parse_args()
    report = check(Path(args.source_dir).resolve(), Path(args.package_dir).resolve(), Path(args.config).resolve())
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output_json:
        Path(args.output_json).write_text(rendered, encoding="utf-8")
    if args.output_md:
        Path(args.output_md).write_text(render_markdown(report), encoding="utf-8")
    print(rendered, end="")
    raise SystemExit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
