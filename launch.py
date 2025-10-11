#!/usr/bin/env python3
"""
ActivityMonitorDefenseMonster Launcher
Quick launcher for the ultimate firewall generator
"""

import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if PyQt6 is installed"""
    try:
        import PyQt6
        print("✅ PyQt6 is installed")
        return True
    except ImportError:
        print("❌ PyQt6 not found")
        print("📦 Install with: pip3 install PyQt6")
        return False

def launch_gui():
    """Launch the enhanced GUI"""
    script_dir = Path(__file__).parent
    gui_script = script_dir / "enhanced_gui_v2.py"
    
    if gui_script.exists():
        print("🚀 Launching ActivityMonitorDefenseMonster GUI...")
        subprocess.run([sys.executable, str(gui_script)])
    else:
        print("❌ GUI script not found!")

def main():
    """Main launcher"""
    print("🛡️ ACTIVITYMONITORDEFENSEMONSTER LAUNCHER")
    print("=" * 50)
    print("The Ultimate App-Based Firewall Generator")
    print()
    
    if check_requirements():
        launch_gui()
    else:
        print("\n📋 Setup Instructions:")
        print("1. Install PyQt6: pip3 install PyQt6")
        print("2. Run launcher again: python3 launch.py")

if __name__ == "__main__":
    main()
