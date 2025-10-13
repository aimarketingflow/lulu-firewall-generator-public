#!/usr/bin/env python3
"""
Smart Rule Merger - Preserves all original rules while enhancing with port-specific rules
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from collections import defaultdict

def get_timestamp():
    """Get current timestamp in LuLu format"""
    now = datetime.now().astimezone()
    timestamp = now.strftime("%Y-%m-%dT%H:%M:%S%z")
    return timestamp[:-2] + ':' + timestamp[-2:] if len(timestamp) > 2 else timestamp

def deduplicate_rules(rules_list):
    """
    Smart deduplication:
    - Wildcard port (*) supersedes specific ports for same endpoint
    - Prefer BLOCK over ALLOW for wildcards
    """
    by_endpoint = defaultdict(list)
    
    for rule in rules_list:
        addr = rule['endpointAddr']
        by_endpoint[addr].append(rule)
    
    deduped = []
    
    for addr, rules in by_endpoint.items():
        # Find wildcard port rule
        wildcard_port = None
        specific_ports = []
        
        for rule in rules:
            if rule['endpointPort'] == '*':
                # LuLu inverts: 0=BLOCK, 1=ALLOW in our JSON
                # Prefer BLOCK (0) over ALLOW (1) for wildcards
                if not wildcard_port or (rule['action'] == '0' and wildcard_port['action'] == '1'):
                    wildcard_port = rule
            else:
                specific_ports.append(rule)
        
        # If wildcard exists, only use that
        if wildcard_port:
            deduped.append(wildcard_port)
        else:
            # Dedupe specific ports
            seen_ports = {}
            for rule in specific_ports:
                port = rule['endpointPort']
                if port not in seen_ports:
                    seen_ports[port] = rule
                    deduped.append(rule)
    
    return deduped

def enhance_rules(existing_rules, manual_enhancements):
    """
    Enhance existing rules with manual port-specific rules
    
    For each app in manual_enhancements:
    1. Find matching keys in existing_rules
    2. Add new port-specific rules
    3. Deduplicate
    """
    enhanced = {}
    
    # Copy all existing rules first
    for key, rules in existing_rules.items():
        enhanced[key] = list(rules)  # Make a copy
    
    # Apply enhancements
    for bundle_id, config in manual_enhancements.items():
        app_name = config["name"]
        endpoints = config["endpoints"]
        also_update = config.get("also_update", [])
        
        # Find all matching keys
        matching_keys = []
        
        # Direct match
        for key in existing_rules.keys():
            if bundle_id in key:
                matching_keys.append(key)
        
        # Also update matches
        for extra_key in also_update:
            for key in existing_rules.keys():
                if extra_key in key and key not in matching_keys:
                    matching_keys.append(key)
        
        if not matching_keys:
            print(f"  ⚠️  No existing rules found for {app_name}, skipping")
            continue
        
        print(f"  ✅ Enhancing {app_name} ({len(matching_keys)} components)")
        
        # Enhance each matching key
        for key in matching_keys:
            original_rules = enhanced[key]
            
            # Create new port-specific rules
            new_rules = []
            for endpoint, port, is_regex, action in endpoints:
                # Skip if this exact rule already exists
                exists = any(
                    r['endpointAddr'] == endpoint and 
                    r['endpointPort'] == port and 
                    r['action'] == action
                    for r in original_rules
                )
                
                if not exists:
                    # Get template from first rule
                    template = original_rules[0]
                    
                    new_rule = {
                        "key": template["key"],
                        "uuid": str(uuid.uuid4()).upper(),
                        "path": template["path"],
                        "name": template["name"],
                        "endpointAddr": endpoint,
                        "endpointPort": port,
                        "creation": get_timestamp(),
                        "isEndpointAddrRegex": "1" if is_regex else "0",
                        "type": template.get("type", "1"),
                        "scope": "0",
                        "action": action
                    }
                    
                    if "csInfo" in template:
                        new_rule["csInfo"] = template["csInfo"]
                    
                    new_rules.append(new_rule)
            
            # Combine and deduplicate
            combined = original_rules + new_rules
            deduped = deduplicate_rules(combined)
            
            enhanced[key] = deduped
            
            removed = len(combined) - len(deduped)
            if removed > 0:
                print(f"     [{key[:30]}...] Added {len(new_rules)}, removed {removed} duplicates")
    
    return enhanced

def main():
    print("🛡️  Smart LuLu Rule Merger")
    print("=" * 60)
    print()
    
    # Load existing rules
    existing_path = "/Users/meep/Documents/_ToInvestigate-Offline-Attacks·/ExistingLuluRulesforOps/rules-101225.json"
    print(f"📂 Loading existing rules...")
    
    with open(existing_path) as f:
        existing_rules = json.load(f)
    
    print(f"   Found {len(existing_rules)} apps")
    original_count = sum(len(r) for r in existing_rules.values())
    print(f"   Total rules: {original_count}")
    print()
    
    # Manual enhancements (Windsurf with all ports)
    print("🔧 Applying enhancements...")
    print()
    
    enhancements = {
        "com.exafunction.windsurf": {
            "name": "Windsurf",
            "endpoints": [
                ("*", "*", False, "0"),  # BLOCK all (LuLu inverts: 0→BLOCK)
                ("*.github.com", "*", True, "1"),  # ALLOW GitHub (LuLu inverts: 1→ALLOW)
                ("*.githubusercontent.com", "*", True, "1"),
                ("vscode.dev", "*", False, "1"),  # VSCode auth
                ("*.vscode.dev", "*", True, "1"),  # VSCode subdomains
                ("github.dev", "*", False, "1"),  # GitHub Codespaces
                ("api.codeium.com", "443", False, "1"),
                ("inference.codeium.com", "443", False, "1"),
                ("*.googleusercontent.com", "443", True, "1"),
                ("*.windsurf.com", "*", True, "1")  # ALLOW Windsurf (LuLu inverts: 1→ALLOW)
            ],
            "also_update": [
                "com.exafunction.windsurf.helper",
                "com.github.Electron.helper",
                "language_server_macos_arm"
            ]
        }
    }
    
    # Enhance
    enhanced_rules = enhance_rules(existing_rules, enhancements)
    
    print()
    print("🧹 Final deduplication...")
    
    # Final dedupe pass
    for key in enhanced_rules.keys():
        enhanced_rules[key] = deduplicate_rules(enhanced_rules[key])
    
    final_count = sum(len(r) for r in enhanced_rules.values())
    
    print()
    print("📊 SUMMARY:")
    print(f"   Apps: {len(enhanced_rules)}")
    print(f"   Original rules: {original_count}")
    print(f"   Final rules: {final_count}")
    print(f"   Added: {final_count - original_count}")
    print()
    
    # Save
    output_path = "enhanced_lulu_rules-v14-GITHUB-AUTH.json"
    with open(output_path, 'w') as f:
        json.dump(enhanced_rules, f, indent=2)
    
    print(f"💾 Saved to: {output_path}")
    print()
    
    # Verify Windsurf
    print("🔍 Verifying Windsurf components...")
    windsurf_keys = [k for k in enhanced_rules.keys() if 'windsurf' in k.lower() or ('language_server' in k.lower() and 'EXAFUNCTION' in k) or ('electron' in k.lower() and 'EXAFUNCTION' in k)]
    
    for key in sorted(windsurf_keys):
        rules = enhanced_rules[key]
        print(f"  ✅ {key[:50]}...")
        print(f"     Rules: {len(rules)}")
        
        # Check for duplicates
        endpoints = [f"{r['endpointAddr']}:{r['endpointPort']}" for r in rules]
        if len(endpoints) != len(set(endpoints)):
            print(f"     ⚠️  HAS DUPLICATES!")
        else:
            print(f"     ✅ No duplicates")

if __name__ == "__main__":
    main()
