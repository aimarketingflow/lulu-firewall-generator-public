# Quick Reference - Port-Specific Firewall Rules

## 🚀 Files You Have

1. **app_specific_port_rules.json** ⭐ READY TO IMPORT
   - 13 curated rules for Safari, Windsurf, Slack, Mail
   - Includes telemetry blocking
   - **Import this one first**

2. **sysdiag_lulu_rules.json** ⚠️ NEEDS REVIEW
   - 41 rules from your actual connections
   - Many "Unknown" IPs
   - Review before importing

## 📥 How to Import

```bash
# Location
cd /Users/meep/Documents/_ToInvestigate-Offline-Attacks·/ActivityMonitorDefenseMonster

# Import to LuLu
1. Open LuLu
2. Rules → Import
3. Select app_specific_port_rules.json
4. Done!
```

## 🔍 How to Test

After importing, test each app:
- Safari → google.com
- Windsurf → Open a project
- Slack → Send a message
- Mail → Check email

If blocked, check LuLu logs and add the destination.

## 🛠️ How to Add More Apps

```bash
# Edit the template
nano create_app_specific_rules.py

# Add your app in create_app_rules()
# Then run:
python3 create_app_specific_rules.py
```

## 📊 Security Levels

**Level 1**: Wildcard (❌ Insecure)
```json
{"endpointAddr": "*", "endpointPort": "*"}
```

**Level 2**: Port-Specific (⚠️ Medium)
```json
{"endpointAddr": "*", "endpointPort": "443"}
```

**Level 3**: Domain + Port (✅ Secure)
```json
{"endpointAddr": "api.example.com", "endpointPort": "443"}
```

## 🚨 What We Blocked Today

- Python → cdns1.cox.net (Cox DNS)
- *.telemetry.* (All telemetry)
- *.analytics.* (All analytics)
- *.tracking.* (All tracking)

## 📋 Common Ports

- 80 = HTTP
- 443 = HTTPS
- 53 = DNS
- 587 = SMTP (email)
- 993 = IMAP (email)

## 🎯 Next Steps

1. Import app_specific_port_rules.json
2. Test all your apps
3. Monitor LuLu logs for 1 week
4. Adjust rules as needed
5. Profit! 🎉
