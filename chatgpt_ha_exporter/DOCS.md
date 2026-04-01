# ChatGPT HA Exporter – technische Dokumentation

## 1. Überblick

Der ChatGPT HA Exporter erzeugt ein sanitisiertes Analysepaket aus Home Assistant. Das Paket ist nicht auf Wiederherstellung optimiert, sondern auf **Analyse, Kontext-Erhalt und sichere Weitergabe**.

Der Exporter versucht drei Ziele gleichzeitig zu erfüllen:

- **ausreichende Tiefe** für belastbare Analyse
- **Datensparsamkeit** bei sensiblen Inhalten
- **Strukturtreue** für Beziehungen und Refactoring-Kontext

## 2. Grundprinzipien

### 2.1 Analyse statt Backup

Der Exporter ist kein klassisches Backup-System. Er priorisiert:

- Struktur
- Beziehungen
- Inventarisierung
- Laufzeitkontext
- Auswertungshilfen

### 2.2 Sanitization mit Strukturerhalt

Sensible Inhalte werden redigiert oder pseudonymisiert. Dabei gilt:

- echte Secrets und operative Zugangsdaten sollen nicht im Klartext landen
- referenzielle Beziehungen sollen erhalten bleiben
- Devices, Entities, Areas und Config Entries sollen weiter zusammen analysierbar bleiben

### 2.3 Ein Archiv, kein verstreutes Ausgabeziel

Der Export läuft intern in ein temporäres Arbeitsverzeichnis und endet in **einem TAR.GZ-Archiv unter `/share`**. Das entpackte Arbeitsverzeichnis wird danach entfernt.

## 3. Exportphasen

## 3.1 Quelldateien einsammeln

Aus dem Home-Assistant-Konfigurationsordner werden – abhängig von den Optionen – relevante Dateien und Verzeichnisse gelesen, darunter:

- Hauptkonfiguration
- Dashboards
- Blueprints
- Custom Components
- Python-/Pyscript-/AppDaemon-Logik
- ESPHome-Quellen
- Themes
- Zusatzdateien für Analyse und Kontext

## 3.2 `.storage` erfassen und normalisieren

Ausgewählte `.storage`-Dateien werden nicht nur roh, sondern zusätzlich normalisiert ausgewertet. Das betrifft unter anderem:

- Registries
- Config Entries
- Frontend-Kontext
- Security-/Auth-/Netzwerk-Kontext
- Trace-/Repairs-Daten
- Helper- und Template-Definitionen
- Integrationsspezifische Metadaten

## 3.3 Runtime- und API-Kontext erfassen

Zusätzlich können Laufzeitdaten abgefragt werden, z. B.:

- aktueller State-Snapshot
- Service-Katalog
- Supervisor-Informationen
- Core-/Supervisor-/Add-on-Logs
- Backup-Kontext
- Add-on-Informationen und Add-on-Optionen

## 3.4 Zusatzberichte erzeugen

Aus den exportierten Daten werden zusätzliche Inventare und Berichte abgeleitet, etwa:

- Security-/Exposure-Report
- Relationship-Integrity-Report
- Integrationsprofile
- Unsicherheitsregister
- Export-Manifest, Report und Summary

## 4. Verzeichnisstruktur des Exportarchivs

## 4.1 `source_sanitized/`

Sanitisierte Quelldateien und -verzeichnisse aus der Home-Assistant-Konfiguration.

Typische Inhalte:

- `config/`
- `dashboards/`
- `blueprints/`
- `custom_components/`
- `python_scripts/`
- `pyscript/`
- `appdaemon/`
- `esphome/`
- referenzierte Theme-Dateien

## 4.2 `normalized/`

Normalisierte JSON-Sichten auf exportierte Daten.

Typische Inhalte:

- `normalized/storage/*.json`
- sanitisierte und für Analyse vereinheitlichte Strukturansichten

## 4.3 `inventory/`

Strukturierte Auswertungen und Inventare.

Typische Inhalte:

- `addons.json`
- `api_config.json`
- `core_info.json`
- `supervisor_info.json`
- `storage_inventory.json`
- `config_inventory.json`
- `helper_source_definitions*.json`
- `template_source_definitions*.json`
- `relationship_integrity_report.json`
- `security_exposure_report.json`
- `integration_profiles/*.json`
- `uncertainty_register.json`

## 4.4 `runtime/`

Laufzeitbezogene Daten und Zusammenfassungen.

Typische Inhalte:

- `state_snapshot.ndjson`
- `state_snapshots/*.ndjson`
- `state_snapshots_summary.json`
- `core.latest.log.txt`
- `supervisor.latest.log.txt`
- `addon_logs/*.txt`
- Recorder-Zusammenfassungen und Recorder-Tiefenexporte

## 4.5 `metadata/`

Metadaten zum Export selbst.

Typische Inhalte:

- `export_manifest.json`
- `export_report.json`
- `export_summary.md`
- `checksums.sha256`
- `operator_intent_template.md`
- `operator_intent_import_manifest.json`
- `operator_intent_context.json`

## 5. Wichtige Berichte

## 5.1 `export_manifest.json`

Maschinenlesbare Beschreibung des erzeugten Pakets.

Enthält typischerweise:

- Zähler
- enthaltene Exportblöcke
- Zielpfade des nutzerrelevanten Archivs
- Ausführungs- und Strukturmetadaten

## 5.2 `export_report.json`

Strukturierter Ergebnisbericht des Laufs.

Enthält typischerweise:

- Statusinformationen
- Warnungen
- erzeugte Inventare und Runtime-Blöcke
- Zusammenfassung der wichtigsten Exportteile

## 5.3 `export_summary.md`

Menschenlesbare Kurzfassung des Exports.

Geeignet, um schnell zu sehen:

- was exportiert wurde
- welche Warnungen es gab
- welche Hauptbereiche vorhanden sind

## 5.4 `relationship_integrity_report.json`

Prüft, ob zentrale Verknüpfungen erhalten geblieben sind, insbesondere:

- Device ↔ Entity
- Area ↔ Device
- Config Entry ↔ Device/Entity

## 5.5 `security_exposure_report.json`

Sammelt sicherheitsrelevanten Strukturkontext, z. B.:

- HTTP-/URL-Kontext
- Auth-/Provider-Sicht
- Exposed Entities
- Netzwerk-Hinweise
- Mobile App / Assist / Frontend-Hinweise, sofern exportiert

## 5.6 `uncertainty_register.json`

Maschinenlesbare Liste verbleibender Unsicherheiten.

Unterschieden werden insbesondere:

- `hard_export_gap`
- `export_scope_gap`
- `principled_uncertainty`

## 6. Sanitization-Strategie

## 6.1 Redigiert werden vor allem

- Secrets
- Tokens
- Webhook-IDs
- Client-Secrets
- Hosts und operative Zugangspfade, wenn sie als sensibel bewertet werden
- Felder, die typischerweise direkte Zugangsdaten oder Recovery-relevante Interna enthalten

## 6.2 Erhalten bleiben sollen

- Slugs
- Versionen
- Domains
- nicht sensible Komponentenbezeichnungen
- Entity-/Device-/Area-/Config-Entry-Beziehungen
- analytisch notwendige Strukturfelder

## 6.3 Pseudonymisierung

Wo nötig, werden Werte nicht einfach gelöscht, sondern stabil pseudonymisiert, damit Referenzen im Paket erhalten bleiben.

## 7. Konfigurationsoptionen

Die Optionen in `config.yaml` steuern den Umfang des Exports. Die folgenden Gruppen sind wichtiger als eine bloße alphabetische Liste.

## 7.1 Grundlegender Analyseumfang

- `include_current_state_snapshot`
- `include_service_catalog`
- `include_dashboards`
- `include_blueprints`
- `include_custom_components`

Diese Optionen steuern die Basis für Struktur- und UI-Analyse.

## 7.2 Zusätzliche Quelllogik

- `include_python_scripts`
- `include_pyscript`
- `include_appdaemon`
- `include_esphome`
- `include_themes`

Diese Gruppe ist wichtig, wenn Logik nicht nur in YAML und UI-Entities steckt.

## 7.3 Logs und Laufzeit

- `include_logs`
- `include_log_archives`
- `max_log_lines`
- `include_supervisor_logs`
- `include_addon_logs`
- `addon_log_lines`

Sinnvoll für Fehleranalyse, Startprobleme und Laufzeitkorrelation.

## 7.4 Recorder

- `include_recorder_summary`
- `include_recorder_deep_export`
- `include_recorder_db_copy`
- `recorder_days`
- `recorder_state_sample_limit`
- `recorder_event_sample_limit`
- `recorder_statistics_limit`
- `recorder_entity_history_limit`

Diese Gruppe steuert, ob nur eine Zusammenfassung oder tieferer Recorder-Kontext exportiert wird.

## 7.5 Storage und Systemkontext

- `include_raw_storage_files`
- `include_extended_storage`
- `include_security_storage`
- `include_backup_metadata`
- `include_frontend_storage`
- `include_trace_storage`

Diese Optionen erweitern die `.storage`-Abdeckung und sind oft entscheidend für tiefe Analyse.

## 7.6 Abgeleitete Spezialberichte

- `include_helper_source_definitions`
- `include_template_source_definitions`
- `include_relationship_integrity_report`
- `include_backup_deep_context`
- `include_security_exposure_report`
- `include_integration_profiles`
- `include_uncertainty_register`

Diese Berichte erhöhen die Nutzbarkeit für nachgelagerte Analyse-Instanzen deutlich.

## 7.7 One-shot- und Zusatzkontext

- `include_multi_state_snapshots`
- `multi_state_snapshot_count`
- `multi_state_snapshot_interval_seconds`
- `include_operator_intent_template`
- `include_operator_intent_import`
- `include_addon_options_export`
- `include_addon_stats`
- `slim_hacs_assets`

## 8. Empfohlene Einstellungen

## 8.1 Solider Standardexport

Geeignet für die meisten Analysen:

- States: an
- Services: an
- Dashboards/Blueprints/Custom Components: an
- Logs: an
- Recorder Summary: an
- Recorder Deep Export: an
- Extended/Security/Trace Storage: an
- Integration Profiles: an
- Uncertainty Register: an
- HACS Slimming: an

## 8.2 Datenschutzsensibler Export

Wenn du mehr minimieren willst:

- `include_recorder_db_copy: false`
- Logs ggf. kürzen
- nur die wirklich nötigen Zusatzverzeichnisse einschalten
- Operator Intent separat und bewusst formulieren

## 8.3 Tiefenanalyse / Refactoring-Vorbereitung

Empfohlen für maximale Analysefähigkeit:

- alle wichtigen Inventare an
- Recorder Deep Export an
- Multi-Snapshots an
- Security/Trace/Frontend/Extended Storage an
- Add-on-Options-Export an
- Integrationsprofile an
- Operator Intent bereitstellen

## 9. Troubleshooting

## 9.1 Themes-Warnung

Wenn `configuration.yaml` Themes referenziert, aber das Zielverzeichnis fehlt oder leer ist, meldet der Exporter das.

Prüfen:

- existiert das referenzierte Verzeichnis im echten HA-Config-Ordner?
- liegen dort `.yaml`-Dateien?
- ist der Include-Pfad in `configuration.yaml` korrekt?

## 9.2 Fehlende Logs

Wenn bestimmte Logs fehlen:

- prüfen, ob die jeweilige Log-Option aktiv ist
- prüfen, ob der Endpunkt oder die Datei in der Instanz verfügbar ist
- beachten, dass Add-on-Logs Supervisor-Rechte und funktionierende Endpunkte benötigen

## 9.3 Keine Daten zu bestimmten Bereichen

Das bedeutet nicht immer einen Fehler. Mögliche Ursachen:

- Bereich ist im System nicht vorhanden
- Bereich ist per Option deaktiviert
- Bereich ist vorhanden, aber nicht lesbar oder nicht verfügbar
- Bereich wurde bewusst aus Scope- oder Datenschutzgründen ausgelassen

## 9.4 Start on boot

Das Add-on ist als One-shot-App gedacht. Falls **Start on boot** in deiner bestehenden Installation noch aktiv ist, deaktiviere den Schalter im Home-Assistant-UI.

## 10. Grenzen des Ansatzes

Auch ein sehr guter Export beseitigt nicht jede Unsicherheit.

Nicht rein datenbasiert klärbar sind zum Beispiel:

- gewünschte Zielarchitektur
- absichtlich beibehaltene Altlasten
- bevorzugte Namenssprache
- geschäftskritische Automationen
- Bereiche, die nie automatisch geändert werden dürfen

Dafür ist eine zusätzliche Datei wie `operator_intent.md` oder `operator_intent.json` sehr hilfreich.

## 11. Empfohlene Weitergabe an andere ChatGPT-Instanzen

Für beste Ergebnisse:

1. Export erzeugen.
2. Archiv hochladen.
3. Zuerst eine Instanz nur aufbereiten und inventarisieren lassen.
4. Danach eine zweite Instanz auf Basis dieser strukturierten Aufbereitung optimieren und refactoren lassen.

So trennst du **Analyse** und **Änderungsplanung** sauber voneinander.

## 13. Empfohlene Nutzung mit ChatGPT

Eine praktische, prompt-orientierte Anleitung für den Einsatz dieses Exporters mit ChatGPT findest du in **`CHATGPT_WORKFLOWS.md`**.
Diese Datei enthält:

- den empfohlenen Zwei-Instanzen-Workflow für Analyse und Optimierung des bestehenden Systems
- einen separaten Zwei-Instanzen-Greenfield-Workflow für den kompletten Neuaufbau ohne Altlasten
- copy-paste-fertige Prompts für beide Instanzen
- Hinweise zu Operator Intent und Übergabe-Artefakten
