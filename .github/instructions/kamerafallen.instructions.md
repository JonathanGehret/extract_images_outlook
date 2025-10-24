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

3. **`github_models_analyzer.py`** - AI-powered analyzer (PRIMARY TOOL - 2,170 lines)
   - Uses GitHub Models API (GPT-4o, gpt-4o-mini) for image analysis
   - **Complete workflow in one tool:**
     - AI analyzes image → Manual correction → Confirm → Save to Excel → **Automatic rename**
   - **Rolling buffer system:** Always 5 images pre-analyzed ahead
   - **Request staggering:** 0.8s delays between API calls
   - **Smart rate limiting:** Auto-detection and recovery
   - Generates structured Excel output (multi-sheet by location)
   - **Auto-renames images** after confirmation based on analysis data
   - Format: `MM.DD.YY-FP1-Bartgeier_2-Kolkrabe.jpeg`
   - Includes test mode (dummy data) when no API token available
   - Debug logging to `~/.kamerafallen-tools/analyzer_debug.log`
   - **Two main classes:**
     - `AnalysisBuffer` (~560 lines): Async analysis queue management
     - `ImageAnalyzer` (~1,400 lines): Tkinter GUI and user interaction

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

## ⚡ Recent Performance Improvements (October 2025)

### Critical Bug Fixes & Optimizations

#### **1. Concurrent Request Limit Violation (RESOLVED)**
**Problem:** ThreadPoolExecutor was using 5 workers, but GitHub Models API only allows **2 concurrent requests**. This caused frequent `UserConcurrentRequests` errors.

**Solution:**
```python
# github_models_analyzer.py, Line 188
# BEFORE: ThreadPoolExecutor(max_workers=5) ❌
# AFTER:  ThreadPoolExecutor(max_workers=2) ✅
```

**Result:** Zero concurrent limit violations in production.

---

#### **2. Request Staggering System (NEW)**
**Problem:** Even with 2 workers, simultaneous request bursts triggered rate limits.

**Solution:** Implemented 0.8-second minimum delay between API calls
```python
# github_models_analyzer.py, Lines 204-205
self.last_api_call_time = 0
self.min_delay_between_calls = 0.8

# New method: _start_single_analysis()
# - Calculates time since last API call
# - Schedules delay if < 0.8s elapsed
# - Calls _do_start_analysis() after delay
```

**Timeline Example:**
```
T=0.0s: Start image 0
T=0.8s: Start image 1  (0.8s delay)
T=1.6s: Start image 2  (0.8s delay)
T=2.4s: Start image 3  (0.8s delay)
```

**Result:** Smooth, predictable API load distribution.

---

#### **3. Smart Rate Limit Detection (ENHANCED)**
**Problem:** Multiple rate limit types required different handling strategies.

**Solution:** Comprehensive detection in `_parse_rate_limit_error()` (Lines 565-598)
```python
def _parse_rate_limit_error(self, error_message):
    # Detects 4 types:
    
    # 1. Concurrent (CRITICAL - new detection)
    if 'UserConcurrentRequests' in error_message or 'per 0s' in error_message:
        return {'wait_seconds': 2, 'limit_type': 'concurrent'}
    
    # 2. Token limit (60k tokens/minute)
    if 'UserByModelByMinuteTokens' in error_message:
        return {'wait_seconds': wait_time, 'limit_type': 'minute'}
    
    # 3. Per-minute (varies by model)
    if wait_seconds < 120:
        return {'wait_seconds': wait_seconds, 'limit_type': 'minute'}
    
    # 4. Per-day (50/day for gpt-4o, 8/day for gpt-4o-mini)
    return {'wait_seconds': wait_seconds, 'limit_type': 'day'}
```

**German User Feedback:**
- Concurrent: `⚠️ Zu viele gleichzeitige Anfragen – warte kurz und versuche erneut`
- Per-minute: `⏱️ API-Limit: Bitte 60s warten (1 Anfrage pro Minute)`
- Per-day: `🚫 Tageslimit erreicht: Bitte 3h 24m warten (50 Anfragen pro Tag)`

**Result:** Clear feedback, auto-recovery from short limits.

---

#### **4. Rolling Buffer Continuation (FIXED)**
**Problem:** Buffer stopped after initial batch, no new analyses queued on navigation.

**Solution:** Enhanced `_ensure_buffer_ahead()` with staggering integration
```python
def _ensure_buffer_ahead(self, current_index):
    """
    Maintains 5-image lookahead continuously.
    
    Called after:
    - Each image completion
    - Each "Next" button press
    - Each analysis confirmation
    """
    # Queues next image with 0.8s stagger
    # Buffer never stops rolling
```

**Result:** Seamless navigation, images always pre-analyzed.

---

#### **5. Natural Sorting (NEW)**
**Problem:** Default Python sorting: `fotofallen_2025_1, _10, _11, _2` (wrong!)

**Solution:** Natural sort in `github_models_io.py`
```python
def natural_sort_key(filename):
    return [int(part) if part.isdigit() else part.lower() 
            for part in re.split(r'(\d+)', filename)]

# Results: _1, _2, _3, ..., _10, _11, _12 ✅
```

**Result:** Correct chronological order always maintained.

---

#### **6. Zero-Padding for Extracted Images (NEW)**
**Problem:** File numbers like `fotofallen_2025_1` vs `fotofallen_2025_100` sorted incorrectly.

**Solution:** 4-digit zero-padding in `extract_img_email.py`
```python
# BEFORE: fotofallen_2025_{counter}.jpeg
# AFTER:  fotofallen_2025_{counter:04d}.jpeg

# Output: fotofallen_2025_0001.jpeg, _0002.jpeg, ..., _0234.jpeg
```

**Result:** Perfect sorting in file managers and code.

---

#### **7. Reverse Order Mode (NEW FEATURE)**
**User Request:** Process newest images first.

**Implementation:**
```python
# Checkbox in GUI: "☑ Rückwärts (neueste zuerst)"
# Sorts image_files in reverse before display
# Natural sorting + reverse = newest-first
```

**Result:** Users can prioritize recent captures.

---

### GitHub Models API Limits (Confirmed)

| Limit Type | Value | Detection Method | Recovery |
|------------|-------|------------------|----------|
| **Concurrent** | **2 simultaneous** | `UserConcurrentRequests` or `per 0s` | 2s wait + auto-retry |
| **Per-Minute** | Varies (10-24 req/min) | `per 60s exceeded` | Auto-resume after wait |
| **Per-Day** | gpt-4o: 50, gpt-4o-mini: 8 | `per 86400s exceeded` | Manual wait |
| **Tokens/Min** | 60,000 tokens | `UserByModelByMinuteTokens` | Auto-resume after 60s |

**Critical Discovery:** gpt-4o-mini has only **8 requests/day** (much lower than gpt-4o's 50).

---

### Code Changes Summary

| File | Lines Changed | Change Type | Purpose |
|------|--------------|-------------|---------|
| `github_models_analyzer.py` | Line 188 | Modified | max_workers 5→2 |
| `github_models_analyzer.py` | Lines 204-205 | Added | Staggering variables |
| `github_models_analyzer.py` | Lines 305-365 | Modified/New | Staggering logic + `_do_start_analysis()` |
| `github_models_analyzer.py` | Lines 565-598 | Enhanced | Concurrent limit detection |
| `github_models_analyzer.py` | Lines 498-544 | Modified | German concurrent messages |
| `github_models_api.py` | Lines 40-48 | Removed | api.github.com endpoints (404 errors) |
| `github_models_io.py` | Lines 120-135 | Added | Natural sorting function |
| `extract_img_email.py` | Line 58 | Modified | Zero-padding for counters |

**Total Impact:** ~150 lines changed/added across 4 files.

---

### Testing & Verification

**Debug Log Evidence:**
```bash
# Successful staggering
[2025-10-24 18:34:41] DEBUG: Staggering API call for image 2 by 0.80s
[2025-10-24 18:34:41] DEBUG: Staggering API call for image 3 by 0.80s

# Zero concurrent errors
grep "UserConcurrentRequests" analyzer_debug.log
# Result: 0 occurrences ✅

# Buffer working correctly
[2025-10-24 18:34:55] DEBUG: Buffer state - buffered: 3, analyzing: 3
[2025-10-24 18:34:55] DEBUG: Found result in buffer for image 1: 1 Bartgeier

# Rate limit auto-recovery
[2025-10-24 18:35:16] Rate limit detected for image 4: ⏱️ API-Limit: Bitte 60s warten
[2025-10-24 18:35:16] DEBUG: Scheduled auto-resume in 62s after rate limit
[2025-10-24 18:36:18] DEBUG: Rate limit expired, resuming analysis from image 4
```

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