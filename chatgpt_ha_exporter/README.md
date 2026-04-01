# ChatGPT HA Exporter

[Add Binoalien Home Assistant Apps to Home Assistant](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fbinoalien%2Fhome-assistant-apps)

Der **ChatGPT HA Exporter** erstellt ein sanitisiertes, strukturtreues Analysepaket aus Home Assistant.

Version: **0.5.8**

## Zweck

Dieses Add-on ist ein **Analyse-Exporter für ChatGPT**.

Es erzeugt ein Paket, das:

- Struktur und Beziehungen vollständig erhält
- sensible Daten schützt
- Runtime-, Trace-, Recorder- und Security-Kontext enthält
- für Refactoring, Optimierung und Neuaufbau geeignet ist

## Installation

1. Repository hinzufügen (Link oben)
2. **Einstellungen → Apps**
3. **ChatGPT HA Exporter installieren**

## Nutzung

1. Optionen konfigurieren
2. Add-on starten
3. `.tar.gz` aus `/share` verwenden
4. Archiv an ChatGPT übergeben

## Exportinhalt

Der Export kann enthalten:

- sanitisierte Konfiguration
- `.storage`-Daten
- Dashboards, Blueprints, Custom Components
- optionale Verzeichnisse (python_scripts, pyscript, appdaemon, esphome, themes)
- Inventare und Reports
- Helper- und Template-Definitionen
- State-Snapshots (inkl. Verlauf)
- Recorder-Daten (Summary + Deep Export)
- Logs (Core, Supervisor, Add-ons)
- Security-/Exposure-Analyse
- Integrationsprofile (ESPHome, MQTT, Broadlink, HACS)
- Unsicherheitsregister

## Nicht-Ziel

Dieses Add-on:

- ist kein Backup
- ist kein Restore-Tool
- exportiert keine ungefilterten Rohdaten

## Ausgabe

- genau **ein `.tar.gz`**
- gespeichert unter `/share`
- kein temporärer Export bleibt bestehen

## Empfohlener ChatGPT-Workflow

### Variante A – Direkt

- Export → ChatGPT → Analyse

### Variante B – Zwei Instanzen (empfohlen)

Instanz 1:

- Analyse
- Strukturierung
- Problemidentifikation

Instanz 2:

- Refactoring
- Optimierung
- Architekturverbesserung

## Greenfield-Neuaufbau (Best Practice)

1. Export erstellen
2. Anforderungen extrahieren
3. Altlasten ignorieren
4. neue Struktur definieren
5. sauberes System aufbauen

## Wichtige Hinweise

### One-shot

- läuft einmal
- erzeugt Export
- beendet sich

### Start on boot

Falls aktiviert:

- im Home Assistant UI deaktivieren

### Themes-Warnung

Fehlende `themes` sind meist:

- **HA-Konfigurationsproblem**
- kein Exporter-Fehler

### Operator Intent

Empfohlen:

- `operator_intent.md` oder `.json`

Für:

- Zielarchitektur
- Regeln
- kritische Bereiche

## Struktur des Exports

- `source_sanitized/`
- `normalized/`
- `inventory/`
- `runtime/`
- `metadata/`

## Weitere Dokumentation

- `DOCS.md`
- `CHATGPT_WORKFLOWS.md`
- `CHANGELOG.md`
