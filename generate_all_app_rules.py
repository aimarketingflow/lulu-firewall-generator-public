#!/usr/bin/env python3
"""
Generate Port-Specific Rules for ALL Active Apps
Analyzes sysdiag ps.txt to find all running apps and their dependencies
"""

import json
import re
from pathlib import Path
from collections import defaultdict

def parse_ps_file(ps_path):
    """Parse ps.txt to find all running processes"""
    processes = []
    
    try:
        with open(ps_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                # Look for .app paths
                if '.app' in line and '/Applications/' in line:
                    # Extract app path
                    match = re.search(r'(/Applications/[^/]+\.app)', line)
                    if match:
                        app_path = match.group(1)
                        # Extract process name
                        app_name = app_path.split('/')[-1].replace('.app', '')
                        processes.append({
                            'name': app_name,
                            'path': app_path,
                            'full_line': line
                        })
    except Exception as e:
        print(f"Error parsing ps.txt: {e}")
    
    return processes

def find_app_dependencies(app_name, ps_path):
    """Find helper processes for an app"""
    helpers = []
    app_lower = app_name.lower()
    
    try:
        with open(ps_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line_lower = line.lower()
                
                # Look for helper processes
                if app_lower in line_lower and any(keyword in line_lower for keyword in 
                    ['helper', 'plugin', 'server', 'daemon', 'agent', 'renderer', 'gpu', 'utility']):
                    
                    # Extract process name from path
                    if '.app' in line:
                        match = re.search(r'/([^/]+\.app)', line)
                        if match:
                            helper_name = match.group(1).replace('.app', '')
                            if helper_name.lower() != app_name.lower():
                                helpers.append(helper_name)
    except Exception as e:
        print(f"Error finding dependencies: {e}")
    
    return list(set(helpers))

def get_common_endpoints_for_app(app_name):
    """Get common endpoints based on app type"""
    
    # Default secure endpoints (block all, allow specific)
    default_endpoints = [
        ("*", "*", False, "0"),  # Block by default (inverted)
        ("*.github.com", "443", True, "1"),  # Common for dev tools
        ("*.githubusercontent.com", "443", True, "1")
    ]
    
    app_lower = app_name.lower()
    
    # App-specific endpoints
    if 'windsurf' in app_lower or 'cursor' in app_lower or 'vscode' in app_lower:
        return [
            ("*", "*", False, "0"),
            ("*.github.com", "443", True, "1"),
            ("*.githubusercontent.com", "443", True, "1"),
            ("api.codeium.com", "443", False, "1"),
            ("*.googleusercontent.com", "443", True, "1")
        ]
    elif 'slack' in app_lower:
        return [
            ("*", "*", False, "0"),
            ("*.slack.com", "443", True, "1"),
            ("*.slack-edge.com", "443", True, "1"),
            ("*.slack-msgs.com", "443", True, "1")
        ]
    elif 'spotify' in app_lower:
        return [
            ("*", "*", False, "0"),
            ("*.spotify.com", "443", True, "1"),
            ("*.scdn.co", "443", True, "1")
        ]
    elif 'chrome' in app_lower or 'firefox' in app_lower or 'safari' in app_lower:
        return [
            ("*", "443", False, "1"),  # HTTPS
            ("*", "80", False, "1")    # HTTP
        ]
    elif 'mail' in app_lower:
        return [
            ("*", "*", False, "0"),
            ("*", "993", False, "1"),  # IMAP SSL
            ("*", "587", False, "1"),  # SMTP
            ("*", "465", False, "1")   # SMTP SSL
        ]
    elif 'zoom' in app_lower:
        return [
            ("*", "*", False, "0"),
            ("*.zoom.us", "443", True, "1"),
            ("*.zoom.us", "8801", True, "1"),
            ("*.zoom.us", "8802", True, "1")
        ]
    elif 'discord' in app_lower:
        return [
            ("*", "*", False, "0"),
            ("*.discord.com", "443", True, "1"),
            ("*.discordapp.com", "443", True, "1")
        ]
    else:
        # Generic app - block all by default
        return [
            ("*", "*", False, "0")  # Block everything
        ]

def main():
    print("🔍 Comprehensive App Rule Generator")
    print("=" * 70)
    print()
    
    # Paths (update this to your sysdiag directory)
    sysdiag_dir = "path/to/your/sysdiagnose_YYYY.MM.DD_HH-MM-SS_macOS_Mac"
    ps_path = Path(sysdiag_dir) / "ps.txt"
    
    if not ps_path.exists():
        print(f"❌ ps.txt not found at: {ps_path}")
        return
    
    print("📂 Analyzing running processes...")
    processes = parse_ps_file(ps_path)
    
    # Deduplicate by app name
    unique_apps = {}
    for proc in processes:
        if proc['name'] not in unique_apps:
            unique_apps[proc['name']] = proc
    
    print(f"✅ Found {len(unique_apps)} unique applications")
    print()
    
    # Generate app configurations
    app_configs = {}
    
    for app_name, proc in sorted(unique_apps.items()):
        print(f"📦 {app_name}")
        
        # Find dependencies
        dependencies = find_app_dependencies(app_name, ps_path)
        if dependencies:
            print(f"   Dependencies: {', '.join(dependencies[:3])}")
            if len(dependencies) > 3:
                print(f"   ... and {len(dependencies) - 3} more")
        
        # Get endpoints
        endpoints = get_common_endpoints_for_app(app_name)
        
        # Create config
        bundle_id = f"com.{app_name.lower().replace(' ', '.')}"
        
        app_configs[app_name] = {
            "bundle_id": bundle_id,
            "path": proc['path'],
            "type": "3",  # Bundle
            "endpoints": endpoints,
            "dependencies": dependencies
        }
    
    print()
    print("💾 Saving configurations...")
    
    # Save to JSON
    with open("all_apps_config.json", "w") as f:
        json.dump(app_configs, f, indent=2)
    
    print(f"✅ Saved to: all_apps_config.json")
    print()
    
    # Generate summary
    print("📊 SUMMARY:")
    print("-" * 70)
    print(f"Total apps: {len(app_configs)}")
    
    # Count by type
    browsers = sum(1 for name in app_configs if any(b in name.lower() for b in ['chrome', 'firefox', 'safari']))
    dev_tools = sum(1 for name in app_configs if any(d in name.lower() for d in ['windsurf', 'cursor', 'vscode', 'xcode']))
    comm_apps = sum(1 for name in app_configs if any(c in name.lower() for c in ['slack', 'zoom', 'discord', 'teams']))
    
    print(f"  • Browsers: {browsers}")
    print(f"  • Dev Tools: {dev_tools}")
    print(f"  • Communication: {comm_apps}")
    print(f"  • Other: {len(app_configs) - browsers - dev_tools - comm_apps}")
    print()
    
    print("🎯 NEXT STEPS:")
    print("  1. Review all_apps_config.json")
    print("  2. Run merge script to apply to existing rules")
    print("  3. Import into LuLu")
    print()
    
    return app_configs

if __name__ == "__main__":
    main()
