#!/usr/bin/env python3
"""
App Analyzer for App-Based Firewall Generator
Discovers installed applications and maps them to required processes
"""

import os
import plistlib
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Tuple

class AppAnalyzer:
    def __init__(self):
        self.installed_apps = {}
        self.app_requirements = {}
        self.essential_processes = {
            # Core system processes that should always be allowed
            'mDNSResponder': {'path': '/usr/sbin/mDNSResponder', 'reason': 'DNS resolution'},
            'configd': {'path': '/usr/libexec/configd', 'reason': 'Network configuration'},
            'nehelper': {'path': '/usr/libexec/nehelper', 'reason': 'Network extension helper'},
            'trustd': {'path': '/usr/libexec/trustd', 'reason': 'Certificate validation'},
            'nsurlsessiond': {'path': '/usr/libexec/nsurlsessiond', 'reason': 'System HTTP requests'}
        }
        
    def discover_installed_apps(self) -> Dict:
        """Discover all installed applications"""
        print("🔍 Discovering installed applications...")
        
        apps = {}
        applications_dir = Path("/Applications")
        
        if not applications_dir.exists():
            print("❌ /Applications directory not found")
            return apps
            
        for app_path in applications_dir.glob("*.app"):
            try:
                app_info = self._analyze_app_bundle(app_path)
                if app_info:
                    apps[app_info['name']] = app_info
            except Exception as e:
                print(f"⚠️ Error analyzing {app_path.name}: {e}")
                
        self.installed_apps = apps
        print(f"✅ Found {len(apps)} installed applications")
        return apps
    
    def _analyze_app_bundle(self, app_path: Path) -> Dict:
        """Analyze an app bundle to extract information"""
        info_plist_path = app_path / "Contents" / "Info.plist"
        
        app_info = {
            'name': app_path.stem,
            'path': str(app_path),
            'bundle_id': None,
            'executable': None,
            'helper_apps': [],
            'frameworks': [],
            'estimated_processes': []
        }
        
        # Read Info.plist if it exists
        if info_plist_path.exists():
            try:
                with open(info_plist_path, 'rb') as f:
                    plist_data = plistlib.load(f)
                    
                app_info['bundle_id'] = plist_data.get('CFBundleIdentifier')
                app_info['executable'] = plist_data.get('CFBundleExecutable')
                
            except Exception as e:
                print(f"⚠️ Could not read Info.plist for {app_path.name}: {e}")
        
        # Look for helper applications
        helpers_dir = app_path / "Contents" / "Library" / "LaunchServices"
        if helpers_dir.exists():
            for helper_path in helpers_dir.glob("*.app"):
                app_info['helper_apps'].append(str(helper_path))
        
        # Look for frameworks that might spawn processes
        frameworks_dir = app_path / "Contents" / "Frameworks"
        if frameworks_dir.exists():
            for framework_path in frameworks_dir.glob("*.framework"):
                app_info['frameworks'].append(framework_path.name)
        
        # Estimate likely process names
        app_info['estimated_processes'] = self._estimate_app_processes(app_info)
        
        return app_info
    
    def _estimate_app_processes(self, app_info: Dict) -> List[str]:
        """Estimate what processes an app might spawn"""
        processes = []
        app_name = app_info['name']
        
        # Main executable
        if app_info['executable']:
            processes.append(app_info['executable'])
        else:
            processes.append(app_name)
        
        # Common helper patterns
        helper_patterns = [
            f"{app_name} Helper",
            f"{app_name}Helper", 
            f"com.{app_name.lower()}.helper",
            f"{app_name} (GPU)",
            f"{app_name} (Renderer)"
        ]
        processes.extend(helper_patterns)
        
        # Framework-based processes
        for framework in app_info['frameworks']:
            if 'Helper' in framework or 'Service' in framework:
                processes.append(framework.replace('.framework', ''))
        
        return processes
    
    def map_apps_to_detected_processes(self, detected_processes: Dict) -> Dict:
        """Map discovered apps to actually detected processes from diagnostics"""
        print("🔗 Mapping applications to detected processes...")
        
        app_process_mapping = {}
        
        for app_name, app_info in self.installed_apps.items():
            matched_processes = []
            
            # Check each detected process against this app
            for process_key, process_info in detected_processes.items():
                process_name = process_info.get('name', '')
                process_path = process_info.get('path', '')
                
                # Direct name matches
                if self._is_process_related_to_app(process_name, process_path, app_info):
                    matched_processes.append(process_info)
            
            if matched_processes:
                app_process_mapping[app_name] = {
                    'app_info': app_info,
                    'detected_processes': matched_processes,
                    'process_count': len(matched_processes)
                }
        
        print(f"✅ Mapped {len(app_process_mapping)} apps to detected processes")
        return app_process_mapping
    
    def _is_process_related_to_app(self, process_name: str, process_path: str, app_info: Dict) -> bool:
        """Determine if a process is related to a specific app"""
        app_name = app_info['name'].lower()
        bundle_id = app_info.get('bundle_id', '').lower()
        
        # Safely handle None values
        process_name = process_name.lower() if process_name else ''
        process_path = process_path.lower() if process_path else ''
        
        # Check process name
        if app_name in process_name:
            return True
            
        # Check process path
        if app_name in process_path:
            return True
            
        # Check bundle ID
        if bundle_id and bundle_id in process_path:
            return True
            
        # Check estimated processes
        for estimated_process in app_info.get('estimated_processes', []):
            if estimated_process.lower() in process_name:
                return True
        
        return False
    
    def get_app_requirements(self, selected_apps: List[str], detected_processes: Dict) -> Dict:
        """Get all process requirements for selected apps"""
        print(f"📋 Analyzing requirements for {len(selected_apps)} selected apps...")
        
        requirements = {
            'allowed_processes': [],
            'essential_system_processes': list(self.essential_processes.keys()),
            'blocked_processes': [],
            'app_details': {}
        }
        
        # Map apps to processes
        app_mapping = self.map_apps_to_detected_processes(detected_processes)
        
        # Collect requirements for selected apps
        for app_name in selected_apps:
            if app_name in app_mapping:
                app_data = app_mapping[app_name]
                requirements['app_details'][app_name] = app_data
                
                # Add all detected processes for this app to allowed list
                for process in app_data['detected_processes']:
                    if process not in requirements['allowed_processes']:
                        requirements['allowed_processes'].append(process)
        
        # Identify processes to block (network processes not in allowed list)
        allowed_process_names = {p.get('name') for p in requirements['allowed_processes']}
        allowed_process_names.update(requirements['essential_system_processes'])
        
        for process_key, process_info in detected_processes.items():
            process_name = process_info.get('name', '')
            
            # If it's a network process and not in allowed list, block it
            if (self._is_network_process(process_info) and 
                process_name not in allowed_process_names):
                requirements['blocked_processes'].append(process_info)
        
        print(f"✅ Requirements analysis complete:")
        print(f"   • Allowed processes: {len(requirements['allowed_processes'])}")
        print(f"   • Essential system: {len(requirements['essential_system_processes'])}")
        print(f"   • Blocked processes: {len(requirements['blocked_processes'])}")
        
        return requirements
    
    def _is_network_process(self, process_info: Dict) -> bool:
        """Check if a process is network-related"""
        name = process_info.get('name', '') or ''
        path = process_info.get('path', '') or ''
        name = name.lower()
        path = path.lower()
        
        network_indicators = [
            'network', 'dns', 'http', 'tcp', 'udp', 'wifi', 'bluetooth',
            'cloud', 'sync', 'account', 'connect', 'rapport', 'sharing',
            'telemetry', 'analytics', 'reporting'
        ]
        
        return any(indicator in name or indicator in path for indicator in network_indicators)
    
    def print_app_summary(self):
        """Print summary of discovered applications"""
        print("\n" + "="*60)
        print("📱 INSTALLED APPLICATIONS SUMMARY")
        print("="*60)
        
        for app_name, app_info in self.installed_apps.items():
            print(f"\n• {app_name}")
            if app_info.get('bundle_id'):
                print(f"  Bundle ID: {app_info['bundle_id']}")
            print(f"  Estimated processes: {len(app_info['estimated_processes'])}")


# Test function
def test_app_analyzer():
    """Test the app analyzer"""
    analyzer = AppAnalyzer()
    
    print("🧪 TESTING APP ANALYZER")
    apps = analyzer.discover_installed_apps()
    analyzer.print_app_summary()
    
    return analyzer


if __name__ == "__main__":
    test_app_analyzer()
