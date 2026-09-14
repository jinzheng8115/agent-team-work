# Install Simulation

- OK: `True`
- Package directory: `/Volumes/Code/team-worker/agent-team-work/dist`
- Archive extracted: `True`
- Nested SKILL.md entries: `0`
- Entrypoint loaded: `True`
- Manifest loaded: `True`
- Interface loaded: `True`
- Adapters readable: `4`
- Installer permissions enforced: `0`
- Installer permission failures: `0`
- Failures: `0`
- Warnings: `0`

## Checks

| Check | Status | Detail |
| --- | --- | --- |
| `archive-present` | `pass` | Package archive exists: /Volumes/Code/team-worker/agent-team-work/dist/agent-team-work.zip |
| `archive-safe-paths` | `pass` | Archive has no absolute or parent-traversal entries |
| `single-skill-entrypoint` | `pass` | Installed package exposes only the root SKILL.md entrypoint |
| `single-top-level` | `pass` | Archive top-level directory is agent-team-work |
| `entrypoint-load` | `pass` | Installed SKILL.md frontmatter is readable |
| `entrypoint-name` | `pass` | Installed SKILL.md name matches package directory |
| `entrypoint-description` | `pass` | Installed SKILL.md description is present |
| `manifest-load` | `pass` | Installed manifest.json is readable |
| `manifest-name` | `pass` | Installed manifest name matches package manifest |
| `manifest-version` | `pass` | Installed manifest version matches package manifest |
| `interface-load` | `pass` | Installed agents/interface.yaml is readable |
| `overview-report` | `pass` | Installed overview report is present |
| `review-studio-report` | `pass` | Installed Review Studio report is present |
| `adapter-claude` | `pass` | claude adapter is readable after package install simulation |
| `adapter-claude-name` | `pass` | claude adapter name matches package manifest |
| `adapter-generic` | `pass` | generic adapter is readable after package install simulation |
| `adapter-generic-name` | `pass` | generic adapter name matches package manifest |
| `adapter-openai` | `pass` | openai adapter is readable after package install simulation |
| `adapter-openai-name` | `pass` | openai adapter name matches package manifest |
| `adapter-vscode` | `pass` | vscode adapter is readable after package install simulation |
| `adapter-vscode-name` | `pass` | vscode adapter name matches package manifest |
| `permission-policy-load` | `pass` | Installed permission policy is readable |
| `permission-claude-contract` | `pass` | claude adapter exposes target permission contract for installer enforcement |
| `permission-generic-contract` | `pass` | generic adapter exposes target permission contract for installer enforcement |
| `permission-openai-contract` | `pass` | openai adapter exposes target permission contract for installer enforcement |
| `permission-vscode-contract` | `pass` | vscode adapter exposes target permission contract for installer enforcement |

## Failures

- None

## Warnings

- None
