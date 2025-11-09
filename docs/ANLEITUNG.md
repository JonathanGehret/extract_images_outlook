# Kamerafallen Bild-Analyzer - Benutzerhandbuch

## 📖 Übersicht

Der Kamerafallen Bild-Analyzer ist ein professionelles GUI-Tool zur effizienten Analyse von Kamerafallen-Bildern mit KI-Unterstützung. Das Tool nutzt die GitHub Models API für automatische Bilderkennung und speichert die Ergebnisse strukturiert in Excel-Arbeitsblättern.

**Entwickelt für:** Wildtiermonitoring (speziell Bartgeier/Bearded Vulture)  
**Sprache:** Deutsche Benutzeroberfläche  
**Platform:** Windows & Linux

## ✨ Hauptfunktionen

- **KI-gestützte Bildanalyse** mit GitHub Models (GPT-4o)
- **Vorausschauender Puffer** - immer 5 Bilder voranalysiert
- **Manuelle Korrekturmöglichkeit** für präzise Daten
- **Sofortige Excel-Speicherung** - kein Datenverlust bei Absturz
- **Automatische Umbenennungautische Umbenennung** mit Backup-Funktion
- **Multi-Sheet Excel-Export** (FP1, FP2, FP3, Nische)
- **Testdaten-Modus** ohne API-Nutzung
- **Rückwärts-Modus** - neueste Bilder zuerst
- **Intelligente Rate-Limit-Erkennung** mit automatischer Wiederaufnahme

## 🚀 Installation & Setup

### 1. Voraussetzungen
```bash
pip install pandas pillow requests tkinter
```

### 2. GitHub Token einrichten
1. Gehe zu https://github.com/settings/tokens
2. Erstelle ein neues Personal Access Token
3. **Wichtig**: Aktiviere die 'Models' Berechtigung
4. Kopiere das Token und setze es in `github_models_analyzer.py`:
```python
GITHUB_TOKEN = "dein-github-token-hier"
```

### 3. Pfade konfigurieren
```python
IMAGES_FOLDER = "/pfad/zu/deinen/bildern"
OUTPUT_EXCEL = "/pfad/zur/excel/datei.xlsx"
```

## 🎯 Verwendung

### Programm starten
```bash
python3 github_models_analyzer.py
```

### Arbeitsablauf

#### Schritt 1: **Bildordner laden**
1. Klicke auf das Ordnersymbol neben "Bilder-Ordner"
2. Wähle den Ordner mit deinen Kamerafallen-Bildern
3. Bilder sollten das Format `fotofallen_2025_XXXX.jpeg` haben

#### Schritt 2: **Excel-Ausgabedatei wählen**
1. Klicke auf das Ordnersymbol neben "Ausgabe Excel"
2. Wähle eine bestehende Excel-Datei oder erstelle eine neue
3. Die Datei wird automatisch mit den richtigen Arbeitsblättern erstellt

#### Schritt 3: **Analyse starten**
1. **Option A - Mit KI:** Klicke "Aktuelles Bild analysieren"
   - KI erkennt automatisch: Tiere, Standort, Datum, Zeit
   - Dauert 2-5 Sekunden pro Bild
   - Puffer analysiert automatisch 5 Bilder voraus
   
2. **Option B - Testmodus:** Aktiviere "☑ Testdaten verwenden"
   - Generiert realistische Dummy-Daten
   - Kein API-Token erforderlich
   - Perfekt zum Testen der Oberfläche

#### Schritt 4: **Ergebnisse überprüfen**
- **Grüne Felder:** KI-erkannte Daten
- **Leere Felder:** Keine Erkennung
- **Manuelle Korrektur:** Alle Felder editierbar

**Unterstützte Felder:**
- Standort (FP1/FP2/FP3/Nische)
- Datum (DD.MM.YYYY)
- Uhrzeit (HH:MM:SS)
- Generl/Luisa (Checkboxen für bekannte Individuen)
- Unbestimmt_Bartgeier (Checkbox)
- Aktivität (z.B. "Fressen", "Fliegen")
- Tier 1-4 mit Anzahl
- Interaktion
- Sonstiges

#### Schritt 5: **Bestätigen & Speichern**
1. Klicke "Bestätigen (in Excel speichern)"
2. **Daten werden SOFORT gespeichert** (kein Datenverlust möglich!)
3. Button "Bild umbenennen" wird aktiviert

#### Schritt 6: **Bild umbenennen (optional)**
1. Klicke "Bild umbenennen"
2. Original wird in `backup_originals/` gesichert
3. Neuer Name: `MM.DD.YY-STANDORT-TIER_ANZAHL.jpeg`
4. Excel-Eintrag wird mit neuem Dateinamen aktualisiert

#### Schritt 7: **Weiter zum nächsten Bild**
1. Klicke "Weiter (→)" oder benutze Pfeiltasten
2. **Nächstes Bild ist bereits analysiert!** (dank Puffer)
3. Sofortige Anzeige ohne Wartezeit

---

### Besondere Funktionen

#### **Vorausschauender Puffer**
```
Aktuelles Bild: #5
═══════════════════════════════════
Puffer-Status: "4 analysiert, 1 wird analysiert"

Bedeutung:
- Bilder #6-9: Bereits fertig analysiert
- Bild #10: Wird gerade analysiert
- Beim Klick auf "Weiter": Sofortige Anzeige!
```

#### **Rückwärts-Modus**
- Checkbox "☑ Rückwärts (neueste zuerst)"
- Startet mit dem höchsten Bildnummer
- Nützlich für: Neueste Aufnahmen zuerst prüfen

#### **Rate-Limit-Anzeigen**
Wenn API-Limits erreicht werden, zeigt das Tool:

| Limit-Typ | Anzeige | Verhalten |
|-----------|---------|-----------|
| **Pro Minute** | ⏱️ API-Limit: Bitte 60s warten | Auto-Wiederaufnahme nach Countdown |
| **Pro Tag** | 🚫 Tageslimit erreicht: Bitte 3h warten | Manuelles Warten erforderlich |
| **Gleichzeitig** | ⚠️ Zu viele Anfragen | Auto-Wiederaufnahme nach 2s |

**Wichtig:** Das Tool wartet automatisch und setzt fort, wenn möglich!

---

### Testdaten-Modus (ohne API)

#### Aktivierung
1. Checkbox "☑ Testdaten verwenden" aktivieren
2. Klicke "Aktuelles Bild analysieren"
3. Realistische Dummy-Daten werden generiert

#### Vorteile
- Kein GitHub-Token erforderlich
- Sofortige Ergebnisse (keine Wartezeit)
- Perfekt zum Testen von:
  - Excel-Speicherung
  - Umbenennung-Funktion
  - Navigation
  - Benutzeroberfläche

#### Generierte Daten
```
Tiere: Bartgeier, Generl, Luisa, Kolkrabe, Gämse, Steinadler
Standorte: FP1, FP2, FP3, Nische
Datum: Zufällig zwischen 01.01-31.12.2025
Uhrzeit: Zufällig 00:00-23:59
```

## 📊 Excel-Export

### Arbeitsblatt-Struktur
```
Arbeitsmappe: "Kamerafallen_2025.xlsx"
├── FP1 (Fotopoint 1)
│   ├── Nr. (auto-inkrementiert)
│   ├── Standort
│   ├── Datum
│   ├── Uhrzeit
│   ├── Generl (Checkbox)
│   ├── Luisa (Checkbox)
│   ├── Unbestimmt (Checkbox)
│   ├── Aktivität
│   ├── Art 1-4
│   ├── Anzahl 1-4
│   ├── Interaktion
│   ├── Sonstiges
│   └── Korrektur
├── FP2 (separate Daten)
├── FP3 (separate Daten)
└── Nische (separate Daten)
```

### Beispiel-Einträge
```
Nr. | Standort | Datum      | Uhrzeit  | Generl | Luisa | Art 1        | Anzahl 1
────┼──────────┼────────────┼──────────┼────────┼───────┼──────────────┼─────────
1   | FP1      | 22.08.2025 | 11:52:06 |        |       | Rabenvogel   | 1
2   | FP1      | 22.08.2025 | 09:10:34 |        |       | Bartgeier    | (unbest.)
3   | FP1      | 21.08.2025 | 18:36:53 | ✓      | ✓     | Generl+Luisa |
```

### Sofortige Speicherung
- ✅ Jeder Klick auf "Bestätigen" speichert SOFORT
- ✅ Kein Datenverlust bei Programmabsturz
- ✅ Kompatibel mit bestehenden Excel-Dateien
- ✅ Arbeitsblätter werden automatisch erstellt

---

## 🖼️ Datei-Umbenennung

### Benennungsschema
```
MM.DD.YY-STANDORT-TIER_ANZAHL-TIER2.jpeg
```

### Beispiele
```
Vor:   fotofallen_2025_0379.jpeg
Nach:  08.22.25-FP1-Rabenvogel.jpeg

Vor:   fotofallen_2025_0380.jpeg
Nach:  08.22.25-FP1-Unbestimmt_Bartgeier.jpeg

Vor:   fotofallen_2025_0388.jpeg
Nach:  08.27.25-FP1-Generl-Luisa.jpeg

Vor:   fotofallen_2025_0392.jpeg
Nach:  08.01.25-FP3-Gämse_3-Kolkrabe.jpeg
```

### Spezialfälle
| Situation | Benennung | Beispiel |
|-----------|-----------|----------|
| **Bekanntes Individuum** | Name ohne Art | `Generl.jpeg` |
| **Beide Individuen** | Beide Namen | `Generl-Luisa.jpeg` |
| **Unbestimmter Bartgeier** | `Unbestimmt_Bartgeier` | `Unbestimmt_Bartgeier.jpeg` |
| **Mehrere Tiere** | Anzahl nach Tier | `Gämse_3.jpeg` |
| **Mehrere Arten** | Getrennt mit `-` | `Bartgeier-Kolkrabe.jpeg` |

### Backup-System
```
Ursprünglicher Ordner:
├── fotofallen_2025_0001.jpeg
├── fotofallen_2025_0002.jpeg
└── ...

Nach Umbenennung:
├── 08.15.25-FP1-Bartgeier.jpeg  ← Umbenannt
├── 08.16.25-FP1-Generl.jpeg     ← Umbenannt
└── backup_originals/
    ├── fotofallen_2025_0001.jpeg  ← Backup
    ├── fotofallen_2025_0002.jpeg  ← Backup
    └── ...
```

**Wichtig:** Originale werden IMMER gesichert!

---

## 🛠️ Technische Details

### GitHub Models API
- **Hauptmodell:** GPT-4o (50 Anfragen pro Tag)
- **Fallback:** GPT-4o-mini (8 Anfragen pro Tag)
- **Endpoint:** `https://models.inference.ai.azure.com`
- **Rate-Limits:**
  - Max. 2 gleichzeitige Anfragen
  - 60.000 Tokens pro Minute
  - Modell-spezifische Tageslimits

### Optimierungen
```
ThreadPoolExecutor: 2 Worker (GitHub-Limit)
Anfrage-Staffelung: 0,8s zwischen Anfragen
Puffer-Größe: 5 Bilder voraus
Auto-Wiederaufnahme: < 5 Minuten Wartezeit
```

### Bildverarbeitung
- **Formate:** JPG, JPEG, PNG
- **Größe:** Automatische Anpassung für Anzeige
- **Metadaten:** Extraktion aus Dateinamen
- **Sortierung:** Natürliche Sortierung (1, 2, 10, 11 statt 1, 10, 11, 2)

### Datensicherheit
- **Backups:** Vor jeder Umbenennung erstellt
- **Sofortspeicherung:** Excel nach jeder Bestätigung
- **Debug-Log:** Alles wird protokolliert (Details unten)

---

## 🐛 Fehlerbehebung

### Häufige Probleme

#### ❌ **"401 Unauthorized" Fehler**
```
Problem: GitHub-Token ungültig oder fehlend
```
**Lösung:**
1. Token prüfen auf: https://github.com/settings/tokens
2. **"Models" Berechtigung** aktiviert?
3. Token-Länge: mindestens 40 Zeichen
4. Umgebungsvariable korrekt? `echo $GITHUB_MODELS_TOKEN`

#### ❌ **Excel lässt sich nicht speichern**
```
Problem: Datei gesperrt oder keine Berechtigung
```
**Lösung:**
1. Excel-Datei in allen Programmen schließen
2. Schreibrechte für Ausgabeordner prüfen
3. Anderen Speicherort versuchen
4. Dateipfad auf Sonderzeichen prüfen

#### ❌ **Bilder werden nicht geladen**
```
Problem: Kein Bild gefunden oder falsches Format
```
**Lösung:**
1. Pfad zu Bilderordner prüfen
2. Dateiformate: JPG, JPEG, PNG unterstützt
3. Dateinamen sollten `fotofallen_2025_*` entsprechen
4. Absolute Pfade verwenden statt relative

#### ❌ **"Zu viele Anfragen" / Rate-Limit-Fehler**
```
Problem: API-Limit erreicht
```
**Erwartetes Verhalten:**
- **Tageslimit (50/Tag):** Automatische Erkennung, Wartezeit wird angezeigt
- **Pro-Minute-Limit:** Auto-Wiederaufnahme nach Countdown
- **Gleichzeitige Anfragen:** Wird durch Staffelung verhindert

**Wenn persistent:**
1. Debug-Log prüfen (siehe unten)
2. Nach `UserConcurrentRequests` suchen (sollte 0 sein)
3. Auf Quoten-Reset warten (wird in deutscher Nachricht angezeigt)

#### ❌ **Puffer zeigt falsche Anzahl**
```
Problem: Pufferzähler scheint inkorrekt
```
**Überprüfung via Debug-Log:**
```bash
grep "Buffer state" ~/.kamerafallen-tools/analyzer_debug.log
```
Sollte zeigen: `buffered: X, analyzing: Y` wobei Y ≤ 2

---

### Debug-Logging

#### Speicherort
- **Linux:** `~/.kamerafallen-tools/analyzer_debug.log`
- **Windows:** `C:\Users\BENUTZERNAME\.kamerafallen-tools\analyzer_debug.log`

#### Zugriff
- **Im Programm:** Button "Debug-Log öffnen"
- **Manuell:** Datei direkt öffnen

#### Inhalt
```
[2025-10-24 18:34:32] DEBUG: Analyzer session started
[2025-10-24 18:34:32] DEBUG: GitHub token detected: Yes (length=93)
[2025-10-24 18:34:41] DEBUG: Starting batch analysis from image 0
[2025-10-24 18:34:41] DEBUG: Staggering API call for image 2 by 0.80s
[2025-10-24 18:34:48] ✓ Analysis complete for image 0: 1 Rabenvogel
[2025-10-24 18:34:55] DEBUG: Buffer state - buffered: 3, analyzing: 3
```

#### Nützliche Debug-Befehle
```bash
# Staffelung prüfen
grep "Staggering API call" ~/.kamerafallen-tools/analyzer_debug.log

# Pufferstatus anzeigen
grep "Buffer state" ~/.kamerafallen-tools/analyzer_debug.log

# Rate-Limits finden
grep "Rate limit" ~/.kamerafallen-tools/analyzer_debug.log

# Gleichzeitige Anfragenfehler (sollte 0 sein!)
grep "UserConcurrentRequests" ~/.kamerafallen-tools/analyzer_debug.log
```

---

## 📝 Versionshistorie

### Version 3.0 (Oktober 2025) - **Aktuelle Version**
**Schwerpunkt: Performance & Zuverlässigkeit**

✅ **Neue Features:**
- Vorausschauender Puffer (5 Bilder)
- Rückwärts-Modus (neueste zuerst)
- Intelligente Rate-Limit-Erkennung
- Auto-Wiederaufnahme bei kurzen Limits
- Natürliche Bildersortierung

✅ **Performance-Optimierungen:**
- Anfrage-Staffelung (0,8s Verzögerung)
- Max. 2 gleichzeitige API-Anfragen
- Zero `UserConcurrentRequests` Fehler
- Sofortige Navigation (voranalysierte Bilder)

✅ **Zuverlässigkeit:**
- Backup vor jeder Umbenennung
- Sofortige Excel-Speicherung
- Persistentes Debug-Logging
- Verbesserte Fehlerbehandlung

---

### Version 2.0 (August 2025)
✅ Deutsche Benutzeroberfläche  
✅ Sofortige Excel-Speicherung  
✅ Multi-Sheet Organisation  
✅ Bereinigter Code  
✅ Modulare Architektur (API/IO getrennt)

---

### Version 1.0 (August 2025)
✅ Grundlegende KI-Analyse  
✅ GUI-Interface  
✅ Excel-Export  
✅ GitHub Models Integration

---

## 🎯 Tipps & Best Practices

### Effiziente Nutzung

1. **Puffer ausnutzen:**
   - Lass den Puffer vorarbeiten (zeigt "X analysiert")
   - Navigiere schnell vorwärts - Bilder sind schon fertig!
   - Keine Wartezeit zwischen Bildern

2. **Testmodus verwenden:**
   - Zum Üben: Testmodus aktivieren
   - Excel-Struktur testen ohne API-Quota
   - Umbenennung ausprobieren

3. **Excel-Datei organisieren:**
   - Eine Datei pro Projekt/Zeitraum
   - Arbeitsblätter pro Standort (automatisch)
   - Regelmäßige Backups erstellen

4. **Rate-Limits vermeiden:**
   - Tool arbeitet automatisch mit Limits
   - Tagesquota: 50 Bilder (gpt-4o)
   - Bei Limit: Testmodus verwenden

### Keyboard-Shortcuts

| Taste | Aktion |
|-------|--------|
| `→` | Nächstes Bild |
| `←` | Vorheriges Bild |
| `Eingabe` | Bestätigen (wenn Feld aktiv) |
| `Strg+S` | Speichern (= Bestätigen-Button) |

---

## 📚 Zusätzliche Dokumentation

- **[README.md](README.md)** - English project overview
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Technische Architektur (EN)
- **[BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md)** - Build-Anleitung

---

## 📧 Support & Kontakt

**Bei Problemen:**
1. Debug-Log prüfen (`~/.kamerafallen-tools/analyzer_debug.log`)
2. Häufige Probleme in diesem Handbuch nachschlagen
3. Issue erstellen: https://github.com/JonathanGehret/extract_images_outlook/issues

**Feedback & Vorschläge:**
- GitHub Discussions: https://github.com/JonathanGehret/extract_images_outlook/discussions

---

*Letzte Aktualisierung: Oktober 2025*  
*Version 3.0 mit allen Performance-Optimierungen*

