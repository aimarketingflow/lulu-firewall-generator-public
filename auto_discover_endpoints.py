#!/usr/bin/env python3
"""
Automated Endpoint Discovery from Sysdiag
NO PASSWORD REQUIRED - Analyzes existing sysdiag data

Extracts all URLs and network endpoints from:
1. Process command lines (ps.txt)
2. Active network connections (netstat.txt)
3. DNS queries (logs/)

Usage:
    python3 auto_discover_endpoints.py [sysdiag_dir]
    
If no directory provided, finds latest sysdiag automatically.
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime

class EndpointDiscovery:
    def __init__(self, sysdiag_dir=None):
        self.sysdiag_dir = Path(sysdiag_dir) if sysdiag_dir else self.find_latest_sysdiag()
        self.app_endpoints = defaultdict(lambda: {"urls": set(), "ips": set(), "domains": set()})
        
    def find_latest_sysdiag(self):
        """Find most recent sysdiag directory"""
        home = Path.home()
        
        # Search common locations
        search_paths = [
            home / "Desktop",
            home / "Documents",
            Path("/var/tmp")
        ]
        
        sysdiags = []
        for search_path in search_paths:
            if search_path.exists():
                sysdiags.extend(search_path.glob("sysdiagnose_*"))
        
        # Filter to directories only
        sysdiags = [s for s in sysdiags if s.is_dir()]
        
        if not sysdiags:
            return None
        
        # Return most recent
        return max(sysdiags, key=lambda p: p.stat().st_mtime)
    
    def extract_from_ps(self):
        """Extract URLs from process command lines"""
        ps_file = self.sysdiag_dir / "ps.txt"
        
        if not ps_file.exists():
            print(f"⚠️  ps.txt not found")
            return
        
        print("📋 Analyzing process command lines...")
        
        with open(ps_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Find all URLs with context
        url_pattern = r'https?://[a-zA-Z0-9./?=_%:-]+'
        
        for match in re.finditer(url_pattern, content):
            url = match.group(0)
            
            # Find app name from context (look backwards for .app path)
            start = max(0, match.start() - 1000)
            context = content[start:match.start()]
            
            # Extract app name
            app_match = re.search(r'/Applications/([^/]+)\.app', context)
            if app_match:
                app_name = app_match.group(1)
                self.app_endpoints[app_name]["urls"].add(url)
        
        print(f"   Found URLs for {len(self.app_endpoints)} apps")
    
    def extract_from_netstat(self):
        """Extract active connections from netstat"""
        netstat_file = self.sysdiag_dir / "network-info" / "netstat.txt"
        
        if not netstat_file.exists():
            print(f"⚠️  netstat.txt not found")
            return
        
        print("🌐 Analyzing network connections...")
        
        with open(netstat_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                # Skip localhost
                if '127.0.0.1' in line or '::1' in line:
                    continue
                
                # Look for app names and remote addresses
                # Format: ... remote_ip.port ... AppName
                parts = line.split()
                
                # Find app name (usually at end)
                app_name = None
                for part in reversed(parts):
                    if any(keyword in part for keyword in ['Helper', '.app', 'server', 'language']):
                        app_name = part.split(':')[0]  # Remove PID
                        break
                
                if not app_name:
                    continue
                
                # Find remote address
                for part in parts:
                    # Match IP:port or hostname:port
                    if re.match(r'[\d.]+\.\d+', part) or re.match(r'[a-z0-9.-]+\.\d+', part):
                        addr = part.split('.')[:-1]  # Remove port
                        if addr:
                            ip = '.'.join(addr)
                            # Skip private IPs
                            if not ip.startswith(('192.168.', '10.', '172.', '127.')):
                                self.app_endpoints[app_name]["ips"].add(ip)
        
        print(f"   Found connections for {sum(1 for e in self.app_endpoints.values() if e['ips'])} apps")
    
    def extract_from_logs(self):
        """Extract DNS queries from logs"""
        logs_dir = self.sysdiag_dir / "logs"
        
        if not logs_dir.exists():
            print(f"⚠️  logs/ directory not found")
            return
        
        print("🔍 Analyzing DNS queries...")
        
        # Search all log files
        for log_file in logs_dir.glob("*.log"):
            try:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Find domain names
                domain_pattern = r'\b[a-z0-9.-]+\.(com|net|org|io|dev|ai|co)\b'
                
                for match in re.finditer(domain_pattern, content, re.IGNORECASE):
                    domain = match.group(0).lower()
                    
                    # Find associated app (look for app name in context)
                    start = max(0, match.start() - 200)
                    end = min(len(content), match.end() + 200)
                    context = content[start:end]
                    
                    # Look for app names
                    for app_name in self.app_endpoints.keys():
                        if app_name.lower() in context.lower():
                            self.app_endpoints[app_name]["domains"].add(domain)
                            break
            except Exception as e:
                continue
        
        print(f"   Found domains for {sum(1 for e in self.app_endpoints.values() if e['domains'])} apps")
    
    def convert_to_rules(self):
        """Convert discovered endpoints to LuLu rules"""
        rules = {}
        
        for app_name, endpoints in self.app_endpoints.items():
            if not any([endpoints["urls"], endpoints["ips"], endpoints["domains"]]):
                continue
            
            # Extract domains from URLs
            domains = set()
            for url in endpoints["urls"]:
                match = re.match(r'https?://([^/:]+)', url)
                if match:
                    domain = match.group(1)
                    port = '443' if url.startswith('https') else '80'
                    
                    # Convert to wildcard if subdomain
                    if domain.count('.') > 1:
                        parts = domain.split('.')
                        domain = f"*.{'.'.join(parts[-2:])}"
                    
                    domains.add((domain, port, True))
            
            # Add discovered domains
            for domain in endpoints["domains"]:
                if domain.count('.') > 1:
                    parts = domain.split('.')
                    domain = f"*.{'.'.join(parts[-2:])}"
                domains.add((domain, "443", True))
            
            # Create rule list
            endpoint_list = [
                ("*", "*", False, "0")  # Default deny
            ]
            
            for domain, port, is_regex in sorted(domains):
                endpoint_list.append((domain, port, is_regex, "1"))
            
            # Create config
            bundle_id = f"com.{app_name.lower().replace(' ', '.').replace('-', '.')}"
            
            rules[bundle_id] = {
                "name": app_name,
                "path": f"/Applications/{app_name}.app",
                "type": "3",
                "endpoints": endpoint_list
            }
        
        return rules
    
    def run(self):
        """Run full discovery process"""
        if not self.sysdiag_dir:
            print("❌ No sysdiag directory found")
            print("   Run: sudo sysdiagnose -f ~/Desktop/")
            return None
        
        print(f"🔍 Analyzing sysdiag: {self.sysdiag_dir.name}")
        print("=" * 70)
        print()
        
        # Extract from all sources
        self.extract_from_ps()
        self.extract_from_netstat()
        self.extract_from_logs()
        
        print()
        print("🔄 Converting to LuLu rules...")
        
        # Convert to rules
        rules = self.convert_to_rules()
        
        print(f"✅ Generated rules for {len(rules)} apps")
        
        return rules

def main():
    import sys
    
    # Get sysdiag directory
    sysdiag_dir = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Run discovery
    discovery = EndpointDiscovery(sysdiag_dir)
    rules = discovery.run()
    
    if not rules:
        print("\n❌ No rules generated")
        return
    
    # Save results
    output_file = "auto_discovered_rules.json"
    with open(output_file, 'w') as f:
        json.dump(rules, f, indent=2)
    
    print()
    print(f"💾 Saved to: {output_file}")
    print()
    
    # Show summary
    print("📊 SUMMARY:")
    print("-" * 70)
    for bundle_id, config in sorted(rules.items()):
        app_name = config["name"]
        endpoint_count = len(config["endpoints"]) - 1  # Exclude default deny
        print(f"  📱 {app_name}: {endpoint_count} endpoints")
        
        # Show first 3 endpoints
        for endpoint in config["endpoints"][1:4]:  # Skip default deny
            addr, port, is_regex, action = endpoint
            print(f"     • {addr}:{port}")
        
        if endpoint_count > 3:
            print(f"     ... and {endpoint_count - 3} more")
    
    print()
    print("🎯 NEXT STEPS:")
    print("  1. Review auto_discovered_rules.json")
    print("  2. Run: python3 merge_and_enhance_rules.py")
    print("  3. Import enhanced rules into LuLu")

if __name__ == "__main__":
    main()
