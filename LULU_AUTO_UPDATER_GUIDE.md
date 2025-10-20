# 🚀 LuLu Auto-Updater Guide

## What This Does

**Automatically updates your LuLu firewall rules in real-time when it detects package installs!**

### The Magic:

```
1. You run: pip install requests
2. Auto-updater detects pip3 process
3. Adds temporary ALLOW rules to LuLu:
   - pypi.org:443
   - github.com:443
   - files.pythonhosted.org:443
4. Install completes
5. Rules automatically removed after 5 minutes
```

**No more manual clicking!** 🎉

## Safety Features

✅ **Automatic backup** - Creates backup before any changes
✅ **Temporary rules** - Auto-removed after 5 minutes
✅ **Process monitoring** - Only triggers on actual installs
✅ **Specific endpoints** - No wildcards (*:*)
✅ **Cleanup on exit** - Removes all temp rules when stopped

## How to Use

### Step 1: Start the Auto-Updater

```bash
sudo python3 lulu_auto_updater.py
```

You'll see:
```
🛡️  LULU AUTO-UPDATER
======================================================================
This will AUTOMATICALLY update LuLu rules when actions are detected
======================================================================

⚠️  WARNING: This modifies your LuLu rules in real-time!
⚠️  A backup will be created before any changes

Continue? (yes/no):
```

Type `yes` and press Enter.

### Step 2: Use Your Apps Normally

The auto-updater is now monitoring. When you:

**Install Python package:**
```bash
pip install requests
```

**Install npm package:**
```bash
npm install lodash
```

**Clone git repo:**
```bash
git clone https://github.com/user/repo
```

The auto-updater will:
1. 🎯 Detect the process
2. ✅ Add temporary ALLOW rules
3. ⏱️ Remove them automatically

### Step 3: Stop When Done

Press `Ctrl+C` to stop the auto-updater.

It will automatically clean up all temporary rules.

## What You'll See

### When Detection Happens:

```
[2025-10-19T20:35:00] [DETECT] 🎯 DETECTED: python_install - Windsurf spawned pip3 (PID: 12345)
[2025-10-19T20:35:00] [INFO] Adding temporary rule: Windsurf → pypi.org:443
[2025-10-19T20:35:01] [SUCCESS] ✅ Added rule (expires in 300s)
[2025-10-19T20:35:01] [INFO] Adding temporary rule: Windsurf → github.com:443
[2025-10-19T20:35:02] [SUCCESS] ✅ Added rule (expires in 300s)
[2025-10-19T20:35:02] [INFO] Restarted LuLu
```

### When Rules Expire:

```
[2025-10-19T20:40:00] [INFO] Removing temporary rule: pypi.org:443
[2025-10-19T20:40:01] [SUCCESS] 🧹 Removed temporary rule
[2025-10-19T20:40:01] [INFO] Restarted LuLu
```

## Backup & Recovery

### Backups Location

All backups are stored in: `~/.lulu_auto_updater/`

```
~/.lulu_auto_updater/
├── rules_backup_20251019_203500.plist
├── rules_backup_20251019_204500.plist
└── updater.log
```

### Restore from Backup

If something goes wrong:

```bash
# List backups
ls -lt ~/.lulu_auto_updater/rules_backup_*.plist

# Restore a backup
sudo cp ~/.lulu_auto_updater/rules_backup_TIMESTAMP.plist /Library/Objective-See/LuLu/rules.plist

# Restart LuLu
killall LuLu && open -a LuLu
```

## Supported Actions

### Python Package Install
**Triggers**: pip, pip3, python, python3
**Parent Apps**: Windsurf, VSCode, PyCharm
**Allows**:
- pypi.org:443
- files.pythonhosted.org:443
- github.com:443
- raw.githubusercontent.com:443
**Duration**: 5 minutes

### NPM Package Install
**Triggers**: npm, yarn, pnpm
**Parent Apps**: Windsurf, VSCode, WebStorm
**Allows**:
- registry.npmjs.org:443
- github.com:443
- raw.githubusercontent.com:443
**Duration**: 5 minutes

### Git Clone
**Triggers**: git
**Parent Apps**: Windsurf, VSCode, Terminal
**Allows**:
- github.com:443
- gitlab.com:443
- bitbucket.org:443
**Duration**: 3 minutes

## Comparison

### Before (Manual):
```
1. Run pip install
2. LuLu blocks → Click "Allow" → Creates *:* wildcard
3. LuLu blocks → Click "Allow" → Creates *:* wildcard
4. LuLu blocks → Click "Allow" → Creates *:* wildcard
5. Manually go back and remove rules
6. Hope you didn't forget any

Time: 2-5 minutes
Risk: Wildcards, might forget to remove
```

### After (Auto-Updater):
```
1. Run pip install
2. Auto-updater adds specific rules
3. Install completes
4. Rules auto-removed

Time: 0 seconds
Risk: None, guaranteed cleanup
```

## Troubleshooting

### "Permission denied"
```bash
# Must run with sudo
sudo python3 lulu_auto_updater.py
```

### "LuLu rules file not found"
```bash
# LuLu might not be installed or rules don't exist yet
# The auto-updater will create a new rules file
```

### Rules not being added
```bash
# Check if LuLu is running
ps aux | grep LuLu

# Check logs
tail -f ~/.lulu_auto_updater/updater.log
```

### LuLu keeps restarting
```bash
# This is normal - LuLu must restart to reload rules
# Each rule addition triggers one restart
```

## Advanced Usage

### Custom Duration

Edit `lulu_auto_updater.py` and modify:

```python
'duration': 300  # Change to desired seconds
```

### Add New Actions

Add to `action_patterns`:

```python
'rust_build': {
    'processes': ['cargo'],
    'parent_apps': ['Windsurf', 'VSCode'],
    'endpoints': [
        ('crates.io', '443'),
        ('github.com', '443')
    ],
    'duration': 600
}
```

## Safety Tips

1. **Start with safe demo first** to understand behavior
2. **Keep backups** - they're created automatically
3. **Monitor the logs** - watch what's being added/removed
4. **Test with non-critical apps** first
5. **Keep LuLu's UI open** to see rule changes

## Logs

All activity is logged to: `~/.lulu_auto_updater/updater.log`

```bash
# Watch logs in real-time
tail -f ~/.lulu_auto_updater/updater.log

# Search logs
grep "DETECT" ~/.lulu_auto_updater/updater.log
```

## Stopping the Auto-Updater

Press `Ctrl+C` - it will:
1. Stop monitoring
2. Remove all temporary rules
3. Restore LuLu to pre-monitoring state

## Next Steps

After testing with the auto-updater, you might want to:

1. **Generate permanent rules** from learned patterns
2. **Share your action patterns** with the community
3. **Customize durations** based on your workflow
4. **Add new action types** for your specific tools

## Questions?

- Check logs: `~/.lulu_auto_updater/updater.log`
- Review backups: `~/.lulu_auto_updater/`
- Test in safe demo mode first: `python3 safe_demo_mode.py`
