# 🛡️ Adaptive Firewall Daemon

## The Problem

Apps like Windsurf need different connections during:
- **Startup**: OAuth, updates, auth servers
- **Runtime**: API calls, telemetry, specific services

Traditional firewalls can't distinguish between these phases.

## The Solution

**Learning Mode**: Monitor an app during startup, capture all connections, generate precise rules.

## How It Works

```
1. Start learning mode
2. Launch your app (e.g., Windsurf)
3. Use it normally for 5 minutes
4. Daemon captures all connections
5. Generates LuLu-compatible rules
6. Import rules into LuLu
```

## Usage

### Quick Start

```bash
# Run with sudo (required for packet capture)
sudo python3 adaptive_firewall_daemon.py
```

### Interactive Menu

```
1. Start learning mode for an app
   → Enter app name (e.g., "Windsurf")
   → Specify duration (default: 300 seconds)
   → Launch and use the app
   → Daemon captures all connections

2. View discovered connections
   → See all endpoints discovered per app
   → Grouped by frequency

3. Generate rules
   → Create firewall rules from captured data
   → Deduplicates and optimizes

4. Export to LuLu format
   → Creates JSON file ready for LuLu import
   → Located in ~/.adaptive_firewall/
```

### Example Session

```bash
$ sudo python3 adaptive_firewall_daemon.py

🛡️  Adaptive Firewall Daemon
============================================================

Options:
  1. Start learning mode for an app
  2. View discovered connections
  3. Generate rules
  4. Export to LuLu format
  5. Exit

Select option: 1
App name (e.g., Windsurf): Windsurf
Duration in seconds (default 300): 300

🎓 Starting learning mode for Windsurf...
⚠️  Please start Windsurf now and use it normally
⏰ Will monitor for 300 seconds

🔍 Monitoring Windsurf connections...
  📡 140.82.121.4:443
  📡 140.82.121.3:443
  📡 185.199.108.133:443
  ...

✅ Learning complete for Windsurf

📊 Discovered 12 unique endpoints for Windsurf:
  • 140.82.121.4:443 (tcp)
  • 140.82.121.3:443 (tcp)
  • 185.199.108.133:443 (tcp)
  ...

💾 Exported LuLu rules to: ~/.adaptive_firewall/lulu_rules_windsurf.json
```

## Architecture

### Works Alongside LuLu

```
┌─────────────────────────────────────┐
│      macOS Network Stack            │
└─────────────────────────────────────┘
                 ↓
    ┌────────────────────────┐
    │  Adaptive Firewall     │
    │  (Learning & Monitoring)│
    └────────────────────────┘
                 ↓
    ┌────────────────────────┐
    │  LuLu (Enforcement)    │
    │  (Static Rules)        │
    └────────────────────────┘
```

### Division of Labor

**Adaptive Firewall**:
- ✅ Learns startup patterns
- ✅ Captures real connections
- ✅ Generates precise rules
- ✅ Exports to LuLu format

**LuLu**:
- ✅ Enforces rules
- ✅ User prompts for new connections
- ✅ Persistent rule storage
- ✅ System-level blocking

## Technical Details

### Monitoring Method

Uses `tcpdump` to capture network traffic:
```bash
sudo tcpdump -i any -n -l -q 'tcp or udp'
```

### Data Storage

All data stored in `~/.adaptive_firewall/`:
- `rules.json` - Generated rules
- `learning_data.json` - Raw captured connections
- `firewall.log` - Activity log
- `lulu_rules_*.json` - LuLu-compatible exports

### Rule Format

Generated rules include:
- Endpoint IP address
- Port number
- Protocol (TCP/UDP)
- Timestamp of discovery
- Frequency count

### LuLu Export Format

```json
{
  "com.windsurf": [
    {
      "endpointAddr": "140.82.121.4",
      "endpointPort": "443",
      "action": "1",
      "type": "3",
      "scope": "0"
    }
  ]
}
```

## Workflow

### Phase 1: Learning

```bash
# Start daemon
sudo python3 adaptive_firewall_daemon.py

# Select option 1
# Enter app name: Windsurf
# Duration: 300 seconds

# Launch Windsurf and use normally:
# - Sign in
# - Open projects
# - Use AI features
# - Let it update
# - Access settings

# Wait for learning to complete
```

### Phase 2: Rule Generation

Rules are automatically generated after learning completes.

View them:
```bash
# Select option 2 in the menu
# Shows all discovered endpoints
```

### Phase 3: Export & Import

```bash
# Select option 4
# Enter app name: Windsurf
# File created: ~/.adaptive_firewall/lulu_rules_windsurf.json

# Import into LuLu:
# 1. Open LuLu preferences
# 2. Click "Import Rules"
# 3. Select the generated JSON file
# 4. Confirm import
```

### Phase 4: Testing

```bash
# Quit Windsurf completely
# Restart Windsurf
# Should work perfectly with new rules!
```

## Advantages

### vs. Manual Rule Creation
- ✅ Captures ALL connections (not just blocked ones)
- ✅ No interruptions during use
- ✅ Complete startup flow captured
- ✅ Includes one-time auth connections

### vs. Static Rules
- ✅ Adapts to app updates
- ✅ Learns actual usage patterns
- ✅ No guessing required
- ✅ Comprehensive coverage

### vs. Permissive Rules
- ✅ Minimal attack surface
- ✅ Only discovered endpoints allowed
- ✅ No wildcards
- ✅ Port-specific rules

## Limitations

### Requires sudo
- Packet capture needs root access
- Run with `sudo` command

### Captures system-wide traffic
- May include other apps' connections
- Best to run when only target app is active
- Can filter by process in future versions

### Learning period needed
- Must use app normally during capture
- 5 minutes recommended minimum
- Longer = more complete rules

## Future Enhancements

### Process Filtering
```python
# Filter tcpdump by specific process
# Requires additional tooling
```

### Automatic Re-learning
```python
# Detect when app fails to connect
# Trigger learning mode automatically
```

### Rule Merging
```python
# Merge new discoveries with existing rules
# Incremental learning
```

### GUI Integration
```python
# Visual interface for learning mode
# Real-time connection display
# One-click export to LuLu
```

## Troubleshooting

### "Permission denied"
```bash
# Must run with sudo
sudo python3 adaptive_firewall_daemon.py
```

### "No connections captured"
```bash
# Make sure app is actually running
# Check that you're using the app during capture
# Verify tcpdump is working: sudo tcpdump -i any -c 10
```

### "Rules don't work after import"
```bash
# Verify LuLu imported correctly
# Check LuLu preferences for new rules
# Ensure app path matches in LuLu
# Try restarting LuLu
```

## Security Considerations

### Trustworthy Learning Environment
- Run learning mode on clean system
- Don't visit untrusted sites during capture
- Only use legitimate app features
- Captured endpoints become allowed forever

### Review Generated Rules
- Check discovered endpoints before import
- Remove any suspicious IPs
- Verify domains make sense for the app

### Periodic Re-learning
- Apps update and change endpoints
- Re-run learning mode after major updates
- Merge new rules with existing ones

## Examples

### Windsurf
```bash
# Typical discovered endpoints:
- *.github.com:443 (GitHub API)
- *.githubusercontent.com:443 (Content)
- *.vscode.dev:443 (VSCode services)
- api.codeium.com:443 (AI features)
- 127.0.0.1:* (IPC)
```

### Slack
```bash
# Typical discovered endpoints:
- *.slack.com:443 (Main API)
- *.slack-edge.com:443 (CDN)
- *.slack-imgs.com:443 (Images)
- wss://ms*.slack.com:443 (WebSocket)
```

### Safari
```bash
# Highly variable based on usage
# Recommend permissive rules for browsers
# Or use learning mode per browsing session
```

## Contributing

Ideas for improvement:
1. Process-specific filtering
2. DNS resolution for IPs
3. Automatic rule updates
4. Integration with other firewalls
5. Machine learning for pattern detection

## License

MIT License - Use freely, contribute back!
