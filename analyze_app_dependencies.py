#!/usr/bin/env python3
"""
Analyze Sysdiag to Find App Dependencies
Identifies helper processes, language servers, and other supporting binaries
"""

import json
import re
from pathlib import Path
from collections import defaultdict

def parse_netstat_file(netstat_path):
    """Parse netstat output to find process connections"""
    connections = defaultdict(set)
    
    try:
        with open(netstat_path, 'r') as f:
            for line in f:
                # Look for lines with process names and connections
                # Format: tcp4  0  0  192.168.0.145.53535  35.223.238.178.443  ESTABLISHED  55526  Windsurf
                if 'ESTABLISHED' in line or 'LISTEN' in line:
                    parts = line.split()
                    if len(parts) >= 8:
                        process_name = parts[-1]
                        remote_addr = parts[4] if len(parts) > 4 else ""
                        
                        # Extract destination
                        if ':' in remote_addr or '.' in remote_addr:
                            connections[process_name].add(remote_addr)
    except Exception as e:
        print(f"Error parsing netstat: {e}")
    
    return connections

def find_app_related_processes(app_name, connections):
    """Find all processes related to an app"""
    related = {}
    app_lower = app_name.lower()
    
    for process, dests in connections.items():
        process_lower = process.lower()
        
        # Check if process is related to the app
        if (app_lower in process_lower or 
            process_lower.startswith(app_lower) or
            any(keyword in process_lower for keyword in ['helper', 'server', 'daemon', 'agent'])):
            related[process] = list(dests)
    
    return related

def analyze_sysdiag(sysdiag_dir, app_name="windsurf"):
    """Analyze sysdiag for app dependencies"""
    sysdiag_path = Path(sysdiag_dir)
    netstat_path = sysdiag_path / "network-info" / "netstat.txt"
    
    if not netstat_path.exists():
        print(f"❌ netstat.txt not found at: {netstat_path}")
        return {}
    
    print(f"📂 Analyzing: {netstat_path}")
    print()
    
    # Parse connections
    connections = parse_netstat_file(netstat_path)
    
    # Find related processes
    related = find_app_related_processes(app_name, connections)
    
    return related

def generate_rules_for_dependencies(app_name, dependencies, base_endpoints):
    """Generate LuLu rules for app dependencies"""
    rules = {}
    
    # Map process names to likely bundle IDs
    process_to_bundle = {
        "Windsurf": "com.exafunction.windsurf",
        "Electron Helper": "com.github.Electron.helper",
        "language_server_macos_arm": "language_server_macos_arm",
        "Windsurf Helper": "com.exafunction.windsurf.helper"
    }
    
    for process, destinations in dependencies.items():
        # Try to find bundle ID
        bundle_id = process_to_bundle.get(process, f"com.{process.lower().replace(' ', '.')}")
        
        print(f"📦 {process}")
        print(f"   Bundle ID: {bundle_id}")
        print(f"   Destinations: {len(destinations)}")
        
        # Create rules
        rules[process] = {
            "bundle_id": bundle_id,
            "endpoints": base_endpoints.copy()  # Use same endpoints as main app
        }
        
        print()
    
    return rules

def main():
    print("🔍 App Dependency Analyzer")
    print("=" * 70)
    print()
    
    # Analyze latest sysdiag (update this path)
    sysdiag_dir = "path/to/your/sysdiagnose_YYYY.MM.DD_HH-MM-SS_macOS_Mac"
    
    print("🎯 Analyzing Windsurf dependencies...")
    print()
    
    dependencies = analyze_sysdiag(sysdiag_dir, "windsurf")
    
    if not dependencies:
        print("❌ No dependencies found")
        return
    
    print("✅ FOUND DEPENDENCIES:")
    print("-" * 70)
    for process, dests in dependencies.items():
        print(f"  • {process}: {len(dests)} connections")
        for dest in list(dests)[:3]:
            print(f"    → {dest}")
        if len(dests) > 3:
            print(f"    ... and {len(dests) - 3} more")
    print()
    
    # Base endpoints for Windsurf
    base_endpoints = [
        ("*", "*", False, "0"),  # Block by default (inverted)
        ("*.github.com", "443", True, "1"),  # Allow (inverted)
        ("*.githubusercontent.com", "443", True, "1"),
        ("api.codeium.com", "443", False, "1"),
        ("*.googleusercontent.com", "443", True, "1")
    ]
    
    print("🛡️ RECOMMENDED RULES:")
    print("-" * 70)
    
    for process in dependencies.keys():
        print(f"\n{process}:")
        print("  1. BLOCK any address:any port (default deny)")
        print("  2. ALLOW *.github.com:443")
        print("  3. ALLOW *.githubusercontent.com:443")
        print("  4. ALLOW api.codeium.com:443")
        print("  5. ALLOW *.googleusercontent.com:443")
    
    print()
    print("💡 TIP: These helper processes should have the SAME rules as the main app")
    print("         This ensures consistent security across all components.")
    print()
    
    # Save analysis
    output = {
        "app": "Windsurf",
        "main_bundle": "com.exafunction.windsurf",
        "dependencies": {}
    }
    
    for process, dests in dependencies.items():
        output["dependencies"][process] = {
            "destinations": list(dests),
            "recommended_rules": "Same as main app"
        }
    
    with open("windsurf_dependencies.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print("💾 Saved analysis to: windsurf_dependencies.json")

if __name__ == "__main__":
    main()
