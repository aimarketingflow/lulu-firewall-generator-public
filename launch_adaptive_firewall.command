#!/bin/bash
# Adaptive Firewall Launcher
# Double-click this file to start the adaptive firewall

cd "$(dirname "$0")"

echo "🛡️  ADAPTIVE FIREWALL LAUNCHER"
echo "================================"
echo ""
echo "Starting adaptive firewall..."
echo ""
echo "This will:"
echo "  ✅ Detect pip/npm installs"
echo "  ✅ Temporarily allow required endpoints"
echo "  ✅ Re-block immediately when done"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run with sudo
sudo python3 lulu_auto_updater.py

echo ""
echo "Adaptive firewall stopped."
echo "Press any key to close..."
read -n 1
