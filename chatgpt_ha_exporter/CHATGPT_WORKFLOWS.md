# ChatGPT HA Exporter – Empfohlene Workflows mit ChatGPT

Diese Datei beschreibt die **empfohlene operative Nutzung** des ChatGPT HA Exporters mit ChatGPT.

Sie ergänzt die übrige Dokumentation wie folgt:

- `README.md` → Einstieg und Installation
- `DOCS.md` → technische Erklärung des Exporters
- `EXPORT_SCHEMA.md` → Strukturvertrag des Exportarchivs
- `CHATGPT_WORKFLOWS.md` → **praktische Nutzung, Rollenmodell, Übergabe und Prompts**

Die Grundregel dieses Projekts lautet:

> Nutze **nicht dieselbe ChatGPT-Instanz** für Rohdatenanalyse, Zielbild-Definition und konkrete Umsetzungsplanung.
>
> Für hohe Qualität ist ein **zweistufiger Workflow mit zwei Instanzen** die empfohlene Standardvorgehensweise.

---

## 1. Wann welchen Workflow verwenden?

## 1.1 Workflow A – Bestehendes Home Assistant verbessern

Nutze diesen Workflow, wenn du:

- dein aktuelles Setup grundsätzlich behalten willst
- Altlasten gezielt abbauen willst
- Performance-, Sicherheits- und Wartbarkeitsprobleme lösen willst
- Refactorings, Bereinigung und Standardisierung auf Basis des Ist-Systems willst
- das bestehende Verhalten möglichst kontrolliert erhalten möchtest

**Ziel:**
Das bestehende Home Assistant systematisch verbessern, ohne unnötig funktionierende Logik zu zerstören.

**Empfohlene Rollen:**

- **Instanz 1:** Analyse, Aufbereitung, Inventarisierung, Unsicherheits- und Risikoerkennung
- **Instanz 2:** konkrete Optimierung, Refactoring, Zielstruktur und Umsetzungsplanung

---

## 1.2 Workflow B – Home Assistant komplett neu aufbauen

Nutze diesen Workflow, wenn du:

- dein aktuelles Setup **nicht direkt weiterentwickeln**, sondern **sauber neu aufbauen** willst
- historisch gewachsene Struktur, Workarounds und Inkonsistenzen **nicht übernehmen** willst
- das bestehende System nur noch als **Anforderungsquelle**, nicht als Strukturvorlage verwenden willst
- eine klare Zielarchitektur, Namenskonventionen und Domänengrenzen von Grund auf definieren willst

**Ziel:**
Ein neues Home-Assistant-Zielsystem aufbauen, das fachlich alles Relevante übernimmt, aber strukturell **keine Altlasten mitschleppt**.

**Empfohlene Rollen:**

- **Instanz 1:** extrahiert Anforderungen, Regeln, Geräteklassen, Betriebsabsicht und Muss-Funktionen
- **Instanz 2:** entwirft daraus das neue Zielsystem, ohne die Altsystem-Struktur ungeprüft zu spiegeln

---

## 2. Grundregeln für gute Ergebnisse

Diese Regeln gelten unabhängig vom gewählten Workflow.

### 2.1 Export zuerst

Arbeite immer mit einem **aktuellen Export** aus dem ChatGPT HA Exporter.

Für hochwertige Ergebnisse sind in der Regel sinnvoll:

- Storage-Kontext
- Runtime-Kontext
- Logs
- Recorder-Zusammenfassungen oder Recorder-Deep-Export
- Security-/Exposure-Report
- Integrationsprofile
- Uncertainty Register

### 2.2 Rohdaten nicht sofort refactoren lassen

Rohdaten sollten zuerst:

- inventarisiert
- normalisiert
- geprüft
- priorisiert
- mit Unsicherheiten markiert

werden.

Erst danach sollte eine zweite Instanz konkrete Änderungen planen.

### 2.3 Fakten, Schlussfolgerungen und Unsicherheiten trennen

Home-Assistant-Probleme entstehen oft nicht durch eine einzelne Datei, sondern durch:

- Zusammenspiel mehrerer Integrationen
- Laufzeitverhalten
- implizite Betreiberentscheidungen
- Altlasten
- Timing- oder Recorder-Effekte

Deshalb müssen immer getrennt werden:

- **Fakten**
- **abgeleitete Schlussfolgerungen**
- **verbleibende Unsicherheiten**

### 2.4 Operator Intent aktiv ergänzen

Wenn möglich, gib zusätzlich eine Datei wie `operator_intent.md` oder `operator_intent.json` mit.

Sie reduziert Restunsicherheit erheblich, insbesondere bei:

- Zielarchitektur
- gewollten Altlasten
- kritischen Automationen
- Naming-Regeln
- Bereichen, die nie automatisch geändert werden dürfen

### 2.5 Menschliche Freigabe zwischen den Stufen

Zwischen Instanz 1 und Instanz 2 sollte immer eine kurze menschliche Prüfung stattfinden:

- Ist die Analyse konsistent?
- Fehlen wichtige Bereiche?
- Wurde die Betriebsabsicht korrekt verstanden?
- Soll der Fokus eher auf Verbesserung oder auf Neuaufbau liegen?

---

## 3. Workflow A – Bestehendes Home Assistant verbessern

## 3.1 Zielbild

Dieser Workflow soll dein aktuelles Home Assistant:

- strukturieren
- vereinfachen
- absichern
- wartbarer machen
- performanter machen
- logisch entflechten
- kontrolliert refactoren

ohne unnötig bestehendes Verhalten zu zerstören.

---

## 3.2 Rollenmodell

### Instanz 1 – Analyse- und Aufbereitungsinstanz

**Aufgabe:**
Aus dem Export ein **belastbares Übergabepaket** für die Optimierungsinstanz machen.

**Diese Instanz macht:**

- Entpacken und Inventarisieren
- Struktur- und Kontextaufbereitung
- Konsistenzprüfung
- Risikoanalyse
- Problemklassifikation
- Refactoring-Vorbereitung
- Handoff-Paket für Instanz 2

**Diese Instanz macht nicht:**

- keine endgültigen Refactorings
- keine spekulativen Umbauten
- keine stillen Architekturentscheidungen
- keine unmarkierten Annahmen

### Instanz 2 – Optimierungs- und Refactoring-Instanz

**Aufgabe:**
Das bestehende System **auf Basis des Handoffs** strukturiert verbessern.

**Diese Instanz macht:**

- konkrete Verbesserungsvorschläge
- priorisierte Refactoring-Schritte
- Naming- und Strukturstandardisierung
- Dashboard-/Automation-/Template-/Helper-Bereinigung
- Integrations- und Legacy-Bereinigung
- Security- und Performance-Härtung
- konkrete YAML-/JSON-/Diff-Vorschläge, wenn sinnvoll

**Diese Instanz macht nicht:**

- keine komplett neue Greenfield-Architektur ohne Auftrag
- keine impliziten Betriebsentscheidungen
- keine stillschweigende Entfernung potenziell kritischer Logik

---

## 3.3 Empfohlener Ablauf

1. aktuellen Export erzeugen
2. Export an Instanz 1 geben
3. strukturiertes Handoff prüfen
4. Handoff an Instanz 2 geben
5. Änderungen priorisieren lassen
6. selektiv umsetzen
7. neuen Export erzeugen
8. optional Gegenprüfung mit Instanz 1 oder Instanz 2

---

## 3.4 Erwartete Ausgabe von Instanz 1

Instanz 1 sollte mindestens folgende Artefakte liefern:

- `executive_summary.md`
- `current_architecture.md`
- `integrations_inventory.json`
- `devices_inventory.json`
- `entities_inventory.json`
- `automations_inventory.json`
- `dashboards_inventory.json`
- `custom_components_inventory.json`
- `relationship_overview.json`
- `security_risks.md`
- `performance_risks.md`
- `maintainability_issues.md`
- `technical_debt_register.json`
- `quick_wins.json`
- `high_impact_changes.json`
- `risky_changes_requiring_care.json`
- `optimizer_task_list.json`
- `optimizer_constraints.json`
- `handoff_for_optimizer.md`

**Wichtigstes Artefakt:**

- `handoff_for_optimizer.md`

---

## 3.5 Prompt für Instanz 1 – Analyse und Aufbereitung

```text
Du bist eine spezialisierte Home-Assistant-Analyse- und Aufbereitungsinstanz.

Ich gebe dir ein vom ChatGPT HA Exporter erzeugtes Export-Archiv. Deine Aufgabe ist NICHT, sofort Änderungen oder Refactorings vorzunehmen. Deine Aufgabe ist es, die Daten maximal sauber, konsistent, präzise und für eine zweite ChatGPT-Instanz optimal nutzbar aufzubereiten.

Arbeitsprinzip:
- Arbeite streng evidenzbasiert.
- Trenne klar zwischen Fakten, Schlussfolgerungen und Unsicherheiten.
- Erfinde nichts.
- Markiere Datenlücken explizit.
- Verändere keine Semantik.

Pflichtaufgaben:
- Exportarchiv vollständig erfassen
- Dateistruktur und Exportumfang dokumentieren
- Integrationen, Add-ons, Geräte, Entitäten, Areas, Config Entries, Automationen, Skripte, Szenen, Templates, Helper, Dashboards, Blueprints, Custom Components, Services und Runtime-Hinweise inventarisieren
- Inkonsistenzen, Duplikate, tote Konfiguration, Legacy-Reste, Naming-Probleme, Sicherheits-, Performance- und Wartbarkeitsrisiken benennen
- Relationships zwischen Dateien, Entitäten, Geräten, Areas, Config Entries und Automationen erhalten
- ein maximales Handoff-Paket für eine zweite Instanz erzeugen

Erzeuge mindestens:
- executive_summary.md
- current_architecture.md
- integrations_inventory.json
- devices_inventory.json
- entities_inventory.json
- automations_inventory.json
- dashboards_inventory.json
- custom_components_inventory.json
- relationship_overview.json
- security_risks.md
- performance_risks.md
- maintainability_issues.md
- technical_debt_register.json
- quick_wins.json
- high_impact_changes.json
- risky_changes_requiring_care.json
- optimizer_task_list.json
- optimizer_constraints.json
- handoff_for_optimizer.md

Wichtig:
- keine Refactorings durchführen
- keine stillen Architekturentscheidungen
- keine Halluzinationen
- Unsicherheit explizit markieren
- Ausgabe so strukturieren, dass eine zweite ChatGPT-Instanz ohne Rückfragen direkt weiterarbeiten kann

Die wichtigste Ausgabedatei ist:
- handoff_for_optimizer.md
```

---

## 3.6 Prompt für Instanz 2 – Verbesserung und Refactoring des bestehenden Systems

```text
Du bist eine Home-Assistant-Optimierungs- und Refactoring-Instanz.

Ich gebe dir ein bereits aufbereitetes Analyse- und Übergabepaket zu meinem bestehenden Home-Assistant-System. Nutze dieses Paket als primäre Arbeitsgrundlage.

Dein Ziel:
Mein bestehendes Home Assistant evidenzbasiert verbessern, optimieren, vereinfachen, absichern, erweitern und strukturell refactoren – aber kontrolliert, nachvollziehbar und priorisiert.

Arbeitsregeln:
- Nutze das Handoff-Paket und die strukturierten Inventare als Hauptquelle.
- Verändere nichts stillschweigend.
- Trenne klar zwischen:
  - sichere Änderungen
  - Änderungen mit Abhängigkeiten
  - riskante Änderungen
  - Änderungen, die Betreiberentscheidung erfordern
- Gib keine generischen Ratschläge, sondern systembezogene Maßnahmen.
- Respektiere bestehendes Verhalten, sofern nicht klar belegt ist, dass es fehlerhaft, redundant oder veraltet ist.

Pflichtaufgaben:
- priorisierte Verbesserungsstrategie erstellen
- sichere Quick Wins identifizieren
- Naming- und Strukturstandard vorschlagen
- Helper-/Template-/Automation-/Script-Refactoring planen
- Dashboard-/Frontend-Verbesserungen planen
- Security-/Exposure-Verbesserungen planen
- Performance-Optimierungen planen
- Integrationsbereinigung und Legacy-Abbau planen
- konkrete Zieländerungen formulieren

Liefere mindestens:
- master_improvement_plan.md
- phased_refactor_plan.md
- safe_first_changes.md
- risky_changes_needing_confirmation.md
- naming_standard.md
- helper_template_refactor.md
- automation_refactor.md
- dashboard_refactor.md
- integration_cleanup_plan.md
- security_hardening_plan.md
- performance_optimization_plan.md
- implementation_backlog.json

Zusätzlich:
- Für jede empfohlene Änderung: Grund, Nutzen, Risiko, Abhängigkeiten, Reihenfolge
- Wenn sinnvoll: konkrete YAML-/JSON-/Datei-Vorschläge oder Diffs

Wichtig:
- keine Halluzinationen
- keine unmarkierten Annahmen
- keine implizite Neuarchitektur ohne Begründung
```

---

## 4. Workflow B – Home Assistant komplett neu aufbauen

## 4.1 Zielbild

Dieser Workflow ist für den Fall gedacht, dass du **nicht** das bestehende Setup bereinigen, sondern ein **neues Zielsystem** entwerfen willst.

Dabei ist das aktuelle Home Assistant nur noch:

- Verhaltensquelle
- Gerätequelle
- Integrationsquelle
- Anforderungenquelle
- Prioritätenquelle
- Risikoquelle

Es ist **nicht** mehr die Strukturvorlage.

Die zentrale Regel lautet:

> Der Greenfield-Workflow soll das bestehende Setup **nicht spiegeln**, sondern aus dem Ist-System nur extrahieren:
>
> - was das System können muss
> - welche Geräte und Domänen es gibt
> - welche Automationen fachlich gebraucht werden
> - welche Betriebsregeln wichtig sind
> - welche Altlasten nicht übernommen werden sollen

---

## 4.2 Rollenmodell

### Instanz 1 – Requirements- und Blueprint-Instanz

**Aufgabe:**
Aus dem Export die **fachlichen Anforderungen** herauslösen und vom Altbestand trennen.

**Diese Instanz macht:**

- Geräte- und Domäneninventar
- Extraktion funktionaler Anforderungen
- Identifikation kritischer Betriebsregeln
- Trennung von Muss-Logik und Altlast
- Definition von Zielprinzipien
- Definition von Naming-, Struktur- und Architekturregeln
- Übergabepaket für den Neuaufbau

**Diese Instanz macht nicht:**

- keinen direkten Umbau des Altbestands
- keine automatische Übernahme historischer Struktur
- keine stillschweigende Wiederverwendung alter Workarounds

### Instanz 2 – Greenfield-Architektur- und Build-Instanz

**Aufgabe:**
Aus Requirements und Zielprinzipien ein **sauberes neues Home-Assistant-Zielsystem** entwerfen.

**Diese Instanz macht:**

- Zielarchitektur
- Namensstandard
- Domänenschnitt
- Helper-Strategie
- Template-Strategie
- Automationsstruktur
- Dashboard-Konzept
- Migrationsreihenfolge aus dem Altbestand

**Diese Instanz macht nicht:**

- keine blinde Übernahme alter Dateistrukturen
- keine direkte Spiegelung historischer Automationen
- keine automatische Übernahme unklarer Integrationen ohne Begründung

---

## 4.3 Empfohlener Ablauf

1. aktuellen Export erzeugen
2. Export an Instanz 1 geben
3. fachliche Zielanforderungen und Zielprinzipien extrahieren lassen
4. Ergebnis menschlich prüfen
5. Ergebnis an Instanz 2 geben
6. Greenfield-Zielsystem entwerfen lassen
7. Migrationsreihenfolge definieren
8. neue Struktur schrittweise umsetzen

---

## 4.4 Erwartete Ausgabe von Instanz 1

Instanz 1 sollte mindestens liefern:

- `system_requirements.md`
- `device_capability_inventory.json`
- `domain_logic_inventory.json`
- `critical_behaviors.md`
- `legacy_to_drop.md`
- `constraints_and_rules.md`
- `target_principles.md`
- `naming_principles.md`
- `must_keep_features.json`
- `greenfield_handoff.md`

**Wichtigstes Artefakt:**

- `greenfield_handoff.md`

---

## 4.5 Prompt für Instanz 1 – Requirements-Extraktion und Blueprint

```text
Du bist eine Requirements- und Blueprint-Instanz für Home Assistant.

Ich gebe dir ein Export-Archiv meines aktuellen Home-Assistant-Systems. Deine Aufgabe ist NICHT, das bestehende Setup zu verbessern oder zu refactoren. Deine Aufgabe ist es, aus dem Altbestand die fachlichen Anforderungen, kritischen Betriebsregeln, Muss-Funktionen, Geräteklassen, Domänenlogik und Zielprinzipien zu extrahieren.

Ziel:
Erzeuge ein belastbares Requirements- und Handoff-Paket für eine zweite ChatGPT-Instanz, die mein Home Assistant von Grund auf neu und ohne Altlasten entwerfen soll.

Arbeitsregeln:
- Nutze den Altbestand als Quellmaterial, nicht als Strukturvorlage.
- Trenne strikt zwischen:
  - was fachlich benötigt wird
  - was historisch gewachsen ist
  - was vermutlich Altlast ist
  - was unklar bleibt
- Erfinde nichts.
- Markiere Unsicherheiten und fehlende Betreiber-Entscheidungen explizit.

Pflichtaufgaben:
- Geräte, Integrationen und Domänenlogik inventarisieren
- kritische Funktionen identifizieren
- betriebsrelevante Regeln und Nicht-Ausfall-Funktionen ableiten
- Naming- und Strukturprobleme des Altbestands benennen
- klar markieren, welche Altlasten nicht automatisch übernommen werden sollten
- Zielprinzipien für ein Greenfield-System formulieren
- ein Handoff für die Greenfield-Aufbauinstanz erzeugen

Erzeuge mindestens:
- system_requirements.md
- device_capability_inventory.json
- domain_logic_inventory.json
- critical_behaviors.md
- legacy_to_drop.md
- constraints_and_rules.md
- target_principles.md
- naming_principles.md
- must_keep_features.json
- greenfield_handoff.md

Wichtig:
- kein Refactoring des Altbestands
- keine blinde Übernahme der alten Struktur
- keine Halluzinationen
- Unsicherheit explizit markieren
```

---

## 4.6 Prompt für Instanz 2 – Greenfield-Neuaufbau von Grund auf

```text
Du bist eine Greenfield-Architektur- und Build-Instanz für Home Assistant.

Ich gebe dir ein bereits aufbereitetes Requirements- und Handoff-Paket, das aus meinem bestehenden Home-Assistant-System extrahiert wurde. Nutze dieses Paket als primäre Grundlage.

Dein Ziel:
Entwirf ein neues, sauberes Home-Assistant-Zielsystem von Grund auf – ohne Altlasten, ohne blind übernommene historische Struktur und mit klaren Architektur-, Naming- und Wartbarkeitsprinzipien.

Arbeitsregeln:
- Nutze den Altbestand nur indirekt über das Handoff.
- Übernimm nichts unkritisch nur deshalb, weil es im alten System existierte.
- Trenne klar zwischen:
  - Muss-Funktionen
  - optionale Verbesserungen
  - spätere Erweiterungen
  - Betreiberentscheidungen
- Plane so, dass das neue System logisch, modular, verständlich und wartbar ist.

Pflichtaufgaben:
- Zielarchitektur definieren
- Namensschema definieren
- Domänengruppen und Verantwortlichkeiten definieren
- Helper-/Template-/Automation-Strategie definieren
- Dashboard-Strategie definieren
- Integrationsstrategie definieren
- Migration aus dem Altbestand planen
- eine priorisierte Umsetzungsreihenfolge liefern

Liefere mindestens:
- target_architecture.md
- naming_standard.md
- directory_structure.md
- helper_strategy.md
- template_strategy.md
- automation_architecture.md
- dashboard_architecture.md
- integration_strategy.md
- migration_plan.md
- phased_build_plan.md
- implementation_backlog.json

Zusätzlich:
- Begründe jede strukturelle Entscheidung
- Kennzeichne riskante oder betreiberabhängige Entscheidungen
- Liefere, wenn sinnvoll, konkrete Datei- und YAML-Vorschläge

Wichtig:
- keine Spiegelung des Altbestands ohne Begründung
- keine Halluzinationen
- keine stillen Annahmen
```

---

## 5. Empfohlene Zusatzdatei – `operator_intent.md`

Wenn du willst, dass beide Instanzen weniger raten müssen, gib zusätzlich eine Datei wie `operator_intent.md` oder `operator_intent.json` mit.

Empfohlene Inhalte:

### Zielbild

- Was soll das System langfristig sein?
- Eher pragmatisch erweitert oder eher grundlegend neu strukturiert?

### Kritische Funktionen

- Welche Automationen oder Geräte dürfen auf keinen Fall ausfallen?
- Welche Bereiche sind geschäfts- oder alltagskritisch?

### Nicht automatisch ändern

- Welche Teile dürfen nie ohne Rückfrage verändert werden?
- Gibt es Systeme mit Sicherheits-, Komfort- oder Familienrelevanz?

### Darf neu aufgebaut werden

- Welche Altlasten dürfen entfernt, ersetzt oder neu modelliert werden?

### Naming und Sprache

- Deutsch, Englisch oder Hybrid?
- Welche Namensprinzipien sind gewünscht?

### Betriebsregeln

- Was hat Vorrang: Stabilität, Klarheit, Performance, Datenschutz, Erweiterbarkeit?

---

## 6. Welche Artefakte an welche Instanz geben?

## 6.1 Für Instanz 1

Immer sinnvoll:

- Exportarchiv
- optional `operator_intent.md` / `operator_intent.json`
- ggf. zusätzliche manuelle Hinweise des Betreibers

## 6.2 Für Instanz 2 im Verbesserungsworkflow

Nicht erneut den Roh-Export priorisieren, sondern zuerst:

- `handoff_for_optimizer.md`
- Inventare
- Risiko- und Debt-Dateien
- priorisierte Task-Listen
- Betreiberhinweise

Roh-Export nur ergänzend nutzen.

## 6.3 Für Instanz 2 im Greenfield-Workflow

Nicht den Altbestand als Hauptgrundlage verwenden, sondern:

- `greenfield_handoff.md`
- Requirements-Dateien
- Zielprinzipien
- Constraints
- `operator_intent.md` / `operator_intent.json`

Der Roh-Export dient nur als Rückversicherung.

---

## 7. Qualitätsprüfung nach jeder Stufe

Nach Instanz 1 prüfen:

- Wurden Fakten und Unsicherheiten sauber getrennt?
- Fehlen kritische Integrationen oder Geräte?
- Ist der Ist-Zustand korrekt verstanden?
- Ist das Handoff ohne Rückfragen nutzbar?

Nach Instanz 2 prüfen:

- Sind Änderungen priorisiert?
- Sind Risiken markiert?
- Sind Betreiberentscheidungen klar getrennt?
- Ist die Zielstruktur nachvollziehbar?
- Wird Altlast nicht unkritisch mitgeschleppt?

---

## 8. Häufige Fehler, die du vermeiden solltest

### Beim Verbesserungsworkflow

- dieselbe Instanz analysiert und refactort alles selbst
- Rohdaten werden sofort umgebaut
- Runtime- und Unsicherheitskontext wird ignoriert
- unklare Altlasten werden als Bugs fehlgedeutet
- Security-/Performance-Themen werden aus reiner YAML-Sicht beurteilt

### Beim Greenfield-Workflow

- das neue System spiegelt nur die alte Struktur in „schöner“
- Workarounds werden übernommen, ohne ihre Ursache zu prüfen
- Naming-Chaos wird mitmigriert
- unkritische Integrationen werden nur aus Gewohnheit übernommen
- Altlogik wird nicht in Muss-Funktion vs Altlast getrennt

---

## 9. Minimalempfehlung, wenn du wenig Aufwand willst

### Für Verbesserungen

- Export erzeugen
- Instanz 1 Analyse machen lassen
- Handoff an Instanz 2 geben
- nur sichere Änderungen zuerst umsetzen

### Für kompletten Neuaufbau

- Export erzeugen
- Instanz 1 Requirements extrahieren lassen
- Instanz 2 Greenfield-Architektur erstellen lassen
- neue Struktur schrittweise aufbauen

---

## 10. Projekt-Empfehlung

### Für bestehendes Home Assistant

Die empfohlene Standardvorgehensweise dieses Projekts ist:

**Zwei Instanzen**

1. Analyse und Handoff
2. Optimierung und Refactoring

### Für kompletten Neuanfang ohne Altlasten

Die empfohlene Standardvorgehensweise dieses Projekts ist:

**Zwei Instanzen**

1. Requirements-Extraktion aus dem Altbestand
2. Greenfield-Neuaufbau auf Basis dieser Requirements

---

## 11. Verhältnis zu den anderen Dokumenten

- `README.md` erklärt, **was** die App ist und wie sie installiert/verwendet wird.
- `DOCS.md` erklärt, **wie** der Exporter technisch arbeitet.
- `EXPORT_SCHEMA.md` beschreibt, **wie der Export aufgebaut ist**.
- `CHATGPT_WORKFLOWS.md` beschreibt, **wie du mit dem Export praktisch mit ChatGPT arbeitest**.

Wenn du Prompts oder Instanz-Übergaben baust, ist diese Datei der richtige Startpunkt.
