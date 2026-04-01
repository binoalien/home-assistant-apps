# Changelog

This history was reconstructed as accurately as possible from the surviving project state and export/audit milestones. Early entries are less exact than later ones.

## 0.6.1

- sharpens uncertainty semantics for missing logic directories by distinguishing truly absent sources from export-scope gaps
- stabilizes `operator_intent_context.json` so it is always an object with explicit status metadata
- enriches storage-derived template definitions with linked `entity_id` / `entity_ids` when they can be reconstructed from the entity registry
- clarifies log fallback reporting when local `home-assistant.log` files are missing but API runtime logs were exported

## 0.6.0

- restores the later large-scale exporter state as a coherent project baseline
- aligns the exporter version across `config.yaml`, `export_bundle.py`, documentation, and packaging
- converts the project to English outside `translations/`
- rewrites the root `README.md` and app `README.md` as clean repository/app entry points
- rewrites `DOCS.md` as a high-end technical reference
- rewrites `CHATGPT_WORKFLOWS.md` as an operational two-instance workflow guide with prompt library
- keeps `EXPORT_SCHEMA.md` as the machine-oriented export contract
- removes shipped bytecode and reintroduces `.gitignore`
- translates user-facing runtime/export summary messages to English

## 0.5.8

- added `CHATGPT_WORKFLOWS.md` as a dedicated workflow and prompt document
- documented a full two-instance workflow for improving an existing Home Assistant system
- documented a separate two-instance greenfield workflow for rebuilding without legacy baggage
- added copy-paste prompts for analysis, optimization, requirements extraction, and greenfield planning

## 0.5.7

- rewrote `README.md` as compact user documentation
- rewrote `DOCS.md` as a technical reference instead of a changelog duplicate
- expanded `CHANGELOG.md` into a substantially fuller project history
- separated README, technical documentation, and change history more clearly

## 0.5.6

- fixed a remaining sanitization edge case for `include_uncertainty_register`
- completed the English configuration translations
- added complete German configuration translations

## 0.5.5

- removed the last unnecessary internal workdir path from user-facing export metadata

## 0.5.4

- always generated `operator_intent_import_manifest.json`
- always generated `operator_intent_context.json`
- removed internal workdir paths from user-facing summary/report outputs

## 0.5.3

- fixed mismatches between archive contents, manifest counts, report counts, and checksums
- improved HACS slimming for bulky frontend assets
- treated unsupported `/stats` endpoints as unsupported instead of global export errors
- set `startup: once` for one-shot behavior

## 0.5.2

- preserved helper IDs more reliably in helper-related stores
- exported `.storage/auth`
- made security reporting more honest when auth/network context is incomplete
- corrected uncertainty handling for existing logs and API-based log sources
- removed duplicate ESPHome export trees
- added optional HACS asset slimming
- cleaned temporary extracted export trees after packaging

## 0.5.1

- repaired helper extraction from actual helper stores
- repaired template extraction from real Home Assistant template config entries
- switched to more field-aware sanitization behavior
- preserved add-on slugs, versions, component names, and other non-sensitive structural values better
- corrected security/exposure logic for adapter, provider, and URL presence
- prevented misleading `config_inventory` entries for missing source directories

## 0.5.0

- added targeted add-on options export
- added add-on stats export
- introduced integration profiles for ESPHome, MQTT, Broadlink, and HACS
- introduced a machine-readable uncertainty register
- expanded the inventory layer toward refactoring-oriented analysis artifacts

## 0.4.0

- added JSON and Markdown security/exposure reports
- introduced import of `operator_intent` files
- supported operator intent from Home Assistant config, add-on context, and share context
- normalized imported operator intent into structured metadata

## 0.3.0

- added recorder deep exports
- added repeated state snapshots over time
- added snapshot summaries and delta views
- added deeper backup/restore context
- added additional runtime artifacts for later analysis instances

## 0.2.0

- broadened `.storage` coverage significantly
- added export of `python_scripts`, `pyscript`, `appdaemon`, `esphome`, and referenced themes
- added additional core, supervisor, and add-on logs
- introduced `relationship_integrity_report.json`
- added `operator_intent_template.md`

## 0.1.6

- read the actual theme include target from `configuration.yaml`
- added richer theme metadata to `config_inventory`

## 0.1.5

- replaced overly aggressive registry ID redaction with stable pseudonymization for relationship IDs
- preserved device↔entity, area, and config-entry relationships more reliably
- exported theme directories in line with configuration references
- improved the basis for device-centric analysis and graph reconstruction

## 0.1.4

- added dedicated helper source definitions
- added dedicated template source definitions
- expanded detection of helper/template sources beyond the earliest standard files

## 0.1.3

- intermediate maintenance version during the early expansion phase
- served as the working base for the helper/template improvements in 0.1.4
- exact individual changes cannot be reconstructed completely from the surviving artifacts

## 0.1.2

- moved the primary export toward the public add-on context rather than relying only on `/share`
- added clearer reporting on where exports can be found
- added last-export style diagnostics for early target-path problems
- improved behavior where `/share` was not usable as expected

## 0.1.1

- added `hassio_role: manager`
- improved supervisor API access for add-on inventory export

## 0.1.0

- first published version of ChatGPT HA Exporter
- exported a sanitized analysis package from Home Assistant
- included basic configuration, selected `.storage` data, states, services, and inventories
- established the base for later runtime, security, recorder, and refactoring-oriented expansion
