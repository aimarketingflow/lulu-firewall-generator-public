#!/usr/bin/env python3
"""
Sysdiagnose Connection Parser
Extracts network connections from sysdiagnose and creates port-specific rules
"""

import re
import socket
import json
from collections import defaultdict
from pathlib import Path

class SysdiagParser:
    def __init__(self):
        self.connections = []
        self.ip_to_domain = {}
        
    def parse_netstat_routing(self, netstat_file):
        """Parse netstat routing table to find destination IPs"""
        print(f"📄 Parsing {netstat_file}...")
        
        ips = set()
        with open(netstat_file, 'r') as f:
            for line in f:
                # Skip headers and localhost
                if line.startswith('#') or '127.0.0.1' in line or 'Destination' in line:
                    continue
                
                # Extract IP addresses (first column)
                parts = line.split()
                if len(parts) > 0:
                    ip = parts[0]
                    # Check if it's a valid IP (not a network address)
                    if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
                        # Skip private IPs
                        if not ip.startswith(('192.168.', '10.', '172.', '127.')):
                            ips.add(ip)
        
        print(f"✅ Found {len(ips)} unique destination IPs")
        return list(ips)
    
    def resolve_ip_to_domain(self, ip):
        """Resolve IP to domain name"""
        if ip in self.ip_to_domain:
            return self.ip_to_domain[ip]
        
        try:
            domain = socket.gethostbyaddr(ip)[0]
            self.ip_to_domain[ip] = domain
            return domain
        except:
            self.ip_to_domain[ip] = None
            return None
    
    def categorize_by_service(self, ip, domain):
        """Categorize IP/domain by service"""
        if not domain:
            return "Unknown"
        
        domain_lower = domain.lower()
        
        # Common services
        if 'google' in domain_lower or 'goog' in domain_lower:
            return "Google"
        elif 'github' in domain_lower:
            return "GitHub"
        elif 'apple' in domain_lower or 'icloud' in domain_lower:
            return "Apple"
        elif 'microsoft' in domain_lower or 'azure' in domain_lower:
            return "Microsoft"
        elif 'amazon' in domain_lower or 'aws' in domain_lower:
            return "Amazon/AWS"
        elif 'cloudflare' in domain_lower:
            return "Cloudflare"
        elif 'akamai' in domain_lower:
            return "Akamai CDN"
        elif 'fastly' in domain_lower:
            return "Fastly CDN"
        elif 'slack' in domain_lower:
            return "Slack"
        elif 'zoom' in domain_lower:
            return "Zoom"
        else:
            return "Other"
    
    def analyze_connections(self, ips):
        """Analyze IPs and categorize them"""
        print("\n🔍 Analyzing connections...")
        
        categorized = defaultdict(list)
        
        for ip in ips:
            print(f"   Resolving {ip}...", end='\r')
            domain = self.resolve_ip_to_domain(ip)
            category = self.categorize_by_service(ip, domain)
            
            categorized[category].append({
                'ip': ip,
                'domain': domain if domain else ip,
                'port': '443'  # Most connections are HTTPS
            })
        
        print(" " * 50, end='\r')  # Clear line
        print(f"✅ Categorized {len(ips)} connections")
        
        return categorized
    
    def generate_lulu_rules(self, categorized, output_file="sysdiag_lulu_rules.json"):
        """Generate LuLu rules from categorized connections"""
        print(f"\n🛡️ Generating LuLu rules...")
        
        lulu_rules = {}
        
        for category, connections in categorized.items():
            if not connections:
                continue
            
            # Create rules for each connection
            rules = []
            for conn in connections:
                rule = {
                    "key": category,
                    "name": category,
                    "path": f"/Applications/{category}.app",  # Generic path
                    "endpointAddr": conn['domain'],
                    "endpointPort": conn['port'],
                    "isEndpointAddrRegex": 0,
                    "type": 1,  # Allow
                    "scope": 0,
                    "action": 0  # Allow
                }
                rules.append(rule)
            
            lulu_rules[category] = rules
        
        # Write to file
        with open(output_file, 'w') as f:
            json.dump(lulu_rules, f, separators=(',', ' : '))
        
        print(f"✅ Generated {sum(len(r) for r in lulu_rules.values())} rules")
        print(f"💾 Saved to: {output_file}")
        
        return lulu_rules
    
    def print_summary(self, categorized):
        """Print human-readable summary"""
        print("\n" + "="*60)
        print("📊 CONNECTION SUMMARY")
        print("="*60)
        
        for category, connections in sorted(categorized.items()):
            if not connections:
                continue
            
            print(f"\n🔹 {category} ({len(connections)} connections):")
            for conn in connections[:10]:  # Show first 10
                print(f"   → {conn['domain']}:{conn['port']}")
            if len(connections) > 10:
                print(f"   ... and {len(connections) - 10} more")
        
        print("\n" + "="*60)
        print(f"Total: {sum(len(c) for c in categorized.values())} unique connections")
        print("="*60 + "\n")


def main():
    import sys
    
    parser = SysdiagParser()
    
    # Default path
    netstat_file = "/Users/meep/Documents/_ToInvestigate-Offline-Attacks·/missing-logs/sysdiag_extract/sysdiagnose_2025.10.08_19-31-08-0700_macOS_Mac_25A362/network-info/netstat.txt"
    
    if len(sys.argv) > 1:
        netstat_file = sys.argv[1]
    
    if not Path(netstat_file).exists():
        print(f"❌ File not found: {netstat_file}")
        print("\nUsage: python3 sysdiag_connection_parser.py [netstat_file]")
        return
    
    # Parse netstat
    ips = parser.parse_netstat_routing(netstat_file)
    
    if not ips:
        print("❌ No IPs found in netstat file")
        return
    
    # Analyze connections
    categorized = parser.analyze_connections(ips)
    
    # Print summary
    parser.print_summary(categorized)
    
    # Generate LuLu rules
    rules = parser.generate_lulu_rules(categorized)
    
    print("\n📋 NEXT STEPS:")
    print("   1. Review sysdiag_lulu_rules.json")
    print("   2. Remove any unwanted connections")
    print("   3. Import into LuLu firewall")
    print("   4. Test your apps work correctly")


if __name__ == "__main__":
    main()
