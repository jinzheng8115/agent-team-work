#!/usr/bin/env python3
"""Build the small runtime-only archive from an explicit source allowlist."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "package-runtime.json"


def json_bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def write_entry(archive: zipfile.ZipFile, name: str, content: bytes) -> None:
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    archive.writestr(info, content)


def load_config(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("profile") != "runtime-only":
        raise ValueError("package runtime config must declare profile=runtime-only")
    include = payload.get("include")
    if not isinstance(include, list) or not include or any(not isinstance(item, str) for item in include):
        raise ValueError("package runtime config must contain a non-empty include list")
    if len(set(include)) != len(include):
        raise ValueError("package runtime config contains duplicate include paths")
    unsafe = [item for item in include if PurePosixPath(item).is_absolute() or ".." in PurePosixPath(item).parts]
    if unsafe:
        raise ValueError(f"package runtime config contains unsafe include paths: {unsafe[:5]}")
    return payload


def runtime_manifest(source: dict[str, Any], include: list[str]) -> dict[str, Any]:
    payload = dict(source)
    payload.pop("skill_ir_source", None)
    payload.pop("factory_components", None)
    payload.update(
        {
            "package_profile": "runtime-only",
            "runtime_entrypoint": "SKILL.md",
            "runtime_files": sorted(include),
            "development_assets_excluded": True,
        }
    )
    return payload


def patch_generated_metadata(package_dir: Path, config: dict[str, Any]) -> None:
    """Make separately exported target metadata describe the runtime package."""

    include = list(config["include"])
    manifest_path = package_dir / "manifest.json"
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest.update(
            {
                "package_profile": "runtime-only",
                "runtime_entrypoint": "SKILL.md",
                "runtime_files": sorted(include),
                "development_assets_excluded": True,
            }
        )
        manifest_path.write_bytes(json_bytes(manifest))

    for adapter_path in sorted((package_dir / "targets").glob("*/adapter.json")):
        adapter = json.loads(adapter_path.read_text(encoding="utf-8"))
        adapter["package_profile"] = "runtime-only"
        adapter["runtime_files"] = sorted(include)
        adapter_path.write_bytes(json_bytes(adapter))


def build(source_dir: Path, package_dir: Path, config_path: Path) -> dict[str, Any]:
    source_dir = source_dir.resolve()
    package_dir = package_dir.resolve()
    config = load_config(config_path.resolve())
    include = sorted(str(item) for item in config["include"])
    source_manifest = json.loads((source_dir / "manifest.json").read_text(encoding="utf-8"))
    package_name = str(source_manifest.get("name", "")).strip()
    if not package_name:
        raise ValueError("manifest.json has no package name")

    files: dict[str, bytes] = {}
    for relative in include:
        if relative in set(config.get("integrity_files", [])):
            continue
        path = source_dir / relative
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"runtime package input is missing or not a regular file: {relative}")
        files[relative] = path.read_bytes()
    files["manifest.json"] = json_bytes(runtime_manifest(source_manifest, include))
    artifact_index = {"schema_version": "1.0", "run_id": "portable-runtime", "skill_name": package_name, "artifacts": []}
    artifact_index_bytes = json_bytes(artifact_index)
    files["reports/artifact-index.json"] = artifact_index_bytes
    files["reports/.current-run.json"] = json_bytes(
        {
            "schema_version": "1.0",
            "mode": "portable",
            "run_id": "portable-runtime",
            "skill_name": package_name,
            "artifact_index": "reports/artifact-index.json",
            "artifact_index_sha256": hashlib.sha256(artifact_index_bytes).hexdigest(),
        }
    )

    package_dir.mkdir(parents=True, exist_ok=True)
    output = package_dir / f"{package_name}.zip"
    fd, temporary_name = tempfile.mkstemp(prefix=f".{package_name}.runtime.", suffix=".zip", dir=package_dir)
    os.close(fd)
    temporary = Path(temporary_name)
    try:
        with zipfile.ZipFile(temporary, "w") as archive:
            for relative in sorted(files):
                write_entry(archive, str(PurePosixPath(package_name, *Path(relative).parts)), files[relative])
        os.replace(temporary, output)
        output.chmod(0o644)
    finally:
        if temporary.exists():
            temporary.unlink()

    patch_generated_metadata(package_dir, config)
    return {
        "ok": True,
        "profile": "runtime-only",
        "package": str(output),
        "package_name": package_name,
        "entry_count": len(files),
        "entries": sorted(files),
        "excluded_roots": config.get("excluded_roots", []),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the runtime-only Agent Team Work package.")
    parser.add_argument("source_dir", nargs="?", default=".")
    parser.add_argument("--package-dir", default="dist")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--output-json")
    args = parser.parse_args()
    report = build(Path(args.source_dir), Path(args.package_dir), Path(args.config))
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output_json:
        Path(args.output_json).write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
