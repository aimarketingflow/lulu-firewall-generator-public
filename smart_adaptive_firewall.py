#!/usr/bin/env python3
"""
Smart Adaptive Firewall
Detects specific app actions (like package installs) and temporarily allows required connections

Example: Windsurf installing Python packages
- Detects: pip/npm/yarn process spawned by Windsurf
- Allows: GitHub, PyPI, curl temporarily
- Locks down: After install completes
"""

import os
import sys
import json
import time
import subprocess
import threading
import re
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

# Try to import psutil, fall back to subprocess if not available
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print("⚠️  psutil not installed. Install with: pip3 install psutil")
    print("⚠️  Falling back to subprocess-based monitoring (less efficient)\n")

class SmartAdaptiveFirewall:
    def __init__(self):
        self.config_dir = Path.home() / ".smart_firewall"
        self.config_dir.mkdir(exist_ok=True)
        
        self.rules_file = self.config_dir / "rules.json"
        self.log_file = self.config_dir / "firewall.log"
        
        # Temporary allows with expiry times
        self.temp_allows = {}  # {(app, endpoint): expiry_time}
        
        # Action patterns to detect
        self.action_patterns = {
            'python_install': {
                'processes': ['pip', 'pip3', 'python', 'python3'],
                'parent_apps': ['Windsurf', 'VSCode', 'PyCharm'],
                'required_endpoints': [
                    'pypi.org:443',
                    'files.pythonhosted.org:443',
                    'github.com:443',
                    'raw.githubusercontent.com:443'
                ],
                'duration': 300  # 5 minutes
            },
            'npm_install': {
                'processes': ['npm', 'yarn', 'pnpm'],
                'parent_apps': ['Windsurf', 'VSCode', 'WebStorm'],
                'required_endpoints': [
                    'registry.npmjs.org:443',
                    'github.com:443',
                    'raw.githubusercontent.com:443'
                ],
                'duration': 300
            },
            'git_clone': {
                'processes': ['git'],
                'parent_apps': ['Windsurf', 'VSCode', 'Terminal'],
                'required_endpoints': [
                    'github.com:443',
                    'gitlab.com:443',
                    'bitbucket.org:443'
                ],
                'duration': 180  # 3 minutes
            }
        }
        
        self.monitoring = False
        self.detected_actions = []
    
    def log(self, message, level="INFO"):
        """Log message"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        # Color coding
        colors = {
            'INFO': '\033[94m',    # Blue
            'SUCCESS': '\033[92m', # Green
            'WARNING': '\033[93m', # Yellow
            'ERROR': '\033[91m',   # Red
            'DETECT': '\033[95m'   # Magenta
        }
        
        color = colors.get(level, '')
        reset = '\033[0m'
        
        print(f"{color}{log_entry.strip()}{reset}")
        
        with open(self.log_file, 'a') as f:
            f.write(log_entry)
    
    def start_monitoring(self):
        """Start monitoring for process spawns"""
        self.log("🔍 Starting smart adaptive firewall...", "INFO")
        self.log("Monitoring for: Python installs, npm installs, git clones", "INFO")
        self.monitoring = True
        
        # Start process monitor thread
        monitor_thread = threading.Thread(target=self._monitor_processes, daemon=True)
        monitor_thread.start()
        
        # Start cleanup thread
        cleanup_thread = threading.Thread(target=self._cleanup_expired, daemon=True)
        cleanup_thread.start()
        
        return monitor_thread
    
    def _monitor_processes(self):
        """Monitor for new processes that match action patterns"""
        seen_pids = set()
        
        while self.monitoring:
            try:
                if HAS_PSUTIL:
                    # Use psutil for efficient monitoring
                    for proc in psutil.process_iter(['pid', 'name', 'ppid']):
                        try:
                            pid = proc.info['pid']
                            name = proc.info['name']
                            ppid = proc.info['ppid']
                            
                            # Skip if we've already seen this process
                            if pid in seen_pids:
                                continue
                            
                            seen_pids.add(pid)
                            
                            # Check if this matches any action pattern
                            for action_name, pattern in self.action_patterns.items():
                                if name in pattern['processes']:
                                    # Get parent process
                                    try:
                                        parent = psutil.Process(ppid)
                                        parent_name = parent.name()
                                        
                                        # Check if parent is one of our monitored apps
                                        for app in pattern['parent_apps']:
                                            if app.lower() in parent_name.lower():
                                                self._handle_action_detected(
                                                    action_name,
                                                    app,
                                                    name,
                                                    pid,
                                                    pattern
                                                )
                                                break
                                    except:
                                        pass
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                else:
                    # Fall back to ps command
                    self._monitor_processes_ps(seen_pids)
                
                time.sleep(1)  # Check every second
                
            except Exception as e:
                self.log(f"Error monitoring processes: {e}", "ERROR")
    
    def _monitor_processes_ps(self, seen_pids):
        """Monitor processes using ps command (fallback)"""
        try:
            result = subprocess.run(
                ['ps', '-eo', 'pid,ppid,comm'],
                capture_output=True,
                text=True
            )
            
            for line in result.stdout.split('\n')[1:]:  # Skip header
                parts = line.split()
                if len(parts) >= 3:
                    pid = int(parts[0])
                    ppid = int(parts[1])
                    name = parts[2]
                    
                    if pid in seen_pids:
                        continue
                    
                    seen_pids.add(pid)
                    
                    # Check patterns
                    for action_name, pattern in self.action_patterns.items():
                        if any(proc in name for proc in pattern['processes']):
                            # Get parent name
                            parent_result = subprocess.run(
                                ['ps', '-p', str(ppid), '-o', 'comm='],
                                capture_output=True,
                                text=True
                            )
                            parent_name = parent_result.stdout.strip()
                            
                            for app in pattern['parent_apps']:
                                if app.lower() in parent_name.lower():
                                    self._handle_action_detected(
                                        action_name,
                                        app,
                                        name,
                                        pid,
                                        pattern
                                    )
                                    break
        except Exception as e:
            pass
    
    def _handle_action_detected(self, action_name, app_name, process_name, pid, pattern):
        """Handle detected action"""
        self.log(f"🎯 DETECTED: {action_name} - {app_name} spawned {process_name} (PID: {pid})", "DETECT")
        
        # Record detection
        detection = {
            'action': action_name,
            'app': app_name,
            'process': process_name,
            'pid': pid,
            'timestamp': datetime.now().isoformat()
        }
        self.detected_actions.append(detection)
        
        # Temporarily allow required endpoints
        self.log(f"⏰ Temporarily allowing {len(pattern['required_endpoints'])} endpoints for {pattern['duration']}s", "INFO")
        
        for endpoint in pattern['required_endpoints']:
            self._temporarily_allow(app_name, endpoint, pattern['duration'])
        
        # Monitor process completion
        monitor_thread = threading.Thread(
            target=self._monitor_process_completion,
            args=(pid, app_name, pattern),
            daemon=True
        )
        monitor_thread.start()
    
    def _temporarily_allow(self, app_name, endpoint, duration_seconds):
        """Temporarily allow an endpoint"""
        expiry = datetime.now() + timedelta(seconds=duration_seconds)
        key = (app_name, endpoint)
        
        self.temp_allows[key] = expiry
        
        self.log(f"  ✅ ALLOW: {app_name} → {endpoint} (expires in {duration_seconds}s)", "SUCCESS")
        
        # In a real implementation, this would:
        # 1. Add rule to actual firewall (iptables/pf)
        # 2. Or send command to LuLu
        # 3. Or modify packet filter rules
        
        # For now, we just track it
        self._apply_firewall_rule(app_name, endpoint, "ALLOW")
    
    def _apply_firewall_rule(self, app_name, endpoint, action):
        """Apply actual firewall rule"""
        # This is where we'd interact with the actual firewall
        # Options:
        # 1. macOS pf (packet filter)
        # 2. LuLu via AppleScript
        # 3. Custom kernel extension
        
        # For demonstration, we'll create a pf rule
        host, port = endpoint.split(':')
        
        if action == "ALLOW":
            # Create pf rule
            pf_rule = f"pass out proto tcp from any to {host} port {port}"
            self.log(f"  📝 PF Rule: {pf_rule}", "INFO")
            
            # In production:
            # subprocess.run(['sudo', 'pfctl', '-a', 'smart_firewall', '-f', '-'], 
            #                input=pf_rule.encode())
    
    def _monitor_process_completion(self, pid, app_name, pattern):
        """Monitor when process completes and clean up early"""
        try:
            if HAS_PSUTIL:
                proc = psutil.Process(pid)
                proc.wait()  # Wait for process to complete
            else:
                # Poll using ps command
                while True:
                    result = subprocess.run(
                        ['ps', '-p', str(pid)],
                        capture_output=True
                    )
                    if result.returncode != 0:
                        break  # Process no longer exists
                    time.sleep(1)
            
            self.log(f"✅ Process {pid} completed, cleaning up early", "SUCCESS")
            
            # Remove temporary allows for this app
            for endpoint in pattern['required_endpoints']:
                key = (app_name, endpoint)
                if key in self.temp_allows:
                    del self.temp_allows[key]
                    self.log(f"  🧹 Removed: {app_name} → {endpoint}", "INFO")
                    self._apply_firewall_rule(app_name, endpoint, "BLOCK")
                    
        except Exception:
            pass
    
    def _cleanup_expired(self):
        """Cleanup expired temporary allows"""
        while self.monitoring:
            now = datetime.now()
            expired = []
            
            for key, expiry in list(self.temp_allows.items()):
                if now > expiry:
                    expired.append(key)
            
            for key in expired:
                app_name, endpoint = key
                del self.temp_allows[key]
                self.log(f"⏰ EXPIRED: {app_name} → {endpoint}", "WARNING")
                self._apply_firewall_rule(app_name, endpoint, "BLOCK")
            
            time.sleep(10)  # Check every 10 seconds
    
    def show_status(self):
        """Show current firewall status"""
        print("\n" + "="*70)
        print("🛡️  SMART ADAPTIVE FIREWALL STATUS")
        print("="*70)
        
        print(f"\n📊 Active Temporary Allows: {len(self.temp_allows)}")
        if self.temp_allows:
            print("\nCurrently Allowed:")
            for (app, endpoint), expiry in sorted(self.temp_allows.items()):
                remaining = (expiry - datetime.now()).total_seconds()
                if remaining > 0:
                    print(f"  • {app} → {endpoint} ({int(remaining)}s remaining)")
        
        print(f"\n🎯 Detected Actions: {len(self.detected_actions)}")
        if self.detected_actions:
            print("\nRecent Detections:")
            for detection in self.detected_actions[-5:]:
                print(f"  • {detection['action']}: {detection['app']} → {detection['process']} "
                      f"(PID {detection['pid']}) at {detection['timestamp']}")
        
        print("\n" + "="*70 + "\n")
    
    def test_mode(self):
        """Test mode - simulate a Python install"""
        self.log("🧪 TEST MODE: Simulating Python package install", "INFO")
        
        # Simulate detection
        self._handle_action_detected(
            'python_install',
            'Windsurf',
            'pip3',
            12345,
            self.action_patterns['python_install']
        )
        
        # Show status
        time.sleep(2)
        self.show_status()
        
        self.log("✅ Test complete! In real mode, this would allow GitHub/PyPI temporarily", "SUCCESS")

def main():
    print("\n🛡️  SMART ADAPTIVE FIREWALL")
    print("="*70)
    print("Automatically detects actions and temporarily allows required connections")
    print("="*70)
    print()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        # Test mode
        firewall = SmartAdaptiveFirewall()
        firewall.test_mode()
        return
    
    if os.geteuid() != 0:
        print("⚠️  This tool requires sudo for firewall rule modification")
        print("Please run: sudo python3 smart_adaptive_firewall.py")
        sys.exit(1)
    
    firewall = SmartAdaptiveFirewall()
    
    print("Options:")
    print("  1. Start monitoring (real-time)")
    print("  2. Test mode (simulate detection)")
    print("  3. Show status")
    print("  4. Exit")
    print()
    
    choice = input("Select option: ").strip()
    
    if choice == '1':
        print("\n🔍 Starting real-time monitoring...")
        print("⚠️  Try installing a Python package in Windsurf to test!")
        print("Press Ctrl+C to stop\n")
        
        firewall.start_monitoring()
        
        try:
            while True:
                time.sleep(5)
                firewall.show_status()
        except KeyboardInterrupt:
            print("\n\n⏹️  Stopping monitor...")
            firewall.monitoring = False
            
    elif choice == '2':
        firewall.test_mode()
        
    elif choice == '3':
        firewall.show_status()
        
    else:
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()
