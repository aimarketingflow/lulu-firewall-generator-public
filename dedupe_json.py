#!/usr/bin/env python3
"""
Deduplicate JSON Rules File
Removes duplicate rules within each app
"""

import json
import sys
from collections import defaultdict

def dedupe_app_rules(rules_list):
    """Deduplicate rules for a single app"""
    # Group by endpoint address
    by_endpoint = defaultdict(list)
    
    for rule in rules_list:
        addr = rule['endpointAddr']
        by_endpoint[addr].append(rule)
    
    deduped = []
    
    for addr, rules in by_endpoint.items():
        # Check for wildcard port
        wildcard_port = None
        specific_ports = []
        
        for rule in rules:
            if rule['endpointPort'] == '*':
                if not wildcard_port:
                    wildcard_port = rule
                elif rule['action'] == '0' and wildcard_port['action'] == '1':
                    wildcard_port = rule  # Prefer BLOCK
            else:
                specific_ports.append(rule)
        
        # If wildcard port exists, only use that
        if wildcard_port:
            deduped.append(wildcard_port)
        else:
            # Dedupe specific ports
            seen_ports = set()
            for rule in specific_ports:
                port = rule['endpointPort']
                if port not in seen_ports:
                    deduped.append(rule)
                    seen_ports.add(port)
    
    return deduped

def dedupe_json_file(input_file, output_file=None):
    """Deduplicate entire JSON rules file"""
    print(f"🔍 Loading: {input_file}")
    
    with open(input_file) as f:
        rules = json.load(f)
    
    print(f"   Found {len(rules)} apps")
    print()
    
    total_before = sum(len(r) for r in rules.values())
    
    # Dedupe each app
    deduped_rules = {}
    removed_count = 0
    
    for app_key, app_rules in rules.items():
        before = len(app_rules)
        deduped = dedupe_app_rules(app_rules)
        after = len(deduped)
        
        if before != after:
            removed = before - after
            removed_count += removed
            print(f"  🧹 {app_key[:50]}...")
            print(f"     Removed {removed} duplicate(s)")
        
        deduped_rules[app_key] = deduped
    
    total_after = sum(len(r) for r in deduped_rules.values())
    
    print()
    print(f"📊 SUMMARY:")
    print(f"   Rules before: {total_before}")
    print(f"   Rules after: {total_after}")
    print(f"   Removed: {removed_count} duplicates")
    print()
    
    # Save
    if not output_file:
        output_file = input_file.replace('.json', '-DEDUPED.json')
        if output_file == input_file:
            output_file = input_file.replace('.json', '') + '-DEDUPED.json'
    
    with open(output_file, 'w') as f:
        json.dump(deduped_rules, f, indent=2)
    
    print(f"💾 Saved to: {output_file}")
    
    return output_file

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 dedupe_json.py <input.json> [output.json]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        result = dedupe_json_file(input_file, output_file)
        print()
        print("✅ Done! Import this file into LuLu:")
        print(f"   {result}")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
