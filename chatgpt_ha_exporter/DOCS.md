# ChatGPT HA Exporter – Technical Documentation

## 1. Overview

The ChatGPT HA Exporter creates a **sanitised analysis package** from Home Assistant.

It is designed for:
- ChatGPT-based inspection
- safer hand-off of Home Assistant structure
- evidence-based optimisation planning
- refactoring preparation

It is **not** a backup or restore tool.

For the formal export contract, see **`EXPORT_SCHEMA.md`**.  
For operational ChatGPT usage and prompts, see **`CHATGPT_WORKFLOWS.md`**.

---

## 2. Core Principles

### 2.1 Analysis over Backup

Prioritised:
- structure
- inventories
- key runtime context
- sanitised source material

Not prioritised:
- full restore fidelity
- raw one-to-one replication of all internals

### 2.2 Sanitisation with Structural Retention

The exporter removes or redacts sensitive values while trying to preserve:
- analyzable YAML structure
- entity/device/area/config-entry context where exported
- service and integration visibility
- configuration reasoning value

### 2.3 Share-Based Output

The current exporter writes:
- an extracted export directory under `/share`
- a matching `.tar.gz` archive next to it

---

## 3. Export Pipeline

### 3.1 Config Sources

The exporter may collect:
- `configuration.yaml`
- `automations.yaml`
- `scripts.yaml`
- `scenes.yaml`
- `ui-lovelace.yaml`
- `customize*.yaml`
- `groups.yaml`
- YAML files from `packages/`, `themes/`, `dashboards/`, `blueprints/`
- `custom_components/`
- `python_scripts/`
- `pyscript/`

### 3.2 `.storage` Sources

The exporter includes a selected allowlist of `.storage` files, including:
- device/entity/area/floor/label registries
- config entries
- core config
- restore state
- Lovelace-related files
- selected energy/person data

### 3.3 Runtime/API Sources

Optional runtime/API collection includes:
- current states
- services
- supervisor info
- core info
- add-on inventory
- API config
- log tail
- recorder summary

---

## 4. Output Domains

### 4.1 `source_sanitized/`

Sanitised raw source copies.

Typical subtrees:
- `source_sanitized/config/`
- `source_sanitized/storage/`
- `source_sanitized/custom_components/`
- `source_sanitized/python_scripts/`
- `source_sanitized/pyscript/`

### 4.2 `normalized/`

Normalised JSON views for downstream analysis.

Typical subtrees:
- `normalized/config/`
- `normalized/storage/`

### 4.3 `inventory/`

Structured metadata and system views.

Typical files:
- `supervisor_info.json`
- `core_info.json`
- `addons.json`
- `api_config.json`
- `services.json`
- `storage_inventory.json`

### 4.4 `runtime/`

Runtime-derived outputs.

Typical files:
- `state_snapshot.ndjson`
- `home-assistant.log.tail.txt`
- `recorder_summary.json`
- `recorder_top_entities.ndjson`

### 4.5 `metadata/`

Export metadata.

Typical files:
- `export_manifest.json`
- `export_summary.md`
- `checksums.sha256`

---

## 5. Key Reports

### 5.1 `export_manifest.json`

Machine-readable manifest of the run.

Current responsibilities:
- exporter identity
- path metadata
- options used
- included/excluded counts
- config/storage/API/recorder summary
- warnings

### 5.2 `export_summary.md`

Human-readable summary.

Use it for:
- quick inspection
- warning review
- seeing what a downstream ChatGPT instance should inspect first

### 5.3 `storage_inventory.json`

Shows:
- available `.storage` files
- included `.storage` files

This is important for distinguishing missing source data from intentional scope.

---

## 6. Sanitisation Model

### 6.1 Redacted or trimmed

Examples:
- passwords
- tokens
- API keys
- client secrets
- webhook values
- internal/external URL fields
- obvious bearer-style credentials

### 6.2 Preserved where useful

Examples:
- non-sensitive YAML structure
- entity IDs in state snapshots
- service inventory structure
- config-entry and registry structures, subject to sanitisation

### 6.3 Text-tail processing

Text files are sanitised line-wise.
Logs are exported as a tail, not as full archives.

---

## 7. Configuration Model

### 7.1 Base scope

- `include_current_state_snapshot`
- `include_service_catalog`
- `include_dashboards`
- `include_blueprints`
- `include_custom_components`

### 7.2 Source logic

- `include_python_scripts`
- `include_pyscript`

### 7.3 Runtime and logs

- `include_logs`
- `max_log_lines`

### 7.4 Recorder

- `include_recorder_summary`
- `recorder_days`

### 7.5 Storage scope

- `include_raw_storage_files`

---

## 8. Troubleshooting

### 8.1 Missing logs

Possible reasons:
- `include_logs` disabled
- `home-assistant.log` not present
- read failure

### 8.2 Missing dashboard or blueprint files

Possible reasons:
- source directory not present
- directory empty
- option disabled

### 8.3 Missing `.storage` data

Possible reasons:
- source file not in allowlist
- source file absent in Home Assistant
- read or parse failure

### 8.4 API warnings

Supervisor/core API calls may fail because of:
- permissions
- unavailable endpoints
- malformed responses
- temporary runtime issues

---

## 9. Limitations

This exporter does not eliminate all uncertainty.

Not fully derivable from data alone:
- operator intent
- desired target architecture
- preferred naming conventions
- intentionally retained legacy behaviour
- critical business logic that only the operator can confirm

---

## 10. Recommended Use with ChatGPT

Recommended sequence:
1. create a fresh export
2. let one ChatGPT instance analyse and structure it
3. let a second instance optimise or refactor based on that handoff

For concrete two-instance workflows and prompts, see **`CHATGPT_WORKFLOWS.md`**.
