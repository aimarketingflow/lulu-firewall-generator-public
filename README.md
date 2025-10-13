# LuLu Custom Firewall Generator

🛡️ **Automated port-specific firewall rules for macOS**

**The Problem:** LuLu creates wildcard rules (`ALLOW *:*`) when you click "Allow" - meaning apps can connect anywhere.

**Our Solution:** Analyze system diagnostics → Generate specific endpoint rules → 95% attack surface reduction.

**Result:** Apps limited to discovered endpoints only, not unlimited network access.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-macOS-lightgrey.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)

> **📖 [Read the full story](about.html)** - Learn how and why this tool was created from a real-world security investigation
> 
> **🔍 [How LuLu Works](HOW_LULU_WORKS.md)** - Understanding LuLu's wildcard behavior and why our tool is necessary

---

## 🌟 Key Features

- **🎯 Replaces Wildcards with Specific Endpoints**: LuLu's `*:*` → Our `github.com:443`
- **📊 Automated Discovery**: Extract endpoints from sysdiagnose (no manual analysis)
- **🛡️ Default-Deny Security**: BLOCK `*:*` + ALLOW specific endpoints only
- **🔄 Two-Phase Protection**: Permissive startup → Restrictive runtime
- **🌐 Port-Specific Rules**: 90-95% attack surface reduction vs manual LuLu
- **📊 Live System Monitoring**: Capture and analyze running processes in real-time
- **🔍 Sysdiag Parser**: Extract 40+ connections from system diagnostics automatically
- **🛠️ App-Specific Templates**: Pre-configured rules for Safari, Windsurf, Slack, Mail
- **🚫 Telemetry Blocker**: Auto-block analytics, tracking, and telemetry domains
- **📁 Multiple Export Formats**:
  - **LuLu Format**: Compact single-line JSON for LuLu firewall
  - **Murus Format**: Pretty-printed JSON for Murus firewall
- **🖥️ Beautiful GUI**: Modern PyQt6 interface with dark theme
- **⚡ CLI Support**: Command-line interface for automation
- **💾 Configuration Management**: Save and load firewall configurations
- **📚 Complete Documentation**: Step-by-step guides, security hardening, and best practices

## 🚀 Quick Start

### Prerequisites

- macOS 10.15 or later
- Python 3.8+
- PyQt6 (for GUI)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/aimarketingflow/Lulu-custom-firewall-generator.git
cd Lulu-custom-firewall-generator
```

2. **Install dependencies**
```bash
pip3 install PyQt6
```

3. **Launch the GUI**
```bash
python3 enhanced_gui_v2.py
```

Or use the CLI:
```bash
python3 cli_generator.py
```

## 📖 Usage

### GUI Mode (Recommended)

1. **Launch the application**
   ```bash
   python3 enhanced_gui_v2.py
   ```

2. **Choose your data source**:
   - **Live Capture**: Click "📡 Capture Live" to scan running processes
   - **Load Diagnostics**: Import existing spindump or diagnostic files

3. **Select your mode**:
   - **🌐 Online Mode**: Allow selected apps to access the internet
   - **🔒 Offline Mode**: Complete air-gapped security (no internet)

4. **Select applications**:
   - Check the apps you want to allow internet access
   - Use the filter box to search for specific apps
   - Click "Select All" or "Deselect All" for quick selection

5. **Generate rules**:
   - Click "🛡️ Generate Murus Rules"
   - Review the live preview and threat analysis

6. **Export**:
   - Click "📁 Export (LuLu)" for LuLu firewall format
   - Click "📁 Export (Murus)" for Murus firewall format

7. **Import into your firewall**:
   - Open LuLu or Murus
   - Import the generated JSON file
   - Enable the rules

### CLI Mode

```bash
python3 cli_generator.py
```

The CLI will:
1. Discover installed applications
2. Generate rules for demo apps (Safari, Windsurf, or first 2 apps)
3. Export both LuLu and Murus formats automatically

## 🎯 Use Cases

### 🔐 Maximum Security (Offline Mode)
Perfect for:
- Working with sensitive data
- Air-gapped environments
- Preventing all data exfiltration
- Maximum privacy protection

**What it does**: Blocks ALL internet access except local network communication

### 🌐 Selective Access (Online Mode)
Perfect for:
- Daily work with specific apps
- Blocking telemetry and analytics
- Preventing cloud sync services
- Allowing only trusted applications

**What it does**: Allows only your selected apps to access the internet

## 📊 What Gets Blocked?

The tool automatically identifies and blocks:

- ☁️ Cloud sync services (iCloud, Dropbox, etc.)
- 📊 Analytics and telemetry
- 🔄 Auto-update services
- 📱 Background app services
- 🌐 Browser helper processes
- 🔍 Search and indexing services
- And many more potential exfiltration vectors

## 🛠️ Advanced Features

### Configuration Management
- **Save configurations**: Store your app selections and mode preferences
- **Load configurations**: Quickly switch between different security profiles
- **Export configurations**: Share setups across machines

### Live System Monitoring
- Real-time process capture
- Network process detection
- App relationship mapping
- Process categorization

### Rule Preview
- View generated rules before export
- See exactly what will be allowed/blocked
- Threat analysis summary
- Rule count and breakdown

## 📚 Documentation

### Getting Started
- **[Quick Start Guide](QUICKSTART.md)** - Get up and running in 5 minutes
- **[Interactive HTML Setup](setup-guide.html)** - Beautiful step-by-step visual guide
- **[Quick Reference](QUICK_REFERENCE.md)** - Cheat sheet for common tasks

### Security Guides
- **[macOS Security Hardening Guide](MACOS_SECURITY_HARDENING_GUIDE.md)** - Complete security setup
  - LuLu + Murus configuration
  - Activity Monitor as Wireshark alternative
  - Apple ID security considerations
  - Recommended block rules
- **[Step-by-Step: Adding Rules](STEP_BY_STEP_LULU_RULES.md)** - Visual guide with screenshots
  - Monitor network activity
  - Create firewall rules
  - Use Activity Monitor effectively

### Technical Documentation
- **[Port-Specific Rules Summary](PORT_SPECIFIC_RULES_SUMMARY.md)** - Complete technical guide
- **[Manual Port Discovery](MANUAL_PORT_DISCOVERY_GUIDE.md)** - Manual discovery methods
- **[LuLu Format Update](LULU_FORMAT_UPDATE.md)** - Format specifications

### Project Information
- **[About This Project](ABOUT.md)** - Origin story and motivation
- **[File Structure](FILE_STRUCTURE.md)** - Complete file organization
- **[Launch Checklist](LAUNCH_CHECKLIST.md)** - For contributors

## 📁 File Structure

```
lulu-firewall-generator/
├── enhanced_gui_v2.py                    # Main GUI application
├── cli_generator.py                      # Command-line interface
├── create_app_specific_rules.py          # Generate port-specific rules
├── sysdiag_connection_parser.py          # Parse sysdiagnose files
├── rule_generator.py                     # Core rule generation logic
├── app_analyzer.py                       # Application discovery
├── diagnostic_parser.py                  # Parse system diagnostics
├── system_monitor.py                     # Live system monitoring
├── setup-guide.html                      # Interactive HTML guide
└── README.md                             # This file
```

## 🔧 Technical Details

### LuLu Format
The tool generates LuLu-compatible rules with all required fields:
- `key`: Process identifier
- `uuid`: Unique rule identifier
- `path`: Full executable path
- `name`: Process name
- `endpointAddr`: Destination address
- `creation`: Timestamp with timezone
- `endpointPort`: Destination port
- `isEndpointAddrRegex`: Regex flag
- `type`: Rule type (1=allow, 3=block)
- `scope`: Rule scope
- `action`: Action to take (0=allow, 1=block)

### Murus Format
Pretty-printed JSON with metadata:
- Rule versioning
- Generation timestamp
- Rule count and statistics
- Detailed rule descriptions

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.
## ⚠️ Disclaimer

This tool is provided as-is for educational and security purposes. Always test firewall rules in a safe environment before deploying to production systems. The authors are not responsible for any system issues or data loss resulting from the use of this tool.

## 🙏 Acknowledgments & Support

This project wouldn't exist without:
- **[LuLu Firewall](https://objective-see.org/products/lulu.html)** by [Objective-See Foundation](https://objective-see.org/) (Patrick Wardle) - The amazing open-source firewall that inspired this tool
- **[Murus Firewall](https://www.murusfirewall.com/)** - Alternative firewall support
- **The macOS Security Community** - For sharing knowledge and tools
- **Privacy Advocates** - For fighting for user rights

### 💚 Support LuLu's Development

Patrick Wardle and the Objective-See Foundation create free, open-source macOS security tools. If you find this rule generator useful, please consider supporting their work:

- **[💚 Support on Patreon](https://www.patreon.com/objective_see)** - Become a patron of Patrick Wardle
- **[🏛️ Objective-See Foundation](https://objective-see.org/)** - 501(c)(3) Non-Profit organization
- **[📥 Download LuLu](https://objective-see.org/products/lulu.html)** - Get the free, open-source firewall

*This is an independent community project. Not affiliated with Objective-See Foundation.*
