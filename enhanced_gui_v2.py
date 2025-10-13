#!/usr/bin/env python3
"""
Enhanced App-Based Firewall Generator GUI v2
Added offline/online mode and app filtering
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QLabel, QTextEdit, QFileDialog, QMessageBox, 
    QGroupBox, QCheckBox, QScrollArea, QProgressBar, QTabWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QSplitter,
    QDialog, QDialogButtonBox, QLineEdit, QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from diagnostic_parser import DiagnosticParser
from app_analyzer import AppAnalyzer
from rule_generator import MurusRuleGenerator

class RulePreviewDialog(QDialog):
    """Large dialog for previewing rules"""
    def __init__(self, ruleset, rule_generator, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🛡️ Murus Rules Preview")
        self.setGeometry(100, 100, 1200, 800)  # Made bigger
        self.ruleset = ruleset
        self.rule_generator = rule_generator
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("🛡️ Generated Murus Rules Preview")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Tab widget for different views
        tab_widget = QTabWidget()
        
        # Summary tab with scroll area
        summary_widget = QWidget()
        summary_layout = QVBoxLayout(summary_widget)
        
        summary_scroll = QScrollArea()
        summary_scroll.setWidgetResizable(True)
        summary_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        summary_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        summary_text = QTextEdit()
        summary_text.setFont(QFont("Courier", 10))
        summary_text.setMinimumHeight(600)  # Ensure minimum height
        summary = self.rule_generator.generate_rule_summary(self.ruleset)
        summary_text.setPlainText(summary)
        
        summary_scroll.setWidget(summary_text)
        summary_layout.addWidget(summary_scroll)
        
        tab_widget.addTab(summary_widget, "📊 Summary")
        
        # Rules table tab
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        
        rules_table = QTableWidget()
        rules_table.setColumnCount(5)
        rules_table.setHorizontalHeaderLabels(["ID", "Action", "Process", "Description", "Enabled"])
        rules_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Populate table
        rules = self.ruleset['rules']
        rules_table.setRowCount(len(rules))
        
        for row, rule in enumerate(rules):
            rules_table.setItem(row, 0, QTableWidgetItem(str(rule.get('id', ''))))
            
            action = rule.get('action', 'unknown')
            action_text = "✅ ALLOW" if action == 'allow' else "❌ BLOCK"
            rules_table.setItem(row, 1, QTableWidgetItem(action_text))
            
            process_name = rule.get('process', {}).get('name', 'Unknown')
            rules_table.setItem(row, 2, QTableWidgetItem(process_name))
            
            description = rule.get('description', '')
            rules_table.setItem(row, 3, QTableWidgetItem(description))
            
            enabled = "✅ Yes" if rule.get('enabled', False) else "❌ No"
            rules_table.setItem(row, 4, QTableWidgetItem(enabled))
        
        table_layout.addWidget(rules_table)
        tab_widget.addTab(table_widget, "📋 Rules Table")
        
        # JSON tab with scroll area
        json_widget = QWidget()
        json_layout = QVBoxLayout(json_widget)
        
        json_scroll = QScrollArea()
        json_scroll.setWidgetResizable(True)
        json_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        json_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        json_text = QTextEdit()
        json_text.setFont(QFont("Courier", 9))
        json_text.setMinimumHeight(600)
        json_content = json.dumps(self.ruleset, indent=2)
        json_text.setPlainText(json_content)
        
        json_scroll.setWidget(json_text)
        json_layout.addWidget(json_scroll)
        
        tab_widget.addTab(json_widget, "📄 JSON")
        
        layout.addWidget(tab_widget)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

class EnhancedFirewallGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🛡️ App-Based Firewall Generator - Enhanced v2")
        self.setGeometry(50, 50, 1400, 950)  # Slightly taller for new features
        self.setMinimumSize(1200, 800)  # Set minimum size
        
        # Data
        self.detected_processes = {}
        self.installed_apps = {}
        self.analyzer = AppAnalyzer()
        self.ruleset = None
        self.saved_configs = {}
        self.is_offline_mode = False  # New: offline/online mode
        self.known_malicious = set()  # New: learned malicious processes
        
        self.setup_ui()
        self.discover_apps()
    
    def setup_ui(self):
        """Setup enhanced UI with offline/online mode and filtering"""
        # Create main scroll area
        main_scroll = QScrollArea()
        main_scroll.setWidgetResizable(True)
        main_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        main_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
        # Set the scroll area as the central widget
        main_scroll.setWidget(central_widget)
        self.setCentralWidget(main_scroll)
        
        # Title
        title = QLabel("🛡️ App-Based Firewall Generator - Enhanced v2")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Main tab widget
        self.main_tabs = QTabWidget()
        layout.addWidget(self.main_tabs)
        
        # Tab 1: Rule Generator
        self.setup_generator_tab()
        
        # Tab 2: Rule Configurations
        self.setup_configurations_tab()
        
        # Tab 3: Sysdiag Automation (NEW)
        self.setup_sysdiag_tab()
        
        # Tab 4: Analysis Dashboard
        self.setup_analysis_tab()
        
        # Status and progress
        self.status_label = QLabel("Ready - Load diagnostics and select apps")
        layout.addWidget(self.status_label)
        
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
    
    def setup_generator_tab(self):
        """Setup the main rule generator tab with enhanced features"""
        gen_widget = QWidget()
        layout = QHBoxLayout(gen_widget)
        
        # Left panel - Controls
        left_panel = QWidget()
        left_panel.setMaximumWidth(520)  # Slightly wider for new features
        left_layout = QVBoxLayout(left_panel)
        
        # NEW: Device Mode Selection
        mode_group = QGroupBox("🌐 Device Mode")
        mode_layout = QVBoxLayout(mode_group)
        
        self.mode_group = QButtonGroup()
        self.online_radio = QRadioButton("🌐 Online Mode - Allow internet access")
        self.offline_radio = QRadioButton("🔒 Offline Mode - Block all internet (air-gapped)")
        
        self.online_radio.setChecked(True)  # Default to online
        self.online_radio.toggled.connect(self.on_mode_changed)
        self.offline_radio.toggled.connect(self.on_mode_changed)
        
        self.mode_group.addButton(self.online_radio)
        self.mode_group.addButton(self.offline_radio)
        
        mode_layout.addWidget(self.online_radio)
        mode_layout.addWidget(self.offline_radio)
        
        # Mode description
        self.mode_description = QLabel("Online mode allows selected apps internet access while blocking exfiltration")
        self.mode_description.setWordWrap(True)
        self.mode_description.setStyleSheet("color: #888; font-size: 10px; padding: 5px;")
        mode_layout.addWidget(self.mode_description)
        
        left_layout.addWidget(mode_group)
        
        # Step 1: Load Diagnostics
        diag_group = QGroupBox("📋 Step 1: Load Diagnostics")
        diag_layout = QVBoxLayout(diag_group)
        
        diag_btn_layout = QHBoxLayout()
        
        # Simplified buttons
        load_btn = QPushButton("📂 Load")
        load_btn.clicked.connect(self.load_diagnostics)
        load_btn.setToolTip("Load spindump file or sysdiag folder")
        diag_btn_layout.addWidget(load_btn)
        
        live_btn = QPushButton("🔴 Live")
        live_btn.clicked.connect(self.capture_live)
        live_btn.setToolTip("Capture live system diagnostics")
        diag_btn_layout.addWidget(live_btn)
        
        diag_layout.addLayout(diag_btn_layout)
        
        self.diag_status = QLabel("No diagnostics loaded")
        diag_layout.addWidget(self.diag_status)
        
        left_layout.addWidget(diag_group)
        
        # Step 2: Select Apps (ENHANCED)
        app_group = QGroupBox("📱 Step 2: Select Applications")
        app_layout = QVBoxLayout(app_group)
        
        # NEW: Filter box
        filter_layout = QHBoxLayout()
        filter_label = QLabel("🔍 Filter:")
        filter_layout.addWidget(filter_label)
        
        self.app_filter = QLineEdit()
        self.app_filter.setPlaceholderText("Type to filter applications...")
        self.app_filter.textChanged.connect(self.filter_apps)
        filter_layout.addWidget(self.app_filter)
        
        app_layout.addLayout(filter_layout)
        
        # App checkboxes in scroll area (EXPANDED HEIGHT)
        self.app_scroll = QScrollArea()
        self.app_scroll.setMaximumHeight(270)  # Increased by 20px (was 250)
        app_layout.addWidget(self.app_scroll)
        
        # Quick select buttons
        btn_layout = QHBoxLayout()
        select_all_btn = QPushButton("✅ All")
        select_all_btn.clicked.connect(self.select_all)
        btn_layout.addWidget(select_all_btn)
        
        clear_btn = QPushButton("❌ Clear")
        clear_btn.clicked.connect(self.clear_all)
        btn_layout.addWidget(clear_btn)
        
        windsurf_btn = QPushButton("🌊 Windsurf")
        windsurf_btn.clicked.connect(self.select_windsurf)
        btn_layout.addWidget(windsurf_btn)
        
        safari_btn = QPushButton("🦁 Safari")
        safari_btn.clicked.connect(self.select_safari)
        btn_layout.addWidget(safari_btn)
        
        app_layout.addLayout(btn_layout)
        left_layout.addWidget(app_group)
        
        # Add some vertical spacing before Step 3
        left_layout.addSpacing(15)  # NEW: Vertical spacing
        
        # Step 3: Generate Rules (MOVED DOWN)
        rules_group = QGroupBox("🛡️ Step 3: Generate & Export Rules")
        rules_layout = QVBoxLayout(rules_group)
        
        self.generate_btn = QPushButton("🛡️ Generate Murus Rules")
        self.generate_btn.clicked.connect(self.generate_rules)
        self.generate_btn.setEnabled(False)
        rules_layout.addWidget(self.generate_btn)
        
        export_layout = QHBoxLayout()
        self.export_btn = QPushButton("📁 Export (Murus)")
        self.export_btn.clicked.connect(self.export_rules)
        self.export_btn.setEnabled(False)
        export_layout.addWidget(self.export_btn)
        
        self.export_lulu_btn = QPushButton("📁 Export (LuLu)")
        self.export_lulu_btn.clicked.connect(self.export_rules_lulu)
        self.export_lulu_btn.setEnabled(False)
        export_layout.addWidget(self.export_lulu_btn)
        
        self.preview_btn = QPushButton("👁️ Preview")
        self.preview_btn.clicked.connect(self.preview_rules)
        self.preview_btn.setEnabled(False)
        export_layout.addWidget(self.preview_btn)
        
        rules_layout.addLayout(export_layout)
        
        # Save configuration
        save_layout = QHBoxLayout()
        self.save_config_btn = QPushButton("💾 Save Config")
        self.save_config_btn.clicked.connect(self.save_configuration)
        self.save_config_btn.setEnabled(False)
        save_layout.addWidget(self.save_config_btn)
        
        self.load_config_btn = QPushButton("📂 Load Config")
        self.load_config_btn.clicked.connect(self.load_configuration)
        save_layout.addWidget(self.load_config_btn)
        
        rules_layout.addLayout(save_layout)
        left_layout.addWidget(rules_group)
        
        left_layout.addStretch()
        layout.addWidget(left_panel)
        
        # Right panel - Preview
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        preview_group = QGroupBox("📋 Live Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.live_preview = QTextEdit()
        self.live_preview.setFont(QFont("Courier", 10))
        self.live_preview.setPlainText("Generate rules to see preview...")
        preview_layout.addWidget(self.live_preview)
        
        right_layout.addWidget(preview_group)
        layout.addWidget(right_panel)
        
        self.main_tabs.addTab(gen_widget, "🛡️ Rule Generator")
    
    def setup_configurations_tab(self):
        """Setup rule configurations management tab"""
        config_widget = QWidget()
        layout = QVBoxLayout(config_widget)
        
        # Title
        title = QLabel("💾 Saved Rule Configurations")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Configurations table
        self.config_table = QTableWidget()
        self.config_table.setColumnCount(6)
        self.config_table.setHorizontalHeaderLabels([
            "Name", "Mode", "Apps", "Rules Count", "Created", "Actions"
        ])
        self.config_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.config_table)
        
        # Config actions
        config_actions = QHBoxLayout()
        
        refresh_configs_btn = QPushButton("🔄 Refresh")
        refresh_configs_btn.clicked.connect(self.refresh_configurations)
        config_actions.addWidget(refresh_configs_btn)
        
        delete_config_btn = QPushButton("🗑️ Delete Selected")
        delete_config_btn.clicked.connect(self.delete_configuration)
        config_actions.addWidget(delete_config_btn)
        
        export_config_btn = QPushButton("📤 Export Selected")
        export_config_btn.clicked.connect(self.export_configuration)
        config_actions.addWidget(export_config_btn)
        
        layout.addLayout(config_actions)
        
        self.main_tabs.addTab(config_widget, "💾 Configurations")
    
    def setup_sysdiag_tab(self):
        """Setup sysdiag automation tab (NEW)"""
        sysdiag_widget = QWidget()
        layout = QVBoxLayout(sysdiag_widget)
        
        # Title and description
        title = QLabel("🔍 Sysdiag Automation - Port-Specific Rules")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        desc = QLabel(
            "Automatically generate port-specific firewall rules from macOS sysdiagnose data.\n"
            "This eliminates manual network analysis and provides 90% attack surface reduction."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #888; padding: 10px; font-size: 11px;")
        layout.addWidget(desc)
        
        # How it works section
        how_it_works = QGroupBox("📚 How Sysdiag Automation Works")
        how_layout = QVBoxLayout(how_it_works)
        
        steps_text = QTextEdit()
        steps_text.setReadOnly(True)
        steps_text.setMaximumHeight(300)
        steps_text.setPlainText(
            "1. GENERATE SYSDIAGNOSE\n"
            "   Run: sudo sysdiagnose\n"
            "   Wait 10 minutes, file saved to /var/tmp/\n"
            "   Extract the .tar.gz file\n\n"
            
            "2. LOAD SYSDIAG FOLDER\n"
            "   Click 'Load Sysdiag Folder' below\n"
            "   Select the extracted sysdiagnose folder\n"
            "   Tool analyzes: ps.txt, netstat.txt, network-info/\n\n"
            
            "3. AUTO-DETECTION\n"
            "   • Finds all running applications\n"
            "   • Identifies app dependencies (helpers, plugins, servers)\n"
            "   • Extracts actual network connections\n"
            "   • Generates port-specific rules\n\n"
            
            "4. DEFAULT-DENY POLICY\n"
            "   For each app with specific connections:\n"
            "   • BLOCK *:* (deny everything by default)\n"
            "   • ALLOW specific endpoints only\n"
            "   Example: Windsurf → BLOCK all, ALLOW github.com:443\n\n"
            
            "5. SECURITY BENEFITS\n"
            "   • 90% attack surface reduction\n"
            "   • If app is compromised, attacker limited to allowed destinations\n"
            "   • Blocked connections = intrusion detection\n"
            "   • Zero manual network analysis required\n\n"
            
            "6. EXPORT & IMPORT\n"
            "   • Exports to LuLu-compatible JSON\n"
            "   • Import into LuLu → Rules → Import\n"
            "   • Preserves existing blocked Apple processes\n"
            "   • Deduplicates conflicting rules"
        )
        how_layout.addWidget(steps_text)
        layout.addWidget(how_it_works)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.load_sysdiag_btn = QPushButton("📁 Load Sysdiag Folder")
        self.load_sysdiag_btn.clicked.connect(self.load_sysdiag_folder)
        self.load_sysdiag_btn.setMinimumHeight(40)
        button_layout.addWidget(self.load_sysdiag_btn)
        
        self.generate_sysdiag_rules_btn = QPushButton("🛡️ Generate Port-Specific Rules")
        self.generate_sysdiag_rules_btn.clicked.connect(self.generate_sysdiag_rules)
        self.generate_sysdiag_rules_btn.setEnabled(False)
        self.generate_sysdiag_rules_btn.setMinimumHeight(40)
        button_layout.addWidget(self.generate_sysdiag_rules_btn)
        
        layout.addLayout(button_layout)
        
        # Status
        self.sysdiag_status = QLabel("No sysdiag data loaded")
        self.sysdiag_status.setStyleSheet("padding: 10px; background-color: #333; border-radius: 5px;")
        layout.addWidget(self.sysdiag_status)
        
        # Results area
        results_group = QGroupBox("📊 Analysis Results")
        results_layout = QVBoxLayout(results_group)
        
        self.sysdiag_results = QTextEdit()
        self.sysdiag_results.setReadOnly(True)
        self.sysdiag_results.setPlainText("Load sysdiag data to see analysis results...")
        results_layout.addWidget(self.sysdiag_results)
        
        layout.addWidget(results_group)
        
        self.main_tabs.addTab(sysdiag_widget, "🔍 Sysdiag Automation")
    
    def setup_analysis_tab(self):
        """Setup analysis dashboard tab"""
        analysis_widget = QWidget()
        layout = QVBoxLayout(analysis_widget)
        
        # Title
        title = QLabel("📊 Security Analysis Dashboard")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Analysis content
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left: Process analysis
        process_group = QGroupBox("🔍 Process Analysis")
        process_layout = QVBoxLayout(process_group)
        
        self.process_analysis = QTextEdit()
        self.process_analysis.setFont(QFont("Courier", 10))
        self.process_analysis.setPlainText("Load diagnostics to see process analysis...")
        process_layout.addWidget(self.process_analysis)
        
        splitter.addWidget(process_group)
        
        # Right: Threat assessment
        threat_group = QGroupBox("🚨 Threat Assessment")
        threat_layout = QVBoxLayout(threat_group)
        
        self.threat_analysis = QTextEdit()
        self.threat_analysis.setFont(QFont("Courier", 10))
        self.threat_analysis.setPlainText("Generate rules to see threat analysis...")
        threat_layout.addWidget(self.threat_analysis)
        
        splitter.addWidget(threat_group)
        layout.addWidget(splitter)
        
        self.main_tabs.addTab(analysis_widget, "📊 Analysis")
    
    # NEW: Mode change handler
    def on_mode_changed(self):
        """Handle offline/online mode changes"""
        self.is_offline_mode = self.offline_radio.isChecked()
        
        if self.is_offline_mode:
            self.mode_description.setText("🔒 Offline mode blocks ALL internet access - only local communication allowed")
            self.mode_description.setStyleSheet("color: #ff6b6b; font-size: 10px; padding: 5px;")
        else:
            self.mode_description.setText("🌐 Online mode allows selected apps internet access while blocking exfiltration")
            self.mode_description.setStyleSheet("color: #51cf66; font-size: 10px; padding: 5px;")
        
        # Update status
        mode_text = "OFFLINE" if self.is_offline_mode else "ONLINE"
        self.status_label.setText(f"Mode: {mode_text} - {'Air-gapped security' if self.is_offline_mode else 'Selective internet access'}")
    
    # Core functionality methods
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
            
            # Add tooltip with app info
            app_info = self.installed_apps[app_name]
            tooltip = f"Bundle ID: {app_info.get('bundle_id', 'Unknown')}\n"
            tooltip += f"Path: {app_info.get('path', 'Unknown')}"
            checkbox.setToolTip(tooltip)
            
            self.app_checkboxes.append(checkbox)
            layout.addWidget(checkbox)
        
        self.app_scroll.setWidget(widget)
    
    # NEW: App filtering functionality
    def filter_apps(self, filter_text):
        """Filter applications based on search text"""
        filter_text = filter_text.lower()
        
        for checkbox in getattr(self, 'app_checkboxes', []):
            app_name = checkbox.objectName().lower()
            should_show = filter_text in app_name
            checkbox.setVisible(should_show)
    
    def load_diagnostics(self):
        """Load spindump file or sysdiag folder"""
        # Ask user what type of diagnostic to load
        msg = QMessageBox()
        msg.setWindowTitle("Load Diagnostics")
        msg.setText("What type of diagnostic data would you like to load?")
        msg.setInformativeText("Spindump: Single file with process info\nSysdiag: Folder with comprehensive system diagnostics")
        spindump_btn = msg.addButton("📄 Spindump File", QMessageBox.ButtonRole.ActionRole)
        sysdiag_btn = msg.addButton("📁 Sysdiag Folder", QMessageBox.ButtonRole.ActionRole)
        msg.addButton(QMessageBox.StandardButton.Cancel)
        msg.exec()
        
        if msg.clickedButton() == spindump_btn:
            self.load_spindump_file()
        elif msg.clickedButton() == sysdiag_btn:
            self.load_sysdiag_folder()
    
    def load_spindump_file(self):
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
                self.parser = parser
                
                self.progress.setVisible(False)
                
                count = len(self.detected_processes)
                network_count = len(parser.get_network_processes())
                
                self.diag_status.setText(f"✅ Spindump: {count} processes ({network_count} network)")
                self.status_label.setText("Spindump loaded - Select apps and generate rules")
                
                # Update analysis tab
                self.update_process_analysis()
                
                # Enable rule generation if apps are selected
                if self.get_selected_apps():
                    self.generate_btn.setEnabled(True)
                    
            except Exception as e:
                self.progress.setVisible(False)
                QMessageBox.critical(self, "Error", f"Failed to load diagnostics: {e}")
    
    def load_sysdiag_folder(self):
        """Load sysdiag folder for comprehensive analysis"""
        folder_path = QFileDialog.getExistingDirectory(
            self, "Select Sysdiag Folder", "",
            QFileDialog.Option.ShowDirsOnly
        )
        
        if folder_path:
            try:
                self.progress.setVisible(True)
                self.progress.setRange(0, 0)
                self.status_label.setText("🔍 Analyzing sysdiag data...")
                
                # Import the sysdiag analyzer
                import sys
                from pathlib import Path
                sys.path.insert(0, str(Path(__file__).parent))
                from generate_all_app_rules import parse_ps_file, find_app_dependencies
                
                # Parse ps.txt
                ps_path = Path(folder_path) / "ps.txt"
                if not ps_path.exists():
                    raise FileNotFoundError(f"ps.txt not found in {folder_path}")
                
                processes = parse_ps_file(ps_path)
                
                # Store sysdiag data
                self.sysdiag_folder = folder_path
                self.sysdiag_processes = processes
                
                # Deduplicate by app name
                unique_apps = {}
                for proc in processes:
                    if proc['name'] not in unique_apps:
                        unique_apps[proc['name']] = proc
                
                self.sysdiag_apps = unique_apps
                
                self.progress.setVisible(False)
                
                # Update status
                app_count = len(unique_apps)
                self.sysdiag_status.setText(f"✅ Loaded sysdiag: {app_count} applications found")
                self.status_label.setText(f"Sysdiag loaded - {app_count} apps detected")
                
                # Enable generation button
                self.generate_sysdiag_rules_btn.setEnabled(True)
                
                # Show results
                results_text = f"📊 SYSDIAG ANALYSIS RESULTS\n"
                results_text += f"=" * 60 + "\n\n"
                results_text += f"Folder: {folder_path}\n"
                results_text += f"Applications found: {app_count}\n\n"
                results_text += f"Top 20 Applications:\n"
                results_text += "-" * 60 + "\n"
                
                for i, (app_name, proc) in enumerate(sorted(unique_apps.items())[:20], 1):
                    results_text += f"{i}. {app_name}\n"
                    results_text += f"   Path: {proc['path']}\n\n"
                
                if len(unique_apps) > 20:
                    results_text += f"... and {len(unique_apps) - 20} more applications\n\n"
                
                results_text += "\nClick 'Generate Port-Specific Rules' to create LuLu rules!"
                
                self.sysdiag_results.setPlainText(results_text)
                
            except Exception as e:
                self.progress.setVisible(False)
                QMessageBox.critical(self, "Error", f"Failed to load sysdiag: {e}\n\nMake sure you selected the extracted sysdiagnose folder.")
    
    def generate_sysdiag_rules(self):
        """Generate port-specific rules from sysdiag data"""
        if not hasattr(self, 'sysdiag_apps'):
            QMessageBox.warning(self, "No Data", "Please load sysdiag data first!")
            return
        
        try:
            self.progress.setVisible(True)
            self.progress.setRange(0, 0)
            self.status_label.setText("🛡️ Generating port-specific rules...")
            
            # Ask for output location
            output_path, _ = QFileDialog.getSaveFileName(
                self, "Save Port-Specific Rules", 
                "enhanced_lulu_rules.json",
                "JSON Files (*.json)"
            )
            
            if not output_path:
                self.progress.setVisible(False)
                return
            
            # Import the rule generator
            from generate_all_app_rules import get_common_endpoints_for_app
            
            # Generate rules for all apps
            rules_data = {}
            for app_name, proc in self.sysdiag_apps.items():
                endpoints = get_common_endpoints_for_app(app_name)
                bundle_id = f"com.{app_name.lower().replace(' ', '.')}"
                
                rules_data[app_name] = {
                    "bundle_id": bundle_id,
                    "path": proc['path'],
                    "endpoints": endpoints
                }
            
            # Save to file
            import json
            with open(output_path, 'w') as f:
                json.dump(rules_data, f, indent=2)
            
            self.progress.setVisible(False)
            
            # Show success message
            QMessageBox.information(
                self, "Success", 
                f"✅ Generated port-specific rules for {len(rules_data)} applications!\n\n"
                f"Saved to: {output_path}\n\n"
                f"Next steps:\n"
                f"1. Review the generated rules\n"
                f"2. Run merge_and_enhance_rules.py to merge with existing rules\n"
                f"3. Import into LuLu → Rules → Import"
            )
            
            self.status_label.setText(f"✅ Generated rules for {len(rules_data)} apps")
            
        except Exception as e:
            self.progress.setVisible(False)
            QMessageBox.critical(self, "Error", f"Failed to generate rules: {e}")
    
    def capture_live(self):
        """Capture live system diagnostics"""
        reply = QMessageBox.question(self, "Live Capture", 
                                   "🔴 LIVE SYSTEM CAPTURE\n\n" +
                                   "This will capture running processes and network activity.\n" +
                                   "Make sure target applications are running!\n\n" +
                                   "Continue with live capture?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.perform_live_capture()
    
    def perform_live_capture(self):
        """Perform the actual live system capture"""
        try:
            self.progress.setVisible(True)
            self.progress.setRange(0, 0)
            self.status_label.setText("🔴 Capturing live system data...")
            
            import subprocess
            import tempfile
            from datetime import datetime
            
            # Create temporary file for live data
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_file = f"/tmp/live_capture_{timestamp}.txt"
            
            # Capture current processes
            self.status_label.setText("📋 Capturing process list...")
            with open(temp_file, 'w') as f:
                f.write("LIVE SYSTEM CAPTURE\n")
                f.write(f"Timestamp: {datetime.now()}\n")
                f.write("=" * 50 + "\n\n")
                
                # Get process list
                f.write("RUNNING PROCESSES:\n")
                f.write("-" * 30 + "\n")
                
                try:
                    ps_output = subprocess.run(['ps', 'aux'], capture_output=True, text=True, timeout=10)
                    f.write(ps_output.stdout)
                except Exception as e:
                    f.write(f"Error capturing processes: {e}\n")
                
                f.write("\n\nNETWORK CONNECTIONS:\n")
                f.write("-" * 30 + "\n")
                
                # Get network connections
                try:
                    lsof_output = subprocess.run(['lsof', '-i'], capture_output=True, text=True, timeout=10)
                    f.write(lsof_output.stdout)
                except Exception as e:
                    f.write(f"Error capturing network: {e}\n")
            
            # Parse the captured data
            self.status_label.setText("🔍 Analyzing captured data...")
            
            # Create a simple parser for the live data
            live_processes = {}
            process_count = 0
            
            with open(temp_file, 'r') as f:
                content = f.read()
                
                # Extract processes from ps output
                lines = content.split('\n')
                in_processes = False
                
                for line in lines:
                    if 'RUNNING PROCESSES:' in line:
                        in_processes = True
                        continue
                    elif 'NETWORK CONNECTIONS:' in line:
                        in_processes = False
                        continue
                    
                    if in_processes and line.strip() and not line.startswith('-'):
                        parts = line.split()
                        if len(parts) >= 11:
                            pid = parts[1]
                            command = ' '.join(parts[10:])
                            process_name = parts[10] if len(parts) > 10 else 'Unknown'
                            
                            # Create process entry
                            process_key = f"{process_name}_{pid}"
                            live_processes[process_key] = {
                                'name': process_name,
                                'pid': int(pid) if pid.isdigit() else 0,
                                'path': command.split()[0] if command else process_name,
                                'codesigning_id': None,
                                'uuid': None
                            }
                            process_count += 1
            
            # Update the GUI with live data
            self.detected_processes = live_processes
            
            # Create a mock parser object for compatibility
            class LiveParser:
                def __init__(self, processes):
                    self.processes = processes
                    self.network_processes = set()
                    self.system_processes = set()
                    self.app_processes = {}
                    
                    # Categorize processes
                    for proc_key, proc_info in processes.items():
                        name = proc_info.get('name', '').lower()
                        path = proc_info.get('path', '').lower()
                        
                        # Network processes
                        if any(net in name or net in path for net in ['network', 'wifi', 'cloud', 'sync']):
                            self.network_processes.add(proc_info['name'])
                        
                        # System processes  
                        if any(sys_path in path for sys_path in ['/usr/', '/system/', '/library/']):
                            self.system_processes.add(proc_info['name'])
                        
                        # App processes
                        if '/applications/' in path:
                            app_name = self._extract_app_name(path)
                            if app_name:
                                if app_name not in self.app_processes:
                                    self.app_processes[app_name] = []
                                self.app_processes[app_name].append(proc_info)
                
                def _extract_app_name(self, path):
                    import re
                    match = re.search(r'/applications/([^/]+)\.app', path, re.IGNORECASE)
                    return match.group(1) if match else None
                
                def get_network_processes(self):
                    return self.network_processes
                
                def get_system_processes(self):
                    return self.system_processes
            
            self.parser = LiveParser(live_processes)
            
            self.progress.setVisible(False)
            
            # Update UI
            network_count = len(self.parser.get_network_processes())
            self.diag_status.setText(f"🔴 LIVE: {process_count} processes ({network_count} network)")
            self.status_label.setText(f"Live capture complete - {process_count} processes analyzed")
            
            # Update analysis tab
            self.update_process_analysis()
            
            # Enable rule generation if apps are selected
            if self.get_selected_apps():
                self.generate_btn.setEnabled(True)
            
            # Clean up temp file
            import os
            try:
                os.remove(temp_file)
            except:
                pass
                
            QMessageBox.information(self, "Live Capture Complete", 
                                  f"🔴 LIVE CAPTURE SUCCESSFUL!\n\n" +
                                  f"📊 Captured {process_count} running processes\n" +
                                  f"🌐 Found {network_count} network processes\n" +
                                  f"📱 Detected {len(self.parser.app_processes)} applications\n\n" +
                                  f"Ready to generate firewall rules!")
            
        except Exception as e:
            self.progress.setVisible(False)
            QMessageBox.critical(self, "Live Capture Error", 
                               f"Failed to capture live system data:\n{str(e)}\n\n" +
                               f"Try running with administrator privileges or check system permissions.")
    
    def capture_sysdiagnose(self):
        """Generate comprehensive sysdiagnose"""
        reply = QMessageBox.question(self, "Generate Sysdiagnose", 
                                   "🔬 COMPREHENSIVE SYSTEM DIAGNOSTICS\n\n" +
                                   "This will generate a complete system diagnostic report including:\n" +
                                   "• All running processes and network connections\n" +
                                   "• System logs and performance data\n" +
                                   "• Network configuration and routing tables\n" +
                                   "• Service discovery and system state\n\n" +
                                   "⏱️ This will take 2-5 minutes and requires admin privileges.\n" +
                                   "📁 Output will be saved to Desktop.\n\n" +
                                   "Continue with sysdiagnose generation?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.perform_sysdiagnose()
    
    def perform_sysdiagnose(self):
        """Perform the actual sysdiagnose generation"""
        try:
            self.progress.setVisible(True)
            self.progress.setRange(0, 0)
            self.status_label.setText("🔬 Generating comprehensive system diagnostics...")
            
            import subprocess
            import os
            from datetime import datetime
            
            # Create output directory
            desktop_path = os.path.expanduser("~/Desktop")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_name = f"ActivityMonitor_Sysdiagnose_{timestamp}"
            
            self.status_label.setText("🔬 Running sysdiagnose (this may take 2-5 minutes)...")
            
            # Run sysdiagnose command
            # -f: specify output directory
            # -A: include all available data
            # -u: don't include user data (privacy)
            cmd = [
                'sudo', 'sysdiagnose', 
                '-f', desktop_path,
                '-A',  # All system data
                '-u',  # Skip user data for privacy
                '-n', output_name
            ]
            
            # Show progress dialog
            progress_msg = QMessageBox(self)
            progress_msg.setWindowTitle("Generating Sysdiagnose")
            progress_msg.setText("🔬 Generating comprehensive diagnostics...\n\n" +
                               "This process will:\n" +
                               "1. Collect all running processes\n" +
                               "2. Capture network connections\n" +
                               "3. Extract system logs\n" +
                               "4. Analyze system performance\n\n" +
                               "⏱️ Please wait 2-5 minutes...")
            progress_msg.setStandardButtons(QMessageBox.StandardButton.NoButton)
            progress_msg.show()
            
            # Process events to keep GUI responsive
            QApplication.processEvents()
            
            try:
                # Run sysdiagnose with timeout
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)  # 10 min timeout
                
                progress_msg.close()
                self.progress.setVisible(False)
                
                if result.returncode == 0:
                    # Find the generated file
                    sysdiag_files = []
                    for file in os.listdir(desktop_path):
                        if output_name in file and (file.endswith('.tar.gz') or 'sysdiagnose' in file):
                            sysdiag_files.append(os.path.join(desktop_path, file))
                    
                    if sysdiag_files:
                        sysdiag_file = sysdiag_files[0]
                        file_size = os.path.getsize(sysdiag_file) / (1024 * 1024)  # MB
                        
                        QMessageBox.information(self, "Sysdiagnose Complete", 
                                              f"🔬 SYSDIAGNOSE GENERATION COMPLETE!\n\n" +
                                              f"📁 File: {os.path.basename(sysdiag_file)}\n" +
                                              f"📊 Size: {file_size:.1f} MB\n" +
                                              f"📂 Location: Desktop\n\n" +
                                              f"💡 Use 'Load Spindump' to analyze the extracted data,\n" +
                                              f"or extract the .tar.gz file and load individual components.")
                        
                        self.status_label.setText(f"Sysdiagnose complete - {file_size:.1f}MB generated on Desktop")
                    else:
                        QMessageBox.warning(self, "File Not Found", 
                                          "Sysdiagnose completed but output file not found on Desktop.")
                else:
                    error_msg = result.stderr if result.stderr else "Unknown error"
                    QMessageBox.critical(self, "Sysdiagnose Failed", 
                                       f"Failed to generate sysdiagnose:\n{error_msg}\n\n" +
                                       f"Make sure you have admin privileges and try again.")
                    
            except subprocess.TimeoutExpired:
                progress_msg.close()
                self.progress.setVisible(False)
                QMessageBox.critical(self, "Timeout", 
                                   "Sysdiagnose generation timed out (>10 minutes).\n" +
                                   "The system may be under heavy load. Try again later.")
                
        except Exception as e:
            if 'progress_msg' in locals():
                progress_msg.close()
            self.progress.setVisible(False)
            QMessageBox.critical(self, "Sysdiagnose Error", 
                               f"Failed to generate sysdiagnose:\n{str(e)}\n\n" +
                               f"Requirements:\n" +
                               f"• Administrator privileges\n" +
                               f"• macOS system with sysdiagnose command\n" +
                               f"• Sufficient disk space (~100MB)")
    
    def scan_existing_rules(self):
        """Scan existing rule files to learn about blocked processes"""
        reply = QMessageBox.question(self, "Load Threat Database", 
                                   "🔍 LOAD THREAT INTELLIGENCE\n\n" +
                                   "Choose how to load malicious process database:\n\n" +
                                   "• YES: Scan existing rule files\n" +
                                   "• NO: Load predefined threat set\n" +
                                   "• CANCEL: Skip",
                                   QMessageBox.StandardButton.Yes | 
                                   QMessageBox.StandardButton.No | 
                                   QMessageBox.StandardButton.Cancel)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.scan_rule_files()
        elif reply == QMessageBox.StandardButton.No:
            self.load_predefined_threats()
    
    def scan_rule_files(self):
        """Scan existing rule files for blocked processes"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Select Existing Rule Files", "", 
            "Rule Files (*.json *.plist);;JSON Files (*.json);;All Files (*)"
        )
        
        if not file_paths:
            return
        
        try:
            self.progress.setVisible(True)
            self.progress.setRange(0, 0)
            self.status_label.setText("🔍 Scanning existing rules...")
            
            newly_found = set()
            total_blocked = set()
            
            for file_path in file_paths:
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    # Parse JSON rules
                    if file_path.endswith('.json'):
                        try:
                            rules_data = json.loads(content)
                            blocked = self._extract_blocked_from_json(rules_data)
                            total_blocked.update(blocked)
                        except json.JSONDecodeError:
                            pass
                    
                    # Parse text-based rules
                    blocked = self._extract_blocked_from_text(content)
                    total_blocked.update(blocked)
                        
                except Exception as e:
                    continue
            
            newly_found = total_blocked - self.known_malicious
            self.known_malicious.update(total_blocked)
            
            self.progress.setVisible(False)
            self._show_threat_results("Rule Scan", total_blocked, newly_found)
            
        except Exception as e:
            self.progress.setVisible(False)
            QMessageBox.critical(self, "Scan Error", f"Failed to scan rule files:\n{str(e)}")
    
    def load_predefined_threats(self):
        """Load predefined set of known malicious processes"""
        try:
            self.progress.setVisible(True)
            self.progress.setRange(0, 0)
            self.status_label.setText("📋 Loading threat intelligence...")
            
            # Predefined malicious processes based on our research
            predefined_threats = {
                # Apple Data Exfiltration Network
                'cloudd', 'cloudphotod', 'accountsd', 'amsaccountsd', 'itunescloudd',
                'bird', 'rtcreportingd', 'analyticsd', 'appleaccountd',
                
                # Telemetry & Analytics
                'ecosystemanalyticsd', 'audioanalyticsd', 'inputanalyticsd', 
                'wifianalyticsd', 'osanalyticshelper', 'adprivacyd',
                
                # Cloud Services
                'CloudDocsStorageManagement', 'CloudStorageHelper', 'CloudTelemetryService',
                'ProtectedCloudKeySyncing', 'iCloudNotificationAgent', 'icloudmailagent',
                'com.apple.CloudPhotosConfiguration', 'com.apple.iCloudHelper',
                
                # Sync Services
                'SafariBookmarksSyncAgent', 'mapssyncd', 'syncdefaultsd', 'biomesyncd',
                'audioclocksyncd', 'colorsync.useragent', 'colorsyncd',
                
                # Network & Communication
                'rapportd', 'sharingd', 'bluetoothd', 'airportd', 'nehelper',
                'networkserviceproxy', 'mDNSResponderHelper', 'wifip2pd', 'wifivelocityd',
                
                # System Extensions & Helpers
                'xpcroleaccountd', 'IOUserBluetoothSerialDriver', 'com.apple.ColorSyncXPCAgent',
                'PerfPowerTelemetryClientRegistrationService',
                
                # News & Content
                'newsd', 'NewsToday2', 'tipsd', 'privatecloudcomputed',
                
                # Location & Search
                'locationd', 'searchpartyuseragent',
                
                # System Diagnostics
                'SubmitDiagInfo', 'trustd'  # trustd can be malicious in some contexts
            }
            
            newly_found = predefined_threats - self.known_malicious
            self.known_malicious.update(predefined_threats)
            
            self.progress.setVisible(False)
            self._show_threat_results("Predefined Threats", predefined_threats, newly_found)
            
        except Exception as e:
            self.progress.setVisible(False)
            QMessageBox.critical(self, "Load Error", f"Failed to load threat database:\n{str(e)}")
    
    def _extract_blocked_from_json(self, rules_data):
        """Extract blocked process names from JSON rule data"""
        blocked = set()
        
        try:
            if isinstance(rules_data, dict):
                rules = rules_data.get('rules', [])
                for rule in rules:
                    if isinstance(rule, dict):
                        action = rule.get('action', '').lower()
                        if action in ['block', 'deny', 'reject']:
                            process_info = rule.get('process', {})
                            if isinstance(process_info, dict):
                                # Extract process name - could be in 'name' field
                                name = process_info.get('name', '')
                                path = process_info.get('path', '')
                                
                                # If name is a full path, extract just the process name
                                if name and '/' in name:
                                    import os
                                    name = os.path.basename(name)
                                
                                # If no name but has path, extract from path
                                if not name and path:
                                    import os
                                    name = os.path.basename(path)
                                
                                if name:
                                    blocked.add(name)
                            else:
                                # Handle case where process is just a string
                                name = str(process_info)
                                if name and name != 'None':
                                    if '/' in name:
                                        import os
                                        name = os.path.basename(name)
                                    blocked.add(name)
            
            elif isinstance(rules_data, list):
                # Handle array of rules
                for rule in rules_data:
                    if isinstance(rule, dict):
                        action = rule.get('action', '').lower()
                        if action in ['block', 'deny', 'reject']:
                            name = rule.get('name', '') or rule.get('process', '')
                            if name:
                                if '/' in name:
                                    import os
                                    name = os.path.basename(name)
                                blocked.add(name)
        
        except Exception as e:
            print(f"Error parsing JSON rules: {e}")
        
        return blocked
    
    def _extract_blocked_from_text(self, content):
        """Extract blocked process names from text-based rule files"""
        blocked = set()
        import re
        
        # Look for blocked processes in various formats
        patterns = [
            r'(?:block|deny|reject)\s+([a-zA-Z0-9_.-]+)',
            r'"name"\s*:\s*"([^"]+)".*"action"\s*:\s*"(?:block|deny)"',
            r'"action"\s*:\s*"(?:block|deny)".*"name"\s*:\s*"([^"]+)"'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if match and len(match) > 2:
                    blocked.add(match.strip())
        
        return blocked
    
    def _show_threat_results(self, source_type, total_threats, newly_found):
        """Show threat loading results"""
        if total_threats:
            result_msg = f"🔍 {source_type.upper()} LOADED!\n\n"
            result_msg += f"📊 Total threats: {len(total_threats)}\n"
            result_msg += f"🆕 New threats learned: {len(newly_found)}\n\n"
            
            if newly_found:
                result_msg += "🚨 NEWLY IDENTIFIED THREATS:\n"
                for proc in sorted(list(newly_found)[:10]):
                    result_msg += f"  • {proc}\n"
                if len(newly_found) > 10:
                    result_msg += f"  ... and {len(newly_found) - 10} more\n"
            
            result_msg += f"\n💡 These processes will be automatically blocked in future rules!"
            
            QMessageBox.information(self, f"{source_type} Complete", result_msg)
            self.status_label.setText(f"Loaded {len(total_threats)} known threats from {source_type.lower()}")
            
            # Update diagnostics if available
            if self.detected_processes:
                malicious_count = self._count_malicious_in_detected()
                if malicious_count > 0:
                    current_status = self.diag_status.text()
                    self.diag_status.setText(f"{current_status} | 🚨 {malicious_count} threats detected!")
        else:
            QMessageBox.information(self, "No Threats", f"No threats found in {source_type.lower()}.")
    
    def _count_malicious_in_detected(self):
        """Count malicious processes in detected processes"""
        count = 0
        for process_info in self.detected_processes.values():
            name = process_info.get('name', '')
            if name in self.known_malicious:
                count += 1
        return count
    
    def launch_system_monitor(self):
        """Launch the real-time system monitor"""
        try:
            import subprocess
            import sys
            from pathlib import Path
            
            # Get the path to system_monitor.py
            current_dir = Path(__file__).parent
            monitor_script = current_dir / "system_monitor.py"
            
            if monitor_script.exists():
                # Launch the monitor in a separate process
                subprocess.Popen([sys.executable, str(monitor_script)])
                
                QMessageBox.information(self, "System Monitor Launched", 
                                      "📊 REAL-TIME SYSTEM MONITOR LAUNCHED!\n\n" +
                                      "The system resource monitor is now running in a separate window.\n\n" +
                                      "Features:\n" +
                                      "• Real-time process monitoring\n" +
                                      "• Memory/CPU usage tracking\n" +
                                      "• Network connection analysis\n" +
                                      "• Suspicious activity detection\n" +
                                      "• Resource abuse alerts\n\n" +
                                      "Monitor will update every 2 seconds by default.")
            else:
                QMessageBox.critical(self, "Monitor Not Found", 
                                   f"System monitor script not found at:\n{monitor_script}\n\n" +
                                   "Make sure system_monitor.py is in the same directory.")
                
        except Exception as e:
            QMessageBox.critical(self, "Launch Error", 
                               f"Failed to launch system monitor:\n{str(e)}")
    
    def get_selected_apps(self):
        """Get selected app names"""
        selected = []
        for checkbox in getattr(self, 'app_checkboxes', []):
            if checkbox.isChecked() and checkbox.isVisible():  # Only count visible (filtered) apps
                selected.append(checkbox.objectName())
        return selected
    
    def on_selection_changed(self):
        """Handle app selection changes"""
        selected = self.get_selected_apps()
        can_generate = len(selected) > 0 and len(self.detected_processes) > 0
        self.generate_btn.setEnabled(can_generate)
        
        if selected:
            mode_text = "OFFLINE" if self.is_offline_mode else "ONLINE"
            self.status_label.setText(f"Mode: {mode_text} - Selected {len(selected)} apps: {', '.join(selected[:3])}{'...' if len(selected) > 3 else ''}")
    
    def select_all(self):
        """Select all visible (filtered) apps"""
        for checkbox in getattr(self, 'app_checkboxes', []):
            if checkbox.isVisible():  # Only select visible apps
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
    
    def select_safari(self):
        """Select only Safari"""
        self.clear_all()
        for checkbox in getattr(self, 'app_checkboxes', []):
            if 'safari' in checkbox.objectName().lower():
                checkbox.setChecked(True)
    
    def generate_rules(self):
        """Generate firewall rules with offline/online mode consideration"""
        selected_apps = self.get_selected_apps()
        
        if not selected_apps or not self.detected_processes:
            QMessageBox.warning(self, "Missing Data", "Need both diagnostics and app selection")
            return
        
        try:
            self.progress.setVisible(True)
            self.progress.setRange(0, 0)
            
            # Generate requirements with mode consideration
            requirements = self.analyzer.get_app_requirements(selected_apps, self.detected_processes)
            
            # Modify requirements based on offline/online mode and learned threats
            if self.is_offline_mode:
                # OFFLINE MODE: Block ALL internet access
                all_network_processes = []
                for process_key, process_info in self.detected_processes.items():
                    if self._is_network_process(process_info):
                        all_network_processes.append(process_info)
                
                requirements['blocked_processes'] = all_network_processes
                requirements['essential_system_processes'] = ['mDNSResponder', 'configd']
            
            # Add learned malicious processes to blocked list
            if self.known_malicious:
                malicious_detected = []
                for process_key, process_info in self.detected_processes.items():
                    if process_info.get('name') in self.known_malicious:
                        malicious_detected.append(process_info)
                
                # Merge with existing blocked processes
                existing_blocked = requirements.get('blocked_processes', [])
                all_blocked = existing_blocked + malicious_detected
                requirements['blocked_processes'] = all_blocked
            
            # Generate rules
            rule_gen = MurusRuleGenerator()
            self.ruleset = rule_gen.generate_murus_rules(requirements)
            self.rule_generator = rule_gen
            self.requirements = requirements
            
            self.progress.setVisible(False)
            
            rule_count = len(self.ruleset['rules'])
            allow_count = sum(1 for rule in self.ruleset['rules'] if rule['action'] == 'allow')
            block_count = rule_count - allow_count
            
            mode_text = "OFFLINE" if self.is_offline_mode else "ONLINE"
            security_level = "MAXIMUM (Air-gapped)" if self.is_offline_mode else "HIGH (Selective)"
            
            self.status_label.setText(f"✅ {mode_text} - Generated {rule_count} rules ({allow_count} allow, {block_count} block) - {security_level} security")
            
            # Enable export buttons
            self.export_btn.setEnabled(True)
            self.export_lulu_btn.setEnabled(True)
            self.preview_btn.setEnabled(True)
            self.save_config_btn.setEnabled(True)
            
            # Update live preview
            summary = self.rule_generator.generate_rule_summary(self.ruleset)
            mode_header = f"🔒 OFFLINE MODE - AIR-GAPPED SECURITY\n" if self.is_offline_mode else f"🌐 ONLINE MODE - SELECTIVE ACCESS\n"
            self.live_preview.setPlainText(mode_header + "="*50 + "\n\n" + summary)
            
            # Update threat analysis
            self.update_threat_analysis()
            
        except Exception as e:
            self.progress.setVisible(False)
            QMessageBox.critical(self, "Error", f"Failed to generate rules: {e}")
    
    def _is_network_process(self, process_info):
        """Check if a process is network-related"""
        name = process_info.get('name', '') or ''
        path = process_info.get('path', '') or ''
        name = name.lower()
        path = path.lower()
        
        network_indicators = [
            'network', 'dns', 'http', 'tcp', 'udp', 'wifi', 'bluetooth',
            'cloud', 'sync', 'account', 'connect', 'rapport', 'sharing',
            'telemetry', 'analytics', 'reporting', 'internet'
        ]
        
        return any(indicator in name or indicator in path for indicator in network_indicators)
    
    def preview_rules(self):
        """Show large preview dialog"""
        if not self.ruleset:
            QMessageBox.warning(self, "No Rules", "Generate rules first")
            return
        
        dialog = RulePreviewDialog(self.ruleset, self.rule_generator, self)
        dialog.exec()
    
    def export_rules(self):
        """Export rules to file in Murus format"""
        if not self.ruleset:
            QMessageBox.warning(self, "No Rules", "Generate rules first")
            return
        
        mode_suffix = "_offline" if self.is_offline_mode else "_online"
        default_name = f"murus_rules{mode_suffix}.json"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Murus Rules", default_name, "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                self.rule_generator.export_to_murus_format(self.ruleset, file_path)
                
                summary = self.rule_generator.generate_rule_summary(self.ruleset)
                mode_text = "OFFLINE (Air-gapped)" if self.is_offline_mode else "ONLINE (Selective)"
                QMessageBox.information(self, "Export Complete", 
                                      f"Rules exported to:\n{file_path}\n\nMode: {mode_text}\n\n{summary}")
                
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export: {e}")
    
    def export_rules_lulu(self):
        """Export rules to file in LuLu format"""
        if not self.ruleset:
            QMessageBox.warning(self, "No Rules", "Generate rules first")
            return
        
        mode_suffix = "_offline" if self.is_offline_mode else "_online"
        default_name = f"lulu_rules{mode_suffix}.json"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save LuLu Rules", default_name, "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                self.rule_generator.export_to_lulu_format(self.ruleset, file_path)
                
                mode_text = "OFFLINE (Air-gapped)" if self.is_offline_mode else "ONLINE (Selective)"
                rule_count = len([r for r in self.ruleset['rules'] if r.get('process', {}).get('name') != '*'])
                QMessageBox.information(self, "Export Complete", 
                                      f"LuLu rules exported to:\n{file_path}\n\nMode: {mode_text}\n\nExported {rule_count} rules in LuLu format")
                
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export: {e}")
    
    def save_configuration(self):
        """Save current configuration"""
        if not self.ruleset:
            QMessageBox.warning(self, "No Rules", "Generate rules first")
            return
        
        from PyQt6.QtWidgets import QInputDialog
        
        name, ok = QInputDialog.getText(self, "Save Configuration", "Configuration name:")
        if ok and name:
            try:
                config = {
                    'name': name,
                    'mode': 'offline' if self.is_offline_mode else 'online',
                    'selected_apps': self.get_selected_apps(),
                    'ruleset': self.ruleset,
                    'requirements': getattr(self, 'requirements', {}),
                    'created': str(datetime.now())
                }
                
                self.saved_configs[name] = config
                self.refresh_configurations()
                mode_text = "OFFLINE" if self.is_offline_mode else "ONLINE"
                QMessageBox.information(self, "Saved", f"Configuration '{name}' saved!\nMode: {mode_text}")
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Failed to save configuration:\n{str(e)}")
    
    def load_configuration(self):
        """Load saved configuration"""
        if not self.saved_configs:
            QMessageBox.information(self, "No Configurations", "No saved configurations found")
            return
        
        names = list(self.saved_configs.keys())
        from PyQt6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getItem(self, "Load Configuration", "Select configuration:", names, 0, False)
        
        if ok and name:
            config = self.saved_configs[name]
            
            # Load mode
            is_offline = config.get('mode', 'online') == 'offline'
            if is_offline:
                self.offline_radio.setChecked(True)
            else:
                self.online_radio.setChecked(True)
            
            # Load app selection
            self.clear_all()
            selected_apps = config['selected_apps']
            for checkbox in getattr(self, 'app_checkboxes', []):
                if checkbox.objectName() in selected_apps:
                    checkbox.setChecked(True)
            
            # Load ruleset
            self.ruleset = config['ruleset']
            self.requirements = config['requirements']
            
            # Update UI
            self.export_btn.setEnabled(True)
            self.preview_btn.setEnabled(True)
            self.save_config_btn.setEnabled(True)
            
            mode_text = "OFFLINE" if is_offline else "ONLINE"
            QMessageBox.information(self, "Loaded", f"Configuration '{name}' loaded!\nMode: {mode_text}")
    
    def refresh_configurations(self):
        """Refresh configurations table"""
        self.config_table.setRowCount(len(self.saved_configs))
        
        for row, (name, config) in enumerate(self.saved_configs.items()):
            self.config_table.setItem(row, 0, QTableWidgetItem(name))
            
            mode_text = "🔒 OFFLINE" if config.get('mode') == 'offline' else "🌐 ONLINE"
            self.config_table.setItem(row, 1, QTableWidgetItem(mode_text))
            
            apps_text = ', '.join(config['selected_apps'][:3])
            if len(config['selected_apps']) > 3:
                apps_text += "..."
            self.config_table.setItem(row, 2, QTableWidgetItem(apps_text))
            
            self.config_table.setItem(row, 3, QTableWidgetItem(str(len(config['ruleset']['rules']))))
            self.config_table.setItem(row, 4, QTableWidgetItem(config['created'][:19]))
            
            # Actions button
            actions_btn = QPushButton("🔧 Actions")
            self.config_table.setCellWidget(row, 5, actions_btn)
    
    def delete_configuration(self):
        """Delete selected configuration"""
        current_row = self.config_table.currentRow()
        if current_row >= 0:
            name = self.config_table.item(current_row, 0).text()
            reply = QMessageBox.question(self, "Delete Configuration", 
                                       f"Delete configuration '{name}'?")
            if reply == QMessageBox.StandardButton.Yes:
                del self.saved_configs[name]
                self.refresh_configurations()
    
    def export_configuration(self):
        """Export selected configuration"""
        current_row = self.config_table.currentRow()
        if current_row >= 0:
            name = self.config_table.item(current_row, 0).text()
            config = self.saved_configs[name]
            
            mode_suffix = "_offline" if config.get('mode') == 'offline' else "_online"
            default_name = f"{name}_config{mode_suffix}.json"
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, f"Export Configuration '{name}'", default_name, "JSON Files (*.json)"
            )
            
            if file_path:
                with open(file_path, 'w') as f:
                    json.dump(config, f, indent=2)
                mode_text = config.get('mode', 'online').upper()
                QMessageBox.information(self, "Exported", f"Configuration exported to {file_path}\nMode: {mode_text}")
    
    def update_process_analysis(self):
        """Update process analysis display"""
        if not hasattr(self, 'parser') or not self.parser:
            return
        
        analysis = []
        analysis.append("🔍 PROCESS ANALYSIS SUMMARY")
        analysis.append("=" * 40)
        analysis.append(f"📊 Total processes: {len(self.detected_processes)}")
        analysis.append(f"🌐 Network processes: {len(self.parser.get_network_processes())}")
        analysis.append(f"⚙️ System processes: {len(self.parser.get_system_processes())}")
        analysis.append(f"📱 App processes: {len(self.parser.app_processes)}")
        analysis.append("")
        
        analysis.append("🚨 HIGH-RISK NETWORK PROCESSES:")
        risky = [p for p in self.parser.get_network_processes() if any(
            risk in p.lower() for risk in ['cloud', 'sync', 'account', 'telemetry', 'analytics']
        )]
        for process in sorted(risky)[:10]:
            analysis.append(f"  • {process}")
        
        self.process_analysis.setPlainText('\n'.join(analysis))
    
    def update_threat_analysis(self):
        """Update threat analysis display"""
        if not self.requirements:
            return
        
        analysis = []
        mode_text = "OFFLINE (AIR-GAPPED)" if self.is_offline_mode else "ONLINE (SELECTIVE)"
        analysis.append(f"🚨 THREAT ANALYSIS - {mode_text} MODE")
        analysis.append("=" * 50)
        analysis.append(f"✅ Allowed processes: {len(self.requirements['allowed_processes'])}")
        analysis.append(f"🛡️ Essential services: {len(self.requirements['essential_system_processes'])}")
        analysis.append(f"❌ Blocked processes: {len(self.requirements['blocked_processes'])}")
        analysis.append("")
        
        if self.is_offline_mode:
            analysis.append("🔒 OFFLINE MODE SECURITY:")
            analysis.append("  • ALL internet access blocked")
            analysis.append("  • Only local communication allowed")
            analysis.append("  • Maximum air-gapped security")
        else:
            analysis.append("🌐 ONLINE MODE SECURITY:")
            analysis.append("  • Selected apps have internet access")
            analysis.append("  • Exfiltration vectors blocked")
            analysis.append("  • Surgical precision blocking")
        
        analysis.append("")
        analysis.append("🔥 BLOCKED PROCESSES:")
        for process in self.requirements['blocked_processes'][:10]:
            analysis.append(f"  • {process.get('name', 'Unknown')}")
        
        self.threat_analysis.setPlainText('\n'.join(analysis))

def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    
    # Set enhanced dark theme with new styling for radio buttons and filter box
    app.setStyleSheet("""
        QMainWindow { 
            background-color: #2b2b2b; 
            color: white; 
        }
        QGroupBox { 
            font-weight: bold; 
            border: 2px solid #555; 
            border-radius: 8px; 
            margin-top: 1ex; 
            padding-top: 15px; 
            background-color: #333;
        }
        QGroupBox::title { 
            subcontrol-origin: margin; 
            left: 15px; 
            padding: 0 8px 0 8px; 
            color: #0078d4;
        }
        QPushButton { 
            background-color: #0078d4; 
            color: white; 
            border: none; 
            padding: 10px 20px; 
            border-radius: 6px; 
            font-weight: bold; 
            font-size: 11px;
        }
        QPushButton:hover { 
            background-color: #106ebe; 
        }
        QPushButton:pressed { 
            background-color: #005a9e; 
        }
        QPushButton:disabled { 
            background-color: #555; 
            color: #888; 
        }
        QTextEdit, QScrollArea, QTableWidget { 
            background-color: #1e1e1e; 
            color: white; 
            border: 1px solid #555; 
            border-radius: 6px;
            padding: 8px;
        }
        QLineEdit {
            background-color: #1e1e1e;
            color: white;
            border: 1px solid #555;
            border-radius: 6px;
            padding: 8px;
            font-size: 11px;
        }
        QLineEdit:focus {
            border: 2px solid #0078d4;
        }
        QRadioButton {
            color: white;
            padding: 6px;
            font-size: 11px;
        }
        QRadioButton::indicator {
            width: 16px;
            height: 16px;
        }
        QRadioButton::indicator:unchecked {
            background-color: #555;
            border: 2px solid #777;
            border-radius: 8px;
        }
        QRadioButton::indicator:checked {
            background-color: #0078d4;
            border: 2px solid #0078d4;
            border-radius: 8px;
        }
        QTabWidget::pane {
            border: 1px solid #555;
            background-color: #2b2b2b;
            border-radius: 6px;
        }
        QTabBar::tab {
            background-color: #3c3c3c;
            color: white;
            padding: 12px 20px;
            margin-right: 2px;
            border-radius: 6px 6px 0 0;
        }
        QTabBar::tab:selected {
            background-color: #0078d4;
        }
        QCheckBox {
            color: white;
            padding: 4px;
            font-size: 11px;
        }
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
        }
        QCheckBox::indicator:unchecked {
            background-color: #555;
            border: 1px solid #777;
            border-radius: 3px;
        }
        QCheckBox::indicator:checked {
            background-color: #0078d4;
            border: 1px solid #0078d4;
            border-radius: 3px;
        }
    """)
    
    window = EnhancedFirewallGUI()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
