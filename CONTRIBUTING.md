# Contributing to Kamerafallen-Tools

First off, thank you for considering contributing to Kamerafallen-Tools! 🎉

This project was created to support wildlife conservation research, and your contributions help make wildlife monitoring more accessible and efficient.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Pull Request Process](#pull-request-process)
- [Project Structure](#project-structure)

---

## 🤝 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all. Please be respectful and constructive in your interactions.

### Expected Behavior

- ✅ Be respectful and inclusive
- ✅ Welcome newcomers and help them learn
- ✅ Focus on what is best for the community
- ✅ Show empathy towards other community members

### Unacceptable Behavior

- ❌ Harassment, discrimination, or offensive comments
- ❌ Trolling, insulting, or derogatory comments
- ❌ Publishing others' private information
- ❌ Other conduct which could reasonably be considered inappropriate

---

## 💡 How Can I Contribute?

### Reporting Bugs

**Before submitting a bug report:**
1. Check the [debug log](#debugging) at `~/.kamerafallen-tools/analyzer_debug.log`
2. Search existing [Issues](https://github.com/JonathanGehret/extract_images_outlook/issues) to avoid duplicates
3. Try to isolate the problem and provide minimal reproduction steps

**When submitting a bug report, include:**
- Clear, descriptive title
- Steps to reproduce the behavior
- Expected vs. actual behavior
- Screenshots (if applicable)
- Environment details:
  - OS (Linux, Windows, macOS)
  - Python version (`python --version`)
  - Relevant debug log excerpts
- Sample files (if applicable, but NO sensitive data)

### Suggesting Enhancements

**Enhancement suggestions are welcome for:**
- New species recognition
- UI/UX improvements
- Performance optimizations
- Documentation improvements
- New features

**When suggesting enhancements:**
- Use a clear, descriptive title
- Explain the current limitation
- Describe the proposed solution
- Explain why this would be useful
- Include mockups or examples if applicable

### Contributing Code

**Areas that need contributions:**
1. **Species Detection**
   - Add new animal species to recognition list
   - Improve species name normalization
   - Add multilingual species names

2. **UI/UX**
   - Improve accessibility
   - Add keyboard shortcuts
   - Enhance visual design
   - Improve error messages

3. **Documentation**
   - Translate docs to other languages
   - Add tutorials and examples
   - Improve API documentation
   - Create video guides

4. **Testing**
   - Add unit tests
   - Add integration tests
   - Improve test coverage

5. **Performance**
   - Optimize image processing
   - Improve API rate limit handling
   - Reduce memory usage

---

## 🛠️ Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/extract_images_outlook.git
cd extract_images_outlook
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Create `.env` file:
```env
GITHUB_MODELS_TOKEN=ghp_your_token_here
ANALYZER_IMAGES_FOLDER=/path/to/test/images
ANALYZER_OUTPUT_EXCEL=/path/to/test/output.xlsx
```

### 5. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/issue-123
```

### 6. Make Your Changes

- Follow [coding standards](#coding-standards)
- Test thoroughly
- Update documentation
- Add comments for complex logic

### 7. Test Your Changes

```bash
# Test main analyzer
python github_models_analyzer.py

# Test email extractor
python extract_img_email.py

# Test with dummy data (no API token needed)
# Use "Testdaten verwenden" checkbox in GUI
```

### 8. Commit Your Changes

```bash
git add .
git commit -m "feat: add new species detection for Adler"
```

**Commit message format:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style/formatting (no logic change)
- `refactor:` Code refactoring
- `test:` Adding tests
- `chore:` Maintenance tasks

---

## 📐 Coding Standards

### Python Style

Follow **PEP 8** guidelines:

```python
# Good
def analyze_image(image_path, token, species_list):
    """Analyze camera trap image using AI.
    
    Args:
        image_path: Path to image file
        token: GitHub Models API token
        species_list: List of expected species
        
    Returns:
        dict: Analysis results with species, location, date
    """
    # Implementation
    pass

# Avoid
def img_analyze(img,t,spl): # No docstring, unclear names
    pass
```

### Code Organization

1. **Imports**: Organized in blocks
   ```python
   # Standard library
   import os
   import sys
   
   # Third-party
   import pandas as pd
   from PIL import Image
   
   # Local
   import github_models_api as gm_api
   ```

2. **Functions**: Single responsibility, clear naming
3. **Classes**: Follow established patterns (see `ImageAnalyzer`)
4. **Comments**: Explain WHY, not WHAT
   ```python
   # Good: Explains reasoning
   # Use LANCZOS resampling to preserve image quality for AI analysis
   image.thumbnail((500, 400), Image.Resampling.LANCZOS)
   
   # Avoid: States the obvious
   # Resize the image
   image.thumbnail((500, 400), Image.Resampling.LANCZOS)
   ```

### German UI Text

All user-facing text should be in **German**:
```python
# Good
messagebox.showerror("Fehler", "Bitte geben Sie einen gültigen Standort ein")

# Avoid
messagebox.showerror("Error", "Please enter valid location")
```

### Error Handling

Always handle errors gracefully:
```python
try:
    result = analyze_image(path)
except FileNotFoundError:
    logger.error(f"Image not found: {path}")
    messagebox.showerror("Fehler", "Bild nicht gefunden")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    messagebox.showerror("Fehler", f"Ein Fehler ist aufgetreten: {e}")
```

---

## 🔄 Pull Request Process

### Before Submitting

1. ✅ **Test thoroughly** with real data (if possible)
2. ✅ **Update documentation** (README, docstrings, comments)
3. ✅ **Check code style** (follow PEP 8)
4. ✅ **Verify no sensitive data** (tokens, personal info) in commits
5. ✅ **Update CHANGELOG** (if applicable)

### PR Guidelines

1. **Title**: Clear, concise description
   - Good: `feat: Add Gämse species detection with count validation`
   - Avoid: `Update analyzer.py`

2. **Description**: Include:
   - What changed and why
   - Related issue numbers (`Fixes #123`)
   - Screenshots (for UI changes)
   - Testing performed
   - Breaking changes (if any)

3. **Size**: Keep PRs focused and reasonably sized
   - One feature/fix per PR
   - Split large changes into multiple PRs

4. **Review**: Be responsive to feedback
   - Address reviewer comments
   - Make requested changes
   - Ask questions if unclear

### PR Template

```markdown
## Description
Brief description of changes

## Related Issues
Fixes #123

## Changes Made
- Added X feature
- Fixed Y bug
- Updated Z documentation

## Testing
- [ ] Tested with real camera trap images
- [ ] Tested with dummy data
- [ ] Verified Excel output
- [ ] Checked UI responsiveness

## Screenshots (if applicable)
[Add screenshots]

## Breaking Changes
None / [Describe breaking changes]
```

### Review Process

1. Maintainer reviews your PR
2. Feedback/changes requested (if needed)
3. You make updates
4. Approval and merge
5. Your contribution is live! 🎉

---

## 📁 Project Structure

Understanding the codebase:

```
extract_images_outlook/
├── main_gui.py                    # Entry point - launcher GUI
├── github_models_analyzer.py      # Main analyzer (2400+ lines)
│   ├── AnalysisBuffer class       # Async API handling
│   └── ImageAnalyzer class        # Main GUI logic
├── github_models_api.py           # API communication
│   ├── analyze_image()            # Core AI analysis
│   └── Rate limit handling
├── github_models_io.py            # File operations
│   ├── Excel read/write
│   ├── Image renaming
│   └── Backup management
├── extract_img_email.py           # Email extractor
└── rename_images_from_excel.py    # Batch renamer
```

### Key Components

**ImageAnalyzer** (`github_models_analyzer.py`):
- Lines 738-2340: Main GUI class
- Lines 745-895: UI setup
- Lines 1250-1400: Image loading/navigation
- Lines 1450-1600: AI analysis integration
- Lines 2090-2230: Fullscreen viewer

**API Layer** (`github_models_api.py`):
- API communication
- Rate limit detection
- Error handling

**I/O Layer** (`github_models_io.py`):
- Excel operations
- File management
- Backup system

---

## 🧪 Testing Guidelines

### Manual Testing Checklist

When testing changes:

- [ ] **Email Extractor**
  - [ ] Extract from `.msg` files
  - [ ] Verify sequential naming
  - [ ] Check zero-padding

- [ ] **Analyzer**
  - [ ] AI analysis works (or dummy data)
  - [ ] Dropdown menus populate
  - [ ] Date/time pickers functional
  - [ ] Excel save successful
  - [ ] Image rename works
  - [ ] Fullscreen viewer (zoom/pan)
  - [ ] Navigation (next/previous)
  - [ ] Buffer system (pre-analysis)

- [ ] **Edge Cases**
  - [ ] Empty folders
  - [ ] Corrupted images
  - [ ] API rate limits
  - [ ] Excel file locked
  - [ ] Missing token

### Automated Tests

Currently, the project uses manual testing. **Adding automated tests is a welcomed contribution!**

Suggested test framework: `pytest`

---

## 📖 Documentation Guidelines

### Code Documentation

```python
def analyze_image(image_path: str, token: str, species_list: list) -> dict:
    """Analyze camera trap image using GitHub Models API.
    
    Sends image to GPT-4o for species detection, location identification,
    and metadata extraction. Handles rate limits and retries automatically.
    
    Args:
        image_path: Absolute path to image file (JPEG/PNG)
        token: GitHub Models API token with Models permission
        species_list: List of expected species names for prompt context
        
    Returns:
        dict: Analysis results containing:
            - location (str): Camera trap location (FP1/FP2/FP3/Nische)
            - date (str): Date in DD.MM.YYYY format
            - time (str): Time in HH:MM:SS format
            - animals (str): Detected species with counts
            - confidence (float): AI confidence score (0-1)
            
    Raises:
        FileNotFoundError: If image_path doesn't exist
        RateLimitError: If API rate limit exceeded (auto-retries)
        APIError: If API returns error response
        
    Example:
        >>> result = analyze_image('/path/image.jpg', token, ['Bartgeier'])
        >>> print(result['animals'])
        '2 Bartgeier, 1 Gämse'
    """
```

### README Updates

When adding features, update:
1. Feature list
2. Usage examples
3. Configuration options
4. Screenshots (if UI changed)

---

## 🎯 Priority Areas

Current focus areas (as of November 2025):

1. **High Priority**
   - 🧪 Add automated tests
   - 🌍 Internationalization (English UI option)
   - 📱 Improve mobile/small screen support

2. **Medium Priority**
   - 🐛 Bug fixes and stability
   - 📊 Export formats (CSV, JSON)
   - 🔍 Search/filter in Excel output

3. **Low Priority**
   - 🎨 Theme customization
   - 📈 Statistics dashboard
   - 🔌 Plugin system

---

## 🆘 Getting Help

- **Questions**: Open a [Discussion](https://github.com/JonathanGehret/extract_images_outlook/discussions)
- **Bugs**: File an [Issue](https://github.com/JonathanGehret/extract_images_outlook/issues)
- **Feature Requests**: Open an [Issue](https://github.com/JonathanGehret/extract_images_outlook/issues) with `enhancement` label

---

## 📜 License

By contributing, you agree that your contributions will be licensed under the **CC BY-NC 4.0 License** (same as the project).

For commercial use of your contributions, the project maintainer reserves the right to dual-license.

---

## 🙏 Acknowledgments

Thank you to all contributors who help make this project better!

- Wildlife researchers providing feedback
- Developers improving the codebase
- Translators making it accessible
- Bug reporters helping us improve quality

**Your contributions matter!** 🌟

---

<p align="center">
  <sub>Together we're making wildlife conservation more accessible</sub>
</p>
