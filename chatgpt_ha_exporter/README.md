# ChatGPT HA Exporter

[Add Binoalien Home Assistant Apps to Home Assistant](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fbinoalien%2Fhome-assistant-apps)

Der **ChatGPT HA Exporter** erstellt ein sanitisiertes Analysepaket aus Home Assistant.

Version: **0.1.1**

## Zweck

Dieses Add-on ist ein **Analyse-Exporter für ChatGPT**.

Es erzeugt ein Paket, das:
- zentrale Konfiguration erhält
- ausgewählte `.storage`-Dateien sanitisiert exportiert
- einen aktuellen State-Snapshot bereitstellen kann
- einen Service-Katalog bereitstellen kann
- einen Recorder-Überblick statt der vollständigen DB liefern kann
- ein Archiv für nachgelagerte ChatGPT-Analyse erzeugt

## Installation

1. Repository hinzufügen (Link oben)
2. **Einstellungen → Apps** öffnen
3. **ChatGPT HA Exporter** installieren

## Nutzung

1. Optionen konfigurieren
2. Add-on manuell starten
3. Exportverzeichnis oder `.tar.gz` aus `/share` verwenden
4. Archiv oder entpackte Dateien an ChatGPT übergeben

## Exportinhalt

Der Export kann enthalten:
- sanitierte YAML-Konfiguration
- ausgewählte `.storage`-Dateien
- Dashboard- und Blueprint-Dateien
- `custom_components`
- `python_scripts` und `pyscript`, falls vorhanden
- Add-on-, Core- und Supervisor-Inventar
- State-Snapshot
- Service-Katalog
- Log-Tail
- Recorder-Zusammenfassung
- normalisierte JSON/NDJSON-Dateien für die Weitergabe

## Nicht-Ziel

Dieses Add-on:
- ist kein Backup
- ist kein Restore-Tool
- exportiert keine ungefilterten Secrets
- exportiert standardmäßig keine vollständige Recorder-Datenbank

## Weitere Dokumentation

- `DOCS.md`
- `EXPORT_SCHEMA.md`
- `CHATGPT_WORKFLOWS.md`
- `CHANGELOG.md`
