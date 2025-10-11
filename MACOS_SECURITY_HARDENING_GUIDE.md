# macOS Security Hardening Guide

## 🛡️ Complete Guide to Securing Your Mac

This guide covers essential security practices for macOS, including firewall configuration, network monitoring, and privacy hardening.

---

## 📋 Table of Contents

1. [Essential Security Tools](#essential-security-tools)
2. [LuLu Firewall Setup](#lulu-firewall-setup)
3. [Recommended Block Rules](#recommended-block-rules)
4. [Activity Monitor as Network Monitor](#activity-monitor-as-network-monitor)
5. [Adding Rules Based on Activity Monitor](#adding-rules-based-on-activity-monitor)
6. [Apple ID Security Considerations](#apple-id-security-considerations)
7. [Advanced: LuLu + Murus Combined](#advanced-lulu--murus-combined)
8. [Maintenance & Monitoring](#maintenance--monitoring)

---

## 🔧 Essential Security Tools

### Required Tools

1. **LuLu Firewall** (Free)
   - Download: https://objective-see.org/products/lulu.html
   - Application-level firewall
   - Blocks outbound connections
   - Essential for privacy

2. **Activity Monitor** (Built-in)
   - Location: `/Applications/Utilities/Activity Monitor.app`
   - Free alternative to Wireshark
   - Monitor network activity in real-time
   - No installation needed

3. **Our Tool** (Free)
   - Generate port-specific firewall rules
   - Parse network connections
   - Create surgical security rules

### Optional Tools

4. **Murus Firewall** (Paid, ~$20)
   - Download: https://www.murusfirewall.com
   - Advanced PF (Packet Filter) configuration
   - Network-level firewall
   - Complements LuLu

---

## 🛡️ LuLu Firewall Setup

### Step 1: Install LuLu

1. Download LuLu from Objective-See
2. Open the DMG file
3. Drag LuLu to Applications
4. Launch LuLu
5. Grant necessary permissions when prompted

### Step 2: Configure LuLu Settings

Click the LuLu menu bar icon → **Settings**

#### Rules Tab Settings

```
✓ Allow Installed Programs (checked)
✗ Allow Apple Programs (UNCHECKED - we'll add specific ones)
✗ Allow DNS Traffic (UNCHECKED - more secure)
✗ Allow Simulator Applications (unchecked unless needed)
```

**Why uncheck "Allow Apple Programs"?**
- Many Apple processes phone home unnecessarily
- Telemetry, analytics, crash reports
- We'll manually allow only what you need

#### Mode Tab Settings

**Choose: Passive Mode**

```
New connections should be: BLOCKED
Rules for new connections should be created? YES
```

**What this means:**
- LuLu runs silently in the background
- All new connections are blocked by default
- You'll be prompted to allow/block each new connection
- Rules are saved automatically

**Alternative: Block Mode** (Advanced)
- Blocks EVERYTHING unless explicitly allowed
- More secure but requires pre-configured rules
- Use after you've built your ruleset

### Step 3: Initial Setup Complete

✅ LuLu is now running in Passive Mode
✅ All new connections will be blocked
✅ You'll be prompted for each app

---

## 🚫 Recommended Block Rules

These Apple processes should be **BLOCKED** for maximum privacy:

### Telemetry & Analytics

1. **adprivacyd** - Ad privacy daemon
   - `com.apple.ap.adprivacyd`
   - Block: `any address:any port`

2. **analyticsd** - Analytics collection
   - `com.apple.analyticsd`
   - Block: `any address:any port`

3. **diagnosticd** - Diagnostic reporting
   - `com.apple.diagnosticd`
   - Block: `any address:any port`

### Cloud Services (Block if not using iCloud)

4. **cloudd** - iCloud daemon
   - `com.apple.cloudd`
   - Block: `any address:any port`

5. **cloudpaird** - iCloud pairing
   - `com.apple.cloudpaird`
   - Block: `any address:any port`

6. **iCloudDrive** - iCloud Drive sync
   - Block: `any address:any port`

### System Telemetry

7. **trustd** - Certificate trust evaluation (phones home)
   - `com.apple.trustd`
   - Block: `any address:any port`
   - ⚠️ May affect some SSL certificates

8. **nsurlsessiond** - Background URL sessions
   - `com.apple.nsurlsessiond`
   - Block: `any address:any port`

9. **rapportd** - Handoff/Continuity
   - `com.apple.rapportd`
   - Block: `any address:any port`

### Location Services

10. **locationd** - Location services
    - `com.apple.locationd`
    - Block: `any address:any port`
    - Only if you don't need location

### How to Add These Block Rules

1. Open LuLu → **Rules**
2. Click **Add Rule** (+ button)
3. For each process:
   - **Process**: Browse to `/usr/libexec/[process-name]` or `/System/Library/PrivateFrameworks/`
   - **Endpoint**: `any address`
   - **Port**: `any port`
   - **Action**: **Block** (red X)
4. Click **Add**

---

## 📊 Activity Monitor as Network Monitor

Activity Monitor is a free, built-in alternative to Wireshark for basic network monitoring.

### Step 1: Open Activity Monitor

```bash
# Via Spotlight
Cmd + Space → "Activity Monitor"

# Or via Terminal
open -a "Activity Monitor"
```

### Step 2: View Network Activity

1. Click the **Network** tab at the top
2. You'll see:
   - **Packets In/Out** - Total network traffic
   - **Data Received/Sent** - Bandwidth usage per process

### Step 3: Sort by Network Usage

1. Click **Sent Bytes** column header
2. Processes using the most bandwidth appear at top
3. Look for suspicious activity:
   - Unknown processes
   - High bandwidth from system processes
   - Apps that shouldn't be online

### Step 4: Identify Suspicious Connections

**Red Flags:**
- ❌ System processes sending large amounts of data
- ❌ Apps you're not using showing network activity
- ❌ Unknown process names
- ❌ Processes connecting when you're "offline"

**Example Suspicious Activity:**
```
Process: trustd
Sent Bytes: 50 MB
Received Bytes: 10 MB
→ Why is a certificate daemon sending 50MB?
```

### Step 5: Get Detailed Connection Info

Open Terminal and run:

```bash
# See all active connections
lsof -i -n -P

# See connections for a specific process
lsof -i -n -P | grep "process-name"

# Example: Check what Safari is connecting to
lsof -i -n -P | grep Safari
```

**Output Example:**
```
Safari    1234 user   42u  IPv4 0x123abc  TCP 192.168.1.5:54321->17.253.144.10:443 (ESTABLISHED)
```

This shows:
- Safari (PID 1234)
- Connected to 17.253.144.10:443 (Apple server)
- Connection is established

---

## ➕ Adding Rules Based on Activity Monitor

### Scenario: You see suspicious activity in Activity Monitor

**Example:** You notice `trustd` is sending data to `17.253.144.10:443`

### Step-by-Step: Create a Block Rule

#### 1. Identify the Process

In Activity Monitor:
- Note the process name: `trustd`
- Note it's sending data

#### 2. Get Connection Details

In Terminal:
```bash
lsof -i -n -P | grep trustd
```

Output:
```
trustd  567  root   8u  IPv4  TCP *:*->17.253.144.10:443 (ESTABLISHED)
```

You now know:
- Process: `trustd`
- Destination: `17.253.144.10`
- Port: `443`

#### 3. Find Process Path

```bash
ps aux | grep trustd
```

Output shows path:
```
/usr/libexec/trustd
```

#### 4. Create LuLu Rule

1. Open LuLu → **Rules**
2. Click **Add Rule** (+ button at bottom right)
3. Fill in the form:

```
Process Path: /usr/libexec/trustd
Endpoint Address: 17.253.144.10
Endpoint Port: 443
Action: BLOCK (red X icon)
```

4. Click **Add**

#### 5. Verify Rule is Active

1. In LuLu Rules window
2. Find `trustd` in the list
3. Should show: `17.253.144.10:443` → **Block**

#### 6. Test the Block

1. Watch Activity Monitor
2. `trustd` should show 0 bytes sent
3. If still sending, check rule is correct

### Alternative: Block All Connections for a Process

If you want to block ALL connections (not just one IP):

```
Process Path: /usr/libexec/trustd
Endpoint Address: * (wildcard)
Endpoint Port: * (wildcard)
Action: BLOCK
```

This blocks `trustd` from connecting to ANY destination.

---

## 🚫 Apple ID Security Considerations

### Why Not Using an Apple ID Improves Security

**Exploits Prevented:**
1. **iCloud Sync Exploits** - No cloud data to compromise
2. **Keychain Sync Attacks** - Passwords stay local only
3. **Find My Mac Tracking** - Can't be tracked remotely
4. **Remote Wipe Attacks** - Can't be remotely wiped
5. **Account Takeover** - No Apple account to hijack
6. **Two-Factor Bypass** - No 2FA to bypass
7. **Phishing Attacks** - No Apple ID to phish

**Services You Lose:**
- ❌ iCloud Drive
- ❌ iCloud Photos
- ❌ iCloud Keychain
- ❌ Find My Mac
- ❌ Handoff/Continuity
- ❌ App Store purchases (can still download free apps)
- ❌ iMessage (on Mac)
- ❌ FaceTime (on Mac)

### How to Use macOS Without Apple ID

#### 1. During Setup

When setting up a new Mac:
1. Skip the Apple ID login screen
2. Click "Set Up Later" or "Skip"
3. Continue with local account only

#### 2. On Existing Mac

To sign out:
1. System Settings → Apple ID
2. Click "Sign Out"
3. Choose to keep or delete local copies of iCloud data
4. Confirm sign out

#### 3. Alternative Services

Replace iCloud services:
- **Cloud Storage**: Dropbox, Google Drive, Nextcloud (self-hosted)
- **Password Manager**: 1Password, Bitwarden, KeePassXC (local)
- **Photos**: Local storage + external backup
- **Messaging**: Signal, Telegram, WhatsApp
- **Video Calls**: Zoom, Google Meet, Signal

### Processes to Block When Not Using Apple ID

```
✓ cloudd - iCloud daemon
✓ cloudpaird - iCloud pairing  
✓ iCloudDrive - iCloud Drive sync
✓ bird - iCloud sync
✓ CloudPhotosConfiguration - iCloud Photos
✓ accountsd - Account services
✓ IMDPersistenceAgent - iMessage
✓ imagent - iMessage agent
```

---

## 🔥 Advanced: LuLu + Murus Combined

For maximum security, use both LuLu and Murus together.

### Why Use Both?

**LuLu (Application Firewall)**
- Controls which apps can connect
- Blocks at application level
- Easy to use
- Free

**Murus (Network Firewall)**
- Controls network traffic by IP/port
- Blocks at network level
- Advanced packet filtering
- Paid (~$20)

**Together:**
- Double layer of protection
- LuLu blocks apps
- Murus blocks network traffic
- Even if an app bypasses LuLu, Murus catches it

### Setup: LuLu + Murus

#### 1. Install Both

- LuLu: https://objective-see.org/products/lulu.html
- Murus: https://www.murusfirewall.com

#### 2. Configure LuLu (Application Layer)

Use our tool to generate app-specific rules:
```bash
python3 create_app_specific_rules.py
```

Import rules into LuLu.

#### 3. Configure Murus (Network Layer)

In Murus:
1. **Inbound Rules**: Block all by default
2. **Outbound Rules**: Allow only specific ports
   - Port 443 (HTTPS)
   - Port 80 (HTTP)
   - Port 53 (DNS) - if needed
   - Port 587 (SMTP) - for email
   - Port 993 (IMAP) - for email

3. **Block Lists**: Enable
   - Malware IPs
   - Tracking domains
   - Ad networks

#### 4. Test Both Firewalls

```bash
# Test outbound connection
curl https://google.com

# Should be blocked by either LuLu or Murus
# Allow in both if needed
```

### Rule Priority

```
1. Murus blocks at network level (first)
2. If Murus allows, LuLu checks at app level (second)
3. If both allow, connection succeeds
```

---

## 🔍 Maintenance & Monitoring

### Daily Checks

**Activity Monitor:**
1. Open Activity Monitor
2. Check Network tab
3. Look for unusual activity
4. Investigate unknown processes

**LuLu Logs:**
```bash
# View recent blocks
tail -f /var/log/lulu.log

# Search for specific process
grep "trustd" /var/log/lulu.log
```

### Weekly Tasks

1. **Review LuLu Rules**
   - Remove unused app rules
   - Update app paths if apps updated
   - Check for duplicate rules

2. **Check for Suspicious Connections**
   ```bash
   # See all established connections
   lsof -i -n -P | grep ESTABLISHED
   
   # Look for unknown IPs
   ```

3. **Update Block Lists**
   - Add new telemetry domains
   - Block new tracking services

### Monthly Tasks

1. **Audit All Rules**
   - Export LuLu rules
   - Review each rule
   - Remove unnecessary allows

2. **Test Offline Mode**
   - Block all internet
   - Verify critical apps still work
   - Identify dependencies

3. **Update Tools**
   - Update LuLu
   - Update Murus (if using)
   - Update our tool

---

## 📚 Quick Reference

### Essential Commands

```bash
# View active connections
lsof -i -n -P

# View connections for specific app
lsof -i -n -P | grep "AppName"

# View LuLu logs
tail -f /var/log/lulu.log

# Generate port-specific rules
python3 create_app_specific_rules.py

# Parse sysdiagnose
python3 sysdiag_connection_parser.py
```

### LuLu Keyboard Shortcuts

- `Cmd + ,` - Open Settings
- `Cmd + R` - Open Rules
- `Cmd + Q` - Quit LuLu

### Activity Monitor Tips

- **Network Tab** - See bandwidth usage
- **Sort by Sent Bytes** - Find chattiest apps
- **Double-click process** - See detailed info
- **Sample Process** - See what it's doing

---

## ✅ Security Checklist

### Initial Setup
- [ ] Install LuLu firewall
- [ ] Configure LuLu to Passive Mode (Blocked by default)
- [ ] Uncheck "Allow Apple Programs"
- [ ] Add recommended block rules
- [ ] Generate port-specific rules with our tool
- [ ] Import rules into LuLu

### Privacy Hardening
- [ ] Consider not using Apple ID
- [ ] Block telemetry processes (analyticsd, adprivacyd, etc.)
- [ ] Block cloud services if not needed
- [ ] Disable location services
- [ ] Block diagnostic reporting

### Monitoring
- [ ] Check Activity Monitor daily
- [ ] Review LuLu logs weekly
- [ ] Audit rules monthly
- [ ] Test offline mode quarterly

### Advanced (Optional)
- [ ] Install Murus for network-level filtering
- [ ] Configure Murus + LuLu together
- [ ] Set up automated monitoring scripts
- [ ] Create backup of firewall rules

---

## 🎯 Recommended Security Posture

### Level 1: Basic (Everyone)
- ✅ Install LuLu
- ✅ Use Passive Mode with Blocked default
- ✅ Block telemetry processes
- ✅ Check Activity Monitor weekly

### Level 2: Intermediate (Privacy-Conscious)
- ✅ All Level 1 items
- ✅ Don't use Apple ID
- ✅ Use port-specific rules
- ✅ Block all cloud services
- ✅ Monitor logs daily

### Level 3: Advanced (Security Professionals)
- ✅ All Level 2 items
- ✅ Install Murus + LuLu
- ✅ Use Block Mode in LuLu
- ✅ Audit all network connections
- ✅ Automated monitoring
- ✅ Regular security audits

---

## 📖 Additional Resources

- **LuLu Documentation**: https://objective-see.org/products/lulu.html
- **Our Tool**: https://github.com/aimarketingflow/Lulu-custom-firewall-generator
- **Patrick Wardle's Blog**: https://objective-see.org/blog.html
- **macOS Security Guide**: https://github.com/drduh/macOS-Security-and-Privacy-Guide

---

## 💚 Support the Tools

**LuLu is free and open-source.** Support Patrick Wardle:
- https://www.patreon.com/objective_see

**Our tool is also free.** Star us on GitHub:
- https://github.com/aimarketingflow/Lulu-custom-firewall-generator

---

**Stay secure! 🛡️**
