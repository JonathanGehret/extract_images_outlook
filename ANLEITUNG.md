# Kamerafallen Bild-Analyzer - Anleitung

## 📖 Übersicht

Der Kamerafallen Bild-Analyzer ist ein GUI-Tool zur effizienten Analyse von Kamerafallen-Bildern mit KI-Unterstützung. Das Tool nutzt die GitHub Models API für automatische Bilderkennung und speichert die Ergebnisse strukturiert in Excel-Arbeitsblättern.

## ✨ Funktionen

- **Automatische KI-Analyse** mit GitHub Models (GPT-4o/GPT-5)
- **Manuelle Datenbearbeitung** für präzise Kontrolle
- **Sofortige Excel-Speicherung** nach jeder Bestätigung
- **Multi-Sheet Export** basierend auf Standorten (FP1, FP2, FP3, Nische)
- **Testdaten-Modus** für schnelle Entwicklung und Tests
- **Deutsche Benutzeroberfläche** mit lokalisierten Begriffen

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

### Hauptfunktionen

#### 1. **Automatische Analyse**
- Klicke "Aktuelles Bild analysieren"
- KI erkennt automatisch Tiere, Standort, Datum und Zeit
- Überprüfe und korrigiere die Ergebnisse bei Bedarf

#### 2. **Testdaten-Modus**
- Checkbox "Testdaten verwenden" aktiviert
- Automatische Generierung realistischer Testdaten
- Perfekt für Entwicklung und Tests

#### 3. **Manuelle Eingabe**
- Alle Felder können manuell bearbeitet werden
- Unterstützte Felder:
  - Standort (FP1/FP2/FP3/Nische)
  - Datum und Uhrzeit
  - Erkannte Tiere
  - Aktivität
  - Interaktion
  - Sonstiges

#### 4. **Daten bestätigen**
- Klicke "Bestätigen & Weiter"
- Daten werden sofort in Excel gespeichert
- Automatischer Wechsel zum nächsten Bild

## 📊 Excel-Export

### Arbeitsblatt-Struktur
- **FP1, FP2, FP3, Nische**: Separate Arbeitsblätter nach Standorten
- **Spalten**: Nr., Standort, Datum, Uhrzeit, Dagmar, Recka, Unbestimmt, Aktivität, Art 1, Anzahl 1, Art 2, Anzahl 2, Interaktion, Sonstiges, Korrektur

### Sofortige Speicherung
- Jede Bestätigung speichert sofort in Excel
- Keine Datenverluste bei Programmabsturz
- Kompatibel mit bestehenden Excel-Strukturen

## 🛠️ Technische Details

### GitHub Models API
- **GPT-4o**: Standard für Bildanalyse
- **GPT-5**: Erweiterte Funktionen (falls verfügbar)
- Automatische Fallback-Mechanismen

### Bilderkennung
- Unterstützte Formate: JPG, PNG
- Automatische Größenanpassung für Display
- Metadaten-Extraktion aus Dateinamen

### Datenspeicherung
- Pandas Excel-Integration
- Arbeitsblatt-basierte Organisation
- Bestehende Daten werden erhalten

## 🐛 Fehlerbehebung

### Häufige Probleme

#### 401-Fehler (Unauthorized)
```
Lösung: GitHub Token überprüfen
- Token hat 'Models' Berechtigung?
- Token noch gültig?
- Korrekt in Code eingesetzt?
```

#### Excel-Speicherung funktioniert nicht
```
Lösung: Datei-Berechtigungen prüfen
- Excel-Datei nicht in anderem Programm geöffnet?
- Schreibrechte für Ausgabeordner?
- Pandas korrekt installiert?
```

#### Bilder werden nicht geladen
```
Lösung: Bilderpfad überprüfen
- IMAGES_FOLDER Pfad korrekt?
- Bilder im richtigen Format?
- Dateinamen folgen Schema "fotofallen_2025_XXX"?
```

## 📝 Changelog

### Version 2.0 (August 2025)
- ✅ Deutsche Benutzeroberfläche
- ✅ Sofortige Excel-Speicherung
- ✅ Multi-Sheet Organisation
- ✅ Bereinigter Code
- ✅ Verbesserte Fehlerbehandlung

### Version 1.0 (August 2025)
- ✅ Grundlegende KI-Analyse
- ✅ GUI-Interface
- ✅ Excel-Export
- ✅ GitHub Models Integration

## 📧 Support

Bei Problemen oder Fragen wenden Sie sich an den Entwickler oder erstellen Sie ein Issue im Repository.

---
*Entwickelt mit GitHub Copilot für effiziente Kamerafallen-Datenanalyse*
