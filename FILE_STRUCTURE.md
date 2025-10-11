# LuLu Firewall Generator - File Structure

## 📁 Core Tools

### Port-Specific Rule Generation
- **`create_app_specific_rules.py`** - Generate curated port-specific rules for common apps
- **`sysdiag_connection_parser.py`** - Parse sysdiagnose files to extract network connections
- **`rule_generator.py`** - Core rule generation engine

### GUI Applications
- **`enhanced_gui_v2.py`** - Main PyQt6 GUI application
- **`simple_gui.py`** - Simplified GUI interface
- **`launch.py`** - Application launcher

### Analysis Tools
- **`app_analyzer.py`** - Analyze installed applications
- **`diagnostic_parser.py`** - Parse system diagnostic files
- **`system_monitor.py`** - Monitor system network activity
- **`cli_generator.py`** - Command-line interface for rule generation

### Testing
- **`test_gui.py`** - GUI testing utilities
- **`test_lulu_export.py`** - Test LuLu export functionality

## 📚 Documentation

### Setup & Guides
- **`README.md`** - Main project documentation
- **`QUICKSTART.md`** - Quick start guide
- **`setup-guide.html`** - Interactive HTML setup guide
- **`MANUAL_PORT_DISCOVERY_GUIDE.md`** - Manual port discovery instructions
- **`QUICK_REFERENCE.md`** - Quick reference card

### Technical Documentation
- **`PORT_SPECIFIC_RULES_SUMMARY.md`** - Complete port-specific rules documentation
- **`LULU_FORMAT_UPDATE.md`** - LuLu format specifications
- **`ABOUT.md`** - About the project

### Marketing
- **`LINKEDIN_POST.md`** - LinkedIn announcement (3 versions)
- **`about.html`** - Project about page (HTML)

## 🔧 Configuration

- **`requirements.txt`** - Python dependencies
- **`LICENSE`** - MIT License
- **`.gitignore`** - Git ignore rules

## 🎯 Key Features

1. **Port-Specific Filtering** - 90% attack surface reduction
2. **Sysdiag Parsing** - Extract 40+ connections automatically
3. **App Templates** - Pre-configured rules for Safari, Windsurf, Slack, Mail
4. **Telemetry Blocking** - Auto-block analytics and tracking
5. **Interactive GUI** - Beautiful PyQt6 interface
6. **Complete Documentation** - Guides for all skill levels

## 🚀 Quick Start

```bash
# Generate port-specific rules
python3 create_app_specific_rules.py

# Launch GUI
python3 enhanced_gui_v2.py

# Parse sysdiagnose
python3 sysdiag_connection_parser.py
```

## 📦 Ready for Public Release

All files are production-ready and documented.
No sensitive data or private information included.
