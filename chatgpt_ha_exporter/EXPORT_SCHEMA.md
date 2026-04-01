# ChatGPT HA Exporter – Export Schema

## 1. Purpose

This document defines the **structural contract** of the current ChatGPT HA Exporter package.

It is intended for:
- downstream ChatGPT analysis
- validation of generated exports
- clear separation between required and optional artifacts

This is not a byte-level serialization spec.  
It is a **semantic export structure contract**.

---

## 2. Output Model

The exporter currently produces:
- one extracted export directory under `/share`
- one `.tar.gz` archive next to it

Expected export root pattern:
- `ha_chatgpt_export_<timestamp>/`
- or the configured custom prefix with the same timestamp pattern

---

## 3. Top-Level Domains

An export root may contain:
- `source_sanitized/`
- `normalized/`
- `inventory/`
- `runtime/`
- `metadata/`

### Required domains

- `inventory/`
- `metadata/`

### Optional domains

- `source_sanitized/`
- `normalized/`
- `runtime/`

Presence depends on source availability and options.

---

## 4. Metadata Domain

### Required files

#### `metadata/export_manifest.json`

Expected semantics:
- exporter name and version
- path metadata
- options used
- included/warning counters
- config/storage/API/recorder summary
- excluded items and warnings

#### `metadata/export_summary.md`

Expected semantics:
- human-readable overview
- primary entry files for downstream ChatGPT
- warning section
- quick export observations

#### `metadata/checksums.sha256`

Expected semantics:
- checksums for all exported files except itself

---

## 5. Inventory Domain

### Expected files

#### `inventory/storage_inventory.json`

Describes:
- available `.storage` files
- included `.storage` files

#### `inventory/supervisor_info.json`

Optional. Present if supervisor info API succeeded.

#### `inventory/core_info.json`

Optional. Present if core info API succeeded.

#### `inventory/addons.json`

Optional. Present if add-ons API succeeded.

#### `inventory/api_config.json`

Optional. Present if API config call succeeded.

#### `inventory/services.json`

Optional. Present if service export is enabled and the API call succeeded.

---

## 6. Source Sanitized Domain

### `source_sanitized/config/`

May contain sanitised copies of:
- `configuration.yaml`
- `automations.yaml`
- `scripts.yaml`
- `scenes.yaml`
- `secrets.yaml`
- `ui-lovelace.yaml`
- `customize.yaml`
- `customize_glob.yaml`
- `groups.yaml`
- YAML files from `packages/`, `themes/`, `dashboards/`, `blueprints/`

### `source_sanitized/storage/`

May contain sanitised copies of selected allowlisted `.storage` files.

### Additional optional source trees

May contain:
- `source_sanitized/custom_components/`
- `source_sanitized/python_scripts/`
- `source_sanitized/pyscript/`

---

## 7. Normalized Domain

### `normalized/config/`

JSON-normalised views of exported YAML files.

### `normalized/storage/`

JSON-normalised views of selected `.storage` files.

Important examples may include:
- `core.device_registry.json`
- `core.entity_registry.json`
- `core.area_registry.json`
- `core.config_entries.json`
- `lovelace*.json`

---

## 8. Runtime Domain

### Expected optional files

#### `runtime/state_snapshot.ndjson`

Present when state export is enabled and API access succeeds.

#### `runtime/home-assistant.log.tail.txt`

Present when log export is enabled and the log file exists.

#### `runtime/recorder_summary.json`

Present when recorder summary is enabled and the recorder DB exists.

#### `runtime/recorder_top_entities.ndjson`

Optional companion file to the recorder summary.

---

## 9. Referential Expectations

The current exporter does not yet define a formal relationship-integrity report, but downstream consumers should still expect useful structure from:
- device/entity registries
- config entries
- Lovelace metadata
- state snapshot entity IDs

Because sanitisation is coarse in this version, downstream consumers should treat relationship-level conclusions as **helpful but not guaranteed perfect**.

---

## 10. Sanitisation Contract

### Should be redacted

Examples:
- secrets
- passwords
- tokens
- API keys
- client secrets
- webhook values
- obvious auth-related fields
- location fields

### Should generally remain visible

Examples:
- filenames
- YAML structure
- service domains
- dashboard structure
- entity IDs in runtime snapshots where not directly sensitive

---

## 11. Validation Guidance

A downstream validator should at minimum check:
- export root exists
- `metadata/export_manifest.json` exists
- `metadata/export_summary.md` exists
- `metadata/checksums.sha256` exists
- `inventory/storage_inventory.json` exists
- checksum file parses correctly
- archive opens successfully

---

## 12. Minimal Acceptable Export

An export is minimally acceptable for downstream ChatGPT analysis if it contains at least:
- `metadata/export_manifest.json`
- `metadata/export_summary.md`
- `metadata/checksums.sha256`
- `inventory/storage_inventory.json`
- at least one of:
  - `normalized/storage/core.entity_registry.json`
  - `normalized/storage/core.device_registry.json`
  - `runtime/state_snapshot.ndjson`
  - `inventory/services.json`
