# ChatGPT HA Exporter – Technical Documentation

## Scope

This document covers exporter architecture, phases, configuration behavior, and troubleshooting.
Shared canonical concepts (domains, sanitization, uncertainty categories) are referenced from `DOC_BLOCKS.md`.

## 1. Overview

The ChatGPT HA Exporter generates a **sanitized, structure-preserving analysis package** from Home Assistant.

It is built for:
- analysis
- safe hand-off to ChatGPT
- refactoring preparation
- system redesign
- evidence-based optimization

It is **not** a backup or restore tool.

This file explains:
- exporter architecture
- export phases
- output domains
- sanitization model
- configuration model
- limits and troubleshooting

For the formal export contract, see **`EXPORT_SCHEMA.md`**.  
For practical two-instance usage and prompts, see **`CHATGPT_WORKFLOWS.md`**.

---

## 2. Core Principles

### 2.1 Analysis over Backup

Prioritized:
- structure
- relationships
- runtime context
- diagnostics
- downstream usability

Not prioritized:
- raw one-to-one replication
- restore completeness

### 2.2 Structure-Preserving Sanitization

The exporter aims to:
- remove secrets and sensitive operational values
- preserve analyzable structure
- preserve linkable references
- keep downstream graph reconstruction possible

Usually preserved:
- slugs
- versions
- domains
- entity relationships
- device mappings
- config-entry linkage

### 2.3 Single Output Artifact

The exporter works in a temporary internal work directory, but the user-facing result is:
- exactly one `.tar.gz`
- written to `/share`
- with no leftover extracted export tree

---

## 3. Export Pipeline

### 3.1 Source Collection

Depending on configuration, the exporter reads relevant Home Assistant config-side sources, including:
- core YAML configuration
- dashboards
- blueprints
- custom components
- python scripts
- pyscript
- AppDaemon
- ESPHome
- themes

### 3.2 Storage Extraction and Normalization

Selected `.storage` files are:
- copied in sanitized form
- normalized into analysis-ready JSON views

This commonly includes:
- registries
- config entries
- frontend state
- security/auth/network context
- traces and repairs
- helper definitions
- template definitions
- integration-specific metadata

### 3.3 Runtime and API Context

Optional runtime/API collection includes:
- current state snapshot
- repeated snapshots over time
- service catalog
- supervisor/core information
- logs
- backup context
- add-on options
- add-on stats

### 3.4 Derived Reports

The exporter derives additional analysis artifacts such as:
- relationship integrity report
- security exposure report
- integration profiles
- uncertainty register
- manifest/report/summary metadata

---

## 4. Export Domains

For canonical top-level export domains, see **`DOC_BLOCKS.md` → “Top-Level Export Domains”**.

This file focuses on operational interpretation (pipeline and report usage), while formal required/optional contract details remain in **`EXPORT_SCHEMA.md`**.

---

## 5. Key Reports

### 5.1 `export_manifest.json`

Machine-readable package manifest.

Typical responsibilities:
- included file counts
- enabled/exported blocks
- structure overview
- warning context

### 5.2 `export_report.json`

Structured execution result.

Typical responsibilities:
- run outcome
- warnings
- runtime/export coverage
- high-level feature summary

### 5.3 `export_summary.md`

Human-readable summary.

Useful for:
- quick inspection
- warning review
- top-level export verification

### 5.4 `relationship_integrity_report.json`

Validates preserved linkage across:
- device ↔ entity
- area ↔ device
- config entry ↔ entity/device

### 5.5 `security_exposure_report.json`

Summarizes structure-level security context such as:
- HTTP context
- auth/provider context
- exposed entities
- network signals
- mobile/assist/frontend hints

### 5.6 `uncertainty_register.json`

Uses canonical uncertainty categories from **`DOC_BLOCKS.md` → “Uncertainty Categories”**.

---

## 6. Sanitization Model

For canonical sanitization definitions, see **`DOC_BLOCKS.md` → “Sanitization Model”**.

This document uses that model as the baseline for interpreting export artifacts and troubleshooting outcomes.

---

## 7. Configuration Model

### 7.1 Base Analysis

- state snapshot
- services
- dashboards
- blueprints
- custom components

### 7.2 Logic Sources

- python_scripts
- pyscript
- appdaemon
- esphome
- themes

### 7.3 Runtime and Logs

- core, supervisor, and add-on logs
- archived logs
- repeated state snapshots

### 7.4 Recorder

- summary
- deep export (states/events/statistics)
- optional DB copy

### 7.5 Storage Coverage

- raw storage
- extended storage
- security storage
- frontend storage
- trace storage
- backup metadata

### 7.6 Derived Analysis

- helper definitions
- template definitions
- relationship integrity
- security exposure
- integration profiles
- uncertainty register

### 7.7 Advanced Features

- multi snapshots
- operator intent template/import
- add-on options export
- add-on stats
- HACS slimming

---

## 8. Recommended Profiles

### 8.1 Standard

Balanced default:
- snapshots
- logs
- recorder summary + deep export
- extended + security storage
- integration profiles
- uncertainty register

### 8.2 Privacy-Focused

Reduced exposure:
- no recorder DB copy
- reduced logs
- only needed optional directories
- operator intent provided separately

### 8.3 Deep Analysis / Refactoring

Maximum insight:
- full storage coverage
- deep recorder export
- multi snapshots
- add-on options export
- integration profiles
- operator intent provided

---

## 9. Troubleshooting

### 9.1 Missing Themes

Check:
- the referenced directory exists
- it contains YAML files
- the include path is correct

### 9.2 Missing Logs

Check:
- log options are enabled
- the endpoint/file exists in the installation
- supervisor permissions are sufficient for supervisor/add-on logs

### 9.3 Missing Data

Possible causes:
- the source does not exist in the system
- the export option is disabled
- the data is unavailable or unreadable
- it was intentionally excluded by scope or sanitization policy

### 9.4 Start on Boot

The app is intended as a one-shot app. If **Start on boot** is still active from an older installation state, disable it in the Home Assistant UI.

---

## 10. Limits

An export cannot answer everything automatically.

Examples that usually still need human clarification:
- target architecture
- intentionally retained legacy behavior
- preferred naming language/style
- business-critical automations
- areas that must never be changed automatically

For that, provide `operator_intent.md` or `operator_intent.json`.

---

## 11. ChatGPT Usage

For practical workflow guidance, prompt patterns, and two-instance operating models, see **`CHATGPT_WORKFLOWS.md`**.

For the formal export contract, see **`EXPORT_SCHEMA.md`**.
