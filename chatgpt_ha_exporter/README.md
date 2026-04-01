# ChatGPT HA Exporter

Der **ChatGPT HA Exporter** erstellt ein sanitisiertes, strukturtreues Analysepaket aus Home Assistant, damit eine andere ChatGPT-Instanz dein Setup belastbar analysieren, verbessern und refactoren kann.

Version: **0.5.8**

## Zweck

Dieses Add-on ist kein Backup-Ersatz und kein Restore-Werkzeug. Es ist ein **Analyse-Exporter**.

Ziel ist ein Paket, das:
- genug Struktur und Kontext für tiefgehende Analyse enthält,
- sensible Daten nicht unnötig offenlegt,
- Beziehungen zwischen Geräten, Entitäten, Areas, Config Entries und Automationen erhält,
- auch Runtime-, Trace-, Security-, Recorder- und Integrationskontext mitliefert.

## Was exportiert wird

Je nach Optionen enthält der Export unter anderem:
- sanitisierte Konfigurationsdateien aus dem Home-Assistant-Konfigurationsordner
- ausgewählte und normalisierte `.storage`-Daten
- Dashboards, Blueprints und `custom_components`
- optionale Verzeichnisse wie `python_scripts/`, `pyscript/`, `appdaemon/`, `esphome/`, `themes/`
- Core-, Supervisor- und Add-on-Inventare
- Helper- und Template-Quelldefinitionen
- State-Snapshots und mehrfache Snapshots über Zeit
- Recorder-Zusammenfassungen und Recorder-Tiefenexporte
- Core-, Supervisor- und Add-on-Logs
- Security-/Exposure-Berichte
- Integrationsprofile für kritische Bereiche wie ESPHome, MQTT, Broadlink und HACS
- ein maschinenlesbares Unsicherheitsregister

## Was bewusst nicht das Ziel ist

Dieses Add-on soll **kein vollständiges ungefiltertes Abbild** deines Systems erzeugen.

Es ist bewusst darauf ausgelegt,
- Secrets, Tokens, Hosts und ähnliche sensible Werte zu redigieren,
- Struktur zu erhalten statt rohe Interna blind zu kopieren,
- Analyse zu ermöglichen, ohne unnötig viele operative Details preiszugeben.

## Ausgabeort

Der Export wird als **ein einziges TAR.GZ-Archiv** unter `/share` abgelegt.

Es bleibt dort **kein entpacktes Exportverzeichnis** zurück.

## Nutzung in Kurzform

1. Add-on installieren.
2. Optionen prüfen und an deinen gewünschten Analyseumfang anpassen.
3. Add-on manuell starten.
4. Das erzeugte `.tar.gz` aus `/share` verwenden.
5. Dieses Archiv an eine andere ChatGPT-Instanz übergeben.

## Empfohlener Workflow mit ChatGPT

### Variante A – direkt analysieren lassen
- Export erzeugen
- Archiv hochladen
- ChatGPT die Analyse, Aufbereitung oder Refactoring-Vorbereitung machen lassen

### Variante B – zweistufig
1. Erste ChatGPT-Instanz bereitet den Export strukturiert auf.
2. Zweite ChatGPT-Instanz nutzt diese aufbereiteten Daten für konkrete Optimierungen und Refactorings.

Diese zweistufige Variante ist besonders sinnvoll, wenn du maximale Sorgfalt und Nachvollziehbarkeit willst.

## Wichtige Hinweise

### One-shot-Verhalten
Das Add-on ist als **One-shot-App** gedacht. Es läuft, erzeugt ein Archiv und beendet sich wieder.

Wenn in einer älteren Installation der Supervisor-Schalter **Start on boot** bereits aktiviert wurde, musst du ihn im Home-Assistant-UI selbst deaktivieren. Das Paket selbst kann diesen benutzerseitigen Laufzeit-Schalter nicht zuverlässig rückwirkend zurücksetzen.

### Themes-Warnung
Wenn `configuration.yaml` `frontend: themes: !include_dir_merge_named ...` enthält, aber das referenzierte Verzeichnis im echten HA-Config-Ordner fehlt, meldet der Exporter das als Warnung.

Das ist dann meist **ein Befund deines HA-Setups**, nicht automatisch ein Exporter-Fehler.

### Operator Intent
Wenn du willst, dass eine nachgelagerte Instanz weniger raten muss, lege zusätzlich eine Datei wie `operator_intent.md` oder `operator_intent.json` an.

Darin kannst du z. B. festhalten:
- gewünschte Zielarchitektur
- kritische Automationen
- bewusst beibehaltene Altlasten
- Bereiche, die nie automatisch verändert werden sollen

## Exportstruktur auf hoher Ebene

Das Archiv enthält typischerweise diese Hauptbereiche:
- `source_sanitized/` – sanitisierte Quelldateien
- `normalized/` – normalisierte JSON-Sichten
- `inventory/` – strukturierte Berichte und Inventare
- `runtime/` – Snapshots, Logs, Recorder-Auszüge
- `metadata/` – Manifest, Report, Checksums und Zusammenfassungen

## Für wen dieses Add-on gedacht ist

Der Exporter ist sinnvoll, wenn du:
- Home Assistant mit ChatGPT analysieren willst,
- eine sichere, strukturierte Übergabe an eine andere Instanz brauchst,
- Refactorings, Performance-Analysen oder Sicherheitsbewertungen vorbereiten willst,
- nicht einfach nur ein Backup, sondern ein **analysefähiges Paket** willst.


## ChatGPT-Workflows und Prompts

Eine ausführliche Anleitung für den praktischen Einsatz mit ChatGPT findest du in **`CHATGPT_WORKFLOWS.md`**.
Dort enthalten sind:
- empfohlene Zwei-Instanzen-Workflows
- copy-paste-fertige Prompts
- ein separater Greenfield-Workflow für den kompletten Neuaufbau ohne Altlasten
- Hinweise zur Übergabe zwischen den Instanzen

## Weiterführende Doku

Die ausführliche technische Dokumentation findest du in **`DOCS.md`**.
Dort stehen unter anderem:
- Exportphasen
- Sanitization-Strategie
- detaillierte Optionsbeschreibung
- Berichte und Ausgabedateien
- Troubleshooting
- Grenzen des Ansatzes
