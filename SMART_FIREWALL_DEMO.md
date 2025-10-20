# 🎯 Smart Adaptive Firewall - Demo Guide

## The Scenario

**Problem**: Windsurf needs to install Python packages, but your firewall blocks GitHub and PyPI.

**Old Solution**: Manually allow GitHub/PyPI permanently (security risk)

**Our Solution**: Automatically detect package install, temporarily allow, lock back down!

## How It Works

```
1. Windsurf spawns pip3 process
2. Our firewall detects it instantly
3. Temporarily allows:
   - pypi.org:443
   - files.pythonhosted.org:443
   - github.com:443
   - raw.githubusercontent.com:443
4. pip3 completes installation
5. Firewall automatically locks back down
```

## Test Mode Demo

```bash
$ python3 smart_adaptive_firewall.py --test

🛡️  SMART ADAPTIVE FIREWALL
======================================================================

🧪 TEST MODE: Simulating Python package install

🎯 DETECTED: python_install - Windsurf spawned pip3 (PID: 12345)
⏰ Temporarily allowing 4 endpoints for 300s

  ✅ ALLOW: Windsurf → pypi.org:443 (expires in 300s)
  📝 PF Rule: pass out proto tcp from any to pypi.org port 443
  
  ✅ ALLOW: Windsurf → files.pythonhosted.org:443 (expires in 300s)
  📝 PF Rule: pass out proto tcp from any to files.pythonhosted.org port 443
  
  ✅ ALLOW: Windsurf → github.com:443 (expires in 300s)
  📝 PF Rule: pass out proto tcp from any to github.com port 443
  
  ✅ ALLOW: Windsurf → raw.githubusercontent.com:443 (expires in 300s)
  📝 PF Rule: pass out proto tcp from any to raw.githubusercontent.com port 443

✅ Process 12345 completed, cleaning up early
  🧹 Removed: Windsurf → pypi.org:443
  🧹 Removed: Windsurf → files.pythonhosted.org:443
  🧹 Removed: Windsurf → github.com:443
  🧹 Removed: Windsurf → raw.githubusercontent.com:443

======================================================================
🛡️  SMART ADAPTIVE FIREWALL STATUS
======================================================================

📊 Active Temporary Allows: 0
🎯 Detected Actions: 1

Recent Detections:
  • python_install: Windsurf → pip3 (PID 12345)

✅ Test complete!
```

## Real-World Usage

### Step 1: Start Monitoring

```bash
$ sudo python3 smart_adaptive_firewall.py

Options:
  1. Start monitoring (real-time)
  2. Test mode (simulate detection)
  3. Show status
  4. Exit

Select option: 1

🔍 Starting real-time monitoring...
⚠️  Try installing a Python package in Windsurf to test!
```

### Step 2: Trigger Action in Windsurf

In Windsurf terminal:
```bash
pip install requests
```

### Step 3: Watch the Magic

```
🎯 DETECTED: python_install - Windsurf spawned pip3 (PID: 54321)
⏰ Temporarily allowing 4 endpoints for 300s

  ✅ ALLOW: Windsurf → pypi.org:443
  ✅ ALLOW: Windsurf → files.pythonhosted.org:443
  ✅ ALLOW: Windsurf → github.com:443
  ✅ ALLOW: Windsurf → raw.githubusercontent.com:443

# Package installs successfully...

✅ Process 54321 completed, cleaning up early
  🧹 Removed all temporary allows
```

## Supported Actions

### Python Package Install
**Detects**: `pip`, `pip3`, `python`, `python3`
**Parent Apps**: Windsurf, VSCode, PyCharm
**Allows**:
- pypi.org:443
- files.pythonhosted.org:443
- github.com:443
- raw.githubusercontent.com:443

**Duration**: 5 minutes (or until process completes)

### NPM Package Install
**Detects**: `npm`, `yarn`, `pnpm`
**Parent Apps**: Windsurf, VSCode, WebStorm
**Allows**:
- registry.npmjs.org:443
- github.com:443
- raw.githubusercontent.com:443

**Duration**: 5 minutes

### Git Clone
**Detects**: `git`
**Parent Apps**: Windsurf, VSCode, Terminal
**Allows**:
- github.com:443
- gitlab.com:443
- bitbucket.org:443

**Duration**: 3 minutes

## Architecture

### Detection Flow

```
┌─────────────────────────────────────┐
│  Process Monitor (every 1 second)   │
│  - Scans for new processes          │
│  - Checks against patterns          │
│  - Identifies parent app            │
└─────────────────────────────────────┘
                 ↓
        [Match Found?]
                 ↓
┌─────────────────────────────────────┐
│  Action Handler                     │
│  - Logs detection                   │
│  - Temporarily allows endpoints     │
│  - Starts completion monitor        │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│  Firewall Rule Application          │
│  - Generates PF rules               │
│  - Applies to packet filter         │
│  - Sets expiry timer                │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│  Completion Monitor                 │
│  - Watches process                  │
│  - Detects completion               │
│  - Removes rules early              │
└─────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│  Cleanup Thread (every 10 seconds)  │
│  - Checks for expired rules         │
│  - Removes stale allows             │
│  - Logs cleanup actions             │
└─────────────────────────────────────┘
```

### Process Monitoring

**With psutil** (recommended):
```python
for proc in psutil.process_iter(['pid', 'name', 'ppid']):
    # Efficient, real-time monitoring
```

**Without psutil** (fallback):
```python
subprocess.run(['ps', '-eo', 'pid,ppid,comm'])
# Less efficient but works
```

### Firewall Integration

**Current**: Logs PF rules (demonstration mode)
**Future**: Actually applies rules via:
```bash
sudo pfctl -a smart_firewall -f -
```

## Security Benefits

### vs. Permanent Allow

| Permanent Allow | Smart Adaptive |
|----------------|----------------|
| Always open | Only open during action |
| 24/7 attack surface | 5-minute window |
| No context awareness | Action-specific |
| Manual management | Automatic |

### Attack Surface Reduction

**Example**: Python package install

**Permanent Allow**:
- GitHub: Open 24/7
- PyPI: Open 24/7
- Risk: Malware can exfiltrate anytime

**Smart Adaptive**:
- GitHub: Open 5 minutes
- PyPI: Open 5 minutes
- Risk: 99.7% reduction (5 min / 24 hours)

## Configuration

### Adding New Actions

Edit `smart_adaptive_firewall.py`:

```python
self.action_patterns = {
    'your_action': {
        'processes': ['process_name'],
        'parent_apps': ['ParentApp'],
        'required_endpoints': [
            'endpoint.com:443'
        ],
        'duration': 300  # seconds
    }
}
```

### Examples

#### Rust Cargo Build
```python
'rust_build': {
    'processes': ['cargo'],
    'parent_apps': ['Windsurf', 'VSCode', 'RustRover'],
    'required_endpoints': [
        'crates.io:443',
        'static.crates.io:443',
        'github.com:443'
    ],
    'duration': 600  # 10 minutes for large builds
}
```

#### Docker Pull
```python
'docker_pull': {
    'processes': ['docker'],
    'parent_apps': ['Terminal', 'Windsurf'],
    'required_endpoints': [
        'registry-1.docker.io:443',
        'auth.docker.io:443',
        'production.cloudflare.docker.com:443'
    ],
    'duration': 300
}
```

## Logging

All activity logged to: `~/.smart_firewall/firewall.log`

```
[2025-10-19T20:22:06] [DETECT] 🎯 DETECTED: python_install - Windsurf spawned pip3
[2025-10-19T20:22:06] [SUCCESS] ✅ ALLOW: Windsurf → pypi.org:443
[2025-10-19T20:22:06] [INFO] 📝 PF Rule: pass out proto tcp from any to pypi.org port 443
[2025-10-19T20:27:06] [WARNING] ⏰ EXPIRED: Windsurf → pypi.org:443
```

## Status Monitoring

Press Ctrl+C or select option 3 to see status:

```
======================================================================
🛡️  SMART ADAPTIVE FIREWALL STATUS
======================================================================

📊 Active Temporary Allows: 2

Currently Allowed:
  • Windsurf → pypi.org:443 (245s remaining)
  • Windsurf → github.com:443 (245s remaining)

🎯 Detected Actions: 3

Recent Detections:
  • python_install: Windsurf → pip3 (PID 54321) at 2025-10-19T20:22:06
  • npm_install: Windsurf → npm (PID 54400) at 2025-10-19T20:25:15
  • git_clone: Windsurf → git (PID 54500) at 2025-10-19T20:28:30

======================================================================
```

## Troubleshooting

### "psutil not installed"
```bash
# Install psutil for better performance
pip3 install psutil

# Or use without it (fallback mode works fine)
```

### "Permission denied"
```bash
# Firewall rule application requires sudo
sudo python3 smart_adaptive_firewall.py
```

### "Action not detected"
```bash
# Check if process name matches pattern
ps aux | grep pip

# Verify parent app name
ps -p <parent_pid> -o comm=

# Add debug logging to see what's being scanned
```

## Future Enhancements

### 1. Machine Learning
```python
# Learn patterns from user behavior
# Predict which endpoints will be needed
# Proactively allow before process spawns
```

### 2. Network Traffic Analysis
```python
# Monitor actual connections, not just processes
# Detect anomalies (unexpected endpoints)
# Alert on suspicious behavior
```

### 3. GUI Dashboard
```python
# Real-time visualization
# Click to approve/deny actions
# Historical analytics
```

### 4. Cloud Sync
```python
# Share action patterns across devices
# Community-sourced endpoint lists
# Automatic updates
```

## Comparison

### vs. Little Snitch
- ✅ Free (Little Snitch: $45)
- ✅ Open source
- ✅ Action-aware (not just connection-aware)
- ✅ Automatic cleanup
- ❌ No GUI (yet)

### vs. Manual LuLu
- ✅ Automatic detection
- ✅ Temporary allows
- ✅ Context-aware
- ✅ No interruptions
- ✅ 99%+ attack surface reduction

### vs. Static Rules
- ✅ Adapts to actions
- ✅ Time-limited exposure
- ✅ Process-specific
- ✅ Automatic management

## Conclusion

**Smart Adaptive Firewall** = Context-aware security

Instead of:
- ❌ Blocking everything (breaks functionality)
- ❌ Allowing everything (no security)
- ❌ Manual clicking (annoying)

We get:
- ✅ Automatic detection
- ✅ Temporary allows
- ✅ Maximum security
- ✅ Zero interruptions

**The future of firewall management!** 🚀
