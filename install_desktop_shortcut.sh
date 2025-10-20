#!/bin/bash
# Install Adaptive Firewall shortcut to Desktop

echo "🛡️  Installing Adaptive Firewall Desktop Shortcut"
echo "=================================================="
echo ""

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DESKTOP="$HOME/Desktop"

# Create the launcher command
cat > "$DESKTOP/🛡️ Adaptive Firewall.command" << 'EOF'
#!/bin/bash
cd "/Users/meep/Documents/LuluFirewallGenerator-Public"

clear
echo "🛡️  ADAPTIVE FIREWALL"
echo "========================================================================"
echo ""
echo "This firewall automatically:"
echo "  ✅ Detects pip/npm package installs"
echo "  ✅ Temporarily allows required endpoints (pypi.org, github.com)"
echo "  ✅ Monitors process completion"
echo "  ✅ Re-blocks immediately when done"
echo ""
echo "No manual clicking. No wildcards. No forgetting."
echo ""
echo "========================================================================"
echo ""
echo "Starting in 3 seconds... (Press Ctrl+C to cancel)"
sleep 3

sudo python3 lulu_auto_updater.py

echo ""
echo "Adaptive firewall stopped."
echo ""
echo "Logs: ~/.lulu_auto_updater/updater.log"
echo "Backups: ~/.lulu_auto_updater/"
echo ""
echo "Press any key to close..."
read -n 1
EOF

# Make executable
chmod +x "$DESKTOP/🛡️ Adaptive Firewall.command"

echo "✅ Desktop shortcut created!"
echo ""
echo "📍 Location: $DESKTOP/🛡️ Adaptive Firewall.command"
echo ""
echo "To use:"
echo "  1. Double-click the '🛡️ Adaptive Firewall' icon on your Desktop"
echo "  2. Enter your password when prompted"
echo "  3. Type 'yes' to start monitoring"
echo "  4. Use your apps normally!"
echo ""
echo "The firewall will automatically handle pip/npm installs."
echo ""
