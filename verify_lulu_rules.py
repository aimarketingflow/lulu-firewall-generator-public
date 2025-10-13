#!/usr/bin/env python3
"""
Verify LuLu Rules - Shows what's actually imported
"""

import json
import sys

def verify_rules(rules_file):
    """Verify rules in a JSON file"""
    with open(rules_file) as f:
        rules = json.load(f)
    
    print("🔍 LuLu Rules Verification")
    print("=" * 70)
    print()
    
    # Find Windsurf entries
    windsurf_keys = [k for k in rules.keys() if 'windsurf' in k.lower() or 'language_server' in k.lower()]
    
    if not windsurf_keys:
        print("❌ No Windsurf rules found!")
        return
    
    print(f"✅ Found {len(windsurf_keys)} Windsurf components")
    print()
    
    # Check each component
    for key in windsurf_keys:
        component_name = key.split(':')[0]
        rules_list = rules[key]
        
        print(f"📱 {component_name}")
        print(f"   Total rules: {len(rules_list)}")
        
        # Check for duplicates
        seen = set()
        duplicates = []
        for rule in rules_list:
            rule_key = f"{rule['endpointAddr']}:{rule['endpointPort']}"
            if rule_key in seen:
                duplicates.append(rule_key)
            seen.add(rule_key)
        
        if duplicates:
            print(f"   ⚠️  DUPLICATES FOUND: {len(duplicates)}")
            for dup in duplicates:
                print(f"      • {dup}")
        else:
            print(f"   ✅ No duplicates")
        
        # Show rules
        for i, rule in enumerate(rules_list, 1):
            action = 'BLOCK' if rule['action'] == '0' else 'ALLOW'
            addr = rule['endpointAddr']
            port = rule['endpointPort']
            print(f"   {i}. {action}: {addr}:{port}")
        
        print()
    
    # Summary
    print("📊 SUMMARY:")
    print(f"   Total apps: {len(rules)}")
    print(f"   Total rules: {sum(len(r) for r in rules.values())}")
    print(f"   Windsurf components: {len(windsurf_keys)}")
    
    # Check for GitHub wildcards
    github_wildcards = 0
    for key in windsurf_keys:
        for rule in rules[key]:
            if '*.github.com' in rule['endpointAddr'] and rule['endpointPort'] == '*':
                github_wildcards += 1
                break
    
    print(f"   Components with GitHub wildcard ports: {github_wildcards}/{len(windsurf_keys)}")

if __name__ == "__main__":
    rules_file = sys.argv[1] if len(sys.argv) > 1 else "enhanced_lulu_rules-v9-DEDUPED.json"
    
    try:
        verify_rules(rules_file)
    except FileNotFoundError:
        print(f"❌ File not found: {rules_file}")
    except Exception as e:
        print(f"❌ Error: {e}")
