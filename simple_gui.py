#!/usr/bin/env python3
"""
Simple App-Based Firewall Generator GUI
Streamlined version focusing on core functionality
"""

import sys
import json
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QLabel, QTextEdit, QFileDialog, QMessageBox, 
    QGroupBox, QCheckBox, QScrollArea, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from diagnostic_parser import DiagnosticParser
from app_analyzer import AppAnalyzer
from rule_generator import MurusRuleGenerator

class SimpleFirewallGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🛡️ App-Based Firewall Generator")
        self.setGeometry(200, 200, 800, 600)
        
        # Data
        self.detected_processes = {}
        self.installed_apps = {}
        self.analyzer = AppAnalyzer()
        self.ruleset = None
        
        self.setup_ui()
        self.discover_apps()
    
    def setup_ui(self):
        """Setup simple UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("🛡️ App-Based Firewall Generator")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Step 1: Load Diagnostics
        diag_group = QGroupBox("📋 Step 1: Load Diagnostics")
        diag_layout = QVBoxLayout(diag_group)
        
        load_btn = QPushButton("📁 Load Spindump File")
        load_btn.clicked.connect(self.load_diagnostics)
        diag_layout.addWidget(load_btn)
        
        self.diag_status = QLabel("No diagnostics loaded")
        diag_layout.addWidget(self.diag_status)
        
        layout.addWidget(diag_group)
        
        # Step 2: Select Apps
        app_group = QGroupBox("📱 Step 2: Select Applications")
        app_layout = QVBoxLayout(app_group)
        
        # App checkboxes in scroll area
        self.app_scroll = QScrollArea()
        self.app_scroll.setMaximumHeight(200)
        app_layout.addWidget(self.app_scroll)
        
        # Quick select buttons
        btn_layout = QHBoxLayout()
        select_all_btn = QPushButton("✅ All")
        select_all_btn.clicked.connect(self.select_all)
        btn_layout.addWidget(select_all_btn)
        
        clear_btn = QPushButton("❌ Clear")
        clear_btn.clicked.connect(self.clear_all)
        btn_layout.addWidget(clear_btn)
        
        windsurf_btn = QPushButton("🌊 Windsurf Only")
        windsurf_btn.clicked.connect(self.select_windsurf)
        btn_layout.addWidget(windsurf_btn)
        
        app_layout.addLayout(btn_layout)
        layout.addWidget(app_group)
        
        # Step 3: Generate Rules
        rules_group = QGroupBox("🛡️ Step 3: Generate Rules")
        rules_layout = QVBoxLayout(rules_group)
        
        self.generate_btn = QPushButton("🛡️ Generate Murus Rules")
        self.generate_btn.clicked.connect(self.generate_rules)
        self.generate_btn.setEnabled(False)
        rules_layout.addWidget(self.generate_btn)
        
        export_layout = QHBoxLayout()
        self.export_btn = QPushButton("📁 Export Rules")
        self.export_btn.clicked.connect(self.export_rules)
        self.export_btn.setEnabled(False)
        export_layout.addWidget(self.export_btn)
        
        self.preview_btn = QPushButton("👁️ Preview")
        self.preview_btn.clicked.connect(self.preview_rules)
        self.preview_btn.setEnabled(False)
        export_layout.addWidget(self.preview_btn)
        
        rules_layout.addLayout(export_layout)
        layout.addWidget(rules_group)
        
        # Status
        self.status_label = QLabel("Ready - Load diagnostics and select apps")
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
    
    def discover_apps(self):
        """Discover installed applications"""
        try:
            self.installed_apps = self.analyzer.discover_installed_apps()
            self.update_app_checkboxes()
            self.status_label.setText(f"Found {len(self.installed_apps)} applications")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to discover apps: {e}")
    
    def update_app_checkboxes(self):
        """Update app selection checkboxes"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.app_checkboxes = []
        for app_name in sorted(self.installed_apps.keys()):
            checkbox = QCheckBox(f"📱 {app_name}")
            checkbox.setObjectName(app_name)
            checkbox.stateChanged.connect(self.on_selection_changed)
            self.app_checkboxes.append(checkbox)
            layout.addWidget(checkbox)
        
        self.app_scroll.setWidget(widget)
    
    def load_diagnostics(self):
        """Load spindump file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Spindump File", "", "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                self.progress.setVisible(True)
                self.progress.setRange(0, 0)
                
                parser = DiagnosticParser()
                self.detected_processes = parser.parse_spindump_file(file_path)
                
                self.progress.setVisible(False)
                
                count = len(self.detected_processes)
                self.diag_status.setText(f"✅ Loaded {count} processes")
                self.status_label.setText("Diagnostics loaded - Select apps and generate rules")
                
                # Enable rule generation if apps are selected
                if self.get_selected_apps():
                    self.generate_btn.setEnabled(True)
                    
            except Exception as e:
                self.progress.setVisible(False)
                QMessageBox.critical(self, "Error", f"Failed to load diagnostics: {e}")
    
    def get_selected_apps(self):
        """Get selected app names"""
        selected = []
        for checkbox in getattr(self, 'app_checkboxes', []):
            if checkbox.isChecked():
                selected.append(checkbox.objectName())
        return selected
    
    def on_selection_changed(self):
        """Handle app selection changes"""
        selected = self.get_selected_apps()
        can_generate = len(selected) > 0 and len(self.detected_processes) > 0
        self.generate_btn.setEnabled(can_generate)
        
        if selected:
            self.status_label.setText(f"Selected {len(selected)} apps")
    
    def select_all(self):
        """Select all apps"""
        for checkbox in getattr(self, 'app_checkboxes', []):
            checkbox.setChecked(True)
    
    def clear_all(self):
        """Clear all selections"""
        for checkbox in getattr(self, 'app_checkboxes', []):
            checkbox.setChecked(False)
    
    def select_windsurf(self):
        """Select only Windsurf"""
        self.clear_all()
        for checkbox in getattr(self, 'app_checkboxes', []):
            if 'windsurf' in checkbox.objectName().lower():
                checkbox.setChecked(True)
    
    def generate_rules(self):
        """Generate firewall rules"""
        selected_apps = self.get_selected_apps()
        
        if not selected_apps or not self.detected_processes:
            QMessageBox.warning(self, "Missing Data", "Need both diagnostics and app selection")
            return
        
        try:
            self.progress.setVisible(True)
            self.progress.setRange(0, 0)
            
            # Generate requirements
            requirements = self.analyzer.get_app_requirements(selected_apps, self.detected_processes)
            
            # Generate rules
            rule_gen = MurusRuleGenerator()
            self.ruleset = rule_gen.generate_murus_rules(requirements)
            self.rule_generator = rule_gen
            
            self.progress.setVisible(False)
            
            rule_count = len(self.ruleset['rules'])
            self.status_label.setText(f"✅ Generated {rule_count} rules")
            
            # Enable export buttons
            self.export_btn.setEnabled(True)
            self.preview_btn.setEnabled(True)
            
        except Exception as e:
            self.progress.setVisible(False)
            QMessageBox.critical(self, "Error", f"Failed to generate rules: {e}")
    
    def export_rules(self):
        """Export rules to file"""
        if not self.ruleset:
            QMessageBox.warning(self, "No Rules", "Generate rules first")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Murus Rules", "murus_rules.json", "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                self.rule_generator.export_to_murus_format(self.ruleset, file_path)
                
                summary = self.rule_generator.generate_rule_summary(self.ruleset)
                QMessageBox.information(self, "Export Complete", 
                                      f"Rules exported to:\n{file_path}\n\n{summary}")
                
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export: {e}")
    
    def preview_rules(self):
        """Preview generated rules"""
        if not self.ruleset:
            QMessageBox.warning(self, "No Rules", "Generate rules first")
            return
        
        summary = self.rule_generator.generate_rule_summary(self.ruleset)
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Rules Preview")
        msg.setText("Generated Murus Rules Summary:")
        msg.setDetailedText(summary)
        msg.exec()

def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    
    # Set dark theme
    app.setStyleSheet("""
        QMainWindow { background-color: #2b2b2b; color: white; }
        QGroupBox { font-weight: bold; border: 2px solid #555; border-radius: 5px; margin-top: 1ex; padding-top: 10px; }
        QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px 0 5px; }
        QPushButton { background-color: #0078d4; color: white; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold; }
        QPushButton:hover { background-color: #106ebe; }
        QPushButton:disabled { background-color: #555; color: #888; }
        QTextEdit, QScrollArea { background-color: #1e1e1e; color: white; border: 1px solid #555; }
    """)
    
    window = SimpleFirewallGUI()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
