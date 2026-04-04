# ChatGPT HA Exporter – Recommended Workflows with ChatGPT

## Scope

This document only covers workflow design, handoff discipline, and prompt usage across ChatGPT instances.
Shared canonical concept blocks are referenced from `DOC_BLOCKS.md`; export-structure contract details remain in `EXPORT_SCHEMA.md`.
For canonical documentation responsibilities, see `DOC_BLOCKS.md` → **“Documentation Roles”**.

This document explains the **operational use** of ChatGPT HA Exporter with ChatGPT.

Canonical workflow split is defined in `DOC_BLOCKS.md` → **“Two-Instance Workflow Rule”**.
This document provides the detailed procedures and prompts that operationalize that rule.

---

## 1. Choose the right workflow

### 1.1 Workflow A – Improve an existing Home Assistant system

Use this when you want to:
- keep the current system as the baseline
- remove legacy clutter gradually
- improve performance, security, and maintainability
- refactor without unnecessary behavioral breakage

**Goal:** improve the current system in a controlled way.

**Roles:**
- **Instance 1:** analysis, inventory, uncertainty/risk detection, handoff preparation
- **Instance 2:** optimization, refactoring, target structure, implementation planning

### 1.2 Workflow B – Rebuild Home Assistant from scratch

Use this when you want to:
- stop evolving the legacy structure directly
- avoid carrying forward historical workarounds and inconsistencies
- use the old system only as a requirements source
- define a clean architecture from the ground up

**Goal:** build a new target system that preserves required behavior without preserving legacy structure.

**Roles:**
- **Instance 1:** requirements extraction, device/domain inventory, critical behavior capture, non-carry-forward identification
- **Instance 2:** greenfield architecture and migration strategy

---

## 2. Ground rules

### 2.1 Always start with a current export

For strong results, the export should usually include:
- storage context
- runtime context
- logs
- recorder summary or deep export
- security exposure report
- integration profiles
- uncertainty register

### 2.2 Do not refactor raw data immediately

The raw export should first be:
- inventoried
- normalized
- validated
- prioritized
- annotated with uncertainty

Only then should another instance propose concrete changes.

### 2.3 Separate facts, inferences, and uncertainty

Always distinguish facts, inferences, and uncertainties. For uncertainty category labels, use **`DOC_BLOCKS.md` → “Uncertainty Categories”**.

### 2.4 Add operator intent when possible

Provide one of:
- `operator_intent.md`
- `operator_intent.json`

Useful topics:
- target architecture
- intentionally retained legacy behavior
- critical automations
- naming rules
- areas that must never be changed automatically

### 2.5 Insert a human checkpoint between instances

Before handing off from Instance 1 to Instance 2, confirm:
- Is the analysis consistent?
- Are critical areas missing?
- Was operator intent understood correctly?
- Are you optimizing the current system or designing a replacement?

---

## 3. Workflow A – Improve the current system

### 3.1 Sequence

1. Generate a current export.
2. Give the archive to Instance 1.
3. Review the handoff package.
4. Give the reviewed handoff to Instance 2.
5. Let Instance 2 prioritize improvements and refactors.
6. Apply selected changes.
7. Generate a new export.
8. Repeat if needed.

### 3.2 Instance 1 role

**Mission:** convert the export into a reliable handoff package for optimization work.

**Does:**
- unpacking and inventory
- consistency checking
- uncertainty mapping
- risk identification
- technical-debt identification
- refactoring preparation
- structured handoff generation

**Does not:**
- execute final refactors
- redesign blindly
- invent missing data

### 3.3 Recommended outputs from Instance 1

The handoff should ideally contain:
- system overview
- inventory of integrations/devices/entities/areas/helpers/templates
- automation and script analysis
- dashboard/frontend findings
- relationship and dependency mapping
- security/performance/maintainability findings
- uncertainty register interpretation
- prioritized improvement opportunities
- explicit “safe first” actions
- explicit “risky / needs confirmation” actions

### 3.4 Instance 2 role

**Mission:** turn the prepared handoff into a concrete improvement and refactoring plan.

**Should produce:**
- prioritized change list
- rationale, impact, dependencies, and risks per change
- safe-first implementation ordering
- suggested file and YAML changes where appropriate
- explicit guardrails for risky areas

---

## 4. Workflow B – Greenfield rebuild without legacy baggage

### 4.1 Principle

Use the legacy system as:
- requirements source
- behavior source
- inventory source
- risk source

Do **not** use it as the default structural blueprint.

### 4.2 Sequence

1. Generate a current export.
2. Give the archive to Instance 1.
3. Extract requirements and “must preserve” behavior.
4. Review the results manually.
5. Give the reviewed handoff to Instance 2.
6. Design the clean target architecture.
7. Define migration order.
8. Rebuild selectively.

### 4.3 Instance 1 role

**Mission:** separate functional requirements from legacy structure.

**Should extract:**
- device and integration inventory
- critical automations and behavior
- helper and template roles
- dashboard purpose
- naming issues
- legacy patterns not worth preserving
- migration constraints
- no-go areas

**Should not:**
- mirror the old structure automatically
- assume all legacy logic is worth keeping

### 4.4 Instance 2 role

**Mission:** design a new target system from scratch.

**Should produce:**
- target architecture
- domain boundaries
- naming strategy
- helper/template strategy
- automation design principles
- dashboard structure principles
- migration phases
- items that should be intentionally dropped

---

## 5. Handoff rules between instances

### 5.1 Handoff from Instance 1 to Instance 2 must include

- clear system summary
- scope definition
- facts vs inferences vs uncertainties
- high-risk areas
- safe-first areas
- critical missing context
- recommended work order
- primary source artifacts to trust most

### 5.2 What Instance 2 should trust first

Preferred input order:
1. `metadata/export_manifest.json`
2. `metadata/export_report.json`
3. `inventory/storage_inventory.json`
4. `inventory/config_inventory.json`
5. relationship/security/uncertainty reports
6. normalized registries
7. source files only where needed
8. runtime/log artifacts as corroboration, not sole truth

### 5.3 Never hand off only raw data if avoidable

A raw export alone is weaker than:
- raw export
- structured inventory
- uncertainty-aware summary
- explicit target instructions

---

## 6. Prompt library

## 6.1 Prompt for Instance 1 – Existing system analysis and handoff

```text
You are a Home Assistant analysis and handoff preparation agent.

I will provide a ChatGPT HA Exporter archive from an existing Home Assistant system. Your job is NOT to immediately refactor the system. Your job is to inspect, inventory, normalize, validate, and prepare a high-quality handoff package for a second ChatGPT instance.

Goals:
- identify what exists
- preserve facts and relationships
- separate facts, inferences, and uncertainty
- identify technical debt, security/performance risks, and refactoring opportunities
- prepare a structured handoff package for optimization/refactoring

Requirements:
- work strictly evidence-first
- do not invent missing data
- clearly distinguish hard export gaps, scope gaps, and principled uncertainty
- preserve relationships between devices, entities, areas, config entries, automations, helpers, and templates
- identify safe-first changes versus risky changes
- identify which source artifacts should be trusted most

Deliverables:
- executive summary
- system inventory
- risk and uncertainty summary
- prioritized improvement opportunities
- safe-first changes
- risky areas requiring care or confirmation
- a handoff document for the optimizer instance
```

## 6.2 Prompt for Instance 2 – Improve and refactor the current system

```text
You are a Home Assistant optimization and refactoring agent.

I will provide a prepared handoff package derived from a ChatGPT HA Exporter archive. Use the handoff as the primary input. Use the raw export only as supporting evidence when needed.

Goals:
- improve maintainability, clarity, and safety
- reduce duplication and legacy clutter
- simplify helpers/templates/automations where justified
- preserve intended behavior unless explicitly told otherwise

Requirements:
- do not invent missing facts
- do not silently redesign the system without justification
- for every recommended change, provide rationale, impact, dependencies, and risk
- clearly mark safe-first changes and risky changes
- propose concrete file/YAML changes where useful
```

## 6.3 Prompt for Instance 1 – Requirements extraction for greenfield rebuild

```text
You are a Home Assistant requirements and blueprint extraction agent.

I will provide a ChatGPT HA Exporter archive from an existing Home Assistant system. Your job is NOT to improve the current structure. Your job is to extract requirements, critical behavior, constraints, and target principles for a clean rebuild.

Goals:
- identify what the system must do
- identify devices, domains, and critical behavior
- identify legacy behavior that should not automatically be preserved
- prepare a clean handoff for a greenfield architecture instance

Requirements:
- treat the old system as a requirements source, not as the target structure
- separate facts, inferences, and uncertainty
- identify critical automations and no-go areas
- identify migration constraints

Deliverables:
- functional requirements summary
- device/domain inventory
- critical behavior inventory
- migration constraints
- intentionally non-preserved legacy items
- target principles for a clean rebuild
- handoff for the greenfield architecture instance
```

## 6.4 Prompt for Instance 2 – Greenfield architecture and rebuild planning

```text
You are a Home Assistant greenfield architecture and rebuild planning agent.

I will provide a prepared requirements and handoff package derived from a ChatGPT HA Exporter archive. Use that handoff as the primary input. Do not mirror the old structure without justification.

Goals:
- design a clean target architecture from scratch
- preserve required behavior without preserving legacy structure by default
- define naming, helper, template, automation, dashboard, and integration principles
- define a migration order

Requirements:
- do not inherit the legacy layout automatically
- justify every major structural decision
- identify risky or operator-dependent decisions clearly
- propose concrete file/YAML structure where useful

Deliverables:
- target architecture
- domain boundaries
- naming strategy
- helper/template strategy
- automation design rules
- dashboard design rules
- migration phases
- intentionally dropped legacy items
```

---

## 7. Recommended operator intent topics

If you want both instances to guess less, include `operator_intent.md` or `operator_intent.json` with topics such as:

- target architecture direction
- integrations/add-ons that are strategically preferred
- critical automations or devices that must not fail
- naming language and naming rules
- never-change areas
- legacy behavior intentionally kept
- preferred trade-offs between stability, clarity, performance, privacy, and extensibility

---

## 8. Quality checks after each stage

### After Instance 1

Check:
- Are facts and uncertainties separated clearly?
- Are critical devices/integrations/automations covered?
- Are safe-first and risky areas explicit?
- Is the handoff usable without follow-up questions?

### After Instance 2

Check:
- Are changes prioritized?
- Are risky changes marked clearly?
- Are dependencies and sequencing explicit?
- Does the plan preserve intended behavior where required?

---

## 9. Common mistakes to avoid

Avoid:
- using one instance for everything
- refactoring directly from raw data without an analysis stage
- treating missing data as proof of absence
- silently redesigning architecture without stating it
- preserving legacy workarounds automatically
- using logs/runtime artifacts as the only truth source
- mirroring the old system in a cleaner-looking but equally tangled structure

---

## 10. Relationship to the other documents

- `README.md` explains **what** the app is and how to install/use it.
- `DOCS.md` explains **how** the exporter works technically.
- `EXPORT_SCHEMA.md` defines **what structure** downstream consumers can expect.
- `CHATGPT_WORKFLOWS.md` explains **how to operate ChatGPT instances effectively** on top of that export.
