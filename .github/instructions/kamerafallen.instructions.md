---
applyTo: '**'
---

# Kamerafallen-Tools Project Instructions

## 🎯 Project Overview

This is a **camera trap (Kamerafallen) image management suite** for wildlife monitoring in German-speaking research contexts. The application provides a complete workflow from email extraction through AI analysis to organized image cataloging.

### Core Purpose
Process, analyze, and organize wildlife camera trap images with AI assistance, specifically designed for Bartgeier (Bearded Vulture) monitoring and other alpine species.

---

## 📋 Application Architecture

### Main Components

1. **`main_gui.py`** - Single launcher GUI (main entry point)
   - Starts all three tools from one interface
   - Handles environment configuration for sub-tools
   - Python-only, no external dependencies besides Tkinter

2. **`extract_img_email.py`** - Email image extractor
   - Processes Outlook `.msg` files
   - Extracts image attachments with configurable naming patterns
   - Default pattern: `fotofallen_2025_{num}.jpeg`

3. **`github_models_analyzer.py`** - AI-powered analyzer (PRIMARY TOOL)
   - Uses GitHub Models API (GPT-4o/GPT-5) for image analysis
   - **Complete workflow in one tool:**
     - AI analyzes image → Manual correction → Confirm → Save to Excel → **Automatic rename**
   - Generates structured Excel output (multi-sheet by location)
   - **Auto-renames images** after confirmation based on analysis data
   - Format: `MM.DD.YY-FP1-Bartgeier_2-Kolkrabe.jpeg`
   - Includes test mode (dummy data) when no API token available
   - Debug logging to `~/.kamerafallen-tools/analyzer_debug.log`

4. **`rename_images_from_excel.py`** - Batch renamer (FALLBACK TOOL)
   - **Only needed as alternative/fallback** when analyzer wasn't used
   - Reads Excel data and batch-renames images
   - Normally unnecessary since analyzer auto-renames after each confirmation

5. **Helper Modules:**
   - `github_models_api.py` - API calls and response parsing
   - `github_models_io.py` - Image I/O, backups, Excel operations

---

## 🔄 Normal Workflow

### Step 1: Extract Images from Emails
- Input: Folder with `.msg` Outlook email files
- Output: Extracted images with pattern `fotofallen_2025_{num}.jpeg`
- Tool: Email extractor GUI

### Step 2: AI Analysis + Auto-Rename (PRIMARY WORKFLOW)
- Input: Folder with extracted images
- Process:
  1. AI analyzes image (animals, location, date, time)
  2. User reviews/corrects analysis
  3. User clicks "Bestätigen (in Excel speichern)"
  4. Data saved to Excel immediately
  5. "Bild umbenennen" button becomes active
  6. User clicks rename → **Image automatically renamed** to structured format
  7. Move to next image
- Output: 
  - **Renamed images** (e.g., `08.15.25-FP1-Bartgeier_2-Gämse.jpeg`)
  - Multi-sheet Excel file (FP1, FP2, FP3, Nische sheets)
- Tool: GitHub Models Analyzer

### Step 3: Batch Rename (FALLBACK ONLY)
- **Only use if:** Images weren't processed through analyzer
- Input: Original images + completed Excel file
- Output: Batch-renamed images matching Excel data
- Tool: Batch renamer

---

## 🏗️ Code Architecture Principles

### Modular Design
- **API logic** → `github_models_api.py`
- **I/O operations** → `github_models_io.py`
- **GUI logic** → `github_models_analyzer.py`
- Keep concerns separated for maintainability

### GUI Best Practices
- **All user-facing text in German**
- Use `ttk` widgets for consistent styling
- Thread-based operations for API calls (don't block GUI)
- Immediate Excel saves after each confirmation (no batch saves)
- Show status updates and progress indicators

### Data Flow
```
Image → AI Analysis → User Review → Excel Save → Enable Rename → 
Rename Image → Backup Original → Update Excel with new filename → Next Image
```

### Excel Structure
- **Multi-sheet workbook:** Separate sheet per location (FP1, FP2, FP3, Nische)
- **Columns:** Nr., Standort, Datum, Uhrzeit, Generl, Luisa, Unbestimmt, Aktivität, Art 1-4, Anzahl 1-4, Interaktion, Sonstiges, Korrektur
- **Auto-incrementing IDs** per location sheet
- **Immediate writes** after each confirmation

---

## 🐛 Naming Conventions

### Image Renaming Format
```
MM.DD.YY-LOCATION-SPECIES1_COUNT-SPECIES2_COUNT.jpeg
```

**Examples:**
- `08.15.25-FP1-Bartgeier_2.jpeg`
- `07.22.25-FP2-Generl-Luisa.jpeg`
- `08.01.25-FP3-Gämse_3-Kolkrabe.jpeg`
- `09.10.25-Nische-Unbestimmt_Bartgeier.jpeg`

### Special Cases
- **Generl/Luisa:** Named individuals, no species prefix
- **Unbestimmt_Bartgeier:** Unidentified Bartgeier (neither Generl nor Luisa)
- **Multiple animals:** Joined with `-` separator
- **Counts > 1:** Add `_COUNT` suffix (e.g., `Gämse_3`)
- **Backups:** Original images saved to `backup_originals/` subfolder

### Animal Code Mappings
- `RK` (uppercase) → Rabenkrähe
- `rk` (lowercase) → Kolkrabe
- `RV` → Kolkrabe
- `Gams` → Gämse
- Standard names: Fuchs, Marder, Steinadler, Steinbock, Murmeltier

---

## 🔧 Environment Configuration

### Required Environment Variables
```bash
GITHUB_MODELS_TOKEN=ghp_xxxxx        # GitHub Models API token (Models permission)
ANALYZER_IMAGES_FOLDER=/path/to/imgs  # Optional: Default image folder
ANALYZER_OUTPUT_EXCEL=/path/to/out.xlsx  # Optional: Default Excel output
```

### .env File Locations (Priority Order)
1. PyInstaller bundle directory (`sys._MEIPASS`)
2. Executable directory (`sys.executable` parent)
3. Current working directory
4. Script file directory (`__file__` parent)

### Test Mode
- Checkbox: "Testdaten verwenden"
- Generates realistic dummy data without API calls
- Useful for development and testing GUI functionality

---

## 🚀 Build System

### Cross-Platform Executables
- **Linux:** `build_final.py` + `create_release.py`
- **Windows:** `build_windows_release.bat` (creates portable ZIP)
- **Size:** ~130MB standalone executables (includes Python runtime)

### PyInstaller Configuration
- Multiple `.spec` files for different configurations
- Key optimizations:
  - Include: tkinter, PIL, pandas, openpyxl, requests
  - Exclude: matplotlib, scipy, jupyter, Qt
- Bundle all dependencies for true standalone deployment

---

## 📝 Debugging & Logging

### Debug Log
- **Path:** `~/.kamerafallen-tools/analyzer_debug.log`
- **Content:** All print statements, token detection, .env loading
- **Access:** "Debug-Log öffnen" button in analyzer GUI
- **Persistent** across sessions for troubleshooting

### Common Debug Scenarios
1. **Token not detected:** Check debug log for .env file paths tried
2. **API failures:** Check 401 errors (invalid token), 429 (rate limit)
3. **Excel errors:** Verify file not open in another program
4. **Rename failures:** Check backup folder permissions

---

## 🎨 GUI Guidelines

### German Language
- All labels, buttons, messages in German
- Error messages clear and actionable
- Status indicators for async operations

### Button States
- **Disabled** states clearly indicated
- **"Bestätigen"** → Saves to Excel, enables rename
- **"Bild umbenennen"** → Only active after confirmation
- **"Weiter"** → Moves to next image after rename

### Workflow Indicators
- Green checkmarks for completed actions
- Orange/yellow for warnings
- Red for errors
- Status text shows current operation state

---

## ⚠️ Critical Implementation Notes

### Analyzer Workflow
1. **MUST save to Excel BEFORE enabling rename button**
2. **Rename operation MUST create backup first**
3. **Excel entry MUST be updated with new filename after rename**
4. **Image list MUST be refreshed after rename**
5. **Rename button MUST be disabled after successful rename**

### Excel Handling
- **Lock-aware:** Detect if file is open elsewhere
- **Atomic writes:** Use pandas Excel writer correctly
- **Preserve existing data:** Append, don't overwrite
- **Auto-create sheets:** If location sheet doesn't exist

### Image Backup Strategy
- **Always backup before rename:** Copy to `backup_originals/`
- **Never overwrite backups:** Check if backup already exists
- **Preserve metadata:** Use `shutil.copy2()` for timestamps

---

## 🧪 Testing Checklist

When modifying code, verify:
- [ ] Analyzer test mode works without token
- [ ] Excel saves immediately after confirmation
- [ ] Rename button only enables after Excel save
- [ ] Backups created before rename
- [ ] Excel updated with new filename after rename
- [ ] Next image navigation works correctly
- [ ] Debug log captures all operations
- [ ] German text correct and consistent
- [ ] Build scripts produce working executables
- [ ] Cross-platform compatibility maintained

---

## 📚 Key Dependencies

```python
extract-msg     # Outlook .msg file parsing
pandas          # Excel data handling  
openpyxl        # Excel file read/write
Pillow          # Image processing
requests        # GitHub Models API
python-dotenv   # Environment variable loading
pyinstaller     # Executable building
```

---

## 🔐 Security Notes

- **Never commit `.env`** files with real tokens
- **Token validation:** Check for Models permission
- **API rate limits:** Handle 429 errors gracefully
- **File permissions:** Verify write access before operations
- **Input validation:** Sanitize all user inputs

---

## 📖 Documentation Files

- `README.md` - English project overview
- `ANLEITUNG.md` - German user instructions
- `BUILD_INSTRUCTIONS.md` - Build guide for both platforms
- `README_PACKAGE.md` - Packaging notes
- This file - Developer instructions and context

---

## 🎯 Design Philosophy

1. **User-first:** German interface for target users
2. **Fail-safe:** Backups before destructive operations
3. **Immediate saves:** No data loss on crash
4. **Clear feedback:** Status at every step
5. **Modular:** Separated concerns for maintainability
6. **Standalone:** Single executable, no Python installation needed
7. **Debuggable:** Persistent logs for troubleshooting

---

## 🔧 Build Maintenance & Spec File Updates

### ⚠️ CRITICAL: Check After Every Code Change

**After modifying any Python code, ALWAYS verify if build spec files need updating:**

#### Decision Tree: Does My Change Require Spec File Updates?

**❌ YES - UPDATE REQUIRED** if you:
- ✓ Added a new pip package (check `requirements.txt`)
- ✓ Created a new `.py` module file
- ✓ Added `import` for an external library not in `hiddenimports`
- ✓ Added new data files (`.txt`, `.json`, `.csv`, icons, etc.)
- ✓ Changed application icon or resources
- ✓ Added new file dependencies that must be bundled

**✅ NO - UPDATE NOT NEEDED** if you only:
- ✓ Changed code logic within existing functions
- ✓ Added functions/classes to existing modules
- ✓ Used standard library imports already in `hiddenimports`
- ✓ Fixed bugs or optimized existing code
- ✓ Refactored without new dependencies

#### Files to Update When Changes Are Needed

**Both spec files must be kept in sync:**
1. `KamerafallenTools-Linux.spec` - Linux builds
2. `KamerafallenTools-Windows.spec` - Windows builds

#### Common Update Scenarios

**Scenario 1: New External Package**
```python
# If you add to requirements.txt:
pip install some-new-package

# Then add to BOTH spec files' hiddenimports:
hiddenimports=[
    ...,
    'some_new_package',  # ← Add this
]
```

**Scenario 2: New Python Module File**
```python
# If you create: my_new_module.py

# Then add to BOTH spec files' datas:
datas=[
    ('my_new_module.py', '.'),  # ← Add this
    ...
]
```

**Scenario 3: New Data File**
```python
# If you add: config.json or logo.png

# Then add to BOTH spec files' datas:
datas=[
    ('config.json', '.'),  # ← Add this
    ('logo.png', '.'),     # ← Add this
    ...
]
```

**Scenario 4: Standard Library Import (Usually Safe)**
```python
# If you add: import re, import json, import os
# Check if already in hiddenimports - if yes, NO UPDATE NEEDED
# Standard library imports are usually already covered
```

#### Verification Checklist After Code Changes

```bash
# 1. Review what changed
git diff

# 2. Check for new imports
grep -r "^import \|^from " *.py | grep -v "#"

# 3. Check for new files
git status

# 4. If unsure, test build locally
# Linux:
python3 build_final.py
# Windows:
build_windows_release.bat

# 5. Test the built executable thoroughly
```

#### Example: Recent Changes Analysis

**Change Made:** Added natural sorting to `github_models_io.py`
- Added `import re` → Already in hiddenimports ✅
- Modified existing function → No new dependencies ✅
- **Result:** No spec file update needed ✅

**Change Made:** Added zero-padding to `extract_img_email.py`
- Used `.zfill()` method → Built-in str method ✅
- No new imports → No new dependencies ✅
- **Result:** No spec file update needed ✅

#### When in Doubt

**If uncertain whether spec files need updating:**
1. ✓ Check `hiddenimports` section - is your import listed?
2. ✓ Check `datas` section - is your file listed?
3. ✓ Test build locally - does it run without errors?
4. ✓ Ask: "Did I add something from outside the project?"

**Rule of Thumb:** Internal refactoring = no update needed. External additions = update required.

---

**Remember:** The analyzer is the primary tool. It provides a complete workflow from analysis through renaming. The batch renamer is only a fallback for edge cases.