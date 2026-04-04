# ChatGPT HA Exporter – Canonical Documentation Blocks

## Scope

This file contains canonical, reusable text blocks shared across documentation files in this directory.
Use these blocks as the single source of truth for repeated cross-document concepts.

---

## Top-Level Export Domains

Canonical top-level domains in a typical export root:

- `source_sanitized/`
- `normalized/`
- `inventory/`
- `runtime/`
- `metadata/`

Notes:
- Depending on configuration and runtime/source availability, some domains can be optional.
- Contract-level required/optional rules remain defined in `EXPORT_SCHEMA.md`.

---

## Documentation Roles

Canonical responsibility split across documentation files:

- `README.md` → overview, install, and high-level usage
- `DOCS.md` → technical architecture, phases, options, and troubleshooting
- `EXPORT_SCHEMA.md` → formal machine-oriented export structure contract
- `CHATGPT_WORKFLOWS.md` → workflow design, instance handoff discipline, and prompt library

---

## Core Principles

Canonical principles across this documentation set:

1. Analysis over backup/restore: prioritize structure, relationships, runtime context, and diagnostics.
2. Structure-preserving sanitization: remove sensitive values while preserving analyzable linkage.
3. Single output artifact: exactly one `.tar.gz` written to `/share` without leftover extracted export tree.

---

## Two-Instance Workflow Rule

For high-quality outcomes, do not use one ChatGPT instance for all stages.

Recommended split:
- **Instance 1:** analysis/inventory/validation/handoff preparation
- **Instance 2:** optimization/refactoring/rebuild planning and implementation design

Human checkpoint before handoff:
- review consistency, gaps, operator intent fit, and whether the goal is optimization vs replacement.

---

## Sanitization Model

The exporter follows a structure-preserving sanitization approach.

### Redacted (examples)

- secrets
- tokens
- webhook IDs
- client secrets
- sensitive endpoints
- directly exploitable internals where required

### Preserved (examples)

- slugs
- versions
- domains
- non-sensitive structure
- analyzable relationships
- useful inventory markers

### Stable pseudonymization

Where values must remain referencable but should not remain raw, stable pseudonyms are used to preserve analyzable relationships.

---

## Uncertainty Categories

Canonical uncertainty categories used by exporter-derived reports:

- `hard_export_gap`
- `export_scope_gap`
- `principled_uncertainty`

Interpretation:
- `hard_export_gap`: expected artifact/data missing unexpectedly.
- `export_scope_gap`: artifact/data intentionally omitted by export scope/options.
- `principled_uncertainty`: uncertainty remains even with available evidence.
