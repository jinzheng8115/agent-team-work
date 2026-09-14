# VS Code / Copilot Agent Skills Package

Install `agent-team-work` as a VS Code user or project scoped Agent Skill. Keep the folder name aligned with `SKILL.md` frontmatter name.

Native surface: VS Code/Copilot Agent Skills project or user scope.

Activation: Use folder name plus SKILL.md name/description; keep description under platform limits.

Resources: Install as project or user scoped skill source, preserving relative references and scripts.

Scripts: Scripts require workspace trust and operator/client approval outside this compiler.

Permission model: vscode-workspace-trust-plus-metadata. Review `target_permission_contract`, workspace trust, and `reports/security_trust_report.md` before running scripts.

This adapter does not perform automatic VS Code installation; it preserves the reviewed source package plus install notes.
