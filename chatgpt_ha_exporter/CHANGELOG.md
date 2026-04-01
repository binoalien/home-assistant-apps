# Changelog

Diese Historie wurde für die frühen Versionen **bestmöglich aus der tatsächlichen Entwicklungsfolge rekonstruiert**. Ab den späteren Versionen ist sie deutlich genauer.

## 0.5.8

- ergänzt `CHATGPT_WORKFLOWS.md` als eigenständige Workflow- und Prompt-Dokumentation
- beschreibt einen vollständigen Zwei-Instanzen-Workflow zur Analyse und Verbesserung des bestehenden Home-Assistant-Systems
- ergänzt einen separaten Zwei-Instanzen-Greenfield-Workflow für den kompletten Neuaufbau ohne Altlasten
- enthält copy-paste-fertige Prompts für Analyse-, Optimierungs-, Requirements- und Greenfield-Build-Instanzen
- verlinkt die neue Workflow-Dokumentation aus `README.md` und `DOCS.md`

## 0.5.7

- überarbeitet `README.md` vollständig als kompakte Nutzer-Dokumentation
- überarbeitet `DOCS.md` vollständig als technische Referenz statt als Kurz-Changelog
- erweitert `CHANGELOG.md` zu einer deutlich vollständigeren Versionshistorie
- trennt README, technische Doku und Änderungsverlauf klarer voneinander

## 0.5.6

- behebt einen Sanitization-Restfall: `include_uncertainty_register` wird nicht mehr fälschlich redigiert
- vervollständigt die englischen Übersetzungen für alle bekannten Konfigurationsoptionen
- ergänzt vollständige deutsche Übersetzungen
- entfernt `__pycache__` aus dem Add-on-Archiv
- dokumentiert klarer, dass der benutzerseitige Supervisor-Schalter **Start on boot** in bestehenden Installationen manuell deaktiviert werden muss, wenn er noch aktiv ist

## 0.5.5

- entfernt `paths.work_export_dir` aus `metadata/export_manifest.json`
- bereinigt die nutzerseitigen Metadaten um den letzten unnötigen internen Workdir-Pfad
- hebt die Version auf 0.5.5 an

## 0.5.4

- erzeugt `metadata/operator_intent_import_manifest.json` jetzt immer, auch wenn kein Operator-Intent gefunden wurde
- erzeugt `metadata/operator_intent_context.json` jetzt ebenfalls immer
- entfernt interne temporäre Workdir-Pfade aus nutzerseitigen Ausgaben wie `export_report.json` und `export_summary.md`
- verbessert die Konsistenz der Operator-Intent-Metadaten im Nicht-Import-Fall

## 0.5.3

- finalisiert Manifest-, Report- und Checksum-Logik in konsistenter Reihenfolge
- behebt abweichende Dateizählungen zwischen Archivinhalt, Manifest und Report
- macht HACS-Slimming deutlich wirksamer
- entfernt HACS-Sourcemaps, komprimierte Frontend-Artefakte und Font-Dateien bei aktivem Slimming konsequenter
- verbessert die Nutzer-Semantik in der Summary mit Fokus auf das Archiv unter `/share/*.tar.gz`
- klassifiziert Add-on-Stats pro Add-on als `supported`, `unsupported` oder `error`
- behandelt nicht unterstützte `/stats`-Endpunkte nicht länger wie globale Exportfehler
- stellt `startup` passend für den One-shot-Betrieb auf `once`

## 0.5.2

- erhält Helper-IDs in den relevanten Helper-Stores besser für exakte Zuordnung
- exportiert `.storage/auth` zusätzlich
- macht Security-Berichte ehrlicher, wenn Auth-/Netzwerk-Kontext unvollständig ist
- korrigiert das Unsicherheitsregister für vorhandene Logs und API-Logquellen
- dedupliziert ESPHome-Quellen im Export
- ergänzt optionales HACS-Asset-Slimming
- korrigiert Add-on-Stats-Zusammenfassungen in Reports
- entfernt das Schreiben nach `addon_configs`
- schreibt unter `/share` nur noch das TAR.GZ-Archiv
- räumt temporäre entpackte Exportverzeichnisse nach dem Packen wieder auf

## 0.5.1

- repariert die Helper-Extraktion aus den echten Helper-Stores
- verhindert falsche Helper-Treffer aus `.storage/backup`
- repariert die Template-Extraktion aus echten Template-Config-Entries in `core.config_entries`
- verhindert falsche Template-Treffer aus HACS-Repository-Daten
- stellt die Sanitization stärker auf feldbewusste Logik um
- erhält Add-on-Slugs, Versionen, Komponentenlisten und andere nicht sensible Strukturwerte besser
- macht Manifest, Summary und Report deutlich konsistenter
- korrigiert Security-/Exposure-Logik für Adapter-, Provider- und URL-Präsenz
- verhindert irreführende Einträge in `config_inventory` für fehlende Quellverzeichnisse

## 0.5.0

- ergänzt gezielten Add-on-Options-Export
- ergänzt Add-on-Stats-Export
- führt Integrationsprofile für ESPHome, MQTT, Broadlink und HACS ein
- führt ein maschinenlesbares Unsicherheitsregister ein
- erweitert die Inventar-Ebene um stärker refactoring-orientierte Analyseartefakte

## 0.4.0

- ergänzt einen Security-/Exposure-Report als JSON und Markdown
- führt den Import von `operator_intent`-Dateien ein
- unterstützt Operator-Intent aus Home-Assistant-Konfiguration, Add-on-Kontext und Share-Kontext
- normalisiert importierten Operator-Intent zusätzlich in strukturierte Metadaten

## 0.3.0

- ergänzt Recorder-Tiefenexporte
- ergänzt mehrere State-Snapshots über Zeit
- ergänzt Snapshot-Zusammenfassungen und Delta-Sicht
- ergänzt tieferen Backup-/Restore-Kontext
- ergänzt zusätzliche Runtime-Artefakte für spätere Analyseinstanzen

## 0.2.0

- erweitert den Export deutlich um Laufzeit-, Trace-, Security-, Backup- und Frontend-Kontext
- ergänzt breitere `.storage`-Abdeckung
- ergänzt `python_scripts`, `pyscript`, `appdaemon`, `esphome` und referenzierte Themes im Export
- ergänzt zusätzliche Core-/Supervisor-/Add-on-Logs
- führt `relationship_integrity_report.json` ein
- ergänzt `operator_intent_template.md`
- macht `include_raw_storage_files` funktional wirksam

## 0.1.6

- verbessert die Theme-Diagnostik deutlich
- unterscheidet sauber zwischen `missing`, `unreadable`, `empty` und `contains_non_yaml_only`
- liest das tatsächliche Theme-Include-Ziel aus `configuration.yaml`
- exportiert referenzierte Theme-Verzeichnisse robuster
- ergänzt detailliertere Theme-Metadaten in `config_inventory`

## 0.1.5

- ersetzt zu aggressive Registry-Redaction durch stabile, eindeutige Pseudonymisierung für Beziehungs-IDs
- erhält Device↔Entity-, Area- und Config-Entry-Beziehungen besser
- exportiert referenzierte `themes/`-Verzeichnisse
- ergänzt Theme-Metadaten im Konfigurationsinventar
- verbessert die Grundlage für device-zentrierte Analyse und Graph-Rekonstruktion

## 0.1.4

- ergänzt dedizierte Helper-Quelldefinitionen
- ergänzt dedizierte Template-Quelldefinitionen
- exportiert typische Helper-YAML-Dateien explizit
- ergänzt zusätzliche Erkennung von Helper- und Template-Quellen außerhalb der bisherigen Standarddateien

## 0.1.3

- Maintenance-/Zwischenversion in der frühen Ausbauphase
- diente als Arbeitsbasis für die Erweiterungen in 0.1.4
- die exakten Einzeländerungen dieser Version sind aus den verbliebenen Artefakten nicht vollständig rekonstruierbar

## 0.1.2

- verlagert den primären Export in den öffentlichen Add-on-Kontext statt ausschließlich auf `/share`
- ergänzt klarere Berichte darüber, wo Exporte zu finden sind
- ergänzt `last_export_report`-artige Diagnosehilfen für frühere Exportziel-Probleme
- verbessert das Verhalten bei Fällen, in denen `/share` nicht wie erwartet nutzbar war

## 0.1.1

- ergänzt `hassio_role: manager`
- behebt den fehlenden Zugriff auf restriktivere Supervisor-Endpunkte wie die Add-on-Liste
- verbessert dadurch den Export des Add-on-Inventars

## 0.1.0

- erste veröffentlichte Version des ChatGPT HA Exporters
- exportiert ein sanitisiertes Analysepaket aus Home Assistant
- grundlegender Export von Konfiguration, ausgewählten `.storage`-Daten, States, Services und Inventar
- legt die Basis für spätere Runtime-, Security-, Recorder- und Refactoring-Erweiterungen
