# Quick Start Guide

## 🚀 Get Started in 3 Minutes

### Step 1: Install Dependencies

```bash
# Install Python dependencies
pip3 install PyQt6
```

### Step 2: Launch the Application

```bash
# Clone and run
git clone https://github.com/aimarketingflow/Lulu-custom-firewall-generator.git
cd Lulu-custom-firewall-generator
python3 enhanced_gui_v2.py
```

### Step 3: Generate Your First Ruleset

1. **Click "📡 Capture Live"** to scan your running processes
2. **Choose your security mode**:
   - 🌐 **Online Mode**: For normal work (allows selected apps)
   - 🔒 **Offline Mode**: For maximum security (blocks everything)
3. **Select apps** you want to allow (e.g., Safari, Chrome, Slack)
4. **Click "🛡️ Generate Murus Rules"**
5. **Click "📁 Export (LuLu)"** to save the rules

### Step 4: Import into LuLu

1. Open **LuLu** firewall application
2. Go to **Rules** → **Import**
3. Select your generated `lulu_rules_*.json` file
4. Enable the rules
5. Done! 🎉

## 💡 Pro Tips

### Create a Desktop Shortcut (macOS)

```bash
# Create launcher script
cat > ~/Desktop/FirewallGenerator.command << 'EOF'
#!/bin/bash
cd ~/lulu-custom-firewall-generator
python3 enhanced_gui_v2.py
EOF

# Make it executable
chmod +x ~/Desktop/FirewallGenerator.command
```

Now you can double-click `FirewallGenerator.command` to launch!

### Common Use Cases

#### 🔐 Maximum Privacy Mode
1. Select **Offline Mode**
2. Don't select any apps
3. Generate rules
4. Result: Complete internet lockdown

#### 🌐 Work Mode
1. Select **Online Mode**
2. Select: Safari, Slack, Zoom, Mail
3. Generate rules
4. Result: Only work apps can access internet

#### 🎮 Gaming Mode
1. Select **Online Mode**
2. Select: Steam, Discord, your game
3. Generate rules
4. Result: Only gaming apps online

### Keyboard Shortcuts

- **⌘+A**: Select all apps
- **⌘+D**: Deselect all apps
- **⌘+F**: Focus filter box
- **⌘+G**: Generate rules
- **⌘+E**: Export rules

## 🆘 Troubleshooting

### "No processes found"
- Make sure you have apps running before capturing
- Try running with `sudo` for better process visibility

### "PyQt6 not found"
```bash
pip3 install --upgrade PyQt6
```

### "Permission denied"
```bash
chmod +x enhanced_gui_v2.py
```

## 📚 Next Steps

- Read the full [README.md](README.md) for advanced features
- Check [LULU_FORMAT_UPDATE.md](LULU_FORMAT_UPDATE.md) for technical details
- Experiment with different security modes
- Save configurations for quick switching

## 🎯 Example Workflow

```bash
# 1. Clone the repo
git clone https://github.com/aimarketingflow/Lulu-custom-firewall-generator.git
cd Lulu-custom-firewall-generator

# 2. Install dependencies
pip3 install -r requirements.txt

# 3. Run the GUI
python3 enhanced_gui_v2.py

# 4. Or use CLI for automation
python3 cli_generator.py
```

That's it! You're now ready to create custom firewall rules! 🛡️
