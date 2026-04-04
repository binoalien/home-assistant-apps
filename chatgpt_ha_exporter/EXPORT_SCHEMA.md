# ChatGPT HA Exporter – Export Schema

## Scope

This document defines the formal structural/semantic export contract (required vs optional artifacts, domain rules, and validation semantics).
Canonical shared concept blocks are referenced from `DOC_BLOCKS.md`.

## 1. Purpose

This document defines the **expected export structure** of the ChatGPT HA Exporter.

It acts as a **schema-like contract** for downstream analysis agents, tooling, and future exporter versions.

Goals:

- provide a stable machine-oriented structure reference
- separate required vs optional artifacts
- describe semantic meaning of files
- support validation and forward compatibility
- reduce ambiguity for ChatGPT-based analysis pipelines

This is not a byte-level serialization standard.  
It is a **structural and semantic export contract**.

---

## 2. Export Model

The exporter produces exactly:

- **one TAR.GZ archive**
- containing one export root directory
- containing multiple top-level domains of information

### Export root naming

Expected pattern:

`ha_chatgpt_export_<timestamp>Z/`

Example form:

`ha_chatgpt_export_20260401T123203Z/`

The exact prefix may vary depending on exporter configuration.

---

## 3. Top-Level Structure

The canonical top-level domain list is documented in **`DOC_BLOCKS.md` → “Top-Level Export Domains”**.

For contract purposes, this schema still defines required vs optional directory presence below.

### Required top-level directories

The following directories are considered **core**:

- `inventory/`
- `metadata/`

### Expected but optional top-level directories

These may be absent depending on configuration and system state:

- `source_sanitized/`
- `normalized/`
- `runtime/`

---

## 4. Stability Levels

Each artifact belongs to one of these stability levels:

### 4.1 Stable Core

Intended to remain broadly stable across versions.

Examples:

- `metadata/export_manifest.json`
- `metadata/export_report.json`
- `metadata/checksums.sha256`
- `inventory/storage_inventory.json`
- `inventory/config_inventory.json`

### 4.2 Stable Derived

Expected to remain conceptually stable, but may evolve in fields.

Examples:

- `inventory/security_exposure_report.json`
- `inventory/relationship_integrity_report.json`
- `inventory/uncertainty_register.json`
- `inventory/integration_profiles/*.json`

### 4.3 Optional Runtime

Presence depends on options, API availability, or live system context.

Examples:

- `runtime/core.latest.log.txt`
- `runtime/supervisor.latest.log.txt`
- `runtime/addon_logs/*.txt`
- `runtime/state_snapshot.ndjson`
- `runtime/state_snapshots/*.ndjson`

### 4.4 Source-Dependent

Presence depends on whether the Home Assistant system actually contains the source material.

Examples:

- `source_sanitized/python_scripts/`
- `source_sanitized/pyscript/`
- `source_sanitized/appdaemon/`
- `source_sanitized/esphome/`
- `source_sanitized/config/themes/`

---

## 5. Metadata Domain

## 5.1 Required Files

### `metadata/export_manifest.json`

Machine-readable manifest of the exported package.

Expected responsibilities:

- list export structure
- count included files
- describe enabled/included feature blocks
- provide archive path metadata relevant to the user-facing artifact
- describe warnings and major export conditions

Minimum expected semantic fields:

- export version or exporter version context
- archive path or archive name
- included file count
- top-level area coverage
- warnings summary or warning count

### `metadata/export_report.json`

Structured run result.

Expected responsibilities:

- summarize export outcome
- report enabled/disabled sections
- list warnings
- summarize runtime, storage, inventory, and optional areas
- expose high-level execution results

### `metadata/export_summary.md`

Human-readable summary.

Expected responsibilities:

- explain what was exported
- highlight warnings
- summarize important areas
- guide quick interpretation

### `metadata/checksums.sha256`

Checksum list for exported files.

Expected properties:

- one checksum line per included file except the checksum file itself
- count should match manifest/report file count semantics

---

## 5.2 Optional Files

### `metadata/operator_intent_template.md`

Template to help the operator document intended architecture and constraints.

### `metadata/operator_intent_import_manifest.json`

Describes whether operator intent was found/imported and from where.

Expected semantics:

- always present in mature exporter versions
- may indicate `not_found`, `found`, `imported`, or similar status

### `metadata/operator_intent_context.json`

Structured view of imported operator intent or empty/default context.

Expected semantics:

- may contain normalized operator intent sections
- may be present even if no external intent was found

---

## 6. Inventory Domain

The `inventory/` domain contains structured analytical outputs.

## 6.1 Required Core Inventory

### `inventory/storage_inventory.json`

Expected purpose:

- describe discovered `.storage` files
- indicate exported vs available vs missing
- help distinguish hard gaps from scope gaps

### `inventory/config_inventory.json`

Expected purpose:

- describe config-side sources and directories
- indicate whether source directories/files exist
- surface theme include diagnostics
- indicate exported config areas

### `inventory/core_info.json`

Expected purpose:

- summarize Home Assistant core information

### `inventory/supervisor_info.json`

Expected purpose:

- summarize Supervisor information when available

---

## 6.2 Expected Derived Inventory

These files are strongly expected in full-feature exports.

### `inventory/addons.json`

Sanitized add-on inventory.

Expected semantics:

- installed add-ons
- names/slugs/versions where safe
- state/status context

### `inventory/api_config.json`

Sanitized Home Assistant API config/context.

Expected semantics:

- components/domains/config shape summary
- no destructive redaction of harmless structural fields

### `inventory/helper_source_definitions.json`

Normalized helper definitions from YAML-oriented sources.

### `inventory/helper_source_definitions.storage.json`

Normalized helper definitions from supported `.storage` sources.

Supported helper classes may include:

- input_boolean
- input_number
- input_select
- input_datetime
- input_text
- input_button
- counter
- timer
- schedule

### `inventory/template_source_definitions.json`

Normalized template definitions from YAML-oriented sources.

### `inventory/template_source_definitions.storage.json`

Normalized template definitions from UI-managed/storage-managed sources.

Expected semantics:

- derive from Home Assistant template config entries
- should not contain unrelated HACS/template naming collisions

### `inventory/relationship_integrity_report.json`

Expected purpose:

- validate preserved linkages among:
  - devices
  - entities
  - areas
  - config entries

### `inventory/security_exposure_report.json`

Expected purpose:

- expose structure-level security context
- distinguish between present data and missing context
- avoid false certainty when source files are absent

### `inventory/uncertainty_register.json`

Expected purpose:

- classify residual uncertainty

Expected categories are defined canonically in **`DOC_BLOCKS.md` → “Uncertainty Categories”**.

### `inventory/addon_options_profiles.json`

Expected purpose:

- sanitized add-on options and schema-oriented context

### `inventory/addon_stats_profiles.json`

Expected purpose:

- add-on stats when endpoints are supported

### `inventory/integration_profiles/index.json`

Expected purpose:

- list generated integration profile artifacts

### `inventory/integration_profiles/*.json`

Expected profiles may include:

- `esphome_profile.json`
- `mqtt_profile.json`
- `broadlink_profile.json`
- `hacs_profile.json`

---

## 7. Normalized Domain

The `normalized/` domain contains normalized, analysis-friendly views of raw source material.

## 7.1 Expected Structure

Typical pattern:

- `normalized/storage/*.json`

## 7.2 Expected Semantics

Normalized files should:

- preserve analyzable structure
- reduce noisy or irrelevant raw details
- keep referential integrity
- retain important identifiers or stable pseudonyms
- avoid collapsing many distinct IDs into one placeholder

## 7.3 Important Examples

Expected normalized files may include:

- `normalized/storage/core.device_registry.json`
- `normalized/storage/core.entity_registry.json`
- `normalized/storage/core.area_registry.json`
- `normalized/storage/core.config_entries.json`
- `normalized/storage/auth.json`
- `normalized/storage/http.json`
- `normalized/storage/core.network.json`
- `normalized/storage/input_boolean.json`
- `normalized/storage/input_number.json`
- `normalized/storage/input_select.json`
- `normalized/storage/schedule.json`
- `normalized/storage/timer.json`

Presence depends on options and source availability.

---

## 8. Source Sanitized Domain

The `source_sanitized/` domain contains sanitized copies of relevant source files and directories.

## 8.1 Expected Structure

Typical examples:

- `source_sanitized/config/`
- `source_sanitized/dashboards/`
- `source_sanitized/blueprints/`
- `source_sanitized/custom_components/`
- `source_sanitized/python_scripts/`
- `source_sanitized/pyscript/`
- `source_sanitized/appdaemon/`
- `source_sanitized/esphome/`

## 8.2 Config Subtree Expectations

`source_sanitized/config/` may contain:

- `configuration.yaml`
- `automations.yaml`
- `scripts.yaml`
- `scenes.yaml`
- helper YAML files
- `template.yaml`
- `themes/`

## 8.3 Source Semantics

These files are intended for:

- contextual inspection
- source-level reasoning
- cross-referencing normalized and inventory views

They are not guaranteed to be byte-identical to originals because sanitization may change values.

---

## 9. Runtime Domain

The `runtime/` domain contains live-state and runtime-derived export data.

## 9.1 Expected Files

### State Snapshots

- `runtime/state_snapshot.ndjson`
- `runtime/state_snapshots/*.ndjson`
- `runtime/state_snapshots_summary.json`

### Logs

- `runtime/core.latest.log.txt`
- `runtime/supervisor.latest.log.txt`
- `runtime/addon_logs/*.txt`

### Recorder

Possible files:

- `runtime/recorder_summary.json`
- `runtime/recorder_state_samples.ndjson`
- `runtime/recorder_event_samples.ndjson`
- `runtime/recorder_event_type_counts.json`
- `runtime/recorder_statistics_summary.json`
- `runtime/recorder_deep_export_summary.json`

Optional:

- recorder DB copy if explicitly enabled

## 9.2 Runtime Semantics

Runtime artifacts:

- may be partial
- may be API-dependent
- may reflect sampling limits
- should not be assumed exhaustive unless explicitly documented

---

## 10. Referential Integrity Contract

A core exporter requirement is that the following analytical relationships remain reconstructible:

- device → entity
- area → device
- config entry → device/entity
- helper definition → helper entity
- template definition → template entity, where derivable

## 10.1 Allowed Protection Strategy

Sensitive identifiers may be:

- preserved
- or replaced with stable pseudonyms

## 10.2 Forbidden Failure Mode

The exporter must not:

- collapse many distinct IDs into the same placeholder
- destroy one-to-many linkage meaning
- make device/entity graph reconstruction impossible

---

## 11. Sanitization Contract

Canonical sanitization categories are defined in **`DOC_BLOCKS.md` → “Sanitization Model”**.

This section defines schema-specific behavior that downstream validators should enforce.

## 11.1 Confidence Rule

If a source is missing, derived reports should prefer:

- `unknown`
- `not_exported`
- `unavailable`
- `partial`

over falsely definitive values like:

- `0`
- `false`
- `none`

unless absence is actually proven.

---

## 12. Optionality Rules

A downstream consumer should classify missing artifacts as follows:

### 12.1 Hard Missing

Expected and required, but absent unexpectedly.

Example:

- missing `metadata/export_manifest.json`

### 12.2 Scope Missing

Not exported due to options or intentional scope.

Example:

- no `runtime/addon_logs/` when add-on logs were disabled

### 12.3 Source Missing

Not present in the source Home Assistant system.

Example:

- no `source_sanitized/pyscript/` because no `pyscript/` exists

### 12.4 Runtime Missing

Dependent on live APIs or environment.

Example:

- missing add-on stats for unsupported endpoints

---

## 13. Validation Rules

A downstream validator should at minimum check:

### 13.1 Archive Integrity

- archive opens correctly
- one export root exists
- checksums file is parseable

### 13.2 Metadata Consistency

- manifest/report/summary exist
- file counts match actual contents
- checksum count matches exported files

### 13.3 Structural Integrity

- required directories exist
- inventory and metadata domains are present
- optional domains are classified correctly

### 13.4 Referential Integrity

- multiple devices remain distinguishable
- entity `device_id` references remain analyzable
- relationship report does not contradict normalized registries

### 13.5 Report Plausibility

- warnings align with available files
- uncertainty register does not claim missing data that is actually present
- security report distinguishes missing source vs observed absence

---

## 14. Versioning and Compatibility

## 14.1 Exporter Version

Downstream tooling should read exporter version from app/config context where available.

## 14.2 Backward Compatibility

Consumers should prefer:

- semantic presence checks
- graceful handling of optional files
- tolerance for added report fields

Consumers should avoid:

- assuming strict field parity across all versions
- failing on unknown files

## 14.3 Forward Compatibility

New exporter versions may add:

- new inventory files
- new runtime summaries
- new integration profiles

- new metadata fields

They should avoid:

- silently changing meaning of stable core files
- removing core metadata without replacement

---

## 15. Recommended Consumer Strategy for ChatGPT

A ChatGPT instance consuming the export should work in this order:

1. read `metadata/export_manifest.json`
2. read `metadata/export_report.json`
3. inspect `inventory/storage_inventory.json`
4. inspect `inventory/config_inventory.json`
5. read relationship/security/uncertainty reports
6. inspect normalized registries
7. inspect source_sanitized only where needed
8. use runtime artifacts for confirmation, not as the sole truth source

This minimizes confusion and reduces overreliance on any single artifact type.

---

## 16. Non-Goals of the Schema

This schema does not guarantee:

- restore completeness
- operational correctness of the HA system
- complete elimination of ambiguity

- operator intent inference
- full historical runtime reconstruction

For operator intent, use:

- `operator_intent.md`
- `operator_intent.json`

For applied ChatGPT workflows, use:

- `CHATGPT_WORKFLOWS.md`

---

## 17. Minimal Acceptance Profile

An export is minimally acceptable for ChatGPT analysis if it contains at least:

- `metadata/export_manifest.json`
- `metadata/export_report.json`
- `metadata/checksums.sha256`
- `inventory/storage_inventory.json`
- `inventory/config_inventory.json`
- `normalized/storage/core.device_registry.json`
- `normalized/storage/core.entity_registry.json`

A strong export for refactoring should additionally contain:

- relationship integrity report
- helper/template source definitions
- security exposure report
- uncertainty register
- relevant runtime logs
- recorder summaries
- integration profiles
