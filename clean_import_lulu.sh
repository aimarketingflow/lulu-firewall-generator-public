#!/bin/bash
# Clean LuLu Import - Clears cache and imports fresh rules

echo "🧹 LuLu Clean Import"
echo "===================="
echo ""

# Check if rules file provided
if [ -z "$1" ]; then
    # Find latest rules file
    RULES_FILE=$(ls -t ~/Desktop/enhanced_lulu_rules-*.json 2>/dev/null | head -1)
    if [ -z "$RULES_FILE" ]; then
        echo "❌ No rules file found on Desktop"
        echo "Usage: $0 [rules_file.json]"
        exit 1
    fi
else
    RULES_FILE="$1"
fi

echo "📁 Rules file: $(basename $RULES_FILE)"
echo ""

# Step 1: Backup current rules
echo "💾 Step 1: Backing up current LuLu rules..."
BACKUP_FILE=~/Desktop/lulu_backup_$(date +%Y%m%d_%H%M%S).json
if [ -f ~/Library/Objective-See/LuLu/rules.plist ]; then
    cp ~/Library/Objective-See/LuLu/rules.plist "$BACKUP_FILE"
    echo "   ✅ Backup saved: $(basename $BACKUP_FILE)"
else
    echo "   ⚠️  No existing rules found"
fi
echo ""

# Step 2: Stop LuLu
echo "🛑 Step 2: Stopping LuLu..."
killall LuLu 2>/dev/null
sleep 2
echo "   ✅ LuLu stopped"
echo ""

# Step 3: Clear LuLu cache
echo "🧹 Step 3: Clearing LuLu cache..."
rm -rf ~/Library/Caches/com.objective-see.lulu* 2>/dev/null
rm -rf ~/Library/Caches/LuLu* 2>/dev/null
rm -rf /tmp/com.objective-see.lulu* 2>/dev/null
echo "   ✅ Cache cleared"
echo ""

# Step 4: Clear existing rules (optional - commented out for safety)
# echo "🗑️  Step 4: Clearing existing rules..."
# rm -f ~/Library/Objective-See/LuLu/rules.plist
# echo "   ✅ Rules cleared"
# echo ""

# Step 5: Start LuLu
echo "🚀 Step 4: Starting LuLu..."
open -a LuLu
sleep 3
echo "   ✅ LuLu started"
echo ""

# Step 6: Instructions for import
echo "📋 Step 5: Import Rules Manually"
echo "================================"
echo ""
echo "1. Open LuLu (should be running now)"
echo "2. Go to: Rules → Import"
echo "3. Select: $(basename $RULES_FILE)"
echo "4. Review the rules"
echo "5. Click Import"
echo ""
echo "💡 TIP: If you still see duplicates:"
echo "   1. Quit LuLu completely"
echo "   2. Delete: ~/Library/Objective-See/LuLu/rules.plist"
echo "   3. Run this script again"
echo ""
echo "📁 Rules file location: $RULES_FILE"
