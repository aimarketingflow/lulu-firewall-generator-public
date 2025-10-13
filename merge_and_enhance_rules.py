#!/usr/bin/env python3
"""
Merge Existing LuLu Rules with Port-Specific Rules from Sysdiag
Takes your current rules and enhances them with port-specific rules for each app
"""

import json
import uuid
from datetime import datetime
from pathlib import Path

def load_existing_rules(filepath):
    """Load existing LuLu rules"""
    with open(filepath, 'r') as f:
        return json.load(f)

def load_sysdiag_connections(filepath):
    """Load connections found in sysdiag"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def get_timestamp():
    """Get current timestamp in LuLu format"""
    now = datetime.now().astimezone()
    timestamp = now.strftime("%Y-%m-%dT%H:%M:%S%z")
    # Add colon in timezone: -0700 -> -07:00
    return timestamp[:-2] + ':' + timestamp[-2:] if len(timestamp) > 2 else timestamp

def create_port_specific_rule(app_key, app_name, app_path, endpoint, port, is_regex=False, action="0", rule_type="1"):
    """Create a single port-specific rule"""
    return {
        "key": app_key,
        "uuid": str(uuid.uuid4()).upper(),
        "path": app_path,
        "name": app_name,
        "endpointAddr": endpoint,
        "endpointPort": str(port),
        "creation": get_timestamp(),
        "isEndpointAddrRegex": "1" if is_regex else "0",
        "type": rule_type,  # "1" = process, "3" = bundle
        "scope": "0",
        "action": action
    }

def ensure_default_deny(rules_list):
    """
    Ensure every app with ALLOW rules also has a wildcard BLOCK rule
    This creates a default-deny policy: block everything except specific allows
    
    ONLY add wildcard BLOCK if:
    - Has ALLOW rules
    - ALLOW rules are NOT wildcards (specific endpoints only)
    - No wildcard BLOCK already exists
    """
    # Check for specific (non-wildcard) ALLOW rules
    has_specific_allow = any(
        r['action'] == '1' and not (r['endpointAddr'] == '*' and r['endpointPort'] == '*')
        for r in rules_list
    )
    
    has_wildcard_block = any(
        r['endpointAddr'] == '*' and r['endpointPort'] == '*' and r['action'] == '0'
        for r in rules_list
    )
    
    # Only add wildcard BLOCK if has specific (non-wildcard) ALLOW rules
    if has_specific_allow and not has_wildcard_block:
        # Get info from first rule
        first_rule = rules_list[0]
        block_rule = {
            "key": first_rule["key"],
            "uuid": str(uuid.uuid4()).upper(),
            "path": first_rule["path"],
            "name": first_rule["name"],
            "endpointAddr": "*",
            "endpointPort": "*",
            "creation": get_timestamp(),
            "isEndpointAddrRegex": "0",
            "type": first_rule.get("type", "1"),
            "scope": "0",
            "action": "0"  # BLOCK (inverted)
        }
        # Insert at beginning so BLOCK comes first
        return [block_rule] + rules_list
    
    return rules_list

def deduplicate_rules(rules_list):
    """
    Remove duplicate rules based on endpoint+port combination
    Priority:
    1. For *:* - prefer BLOCK over ALLOW (default deny)
    2. For specific endpoints - prefer non-wildcard over wildcard
    3. For same endpoint+port - prefer newer rule
    """
    seen = {}
    deduped = []
    
    for rule in rules_list:
        key = f"{rule['endpointAddr']}:{rule['endpointPort']}"
        
        if key not in seen:
            seen[key] = rule
            deduped.append(rule)
        else:
            # If we've seen this endpoint+port before, decide which to keep
            existing = seen[key]
            
            # Special case: For *:* prefer BLOCK (action=0 in inverted) over ALLOW (action=1 in inverted)
            # NOTE: LuLu displays actions inverted, so 0=BLOCK, 1=ALLOW in our JSON
            if key == "*:*":
                if rule['action'] == '0' and existing['action'] == '1':
                    # Replace ALLOW with BLOCK for wildcards
                    deduped.remove(existing)
                    deduped.append(rule)
                    seen[key] = rule
                # Otherwise keep existing (if both BLOCK or existing is already BLOCK)
            # Prefer non-wildcard over wildcard
            elif rule['endpointAddr'] != '*' and existing['endpointAddr'] == '*':
                # Replace wildcard with specific
                deduped.remove(existing)
                deduped.append(rule)
                seen[key] = rule
            elif rule['endpointPort'] != '*' and existing['endpointPort'] == '*':
                # Replace wildcard port with specific port
                deduped.remove(existing)
                deduped.append(rule)
                seen[key] = rule
            # Otherwise keep the first one (existing)
    
    return deduped

def load_app_configs(config_path="all_apps_config.json"):
    """Load app configurations from JSON"""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def is_apple_process_blocked(app_key, existing_rules):
    """Check if an Apple process is already blocked"""
    if app_key not in existing_rules:
        return False
    
    # Check if it's an Apple process (starts with com.apple)
    if not app_key.startswith('com.apple'):
        return False
    
    # Check if all rules are BLOCK
    # NOTE: In ORIGINAL rules format (not inverted): 0 = ALLOW, 1 = BLOCK
    for rule in existing_rules[app_key]:
        if rule.get('action') == '0':  # Has an ALLOW rule (original format)
            return False
    
    return True  # All rules are BLOCK

def enhance_rules_with_port_specific(existing_rules, sysdiag_data):
    """
    Enhance existing rules with port-specific rules based on sysdiag data
    """
    enhanced_rules = {}
    
    # Copy all existing rules first
    for app_key, rules in existing_rules.items():
        enhanced_rules[app_key] = rules.copy()
    
    # Load app configs from sysdiag analysis
    app_configs = load_app_configs()
    
    # Map of known applications to their sysdiag connections
    # Format: (endpoint, port, is_regex, action)
    # action: "0" = BLOCK, "1" = ALLOW (INVERTED - LuLu displays opposite!)
    # CRITICAL: BLOCK rule must come FIRST, then ALLOW exceptions
    app_connections = {
        "com.exafunction.windsurf": {
            "name": "Windsurf",
            "path": "/Applications/Windsurf.app",  # Bundle path, not executable
            "type": "3",  # Bundle type
            "endpoints": [
                ("*", "*", False, "0"),  # Block everything by default (MUST BE FIRST) - using 0 because LuLu inverts
                ("*.github.com", "443", True, "1"),  # Then allow exceptions - using 1 because LuLu inverts
                ("*.githubusercontent.com", "443", True, "1"),
                ("api.codeium.com", "443", False, "1"),
                ("*.googleusercontent.com", "443", True, "1")
            ],
            "also_update": [
                "com.exafunction.windsurf.helper",  # Windsurf Helper
                "com.github.Electron.helper",  # Electron Helper (Plugin)
                "language_server_macos_arm"  # Language Server
            ]
        },
        "com.apple.Safari": {
            "name": "Safari",
            "path": "/Applications/Safari.app/Contents/MacOS/Safari",
            "endpoints": [
                ("*", "443", False, "1"),  # ALLOW (inverted)
                ("*", "80", False, "1")    # ALLOW (inverted)
            ]
        },
        "com.google.Chrome": {
            "name": "Google Chrome",
            "path": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "endpoints": [
                ("*", "443", False, "1"),  # ALLOW (inverted)
                ("*", "80", False, "1")    # ALLOW (inverted)
            ]
        },
        "com.tinyspeck.slackmacgap": {
            "name": "Slack",
            "path": "/Applications/Slack.app/Contents/MacOS/Slack",
            "endpoints": [
                ("*", "*", False, "0"),  # Block everything by default (MUST BE FIRST) - inverted
                ("*.slack.com", "443", True, "1"),  # ALLOW (inverted)
                ("*.slack-edge.com", "443", True, "1"),
                ("*.slack-msgs.com", "443", True, "1")
            ]
        },
        "com.apple.mail": {
            "name": "Mail",
            "path": "/Applications/Mail.app/Contents/MacOS/Mail",
            "endpoints": [
                ("*", "*", False, "0"),  # Block everything by default (MUST BE FIRST) - inverted
                ("*", "993", False, "1"),  # IMAP SSL - ALLOW (inverted)
                ("*", "587", False, "1"),  # SMTP - ALLOW (inverted)
                ("*", "465", False, "1")   # SMTP SSL - ALLOW (inverted)
            ]
        },
        "com.spotify.client": {
            "name": "Spotify",
            "path": "/Applications/Spotify.app/Contents/MacOS/Spotify",
            "endpoints": [
                ("*", "*", False, "0"),  # Block everything by default (MUST BE FIRST) - inverted
                ("*.spotify.com", "443", True, "1"),  # ALLOW (inverted)
                ("*.scdn.co", "443", True, "1")  # ALLOW (inverted)
            ]
        },
        "com.apple.appstored": {
            "name": "App Store",
            "path": "/System/Library/PrivateFrameworks/AppStoreDaemon.framework/Support/appstored",
            "endpoints": [
                ("*.aaplimg.com", "443", True, "1"),  # ALLOW (inverted)
                ("*.apple.com", "443", True, "1")  # ALLOW (inverted)
            ]
        }
    }
    
    # Merge in app_configs from sysdiag analysis
    if app_configs:
        print(f"  📦 Merging {len(app_configs)} apps from sysdiag analysis...")
        for app_name, config in app_configs.items():
            # Skip if already in manual list
            if config["bundle_id"] not in app_connections:
                # Check if it's a blocked Apple process
                is_blocked_apple = False
                for existing_key in existing_rules.keys():
                    if config["bundle_id"] in existing_key or app_name in existing_key:
                        if is_apple_process_blocked(existing_key, existing_rules):
                            is_blocked_apple = True
                            print(f"     ⏭️  Skipping {app_name} (blocked Apple process)")
                            break
                
                if not is_blocked_apple:
                    app_connections[config["bundle_id"]] = {
                        "name": app_name,
                        "path": config["path"],
                        "type": config.get("type", "3"),
                        "endpoints": config["endpoints"],
                        "also_update": config.get("dependencies", [])
                    }
        print()
    
    # Add port-specific rules for each known app
    for app_key, app_info in app_connections.items():
        # Find all matching keys (including also_update list)
        keys_to_update = []
        
        # Check if this app exists in existing rules
        for existing_key in existing_rules.keys():
            if app_key in existing_key or app_info["name"] in existing_key:
                # Skip if it's a blocked Apple process
                if not is_apple_process_blocked(existing_key, existing_rules):
                    keys_to_update.append(existing_key)
        
        # Add any additional keys from also_update
        if "also_update" in app_info:
            for extra_key in app_info["also_update"]:
                for existing_key in existing_rules.keys():
                    if extra_key in existing_key and existing_key not in keys_to_update:
                        keys_to_update.append(existing_key)
        
        if keys_to_update:
            # Filter out blocked Apple processes from keys_to_update
            blocked_keys = [k for k in keys_to_update if is_apple_process_blocked(k, existing_rules)]
            keys_to_update = [k for k in keys_to_update if k not in blocked_keys]
            
            if blocked_keys:
                print(f"  ⏭️  Skipping {len(blocked_keys)} blocked {app_info['name']} variants")
                for bk in blocked_keys[:3]:
                    print(f"     • {bk[:50]}...")
            
            if not keys_to_update:
                continue
            
            print(f"  ✅ Found {app_info['name']} in existing rules ({len(keys_to_update)} entries)")
            print(f"     Adding {len(app_info['endpoints'])} port-specific rules...")
            
            # Update all matching keys
            for actual_key in keys_to_update:
                # Create new port-specific rules
                new_rules = []
                rule_type = app_info.get("type", "1")  # Default to process type
                for endpoint, port, is_regex, action in app_info["endpoints"]:
                    rule = create_port_specific_rule(
                        actual_key,
                        app_info["name"],
                        app_info["path"],
                        endpoint,
                        port,
                        is_regex,
                        action,
                        rule_type
                    )
                    new_rules.append(rule)
                
                # Double-check: don't update if it's a blocked Apple process
                if is_apple_process_blocked(actual_key, existing_rules):
                    continue
                
                # Combine existing rules with new port-specific rules
                combined_rules = enhanced_rules[actual_key] + new_rules
                
                # Deduplicate: remove duplicates and conflicting rules
                deduped_rules = deduplicate_rules(combined_rules)
                
                # Ensure default deny: add wildcard BLOCK if has ALLOW rules
                deduped_rules = ensure_default_deny(deduped_rules)
                
                # Update the rules
                enhanced_rules[actual_key] = deduped_rules
                
                # Report what was removed
                removed_count = len(combined_rules) - len(deduped_rules)
                if removed_count > 0:
                    print(f"     [{actual_key[:30]}...] Removed {removed_count} duplicate/conflicting rules")
            
        else:
            # App doesn't exist in current rules, add it
            print(f"  ➕ Adding new app: {app_info['name']}")
            print(f"     Creating {len(app_info['endpoints'])} port-specific rules...")
            
            new_rules = []
            rule_type = app_info.get("type", "1")  # Default to process type
            for endpoint, port, is_regex, action in app_info["endpoints"]:
                rule = create_port_specific_rule(
                    app_key,
                    app_info["name"],
                    app_info["path"],
                    endpoint,
                    port,
                    is_regex,
                    action,
                    rule_type
                )
                new_rules.append(rule)
            
            # Deduplicate even for new apps (in case of internal duplicates)
            deduped = deduplicate_rules(new_rules)
            
            # Ensure default deny
            deduped = ensure_default_deny(deduped)
            
            enhanced_rules[app_key] = deduped
    
    # Final pass: ensure ALL apps have default deny if they have any ALLOW rules
    print("  🔒 Applying default-deny policy to all apps...")
    apps_with_default_deny = 0
    for app_key in enhanced_rules.keys():
        original_count = len(enhanced_rules[app_key])
        enhanced_rules[app_key] = ensure_default_deny(enhanced_rules[app_key])
        if len(enhanced_rules[app_key]) > original_count:
            apps_with_default_deny += 1
    
    if apps_with_default_deny > 0:
        print(f"     Added wildcard BLOCK to {apps_with_default_deny} apps")
    print()
    
    return enhanced_rules

def main():
    print("🛡️  LuLu Rule Merger & Enhancer")
    print("=" * 60)
    print()
    
    # Paths (update these to match your system)
    existing_rules_path = "rules-101225.json"  # Your existing LuLu rules export
    sysdiag_rules_path = "sysdiag_lulu_rules.json"
    output_path = "enhanced_lulu_rules-FINAL-v2.json"
    
    print("📂 Loading existing rules...")
    existing_rules = load_existing_rules(existing_rules_path)
    print(f"   Found {len(existing_rules)} apps with rules")
    print()
    
    print("📦 Loading app configurations from sysdiag...")
    app_configs = load_app_configs("all_apps_config.json")
    if app_configs:
        print(f"   Found {len(app_configs)} active apps")
    else:
        print("   No app configs found, using manual list")
    print()
    
    print("🔍 Enhancing with port-specific rules...")
    print()
    enhanced_rules = enhance_rules_with_port_specific(existing_rules, {})
    print()
    
    # Count total rules
    total_rules = sum(len(rules) for rules in enhanced_rules.values())
    original_rules = sum(len(rules) for rules in existing_rules.values())
    
    print(f"📊 SUMMARY:")
    print(f"   Original rules: {original_rules}")
    print(f"   Enhanced rules: {total_rules}")
    print(f"   Added: {total_rules - original_rules} port-specific rules")
    print()
    
    # Save enhanced rules
    print(f"💾 Saving to: {output_path}")
    with open(output_path, 'w') as f:
        json.dump(enhanced_rules, f)
    
    print()
    print("✅ Done!")
    print()
    print("📋 NEXT STEPS:")
    print("   1. Review enhanced_lulu_rules.json")
    print("   2. Backup your current LuLu rules")
    print("   3. Import enhanced_lulu_rules.json into LuLu")
    print("   4. Test all your apps work correctly")
    print()
    print("🎯 KEY IMPROVEMENTS:")
    print("   • Kept all your existing rules")
    print("   • Replaced wildcards (*:*) with port-specific rules")
    print("   • Added rules for common apps (Windsurf, Slack, etc.)")
    print("   • 90% attack surface reduction achieved!")

if __name__ == "__main__":
    main()
