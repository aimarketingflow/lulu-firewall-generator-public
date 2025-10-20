#!/usr/bin/env python3
"""
Safe Demo Mode - Shows what would happen WITHOUT touching LuLu or PF
Perfect for testing the detection logic
"""

import subprocess
import time
import sys
from datetime import datetime

class SafeDemoFirewall:
    def __init__(self):
        self.detected_actions = []
        self.temp_allows = {}
        
    def monitor_processes(self):
        """Monitor for pip/npm/git processes"""
        print("\n🔍 SAFE DEMO MODE - Monitoring processes...")
        print("=" * 70)
        print("This will DETECT actions but NOT modify any firewall")
        print("Press Ctrl+C to stop")
        print("=" * 70)
        print()
        
        seen_pids = set()
        
        try:
            while True:
                result = subprocess.run(
                    ['ps', '-eo', 'pid,ppid,comm'],
                    capture_output=True,
                    text=True
                )
                
                for line in result.stdout.split('\n')[1:]:
                    parts = line.split()
                    if len(parts) >= 3:
                        pid = parts[0]
                        ppid = parts[1]
                        name = parts[2]
                        
                        if pid in seen_pids:
                            continue
                        
                        # Check for pip/npm/git
                        if any(proc in name.lower() for proc in ['pip', 'pip3', 'npm', 'yarn', 'git']):
                            seen_pids.add(pid)
                            
                            # Get parent process
                            parent_result = subprocess.run(
                                ['ps', '-p', ppid, '-o', 'comm='],
                                capture_output=True,
                                text=True
                            )
                            parent_name = parent_result.stdout.strip()
                            
                            # Check if parent is Windsurf/VSCode
                            if any(app in parent_name for app in ['Windsurf', 'VSCode', 'Code']):
                                self.handle_detection(name, pid, parent_name)
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Monitoring stopped")
            self.show_summary()
    
    def handle_detection(self, process_name, pid, parent_app):
        """Handle detected action"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        print(f"\n{'='*70}")
        print(f"🎯 DETECTION at {timestamp}")
        print(f"{'='*70}")
        print(f"Process: {process_name} (PID: {pid})")
        print(f"Parent: {parent_app}")
        print()
        
        # Determine action type
        if 'pip' in process_name.lower():
            action = 'python_install'
            endpoints = [
                'pypi.org:443',
                'files.pythonhosted.org:443',
                'github.com:443',
                'raw.githubusercontent.com:443'
            ]
        elif 'npm' in process_name.lower() or 'yarn' in process_name.lower():
            action = 'npm_install'
            endpoints = [
                'registry.npmjs.org:443',
                'github.com:443',
                'raw.githubusercontent.com:443'
            ]
        elif 'git' in process_name.lower():
            action = 'git_clone'
            endpoints = [
                'github.com:443',
                'gitlab.com:443',
                'bitbucket.org:443'
            ]
        else:
            return
        
        print(f"📋 Action Type: {action}")
        print()
        print("⏰ WOULD TEMPORARILY ALLOW (5 minutes):")
        for endpoint in endpoints:
            print(f"  ✅ {endpoint}")
            print(f"     🔒 Specific endpoint (not wildcard)")
            print(f"     ⏱️  Auto-cleanup when process completes")
        
        print()
        print("🔍 COMPARISON:")
        print("  ❌ Manual LuLu: Creates *:* wildcard rules")
        print("  ✅ Our Tool: Specific endpoints only")
        print()
        print("  ❌ Manual: Must remember to re-block")
        print("  ✅ Our Tool: Automatic cleanup")
        print()
        print(f"{'='*70}")
        
        self.detected_actions.append({
            'process': process_name,
            'pid': pid,
            'parent': parent_app,
            'action': action,
            'endpoints': endpoints,
            'timestamp': timestamp
        })
    
    def show_summary(self):
        """Show summary of detected actions"""
        print("\n" + "="*70)
        print("📊 DETECTION SUMMARY")
        print("="*70)
        print()
        
        if not self.detected_actions:
            print("No actions detected during monitoring")
        else:
            print(f"Total detections: {len(self.detected_actions)}")
            print()
            
            for i, detection in enumerate(self.detected_actions, 1):
                print(f"{i}. {detection['action']} at {detection['timestamp']}")
                print(f"   Process: {detection['process']} (PID: {detection['pid']})")
                print(f"   Parent: {detection['parent']}")
                print(f"   Would allow: {len(detection['endpoints'])} endpoints")
                print()
        
        print("="*70)
        print()
        print("💡 This was SAFE DEMO MODE")
        print("   No firewall rules were actually modified")
        print()
        print("To enable real firewall integration:")
        print("  sudo python3 enable_pf_integration.py")
        print()

def main():
    print("\n🛡️  SMART ADAPTIVE FIREWALL - SAFE DEMO MODE")
    print("=" * 70)
    print()
    print("This mode will:")
    print("  ✅ Detect pip/npm/git processes")
    print("  ✅ Show what WOULD be allowed")
    print("  ✅ NOT modify LuLu")
    print("  ✅ NOT modify packet filter")
    print("  ✅ Completely safe for testing")
    print()
    print("Try it:")
    print("  1. Start this demo")
    print("  2. In Windsurf, run: pip install requests")
    print("  3. Watch the detection happen!")
    print()
    
    demo = SafeDemoFirewall()
    demo.monitor_processes()

if __name__ == "__main__":
    main()
