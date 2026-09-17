# Install Simulation (Runtime-only Package Check)

- Profile: `runtime-only`
- OK: `True`
- Archive entries: `13`
- Adapters: `4`
- Development roots: excluded by explicit allowlist

## Checks

- `pass` archive-present: archive exists: /Volumes/Code/team-worker/agent-team-work/dist/agent-team-work.zip
- `pass` archive-safe-paths: archive has no absolute or parent-traversal paths
- `pass` archive-root: archive entries use the package root: []
- `pass` runtime-allowlist: archive entries match runtime allowlist (13 files)
- `pass` development-assets-excluded: development roots absent: []
- `pass` portable-integrity-index: portable integrity pointer matches artifact index
- `pass` runtime-manifest: archive manifest declares runtime-only profile
- `pass` entrypoint-name: SKILL.md frontmatter name matches package
- `pass` entrypoint-references: entrypoint references are packaged: []
- `pass` single-entrypoint: archive has one root SKILL.md entrypoint
