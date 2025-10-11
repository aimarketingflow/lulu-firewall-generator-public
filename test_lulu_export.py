#!/usr/bin/env python3
"""
Test script to verify LuLu format export
"""

import json
from rule_generator import MurusRuleGenerator

def test_lulu_export():
    """Test LuLu format export"""
    print("🧪 Testing LuLu Format Export")
    print("=" * 60)
    
    # Create a simple test ruleset
    rule_gen = MurusRuleGenerator()
    
    test_ruleset = {
        "metadata": {
            "generated_by": "Test",
            "timestamp": "2025-10-08T16:00:00",
            "rule_count": 3
        },
        "rules": [
            {
                "id": 1001,
                "action": "allow",
                "process": {
                    "name": "Safari",
                    "path": "/Applications/Safari.app/Contents/MacOS/Safari"
                }
            },
            {
                "id": 1002,
                "action": "allow",
                "process": {
                    "name": "Windsurf",
                    "path": "/Applications/Windsurf.app/Contents/MacOS/Windsurf"
                }
            },
            {
                "id": 1003,
                "action": "block",
                "process": {
                    "name": "cloudd",
                    "path": "/usr/libexec/cloudd"
                }
            }
        ]
    }
    
    # Export to LuLu format
    output_file = "test_lulu_output.json"
    rule_gen.export_to_lulu_format(test_ruleset, output_file)
    
    # Read and display the output
    print("\n📄 Generated LuLu Format:")
    print("-" * 60)
    with open(output_file, 'r') as f:
        content = f.read()
        print(content)
    
    # Parse and verify structure
    print("\n✅ Verifying Structure:")
    print("-" * 60)
    with open(output_file, 'r') as f:
        lulu_rules = json.load(f)
    
    print(f"Total rule groups: {len(lulu_rules)}")
    for key, rules in lulu_rules.items():
        print(f"\n  📦 {key}:")
        for rule in rules:
            action_text = "ALLOW" if rule['action'] == 0 else "BLOCK"
            print(f"    • {action_text}: {rule['name']} ({rule['path']})")
    
    print("\n🎉 Test completed successfully!")
    print(f"Output saved to: {output_file}")

if __name__ == "__main__":
    test_lulu_export()
