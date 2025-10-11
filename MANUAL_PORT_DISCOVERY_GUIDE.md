# Manual Port Discovery & Lockdown Guide

## 🎯 Goal
Create surgical firewall rules by discovering which IPs and ports your apps actually use, then blocking everything else.

---

## 📋 Method 1: LuLu Block Mode (Easiest - Recommended)

### Step 1: Enable Block Mode in LuLu

1. **Open LuLu**
2. **Preferences** → Set to **"Block Mode"**
3. **Enable logging** (so you can review later)

### Step 2: Use Your Apps Normally

**Do your normal workflow for 1-2 hours:**
- Open Safari → Browse websites
- Open Windsurf → Work on code
- Open Slack → Send messages
- Open Mail → Check email
- etc.

**LuLu will popup for EVERY connection attempt**

### Step 3: Record Each Connection

When LuLu shows a popup, **write down**:

```
App Name: Safari
Destination: www.google.com (142.250.80.46)
Port: 443
Action: ALLOW (if you need it) or BLOCK (if suspicious)
```

**Example Log**:
```
Safari → www.google.com:443 ✅ ALLOW
Safari → fonts.googleapis.com:443 ✅ ALLOW
Safari → analytics.google.com:443 ❌ BLOCK (telemetry)
Windsurf → api.codeium.com:443 ✅ ALLOW
Windsurf → telemetry.windsurf.com:443 ❌ BLOCK (telemetry)
Slack → slack.com:443 ✅ ALLOW
Slack → files.slack.com:443 ✅ ALLOW
```

### Step 4: Create Rules from Your Log

After 1-2 hours, you'll have a list of:
- ✅ **Essential connections** (app needs these to work)
- ❌ **Telemetry/analytics** (block these)
- ❓ **Unknown** (research these)

### Step 5: Generate LuLu Rules

Use our tool to convert your log into LuLu rules:

```bash
# Create a CSV file with your connections
cat > my_connections.csv << EOF
Safari,www.google.com,443,allow
Safari,fonts.googleapis.com,443,allow
Windsurf,api.codeium.com,443,allow
Slack,slack.com,443,allow
EOF

# Then use our tool (coming soon) to convert to LuLu format
python3 convert_csv_to_lulu.py my_connections.csv
```

---

## 📋 Method 2: Extract from Sysdiagnose (Advanced)

### Step 1: Capture Sysdiagnose While Apps Are Running

```bash
# Make sure your apps are running and active
# Then capture sysdiagnose
sudo sysdiagnose

# This creates: ~/Desktop/sysdiagnose_YYYY.MM.DD_HH-MM-SS.tar.gz
```

### Step 2: Extract Network Connections

```bash
# Extract the archive
tar -xzf sysdiagnose_*.tar.gz

# Find network connection logs
cd sysdiagnose_*/
find . -name "*lsof*" -o -name "*netstat*" -o -name "*network*"
```

### Step 3: Parse Connection Data

Look for files like:
- `lsof.txt` - Shows open network connections
- `netstat.txt` - Network statistics
- `system_logs.logarchive` - System logs with connection info

**Parse lsof output**:
```bash
# Find all ESTABLISHED connections
grep ESTABLISHED lsof.txt | grep -v "127.0.0.1"

# Example output:
# Safari    1234  user  TCP 192.168.1.100:54321->142.250.80.46:443 (ESTABLISHED)
```

This shows: **Safari connected to 142.250.80.46 on port 443**

### Step 4: Resolve IPs to Domains

```bash
# Reverse DNS lookup
nslookup 142.250.80.46

# Output: 46.80.250.142.in-addr.arpa name = lga34s32-in-f14.1e100.net
# This is Google's server
```

### Step 5: Create Port-Specific Rules

Now you know:
- Safari needs: google.com:443, googleapis.com:443
- Windsurf needs: api.codeium.com:443
- etc.

---

## 📋 Method 3: Live Capture with Our Tool

### Step 1: Capture Live Connections

```bash
cd /Users/meep/Documents/_ToInvestigate-Offline-Attacks·/ActivityMonitorDefenseMonster

# Capture live (requires sudo)
sudo python3 network_analyzer.py

# Or from existing lsof output
lsof -i -n -P > connections.txt
python3 network_analyzer.py --from-file connections.txt
```

### Step 2: Review Generated Rules

The tool creates `port_specific_rules.json`:

```json
{
  "Safari": [
    {
      "name": "Safari",
      "endpointAddr": "www.google.com",
      "endpointPort": "443",
      "action": 0
    }
  ]
}
```

### Step 3: Import to LuLu

1. Open LuLu
2. Import `port_specific_rules.json`
3. Test your apps work
4. Monitor logs for blocked connections

---

## 🔍 Analyzing Your Sysdiagnose

Let me extract connection data from your recent sysdiag:

```bash
cd /Users/meep/Documents/_ToInvestigate-Offline-Attacks·/missing-logs

# Extract
tar -xzf sysdiagnose_2025.10.08_19-31-08-0700_macOS_Mac_25A362.tar.gz

# Find network files
find sysdiag_extract -name "*lsof*" -o -name "*netstat*"

# Parse connections
grep -r "ESTABLISHED" sysdiag_extract/ | grep -v "127.0.0.1"
```

---

## 📊 Common Ports Reference

| Port | Protocol | Common Use |
|------|----------|------------|
| 80 | HTTP | Unencrypted web |
| 443 | HTTPS | Encrypted web (most apps) |
| 53 | DNS | Domain name resolution |
| 22 | SSH | Secure shell |
| 25 | SMTP | Email sending |
| 587 | SMTP | Email sending (modern) |
| 993 | IMAP | Email receiving |
| 5222 | XMPP | Chat/messaging |
| 8080 | HTTP-Alt | Alternative HTTP |

---

## 🛡️ Security Levels

### Level 1: Wildcard (Least Secure)
```json
{"endpointAddr": "*", "endpointPort": "*"}
```
❌ App can connect ANYWHERE

### Level 2: Port-Specific
```json
{"endpointAddr": "*", "endpointPort": "443"}
```
⚠️ App can connect to ANY IP on port 443

### Level 3: Domain-Specific (Recommended)
```json
{"endpointAddr": "api.example.com", "endpointPort": "443"}
```
✅ App can ONLY connect to api.example.com:443

### Level 4: IP-Specific (Most Secure)
```json
{"endpointAddr": "142.250.80.46", "endpointPort": "443"}
```
✅✅ App can ONLY connect to specific IP on port 443
⚠️ But IPs change, so use domains instead

---

## 🎯 Recommended Workflow

1. **Day 1**: Enable LuLu Block Mode, log all connections
2. **Day 2-3**: Identify essential vs telemetry
3. **Day 4**: Create port-specific rules with our tool
4. **Day 5**: Import to LuLu and test
5. **Week 2**: Monitor logs, adjust as needed
6. **Monthly**: Review and update rules

---

## 🚨 Red Flags to Watch For

When reviewing connections, **BLOCK immediately** if you see:

❌ **Telemetry domains**:
- analytics.*
- telemetry.*
- tracking.*
- metrics.*

❌ **Unusual ports**:
- Anything not 80, 443, 53, 22, 25, 587, 993
- Random high ports (>10000)

❌ **Unknown destinations**:
- IPs you don't recognize
- Domains not related to the app

❌ **Excessive connections**:
- App making 100+ connections
- Constant reconnection attempts

---

## 📝 Template: Connection Log

```
Date: 2025-10-08
Duration: 2 hours
Apps Tested: Safari, Windsurf, Slack

=== SAFARI ===
✅ www.google.com:443 (search)
✅ fonts.googleapis.com:443 (fonts)
❌ analytics.google.com:443 (BLOCK - telemetry)
✅ github.com:443 (code repos)

=== WINDSURF ===
✅ api.codeium.com:443 (AI features)
✅ github.com:443 (git operations)
❌ telemetry.windsurf.com:443 (BLOCK - telemetry)

=== SLACK ===
✅ slack.com:443 (messaging)
✅ files.slack.com:443 (file uploads)
✅ a.slack-edge.com:443 (CDN)

=== BLOCKED ===
❌ Safari → analytics.google.com:443
❌ Windsurf → telemetry.windsurf.com:443
❌ cloudd → icloud.com:443 (don't use iCloud)
```

---

## 🔧 Next Steps

I'm now analyzing your sysdiag to extract actual connection data...
