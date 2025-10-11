# LuLu Format Export Update

## Summary
Updated the ActivityMonitorDefenseMonster tool to export firewall rules in **LuLu-compatible format** (compact single-line JSON) in addition to the existing Murus format.

## Changes Made

### 1. **rule_generator.py**
- Added new method: `export_to_lulu_format()`
- Converts internal ruleset to LuLu's native format
- Generates compact single-line JSON matching LuLu's structure
- Includes all required LuLu fields:
  - `key`: Process identifier
  - `uuid`: Unique identifier for each rule
  - `path`: Full path to the executable
  - `name`: Process name
  - `endpointAddr`: Destination address (default: "*")
  - `creation`: Timestamp with timezone
  - `endpointPort`: Destination port (default: "*")
  - `isEndpointAddrRegex`: Regex flag (0 = no)
  - `type`: Rule type (1 = allow, 3 = block)
  - `scope`: Rule scope (0 = global)
  - `action`: Action to take (0 = allow, 1 = block)

### 2. **enhanced_gui_v2.py**
- Added new button: **"📁 Export (LuLu)"**
- Added new method: `export_rules_lulu()`
- Both Murus and LuLu export buttons are now available side-by-side
- Export buttons are enabled after rules are generated

### 3. **cli_generator.py**
- Updated to export both formats automatically
- Generates `generated_murus_rules.json` (Murus format)
- Generates `generated_lulu_rules.json` (LuLu format)

## Format Comparison

### Murus Format (Pretty-printed JSON)
```json
{
  "version": "1.0",
  "rules": [
    {
      "id": 1001,
      "action": "allow",
      "process": {
        "name": "Safari",
        "path": "/Applications/Safari.app"
      }
    }
  ]
}
```

### LuLu Format (Compact single-line JSON)
```json
{"Safari" : [{"key" : "Safari","uuid" : "8812EBD6-EC65-4176-B5E4-2E6DFDB11A9E","path" : "/Applications/Safari.app/Contents/MacOS/Safari","name" : "Safari","endpointAddr" : "*","creation" : "2025-10-08T16:10:12-0700","endpointPort" : "*","isEndpointAddrRegex" : 0,"type" : 1,"scope" : 0,"action" : 0}]}
```

## Usage

### GUI Usage
1. Load diagnostics or capture live processes
2. Select apps to allow
3. Generate rules
4. Click **"📁 Export (LuLu)"** to export in LuLu format
5. Or click **"📁 Export (Murus)"** for Murus format

### CLI Usage
```bash
cd ActivityMonitorDefenseMonster
python3 cli_generator.py
```
This will generate both formats automatically.

### Programmatic Usage
```python
from rule_generator import MurusRuleGenerator

rule_gen = MurusRuleGenerator()
ruleset = rule_gen.generate_murus_rules(requirements)

# Export to LuLu format
rule_gen.export_to_lulu_format(ruleset, "my_lulu_rules.json")

# Export to Murus format
rule_gen.export_to_murus_format(ruleset, "my_murus_rules.json")
```

## Testing
A test script is included: `test_lulu_export.py`
```bash
python3 test_lulu_export.py
```

## Compatibility
- ✅ Matches LuLu's native rule format
- ✅ Includes all required fields (key, uuid, path, name, etc.)
- ✅ Proper timestamp format with timezone
- ✅ Compact single-line JSON (LuLu's preferred format)
- ✅ Grouped by process identifier (LuLu's structure)

## Notes
- The LuLu format skips wildcard default rules (those with `name: "*"`)
- Each rule gets a unique UUID generated at export time
- Timestamps include timezone information (e.g., `-0700` for PDT)
- Rules are grouped by process name/identifier as LuLu expects
