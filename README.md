# 🦅 Kamerafallen-Tools# Kamerafallen-Tools (Camera Trap Image Analysis Suite)



> **AI-powered wildlife camera trap image analysis and management suite**A comprehensive Python toolkit for wildlife camera trap image management, featuring AI-powered analysis, automated organization, and intelligent workflow automation.



A comprehensive Python toolkit for camera trap image processing, featuring GPT-4o-powered analysis, automated organization, and intelligent workflow automation. Originally developed for Bearded Vulture (*Bartgeier*) monitoring in alpine environments.## 🎯 Project Overview



[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)This suite provides a complete workflow for camera trap (Kamerafallen) image processing:

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)1. **Extract images** from Outlook email attachments

[![GitHub Models API](https://img.shields.io/badge/AI-GitHub%20Models-purple)](https://github.com/marketplace/models)2. **AI-powered analysis** with GitHub Models API (GPT-4o)

3. **Automated renaming** based on analysis results

---4. **Excel cataloging** with multi-sheet organization



## ✨ FeaturesOriginally developed for Bearded Vulture (Bartgeier) monitoring in alpine environments, but adaptable for any wildlife monitoring project.



### 🤖 **AI-Powered Analysis**## ✨ Key Features

- **Automatic species detection**: Bartgeier, Steinadler, Gämse, Kolkrabe, and more

- **Location recognition**: Identifies camera trap positions (FP1, FP2, FP3, Nische)### 🤖 **AI-Powered Image Analysis**

- **Metadata extraction**: Date, time, and behavioral observations- Automatic species detection (Bartgeier, Steinadler, Gämse, Kolkrabe, etc.)

- **Interactive correction**: Manual review and correction interface with dropdown menus- Location recognition (FP1, FP2, FP3, Nische)

- **Fullscreen viewer**: Zoom, pan, and examine images in detail- Date/time extraction from image metadata

- Manual correction interface for AI results

### ⚡ **Advanced Performance**

- **Rolling buffer system**: Pre-analyzes 5 images ahead for instant results### ⚡ **Advanced Concurrency & Rate Limiting**

- **Smart rate limiting**: Auto-detection and recovery from API limits- **Rolling buffer system**: Always 5 images pre-analyzed ahead

- **Request staggering**: 0.8s delays between calls prevent concurrent errors- **Request staggering**: 0.8s delays prevent API rate limits

- **Zero rate limit failures**: Optimized for GitHub Models 2-concurrent request limit- **Smart rate limit detection**: Auto-recovery from temporary limits

- **Concurrent request optimization**: Respects GitHub Models 2-concurrent limit

### 📊 **Data Management**- Zero `UserConcurrentRequests` errors after optimization

- **Excel integration**: Multi-sheet workbooks organized by location

- **Immediate saves**: No data loss with instant Excel writes after each confirmation### 📊 **Excel Integration**

- **Automated naming**: Structured filenames like `08.15.25-FP1-Bartgeier_2-Gämse.jpeg`- Multi-sheet workbooks (separate tabs per location)

- **Backup system**: Originals preserved before any rename operation- Immediate saves after each confirmation (no data loss)

- **Natural sorting**: Correct chronological order (1, 2, 3... 10, 11, 12)- Auto-incrementing IDs per location

- Preserves existing data when appending

### 🖼️ **Image Processing**

- **Email extraction**: Batch process Outlook `.msg` attachments### 🖼️ **Intelligent Image Management**

- **Smart renaming**: Species, count, location, and date in filename- Natural sorting (handles fotofallen_2025_1, _2, ..., _10, _11 correctly)

- **Image viewer**: Fullscreen mode with zoom and pan- Reverse order mode for newest-first processing

- **Reverse order**: Process newest images first- Automatic backup before renaming

- Structured naming: `MM.DD.YY-LOCATION-SPECIES_COUNT.jpeg`

---

### 🔧 **Email Image Extraction**

## 🚀 Quick Start- Batch processing of Outlook `.msg` files

- Zero-padded sequential naming (fotofallen_2025_0001.jpeg)

### Prerequisites- Progress tracking and error handling

- **Python 3.8+**

- **GitHub Personal Access Token** with Models permission ([Get one here](https://github.com/settings/tokens))## 🚀 Quick Start



### Installation### Prerequisites

- Python 3.8 or higher

```bash- GitHub Personal Access Token with **Models permission**

# Clone the repository

git clone https://github.com/JonathanGehret/extract_images_outlook.git### Installation

cd extract_images_outlook

1. **Clone this repository:**

# Create virtual environment```bash

python3 -m venv venvgit clone https://github.com/JonathanGehret/extract_images_outlook.git

source venv/bin/activate  # On Windows: venv\Scripts\activatecd extract_images_outlook

```

# Install dependencies

pip install -r requirements.txt2. **Install dependencies:**

``````bash

pip install -r requirements.txt

### Configuration```



Create a `.env` file in the project root:3. **Configure GitHub Models API:**

   - Go to https://github.com/settings/tokens

```env   - Create new Personal Access Token

GITHUB_MODELS_TOKEN=ghp_your_token_here   - Enable **"Models"** permission

ANALYZER_IMAGES_FOLDER=/path/to/your/images   - Set environment variable:

ANALYZER_OUTPUT_EXCEL=/path/to/output.xlsx   ```bash

```   export GITHUB_MODELS_TOKEN="ghp_your_token_here"

   ```

Or set environment variables:   Or create a `.env` file:

```bash   ```

export GITHUB_MODELS_TOKEN="ghp_your_token_here"   GITHUB_MODELS_TOKEN=ghp_your_token_here

```   ANALYZER_IMAGES_FOLDER=/path/to/images

   ANALYZER_OUTPUT_EXCEL=/path/to/output.xlsx

### Usage   ```



**Unified Launcher (Recommended)**### Basic Usage

```bash

python main_gui.py**Option 1: Unified Launcher (Recommended)**

``````bash

Select which tool to launch from the menu.python main_gui.py

```

**Direct Tool Launch**Then select which tool to launch (Analyzer, Email Extractor, or Batch Renamer).

```bash

# AI Analyzer (primary tool)**Option 2: Direct Tool Launch**

python github_models_analyzer.py```bash

# AI Analyzer (primary tool)

# Email image extractionpython github_models_analyzer.py

python extract_img_email.py

# Email image extraction

# Batch renaming from Excelpython extract_img_email.py

python rename_images_from_excel.py

```# Batch renaming from Excel

python rename_images_from_excel.py

---```



## 📖 Workflow

## 🏆 Key Technical Achievements

### 1️⃣ **Extract Images from Emails**

Place Outlook `.msg` files in a folder, run the extractor, and get sequentially numbered images.### 1. **Concurrent Request Optimization**

**Problem:** GitHub Models API limits to **2 simultaneous requests**. Initial implementation used 5 workers, causing `UserConcurrentRequests` errors.

```

Input:  email1.msg, email2.msg**Solution:**

Output: fotofallen_2025_0001.jpeg, fotofallen_2025_0002.jpeg...```python

```# Before: ThreadPoolExecutor(max_workers=5) ❌

# After:  ThreadPoolExecutor(max_workers=2) ✅

### 2️⃣ **AI Analysis + Auto-Rename**```

The analyzer processes images with AI, lets you review/correct, saves to Excel, and renames automatically.**Result:** Zero concurrent limit violations, 100% successful request handling.



```---

Original: fotofallen_2025_0001.jpeg

AI finds: 2 Bartgeier at FP1, 08.15.2025, 14:30### 2. **Request Staggering System**

You confirm ✓**Problem:** Even with 2 workers, simultaneous request bursts triggered rate limits.

Renamed:  08.15.25-FP1-Bartgeier_2.jpeg

```**Solution:** Implemented 0.8-second minimum delay between API calls:

```python

**Features per image:**self.last_api_call_time = 0

- 🔍 **Fullscreen viewer** with zoom/panself.min_delay_between_calls = 0.8

- 📝 **Dropdown menus** for quick corrections

- 📅 **Date/time pickers** for easy selection# Timeline:

- ✅ **Instant Excel save** after confirmation# T=0.0s: Start image 0

- 🎯 **Auto-rename** with structured format# T=0.8s: Start image 1

# T=1.6s: Start image 2

### 3️⃣ **Excel Output**# ...smooth, controlled flow

Multi-sheet workbook with organized data:```

**Result:** Predictable load distribution, eliminated burst-related failures.

| Nr. | Standort | Datum | Uhrzeit | Art 1 | Anzahl 1 | Art 2 | Anzahl 2 | ... |

|-----|----------|-------|---------|-------|----------|-------|----------|-----|---

| 1   | FP1      | 08.15.25 | 14:30 | Bartgeier | 2 | Gämse | 1 | ... |

### 3. **Smart Rate Limit Detection & Recovery**

---**Problem:** Multiple rate limit types (concurrent, per-minute, per-day, token-based) required different handling.



## 🎨 UI Features**Solution:** Comprehensive parsing and classification:

```python

### Dropdown Menusdef _parse_rate_limit_error(error_message):

- **Standort**: FP1, FP2, FP3, Nische    # Detects 4 types:

- **Species**: Bartgeier, Steinadler, Gämse, Kolkrabe, Fuchs, Steinbock, Murmeltier, etc.    # 1. Concurrent (2 per 0s) → 2s wait

- **Aktivität**: Fliegen, Stehen, Fressen, Sitzen, Laufen, Beobachten    # 2. Token limit (60k per 60s) → 60s wait

- **Interaktion**: Keine, Territorial, Spielerisch, Aggressiv, Neutral    # 3. Per-minute (varies) → auto-resume

    # 4. Per-day (50/day) → manual wait

### Date & Time Pickers```

- **📅 Calendar popup** for visual date selection**German User Feedback:**

- **⏰ Hour/minute dropdowns** (5-minute intervals)- `⚠️ Zu viele gleichzeitige Anfragen` (concurrent)

- **Auto-formatting** with `dd.mm.yyyy` and `HH:MM`- `⏱️ API-Limit: Bitte 60s warten` (per-minute)

- `🚫 Tageslimit erreicht: Bitte 3h 24m warten` (per-day)

### Fullscreen Image Viewer

- **Click image** or "🔍 Vollbild" button**Result:** Auto-recovery from short limits, clear instructions for long limits.

- **Mouse wheel zoom** (10% - 1000%)

- **Drag to pan** when zoomed---

- **Fit-to-screen** button

- **ESC to close**### 4. **Rolling Buffer Architecture**

**Problem:** Users had to wait for each image analysis before proceeding.

---

**Solution:** Asynchronous pre-analysis with rolling queue:

## 🏗️ Project Structure```python

class AnalysisBuffer:

```    """

extract_images_outlook/    Always maintains 5 images ahead analyzed.

├── main_gui.py                  # Unified launcher    

├── github_models_analyzer.py    # AI analyzer (primary tool)    User clicks "Next" → Instant display (already analyzed!)

├── github_models_api.py         # API communication layer    Image completes → Automatically queue next image

├── github_models_io.py          # File I/O and Excel operations    """

├── extract_img_email.py         # Email image extractor```

├── rename_images_from_excel.py  # Batch renamer (fallback)**Result:** Seamless navigation, zero waiting for users.

├── requirements.txt             # Python dependencies

├── .env.example                 # Environment configuration template---

├── docs/                        # Documentation

│   ├── ARCHITECTURE.md          # Technical deep-dive### 5. **Natural Image Sorting**

│   ├── BUILD_INSTRUCTIONS.md    # Build guide**Problem:** Default Python sorting: `fotofallen_2025_1, _10, _11, _2` (wrong order!)

│   ├── ANLEITUNG.md            # German user manual

│   └── DOCUMENTATION_SUMMARY.md # Doc overview**Solution:** Natural sort with regex-based numeric extraction:

├── build/                       # Build scripts and specs```python

│   ├── scripts/                 # Build automationdef natural_sort_key(filename):

│   └── specs/                   # PyInstaller configurations    return [int(part) if part.isdigit() else part.lower() 

└── .github/            for part in re.split(r'(\d+)', filename)]

    └── instructions/            # AI development context```

```**Result:** Correct chronological order: `_1, _2, ..., _10, _11`.



------



## 🔧 Technical Details### 6. **Zero-Data-Loss Excel Writes**

**Problem:** Batch operations risk data loss on crash.

### API Integration

- **GitHub Models API**: GPT-4o and gpt-4o-mini**Solution:** Immediate Excel save after each confirmation:

- **Rate Limits**: ```python

  - Concurrent: 2 simultaneous requests (strictly enforced)# User clicks "Bestätigen"

  - Per-minute: Varies by model→ Save to Excel immediately

  - Per-day: gpt-4o = 50, gpt-4o-mini = 8→ Enable rename button

- **Auto-recovery**: Smart detection and retry logic→ Update Excel after rename

```

### Performance Optimizations**Result:** No data loss even during crashes or power failures.

- **ThreadPoolExecutor**: 2 workers (concurrent limit)

- **Request staggering**: 0.8s minimum between API calls---

- **Rolling buffer**: 5-image lookahead for seamless navigation

- **Natural sorting**: Correct filename ordering (1, 2... 10, 11, 12)### 7. **Cross-Platform Executable Builds**

**Problem:** Users without Python need standalone executables.

### Data Format

**Image Naming Convention:****Solution:** PyInstaller with optimized bundles:

```- Size: ~130MB (includes Python runtime + all dependencies)

MM.DD.YY-LOCATION-SPECIES1_COUNT-SPECIES2.jpeg- Platforms: Linux (`ELF`) + Windows (`PE32+`)

```- Zero external dependencies required



**Examples:****Result:** True standalone deployment, no Python installation needed.

- `08.15.25-FP1-Bartgeier_2.jpeg`

- `07.22.25-FP2-Generl-Luisa.jpeg` (named individuals)---

- `08.01.25-FP3-Gämse_3-Kolkrabe.jpeg` (multiple species)

- `09.10.25-Nische-Unbestimmt_Bartgeier.jpeg` (unidentified individual)## 📊 Performance Metrics



---| Metric | Before Optimization | After Optimization |

|--------|-------------------|-------------------|

## 📚 Documentation| Concurrent violations | ~60% of requests | **0%** ✅ |

| Buffer lag | Wait 3-5s per image | **Instant** ✅ |

- **[Architecture Guide](docs/ARCHITECTURE.md)** - Technical deep-dive and implementation details| Rate limit crashes | Frequent | **Auto-recovers** ✅ |

- **[Build Instructions](docs/BUILD_INSTRUCTIONS.md)** - Create standalone executables| Data loss on crash | Possible | **Zero** ✅ |

- **[Anleitung (German)](docs/ANLEITUNG.md)** - German user manual| Sorting errors | 15-20% misorders | **0%** ✅ |

- **[Documentation Summary](docs/DOCUMENTATION_SUMMARY.md)** - Doc navigation

---

---

## 📁 Repository Structure

## 🐛 Debugging

```

**Debug Log Location:** `~/.kamerafallen-tools/analyzer_debug.log`extract_images_outlook/

├── main_gui.py                      # Unified launcher GUI (entry point)

**Access from GUI:** Click "Debug-Log öffnen" button in analyzer├── github_models_analyzer.py        # AI analyzer (2,170 lines - primary tool)

│   ├── AnalysisBuffer class         # Async analysis with rolling queue

**Common Issues:**│   └── ImageAnalyzer class          # Tkinter GUI + user interaction

- **No GitHub token**: Check `.env` file or environment variables├── github_models_api.py             # GitHub Models API client (348 lines)

- **API errors**: Verify token has Models permission├── github_models_io.py              # Image I/O + Excel operations (473 lines)

- **Rate limits**: Tool auto-recovers, just wait for countdown├── extract_img_email.py             # Outlook .msg attachment extractor

- **Excel locked**: Close Excel before running analyzer├── rename_images_from_excel.py     # Batch renamer (fallback tool)

├── build_final.py                   # PyInstaller build script (Linux)

---├── build_windows_release.bat        # PyInstaller build script (Windows)

├── requirements.txt                 # Python dependencies

## 🤝 Contributing├── README.md                        # This file

├── ARCHITECTURE.md                  # Technical architecture documentation

Contributions welcome! This project is actively maintained.├── ANLEITUNG.md                     # German user guide

├── BUILD_INSTRUCTIONS.md            # Build process documentation

**Areas for contribution:**└── .github/instructions/

- Additional species detection    └── kamerafallen.instructions.md # Developer instructions

- UI/UX improvements```

- Documentation translations

- Bug reports and fixes## 🔧 Tool Descriptions



---### **1. GitHub Models Analyzer** (PRIMARY TOOL)

**File:** `github_models_analyzer.py`  

## 📝 License**Purpose:** AI-powered image analysis with complete workflow



This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.**Workflow:**

1. AI analyzes image → Detects animals, location, date, time

---2. User reviews/corrects analysis

3. User clicks "Bestätigen" → Saves to Excel immediately

## 🎯 Use Cases4. User clicks "Bild umbenennen" → **Auto-renames** with backup

5. Move to next image → Repeat

- **Wildlife monitoring**: Camera trap image analysis for research

- **Conservation projects**: Track endangered species populations**Output:**

- **Alpine ecology**: Bartgeier and other alpine species- Multi-sheet Excel file (FP1, FP2, FP3, Nische tabs)

- **Data cataloging**: Organize large image collections efficiently- Renamed images: `MM.DD.YY-LOCATION-SPECIES_COUNT.jpeg`

- Backup of originals in `backup_originals/` folder

---

**Key Features:**

## 💡 Credits- Rolling buffer (5 images always pre-analyzed)

- Rate limit auto-recovery

- **Developed by**: Jonathan Gehret (with GitHub Copilot)- Test mode (no API needed)

- **AI**: GitHub Models API (GPT-4o)- Debug logging to `~/.kamerafallen-tools/analyzer_debug.log`

- **UI Framework**: Tkinter with tkcalendar

- **Image Processing**: Pillow (PIL)---

- **Data Management**: pandas, openpyxl

### **2. Email Image Extractor**

---**File:** `extract_img_email.py`  

**Purpose:** Extract images from Outlook `.msg` files

## 📧 Contact

**Usage:**

**Jonathan Gehret**```python

- GitHub: [@JonathanGehret](https://github.com/JonathanGehret)input_folder = "/path/to/msg/files"

output_folder = "/path/to/extracted/images"

---```

Run: `python extract_img_email.py`

<p align="center">

  <sub>Built with ❤️ for wildlife conservation and research</sub>**Output:** `fotofallen_2025_0001.jpeg, _0002.jpeg, ...`

</p>

---

### **3. Batch Renamer** (FALLBACK ONLY)
**File:** `rename_images_from_excel.py`  
**Purpose:** Batch rename images from Excel data

**Note:** Only needed if images weren't processed through analyzer.  
Analyzer auto-renames after each confirmation, making batch renaming unnecessary.

---

### **4. Unified Launcher**
**File:** `main_gui.py`  
**Purpose:** Single entry point for all tools

Launches analyzer, email extractor, or batch renamer from one interface.

---

## 📖 Detailed Documentation

| Document | Purpose |
|----------|---------|
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | Technical deep-dive: buffer system, rate limiting, concurrency |
| **[ANLEITUNG.md](ANLEITUNG.md)** | German user guide with screenshots and examples |
| **[BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md)** | Build standalone executables for Linux/Windows |
| **[.github/instructions/](..github/instructions/kamerafallen.instructions.md)** | Developer guide and code context |

---

## 🔬 API & Rate Limits

### GitHub Models API
- **Endpoint:** `https://models.inference.ai.azure.com/chat/completions`
- **Models:** gpt-4o (primary), gpt-4o-mini (fallback)
- **Authentication:** Personal Access Token with **Models** permission

### Rate Limits
| Type | Limit | Recovery |
|------|-------|----------|
| **Concurrent** | 2 simultaneous requests | 2s auto-recovery |
| **Per-Minute** | Varies by model | Auto-resume after wait |
| **Per-Day** | gpt-4o: 50, gpt-4o-mini: 8 | Manual wait until reset |
| **Tokens/Min** | 60,000 tokens | Auto-resume after 60s |

**Our Optimizations:**
- Max 2 workers (respects concurrent limit)
- 0.8s staggering (prevents bursts)
- Smart detection (4 limit types)
- Auto-recovery (short limits)

---

## 🐛 Troubleshooting

### Common Issues

#### ❌ **401 Unauthorized Error**
```
Problem: Invalid or missing GitHub Models token
```
**Solutions:**
1. Verify token at https://github.com/settings/tokens
2. Ensure **"Models" permission** is enabled
3. Check token length (should be ~40+ characters)
4. Confirm environment variable: `echo $GITHUB_MODELS_TOKEN`

#### ❌ **Excel File Won't Save**
```
Problem: Excel file locked or permission denied
```
**Solutions:**
1. Close Excel file in all programs
2. Check write permissions for output folder
3. Verify file path is valid
4. Try different output location

#### ❌ **Images Not Loading**
```
Problem: No images found or wrong format
```
**Solutions:**
1. Verify `IMAGES_FOLDER` path is correct
2. Check image formats (JPG, PNG supported)
3. Ensure filenames match pattern: `fotofallen_2025_*`
4. Try absolute paths instead of relative

#### ❌ **Rate Limit Errors**
```
Problem: "Too Many Requests" or "Rate limit exceeded"
```
**Expected Behavior:**
- Daily limit (50/day for gpt-4o): Auto-detected, shows wait time
- Per-minute limit: Auto-recovery after countdown
- Concurrent limit (2 max): Prevented by staggering system

**If persistent:**
1. Check debug log: `~/.kamerafallen-tools/analyzer_debug.log`
2. Look for `UserConcurrentRequests` (should be zero)
3. Wait for daily quota reset (shown in German message)

#### ❌ **Buffer Showing Wrong Count**
```
Problem: Buffer counter seems incorrect
```
**Verification:**
```bash
grep "Buffer state" ~/.kamerafallen-tools/analyzer_debug.log
```
Should show: `buffered: X, analyzing: Y` where Y ≤ 2

---

## 🧪 Testing & Development

### Test Mode (No API Required)
```python
# In analyzer GUI, enable:
☑ Testdaten verwenden
```
Generates realistic dummy data without consuming API quota.

### Debug Logging
**Location:**
- Linux: `~/.kamerafallen-tools/analyzer_debug.log`
- Windows: `C:\Users\USERNAME\.kamerafallen-tools\analyzer_debug.log`

**Access:** Click "Debug-Log öffnen" button in analyzer GUI

**Contents:**
- Token detection status
- .env file loading attempts
- API request/response details
- Rate limit events
- Buffer state changes

### Debug Commands
```bash
# Check for staggering
grep "Staggering API call" ~/.kamerafallen-tools/analyzer_debug.log

# Verify buffer state
grep "Buffer state" ~/.kamerafallen-tools/analyzer_debug.log

# Find rate limits
grep "Rate limit" ~/.kamerafallen-tools/analyzer_debug.log

# Check for concurrent errors (should be zero)
grep "UserConcurrentRequests" ~/.kamerafallen-tools/analyzer_debug.log
```

---

## 🔧 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `extract-msg` | Latest | Outlook .msg file parsing |
| `pandas` | ≥1.3.0 | Excel data handling |
| `openpyxl` | ≥3.0.0 | Excel file read/write |
| `Pillow` | ≥8.0.0 | Image processing & display |
| `requests` | ≥2.25.0 | GitHub Models API calls |
| `python-dotenv` | ≥0.19.0 | Environment variable loading |
| `tkinter` | Stdlib | GUI framework |

**Install all:**
```bash
pip install -r requirements.txt
```

---

## 🏗️ Building Standalone Executables

### Linux
```bash
python build_final.py
# Output: dist/KamerafallenTools-Linux
```

### Windows
```bash
build_windows_release.bat
# Output: dist/KamerafallenTools.exe
```

**Size:** ~130-140MB (includes Python runtime + all dependencies)

**Details:** See [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md)

---

## 📸 Screenshots & Examples

### AI Analysis Workflow
```
Step 1: Load images folder
  ↓
Step 2: Press "Analysieren" button
  ↓  
Step 3: AI detects → "2 Bartgeier, FP1, 08.15.2025, 14:23"
  ↓
Step 4: User reviews and corrects if needed
  ↓
Step 5: Press "Bestätigen" → Saves to Excel immediately
  ↓
Step 6: Press "Bild umbenennen" → Creates backup, renames file
  ↓
Step 7: Press "Weiter" → Next image (already analyzed!)
```

### File Naming Examples
```
Before:  fotofallen_2025_0001.jpeg
After:   08.15.25-FP1-Bartgeier_2.jpeg

Before:  fotofallen_2025_0002.jpeg  
After:   07.22.25-FP2-Generl-Luisa.jpeg

Before:  fotofallen_2025_0003.jpeg
After:   08.01.25-FP3-Gämse_3-Kolkrabe.jpeg
```

### Excel Output Structure
```
Sheet: FP1
┌────┬─────────┬────────────┬──────────┬────────┬───────┬─────────────┬─────┬───────┐
│ Nr.│ Standort│ Datum      │ Uhrzeit  │ Generl │ Luisa │ Unbestimmt  │ ... │ Art 1 │
├────┼─────────┼────────────┼──────────┼────────┼───────┼─────────────┼─────┼───────┤
│  1 │ FP1     │ 22.08.2025 │ 11:52:06 │        │       │             │ ... │ 1 Rabe│
│  2 │ FP1     │ 22.08.2025 │ 09:10:34 │        │       │ ✓           │ ... │ Bartg.│
│  3 │ FP1     │ 21.08.2025 │ 18:36:53 │        │       │             │ ... │ 1 Kolk│
└────┴─────────┴────────────┴──────────┴────────┴───────┴─────────────┴─────┴───────┘

Sheet: FP2, FP3, Nische
(separate data per location)
```

---

## 🎓 Learning Resources

For developers interested in the architecture:
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Deep technical documentation
  - Rolling buffer implementation
  - Concurrent request optimization
  - Rate limit detection algorithms
  - Request staggering mechanics

---

## 📊 Project Stats

| Metric | Value |
|--------|-------|
| **Total Lines of Code** | ~4,300 lines |
| **Main Analyzer** | 2,170 lines |
| **API Module** | 348 lines |
| **I/O Module** | 473 lines |
| **Languages** | Python 3.8+ |
| **GUI Framework** | Tkinter |
| **Build Size** | ~130-140MB (standalone) |

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is open source. Feel free to modify and distribute as needed.

---

## 🙏 Acknowledgments

- **GitHub Models API** for AI-powered image analysis
- **Tkinter** for cross-platform GUI framework
- **Pandas & OpenPyXL** for Excel integration
- **Bearded Vulture research teams** for real-world testing and feedback

---

## 📮 Contact & Support

- **Issues:** https://github.com/JonathanGehret/extract_images_outlook/issues
- **Discussions:** https://github.com/JonathanGehret/extract_images_outlook/discussions

---

*Last Updated: October 2025*  
*Reflects all concurrent request optimizations and rolling buffer improvements*
