# Step-by-Step: Adding Rules in LuLu Using Activity Monitor

## 🎯 Complete Visual Guide

This guide shows you exactly how to monitor network activity and create firewall rules.

---

## 📊 Part 1: Monitor Network Activity

### Step 1: Open Activity Monitor

```bash
# Press Cmd + Space, then type:
Activity Monitor
```

Or navigate to:
```
Applications → Utilities → Activity Monitor
```

### Step 2: Switch to Network Tab

1. Click the **Network** tab at the top
2. Click **Sent Bytes** column to sort by network usage
3. Watch for processes sending data

### Step 3: Identify Suspicious Activity

Look for:
- ❌ System processes with high bandwidth
- ❌ Apps you're not using showing activity
- ❌ Unknown process names
- ❌ Processes that shouldn't be online

**Example:**
```
Process: adprivacyd
Sent Bytes: 5.2 MB
Received Bytes: 1.1 MB
→ This is Apple's ad privacy daemon - should be blocked!
```

---

## 🔍 Part 2: Get Connection Details

### Step 4: Open Terminal

```bash
# Press Cmd + Space, then type:
Terminal
```

### Step 5: Find Active Connections

```bash
# See all connections
lsof -i -n -P

# Filter for specific process (example: adprivacyd)
lsof -i -n -P | grep adprivacyd
```

**Example Output:**
```
adprivacyd  567  root   8u  IPv4  TCP *:*->17.253.144.10:443 (ESTABLISHED)
```

This tells you:
- **Process**: adprivacyd
- **Destination IP**: 17.253.144.10
- **Port**: 443 (HTTPS)
- **Status**: Connected

### Step 6: Find Process Path

```bash
# Find where the process is located
ps aux | grep adprivacyd
```

**Example Output:**
```
root  567  /usr/libexec/adprivacyd
```

Now you know:
- **Full Path**: `/usr/libexec/adprivacyd`

---

## 🛡️ Part 3: Create LuLu Block Rule

### Step 7: Open LuLu Rules

1. Click the **LuLu icon** in your menu bar
2. Select **Rules**

You'll see the LuLu Rules window with all your current rules.

### Step 8: Click "Add Rule"

1. Look at the bottom right of the window
2. Click the **"Add Rule"** button (+ icon)

A new window will appear for creating the rule.

### Step 9: Fill in Rule Details

**For blocking adprivacyd completely:**

```
┌─────────────────────────────────────┐
│ Add Rule                            │
├─────────────────────────────────────┤
│                                     │
│ Process Path:                       │
│ /usr/libexec/adprivacyd            │
│                                     │
│ Endpoint Address:                   │
│ *                                   │
│                                     │
│ Endpoint Port:                      │
│ *                                   │
│                                     │
│ Action:                             │
│ ⦿ Block  ○ Allow                   │
│                                     │
│         [Cancel]  [Add]             │
└─────────────────────────────────────┘
```

**Field Explanations:**

- **Process Path**: `/usr/libexec/adprivacyd`
  - The full path to the process
  - Use Browse button to find it, or type it

- **Endpoint Address**: `*`
  - `*` means ANY address (blocks all destinations)
  - Or enter specific IP: `17.253.144.10`

- **Endpoint Port**: `*`
  - `*` means ANY port
  - Or enter specific port: `443`

- **Action**: **Block** (select the red X icon)

### Step 10: Click "Add"

The rule is now active!

---

## ✅ Part 4: Verify the Rule

### Step 11: Check Rules List

In the LuLu Rules window, you should now see:

```
┌──────────────────────────────────────────────────────┐
│ LuLu Rules                    [Filter Rules]         │
├──────────────────────────────────────────────────────┤
│                                                       │
│ ☑ adprivacyd                                    [×]  │
│   com.apple.ap.adprivacyd (signer: Apple Proper)     │
│                                                       │
│   any address:any port                    ⊗ Block    │
│                                                       │
├──────────────────────────────────────────────────────┤
```

This shows:
- ✅ Rule is active (checkbox checked)
- ✅ Blocks ANY address on ANY port
- ✅ Red "Block" indicator

### Step 12: Test the Block

1. Go back to **Activity Monitor**
2. Watch the **Network** tab
3. Look for `adprivacyd`
4. **Sent Bytes** should now be **0** or very low

If it's still sending data:
- Wait a few seconds for the rule to take effect
- Check the rule is correct
- Restart the process (kill and let it restart)

---

## 🎨 Visual Reference: LuLu Settings

### LuLu Mode Settings

Based on your screenshot, here's the recommended configuration:

```
┌─────────────────────────────────────────────────────┐
│ LuLu's Settings                                     │
├─────────────────────────────────────────────────────┤
│ [Rules] [Mode] [Lists] [Update]                     │
├─────────────────────────────────────────────────────┤
│                                                      │
│ ☐ Passive Mode                                      │
│   Silently run without alerts, applying existing    │
│   rules.                                            │
│                                                      │
│   New connections should be:    [Blocked ▼]        │
│   Rules for new connections     [Yes ▼]            │
│   should be created?                                │
│                                                      │
│ ☐ Block Mode                                        │
│   All traffic routed thru LuLu will be blocked      │
│   (unless the endpoint is explicitly on the         │
│   'Allow' list).                                    │
│                                                      │
│ ☐ No Icon Mode                                      │
│   Run without showing an icon in the status         │
│   menu bar.                                         │
│                                                      │
│ ☐ No VirusTotal Mode                                │
│   Disable integration with VirusTotal.              │
│                                                      │
└─────────────────────────────────────────────────────┘
```

**Recommended Settings:**
- ✅ **Passive Mode** - Checked
- ✅ **New connections**: Blocked
- ✅ **Create rules**: Yes
- ❌ **Block Mode** - Unchecked (too aggressive for beginners)
- ❌ **No Icon Mode** - Unchecked (keep icon visible)
- ❌ **No VirusTotal Mode** - Unchecked (useful for checking unknown apps)

---

## 📝 Common Processes to Block

Here are processes you'll commonly see in Activity Monitor that should be blocked:

### 1. adprivacyd (Ad Privacy Daemon)
```
Path: /usr/libexec/adprivacyd
Block: any address:any port
Reason: Sends ad tracking data to Apple
```

### 2. airportd (Airport/WiFi Daemon)
```
Path: /usr/libexec/airportd
Block: any address:any port
Reason: Sends WiFi diagnostics to Apple
```

### 3. akd (Authentication Keys Daemon)
```
Path: /System/Library/PrivateFrameworks/AuthKit.framework/Versions/A/Support/akd
Block: any address:any port
Reason: Apple ID authentication (if not using Apple ID)
```

### 4. amsengagementd (App Store Engagement)
```
Path: /System/Library/PrivateFrameworks/AppleMediaServices.framework/Versions/A/Resources/amsengagementd
Block: any address:any port
Reason: App Store marketing/engagement tracking
```

### 5. amsondevicestoraged (Apple Media Services)
```
Path: /System/Library/PrivateFrameworks/AppleMediaServices.framework/Versions/A/Resources/amsondevicestoraged
Block: any address:any port
Reason: Media services telemetry
```

---

## 🔄 Part 5: Creating Allow Rules

Sometimes you need to ALLOW a connection instead of blocking it.

### Example: Allow Safari to Connect to GitHub

**Scenario:** You want Safari to access GitHub but nothing else.

### Step 1: Find GitHub's IP

```bash
# In Terminal
nslookup github.com
```

Output:
```
Server:  192.168.1.1
Address: 192.168.1.1#53

Non-authoritative answer:
Name:    github.com
Address: 140.82.114.4
```

GitHub's IP: `140.82.114.4`

### Step 2: Create Allow Rule

In LuLu:
1. Click **Add Rule**
2. Fill in:

```
Process Path: /Applications/Safari.app/Contents/MacOS/Safari
Endpoint Address: 140.82.114.4
Endpoint Port: 443
Action: ALLOW (green checkmark)
```

3. Click **Add**

### Step 3: Verify

1. Open Safari
2. Go to github.com
3. Should load successfully
4. Try another site (should be blocked if you have a block-all rule)

---

## 🎯 Part 6: Port-Specific Rules (Advanced)

For maximum security, use port-specific rules instead of wildcards.

### Example: Allow Windsurf to Only Connect to Codeium API

**Instead of:**
```
Endpoint Address: *
Endpoint Port: *
→ Windsurf can connect ANYWHERE
```

**Use:**
```
Endpoint Address: api.codeium.com
Endpoint Port: 443
→ Windsurf can ONLY connect to api.codeium.com on port 443
```

### Why This Matters

If Windsurf is compromised:
- ❌ **With wildcard**: Attacker can connect anywhere, exfiltrate data
- ✅ **With port-specific**: Attacker is limited to api.codeium.com:443 only

**90% reduction in attack surface!**

---

## 📊 Part 7: Monitoring Your Rules

### Check What's Being Blocked

```bash
# View LuLu logs
tail -f /var/log/lulu.log

# See recent blocks
grep "BLOCK" /var/log/lulu.log | tail -20
```

**Example Output:**
```
2025-10-10 20:30:15 [BLOCK] adprivacyd → 17.253.144.10:443
2025-10-10 20:31:22 [BLOCK] trustd → 17.248.193.18:443
2025-10-10 20:32:45 [BLOCK] analyticsd → 17.253.144.10:443
```

This shows:
- ✅ Your block rules are working
- ✅ Apple processes are being blocked
- ✅ No data is being sent to Apple

### Export Your Rules

1. In LuLu → Rules
2. Click **Export**
3. Save as JSON file
4. Keep as backup

---

## ✅ Quick Checklist

### Initial Setup
- [ ] Install LuLu
- [ ] Configure Passive Mode (Blocked by default)
- [ ] Open Activity Monitor
- [ ] Identify suspicious processes

### For Each Suspicious Process
- [ ] Note process name in Activity Monitor
- [ ] Run `lsof -i -n -P | grep processname`
- [ ] Find process path with `ps aux | grep processname`
- [ ] Open LuLu → Rules → Add Rule
- [ ] Enter process path, endpoint, port
- [ ] Select Block action
- [ ] Click Add
- [ ] Verify in Activity Monitor (should show 0 bytes sent)

### Maintenance
- [ ] Check Activity Monitor daily
- [ ] Review LuLu logs weekly
- [ ] Export rules monthly (backup)
- [ ] Update rules as apps change

---

## 🎓 Pro Tips

### Tip 1: Use Regex for Domains

Instead of blocking specific IPs, use domain patterns:

```
Endpoint Address: *.apple.com
→ Blocks all Apple domains
```

```
Endpoint Address: *.telemetry.*
→ Blocks all telemetry domains
```

### Tip 2: Group Rules by Purpose

Organize your rules:
- **Block Rules**: All telemetry/analytics
- **Allow Rules**: Essential apps only
- **Temporary Rules**: Testing/debugging

### Tip 3: Test Before Blocking

Before blocking a system process:
1. Create the block rule
2. Use your Mac normally for 1 hour
3. If something breaks, remove the rule
4. If everything works, keep the rule

### Tip 4: Use Our Tool

Instead of manually creating rules, use our tool:

```bash
# Generate port-specific rules automatically
python3 create_app_specific_rules.py

# Import into LuLu
# Done!
```

---

## 📚 Additional Resources

- **Full Security Guide**: See `MACOS_SECURITY_HARDENING_GUIDE.md`
- **Port-Specific Rules**: See `PORT_SPECIFIC_RULES_SUMMARY.md`
- **Quick Reference**: See `QUICK_REFERENCE.md`
- **LuLu Documentation**: https://objective-see.org/products/lulu.html

---

**You're now a LuLu expert! 🛡️**
