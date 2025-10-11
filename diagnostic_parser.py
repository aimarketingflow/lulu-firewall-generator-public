#!/usr/bin/env python3
"""
Diagnostic File Parser for App-Based Firewall Generator
Parses spindump and sysdiag files to extract process information
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple

class DiagnosticParser:
    def __init__(self):
        self.processes = {}
        self.network_processes = set()
        self.app_processes = {}
        self.system_processes = set()
        
    def parse_spindump_file(self, file_path: str) -> Dict:
        """Parse spindump file and extract process information"""
        print(f"🔍 Parsing spindump file: {file_path}")
        
        processes = {}
        current_process = None
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # Match process headers: "Process: name [PID]"
                    process_match = re.match(r'Process:\s+(.+?)\s+\[(\d+)\]', line)
                    if process_match:
                        process_name = process_match.group(1)
                        process_pid = int(process_match.group(2))
                        
                        current_process = {
                            'name': process_name,
                            'pid': process_pid,
                            'path': None,
                            'codesigning_id': None,
                            'uuid': None,
                            'line_number': line_num
                        }
                        continue
                    
                    # Extract additional process information
                    if current_process:
                        # Path information
                        path_match = re.match(r'Path:\s+(.+)', line)
                        if path_match:
                            current_process['path'] = path_match.group(1)
                        
                        # Codesigning ID
                        codesign_match = re.match(r'Codesigning ID:\s+(.+)', line)
                        if codesign_match:
                            current_process['codesigning_id'] = codesign_match.group(1)
                        
                        # UUID
                        uuid_match = re.match(r'UUID:\s+(.+)', line)
                        if uuid_match:
                            current_process['uuid'] = uuid_match.group(1)
                            
                            # Process is complete, store it
                            if current_process.get('name') and current_process.get('pid'):
                                process_key = f"{current_process['name']}_{current_process['pid']}"
                                processes[process_key] = current_process.copy()
                                
                                # Categorize process
                                self._categorize_process(current_process)
                            current_process = None
                    
                    # Handle empty lines - might indicate end of process block
                    if not line and current_process and current_process.get('name'):
                        # Store incomplete process if we have at least name and PID
                        if current_process.get('pid'):
                            process_key = f"{current_process['name']}_{current_process['pid']}"
                            processes[process_key] = current_process.copy()
                            self._categorize_process(current_process)
                        current_process = None
                            
        except Exception as e:
            print(f"❌ Error parsing spindump file: {e}")
            return {}
        
        self.processes = processes
        print(f"✅ Parsed {len(processes)} processes from spindump")
        return processes
    
    def _categorize_process(self, process: Dict):
        """Categorize process as app, system, or network-related"""
        name = process.get('name', '').lower() if process.get('name') else ''
        path = process.get('path', '').lower() if process.get('path') else ''
        
        # Identify application processes
        if '/applications/' in path:
            app_name = self._extract_app_name_from_path(path)
            if app_name:
                if app_name not in self.app_processes:
                    self.app_processes[app_name] = []
                self.app_processes[app_name].append(process)
        
        # Identify network-related processes
        network_indicators = [
            'network', 'dns', 'http', 'tcp', 'udp', 'wifi', 'bluetooth',
            'cloud', 'sync', 'account', 'connect', 'rapport', 'sharing'
        ]
        
        if any(indicator in name or indicator in path for indicator in network_indicators):
            self.network_processes.add(process['name'])
        
        # Identify system processes
        system_paths = ['/usr/', '/system/', '/library/']
        if any(sys_path in path for sys_path in system_paths):
            self.system_processes.add(process['name'])
    
    def _extract_app_name_from_path(self, path: str) -> str:
        """Extract app name from application path"""
        # Match pattern: /Applications/AppName.app/...
        app_match = re.search(r'/applications/([^/]+)\.app', path, re.IGNORECASE)
        if app_match:
            return app_match.group(1)
        return None
    
    def get_processes_for_app(self, app_name: str) -> List[Dict]:
        """Get all processes associated with a specific app"""
        return self.app_processes.get(app_name, [])
    
    def get_network_processes(self) -> Set[str]:
        """Get all network-related process names"""
        return self.network_processes
    
    def get_system_processes(self) -> Set[str]:
        """Get all system process names"""
        return self.system_processes
    
    def analyze_process_dependencies(self) -> Dict:
        """Analyze which processes are essential for apps to function"""
        dependencies = {}
        
        for app_name, processes in self.app_processes.items():
            app_dependencies = {
                'main_processes': [],
                'helper_processes': [],
                'system_dependencies': []
            }
            
            for process in processes:
                process_name = process['name']
                
                # Main app process (usually matches app name)
                if app_name.lower() in process_name.lower():
                    app_dependencies['main_processes'].append(process)
                # Helper processes
                elif 'helper' in process_name.lower() or app_name.lower() in process_name.lower():
                    app_dependencies['helper_processes'].append(process)
            
            dependencies[app_name] = app_dependencies
        
        return dependencies
    
    def print_analysis_summary(self):
        """Print a summary of the analysis results"""
        print("\n" + "="*60)
        print("🔍 DIAGNOSTIC ANALYSIS SUMMARY")
        print("="*60)
        
        print(f"\n📊 TOTAL PROCESSES: {len(self.processes)}")
        print(f"🖥️  APPLICATIONS FOUND: {len(self.app_processes)}")
        print(f"🌐 NETWORK PROCESSES: {len(self.network_processes)}")
        print(f"⚙️  SYSTEM PROCESSES: {len(self.system_processes)}")
        
        print(f"\n📱 APPLICATIONS DETECTED:")
        for app_name, processes in self.app_processes.items():
            print(f"  • {app_name}: {len(processes)} processes")
        
        print(f"\n🚨 HIGH-RISK NETWORK PROCESSES:")
        risky_processes = [p for p in self.network_processes if any(
            risk in p.lower() for risk in ['cloud', 'sync', 'account', 'telemetry']
        )]
        for process in sorted(risky_processes)[:10]:  # Show top 10
            print(f"  • {process}")


# Test function to validate with our existing data
def test_parser():
    """Test the parser with our existing spindump file"""
    parser = DiagnosticParser()
    
    # Test with our spindump file
    spindump_path = "~/Documents/Documents/_ToInvestigate-Offline-Attacks·/SysDiagDataOffline/Spindump-investigate-incoming0signal-1117-1118-100125.txt"
    
    if Path(spindump_path).exists():
        print("🧪 TESTING DIAGNOSTIC PARSER")
        processes = parser.parse_spindump_file(spindump_path)
        parser.print_analysis_summary()
        
        # Test dependency analysis
        dependencies = parser.analyze_process_dependencies()
        print(f"\n🔗 DEPENDENCY ANALYSIS:")
        for app, deps in dependencies.items():
            print(f"  {app}:")
            print(f"    Main: {len(deps['main_processes'])}")
            print(f"    Helpers: {len(deps['helper_processes'])}")
        
        return parser
    else:
        print(f"❌ Test file not found: {spindump_path}")
        return None


if __name__ == "__main__":
    test_parser()
