# Binoalien Home Assistant Apps

[Add Binoalien Home Assistant Apps to Home Assistant](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fbinoalien%2Fhome-assistant-apps)

Dieses Repository enthält Home Assistant Apps von **binoalien**.

## Enthaltene App

### ChatGPT HA Exporter

Ordner:

`chatgpt_ha_exporter`

Der **ChatGPT HA Exporter** erstellt ein sanitisiertes, strukturtreues Analysepaket aus Home Assistant, damit eine andere ChatGPT-Instanz dein Setup analysieren, verbessern und refactoren kann.

## Installation

1. Klicke auf den Link oben
2. Repository zu Home Assistant hinzufügen
3. Öffne **Einstellungen → Apps**
4. Installiere **ChatGPT HA Exporter**

## Zweck

Dieses Repository stellt Apps bereit, die speziell für:

- Analyse mit ChatGPT
- strukturierte Refactorings
- Performance-Optimierung
- Sicherheitsbewertung
- Greenfield-Neuaufbau

entwickelt wurden.

## Empfohlener Workflow

### Bestehendes System optimieren

- Export erzeugen
- Archiv an ChatGPT übergeben
- Analyse und Refactoring durchführen

### Komplett neu aufbauen (empfohlen)

- Export erzeugen
- Anforderungen extrahieren
- neues System ohne Altlasten planen
- saubere Zielarchitektur umsetzen

## Dokumentation

Die vollständige Dokumentation der App liegt im App-Ordner:

- `chatgpt_ha_exporter/README.md` – Überblick und Nutzung
- `chatgpt_ha_exporter/DOCS.md` – technische Details
- `chatgpt_ha_exporter/EXPORT_SCHEMA.md` – formale Exportstruktur (Schema / API)
- `chatgpt_ha_exporter/CHATGPT_WORKFLOWS.md` – Workflows und Prompts
- `chatgpt_ha_exporter/CHANGELOG.md` – Versionshistorie

## Hinweis

Dieses Repository ist ein **Home Assistant App Repository**.

Der Exporter ist **kein Backup-Tool**, sondern ein **Analyse-Tool für ChatGPT**.
