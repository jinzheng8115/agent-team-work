# Telemetry Hook Recipes

Five metadata-only hook recipes are defined for browser, Chrome, VS Code, CLI-wrapper, and provider-adapter clients. `scripts/import_telemetry_events.py` validates JSONL and emits sanitized events to stdout; it does not call a network or write a file.

These recipes establish the local privacy contract only. They do not prove that a real client emitted telemetry. Native-client evidence remains pending until an external client sends an accepted metadata-only event through an approved host path.
