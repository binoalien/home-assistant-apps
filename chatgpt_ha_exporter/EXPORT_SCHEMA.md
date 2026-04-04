# ChatGPT HA Exporter – Export Schema

## Intro

Dieses Dokument ist der kompakte, schema-nahe Export-Vertrag für ChatGPT-HA-Exports.
Es definiert **welche Artefakte erwartet werden**, ob sie **verpflichtend** sind, welchen **Stability-Level** sie haben und unter welchen **Bedingungen** sie fehlen dürfen.

Wiederkehrende Konzeptdefinitionen werden **nicht erneut erklärt**, sondern referenziert:

- Sanitization Model: `DOC_BLOCKS.md` → **Sanitization Model**
- Uncertainty Categories: `DOC_BLOCKS.md` → **Uncertainty Categories**
- Top-Level Export Domains: `DOC_BLOCKS.md` → **Top-Level Export Domains**

---

## Artifact Matrix

| artifact_path | required | stability_level | description | conditions |
|---|---|---|---|---|
| `ha_chatgpt_export_<timestamp>Z/` | yes | Stable Core | Export-Root innerhalb des TAR.GZ-Archivs. | Genau ein Export-Root pro Archiv. Präfix kann konfigurationsabhängig variieren. |
| `inventory/` | yes | Stable Core | Kern-Domain für strukturierte Analyseausgaben. | Muss vorhanden sein. |
| `metadata/` | yes | Stable Core | Kern-Domain für Manifest/Report/Checksums. | Muss vorhanden sein. |
| `source_sanitized/` | no | Source-Dependent | Sanitized Source-Kopien (Config, Blueprints, Custom Code usw.). | Fehlt bei deaktiviertem Export-Scope oder wenn Quellmaterial nicht existiert. |
| `normalized/` | no | Stable Derived | Normalisierte, analysefreundliche Views (typisch `normalized/storage/*.json`). | Fehlt bei deaktiviertem Normalized-Block. |
| `runtime/` | no | Optional Runtime | Laufzeit-/API-abhängige Artefakte (Logs, Snapshots, Recorder). | Fehlt bei deaktiviertem Runtime-Block oder fehlender API/Umgebung. |
| `metadata/export_manifest.json` | yes | Stable Core | Maschinelles Manifest (Struktur, Counts, Coverage, Warnings). | Hard Missing, falls nicht vorhanden. |
| `metadata/export_report.json` | yes | Stable Core | Strukturierter Export-Laufbericht. | Hard Missing, falls nicht vorhanden. |
| `metadata/export_summary.md` | yes | Stable Core | Menschlich lesbare Zusammenfassung des Exports. | Muss vorhanden sein. |
| `metadata/checksums.sha256` | yes | Stable Core | Prüfsummenliste (eine Zeile pro exportierter Datei außer sich selbst). | Count-Semantik muss mit Manifest/Report konsistent sein. |
| `metadata/operator_intent_template.md` | no | Stable Derived | Template zur Dokumentation von Zielarchitektur/Constraints. | Optional, exporter-/workflowabhängig. |
| `metadata/operator_intent_import_manifest.json` | no | Stable Derived | Status der Operator-Intent-Erkennung/Übernahme. | Optional; in reiferen Exporter-Versionen typischerweise vorhanden. |
| `metadata/operator_intent_context.json` | no | Stable Derived | Strukturierter Operator-Intent-Kontext (auch leer/default möglich). | Optional; kann auch ohne gefundenen externen Intent vorhanden sein. |
| `inventory/storage_inventory.json` | yes | Stable Core | Übersicht über `.storage`-Quellen inkl. exported/available/missing. | Hard Missing, falls nicht vorhanden. |
| `inventory/config_inventory.json` | yes | Stable Core | Übersicht über Config-Quellen/Verzeichnisse inkl. Existenzaussagen. | Hard Missing, falls nicht vorhanden. |
| `inventory/core_info.json` | yes | Stable Core | Zusammenfassung Home Assistant Core-Informationen. | Muss vorhanden sein (sofern exporter nicht explizit inkompatibel konfiguriert). |
| `inventory/supervisor_info.json` | yes | Stable Core | Zusammenfassung Supervisor-Informationen (wenn verfügbar). | Bei fehlendem Supervisor sollte „unavailable/partial“-Semantik statt falscher Definitivwerte genutzt werden. |
| `inventory/addons.json` | no | Stable Derived | Sanitized Add-on-Inventar (Name/Slug/Version/Status, soweit sicher). | Erwartet in Full-Feature-Exports; optional bei Scope/API-Limits. |
| `inventory/api_config.json` | no | Stable Derived | Sanitized API-Kontext/Komponentenübersicht. | Erwartet in Full-Feature-Exports; optional bei Scope/API-Limits. |
| `inventory/helper_source_definitions.json` | no | Stable Derived | Normalisierte Helper-Definitionen aus YAML-Quellen. | Optional; abhängig von vorhandenen Quellen und Export-Scope. |
| `inventory/helper_source_definitions.storage.json` | no | Stable Derived | Normalisierte Helper-Definitionen aus unterstützten `.storage`-Quellen. | Optional; abhängig von `.storage`-Datenlage. |
| `inventory/template_source_definitions.json` | no | Stable Derived | Normalisierte Template-Definitionen aus YAML-Quellen. | Optional; quell- und scopeabhängig. |
| `inventory/template_source_definitions.storage.json` | no | Stable Derived | Normalisierte Template-Definitionen aus UI-/Storage-Verwaltung. | Optional; quell- und scopeabhängig. |
| `inventory/relationship_integrity_report.json` | no | Stable Derived | Validiert rekonstruierbare Beziehungen (Device/Entity/Area/Config Entry). | Stark empfohlen; optional bei reduziertem Scope. |
| `inventory/security_exposure_report.json` | no | Stable Derived | Strukturorientierter Security-Kontext inkl. Missing-vs-Observed-Trennung. | Stark empfohlen; optional bei reduziertem Scope. |
| `inventory/uncertainty_register.json` | no | Stable Derived | Register residualer Unsicherheiten. Kategorien siehe `DOC_BLOCKS.md`. | Stark empfohlen; optional bei reduziertem Scope. |
| `inventory/addon_options_profiles.json` | no | Stable Derived | Sanitized Add-on-Optionen inkl. schema-orientierter Hinweise. | Optional; endpoint-/scopeabhängig. |
| `inventory/addon_stats_profiles.json` | no | Stable Derived | Add-on-Statistiken aus unterstützten Endpoints. | Runtime/API-abhängig; kann als Runtime Missing klassifiziert sein. |
| `inventory/integration_profiles/index.json` | no | Stable Derived | Index generierter Integrationsprofile. | Optional; nur bei aktivierter Profilgenerierung. |
| `inventory/integration_profiles/*.json` | no | Stable Derived | Integrationsprofile (z. B. ESPHome, MQTT, Broadlink, HACS). | Optional; integrations- und scopeabhängig. |
| `normalized/storage/core.device_registry.json` | no | Stable Derived | Normalisierte Device-Registry. | Für starke Analyse empfohlen; presence hängt von Normalized-Export ab. |
| `normalized/storage/core.entity_registry.json` | no | Stable Derived | Normalisierte Entity-Registry. | Für starke Analyse empfohlen; presence hängt von Normalized-Export ab. |
| `normalized/storage/core.area_registry.json` | no | Stable Derived | Normalisierte Area-Registry. | Optional; quell-/scopeabhängig. |
| `normalized/storage/core.config_entries.json` | no | Stable Derived | Normalisierte Config-Entry-Registry. | Optional; quell-/scopeabhängig. |
| `normalized/storage/auth.json` | no | Stable Derived | Normalisierte Auth-Konfiguration. | Optional; sanitization-/scopeabhängig. |
| `normalized/storage/http.json` | no | Stable Derived | Normalisierte HTTP-Konfiguration. | Optional; sanitization-/scopeabhängig. |
| `normalized/storage/core.network.json` | no | Stable Derived | Normalisierte Netzwerk-Konfiguration. | Optional; quell-/scopeabhängig. |
| `normalized/storage/input_boolean.json` | no | Stable Derived | Normalisierte Helper-Storage-Daten (input_boolean). | Optional; helper-/scopeabhängig. |
| `normalized/storage/input_number.json` | no | Stable Derived | Normalisierte Helper-Storage-Daten (input_number). | Optional; helper-/scopeabhängig. |
| `normalized/storage/input_select.json` | no | Stable Derived | Normalisierte Helper-Storage-Daten (input_select). | Optional; helper-/scopeabhängig. |
| `normalized/storage/schedule.json` | no | Stable Derived | Normalisierte Schedule-Daten. | Optional; helper-/scopeabhängig. |
| `normalized/storage/timer.json` | no | Stable Derived | Normalisierte Timer-Daten. | Optional; helper-/scopeabhängig. |
| `source_sanitized/config/` | no | Source-Dependent | Sanitized HA-Config-Baum. | Fehlt bei deaktiviertem Scope oder nicht vorhandener Config-Struktur. |
| `source_sanitized/config/configuration.yaml` | no | Source-Dependent | Sanitized Hauptkonfiguration. | Nur falls Quelle vorhanden und eingeschlossen. |
| `source_sanitized/config/automations.yaml` | no | Source-Dependent | Sanitized Automationen. | Nur falls Quelle vorhanden und eingeschlossen. |
| `source_sanitized/config/scripts.yaml` | no | Source-Dependent | Sanitized Scripts. | Nur falls Quelle vorhanden und eingeschlossen. |
| `source_sanitized/config/scenes.yaml` | no | Source-Dependent | Sanitized Scenes. | Nur falls Quelle vorhanden und eingeschlossen. |
| `source_sanitized/config/template.yaml` | no | Source-Dependent | Sanitized Template-Konfiguration. | Nur falls Quelle vorhanden und eingeschlossen. |
| `source_sanitized/config/themes/` | no | Source-Dependent | Sanitized Themes. | Source Missing, wenn Themes nicht existieren. |
| `source_sanitized/dashboards/` | no | Source-Dependent | Sanitized Dashboards. | Nur falls Quelle vorhanden und eingeschlossen. |
| `source_sanitized/blueprints/` | no | Source-Dependent | Sanitized Blueprints. | Nur falls Quelle vorhanden und eingeschlossen. |
| `source_sanitized/custom_components/` | no | Source-Dependent | Sanitized Custom Components. | Nur falls Quelle vorhanden und eingeschlossen. |
| `source_sanitized/python_scripts/` | no | Source-Dependent | Sanitized Python Scripts. | Source Missing, wenn kein `python_scripts/` existiert. |
| `source_sanitized/pyscript/` | no | Source-Dependent | Sanitized Pyscript-Domain. | Source Missing, wenn kein `pyscript/` existiert. |
| `source_sanitized/appdaemon/` | no | Source-Dependent | Sanitized AppDaemon-Domain. | Source Missing, wenn kein `appdaemon/` existiert. |
| `source_sanitized/esphome/` | no | Source-Dependent | Sanitized ESPHome-Domain. | Source Missing, wenn kein `esphome/` existiert. |
| `runtime/state_snapshot.ndjson` | no | Optional Runtime | Einzelner State-Snapshot. | Runtime/API-abhängig, kann fehlen. |
| `runtime/state_snapshots/*.ndjson` | no | Optional Runtime | Mehrere State-Snapshots (Sampling/Serie). | Runtime/API-abhängig, kann fehlen. |
| `runtime/state_snapshots_summary.json` | no | Optional Runtime | Zusammenfassung der State-Snapshot-Erfassung. | Optional; abhängig von Snapshot-Feature. |
| `runtime/core.latest.log.txt` | no | Optional Runtime | Letztes Core-Log. | Optional; runtime-scope-/zugriffsabhängig. |
| `runtime/supervisor.latest.log.txt` | no | Optional Runtime | Letztes Supervisor-Log. | Optional; supervisor-/runtime-abhängig. |
| `runtime/addon_logs/*.txt` | no | Optional Runtime | Add-on-Logs. | Scope Missing bei deaktivierten Add-on-Logs; Runtime Missing bei Endpoint-Limitierung. |
| `runtime/recorder_summary.json` | no | Optional Runtime | Recorder-Zusammenfassung. | Optional; recorder-/DB-/endpointabhängig. |
| `runtime/recorder_state_samples.ndjson` | no | Optional Runtime | Recorder State-Samples. | Optional; recorder-/samplingabhängig. |
| `runtime/recorder_event_samples.ndjson` | no | Optional Runtime | Recorder Event-Samples. | Optional; recorder-/samplingabhängig. |
| `runtime/recorder_event_type_counts.json` | no | Optional Runtime | Recorder Event-Typ-Häufigkeiten. | Optional; recorder-/endpointabhängig. |
| `runtime/recorder_statistics_summary.json` | no | Optional Runtime | Recorder Statistik-Zusammenfassung. | Optional; recorder-/endpointabhängig. |
| `runtime/recorder_deep_export_summary.json` | no | Optional Runtime | Zusammenfassung tiefer Recorder-Exporte. | Optional; nur bei Deep-Export-Feature. |
| `runtime/recorder*.db*` | no | Optional Runtime | Recorder-DB-Kopie. | Nur bei explizit aktivierter DB-Kopie. |

---

## Interpretation / Notes

- **Missing-Klassifikation ist verpflichtend**:
  - **Hard Missing**: required + unerwartet fehlend (z. B. `metadata/export_manifest.json`).
  - **Scope Missing**: absichtlich nicht exportiert (Optionen/Scope).
  - **Source Missing**: im HA-Quellsystem nicht vorhanden.
  - **Runtime Missing**: API-/Umgebungsabhängig nicht verfügbar.
- **Confidence-Regel**: Bei fehlenden Quellen in Derived Reports `unknown`/`not_exported`/`unavailable`/`partial` bevorzugen; keine falsche Definitivität (`0`, `false`, `none`) ohne Nachweis.
- **Referential Integrity ist Pflicht**: Beziehungen (device↔entity, area↔device, config entry↔device/entity, helper/template↔entities) müssen rekonstruierbar bleiben; stabile Pseudonyme sind erlaubt, Kollaps vieler IDs auf einen Platzhalter ist unzulässig.
- **Validator-Mindestchecks**:
  - Archiv ist lesbar; genau ein Export-Root.
  - `manifest`/`report`/`summary` vorhanden.
  - File-Counts und Checksum-Counts plausibel/konsistent.
  - Required Domains/Artefakte vorhanden, Optionals korrekt klassifiziert.
- **Minimal Acceptance Profile (für ChatGPT-Analyse)**:
  - `metadata/export_manifest.json`
  - `metadata/export_report.json`
  - `metadata/checksums.sha256`
  - `inventory/storage_inventory.json`
  - `inventory/config_inventory.json`
  - `normalized/storage/core.device_registry.json`
  - `normalized/storage/core.entity_registry.json`
- **Empfohlene Consumer-Reihenfolge**: manifest → report → storage/config inventory → relationship/security/uncertainty → normalized registries → source_sanitized bei Bedarf → runtime zur Bestätigung.
- **Nicht-Ziele**: Keine Garantie auf Restore-Vollständigkeit, operative Korrektheit oder vollständige Ambiguitätsauflösung.
