# Automated Rule Generation Workflow

## 🎯 Zero-Password Automated Pipeline

This workflow automatically discovers all app endpoints and generates LuLu rules **without requiring any passwords** (after initial sysdiag capture).

## 🚀 Quick Start

### One-Command Generation:

```bash
./generate_complete_rules.sh
```

That's it! The script will:
1. ✅ Find latest sysdiag automatically
2. ✅ Discover all app endpoints
3. ✅ Merge with existing rules
4. ✅ Apply default-deny policy
5. ✅ Copy to Desktop for import

## 📋 Detailed Workflow

### Step 1: Capture Sysdiag (One-Time, Requires Password)

```bash
# Run this once, then use the data repeatedly
sudo sysdiagnose -f ~/Desktop/

# Wait ~10 minutes, then extract
cd ~/Desktop
tar -xzf sysdiagnose_*.tar.gz
```

### Step 2: Auto-Discover Endpoints (No Password)

```bash
# Analyzes sysdiag and extracts all endpoints
python3 auto_discover_endpoints.py ~/Desktop/sysdiagnose_*/

# Output: auto_discovered_rules.json
```

**What it discovers:**
- URLs from process command lines (`ps.txt`)
- Active network connections (`netstat.txt`)
- DNS queries from logs (`logs/`)

### Step 3: Merge & Enhance (No Password)

```bash
# Merges discovered rules with your existing LuLu rules
python3 merge_and_enhance_rules.py

# Output: enhanced_lulu_rules-v7-GITHUB-FIX.json
```

**What it does:**
- Preserves all existing rules
- Adds newly discovered endpoints
- Applies default-deny policy
- Deduplicates conflicts
- Respects blocked Apple processes

### Step 4: Import to LuLu

1. Open LuLu
2. Go to Rules → Import
3. Select `enhanced_lulu_rules-*.json` from Desktop
4. Review and confirm

## 🔄 Regular Updates (No Password Ever)

```bash
# Just run the master script periodically
./generate_complete_rules.sh

# Or specify a specific sysdiag
./generate_complete_rules.sh ~/Desktop/sysdiagnose_2025.10.12*/
```

## 📊 What Gets Discovered

### From `ps.txt`:
- All URLs in command-line arguments
- API endpoints
- Server URLs
- Configuration URLs

**Example for Windsurf:**
```
https://server.self-serve.windsurf.com
https://inference.codeium.com
https://api.codeium.com
```

### From `netstat.txt`:
- Active TCP/UDP connections
- Remote IP addresses
- Port numbers
- Connection states

### From `logs/`:
- DNS queries
- Domain resolutions
- Network activity patterns

## 🎯 Benefits

### ✅ No Password Required
- After initial sysdiag capture, everything is automated
- No sudo needed for analysis
- Safe to run in CI/CD pipelines

### ✅ Comprehensive Discovery
- Finds endpoints you might miss manually
- Captures startup flows
- Discovers background services

### ✅ Repeatable
- Run as often as needed
- Consistent results
- Version-controlled rules

### ✅ Safe
- Preserves existing rules
- Respects blocked processes
- Deduplicates automatically

## 📁 File Structure

```
LuluFirewallGenerator-Public/
├── auto_discover_endpoints.py      # Endpoint discovery (no password)
├── merge_and_enhance_rules.py      # Rule merger (no password)
├── generate_complete_rules.sh      # Master automation script
├── auto_discovered_rules.json      # Auto-discovered endpoints
└── enhanced_lulu_rules-*.json      # Final output
```

## 🔍 Troubleshooting

### "No sysdiag found"
```bash
# Generate a new one
sudo sysdiagnose -f ~/Desktop/

# Or specify path manually
./generate_complete_rules.sh ~/path/to/sysdiagnose_folder/
```

### "App not working after import"
```bash
# Check what's being blocked
tail -f /Library/Logs/LuLu.log | grep BLOCK

# Re-run discovery after using the app
./generate_complete_rules.sh
```

### "Missing endpoints"
```bash
# Make sure app was running during sysdiag capture
# Run sysdiag while actively using all app features:
# - Login/authentication
# - AI features
# - Extensions
# - Updates
# - Background sync
```

## 🎨 Customization

### Add Manual Rules

Edit `merge_and_enhance_rules.py` and add to `app_connections`:

```python
"com.your.app": {
    "name": "YourApp",
    "path": "/Applications/YourApp.app",
    "type": "3",
    "endpoints": [
        ("*", "*", False, "0"),  # Block all
        ("*.yourapi.com", "443", True, "1"),  # Allow your API
    ]
}
```

### Exclude Apps

Edit `auto_discover_endpoints.py` and add to exclusion list:

```python
EXCLUDED_APPS = ['SystemApp', 'UtilityApp']
```

## 📈 Performance

- **Discovery**: ~5-10 seconds
- **Merging**: ~2-3 seconds  
- **Total**: Under 15 seconds for 100+ apps

## 🔒 Security

### What's Analyzed:
- ✅ Process lists (public info)
- ✅ Network connections (your own)
- ✅ System logs (local only)

### What's NOT Sent:
- ❌ No data leaves your machine
- ❌ No external API calls
- ❌ No telemetry

## 🎯 Real-World Example

```bash
# Day 1: Initial setup (requires password)
sudo sysdiagnose -f ~/Desktop/
# Use your apps for 10 minutes
tar -xzf ~/Desktop/sysdiagnose_*.tar.gz

# Day 1+: Generate rules (no password)
./generate_complete_rules.sh
# Import to LuLu

# Day 7: Update after new app installs (no password)
./generate_complete_rules.sh
# Import updated rules

# Day 30: Refresh after app updates (no password)
./generate_complete_rules.sh
# Import refreshed rules
```

## 💡 Pro Tips

1. **Run sysdiag during active use** - Login, use AI, sync, update
2. **Keep multiple sysdiags** - Compare over time
3. **Version control rules** - Track changes with git
4. **Test in stages** - Import for one app at a time
5. **Monitor logs** - Watch for blocked connections

## 🚀 Next Steps

1. Run `./generate_complete_rules.sh`
2. Review generated rules
3. Import to LuLu
4. Test Windsurf (and all apps)
5. Re-run if needed (no password!)

---

**Generated**: October 2025  
**Version**: 2.0 - Automated Pipeline  
**License**: MIT
