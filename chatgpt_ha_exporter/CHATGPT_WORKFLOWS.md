# ChatGPT HA Exporter – Recommended Workflows with ChatGPT

## Scope

This document covers only workflow selection, two-instance role separation, and minimum handoff quality.
Canonical concept blocks are in `DOC_BLOCKS.md`; export structure contract details are in `EXPORT_SCHEMA.md`.

Documentation roles:
- `README.md` → overview and installation
- `DOCS.md` → technical reference
- `EXPORT_SCHEMA.md` → formal export structure contract
- `CHATGPT_WORKFLOWS.md` → compact workflow guide
- `PROMPT_LIBRARY.md` → full copy-paste prompts

Core rule:

> Do **not** use one ChatGPT instance for raw export analysis, target-state definition, and implementation planning.
> Use a **two-instance workflow**.

---

## 1) Which workflow should I use?

### Workflow A — Improve an existing Home Assistant system
Use Workflow A when the current system should remain the baseline and be improved iteratively.

Typical fit:
- gradual cleanup of legacy clutter
- safer refactoring with minimal behavior breakage
- better maintainability/performance/security without full rebuild

### Workflow B — Rebuild from scratch (greenfield)
Use Workflow B when the legacy system should be treated as a requirements source, not as a structural template.

Typical fit:
- stop carrying historical workarounds forward
- define a clean architecture first
- migrate behavior intentionally, not structure-by-structure

---

## 2) Instance roles (always two instances)

### Instance 1 (analysis/extraction)
- Works evidence-first on export artifacts.
- Produces structured, uncertainty-aware handoff material.
- **Does not** perform final redesign/refactoring decisions.

### Instance 2 (design/planning)
- Uses the reviewed handoff as primary input.
- Produces prioritized architecture/refactor/migration plans.
- Marks safe-first steps vs risky/operator-dependent steps.

---

## 3) Handoff minimum content (Instance 1 → Instance 2)

Every handoff must include at least:
1. **Scope + intent** (optimize existing vs greenfield rebuild)
2. **System summary** (short but complete)
3. **Facts / inferences / uncertainties** (explicitly separated)
4. **Risk map** (high-risk and safe-first areas)
5. **Critical gaps** (missing context/data that can change decisions)
6. **Recommended work order**
7. **Primary source trust order** (which artifacts are most authoritative)

If possible, add operator intent (`operator_intent.md` or `.json`) before Instance 2 starts.

---

## 4) Minimal process checklists

### Workflow A checklist
1. Create current export.
2. Instance 1 analyzes and prepares handoff.
3. Human review of handoff.
4. Instance 2 creates prioritized improvement/refactor plan.
5. Apply selected changes.
6. Re-export and iterate.

### Workflow B checklist
1. Create current export.
2. Instance 1 extracts requirements and must-preserve behavior.
3. Human review of extraction results.
4. Instance 2 designs target architecture + migration phases.
5. Rebuild selectively and validate.

---

## 5) Prompt references (full texts moved out of main flow)

Use full copy-paste prompts from `PROMPT_LIBRARY.md`:
- **P1**: Instance 1 for Workflow A (analysis + handoff)
- **P2**: Instance 2 for Workflow A (optimize/refactor)
- **P3**: Instance 1 for Workflow B (requirements extraction)
- **P4**: Instance 2 for Workflow B (greenfield architecture + migration)

---

## 6) Quality gate after each stage

### After Instance 1
- facts vs uncertainty clearly separated
- critical devices/integrations/automations covered
- safe-first vs risky areas explicit
- handoff usable without major follow-up

### After Instance 2
- changes/migration phases prioritized
- dependencies and sequencing explicit
- risky decisions clearly marked
- intended behavior preservation confirmed

---

## 7) Common mistakes

Avoid:
- one-instance end-to-end execution
- direct refactoring from raw data without analysis stage
- treating missing data as proof of absence
- silent redesign without explicit justification
- automatic legacy carry-over in greenfield mode

---

## 8) Relationship to other docs

- `README.md` → what the app is + usage
- `DOCS.md` → technical internals
- `EXPORT_SCHEMA.md` → export contract
- `CHATGPT_WORKFLOWS.md` → compact operations guide
- `PROMPT_LIBRARY.md` → full prompt appendix/library
