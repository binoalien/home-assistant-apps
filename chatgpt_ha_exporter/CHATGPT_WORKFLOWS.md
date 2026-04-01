# ChatGPT HA Exporter – Empfohlene Workflows mit ChatGPT

Diese Datei beschreibt die **operative Nutzung** des aktuellen ChatGPT HA Exporters mit ChatGPT.

Rollen der Doku:
- `README.md` → Einstieg und Installation
- `DOCS.md` → technische Erklärung des Exporters
- `EXPORT_SCHEMA.md` → formale Exportstruktur
- `CHATGPT_WORKFLOWS.md` → praktische Nutzung, Übergabe und Prompts

Grundregel:
> Nutze nicht dieselbe ChatGPT-Instanz für Rohdatenanalyse und konkrete Umsetzungsplanung.  
> Für bessere Qualität ist ein **zweistufiger Workflow mit zwei Instanzen** die empfohlene Standardvorgehensweise.

---

## 1. Workflow-Auswahl

### 1.1 Workflow A – Bestehendes System analysieren und verbessern

Nutzen, wenn du:
- dein aktuelles Setup grundsätzlich behalten willst
- Altlasten abbauen willst
- bessere Struktur, Klarheit und Wartbarkeit willst
- Refactorings kontrolliert planen willst

**Rollen:**
- **Instanz 1:** Analyse, Inventarisierung, Risiken und Unsicherheiten
- **Instanz 2:** Optimierung, Refactoring, Umsetzungsplanung

### 1.2 Workflow B – Neuaufbau ohne Altlasten

Nutzen, wenn du:
- das bestehende Setup nicht direkt weiterführen willst
- nur Anforderungen und Funktionen übernehmen willst
- eine neue Zielstruktur bewusst von Grund auf definieren willst

**Rollen:**
- **Instanz 1:** Requirements und Muss-Funktionen extrahieren
- **Instanz 2:** Greenfield-Zielsystem entwerfen

---

## 2. Grundregeln

### 2.1 Immer mit aktuellem Export arbeiten

Wenn möglich, aktiviere für die Analyse mindestens:
- State-Snapshot
- Services
- Logs
- Recorder Summary
- `.storage`-Export

### 2.2 Rohdaten nicht direkt refactoren lassen

Zuerst:
- strukturieren
- prüfen
- priorisieren
- Unsicherheiten markieren

Erst danach Änderungen planen.

### 2.3 Fakten, Schlussfolgerungen und Unsicherheiten trennen

Immer sauber unterscheiden zwischen:
- **Fakten**
- **Schlussfolgerungen**
- **Unsicherheiten**

### 2.4 Operator Intent separat ergänzen

Wenn du wichtige Zielentscheidungen schon kennst, gib zusätzlich mit:
- `operator_intent.md`
- `operator_intent.json`

---

## 3. Workflow A – Bestehendes Home Assistant verbessern

### 3.1 Ablauf

1. Export erzeugen
2. Export an Instanz 1 geben
3. Handoff prüfen
4. Handoff an Instanz 2 geben
5. Maßnahmen priorisieren lassen
6. selektiv umsetzen
7. neuen Export erzeugen

### 3.2 Instanz 1 – Analyse und Aufbereitung

**Ziel:** aus dem Export ein belastbares Übergabepaket erzeugen.

**Soll liefern:**
- `executive_summary.md`
- `current_architecture.md`
- `integrations_inventory.json`
- `devices_inventory.json`
- `entities_inventory.json`
- `automations_inventory.json`
- `dashboards_inventory.json`
- `technical_debt_register.json`
- `quick_wins.json`
- `handoff_for_optimizer.md`

### 3.3 Prompt für Instanz 1

```text
Du bist eine spezialisierte Home-Assistant-Analyse- und Aufbereitungsinstanz.

Ich gebe dir ein vom ChatGPT HA Exporter erzeugtes Export-Archiv. Deine Aufgabe ist NICHT, sofort Änderungen oder Refactorings vorzunehmen. Deine Aufgabe ist es, die Daten maximal sauber, konsistent, präzise und für eine zweite ChatGPT-Instanz optimal nutzbar aufzubereiten.

Arbeitsregeln:
- Arbeite evidenzbasiert.
- Trenne klar zwischen Fakten, Schlussfolgerungen und Unsicherheiten.
- Erfinde nichts.
- Markiere Datenlücken explizit.

Pflichtaufgaben:
- Exportarchiv vollständig erfassen
- Dateistruktur und Exportumfang dokumentieren
- Integrationen, Geräte, Entitäten, Config Entries, Automationen, Dashboards, Services und Runtime-Hinweise inventarisieren
- Inkonsistenzen, Duplikate, tote Konfiguration, Naming-Probleme, Sicherheits-, Performance- und Wartbarkeitsrisiken benennen
- ein Handoff-Paket für eine zweite Instanz erzeugen

Erzeuge mindestens:
- executive_summary.md
- current_architecture.md
- integrations_inventory.json
- devices_inventory.json
- entities_inventory.json
- automations_inventory.json
- dashboards_inventory.json
- technical_debt_register.json
- quick_wins.json
- handoff_for_optimizer.md
```

### 3.4 Instanz 2 – Optimierung und Refactoring

**Ziel:** das bestehende System auf Basis des Handoffs verbessern.

**Soll liefern:**
- priorisierte Verbesserungsstrategie
- sichere Quick Wins
- Naming- und Strukturstandard
- Refactoring-Plan für Automationen, Dashboards und Integrationen

### 3.5 Prompt für Instanz 2

```text
Du bist eine Home-Assistant-Optimierungs- und Refactoring-Instanz.

Ich gebe dir ein bereits aufbereitetes Analyse- und Übergabepaket zu meinem bestehenden Home-Assistant-System. Nutze dieses Paket als primäre Arbeitsgrundlage.

Ziel:
Mein bestehendes Home Assistant evidenzbasiert verbessern, vereinfachen und strukturell refactoren – aber kontrolliert, nachvollziehbar und priorisiert.

Arbeitsregeln:
- Nutze das Handoff-Paket als Hauptquelle.
- Verändere nichts stillschweigend.
- Trenne klar zwischen sicheren Änderungen, riskanten Änderungen und Änderungen, die Betreiberentscheidung erfordern.
- Gib keine generischen Ratschläge, sondern systembezogene Maßnahmen.

Liefere mindestens:
- master_improvement_plan.md
- safe_first_changes.md
- risky_changes_needing_confirmation.md
- naming_standard.md
- automation_refactor.md
- dashboard_refactor.md
- implementation_backlog.json
```

---

## 4. Workflow B – Neuaufbau ohne Altlasten

### 4.1 Ablauf

1. Export erzeugen
2. Export an Instanz 1 geben
3. Anforderungen extrahieren lassen
4. Ergebnis prüfen
5. Ergebnis an Instanz 2 geben
6. neues Zielsystem entwerfen lassen

### 4.2 Instanz 1 – Requirements und Zielprinzipien

**Soll liefern:**
- `system_requirements.md`
- `critical_behaviors.md`
- `legacy_to_drop.md`
- `target_principles.md`
- `greenfield_handoff.md`

### 4.3 Prompt für Instanz 1

```text
Du bist eine Requirements-Instanz für Home Assistant.

Ich gebe dir ein Export-Archiv meines aktuellen Home-Assistant-Systems. Deine Aufgabe ist NICHT, das bestehende Setup zu verbessern. Deine Aufgabe ist es, aus dem Altbestand Anforderungen, kritische Funktionen, Muss-Verhalten und Zielprinzipien zu extrahieren.

Arbeitsregeln:
- Nutze den Altbestand als Quellmaterial, nicht als Strukturvorlage.
- Trenne strikt zwischen fachlich benötigt, historisch gewachsen und unklar.
- Erfinde nichts.
- Markiere Unsicherheiten explizit.

Erzeuge mindestens:
- system_requirements.md
- critical_behaviors.md
- legacy_to_drop.md
- target_principles.md
- greenfield_handoff.md
```

### 4.4 Instanz 2 – Greenfield-Aufbau

**Soll liefern:**
- Zielarchitektur
- Namensstandard
- Strukturprinzipien
- Migrationsreihenfolge

### 4.5 Prompt für Instanz 2

```text
Du bist eine Greenfield-Architektur-Instanz für Home Assistant.

Ich gebe dir ein bereits aufbereitetes Requirements- und Handoff-Paket, das aus meinem bestehenden Home-Assistant-System extrahiert wurde.

Ziel:
Ein neues, sauberes Home-Assistant-Zielsystem entwerfen, das fachlich alles Relevante übernimmt, aber strukturell keine Altlasten mitschleppt.

Arbeitsregeln:
- Nutze das Handoff als Quellbasis für Anforderungen, nicht als Vorlage für Dateistruktur.
- Erfinde nichts.
- Übernimm Altlogik nur dann, wenn sie fachlich nötig ist.
- Mache Annahmen explizit.

Liefere mindestens:
- target_architecture.md
- naming_standard.md
- directory_structure.md
- migration_sequence.md
- greenfield_build_plan.md
```

---

## 5. Übergabe zwischen den Instanzen

Immer enthalten sollte:
- Ziel des nächsten Schritts
- wichtigste Fakten
- größte Unsicherheiten
- offene Betreiberentscheidungen
- empfohlene Reihenfolge
- Primärquellen für die nächste Instanz
