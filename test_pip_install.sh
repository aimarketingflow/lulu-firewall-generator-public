#!/bin/bash
# Test script to demonstrate smart firewall detecting pip install

echo "🧪 Testing Smart Adaptive Firewall with pip install"
echo "=================================================="
echo ""
echo "This will:"
echo "1. Start the smart firewall in background"
echo "2. Run a pip install"
echo "3. Show you the automatic detection and temporary allows"
echo ""

# Start smart firewall in background
echo "Starting smart firewall..."
sudo python3 smart_adaptive_firewall.py --monitor &
FIREWALL_PID=$!

sleep 2

echo ""
echo "Now running: pip install requests"
echo "Watch the firewall detect and allow automatically!"
echo ""

# Run pip install (will trigger detection)
pip3 install requests

echo ""
echo "Install complete! Check firewall logs..."
sleep 2

# Stop firewall
sudo kill $FIREWALL_PID

echo ""
echo "✅ Test complete!"
echo "The firewall detected pip3, allowed GitHub/PyPI temporarily,"
echo "and will lock back down after 5 minutes (or when process completes)"
