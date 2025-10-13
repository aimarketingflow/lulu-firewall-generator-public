#!/bin/bash
# Complete Automated Rule Generation Pipeline
# NO PASSWORD REQUIRED (uses existing sysdiag)

set -e  # Exit on error

echo "🛡️  LuLu Complete Rule Generator"
echo "================================"
echo ""

# Step 1: Find or specify sysdiag
if [ -n "$1" ]; then
    SYSDIAG_DIR="$1"
    echo "📂 Using specified sysdiag: $SYSDIAG_DIR"
else
    echo "🔍 Searching for latest sysdiag..."
    SYSDIAG_DIR=$(find ~/Desktop ~/Documents /var/tmp -maxdepth 1 -name "sysdiagnose_*" -type d 2>/dev/null | sort -r | head -1)
    
    if [ -z "$SYSDIAG_DIR" ]; then
        echo "❌ No sysdiag found!"
        echo ""
        echo "Please run: sudo sysdiagnose -f ~/Desktop/"
        echo "Then run this script again."
        exit 1
    fi
    
    echo "✅ Found: $(basename $SYSDIAG_DIR)"
fi

echo ""

# Step 2: Auto-discover endpoints
echo "🔍 Step 1: Auto-discovering endpoints..."
python3 auto_discover_endpoints.py "$SYSDIAG_DIR"

if [ ! -f "auto_discovered_rules.json" ]; then
    echo "⚠️  No auto-discovered rules, continuing with manual rules only"
fi

echo ""

# Step 3: Merge and enhance
echo "🔄 Step 2: Merging with existing rules..."
python3 merge_and_enhance_rules.py

echo ""

# Step 4: Show results
LATEST_RULES=$(ls -t enhanced_lulu_rules-*.json 2>/dev/null | head -1)

if [ -z "$LATEST_RULES" ]; then
    echo "❌ No rules generated"
    exit 1
fi

echo "✅ COMPLETE!"
echo ""
echo "📁 Generated: $LATEST_RULES"
echo ""

# Copy to desktop for easy access
cp "$LATEST_RULES" ~/Desktop/
echo "📋 Copied to: ~/Desktop/$LATEST_RULES"
echo ""

# Show summary
echo "📊 SUMMARY:"
python3 << EOF
import json

with open("$LATEST_RULES") as f:
    rules = json.load(f)

print(f"  Total apps: {len(rules)}")
print(f"  Total rules: {sum(len(r) for r in rules.values())}")

# Count default-deny apps
default_deny = sum(1 for r in rules.values() if any(
    rule.get('endpointAddr') == '*' and rule.get('endpointPort') == '*' and rule.get('action') == '0'
    for rule in r
))
print(f"  Apps with default-deny: {default_deny}")

# Show top 5 apps by rule count
print("")
print("  Top 5 apps by rules:")
sorted_apps = sorted(rules.items(), key=lambda x: len(x[1]), reverse=True)[:5]
for key, app_rules in sorted_apps:
    app_name = app_rules[0].get('name', key.split(':')[0])
    print(f"    • {app_name}: {len(app_rules)} rules")
EOF

echo ""
echo "🎯 NEXT STEPS:"
echo "  1. Review: ~/Desktop/$LATEST_RULES"
echo "  2. Backup current LuLu rules"
echo "  3. Import into LuLu → Rules → Import"
echo "  4. Test your apps!"
echo ""
echo "💡 TIP: Keep LuLu logs open to catch any missing endpoints:"
echo "   tail -f /Library/Logs/LuLu.log | grep BLOCK"
