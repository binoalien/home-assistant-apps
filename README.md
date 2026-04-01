# Binoalien Home Assistant Apps

[Add Binoalien Home Assistant Apps to Home Assistant](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fbinoalien%2Fhome-assistant-apps)

This repository contains Home Assistant apps by **binoalien**.

## Included app

### ChatGPT HA Exporter

Folder:

`chatgpt_ha_exporter`

**ChatGPT HA Exporter** creates a sanitized, structure-preserving analysis package from Home Assistant so another ChatGPT instance can inspect, improve, optimize, refactor, or redesign the system with fewer wrong assumptions.

## Installation

1. Click the link above.
2. Add the repository to Home Assistant.
3. Open **Settings → Apps**.
4. Install **ChatGPT HA Exporter**.

## What this repository is for

This repository provides Home Assistant apps that are designed for:

- ChatGPT-assisted system analysis
- refactoring preparation
- performance and maintainability work
- security and exposure review
- greenfield rebuild planning

## Recommended use

### Improve an existing system

- generate an export
- hand the archive to ChatGPT
- analyze first, then optimize and refactor

### Rebuild from scratch without legacy baggage

- generate an export
- extract requirements and critical behavior
- define a clean target architecture
- rebuild deliberately instead of polishing legacy structure

## Documentation

The full app documentation lives in the app folder:

- `chatgpt_ha_exporter/README.md` – overview and usage
- `chatgpt_ha_exporter/DOCS.md` – technical reference
- `chatgpt_ha_exporter/EXPORT_SCHEMA.md` – formal export structure contract
- `chatgpt_ha_exporter/CHATGPT_WORKFLOWS.md` – recommended ChatGPT workflows and prompts
- `chatgpt_ha_exporter/CHANGELOG.md` – version history

## Note

This repository is a **Home Assistant app repository**.

The exporter is **not a backup or restore tool**. It is an **analysis export tool for ChatGPT-driven review and redesign**.
