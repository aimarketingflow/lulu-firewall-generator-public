#!/usr/bin/env python3
"""
Adaptive Firewall Monitor
Watches for blocked connections during app startup and temporarily allows them
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

class AdaptiveFirewallMonitor:
    def __init__(self, lulu_rules_path="/Library/Objective-See/LuLu/rules.plist"):
        self.lulu_rules_path = lulu_rules_path
        self.temp_allows = {}  # {endpoint: expiry_time}
        self.discovered_endpoints = defaultdict(list)
        self.monitoring = False
        
    def monitor_lulu_logs(self):
        """Monitor LuLu's logs for blocked connections"""
        print("🔍 Starting adaptive firewall monitor...")
        
        # Monitor system log for LuLu events
        cmd = [
            'log', 'stream',
            '--predicate', 'process == "LuLu"',
            '--style', 'json'
        ]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        self.monitoring = True
        
        try:
            for line in process.stdout:
                if not self.monitoring:
                    break
                    
                self.process_log_line(line)
                
        except KeyboardInterrupt:
            print("\n⏹️  Stopping monitor...")
            self.monitoring = False
            process.terminate()
    
    def process_log_line(self, line):
        """Process a log line from LuLu"""
        try:
            data = json.loads(line)
            message = data.get('eventMessage', '')
            
            # Look for blocked connection patterns
            if 'BLOCK' in message or 'blocked' in message.lower():
                self.handle_blocked_connection(message, data)
                
        except json.JSONDecodeError:
            pass
    
    def handle_blocked_connection(self, message, log_data):
        """Handle a blocked connection event"""
        print(f"🚫 Blocked: {message}")
        
        # Parse the blocked connection details
        # Format: "BLOCK: process_name -> endpoint:port"
        endpoint_info = self.parse_blocked_connection(message)
        
        if endpoint_info:
            app_name = endpoint_info['app']
            endpoint = endpoint_info['endpoint']
            port = endpoint_info['port']
            
            # Check if this is a startup-related connection
            if self.is_startup_pattern(app_name, endpoint):
                print(f"✅ Startup pattern detected for {app_name}")
                self.temporarily_allow(app_name, endpoint, port)
                self.discovered_endpoints[app_name].append({
                    'endpoint': endpoint,
                    'port': port,
                    'timestamp': datetime.now().isoformat(),
                    'reason': 'startup_detection'
                })
    
    def parse_blocked_connection(self, message):
        """Parse blocked connection details from log message"""
        # This needs to match LuLu's actual log format
        # Example: "BLOCK: Windsurf.app -> api.github.com:443"
        
        # TODO: Implement actual parsing based on LuLu log format
        return None
    
    def is_startup_pattern(self, app_name, endpoint):
        """Detect if this looks like a startup connection"""
        startup_indicators = [
            'api.',
            'auth.',
            'login.',
            'oauth.',
            'token.',
            '.github.com',
            '.vscode.dev',
            'update.',
            'telemetry.'
        ]
        
        for indicator in startup_indicators:
            if indicator in endpoint.lower():
                return True
        
        return False
    
    def temporarily_allow(self, app_name, endpoint, port, duration_seconds=300):
        """Temporarily allow a connection (5 minutes default)"""
        print(f"⏰ Temporarily allowing {app_name} -> {endpoint}:{port} for {duration_seconds}s")
        
        # Add temporary rule to LuLu
        self.add_lulu_rule(app_name, endpoint, port, temporary=True)
        
        # Track expiry
        expiry = datetime.now() + timedelta(seconds=duration_seconds)
        key = f"{app_name}:{endpoint}:{port}"
        self.temp_allows[key] = expiry
        
        # Schedule cleanup
        # TODO: Implement background thread to remove expired rules
    
    def add_lulu_rule(self, app_name, endpoint, port, temporary=False):
        """Add a rule to LuLu"""
        # This would need to interact with LuLu's rule system
        # Options:
        # 1. Modify rules.plist directly (requires sudo)
        # 2. Use LuLu's CLI if available
        # 3. Use AppleScript to automate LuLu GUI
        
        print(f"  📝 Adding rule: {app_name} -> {endpoint}:{port}")
        
        # TODO: Implement actual LuLu rule addition
        pass
    
    def cleanup_expired_rules(self):
        """Remove expired temporary rules"""
        now = datetime.now()
        expired = []
        
        for key, expiry in self.temp_allows.items():
            if now > expiry:
                expired.append(key)
        
        for key in expired:
            print(f"🧹 Removing expired rule: {key}")
            # TODO: Remove from LuLu
            del self.temp_allows[key]
    
    def save_discovered_endpoints(self, output_path="discovered_startup_endpoints.json"):
        """Save discovered endpoints for future rule generation"""
        with open(output_path, 'w') as f:
            json.dump(dict(self.discovered_endpoints), f, indent=2)
        
        print(f"💾 Saved discovered endpoints to {output_path}")
    
    def generate_permanent_rules(self):
        """Generate permanent rules from discovered endpoints"""
        print("\n📊 Discovered Endpoints Summary:")
        print("=" * 60)
        
        for app_name, endpoints in self.discovered_endpoints.items():
            print(f"\n{app_name}:")
            for ep in endpoints:
                print(f"  • {ep['endpoint']}:{ep['port']} (at {ep['timestamp']})")
        
        # Generate LuLu rules
        rules = {}
        for app_name, endpoints in self.discovered_endpoints.items():
            rules[app_name] = []
            for ep in endpoints:
                rules[app_name].append({
                    'endpointAddr': ep['endpoint'],
                    'endpointPort': ep['port'],
                    'action': '1',  # ALLOW
                    'type': '3',
                    'scope': '0'
                })
        
        return rules

def main():
    print("🛡️ Adaptive Firewall Monitor")
    print("=" * 60)
    print("This tool monitors blocked connections and temporarily allows")
    print("startup-related endpoints, learning as it goes.")
    print()
    print("⚠️  NOTE: This requires LuLu to be installed and running")
    print("⚠️  NOTE: May require sudo for rule modification")
    print()
    
    monitor = AdaptiveFirewallMonitor()
    
    try:
        monitor.monitor_lulu_logs()
    except KeyboardInterrupt:
        print("\n\n📊 Generating summary...")
        monitor.save_discovered_endpoints()
        monitor.generate_permanent_rules()

if __name__ == "__main__":
    main()
