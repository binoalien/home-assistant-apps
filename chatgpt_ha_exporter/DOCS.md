# ChatGPT HA Exporter – Technical Documentation

The ChatGPT HA Exporter generates a sanitised analytics package from Home Assistant.

This documentation describes:

- Architecture and export pipeline
- Data ranges included
- Sanitisation strategy
- Configuration model
- Limitations and troubleshooting

For a formal, machine-readable description of the export structure, see:

👉 **`EXPORT_SCHEMA.md`**

This file serves as a **schema / API contract for ChatGPT and other analytics instances**.

---

## 2. Core Principles

### Analysis > Backup

Focus:

- structure
- relationships
- runtime context
- diagnostics

Not focus:

- full raw replication
- restore fidelity

---

### Structure-Preserving Sanitization

- secrets and sensitive values are redacted
- references remain intact
- relationships stay analyzable

Preserved:

- entity relationships
- device mappings
- config entry links
- domains, slugs, versions

---

### Single Output Artifact

- one `.tar.gz`
- stored in `/share`
- no leftover working directory

---

## 3. Export Pipeline

### 3.1 Source Collection

From Home Assistant config:

- core configuration
- dashboards
- blueprints
- custom components
- python/pyscript/appdaemon
- ESPHome
- themes

---

### 3.2 Storage Extraction

`.storage` data is:

- exported (sanitized)
- normalized for analysis

Includes:

- registries
- config entries
- frontend state
- security/auth/network
- trace + repairs
- helpers + templates
- integration metadata

---

### 3.3 Runtime + API Context

Optional runtime data:

- state snapshots
- service catalog
- supervisor/core info
- logs (core, supervisor, add-ons)
- backup metadata
- add-on options + stats

---

### 3.4 Derived Reports

Generated artifacts:

- relationship integrity report
- security exposure report
- integration profiles
- uncertainty register
- export manifest/report/summary

---

## 4. Export Structure

### `source_sanitized/`

Sanitized Home Assistant source:

- config
- dashboards
- blueprints
- custom_components
- python/pyscript/appdaemon
- esphome
- themes

---

### `normalized/`

Analysis-ready JSON views:

- normalized `.storage`
- unified structures

---

### `inventory/`

Structured system insights:

- core + supervisor info
- api config
- storage + config inventory
- helper/template definitions
- integration profiles
- security exposure
- uncertainty register

---

### `runtime/`

Runtime context:

- state snapshots
- snapshot deltas
- logs
- recorder summaries + samples

---

### `metadata/`

Export metadata:

- manifest
- report
- summary
- checksums
- operator intent context

---

## 5. Key Reports

### Export Manifest

Machine-readable:

- file counts
- included modules
- export structure

---

### Export Report

Execution summary:

- warnings
- enabled features
- runtime coverage

---

### Export Summary

Human-readable:

- quick overview
- warnings
- major components

---

### Relationship Integrity

Validates:

- device ↔ entity
- area ↔ device
- config entry ↔ entity/device

---

### Security Exposure

Includes:

- HTTP context
- auth providers
- exposed entities
- network signals
- mobile/assist/frontend context

---

### Uncertainty Register

Classifies gaps:

- `hard_export_gap`
- `export_scope_gap`
- `principled_uncertainty`

---

## 6. Sanitization Model

### Redacted

- secrets
- tokens
- webhook IDs
- client secrets
- sensitive endpoints

---

### Preserved

- slugs
- versions
- domains
- structure
- relationships

---

### Pseudonymization

Used when:

- value must stay referencable
- but must not leak original data

---

## 7. Configuration Model

### Base Analysis

- state snapshot
- services
- dashboards
- blueprints
- custom components

---

### Logic Sources

- python_scripts
- pyscript
- appdaemon
- esphome
- themes

---

### Runtime + Logs

- logs (core + supervisor + add-ons)
- archived logs
- snapshot sequences

---

### Recorder

- summary
- deep export (states/events/statistics)
- optional DB copy

---

### Storage Coverage

- raw storage
- extended storage
- security storage
- frontend storage
- trace storage
- backup metadata

---

### Derived Analysis

- helper definitions
- template definitions
- relationship integrity
- security exposure
- integration profiles
- uncertainty register

---

### Advanced Features

- multi snapshots
- operator intent template/import
- add-on options export
- add-on stats
- HACS slimming

---

## 8. Recommended Profiles

### Standard

Balanced:

- snapshots
- logs
- recorder summary + deep export
- extended + security storage
- integration profiles
- uncertainty register

---

### Privacy-Focused

Reduced exposure:

- no recorder DB copy
- reduced logs
- minimal optional directories
- operator intent externalized

---

### Deep Analysis / Refactoring

Maximum insight:

- full storage coverage
- deep recorder export
- multi snapshots
- add-on options export
- integration profiles
- operator intent provided

---

## 9. Troubleshooting

### Missing Themes

Cause:

- referenced but not present

Check:

- directory exists
- contains YAML files
- path is correct

---

### Missing Logs

Check:

- options enabled
- endpoint availability
- supervisor permissions

---

### Missing Data

Possible reasons:

- not present in system
- disabled via config
- not accessible
- intentionally excluded

---

### Start on Boot

This is a **one-shot app**.

If still active:

- disable manually in Home Assistant UI

---

## 10. Limitations

Not solvable by export alone:

- architectural intent
- naming conventions
- critical automations
- intentional legacy behavior

---

## 11. Operator Intent

Recommended:

- `operator_intent.md`
- `operator_intent.json`

Contains:

- target architecture
- constraints
- non-changeable areas
- design decisions

---

## 12. ChatGPT Usage

See:

**`CHATGPT_WORKFLOWS.md`**

Includes:

- two-instance workflow
- greenfield rebuild strategy
- ready-to-use prompts
- handover strategy

---

## 13. Export Schema (Machine Contract)

The file **`EXPORT_SCHEMA.md`** describes the export structure in a formal, machine-readable format.

It is relevant for:

- ChatGPT instances
- Analysis pipelines
- Validation of exports
- Future compatibility

Difference from this documentation:

| File | Purpose |
|------|------|
| DOCS.md | Technical explanation for humans |
| EXPORT_SCHEMA.md | Structured contract for machines |

### When to use EXPORT_SCHEMA.md?

- when writing analysis prompts
- when validating an export
- when developing further tools
- when comparing different export versions

### Important

DOCS.md describes **how the export works**  
EXPORT_SCHEMA.md describes **how the export is structured**
