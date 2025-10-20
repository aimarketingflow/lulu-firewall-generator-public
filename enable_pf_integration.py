#!/usr/bin/env python3
"""
Enable packet filter (pf) integration for Smart Adaptive Firewall
This works ALONGSIDE LuLu without interfering with it

Architecture:
- LuLu: Application-level firewall (blocks by app)
- Our PF rules: Network-level firewall (blocks by endpoint)
- Both work together for defense in depth
"""

import os
import sys
import subprocess
from pathlib import Path

def check_pf_status():
    """Check if packet filter is enabled"""
    result = subprocess.run(
        ['sudo', 'pfctl', '-s', 'info'],
        capture_output=True,
        text=True
    )
    
    if 'Status: Enabled' in result.stdout:
        print("✅ Packet filter is enabled")
        return True
    else:
        print("⚠️  Packet filter is disabled")
        return False

def create_pf_anchor():
    """Create PF anchor for our rules"""
    print("\n📝 Creating PF anchor for smart firewall...")
    
    # Create anchor configuration
    anchor_conf = """
# Smart Adaptive Firewall Anchor
# Temporary rules for detected actions

# Default: block nothing (we add rules dynamically)
"""
    
    anchor_file = Path("/etc/pf.anchors/smart_firewall")
    
    # Write anchor file
    try:
        with open('/tmp/smart_firewall_anchor', 'w') as f:
            f.write(anchor_conf)
        
        subprocess.run(
            ['sudo', 'cp', '/tmp/smart_firewall_anchor', str(anchor_file)],
            check=True
        )
        
        print(f"✅ Created anchor file: {anchor_file}")
        
    except Exception as e:
        print(f"❌ Error creating anchor: {e}")
        return False
    
    return True

def add_anchor_to_pf_conf():
    """Add our anchor to main pf.conf"""
    print("\n📝 Adding anchor to pf.conf...")
    
    pf_conf = Path("/etc/pf.conf")
    
    # Check if already added
    try:
        with open(pf_conf) as f:
            content = f.read()
            if 'smart_firewall' in content:
                print("✅ Anchor already in pf.conf")
                return True
    except:
        pass
    
    # Add anchor line
    anchor_line = "\nanchor \"smart_firewall\"\nload anchor \"smart_firewall\" from \"/etc/pf.anchors/smart_firewall\"\n"
    
    try:
        # Backup original
        subprocess.run(
            ['sudo', 'cp', str(pf_conf), str(pf_conf) + '.backup'],
            check=True
        )
        
        # Append anchor
        with open('/tmp/pf_conf_addition', 'w') as f:
            f.write(anchor_line)
        
        subprocess.run(
            ['sudo', 'sh', '-c', f'cat /tmp/pf_conf_addition >> {pf_conf}'],
            check=True
        )
        
        print("✅ Added anchor to pf.conf")
        return True
        
    except Exception as e:
        print(f"❌ Error modifying pf.conf: {e}")
        return False

def reload_pf():
    """Reload packet filter configuration"""
    print("\n🔄 Reloading packet filter...")
    
    try:
        subprocess.run(
            ['sudo', 'pfctl', '-f', '/etc/pf.conf'],
            check=True
        )
        print("✅ Packet filter reloaded")
        return True
    except Exception as e:
        print(f"❌ Error reloading pf: {e}")
        return False

def test_pf_rule():
    """Test adding a temporary rule"""
    print("\n🧪 Testing rule addition...")
    
    test_rule = "pass out proto tcp from any to pypi.org port 443"
    
    try:
        result = subprocess.run(
            ['sudo', 'pfctl', '-a', 'smart_firewall', '-f', '-'],
            input=test_rule.encode(),
            capture_output=True
        )
        
        if result.returncode == 0:
            print("✅ Test rule added successfully")
            print(f"   Rule: {test_rule}")
            
            # Remove test rule
            subprocess.run(
                ['sudo', 'pfctl', '-a', 'smart_firewall', '-F', 'all'],
                check=True
            )
            print("✅ Test rule removed")
            return True
        else:
            print(f"❌ Error adding test rule: {result.stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing rule: {e}")
        return False

def show_status():
    """Show current PF status"""
    print("\n📊 Current Status:")
    print("-" * 60)
    
    # Show PF info
    result = subprocess.run(
        ['sudo', 'pfctl', '-s', 'info'],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    
    # Show our anchor rules
    print("\n📋 Smart Firewall Anchor Rules:")
    result = subprocess.run(
        ['sudo', 'pfctl', '-a', 'smart_firewall', '-s', 'rules'],
        capture_output=True,
        text=True
    )
    
    if result.stdout.strip():
        print(result.stdout)
    else:
        print("  (No active rules)")

def main():
    print("\n🛡️  SMART ADAPTIVE FIREWALL - PF INTEGRATION SETUP")
    print("=" * 60)
    print()
    print("This will configure macOS packet filter (pf) to work")
    print("ALONGSIDE LuLu for enhanced protection.")
    print()
    print("⚠️  This requires sudo access")
    print()
    
    if os.geteuid() != 0:
        print("❌ Please run with sudo:")
        print("   sudo python3 enable_pf_integration.py")
        sys.exit(1)
    
    input("Press Enter to continue or Ctrl+C to cancel...")
    
    # Check PF status
    if not check_pf_status():
        print("\n⚠️  Packet filter is not enabled.")
        print("This is normal on macOS - it will be enabled when we add rules.")
    
    # Create anchor
    if not create_pf_anchor():
        print("\n❌ Setup failed at anchor creation")
        sys.exit(1)
    
    # Add to pf.conf
    if not add_anchor_to_pf_conf():
        print("\n❌ Setup failed at pf.conf modification")
        sys.exit(1)
    
    # Reload PF
    if not reload_pf():
        print("\n❌ Setup failed at PF reload")
        sys.exit(1)
    
    # Test rule addition
    if not test_pf_rule():
        print("\n⚠️  Rule testing failed, but setup may still work")
    
    # Show status
    show_status()
    
    print("\n" + "=" * 60)
    print("✅ SETUP COMPLETE!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Run: sudo python3 smart_adaptive_firewall.py")
    print("2. Select option 1 to start monitoring")
    print("3. Install a Python package in Windsurf")
    print("4. Watch automatic detection and rule application!")
    print()
    print("To disable:")
    print("  sudo pfctl -a smart_firewall -F all  # Clear rules")
    print("  sudo pfctl -d                         # Disable PF")
    print()

if __name__ == "__main__":
    main()
