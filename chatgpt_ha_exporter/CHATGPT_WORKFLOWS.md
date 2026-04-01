# Empfohlene Workflows mit ChatGPT

Diese Datei beschreibt die **empfohlenen Arbeitsweisen mit ChatGPT** für den ChatGPT HA Exporter.

Sie verfolgt zwei Hauptziele:
- dein **bestehendes** Home-Assistant-Setup möglichst sicher analysieren, verbessern und refactoren
- bei Bedarf dein aktuelles Setup **komplett neu und ohne Altlasten** aufbauen lassen, ohne die historische Struktur ungeprüft zu übernehmen

Die zentrale Empfehlung lautet:

> Nutze **nicht dieselbe ChatGPT-Instanz** für Rohanalyse, Aufbereitung, Zielarchitektur und konkrete Umsetzung.
>
> Für hohe Qualität ist ein **mehrstufiger Workflow** besser.

---

## 1. Überblick: Welcher Workflow für welches Ziel?

### Workflow A – Bestehendes System verbessern
Nutze diesen Workflow, wenn du:
- dein aktuelles Setup behalten willst
- Altlasten gezielt abbauen willst
- Optimierungen, Bugfixes, Sicherheitsverbesserungen und Refactorings auf Basis des Ist-Systems willst
- das aktuelle Setup als Ausgangspunkt erhalten möchtest

**Empfehlung:** Zwei Instanzen
- **Instanz 1:** Analyse, Aufbereitung, Inventarisierung, Lücken- und Risikoerkennung
- **Instanz 2:** konkrete Verbesserung, Optimierung, Refactoring, Migrationsvorschläge

### Workflow B – Home Assistant von Grund auf neu aufbauen
Nutze diesen Workflow, wenn du:
- dein aktuelles Setup **nicht direkt weiterentwickeln**, sondern **neu aufsetzen** willst
- Altlasten, historisch gewachsene Strukturen, inkonsistente Benennung und Workarounds **nicht übernehmen** willst
- eine saubere Zielarchitektur aus Anforderungen statt aus Altbestand bauen willst
- das bestehende System nur noch als **Quellmaterial für Anforderungen, Verhalten und Prioritäten** verwenden willst

**Empfehlung:** Ebenfalls zwei Instanzen
- **Instanz 1:** extrahiert Anforderungen, Regeln, Geräteklassen, Domänenlogik, Betriebsabsicht und Zielprinzipien aus dem Altbestand
- **Instanz 2:** entwirft und erzeugt ein **sauberes Zielsystem von Grund auf**, ohne Altlasten blind mitzuschleppen

---

## 2. Grundprinzipien für gute Ergebnisse

Unabhängig vom Workflow gelten diese Regeln:

1. **Export zuerst erzeugen**
   - immer mit dem aktuellen ChatGPT HA Exporter
   - möglichst mit aktivierten Runtime-, Trace-, Security- und Storage-Daten

2. **Rohdaten nicht sofort refactoren lassen**
   - zuerst strukturieren, prüfen, normalisieren, priorisieren

3. **Fakten, Schlussfolgerungen und Unsicherheiten trennen**
   - besonders wichtig bei Home Assistant, weil viele Probleme nicht aus einzelnen Dateien, sondern aus Zusammenspiel, Runtime und Betreiberabsicht entstehen

4. **Operator Intent ergänzen**
   - wenn möglich `operator_intent.md` oder `operator_intent.json` mitgeben
   - dadurch reduziert sich die Restunsicherheit stark

5. **Menschliche Freigabe zwischen den Stufen**
   - nach Instanz 1 kurz prüfen, ob die Analyse korrekt und vollständig wirkt
   - erst danach Instanz 2 auf konkrete Änderungen ansetzen

---

## 3. Workflow A – Bestehendes Setup analysieren und verbessern

## 3.1 Zielbild

Dieser Workflow soll dein aktuelles Home Assistant:
- besser strukturieren
- sicherer machen
- wartbarer machen
- performanter machen
- logisch vereinfachen
- gezielt refactoren

ohne dabei unnötig Funktionsverhalten zu zerstören.

## 3.2 Empfohlene Rollen

### Instanz 1 – Analyse- und Aufbereitungsinstanz
Diese Instanz macht:
- Entpacken und Inventarisieren
- Struktur- und Kontextaufbereitung
- Konsistenzprüfung
- Risikoanalyse
- Problemklassifikation
- Refactoring-Vorbereitung
- Handoff-Paket für Instanz 2

Diese Instanz macht **nicht**:
- keine endgültigen Refactorings
- keine spekulativen Umbauten
- keine stillen Architekturentscheidungen

### Instanz 2 – Optimierungs- und Refactoring-Instanz
Diese Instanz macht:
- konkrete Verbesserungsvorschläge
- Zielarchitektur innerhalb des bestehenden Systems
- Refactoring-Pläne
- Naming-Standardisierung
- Helper-/Template-/Automation-Bereinigung
- Dashboard-/Integration-/Performance-Optimierung
- konkrete neue Dateien, Diffs oder Migrationsschritte

---

## 3.3 Empfohlene Reihenfolge

1. aktuellen Export hochladen
2. Instanz 1 mit Analyse-/Aufbereitungs-Prompt arbeiten lassen
3. Ergebnis von Instanz 1 prüfen
4. strukturierte Ausgabe von Instanz 1 an Instanz 2 übergeben
5. Instanz 2 konkrete Verbesserungen und Refactorings erstellen lassen
6. Änderungen selektiv umsetzen
7. neuen Export erzeugen
8. optional nochmals von Instanz 1/2 gegenprüfen lassen

---

## 3.4 Prompt für Instanz 1 – Analyse und Aufbereitung

```text
Du bist ein spezialisierter Home-Assistant-Analyse- und Aufbereitungsagent.

Ich gebe dir ein vom ChatGPT HA Exporter erzeugtes Export-Archiv. Deine Aufgabe ist NICHT, sofort Änderungen oder Refactorings vorzunehmen. Deine Aufgabe ist es, die Daten maximal sauber, vollständig, präzise, konsistent und für eine nachgelagerte andere ChatGPT-Instanz optimal nutzbar aufzubereiten.

Ziel:
Erstelle aus dem gelieferten Export ein belastbares Analyse- und Übergabepaket, damit eine zweite ChatGPT-Instanz darauf aufbauend umfassende Verbesserungen, Optimierungen, Erweiterungen, Fehlerbehebungen, Sicherheitsverbesserungen und vollständige Refactorings an meinem bestehenden Home-Assistant-Setup durchführen kann.

Arbeite streng evidenzbasiert:
- Fakten
- Schlussfolgerungen
- Unsicherheiten
klar trennen.

Pflichtaufgaben:
- Exportarchiv vollständig analysieren
- Dateistruktur und Exportumfang erfassen
- Integrationen, Add-ons, Geräte, Entitäten, Areas, Labels, Floors, Automationen, Skripte, Szenen, Templates, Helper, Dashboards, Blueprints, Custom Components, Services und Runtime-Hinweise inventarisieren
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
- nichts erfinden
- keine stillen Annahmen
- keine voreiligen Refactorings
- keine Semantik verändern
- Unsicherheit explizit markieren
- Ausgabe so aufbereiten, dass eine zweite ChatGPT-Instanz ohne Nachfragen direkt weiterarbeiten kann

Die wichtigste Ausgabedatei ist:
- handoff_for_optimizer.md
```

---

## 3.5 Prompt für Instanz 2 – Verbesserung und Refactoring des bestehenden Systems

```text
Du bist eine Home-Assistant-Optimierungs- und Refactoring-Instanz.

Ich gebe dir ein bereits aufbereitetes Analyse- und Übergabepaket zu meinem bestehenden Home-Assistant-System. Nutze dieses Paket als primäre Arbeitsgrundlage.

Dein Ziel:
Mein bestehendes Home Assistant umfassend verbessern, optimieren, vereinfachen, absichern, erweitern und strukturell refactoren – aber kontrolliert, evidenzbasiert und nachvollziehbar.

Arbeitsregeln:
- Nutze das Handoff-Paket und die strukturierten Inventare als Hauptquelle.
- Verändere nichts stillschweigend.
- Trenne klar zwischen:
  - sichere Änderungen
  - Änderungen mit Abhängigkeiten
  - riskante Änderungen
  - Änderungen, die Betreiberentscheidung erfordern
- Gib keine generischen Ratschläge, sondern systembezogene, konkrete Maßnahmen.
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

## 4. Workflow B – Home Assistant von Grund auf neu aufbauen, ohne Altlasten

Dieser Workflow ist für den Fall gedacht, dass du **nicht** das bestehende Setup „sauberer machen“, sondern **ein neues, sauberes Zielsystem** erzeugen willst.

Dabei ist das aktuelle Home Assistant nur noch:
- Verhaltensquelle
- Gerätequelle
- Integrationsquelle
- Anforderungenquelle
- Prioritätenquelle
- Risikoquelle

aber **nicht mehr** die Strukturvorlage.

Das ist wichtig.

> Der Neuaufbau-Workflow soll das bestehende Setup **nicht spiegeln**, sondern aus dem Ist-System nur extrahieren:
> - was das System können muss
> - welche Geräte und Domänen es gibt
> - welche Automationen fachlich gebraucht werden
> - welche Betriebsregeln wichtig sind
> - welche Altlasten nicht übernommen werden sollen

---

## 4.1 Zielbild des Neuaufbaus

Instanz 2 soll am Ende ein Home-Assistant-Zielsystem entwerfen, das:
- logisch sauber gegliedert ist
- konsequente Benennung nutzt
- klare Domänengrenzen hat
- Altlasten nicht mitschleppt
- nur notwendige Integrationen übernimmt
- klare Helper-/Template-/Automation-Standards hat
- für spätere Wartung und Erweiterung optimiert ist

---

## 4.2 Die zentrale Regel für den Neuaufbau

Der größte Fehler bei einem Neuaufbau ist:

> Das alte System 1:1 sauberer nachzubauen.

Das willst du hier ausdrücklich **nicht**.

Stattdessen:
- Altbestand analysieren
- Anforderungen extrahieren
- Zielprinzipien definieren
- neues System **von Grund auf** designen

---

## 4.3 Empfohlene Rollen

### Instanz 1 – Requirements- und Blueprint-Instanz
Diese Instanz extrahiert aus dem alten Export:
- fachliche Anforderungen
- Geräteklassen und Rollen
- Pflichtfunktionen
- kritische Automationen
- Betriebsregeln
- Sicherheitsanforderungen
- UI-/Dashboard-Anforderungen
- Namens- und Strukturprobleme im Altbestand
- Liste der Dinge, die NICHT übernommen werden sollen

Am Ende liefert sie **kein Refactoring des Altbestands**, sondern:
- Zielprinzipien
- Anforderungskatalog
- Architekturleitplanken
- Blueprint für den Neuaufbau

### Instanz 2 – Greenfield-Architektur- und Build-Instanz
Diese Instanz nimmt den Blueprint und erzeugt daraus:
- eine saubere Zielarchitektur
- neue Namenskonventionen
- neue Paket-/Dateistruktur
- neue Helper-/Template-/Automation-Architektur
- neue Dashboard-Struktur
- Integrationskonzept
- Migrationspfade vom Alt- ins Neusystem

---

## 4.4 Empfohlene Reihenfolge

1. aktuellen Export erzeugen
2. optional `operator_intent.md` ergänzen
3. Instanz 1 extrahiert Anforderungen und Zielprinzipien
4. Ergebnis kurz menschlich prüfen
5. Instanz 2 entwirft das komplette Zielsystem neu
6. Instanz 2 erstellt Migrationsstrategie vom Alt- ins Zielsystem
7. neues System schrittweise oder parallel aufbauen

---

## 4.5 Prompt für Instanz 1 – Requirements-Extraktion und Blueprint

```text
Du bist eine Home-Assistant-Requirements- und Blueprint-Instanz für einen Greenfield-Neuaufbau.

Ich gebe dir ein Export-Archiv meines bestehenden Home-Assistant-Systems. Deine Aufgabe ist NICHT, das bestehende Setup zu refactoren oder sauberer nachzubauen. Deine Aufgabe ist es, aus dem Altbestand nur die fachlich relevanten Anforderungen, Regeln, Geräteklassen, Muss-Funktionen, Prioritäten, Risiken und Zielprinzipien zu extrahieren.

Ziel:
Erzeuge einen präzisen Blueprint für ein komplett neues Home-Assistant-System ohne Altlasten. Das alte System dient nur als Beleg- und Anforderungsquelle, nicht als Strukturvorlage.

Arbeitsregeln:
- Extrahiere Anforderungen, nicht Altstruktur.
- Übernimm Altlasten nicht stillschweigend.
- Trenne streng zwischen:
  - Muss-Anforderungen
  - Soll-Anforderungen
  - Kann-Anforderungen
  - Legacy, das bewusst nicht übernommen werden sollte
- Identifiziere kritische Geräte, kritische Automationen, Sicherheitszonen, UI-Hauptpfade und betriebliche Muss-Funktionen.
- Leite Zielprinzipien für ein neues sauberes System ab.

Liefere mindestens:
- system_requirements.md
- functional_requirements.md
- non_functional_requirements.md
- critical_behaviors.md
- critical_automations.md
- device_classes_and_roles.json
- integration_requirements.json
- dashboard_requirements.md
- naming_and_structure_principles.md
- do_not_carry_over.md
- greenfield_architecture_principles.md
- migration_constraints.md
- handoff_for_greenfield_builder.md

Wichtig:
- keine direkte Refactoring-Lösung des Altbestands
- keine 1:1-Übernahme der aktuellen Struktur
- nichts erfinden
- Unsicherheiten explizit markieren
- deutlich benennen, welche Altbestandsteile nur historisch gewachsen sind und nicht Zielbild sein sollten
```

---

## 4.6 Prompt für Instanz 2 – Greenfield-Neuaufbau von Grund auf

```text
Du bist eine Home-Assistant-Greenfield-Architektur- und Build-Instanz.

Ich gebe dir ein aufbereitetes Requirements- und Blueprint-Paket, das aus meinem bestehenden Home-Assistant-System abgeleitet wurde. Deine Aufgabe ist es, daraus ein komplett neues, sauberes Home-Assistant-Zielsystem von Grund auf zu entwerfen – ohne Altlasten, ohne historisch gewachsene Strukturfehler und ohne blinde 1:1-Übernahme des alten Systems.

Ziel:
Entwirf ein neues Home Assistant, das dieselben fachlichen Kernfunktionen zuverlässig abdecken kann, aber strukturell, semantisch und architektonisch deutlich sauberer ist.

Grundprinzipien:
- Das alte System ist nur Anforderungsquelle, nicht Vorlage.
- Übernimm nur das, was fachlich notwendig ist.
- Entferne Legacy, Duplikate, Workarounds und historisch gewachsene Inkonsistenz.
- Definiere eine klare Zielarchitektur.
- Erzeuge eine Struktur, die langfristig wartbar, erweiterbar und nachvollziehbar ist.

Pflichtaufgaben:
- Zielarchitektur definieren
- empfohlene Verzeichnis- und Paketstruktur definieren
- Namensstandard definieren
- Integrationsstrategie definieren
- Helper-/Template-/Automation-/Script-Strategie definieren
- Dashboard-/UI-Strategie definieren
- Sicherheits- und Exposure-Modell definieren
- Logging-, Recorder- und Wartbarkeitsstrategie definieren
- Migrationspfad vom Altbestand zum Zielsystem definieren

Liefere mindestens:
- target_architecture.md
- directory_layout.md
- naming_standard.md
- integration_strategy.md
- helper_strategy.md
- template_strategy.md
- automation_architecture.md
- dashboard_architecture.md
- security_model.md
- recorder_and_logging_strategy.md
- migration_plan.md
- staged_rebuild_plan.md
- implementation_roadmap.json

Zusätzlich:
- Wenn möglich, liefere konkrete Startdateien, Paketvorschläge, Beispielstrukturen, Vorlagen und Namensschemata.
- Markiere klar, was direkt umsetzbar ist und was Betreiberentscheidung braucht.
- Gib keine Altlasten ungeprüft wieder aus.

Wichtig:
- baue neu, nicht nur sauberer alt
- nichts erfinden
- Unsicherheit markieren
- keine versteckten Annahmen
```

---

## 5. Empfohlene Zusatzdatei: operator_intent.md

Für beide Workflows ist eine zusätzliche Datei extrem hilfreich:

- `operator_intent.md`
- oder `operator_intent.json`

Empfohlene Inhalte:
- Zielarchitektur-Wunsch
- gewünschte Sprache der Benennung (deutsch, englisch, hybrid)
- kritische Automationen
- sicherheitskritische Geräte/Funktionen
- Bereiche, die nie automatisch geändert werden dürfen
- bevorzugte Integrationen oder Add-ons
- Bereiche, die bewusst alt bleiben dürfen
- Bereiche, die ausdrücklich komplett neu gedacht werden sollen

Beispielstruktur:

```md
# Operator Intent

## Zielbild
- möglichst modulare Struktur
- klare englische Benennung
- wenig Legacy
- Dashboards nach Räumen und Aufgaben getrennt

## Kritische Funktionen
- Alarmanlage
- Heizungssteuerung
- Gewächshaus / Zelt
- Backup-Überwachung

## Nicht automatisch ändern
- Sicherheitsautomationen
- Exposed Entities für Sprachassistenten

## Darf neu aufgebaut werden
- Dashboards
- Naming
- Helper-Struktur
- Automationsorganisation
```

---

## 6. Welche Artefakte du an welche Instanz gibst

## 6.1 Für Instanz 1

Immer mitgeben:
- das originale Export-Archiv (`.tar.gz`)
- optional `operator_intent.md`

## 6.2 Für Instanz 2 im Verbesserungsworkflow

Mitgeben:
- die aufbereitete Ausgabe von Instanz 1
- insbesondere:
  - `handoff_for_optimizer.md`
  - Inventare
  - Risikoberichte
  - Refactoring-Ziele
  - Prioritätslisten

## 6.3 Für Instanz 2 im Greenfield-Workflow

Mitgeben:
- die aufbereitete Ausgabe von Instanz 1
- insbesondere:
  - `handoff_for_greenfield_builder.md`
  - Requirements-Dateien
  - Zielprinzipien
  - `do_not_carry_over.md`
  - Migrationsgrenzen

---

## 7. Empfohlene Qualitätsprüfung nach jeder Stufe

Nach Instanz 1 prüfen:
- wurden Fakten und Schlussfolgerungen sauber getrennt?
- fehlen offensichtliche Kernbereiche?
- wurden kritische Automationen erkannt?
- wurden Unsicherheiten explizit gemacht?

Nach Instanz 2 prüfen:
- sind die Vorschläge systembezogen statt generisch?
- ist die Priorisierung plausibel?
- wurden riskante Änderungen korrekt markiert?
- wurde im Greenfield-Fall wirklich neu gedacht statt Altstruktur zu spiegeln?

---

## 8. Häufige Fehler, die du vermeiden solltest

### Beim Verbesserungsworkflow
- dieselbe Instanz analysiert und ändert gleichzeitig alles
- rohe Exportdaten werden sofort refactoriert
- Betreiberabsicht wird nicht mitgegeben
- riskante Änderungen werden nicht isoliert

### Beim Greenfield-Workflow
- das alte Setup wird einfach hübscher nachgebaut
- alte Namensfehler werden übernommen
- Legacy-Helper und Workarounds werden reproduziert
- Zielarchitektur wird nicht explizit definiert
- Migration wird nicht geplant

---

## 9. Minimalempfehlung, wenn du nur wenig Aufwand willst

Wenn du nicht viel Zeit investieren willst, nimm mindestens diesen Ablauf:

### Für Verbesserungen
1. Export erzeugen
2. Instanz 1 mit Analyse-/Aufbereitungs-Prompt
3. Instanz 2 mit Optimierungs-/Refactoring-Prompt

### Für kompletten Neuaufbau
1. Export erzeugen
2. optional `operator_intent.md` ergänzen
3. Instanz 1 mit Requirements-/Blueprint-Prompt
4. Instanz 2 mit Greenfield-Build-Prompt

---

## 10. Empfehlung des Projekts

Die stärkste Standardempfehlung ist:

### Für bestehendes HA:
**Zwei Instanzen**
- Analyse/Aufbereitung
- Optimierung/Refactoring

### Für kompletten Neuanfang ohne Altlasten:
**Zwei Instanzen**
- Requirements/Blueprint aus dem Altbestand
- Greenfield-Neuaufbau aus dem Blueprint

Genau diese Trennung reduziert Halluzinationen, unnötige Altlastübernahme und unkontrollierte Architekturentscheidungen am stärksten.
