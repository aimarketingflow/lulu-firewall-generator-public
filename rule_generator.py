#!/usr/bin/env python3
"""
Murus Rule Generator for App-Based Firewall Generator
Creates Murus firewall rules based on app requirements analysis
"""

import json
from datetime import datetime
from typing import Dict, List

class MurusRuleGenerator:
    def __init__(self):
        self.rule_counter = 1000  # Start rule IDs from 1000
        
    def generate_murus_rules(self, requirements: Dict) -> Dict:
        """Generate complete Murus ruleset from requirements analysis"""
        print("🛡️ Generating Murus firewall rules...")
        
        ruleset = {
            "metadata": {
                "generated_by": "App-Based Firewall Generator",
                "timestamp": datetime.now().isoformat(),
                "rule_count": 0,
                "description": "Surgical firewall rules allowing selected apps while blocking exfiltration"
            },
            "rules": []
        }
        
        # 1. Essential system service rules (ALLOW)
        essential_processes = requirements.get('essential_system_processes', [])
        if isinstance(essential_processes, list):
            # Handle list format
            for process_name in essential_processes:
                rule = self._create_allow_rule(
                    process_name=process_name,
                    process_path=f'/usr/sbin/{process_name}',
                    reason=f"Essential system service"
                )
                ruleset["rules"].append(rule)
        else:
            # Handle dict format
            for process_name, process_info in essential_processes.items():
                rule = self._create_allow_rule(
                    process_name=process_name,
                    process_path=process_info.get('path', f'/usr/sbin/{process_name}'),
                    reason=f"Essential: {process_info.get('reason', 'System service')}"
                )
                ruleset["rules"].append(rule)
        
        # 2. Selected app rules (ALLOW)
        for process in requirements.get('allowed_processes', []):
            rule = self._create_allow_rule(
                process_name=process.get('name', 'Unknown'),
                process_path=process.get('path', ''),
                reason="User-selected application"
            )
            ruleset["rules"].append(rule)
        
        # 3. Exfiltration blocking rules (BLOCK)
        for process in requirements.get('blocked_processes', []):
            rule = self._create_block_rule(
                process_name=process.get('name', 'Unknown'),
                process_path=process.get('path', ''),
                reason="Potential exfiltration vector"
            )
            ruleset["rules"].append(rule)
        
        # 4. Default deny rule
        default_rule = self._create_default_deny_rule()
        ruleset["rules"].append(default_rule)
        
        ruleset["metadata"]["rule_count"] = len(ruleset["rules"])
        
        print(f"✅ Generated {len(ruleset['rules'])} Murus rules")
        return ruleset
    
    def _create_allow_rule(self, process_name: str, process_path: str, reason: str) -> Dict:
        """Create a Murus ALLOW rule"""
        rule = {
            "id": self._get_next_rule_id(),
            "action": "allow",
            "direction": "out",
            "protocol": "any",
            "process": {
                "name": process_name,
                "path": process_path
            },
            "destination": {
                "address": "any",
                "port": "any"
            },
            "description": f"ALLOW: {reason}",
            "enabled": True,
            "log": False
        }
        return rule
    
    def _create_block_rule(self, process_name: str, process_path: str, reason: str) -> Dict:
        """Create a Murus BLOCK rule"""
        rule = {
            "id": self._get_next_rule_id(),
            "action": "block",
            "direction": "out", 
            "protocol": "any",
            "process": {
                "name": process_name,
                "path": process_path
            },
            "destination": {
                "address": "any",
                "port": "any"
            },
            "description": f"BLOCK: {reason}",
            "enabled": True,
            "log": True  # Log blocked attempts
        }
        return rule
    
    def _create_default_deny_rule(self) -> Dict:
        """Create default deny rule for all other outbound connections"""
        rule = {
            "id": self._get_next_rule_id(),
            "action": "block",
            "direction": "out",
            "protocol": "any", 
            "process": {
                "name": "*",
                "path": "*"
            },
            "destination": {
                "address": "any",
                "port": "any"
            },
            "description": "DEFAULT DENY: Block all other outbound connections",
            "enabled": True,
            "log": True
        }
        return rule
    
    def _get_next_rule_id(self) -> int:
        """Get next available rule ID"""
        rule_id = self.rule_counter
        self.rule_counter += 1
        return rule_id
    
    def export_to_murus_format(self, ruleset: Dict, output_file: str = None) -> str:
        """Export ruleset in Murus-compatible format"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"murus_rules_{timestamp}.json"
        
        # Convert to Murus format
        murus_config = {
            "version": "1.0",
            "rules": ruleset["rules"],
            "metadata": ruleset["metadata"]
        }
        
        with open(output_file, 'w') as f:
            json.dump(murus_config, f, indent=2)
        
        print(f"📁 Exported Murus rules to: {output_file}")
        return output_file
    
    def export_to_lulu_format(self, ruleset: Dict, output_file: str = None) -> str:
        """Export ruleset in LuLu-compatible format (compact single-line JSON)"""
        import uuid as uuid_module
        
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"lulu_rules_{timestamp}.json"
        
        # Convert to LuLu format - dictionary keyed by process identifier
        lulu_rules = {}
        
        for rule in ruleset["rules"]:
            process_name = rule.get('process', {}).get('name', 'unknown')
            process_path = rule.get('process', {}).get('path', '')
            
            # Skip wildcard default rules for LuLu format
            if process_name == '*':
                continue
            
            # Use process name as key (LuLu uses signature identifier)
            key = process_name
            
            # Create LuLu rule structure with all fields
            # Format timestamp with timezone like: 2025-10-01T20:37:01-0700
            from datetime import timezone
            now = datetime.now().astimezone()
            timestamp = now.strftime("%Y-%m-%dT%H:%M:%S%z")
            # Insert colon in timezone if needed (Python outputs -0700, LuLu expects -0700)
            
            lulu_rule = {
                "key": key,
                "uuid": str(uuid_module.uuid4()).upper(),
                "path": process_path,
                "name": process_name,
                "endpointAddr": "*",
                "creation": timestamp,
                "endpointPort": "*",
                "isEndpointAddrRegex": 0,
                "type": 1 if rule.get('action') == 'allow' else 3,  # 1=allow, 3=block
                "scope": 0,
                "action": 0 if rule.get('action') == 'allow' else 1  # 0=allow, 1=block
            }
            
            # Add to rules dictionary (LuLu groups rules by key)
            if key not in lulu_rules:
                lulu_rules[key] = []
            lulu_rules[key].append(lulu_rule)
        
        # Write as compact single-line JSON (LuLu format)
        with open(output_file, 'w') as f:
            json.dump(lulu_rules, f, separators=(',', ' : '))
        
        print(f"📁 Exported LuLu rules to: {output_file}")
        return output_file
    
    def generate_rule_summary(self, ruleset: Dict) -> str:
        """Generate human-readable summary of rules"""
        summary = []
        summary.append("🛡️ MURUS FIREWALL RULES SUMMARY")
        summary.append("=" * 50)
        summary.append(f"Generated: {ruleset['metadata']['timestamp']}")
        summary.append(f"Total Rules: {ruleset['metadata']['rule_count']}")
        summary.append("")
        
        allow_count = sum(1 for rule in ruleset['rules'] if rule['action'] == 'allow')
        block_count = sum(1 for rule in ruleset['rules'] if rule['action'] == 'block')
        
        summary.append(f"📊 RULE BREAKDOWN:")
        summary.append(f"  • ALLOW rules: {allow_count}")
        summary.append(f"  • BLOCK rules: {block_count}")
        summary.append("")
        
        summary.append("✅ ALLOWED PROCESSES:")
        for rule in ruleset['rules']:
            if rule['action'] == 'allow' and rule['process']['name'] != '*':
                summary.append(f"  • {rule['process']['name']}")
        
        summary.append("")
        summary.append("❌ BLOCKED PROCESSES:")
        for rule in ruleset['rules']:
            if rule['action'] == 'block' and rule['process']['name'] != '*':
                summary.append(f"  • {rule['process']['name']}")
        
        return "\n".join(summary)
