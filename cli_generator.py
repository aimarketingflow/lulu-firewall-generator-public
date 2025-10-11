#!/usr/bin/env python3
"""
Command-Line App-Based Firewall Generator
Quick CLI version for immediate testing and use
"""

import sys
from pathlib import Path
from diagnostic_parser import DiagnosticParser
from app_analyzer import AppAnalyzer
from rule_generator import MurusRuleGenerator

def main():
    print("🛡️ APP-BASED FIREWALL GENERATOR - CLI VERSION")
    print("=" * 60)
    
    # Initialize components
    parser = DiagnosticParser()
    analyzer = AppAnalyzer()
    rule_gen = MurusRuleGenerator()
    
    # Step 1: Load diagnostics (optional - can skip if using live capture)
    print("\n📋 STEP 1: LOADING DIAGNOSTICS")
    print("⚠️  Note: This CLI demo uses offline diagnostics.")
    print("    For live capture, use the GUI (enhanced_gui_v2.py)")
    
    # Example: Load from a spindump file if available
    # spindump_path = "path/to/your/spindump.txt"
    # detected_processes = parser.parse_spindump_file(spindump_path)
    
    # For demo purposes, we'll use an empty process list
    detected_processes = {}
    print("    Using live system scan instead...")
    
    # Step 2: Discover apps
    print("\n📋 STEP 2: DISCOVERING APPLICATIONS")
    installed_apps = analyzer.discover_installed_apps()
    analyzer.print_app_summary()
    
    # Step 3: Show app selection
    print("\n📋 STEP 3: APP SELECTION")
    app_names = list(installed_apps.keys())
    
    print("Available applications:")
    for i, app_name in enumerate(app_names, 1):
        print(f"  {i:2d}. {app_name}")
    
    # For demo, let's select Windsurf and Safari
    demo_selection = ["Windsurf", "Safari"]
    available_demo_apps = [app for app in demo_selection if app in app_names]
    
    if available_demo_apps:
        print(f"\n🎯 DEMO: Selecting {available_demo_apps}")
        selected_apps = available_demo_apps
    else:
        print("\n⚠️ Demo apps not found, selecting first 2 available apps")
        selected_apps = app_names[:2] if len(app_names) >= 2 else app_names
    
    print(f"Selected apps: {selected_apps}")
    
    # Step 4: Analyze requirements
    print("\n📋 STEP 4: ANALYZING REQUIREMENTS")
    requirements = analyzer.get_app_requirements(selected_apps, detected_processes)
    
    print(f"\n📊 REQUIREMENTS SUMMARY:")
    print(f"  • Selected apps: {len(selected_apps)}")
    print(f"  • Allowed processes: {len(requirements['allowed_processes'])}")
    print(f"  • Essential system processes: {len(requirements['essential_system_processes'])}")
    print(f"  • Blocked processes: {len(requirements['blocked_processes'])}")
    
    # Step 5: Generate rules
    print("\n📋 STEP 5: GENERATING MURUS RULES")
    ruleset = rule_gen.generate_murus_rules(requirements)
    
    # Step 6: Export rules
    print("\n📋 STEP 6: EXPORTING RULES")
    murus_file = "generated_murus_rules.json"
    lulu_file = "generated_lulu_rules.json"
    
    rule_gen.export_to_murus_format(ruleset, murus_file)
    rule_gen.export_to_lulu_format(ruleset, lulu_file)
    
    # Show summary
    summary = rule_gen.generate_rule_summary(ruleset)
    print(f"\n{summary}")
    
    print(f"\n🎉 SUCCESS! Generated firewall rules saved to:")
    print(f"  • Murus format: {murus_file}")
    print(f"  • LuLu format: {lulu_file}")
    print("\n📋 NEXT STEPS:")
    print("  1. Review the generated rules in the JSON files")
    print("  2. Import the rules into Murus or LuLu")
    print("  3. Test that your selected apps still work")
    print("  4. Monitor blocked connections in firewall logs")

if __name__ == "__main__":
    main()
