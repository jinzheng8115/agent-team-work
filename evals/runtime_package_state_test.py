#!/usr/bin/env python3
"""Regression tests for generated target files in the runtime archive."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_runtime_package import build  # noqa: E402
from runtime_package_check import check  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="agent-team-work-runtime-") as temporary:
        root = Path(temporary)
        source_dir = root / "source"
        package_dir = root / "dist"
        config_path = root / "package-runtime.json"

        write(source_dir / "LICENSE", "MIT\n")
        write(source_dir / "SKILL.md", "---\nname: fixture-skill\n---\nSee references/workflow.md\n")
        write(source_dir / "agents/interface.yaml", "name: fixture\n")
        write(source_dir / "references/workflow.md", "# Workflow\n")
        write(source_dir / "manifest.json", json.dumps({"name": "fixture-skill", "version": "0.0.1"}))
        write(package_dir / "targets/openai/agents/openai.yaml", "name: fixture-openai\n")
        write(
            package_dir / "targets/openai/adapter.json",
            json.dumps({"name": "fixture-skill", "target": "openai"}),
        )

        include = [
            "LICENSE",
            "SKILL.md",
            "manifest.json",
            "agents/interface.yaml",
            "reports/.current-run.json",
            "reports/artifact-index.json",
            "references/workflow.md",
            "targets/openai/adapter.json",
            "targets/openai/agents/openai.yaml",
        ]
        config_path.write_text(
            json.dumps(
                {
                    "schema_version": "1.0",
                    "profile": "runtime-only",
                    "include": include,
                    "generated_roots": ["targets"],
                    "target_files": [
                        "targets/openai/adapter.json",
                        "targets/openai/agents/openai.yaml",
                    ],
                    "integrity_files": [
                        "reports/.current-run.json",
                        "reports/artifact-index.json",
                    ],
                }
            ),
            encoding="utf-8",
        )

        build(source_dir, package_dir, config_path)
        good = check(source_dir, package_dir, config_path)
        assert good["ok"], good
        with zipfile.ZipFile(package_dir / "fixture-skill.zip") as archive:
            adapter = json.loads(archive.read("fixture-skill/targets/openai/adapter.json"))
            assert adapter["package_profile"] == "runtime-only"
            assert adapter["runtime_files"] == sorted(include)

        tampered = package_dir / "tampered.zip"
        archive_path = package_dir / "fixture-skill.zip"
        with zipfile.ZipFile(archive_path) as source_archive, zipfile.ZipFile(tampered, "w") as target_archive:
            for info in source_archive.infolist():
                if info.filename.endswith("/targets/openai/adapter.json"):
                    continue
                target_archive.writestr(info, source_archive.read(info.filename))
        os.replace(tampered, archive_path)
        broken = check(source_dir, package_dir, config_path)
        assert not broken["ok"], broken
        failed_ids = {item["id"] for item in broken["checks"] if item["status"] == "fail"}
        assert {"runtime-allowlist", "target-files-packaged"}.issubset(failed_ids), failed_ids

    print("PASS runtime-package-state")


if __name__ == "__main__":
    main()
