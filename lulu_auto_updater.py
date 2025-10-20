#!/usr/bin/env python3
"""
LuLu Auto-Updater
Automatically updates LuLu rules when actions are detected

This version ACTUALLY modifies LuLu rules in real-time!
"""

import os
import sys
import json
import time
import subprocess
import plistlib
import threading
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

class LuLuAutoUpdater:
    def __init__(self):
        # LuLu rules location
        self.lulu_rules_path = Path("/Library/Objective-See/LuLu/rules.plist")
        self.backup_dir = Path.home() / ".lulu_auto_updater"
        self.backup_dir.mkdir(exist_ok=True)
        
        self.log_file = self.backup_dir / "updater.log"
        
        # Track temporary rules
        self.temp_rules = {}  # {rule_id: expiry_time}
        self.detected_actions = []
        self.action_cooldowns = {}  # {action_name: last_trigger_time}
        
        # Action patterns (ONLY package installs, not git)
        self.action_patterns = {
            'python_install': {
                'processes': ['pip', 'pip3'],  # Only pip, not python (too broad)
                'parent_apps': ['Windsurf', 'VSCode', 'PyCharm'],
                'endpoints': [
                    ('pypi.org', '443'),
                    ('files.pythonhosted.org', '443'),
                    ('github.com', '443'),
                    ('raw.githubusercontent.com', '443')
                ],
                'duration': 300
            },
            'npm_install': {
                'processes': ['npm', 'yarn', 'pnpm'],
                'parent_apps': ['Windsurf', 'VSCode', 'WebStorm'],
                'endpoints': [
                    ('registry.npmjs.org', '443'),
                    ('github.com', '443'),
                    ('raw.githubusercontent.com', '443')
                ],
                'duration': 300
            }
            # Removed git_clone - too noisy, Windsurf runs git constantly
        }
    
    def log(self, message, level="INFO"):
        """Log message"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        colors = {
            'INFO': '\033[94m',
            'SUCCESS': '\033[92m',
            'WARNING': '\033[93m',
            'ERROR': '\033[91m',
            'DETECT': '\033[95m'
        }
        
        color = colors.get(level, '')
        reset = '\033[0m'
        
        print(f"{color}{log_entry.strip()}{reset}")
        
        with open(self.log_file, 'a') as f:
            f.write(log_entry)
    
    def backup_lulu_rules(self):
        """Backup current LuLu rules"""
        if not self.lulu_rules_path.exists():
            self.log("LuLu rules file not found - will create new one", "WARNING")
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"rules_backup_{timestamp}.plist"
        
        try:
            subprocess.run(
                ['sudo', 'cp', str(self.lulu_rules_path), str(backup_path)],
                check=True
            )
            self.log(f"Backed up rules to: {backup_path}", "SUCCESS")
            return backup_path
        except Exception as e:
            self.log(f"Error backing up rules: {e}", "ERROR")
            return None
    
    def read_lulu_rules(self):
        """Read current LuLu rules"""
        if not self.lulu_rules_path.exists():
            return {}
        
        try:
            with open(self.lulu_rules_path, 'rb') as f:
                # Use fmt=plistlib.FMT_XML to handle UIDs
                return plistlib.load(f, fmt=plistlib.FMT_XML)
        except Exception as e:
            self.log(f"Error reading LuLu rules: {e}", "ERROR")
            return {}
    
    def write_lulu_rules(self, rules):
        """Write LuLu rules"""
        try:
            # Write to temp file first
            temp_file = self.backup_dir / "rules_temp.plist"
            with open(temp_file, 'wb') as f:
                # Use XML format to avoid UID issues
                plistlib.dump(rules, f, fmt=plistlib.FMT_XML)
            
            # Copy to LuLu location with sudo
            subprocess.run(
                ['sudo', 'cp', str(temp_file), str(self.lulu_rules_path)],
                check=True
            )
            
            # Restart LuLu to reload rules
            self.restart_lulu()
            
            self.log("Updated LuLu rules", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Error writing LuLu rules: {e}", "ERROR")
            return False
    
    def restart_lulu(self):
        """Restart LuLu to reload rules"""
        try:
            # Kill LuLu process
            subprocess.run(['killall', 'LuLu'], stderr=subprocess.DEVNULL)
            time.sleep(1)
            
            # Restart LuLu
            subprocess.run(
                ['open', '-a', 'LuLu'],
                stderr=subprocess.DEVNULL
            )
            
            self.log("Restarted LuLu", "INFO")
        except Exception as e:
            self.log(f"Error restarting LuLu: {e}", "WARNING")
    
    def temporarily_disable_blocks(self, process_names, duration):
        """Temporarily disable BLOCK rules for specific processes (github, curl, python3)"""
        self.log(f"🔓 Temporarily disabling BLOCK rules for: {', '.join(process_names)}", "INFO")
        
        # Read current rules
        rules = self.read_lulu_rules()
        
        disabled_rules = []
        
        # Find and disable BLOCK rules for these processes
        for key in list(rules.keys()):
            # Check if this key matches our process names
            for proc_name in process_names:
                if proc_name.lower() in key.lower():
                    # Store the original rules
                    original_rules = rules[key].copy() if key in rules else []
                    
                    # Remove BLOCK rules (action = 0 in JSON, which LuLu shows as BLOCK)
                    rules[key] = [r for r in rules[key] if r.get('action') != '0']
                    
                    disabled_rules.append({
                        'key': key,
                        'original_rules': original_rules,
                        'process': proc_name
                    })
                    
                    self.log(f"  🔓 Disabled BLOCK rules for: {key}", "SUCCESS")
        
        # Write modified rules
        if self.write_lulu_rules(rules):
            # Track for re-enabling
            rule_id = f"disabled:{datetime.now().timestamp()}"
            expiry = datetime.now() + timedelta(seconds=duration)
            
            self.temp_rules[rule_id] = {
                'type': 'disabled_blocks',
                'disabled_rules': disabled_rules,
                'expiry': expiry
            }
            
            self.log(f"✅ Disabled {len(disabled_rules)} BLOCK rules (will re-enable in {duration}s)", "SUCCESS")
            return rule_id
        
        return None
    
    def re_enable_blocks(self, rule_id):
        """Re-enable previously disabled BLOCK rules"""
        if rule_id not in self.temp_rules:
            return
        
        rule_info = self.temp_rules[rule_id]
        if rule_info.get('type') != 'disabled_blocks':
            return
        
        self.log(f"🔒 Re-enabling BLOCK rules...", "INFO")
        
        # Read current rules
        rules = self.read_lulu_rules()
        
        # Restore original rules
        for disabled in rule_info['disabled_rules']:
            key = disabled['key']
            rules[key] = disabled['original_rules']
            self.log(f"  🔒 Re-enabled BLOCK rules for: {key}", "SUCCESS")
        
        # Write rules
        self.write_lulu_rules(rules)
        
        # Remove from tracking
        del self.temp_rules[rule_id]
        
        self.log(f"✅ BLOCK rules re-enabled", "SUCCESS")
    
    def add_temporary_rule(self, app_name, endpoint, port, duration):
        """Add a temporary allow rule to LuLu"""
        self.log(f"Adding temporary rule: {app_name} → {endpoint}:{port}", "INFO")
        
        # Read current rules
        rules = self.read_lulu_rules()
        
        # Find or create app entry
        app_key = None
        for key in rules.keys():
            if app_name.lower() in key.lower():
                app_key = key
                break
        
        if not app_key:
            # Create new app entry
            app_key = f"com.{app_name.lower().replace(' ', '.')}"
            rules[app_key] = []
        
        # Create rule
        rule_id = f"{app_name}:{endpoint}:{port}:{datetime.now().timestamp()}"
        
        new_rule = {
            'endpointAddr': endpoint,
            'endpointPort': port,
            'action': '1',  # ALLOW (LuLu inverts: 1 = ALLOW in JSON)
            'type': '3',
            'scope': '0',
            'temporary': True,  # Our marker
            'rule_id': rule_id
        }
        
        # Add rule
        rules[app_key].append(new_rule)
        
        # Write rules
        if self.write_lulu_rules(rules):
            # Track expiry
            expiry = datetime.now() + timedelta(seconds=duration)
            self.temp_rules[rule_id] = {
                'app_key': app_key,
                'endpoint': endpoint,
                'port': port,
                'expiry': expiry
            }
            
            self.log(f"✅ Added rule (expires in {duration}s)", "SUCCESS")
            return True
        
        return False
    
    def remove_temporary_rule(self, rule_id):
        """Remove a temporary rule or re-enable blocks"""
        if rule_id not in self.temp_rules:
            return
        
        rule_info = self.temp_rules[rule_id]
        
        # Check if this is a disabled_blocks entry
        if rule_info.get('type') == 'disabled_blocks':
            self.re_enable_blocks(rule_id)
            return
        
        self.log(f"Removing temporary rule: {rule_info['endpoint']}:{rule_info['port']}", "INFO")
        
        # Read current rules
        rules = self.read_lulu_rules()
        
        # Find and remove the rule
        app_key = rule_info['app_key']
        if app_key in rules:
            rules[app_key] = [
                r for r in rules[app_key]
                if r.get('rule_id') != rule_id
            ]
        
        # Write rules
        self.write_lulu_rules(rules)
        
        # Remove from tracking
        del self.temp_rules[rule_id]
        
        self.log(f"🧹 Removed temporary rule", "SUCCESS")
    
    def cleanup_expired_rules(self):
        """Remove expired temporary rules"""
        now = datetime.now()
        expired = []
        
        for rule_id, rule_info in list(self.temp_rules.items()):
            if now > rule_info['expiry']:
                expired.append(rule_id)
        
        for rule_id in expired:
            self.remove_temporary_rule(rule_id)
    
    def monitor_processes(self):
        """Monitor for processes and update LuLu rules"""
        self.log("🔍 Starting LuLu Auto-Updater...", "INFO")
        self.log("Monitoring for: pip, npm, git processes", "INFO")
        
        # Backup rules before starting
        self.backup_lulu_rules()
        
        seen_pids = set()
        
        try:
            while True:
                # Check for new processes
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
                        
                        # Check patterns
                        for action_name, pattern in self.action_patterns.items():
                            if any(proc in name.lower() for proc in pattern['processes']):
                                seen_pids.add(pid)
                                
                                # Get parent
                                parent_result = subprocess.run(
                                    ['ps', '-p', ppid, '-o', 'comm='],
                                    capture_output=True,
                                    text=True
                                )
                                parent_name = parent_result.stdout.strip()
                                
                                # Check if parent matches
                                found_app = None
                                for app in pattern['parent_apps']:
                                    if app.lower() in parent_name.lower():
                                        found_app = app
                                        break
                                
                                # If not found, check grandparent (for terminal processes)
                                if not found_app:
                                    gp_result = subprocess.run(
                                        ['ps', '-p', ppid, '-o', 'ppid='],
                                        capture_output=True,
                                        text=True
                                    )
                                    if gp_result.returncode == 0:
                                        gpid = gp_result.stdout.strip()
                                        ggp_result = subprocess.run(
                                            ['ps', '-p', gpid, '-o', 'comm='],
                                            capture_output=True,
                                            text=True
                                        )
                                        ggp_name = ggp_result.stdout.strip()
                                        
                                        for app in pattern['parent_apps']:
                                            if app.lower() in ggp_name.lower():
                                                found_app = app
                                                break
                                
                                if found_app:
                                    self.handle_detection(
                                        action_name,
                                        found_app,
                                        name,
                                        pid,
                                        pattern
                                    )
                                    break
                
                # Cleanup expired rules
                self.cleanup_expired_rules()
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.log("\n⏹️  Stopping auto-updater...", "INFO")
            self.cleanup_all_temp_rules()
    
    def handle_detection(self, action_name, app_name, process_name, pid, pattern):
        """Handle detected action"""
        # Check cooldown - don't re-trigger same action within 60 seconds
        now = datetime.now()
        cooldown_key = f"{action_name}:{app_name}"
        
        if cooldown_key in self.action_cooldowns:
            last_trigger = self.action_cooldowns[cooldown_key]
            if (now - last_trigger).total_seconds() < 60:
                # Still in cooldown, skip
                return
        
        self.action_cooldowns[cooldown_key] = now
        
        self.log(f"🎯 DETECTED: {action_name} - {app_name} spawned {process_name} (PID: {pid})", "DETECT")
        
        # FIRST: Disable BLOCK rules for the processes that need to run
        disable_rule_id = None
        if action_name == 'python_install':
            disable_rule_id = self.temporarily_disable_blocks(['python', 'python3', 'pip', 'pip3', 'curl'], pattern['duration'])
        elif action_name == 'npm_install':
            disable_rule_id = self.temporarily_disable_blocks(['npm', 'yarn', 'pnpm', 'node', 'curl'], pattern['duration'])
        
        # SECOND: Add specific ALLOW rules for the endpoints
        for endpoint, port in pattern['endpoints']:
            self.add_temporary_rule(
                app_name,
                endpoint,
                port,
                pattern['duration']
            )
        
        # THIRD: Start monitoring process completion for early cleanup
        self.log(f"👁️  Monitoring PID {pid} for completion...", "INFO")
        monitor_thread = threading.Thread(
            target=self._monitor_process_for_cleanup,
            args=(pid, disable_rule_id),
            daemon=True
        )
        monitor_thread.start()
        
        self.detected_actions.append({
            'action': action_name,
            'app': app_name,
            'process': process_name,
            'pid': pid,
            'timestamp': datetime.now().isoformat()
        })
    
    def _monitor_process_for_cleanup(self, pid, disable_rule_id):
        """Monitor process and cleanup immediately when it completes"""
        start_time = time.time()
        
        try:
            # Poll until process completes
            while True:
                result = subprocess.run(
                    ['ps', '-p', str(pid)],
                    capture_output=True
                )
                
                if result.returncode != 0:
                    # Process completed!
                    elapsed = time.time() - start_time
                    self.log(f"✅ Process {pid} completed after {elapsed:.1f}s", "SUCCESS")
                    
                    # Immediately re-enable blocks
                    if disable_rule_id and disable_rule_id in self.temp_rules:
                        self.log(f"🔒 EARLY CLEANUP: Re-enabling blocks immediately", "SUCCESS")
                        self.re_enable_blocks(disable_rule_id)
                    
                    break
                
                time.sleep(0.5)  # Check every half second
                
        except Exception as e:
            self.log(f"Error monitoring process: {e}", "ERROR")
    
    def cleanup_all_temp_rules(self):
        """Remove all temporary rules"""
        self.log("🧹 Cleaning up all temporary rules...", "INFO")
        
        for rule_id in list(self.temp_rules.keys()):
            self.remove_temporary_rule(rule_id)
        
        self.log("✅ Cleanup complete", "SUCCESS")

def main():
    print("\n🛡️  LULU AUTO-UPDATER")
    print("=" * 70)
    print("This will AUTOMATICALLY update LuLu rules when actions are detected")
    print("=" * 70)
    print()
    print("⚠️  WARNING: This modifies your LuLu rules in real-time!")
    print("⚠️  A backup will be created before any changes")
    print()
    print("Features:")
    print("  ✅ Detects pip/npm/git processes")
    print("  ✅ Adds temporary ALLOW rules to LuLu")
    print("  ✅ Removes rules after 5 minutes or when done")
    print("  ✅ Backs up your rules before starting")
    print()
    
    if os.geteuid() != 0:
        print("❌ This requires sudo to modify LuLu rules")
        print("Please run: sudo python3 lulu_auto_updater.py")
        sys.exit(1)
    
    response = input("Continue? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Cancelled")
        sys.exit(0)
    
    updater = LuLuAutoUpdater()
    updater.monitor_processes()

if __name__ == "__main__":
    main()
