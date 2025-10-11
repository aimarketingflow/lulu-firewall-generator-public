#!/usr/bin/env python3
"""
Create App-Specific Port Rules
Based on what apps you actually use
"""

import json
import uuid
from datetime import datetime

def create_app_rules():
    """Create port-specific rules for common apps"""
    
    rules = {}
    
    # Get current timestamp
    now = datetime.now().astimezone()
    timestamp = now.strftime("%Y-%m-%dT%H:%M:%S%z")
    
    # Safari - Web browsing
    rules["com.apple.Safari"] = [
        {
            "key": "com.apple.Safari",
            "uuid": str(uuid.uuid4()).upper(),
            "path": "/Applications/Safari.app/Contents/MacOS/Safari",
            "name": "Safari",
            "endpointAddr": "*",
            "endpointPort": "443",
            "creation": timestamp,
            "isEndpointAddrRegex": 0,
            "type": 1,
            "scope": 0,
            "action": 0
        },
        {
            "key": "com.apple.Safari",
            "uuid": str(uuid.uuid4()).upper(),
            "path": "/Applications/Safari.app/Contents/MacOS/Safari",
            "name": "Safari",
            "endpointAddr": "*",
            "endpointPort": "80",
            "creation": timestamp,
            "isEndpointAddrRegex": 0,
            "type": 1,
            "scope": 0,
            "action": 0
        }
    ]
    
    # Windsurf - Code editor
    rules["com.exafunction.windsurf"] = [
        {
            "key": "com.exafunction.windsurf",
            "uuid": str(uuid.uuid4()).upper(),
            "path": "/Applications/Windsurf.app/Contents/MacOS/Windsurf",
            "name": "Windsurf",
            "endpointAddr": "api.codeium.com",
            "endpointPort": "443",
            "creation": timestamp,
            "isEndpointAddrRegex": 0,
            "type": 1,
            "scope": 0,
            "action": 0
        },
        {
            "key": "com.exafunction.windsurf",
            "uuid": str(uuid.uuid4()).upper(),
            "path": "/Applications/Windsurf.app/Contents/MacOS/Windsurf",
            "name": "Windsurf",
            "endpointAddr": "github.com",
            "endpointPort": "443",
            "creation": timestamp,
            "isEndpointAddrRegex": 0,
            "type": 1,
            "scope": 0,
            "action": 0
        },
        {
            "key": "com.exafunction.windsurf",
            "uuid": str(uuid.uuid4()).upper(),
            "path": "/Applications/Windsurf.app/Contents/MacOS/Windsurf",
            "name": "Windsurf",
            "endpointAddr": "*.githubusercontent.com",
            "endpointPort": "443",
            "creation": timestamp,
            "isEndpointAddrRegex": 1,
            "type": 1,
            "scope": 0,
            "action": 0
        }
    ]
    
    # Slack - Communication
    rules["com.tinyspeck.slackmacgap"] = [
        {
            "key": "com.tinyspeck.slackmacgap",
            "uuid": str(uuid.uuid4()).upper(),
            "path": "/Applications/Slack.app/Contents/MacOS/Slack",
            "name": "Slack",
            "endpointAddr": "*.slack.com",
            "endpointPort": "443",
            "creation": timestamp,
            "isEndpointAddrRegex": 1,
            "type": 1,
            "scope": 0,
            "action": 0
        },
        {
            "key": "com.tinyspeck.slackmacgap",
            "uuid": str(uuid.uuid4()).upper(),
            "path": "/Applications/Slack.app/Contents/MacOS/Slack",
            "name": "Slack",
            "endpointAddr": "*.slack-edge.com",
            "endpointPort": "443",
            "creation": timestamp,
            "isEndpointAddrRegex": 1,
            "type": 1,
            "scope": 0,
            "action": 0
        }
    ]
    
    # Mail - Email
    rules["com.apple.mail"] = [
        {
            "key": "com.apple.mail",
            "uuid": str(uuid.uuid4()).upper(),
            "path": "/System/Applications/Mail.app/Contents/MacOS/Mail",
            "name": "Mail",
            "endpointAddr": "*",
            "endpointPort": "993",
            "creation": timestamp,
            "isEndpointAddrRegex": 0,
            "type": 1,
            "scope": 0,
            "action": 0
        },
        {
            "key": "com.apple.mail",
            "uuid": str(uuid.uuid4()).upper(),
            "path": "/System/Applications/Mail.app/Contents/MacOS/Mail",
            "name": "Mail",
            "endpointAddr": "*",
            "endpointPort": "587",
            "creation": timestamp,
            "isEndpointAddrRegex": 0,
            "type": 1,
            "scope": 0,
            "action": 0
        },
        {
            "key": "com.apple.mail",
            "uuid": str(uuid.uuid4()).upper(),
            "path": "/System/Applications/Mail.app/Contents/MacOS/Mail",
            "name": "Mail",
            "endpointAddr": "*",
            "endpointPort": "465",
            "creation": timestamp,
            "isEndpointAddrRegex": 0,
            "type": 1,
            "scope": 0,
            "action": 0
        }
    ]
    
    return rules

def create_block_rules():
    """Create rules to BLOCK telemetry and analytics"""
    
    rules = {}
    now = datetime.now().astimezone()
    timestamp = now.strftime("%Y-%m-%dT%H:%M:%S%z")
    
    # Block all telemetry domains
    rules["BLOCK_Telemetry"] = [
        {
            "key": "BLOCK_Telemetry",
            "uuid": str(uuid.uuid4()).upper(),
            "path": "*",
            "name": "Block Telemetry",
            "endpointAddr": "*.telemetry.*",
            "endpointPort": "*",
            "creation": timestamp,
            "isEndpointAddrRegex": 1,
            "type": 3,
            "scope": 0,
            "action": 1
        },
        {
            "key": "BLOCK_Analytics",
            "uuid": str(uuid.uuid4()).upper(),
            "path": "*",
            "name": "Block Analytics",
            "endpointAddr": "*.analytics.*",
            "endpointPort": "*",
            "creation": timestamp,
            "isEndpointAddrRegex": 1,
            "type": 3,
            "scope": 0,
            "action": 1
        },
        {
            "key": "BLOCK_Tracking",
            "uuid": str(uuid.uuid4()).upper(),
            "path": "*",
            "name": "Block Tracking",
            "endpointAddr": "*.tracking.*",
            "endpointPort": "*",
            "creation": timestamp,
            "isEndpointAddrRegex": 1,
            "type": 3,
            "scope": 0,
            "action": 1
        }
    ]
    
    return rules

def main():
    print("🛡️ Creating App-Specific Port Rules...")
    
    # Create allow rules
    allow_rules = create_app_rules()
    
    # Create block rules
    block_rules = create_block_rules()
    
    # Combine
    all_rules = {**allow_rules, **block_rules}
    
    # Save
    output_file = "app_specific_port_rules.json"
    with open(output_file, 'w') as f:
        json.dump(all_rules, f, separators=(',', ' : '))
    
    print(f"✅ Created {sum(len(r) for r in all_rules.values())} rules")
    print(f"💾 Saved to: {output_file}")
    
    # Print summary
    print("\n📊 RULES SUMMARY:")
    print(f"   Safari: {len(allow_rules.get('com.apple.Safari', []))} rules (HTTP/HTTPS)")
    print(f"   Windsurf: {len(allow_rules.get('com.exafunction.windsurf', []))} rules (API, GitHub)")
    print(f"   Slack: {len(allow_rules.get('com.tinyspeck.slackmacgap', []))} rules (Slack domains)")
    print(f"   Mail: {len(allow_rules.get('com.apple.mail', []))} rules (IMAP/SMTP)")
    print(f"   Block Rules: {len(block_rules.get('BLOCK_Telemetry', []))} rules (Telemetry/Analytics)")
    
    print("\n📋 NEXT STEPS:")
    print("   1. Review app_specific_port_rules.json")
    print("   2. Add/remove apps as needed")
    print("   3. Import into LuLu")
    print("   4. Test apps work correctly")

if __name__ == "__main__":
    main()
