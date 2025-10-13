#!/usr/bin/env python3
"""
Minimal LuLu Rule Generator - Just the essentials!
Step 1: Load diagnostics
Step 2: Export rules
"""

import sys
import json
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QLabel, QFileDialog, QMessageBox, QGroupBox
)
from PyQt6.QtGui import QFont

class MinimalGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LuLu Rule Generator - Minimal")
        self.setGeometry(100, 100, 800, 400)
        
        self.sysdiag_folder = None
        self.existing_rules_path = None
        self.rules = {}
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI"""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Title
        title = QLabel("🛡️ LuLu Rule Generator")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Step 1: Load Existing Rules
        step1 = QGroupBox("Step 1: Load Your Current LuLu Rules (Optional)")
        step1_layout = QVBoxLayout(step1)
        
        self.load_rules_btn = QPushButton("📋 Load Existing Rules")
        self.load_rules_btn.setMinimumHeight(50)
        self.load_rules_btn.clicked.connect(self.load_existing_rules)
        step1_layout.addWidget(self.load_rules_btn)
        
        self.rules_label = QLabel("Using default rules (or skip to use base)")
        step1_layout.addWidget(self.rules_label)
        
        layout.addWidget(step1)
        
        # Step 2: Load Diagnostics
        step2 = QGroupBox("Step 2: Load Sysdiag (Optional - enhances rules)")
        step2_layout = QVBoxLayout(step2)
        
        self.load_btn = QPushButton("📁 Select Sysdiag Folder")
        self.load_btn.setMinimumHeight(50)
        self.load_btn.clicked.connect(self.load_folder)
        step2_layout.addWidget(self.load_btn)
        
        self.folder_label = QLabel("No folder selected")
        step2_layout.addWidget(self.folder_label)
        
        layout.addWidget(step2)
        
        # Step 3: Export Rules
        step3 = QGroupBox("Step 3: Export Rules")
        step3_layout = QVBoxLayout(step3)
        
        self.export_btn = QPushButton("💾 Export LuLu Rules")
        self.export_btn.setMinimumHeight(50)
        self.export_btn.setEnabled(True)  # Always enabled
        self.export_btn.clicked.connect(self.export_rules)
        step3_layout.addWidget(self.export_btn)
        
        self.export_label = QLabel("Ready to export (will use loaded or default rules)")
        step3_layout.addWidget(self.export_label)
        
        layout.addWidget(step3)
        
        layout.addStretch()
    
    def load_existing_rules(self):
        """Load user's existing LuLu rules"""
        print("📋 Opening file picker for existing rules...")
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Your Current LuLu Rules",
            str(Path.home() / "Desktop"),
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            self.existing_rules_path = file_path
            self.rules_label.setText(f"✅ Loaded: {Path(file_path).name}")
            print(f"✅ Will use: {file_path}")
            
            # Load the rules
            try:
                with open(file_path) as f:
                    self.rules = json.load(f)
                print(f"✅ Loaded {len(self.rules)} apps from your rules")
            except Exception as e:
                print(f"❌ Error loading: {e}")
        else:
            print("❌ No file selected")
    
    def load_folder(self):
        """Load sysdiag folder"""
        print("🔍 Opening folder picker...")
        
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Sysdiag Folder",
            str(Path.home() / "Desktop")
        )
        
        print(f"📁 Selected: {folder}")
        
        if folder:
            self.sysdiag_folder = folder
            self.folder_label.setText(f"✅ Loaded: {Path(folder).name}")
            
            # Generate rules
            self.generate_rules()
            
            # Enable export
            self.export_btn.setEnabled(True)
            self.export_label.setText("Ready to export!")
        else:
            print("❌ No folder selected")
    
    def generate_rules(self):
        """Generate rules from sysdiag"""
        print(f"🔧 Generating rules from: {self.sysdiag_folder}")
        
        try:
            # Use user's loaded rules, or default
            if not self.rules:  # If user hasn't loaded their own rules
                existing_rules_path = "/Users/meep/Documents/_ToInvestigate-Offline-Attacks·/ExistingLuluRulesforOps/rules-101225.json"
                
                if Path(existing_rules_path).exists():
                    with open(existing_rules_path) as f:
                        self.rules = json.load(f)
                    print(f"✅ Using default rules as base ({len(self.rules)} apps)")
                else:
                    self.rules = {}
                    print("⚠️  No rules found, starting fresh")
            else:
                print(f"✅ Using your loaded rules ({len(self.rules)} apps)")
            
            # Run auto-discovery from sysdiag
            print("🔄 Discovering endpoints from sysdiag...")
            import subprocess
            result = subprocess.run(
                ['python3', 'auto_discover_endpoints.py', self.sysdiag_folder],
                cwd=str(Path(__file__).parent),
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ Auto-discovery complete!")
                print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
                
                # Load the discovered rules
                discovered_path = Path(__file__).parent / "auto_discovered_rules.json"
                if discovered_path.exists():
                    with open(discovered_path) as f:
                        discovered = json.load(f)
                    
                    # Merge discovered with existing
                    for key, rules in discovered.items():
                        if key not in self.rules:
                            self.rules[key] = rules
                            print(f"  ➕ Added: {key}")
                    
                    print(f"✅ Now have {len(self.rules)} apps total")
                else:
                    print("⚠️  No auto-discovered rules found")
            else:
                print(f"⚠️  Auto-discovery failed: {result.stderr[:200]}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"✅ Ready to export {len(self.rules)} rules")
    
    def export_rules(self):
        """Export rules to JSON"""
        print("💾 Exporting rules...")
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save LuLu Rules",
            str(Path.home() / "Desktop" / "lulu_rules.json"),
            "JSON Files (*.json)"
        )
        
        if file_path:
            # Export as compact JSON (no indentation) - LuLu format
            with open(file_path, 'w') as f:
                json.dump(self.rules, f, separators=(',', ' : '))
            
            self.export_label.setText(f"✅ Exported to: {Path(file_path).name}")
            print(f"✅ Saved to: {file_path} (compact LuLu format)")
            
            QMessageBox.information(
                self,
                "Success",
                f"Rules exported to:\n{file_path}"
            )

def main():
    app = QApplication(sys.argv)
    window = MinimalGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
