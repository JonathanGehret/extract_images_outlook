# Kamerafallen-Tools Architecture

## 🏗️ System Architecture Overview

This document explains the technical architecture, design decisions, and key implementation details of the Kamerafallen-Tools image analysis suite.

---

## 📦 Module Structure

```
┌─────────────────────────────────────────────────────────────┐
│                        main_gui.py                          │
│                  (Unified Launcher GUI)                     │
│  Launches all three tools from single interface             │
└────────────┬────────────────────────────────────────────────┘
             │
             ├─────────────► extract_img_email.py
             │               (Email Image Extractor)
             │
             ├─────────────► github_models_analyzer.py
             │               (AI Analyzer - PRIMARY TOOL)
             │               ┌──────────────────────────────┐
             │               │  AnalysisBuffer              │
             │               │  - Rolling analysis queue    │
             │               │  - ThreadPoolExecutor        │
             │               │  - Rate limit management     │
             │               └──────────────────────────────┘
             │               ┌──────────────────────────────┐
             │               │  ImageAnalyzer               │
             │               │  - Tkinter GUI               │
             │               │  - Image display/navigation  │
             │               │  - User input handling       │
             │               └──────────────────────────────┘
             │                      │
             │                      ├──► github_models_api.py
             │                      │    - API request handling
             │                      │    - Response parsing
             │                      │    - Model fallback logic
             │                      │
             │                      └──► github_models_io.py
             │                           - Image I/O operations
             │                           - Excel read/write
             │                           - File backup/rename
             │
             └─────────────► rename_images_from_excel.py
                             (Batch Renamer - FALLBACK TOOL)
```

---

## 🎯 Component Responsibilities

### **main_gui.py** (690 lines)
**Purpose:** Single entry point for all tools

**Responsibilities:**
- Launch analyzer, email extractor, or batch renamer
- Configure environment variables for sub-tools
- Provide unified interface for non-technical users

**Key Features:**
- Pure Tkinter (no external dependencies except stdlib)
- Standalone executable via PyInstaller
- Environment passthrough to child processes

---

### **github_models_analyzer.py** (2,170 lines)
**Purpose:** Main AI-powered image analysis tool

**Architecture:**

#### **Class: AnalysisBuffer** (~560 lines)
```python
class AnalysisBuffer:
    """
    Manages asynchronous image analysis with rolling buffer.
    
    Key Responsibilities:
    - Maintain queue of 5 pre-analyzed images
    - Coordinate ThreadPoolExecutor workers
    - Handle rate limiting and auto-recovery
    - Stagger API requests to respect concurrency limits
    """
```

**Critical Design Decisions:**

1. **Concurrent Workers = 2** (Line 188)
   ```python
   self.executor = ThreadPoolExecutor(max_workers=2)
   ```
   - GitHub Models API **hard limit: 2 concurrent requests**
   - Exceeding causes `UserConcurrentRequests` errors
   - Previous value (5) caused immediate failures

2. **Request Staggering = 0.8s** (Lines 204-205)
   ```python
   self.last_api_call_time = 0
   self.min_delay_between_calls = 0.8
   ```
   - Prevents concurrent request bursts
   - Smooths API load distribution
   - Calculated from: `2 workers × 0.8s = 1.6s window`

3. **Rolling Buffer = 5 Images** (Line 189)
   ```python
   self.buffer_size = 5
   ```
   - Always keeps 5 images ahead analyzed
   - User clicks "Next" → instant display (pre-analyzed)
   - Balance between memory and UX

**Buffer Workflow:**
```
User Action           Buffer Behavior
═══════════════════   ═══════════════════════════════════════
Press "Analysieren"   → Queue images 0-4 (staggered 0.8s apart)
                        Max 2 analyzing simultaneously
                        
Image 0 completes     → Automatically queue image 5
                        
User clicks "Next"    → Display buffered result (instant!)
                      → Queue image 6
                        
Rolling continues...  → Always 5 images ahead
```

#### **Class: ImageAnalyzer** (~1,400 lines)
```python
class ImageAnalyzer:
    """
    Main GUI application for image analysis.
    
    Key Responsibilities:
    - Tkinter interface setup
    - Image display and navigation
    - User input handling
    - Excel save coordination
    - Image renaming workflow
    """
```

**Key GUI Features:**
- Responsive layout (adapts to screen size)
- PhotoImage caching (prevents GC in executables)
- Dual-mode: AI analysis + manual correction
- Immediate Excel saves (no batch operations)
- Debug log viewer integration

---

### **github_models_api.py** (348 lines)
**Purpose:** GitHub Models API client

**Responsibilities:**
- HTTP request handling with `requests` library
- Multi-model fallback (gpt-4o → gpt-4o-mini)
- Response parsing and validation
- Error handling and retry logic

**Model Strategy:**
```python
# Primary: gpt-4o (50 requests/day)
# Fallback: gpt-4o-mini (8 requests/day)

# REMOVED: gpt-5 (not available in GitHub Models)
# REMOVED: api.github.com endpoints (404 errors)
```

**API Endpoint:**
```
https://models.inference.ai.azure.com/chat/completions
```

**Structured Response Parsing:**
```python
Expected format:
TIERE: <animals>
STANDORT: <location>
UHRZEIT: <time>
DATUM: <date>
```

---

### **github_models_io.py** (473 lines)
**Purpose:** I/O operations for images and Excel

**Responsibilities:**
- Image file discovery and listing
- Excel workbook read/write (multi-sheet)
- Image renaming with backup
- Natural sorting (fotofallen_2025_1, _2, ..., _10, _11)

**Excel Structure:**
- **Multi-sheet workbook** (FP1, FP2, FP3, Nische)
- **Columns:** Nr., Standort, Datum, Uhrzeit, Generl, Luisa, Unbestimmt, Aktivität, Art 1-4, Anzahl 1-4, Interaktion, Sonstiges, Korrektur
- **Auto-increment IDs** per sheet
- **Atomic writes** using pandas ExcelWriter

**Backup Strategy:**
```
Before renaming:
original.jpeg
    ↓
Copy to: backup_originals/original.jpeg
Rename: MM.DD.YY-FP1-Bartgeier_2.jpeg
```

---

## 🚦 Rate Limit Handling

### GitHub Models API Limits

| Limit Type | Value | Detection | Recovery |
|------------|-------|-----------|----------|
| **Concurrent** | 2 simultaneous | `UserConcurrentRequests` | 2s wait + retry |
| **Per-Minute** | Varies by model | `per 60s exceeded` | Auto-resume after wait |
| **Per-Day** | 50 (gpt-4o), 8 (gpt-4o-mini) | `per 86400s exceeded` | Manual wait until reset |
| **Tokens/Min** | 60,000 tokens | `UserByModelByMinuteTokens` | Auto-resume after 60s |

### Detection Logic (Lines 565-598)

```python
def _parse_rate_limit_error(self, error_message):
    """
    Detects rate limit type and extracts wait time.
    
    Priority Order:
    1. Concurrent limit (immediate)
    2. Token limit (60s)
    3. Per-minute limit (60s)
    4. Per-day limit (hours)
    """
    
    # Concurrent check (highest priority)
    if 'UserConcurrentRequests' in error_message or 'per 0s' in error_message:
        return {'wait_seconds': 2, 'limit_type': 'concurrent'}
    
    # Extract wait time from error
    match = re.search(r'wait (\d+) seconds', error_message)
    if match:
        wait_seconds = int(match.group(1))
        
        # Classify by duration
        if wait_seconds < 120:
            return {'wait_seconds': wait_seconds, 'limit_type': 'minute'}
        else:
            return {'wait_seconds': wait_seconds, 'limit_type': 'day'}
```

### Auto-Resume Mechanism (Lines 623-638)

```python
def _schedule_rate_limit_resume(self):
    """
    Automatically resumes analysis after short rate limits.
    
    Behavior:
    - < 5 min wait: Auto-resume with countdown
    - ≥ 5 min wait: Manual resume required
    """
    
    if self.rate_limit_wait_seconds < 300:  # 5 minutes
        self.root.after(
            (self.rate_limit_wait_seconds + 2) * 1000,
            self._resume_from_rate_limit
        )
```

### User Feedback (German)

| Limit Type | Message |
|------------|---------|
| Concurrent | `⚠️ Zu viele gleichzeitige Anfragen – warte kurz und versuche erneut` |
| Per-Minute | `⏱️ API-Limit: Bitte 60s warten (1 Anfrage pro Minute)` |
| Per-Day | `🚫 Tageslimit erreicht: Bitte 3h 24m warten (50 Anfragen pro Tag)` |
| Token/Min | `⏱️ API-Limit: Bitte 45s warten (Token-Limit pro Minute)` |

---

## ⚡ Performance Optimizations

### 1. **Request Staggering**
```python
# Timeline example (0.8s delays):
T=0.0s: Start image 0
T=0.8s: Start image 1
T=1.6s: Start image 2
T=2.4s: Start image 3
T=3.2s: Start image 4

# Max 2 analyzing concurrently
# Smooth, predictable load
```

### 2. **Rolling Buffer Continuation**
```python
def _ensure_buffer_ahead(self, current_index):
    """
    Called after:
    - Each image completion
    - Each "Next" button press
    - Each analysis confirmation
    
    Maintains 5-image lookahead continuously
    """
```

### 3. **PhotoImage Caching**
```python
# Prevent garbage collection in PyInstaller bundles
self.photo_images = []  # Strong reference list

# Each image load:
photo = ImageTk.PhotoImage(pil_image)
self.photo_images.append(photo)  # Keep alive
```

---

## 🔐 Security & Environment Configuration

### Environment Variable Priority

```
1. PyInstaller bundle directory (sys._MEIPASS)
   └─ .env, .env.local
   
2. Executable directory (sys.executable parent)
   └─ .env, .env.local
   
3. Current working directory
   └─ .env, .env.local
   
4. Script file directory (__file__ parent)
   └─ .env, .env.local
```

### Required Variables

```bash
GITHUB_MODELS_TOKEN=ghp_xxxxx        # Models permission required
ANALYZER_IMAGES_FOLDER=/path/to/imgs  # Optional: default folder
ANALYZER_OUTPUT_EXCEL=/path/to/out.xlsx  # Optional: default output
```

### Token Validation

```python
# Length check
if len(token) < 40:
    print("⚠️ Token seems too short")
    
# Permission check (via API test)
response = requests.post(endpoint, headers={"Authorization": f"Bearer {token}"})
if response.status_code == 401:
    print("❌ Token invalid or missing 'Models' permission")
```

---

## 🧪 Test Mode

### Dummy Data Generation

```python
if use_dummy_data:
    # Realistic test data without API
    animals = random.choice([
        "Bartgeier",
        "Generl",
        "Luisa", 
        "1 Kolkrabe",
        "2 Gämse",
        "1 Steinadler"
    ])
    
    location = random.choice(["FP1", "FP2", "FP3", "Nische"])
    date = generate_random_date()
    time = generate_random_time()
```

**Use Cases:**
- UI development without API quota
- Excel write testing
- Navigation flow verification
- GUI layout testing

---

## 📁 File Naming Conventions

### Extracted Images
```
fotofallen_2025_0001.jpeg
fotofallen_2025_0002.jpeg
...
fotofallen_2025_0234.jpeg
```
- Zero-padded 4-digit counter
- Natural sorting support
- Chronological order preserved

### Renamed Images
```
MM.DD.YY-LOCATION-SPECIES1_COUNT-SPECIES2.jpeg

Examples:
08.15.25-FP1-Bartgeier_2.jpeg
07.22.25-FP2-Generl-Luisa.jpeg
08.01.25-FP3-Gämse_3-Kolkrabe.jpeg
09.10.25-Nische-Unbestimmt_Bartgeier.jpeg
```

**Special Cases:**
- `Generl` / `Luisa`: Named individuals (no count)
- `Unbestimmt_Bartgeier`: Unidentified bearded vulture
- Multiple animals: Hyphen-separated
- Counts > 1: Underscore + number

### Animal Code Mappings
```python
"RK" (uppercase) → "Rabenkrähe"
"rk" (lowercase) → "Kolkrabe"
"RV" → "Kolkrabe"
"Gams" → "Gämse"
```

---

## 🛠️ Build System

### PyInstaller Configuration

```python
# Key exclusions (reduce size)
excludes = [
    'matplotlib', 'scipy', 'jupyter', 'notebook',
    'IPython', 'tornado', 'zmq', 'qt5', 'PyQt5'
]

# Critical includes
hiddenimports = [
    'PIL._tkinter_finder',
    'pandas', 'openpyxl', 'requests',
    'tkinter', 'tkinter.ttk'
]

# Data files
datas = [
    ('*.py', '.'),  # Include all modules
]
```

### Build Artifacts

| Platform | File | Size | Type |
|----------|------|------|------|
| Linux | `KamerafallenTools-Linux` | ~130MB | ELF executable |
| Windows | `KamerafallenTools.exe` | ~140MB | PE32+ executable |

**Includes:**
- Python 3.x runtime
- All dependencies
- Tkinter GUI libraries
- Image processing libraries

---

## 🐛 Debugging & Logging

### Persistent Debug Log

**Location:**
```
Linux:   ~/.kamerafallen-tools/analyzer_debug.log
Windows: C:\Users\USER\.kamerafallen-tools\analyzer_debug.log
```

**Content:**
- All print statements
- Token detection status
- .env file loading attempts
- API request/response details
- Rate limit events
- Buffer state changes

**Access:**
- GUI button: "Debug-Log öffnen"
- Direct file access
- Survives application restarts

### Common Debug Patterns

```bash
# Check staggering
grep "Staggering API call" ~/.kamerafallen-tools/analyzer_debug.log

# Verify buffer state
grep "Buffer state" ~/.kamerafallen-tools/analyzer_debug.log

# Find rate limit errors
grep "Rate limit" ~/.kamerafallen-tools/analyzer_debug.log

# Check concurrent violations
grep "UserConcurrentRequests" ~/.kamerafallen-tools/analyzer_debug.log
```

---

## 📊 Key Technical Achievements

### 1. **Concurrent Request Mastery**
- Identified GitHub Models hard limit (2 concurrent)
- Reduced ThreadPoolExecutor workers from 5 → 2
- Eliminated `UserConcurrentRequests` errors entirely

### 2. **Request Staggering System**
- 0.8-second minimum delay between API calls
- Prevents burst requests
- Smooth, predictable load distribution

### 3. **Smart Rate Limit Detection**
- Parses 4 different rate limit types
- Auto-classifies by wait duration
- Provides localized German user feedback

### 4. **Auto-Recovery Mechanism**
- Short limits (<5 min): Auto-resume with countdown
- Long limits (≥5 min): Graceful stop with instructions
- Maintains buffer state across rate limit cycles

### 5. **Rolling Buffer Architecture**
- Continuously maintains 5-image lookahead
- Instant navigation ("Next" shows pre-analyzed images)
- Resilient to failures and rate limits

### 6. **Natural Image Sorting**
- Handles numeric sequences correctly (1, 2, 10, 11 not 1, 10, 11, 2)
- Supports reverse order mode
- Preserves chronological relationships

---

## 🔄 Typical Workflow Execution

```
1. User: Press "Analysieren"
   ↓
2. AnalysisBuffer: Queue images 0-4 (staggered 0.8s)
   ↓
3. ThreadPoolExecutor: Max 2 concurrent API calls
   ↓
4. Image 0 completes → Buffer automatically queues image 5
   ↓
5. User: Press "Next" (instant - image 1 already analyzed!)
   ↓
6. AnalysisBuffer: Queue image 6 (0.8s delay)
   ↓
7. User: Review AI analysis, make corrections
   ↓
8. User: Press "Bestätigen"
   ↓
9. ImageAnalyzer: Save to Excel immediately
   ↓
10. User: Press "Bild umbenennen"
    ↓
11. github_models_io: Backup original → Rename
    ↓
12. Update Excel with new filename
    ↓
13. User: Press "Weiter" → Continue rolling...
```

---

## 🎯 Design Philosophy

1. **User-First**: German interface for target users
2. **Fail-Safe**: Backups before destructive operations
3. **Immediate Saves**: No data loss on crash
4. **Clear Feedback**: Status at every step
5. **Modular**: Separated concerns (GUI/API/IO)
6. **Standalone**: Single executable, no Python required
7. **Debuggable**: Persistent logs for troubleshooting
8. **Resilient**: Auto-recovery from transient errors

---

## 📚 Further Reading

- [README.md](README.md) - User documentation
- [ANLEITUNG.md](ANLEITUNG.md) - German usage guide
- [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) - Build process
- [.github/instructions/kamerafallen.instructions.md](.github/instructions/kamerafallen.instructions.md) - Developer guide

---

*Last Updated: October 2025*  
*Architecture reflects all concurrent request limit fixes and rolling buffer improvements*
