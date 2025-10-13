#!/usr/bin/env python3
"""
Temporary: Allow ALL network for Windsurf to diagnose GitHub issue
"""

import json

# Load existing rules
with open('/Users/meep/Documents/_ToInvestigate-Offline-Attacks·/ExistingLuluRulesforOps/rules-101225.json') as f:
    rules = json.load(f)

# Find all Windsurf components
windsurf_keys = [k for k in rules.keys() if 'windsurf' in k.lower() or ('language_server' in k.lower() and 'EXAFUNCTION' in k) or ('electron' in k.lower() and 'EXAFUNCTION' in k)]

print(f"Found {len(windsurf_keys)} Windsurf components")
print()

# Set all to ALLOW *:*
for key in windsurf_keys:
    # Keep only one rule: ALLOW *:*
    # In original format: action=0 is ALLOW
    rules[key] = [{
        **rules[key][0],
        "endpointAddr": "*",
        "endpointPort": "*",
        "action": "0"  # ALLOW
    }]
    print(f"✅ {key[:50]}...")
    print(f"   Set to: ALLOW *:*")

# Save
output = "windsurf_allow_all_TEMP.json"
with open(output, 'w') as f:
    json.dump(rules, f, indent=2)

print()
print(f"💾 Saved to: {output}")
print()
print("⚠️  WARNING: This allows ALL network for Windsurf!")
print("   Use this ONLY to diagnose what connections it needs")
print()
print("📋 STEPS:")
print("1. Import this file into LuLu")
print("2. Start Windsurf")
print("3. Test GitHub authentication")
print("4. Check LuLu logs to see what it connected to:")
print("   tail -f /Library/Logs/LuLu.log | grep Windsurf")
