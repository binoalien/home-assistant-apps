# ChatGPT HA Exporter

[Add Binoalien Home Assistant Apps to Home Assistant](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fbinoalien%2Fhome-assistant-apps)

**ChatGPT HA Exporter** generates a sanitized, structure-preserving analysis package from Home Assistant.

Version: **0.6.1**

## Purpose

This app is an **analysis exporter for ChatGPT**.

It produces a package that:

- preserves structure and cross-file relationships
- protects sensitive values where possible
- includes runtime, trace, recorder, backup, security, helper, template, integration, and refactoring context
- supports both improvement of an existing system and clean greenfield redesign

It is **not** a backup or restore tool.

## Install

1. Add the repository with the link above.
2. Open **Settings → Apps**.
3. Install **ChatGPT HA Exporter**.

## Basic use

1. Configure the export options.
2. Start the app manually.
3. Take the resulting `.tar.gz` archive from `/share`.
4. Upload the archive to another ChatGPT instance.

## What the export can include

Depending on configuration and source availability, the export may include:

- sanitized Home Assistant configuration files
- selected and normalized `.storage` data
- dashboards, blueprints, and custom components
- optional source folders such as `python_scripts/`, `pyscript/`, `appdaemon/`, `esphome/`, and referenced `themes/`
- core, supervisor, and add-on inventory data
- helper and template source definitions
- current state snapshot and repeated snapshots over time
- recorder summaries and deeper recorder samples
- core, supervisor, and add-on logs
- security and exposure reports
- integration profiles for ESPHome, MQTT, Broadlink, and HACS
- a machine-readable uncertainty register

## What it intentionally does not try to do

This app does **not** aim to create a full raw copy of your system.

It deliberately avoids or limits:

- raw secret values
- tokens and direct credentials where detected
- byte-for-byte restore fidelity
- broad export of operational internals that are not necessary for analysis

## Output

The app produces:

- exactly **one `.tar.gz` archive**
- written to `/share`
- with **no leftover extracted export directory** after packaging

## Recommended ChatGPT workflow

### Direct path

- export → upload → analyze

### Recommended path

Use **two ChatGPT instances**:

- **Instance 1** analyzes, inventories, validates, and prepares a handoff package.
- **Instance 2** uses that prepared material to optimize, refactor, or redesign the system.

## Greenfield rebuild

The exporter also supports a clean rebuild workflow:

1. export the current system
2. extract requirements and critical behavior
3. ignore structural legacy unless intentionally retained
4. design a clean target architecture
5. migrate only what is actually needed

## Important notes

### One-shot behavior

This app is intended as a **one-shot app**:

- start
- export
- exit

### Start on boot

If **Start on boot** is still enabled from an older installation state, disable it manually in the Home Assistant UI.

### Themes warning

If `configuration.yaml` references `frontend: themes: !include_dir_merge_named ...` but the referenced directory does not exist in the real Home Assistant config directory, the exporter will warn about it.

That is usually a **Home Assistant configuration finding**, not an exporter bug.

### Operator intent

For best downstream results, optionally provide:

- `operator_intent.md`
- `operator_intent.json`

These files can document:

- target architecture
- critical automations
- intentionally retained legacy behavior
- naming rules
- areas that must never be changed automatically

## High-level export domains

The archive typically contains these top-level areas:

- `source_sanitized/`
- `normalized/`
- `inventory/`
- `runtime/`
- `metadata/`

## Further documentation

- `DOCS.md` – technical reference
- `EXPORT_SCHEMA.md` – machine-oriented export structure contract
- `CHATGPT_WORKFLOWS.md` – workflow guidance and copy-paste prompts
- `CHANGELOG.md` – version history
