#!/usr/bin/env python3
"""
Adaptive Firewall Daemon
A lightweight firewall that learns startup patterns and generates rules

Uses macOS packet filter (pf) to monitor and control connections
Works alongside LuLu for enhanced protection
"""

import os
import sys
import json
import time
import subprocess
import signal
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import threading

class AdaptiveFirewallDaemon:
    def __init__(self, config_dir=None):
        if config_dir is None:
            config_dir = Path.home() / ".adaptive_firewall"
        
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        self.rules_file = self.config_dir / "rules.json"
        self.learning_file = self.config_dir / "learning_data.json"
        self.log_file = self.config_dir / "firewall.log"
        
        self.learning_mode = False
        self.monitored_apps = set()
        self.discovered_connections = defaultdict(list)
        self.temp_allows = {}
        
        self.load_config()
    
    def load_config(self):
        """Load existing configuration"""
        if self.rules_file.exists():
            with open(self.rules_file) as f:
                self.rules = json.load(f)
        else:
            self.rules = {}
        
        if self.learning_file.exists():
            with open(self.learning_file) as f:
                self.discovered_connections = defaultdict(list, json.load(f))
    
    def save_config(self):
        """Save configuration"""
        with open(self.rules_file, 'w') as f:
            json.dump(self.rules, f, indent=2)
        
        with open(self.learning_file, 'w') as f:
            json.dump(dict(self.discovered_connections), f, indent=2)
    
    def log(self, message):
        """Log message"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {message}\n"
        
        print(log_entry.strip())
        
        with open(self.log_file, 'a') as f:
            f.write(log_entry)
    
    def start_learning_mode(self, app_name, duration_seconds=300):
        """
        Start learning mode for an app
        Monitors all connections for specified duration
        """
        self.log(f"🎓 Starting learning mode for {app_name} ({duration_seconds}s)")
        
        self.learning_mode = True
        self.monitored_apps.add(app_name)
        
        # Start monitoring in background thread
        monitor_thread = threading.Thread(
            target=self._monitor_connections,
            args=(app_name, duration_seconds),
            daemon=True
        )
        monitor_thread.start()
        
        return monitor_thread
    
    def _monitor_connections(self, app_name, duration):
        """Monitor connections using tcpdump"""
        self.log(f"🔍 Monitoring {app_name} connections...")
        
        # Use tcpdump to capture connections
        # Filter by process name if possible
        cmd = [
            'sudo', 'tcpdump',
            '-i', 'any',
            '-n',  # Don't resolve hostnames
            '-l',  # Line buffered
            '-q',  # Quiet (less verbose)
            'tcp or udp'
        ]
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            start_time = time.time()
            
            for line in process.stdout:
                if time.time() - start_time > duration:
                    break
                
                # Parse connection
                conn_info = self._parse_tcpdump_line(line)
                if conn_info:
                    self.discovered_connections[app_name].append({
                        'endpoint': conn_info['dst_ip'],
                        'port': conn_info['dst_port'],
                        'protocol': conn_info['protocol'],
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    self.log(f"  📡 {conn_info['dst_ip']}:{conn_info['dst_port']}")
            
            process.terminate()
            
        except Exception as e:
            self.log(f"❌ Error monitoring: {e}")
        
        finally:
            self.learning_mode = False
            self.monitored_apps.discard(app_name)
            self.save_config()
            self.log(f"✅ Learning complete for {app_name}")
            self._generate_rules_for_app(app_name)
    
    def _parse_tcpdump_line(self, line):
        """Parse a tcpdump output line"""
        # Example: "12:34:56.789 IP 192.168.1.100.54321 > 1.2.3.4.443: tcp"
        try:
            parts = line.split()
            if len(parts) < 5:
                return None
            
            # Find the arrow
            arrow_idx = parts.index('>')
            
            src = parts[arrow_idx - 1]
            dst = parts[arrow_idx + 1].rstrip(':')
            protocol = parts[arrow_idx + 2] if len(parts) > arrow_idx + 2 else 'tcp'
            
            # Parse dst IP and port
            dst_parts = dst.rsplit('.', 1)
            if len(dst_parts) == 2:
                return {
                    'dst_ip': dst_parts[0],
                    'dst_port': dst_parts[1],
                    'protocol': protocol
                }
        except:
            pass
        
        return None
    
    def _generate_rules_for_app(self, app_name):
        """Generate firewall rules from discovered connections"""
        connections = self.discovered_connections[app_name]
        
        if not connections:
            self.log(f"⚠️  No connections discovered for {app_name}")
            return
        
        # Deduplicate and sort
        unique_endpoints = {}
        for conn in connections:
            key = f"{conn['endpoint']}:{conn['port']}"
            if key not in unique_endpoints:
                unique_endpoints[key] = conn
        
        self.log(f"\n📊 Discovered {len(unique_endpoints)} unique endpoints for {app_name}:")
        
        rules = []
        for key, conn in sorted(unique_endpoints.items()):
            self.log(f"  • {conn['endpoint']}:{conn['port']} ({conn['protocol']})")
            rules.append({
                'endpointAddr': conn['endpoint'],
                'endpointPort': conn['port'],
                'protocol': conn['protocol'],
                'action': 'allow'
            })
        
        # Save rules
        self.rules[app_name] = rules
        self.save_config()
        
        # Export to LuLu format
        self._export_lulu_rules(app_name, rules)
    
    def _export_lulu_rules(self, app_name, rules):
        """Export rules in LuLu format"""
        output_file = self.config_dir / f"lulu_rules_{app_name.lower()}.json"
        
        lulu_rules = {
            f"com.{app_name.lower()}": []
        }
        
        for rule in rules:
            lulu_rules[f"com.{app_name.lower()}"].append({
                'endpointAddr': rule['endpointAddr'],
                'endpointPort': rule['endpointPort'],
                'action': '1',  # ALLOW
                'type': '3',
                'scope': '0'
            })
        
        with open(output_file, 'w') as f:
            json.dump(lulu_rules, f, separators=(',', ' : '))
        
        self.log(f"💾 Exported LuLu rules to: {output_file}")
    
    def interactive_mode(self):
        """Interactive CLI for managing the firewall"""
        print("\n🛡️  Adaptive Firewall Daemon")
        print("=" * 60)
        print()
        
        while True:
            print("\nOptions:")
            print("  1. Start learning mode for an app")
            print("  2. View discovered connections")
            print("  3. Generate rules")
            print("  4. Export to LuLu format")
            print("  5. Exit")
            print()
            
            choice = input("Select option: ").strip()
            
            if choice == '1':
                app_name = input("App name (e.g., Windsurf): ").strip()
                duration = input("Duration in seconds (default 300): ").strip()
                duration = int(duration) if duration else 300
                
                print(f"\n🎓 Starting learning mode for {app_name}...")
                print(f"⚠️  Please start {app_name} now and use it normally")
                print(f"⏰ Will monitor for {duration} seconds\n")
                
                thread = self.start_learning_mode(app_name, duration)
                thread.join()
                
            elif choice == '2':
                self._show_discovered_connections()
                
            elif choice == '3':
                app_name = input("App name: ").strip()
                self._generate_rules_for_app(app_name)
                
            elif choice == '4':
                app_name = input("App name: ").strip()
                if app_name in self.rules:
                    self._export_lulu_rules(app_name, self.rules[app_name])
                else:
                    print(f"❌ No rules found for {app_name}")
                
            elif choice == '5':
                print("\n👋 Goodbye!")
                break
    
    def _show_discovered_connections(self):
        """Show all discovered connections"""
        print("\n📊 Discovered Connections:")
        print("=" * 60)
        
        for app_name, connections in self.discovered_connections.items():
            print(f"\n{app_name} ({len(connections)} connections):")
            
            # Group by endpoint
            endpoints = defaultdict(int)
            for conn in connections:
                key = f"{conn['endpoint']}:{conn['port']}"
                endpoints[key] += 1
            
            for endpoint, count in sorted(endpoints.items(), key=lambda x: x[1], reverse=True):
                print(f"  • {endpoint} ({count}x)")

def main():
    if os.geteuid() != 0:
        print("⚠️  This tool requires sudo for packet capture")
        print("Please run: sudo python3 adaptive_firewall_daemon.py")
        sys.exit(1)
    
    daemon = AdaptiveFirewallDaemon()
    
    try:
        daemon.interactive_mode()
    except KeyboardInterrupt:
        print("\n\n⏹️  Interrupted")
        daemon.save_config()

if __name__ == "__main__":
    main()
