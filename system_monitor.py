#!/usr/bin/env python3
"""
ActivityMonitorDefenseMonster - System Resource Monitor
Real-time monitoring for suspicious memory/network activity
"""

import sys
import json
import subprocess
import time
import re
from datetime import datetime
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QTableWidget, QTableWidgetItem, QLabel, 
                            QPushButton, QGroupBox, QProgressBar, QTextEdit,
                            QHeaderView, QTabWidget, QCheckBox, QSpinBox,
                            QMessageBox, QSplitter)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor

class SystemMonitorThread(QThread):
    """Background thread for system monitoring"""
    data_updated = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.update_interval = 2000  # 2 seconds
        
    def run(self):
        """Main monitoring loop"""
        while self.running:
            try:
                data = self.collect_system_data()
                self.data_updated.emit(data)
                self.msleep(self.update_interval)
            except Exception as e:
                print(f"Monitor error: {e}")
                self.msleep(5000)  # Wait 5 seconds on error
    
    def collect_system_data(self):
        """Collect comprehensive system resource data"""
        data = {
            'processes': [],
            'network': [],
            'system_stats': {},
            'timestamp': datetime.now().strftime("%H:%M:%S")
        }
        
        try:
            # Get process information with memory and CPU
            ps_cmd = ['ps', 'aux']
            ps_result = subprocess.run(ps_cmd, capture_output=True, text=True, timeout=10)
            
            if ps_result.returncode == 0:
                lines = ps_result.stdout.strip().split('\n')[1:]  # Skip header
                
                for line in lines:
                    parts = line.split(None, 10)
                    if len(parts) >= 11:
                        try:
                            process = {
                                'user': parts[0],
                                'pid': int(parts[1]),
                                'cpu_percent': float(parts[2]),
                                'memory_percent': float(parts[3]),
                                'memory_kb': int(parts[5]) if parts[5].isdigit() else 0,
                                'name': parts[10].split()[0] if parts[10] else 'Unknown',
                                'full_command': parts[10] if len(parts) > 10 else '',
                                'suspicious_score': 0
                            }
                            
                            # Calculate suspicious score
                            process['suspicious_score'] = self.calculate_suspicious_score(process)
                            data['processes'].append(process)
                            
                        except (ValueError, IndexError):
                            continue
            
            # Get network connections
            try:
                lsof_cmd = ['lsof', '-i', '-n', '-P']
                lsof_result = subprocess.run(lsof_cmd, capture_output=True, text=True, timeout=10)
                
                if lsof_result.returncode == 0:
                    for line in lsof_result.stdout.strip().split('\n')[1:]:
                        parts = line.split()
                        if len(parts) >= 8:
                            try:
                                connection = {
                                    'process': parts[0],
                                    'pid': int(parts[1]) if parts[1].isdigit() else 0,
                                    'user': parts[2],
                                    'protocol': parts[7] if len(parts) > 7 else 'Unknown',
                                    'local_address': parts[8] if len(parts) > 8 else '',
                                    'remote_address': parts[9] if len(parts) > 9 else '',
                                    'state': parts[10] if len(parts) > 10 else ''
                                }
                                data['network'].append(connection)
                            except (ValueError, IndexError):
                                continue
            except:
                pass  # Network monitoring is optional
            
            # Get system-wide stats
            try:
                # Memory info
                vm_stat = subprocess.run(['vm_stat'], capture_output=True, text=True, timeout=5)
                if vm_stat.returncode == 0:
                    data['system_stats']['memory_info'] = vm_stat.stdout
                
                # Load average
                uptime = subprocess.run(['uptime'], capture_output=True, text=True, timeout=5)
                if uptime.returncode == 0:
                    data['system_stats']['load_average'] = uptime.stdout.strip()
                    
            except:
                pass
                
        except Exception as e:
            print(f"Data collection error: {e}")
        
        return data
    
    def calculate_suspicious_score(self, process):
        """Calculate suspicion score based on resource usage patterns"""
        score = 0
        
        # High memory usage
        if process['memory_percent'] > 10:
            score += 3
        elif process['memory_percent'] > 5:
            score += 2
        elif process['memory_percent'] > 2:
            score += 1
            
        # High CPU usage
        if process['cpu_percent'] > 50:
            score += 3
        elif process['cpu_percent'] > 20:
            score += 2
        elif process['cpu_percent'] > 10:
            score += 1
        
        # Suspicious process names
        suspicious_names = [
            'cloudd', 'bird', 'accountsd', 'rtcreportingd', 'analyticsd',
            'amsaccountsd', 'itunescloudd', 'rapportd', 'sharingd'
        ]
        
        name_lower = process['name'].lower()
        for sus_name in suspicious_names:
            if sus_name in name_lower:
                score += 5
                break
        
        # Unusual memory/CPU ratio
        if process['memory_percent'] > 0 and process['cpu_percent'] > 0:
            ratio = process['memory_percent'] / process['cpu_percent']
            if ratio > 10:  # High memory, low CPU (potential data hoarding)
                score += 2
            elif ratio < 0.1:  # High CPU, low memory (potential crypto mining)
                score += 2
        
        return min(score, 10)  # Cap at 10
    
    def stop(self):
        """Stop the monitoring thread"""
        self.running = False

class SystemMonitorGUI(QMainWindow):
    """Real-time system resource monitor"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔍 ActivityMonitor DefenseMonster - System Resource Monitor")
        self.setGeometry(100, 100, 1400, 900)
        
        # Data storage
        self.current_data = {}
        self.alert_thresholds = {
            'memory_percent': 15.0,
            'cpu_percent': 80.0,
            'suspicious_score': 5
        }
        
        # Setup monitoring thread
        self.monitor_thread = SystemMonitorThread()
        self.monitor_thread.data_updated.connect(self.update_display)
        
        self.setup_ui()
        self.start_monitoring()
    
    def setup_ui(self):
        """Setup the monitoring interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Title and status
        title = QLabel("🔍 Real-Time System Resource Monitor")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Status bar
        status_layout = QHBoxLayout()
        self.status_label = QLabel("🔄 Starting monitoring...")
        self.last_update_label = QLabel("Last update: Never")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.last_update_label)
        layout.addLayout(status_layout)
        
        # Control panel
        control_group = QGroupBox("⚙️ Monitoring Controls")
        control_layout = QHBoxLayout(control_group)
        
        self.auto_refresh = QCheckBox("Auto Refresh")
        self.auto_refresh.setChecked(True)
        control_layout.addWidget(self.auto_refresh)
        
        control_layout.addWidget(QLabel("Update Interval (sec):"))
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 60)
        self.interval_spin.setValue(2)
        self.interval_spin.valueChanged.connect(self.update_interval)
        control_layout.addWidget(self.interval_spin)
        
        refresh_btn = QPushButton("🔄 Refresh Now")
        refresh_btn.clicked.connect(self.manual_refresh)
        control_layout.addWidget(refresh_btn)
        
        alert_btn = QPushButton("🚨 Configure Alerts")
        alert_btn.clicked.connect(self.configure_alerts)
        control_layout.addWidget(alert_btn)
        
        control_layout.addStretch()
        layout.addWidget(control_group)
        
        # Main content tabs
        self.tab_widget = QTabWidget()
        
        # Process monitor tab
        self.setup_process_tab()
        
        # Network monitor tab
        self.setup_network_tab()
        
        # Alerts tab
        self.setup_alerts_tab()
        
        # System stats tab
        self.setup_system_tab()
        
        # NEW: Development tools monitoring tab
        self.setup_dev_tools_tab()
        
        layout.addWidget(self.tab_widget)
    
    def setup_process_tab(self):
        """Setup process monitoring tab"""
        process_widget = QWidget()
        layout = QVBoxLayout(process_widget)
        
        # Process table
        self.process_table = QTableWidget()
        self.process_table.setColumnCount(8)
        self.process_table.setHorizontalHeaderLabels([
            "Process", "PID", "CPU %", "Memory %", "Memory (MB)", 
            "User", "Suspicion", "Command"
        ])
        
        # Make table sortable and resizable
        self.process_table.setSortingEnabled(True)
        header = self.process_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)  # Command column
        
        layout.addWidget(self.process_table)
        
        # Process stats
        stats_layout = QHBoxLayout()
        self.process_count_label = QLabel("Processes: 0")
        self.high_cpu_label = QLabel("High CPU: 0")
        self.high_memory_label = QLabel("High Memory: 0")
        self.suspicious_label = QLabel("Suspicious: 0")
        
        stats_layout.addWidget(self.process_count_label)
        stats_layout.addWidget(self.high_cpu_label)
        stats_layout.addWidget(self.high_memory_label)
        stats_layout.addWidget(self.suspicious_label)
        stats_layout.addStretch()
        
        layout.addLayout(stats_layout)
        
        self.tab_widget.addTab(process_widget, "💻 Processes")
    
    def setup_network_tab(self):
        """Setup network monitoring tab"""
        network_widget = QWidget()
        layout = QVBoxLayout(network_widget)
        
        # Network connections table
        self.network_table = QTableWidget()
        self.network_table.setColumnCount(7)
        self.network_table.setHorizontalHeaderLabels([
            "Process", "PID", "User", "Protocol", "Local Address", 
            "Remote Address", "State"
        ])
        
        self.network_table.setSortingEnabled(True)
        header = self.network_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.network_table)
        
        # Network stats
        net_stats_layout = QHBoxLayout()
        self.connection_count_label = QLabel("Connections: 0")
        self.external_connections_label = QLabel("External: 0")
        
        net_stats_layout.addWidget(self.connection_count_label)
        net_stats_layout.addWidget(self.external_connections_label)
        net_stats_layout.addStretch()
        
        layout.addLayout(net_stats_layout)
        
        self.tab_widget.addTab(network_widget, "🌐 Network")
    
    def setup_alerts_tab(self):
        """Setup alerts and suspicious activity tab"""
        alerts_widget = QWidget()
        layout = QVBoxLayout(alerts_widget)
        
        # Alert log
        alert_label = QLabel("🚨 Security Alerts & Suspicious Activity")
        alert_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(alert_label)
        
        self.alert_log = QTextEdit()
        self.alert_log.setFont(QFont("Courier", 10))
        self.alert_log.setMaximumHeight(200)
        layout.addWidget(self.alert_log)
        
        # Suspicious processes table
        sus_label = QLabel("🔍 Most Suspicious Processes")
        sus_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(sus_label)
        
        self.suspicious_table = QTableWidget()
        self.suspicious_table.setColumnCount(6)
        self.suspicious_table.setHorizontalHeaderLabels([
            "Process", "Suspicion Score", "CPU %", "Memory %", "Reason", "Action"
        ])
        
        header = self.suspicious_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)  # Reason column
        
        layout.addWidget(self.suspicious_table)
        
        self.tab_widget.addTab(alerts_widget, "🚨 Alerts")
    
    def setup_system_tab(self):
        """Setup system statistics tab"""
        system_widget = QWidget()
        layout = QVBoxLayout(system_widget)
        
        # System overview
        overview_group = QGroupBox("📊 System Overview")
        overview_layout = QVBoxLayout(overview_group)
        
        self.system_stats_text = QTextEdit()
        self.system_stats_text.setFont(QFont("Courier", 10))
        self.system_stats_text.setMaximumHeight(150)
        overview_layout.addWidget(self.system_stats_text)
        
        layout.addWidget(overview_group)
        
        # Resource usage charts (text-based for now)
        charts_group = QGroupBox("📈 Resource Usage Trends")
        charts_layout = QVBoxLayout(charts_group)
        
        self.resource_trends = QTextEdit()
        self.resource_trends.setFont(QFont("Courier", 9))
        charts_layout.addWidget(self.resource_trends)
        
        layout.addWidget(charts_group)
        
        self.tab_widget.addTab(system_widget, "📊 System")
    
    def setup_dev_tools_tab(self):
        """Setup development tools monitoring tab"""
        dev_widget = QWidget()
        layout = QVBoxLayout(dev_widget)
        
        # Title
        title = QLabel("🛠️ Development Tools & AI Processes Monitor")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Windsurf processes section
        windsurf_group = QGroupBox("🌊 Windsurf IDE Processes")
        windsurf_layout = QVBoxLayout(windsurf_group)
        
        self.windsurf_table = QTableWidget()
        self.windsurf_table.setColumnCount(7)
        self.windsurf_table.setHorizontalHeaderLabels([
            "Process", "PID", "CPU %", "Memory %", "Memory (MB)", "Status", "Description"
        ])
        
        header = self.windsurf_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)  # Description column
        
        windsurf_layout.addWidget(self.windsurf_table)
        layout.addWidget(windsurf_group)
        
        # Language servers section
        lang_group = QGroupBox("🔤 Language Servers & ARM Processes")
        lang_layout = QVBoxLayout(lang_group)
        
        self.language_table = QTableWidget()
        self.language_table.setColumnCount(8)
        self.language_table.setHorizontalHeaderLabels([
            "Language/Tool", "Process", "PID", "CPU %", "Memory %", "Architecture", "Status", "Path"
        ])
        
        lang_header = self.language_table.horizontalHeader()
        lang_header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        lang_header.setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)  # Path column
        
        lang_layout.addWidget(self.language_table)
        layout.addWidget(lang_group)
        
        # Development stats
        dev_stats_layout = QHBoxLayout()
        self.windsurf_count_label = QLabel("Windsurf Processes: 0")
        self.lang_server_count_label = QLabel("Language Servers: 0")
        self.arm_process_count_label = QLabel("ARM Processes: 0")
        self.ai_helper_count_label = QLabel("AI Helpers: 0")
        
        dev_stats_layout.addWidget(self.windsurf_count_label)
        dev_stats_layout.addWidget(self.lang_server_count_label)
        dev_stats_layout.addWidget(self.arm_process_count_label)
        dev_stats_layout.addWidget(self.ai_helper_count_label)
        dev_stats_layout.addStretch()
        
        layout.addLayout(dev_stats_layout)
        
        # Development insights
        insights_group = QGroupBox("🧠 Development Environment Insights")
        insights_layout = QVBoxLayout(insights_group)
        
        self.dev_insights = QTextEdit()
        self.dev_insights.setFont(QFont("Courier", 9))
        self.dev_insights.setMaximumHeight(150)
        insights_layout.addWidget(self.dev_insights)
        
        layout.addWidget(insights_group)
        
        self.tab_widget.addTab(dev_widget, "🛠️ Dev Tools")
    
    def start_monitoring(self):
        """Start the monitoring thread"""
        self.monitor_thread.start()
        self.status_label.setText("🔄 Monitoring active...")
    
    def update_display(self, data):
        """Update all display elements with new data"""
        if not self.auto_refresh.isChecked():
            return
            
        self.current_data = data
        self.last_update_label.setText(f"Last update: {data['timestamp']}")
        
        # Update process table
        self.update_process_table(data['processes'])
        
        # Update network table
        self.update_network_table(data['network'])
        
        # Update alerts
        self.update_alerts(data['processes'])
        
        # Update system stats
        self.update_system_stats(data)
        
        # Update development tools
        self.update_dev_tools(data['processes'])
        
        # Update status
        process_count = len(data['processes'])
        network_count = len(data['network'])
        self.status_label.setText(f"✅ Active - {process_count} processes, {network_count} connections")
    
    def update_process_table(self, processes):
        """Update the process monitoring table"""
        # Sort by suspicious score first, then by memory usage
        sorted_processes = sorted(processes, 
                                key=lambda p: (p['suspicious_score'], p['memory_percent']), 
                                reverse=True)
        
        self.process_table.setRowCount(len(sorted_processes))
        
        high_cpu_count = 0
        high_memory_count = 0
        suspicious_count = 0
        
        for row, process in enumerate(sorted_processes):
            # Count statistics
            if process['cpu_percent'] > self.alert_thresholds['cpu_percent']:
                high_cpu_count += 1
            if process['memory_percent'] > self.alert_thresholds['memory_percent']:
                high_memory_count += 1
            if process['suspicious_score'] >= self.alert_thresholds['suspicious_score']:
                suspicious_count += 1
            
            # Populate table
            self.process_table.setItem(row, 0, QTableWidgetItem(process['name']))
            self.process_table.setItem(row, 1, QTableWidgetItem(str(process['pid'])))
            self.process_table.setItem(row, 2, QTableWidgetItem(f"{process['cpu_percent']:.1f}"))
            self.process_table.setItem(row, 3, QTableWidgetItem(f"{process['memory_percent']:.1f}"))
            self.process_table.setItem(row, 4, QTableWidgetItem(f"{process['memory_kb'] / 1024:.1f}"))
            self.process_table.setItem(row, 5, QTableWidgetItem(process['user']))
            
            # Suspicious score with color coding
            score_item = QTableWidgetItem(f"{process['suspicious_score']}/10")
            if process['suspicious_score'] >= 7:
                score_item.setBackground(QColor(255, 100, 100))  # Red
            elif process['suspicious_score'] >= 4:
                score_item.setBackground(QColor(255, 200, 100))  # Orange
            elif process['suspicious_score'] >= 2:
                score_item.setBackground(QColor(255, 255, 100))  # Yellow
            
            self.process_table.setItem(row, 6, score_item)
            self.process_table.setItem(row, 7, QTableWidgetItem(process['full_command'][:100]))
        
        # Update statistics
        self.process_count_label.setText(f"Processes: {len(processes)}")
        self.high_cpu_label.setText(f"High CPU: {high_cpu_count}")
        self.high_memory_label.setText(f"High Memory: {high_memory_count}")
        self.suspicious_label.setText(f"Suspicious: {suspicious_count}")
    
    def update_network_table(self, connections):
        """Update network connections table"""
        self.network_table.setRowCount(len(connections))
        
        external_count = 0
        
        for row, conn in enumerate(connections):
            self.network_table.setItem(row, 0, QTableWidgetItem(conn['process']))
            self.network_table.setItem(row, 1, QTableWidgetItem(str(conn['pid'])))
            self.network_table.setItem(row, 2, QTableWidgetItem(conn['user']))
            self.network_table.setItem(row, 3, QTableWidgetItem(conn['protocol']))
            self.network_table.setItem(row, 4, QTableWidgetItem(conn['local_address']))
            self.network_table.setItem(row, 5, QTableWidgetItem(conn['remote_address']))
            self.network_table.setItem(row, 6, QTableWidgetItem(conn['state']))
            
            # Count external connections
            if conn['remote_address'] and not any(local in conn['remote_address'] 
                                                for local in ['127.0.0.1', 'localhost', '*']):
                external_count += 1
        
        self.connection_count_label.setText(f"Connections: {len(connections)}")
        self.external_connections_label.setText(f"External: {external_count}")
    
    def update_alerts(self, processes):
        """Update alerts for suspicious activity"""
        # Find highly suspicious processes
        suspicious_processes = [p for p in processes if p['suspicious_score'] >= self.alert_thresholds['suspicious_score']]
        
        # Update suspicious processes table
        self.suspicious_table.setRowCount(len(suspicious_processes))
        
        for row, process in enumerate(suspicious_processes):
            self.suspicious_table.setItem(row, 0, QTableWidgetItem(process['name']))
            
            score_item = QTableWidgetItem(f"{process['suspicious_score']}/10")
            if process['suspicious_score'] >= 8:
                score_item.setBackground(QColor(255, 50, 50))
            elif process['suspicious_score'] >= 6:
                score_item.setBackground(QColor(255, 150, 50))
            self.suspicious_table.setItem(row, 1, score_item)
            
            self.suspicious_table.setItem(row, 2, QTableWidgetItem(f"{process['cpu_percent']:.1f}%"))
            self.suspicious_table.setItem(row, 3, QTableWidgetItem(f"{process['memory_percent']:.1f}%"))
            
            # Generate reason
            reasons = []
            if process['memory_percent'] > 10:
                reasons.append("High memory usage")
            if process['cpu_percent'] > 50:
                reasons.append("High CPU usage")
            
            suspicious_names = ['cloudd', 'bird', 'accountsd', 'rtcreportingd']
            if any(name in process['name'].lower() for name in suspicious_names):
                reasons.append("Known malicious process")
            
            reason_text = ", ".join(reasons) if reasons else "Resource pattern anomaly"
            self.suspicious_table.setItem(row, 4, QTableWidgetItem(reason_text))
            
            # Action button would go here
            self.suspicious_table.setItem(row, 5, QTableWidgetItem("Monitor"))
        
        # Add alerts to log for new high-priority threats
        current_time = datetime.now().strftime("%H:%M:%S")
        for process in suspicious_processes:
            if process['suspicious_score'] >= 8:
                alert_msg = f"[{current_time}] 🚨 HIGH THREAT: {process['name']} (PID: {process['pid']}) - Score: {process['suspicious_score']}/10\n"
                self.alert_log.append(alert_msg)
    
    def update_system_stats(self, data):
        """Update system statistics display"""
        stats_text = f"System Statistics - {data['timestamp']}\n"
        stats_text += "=" * 40 + "\n\n"
        
        # Process summary
        processes = data['processes']
        if processes:
            total_cpu = sum(p['cpu_percent'] for p in processes)
            total_memory = sum(p['memory_percent'] for p in processes)
            avg_cpu = total_cpu / len(processes)
            avg_memory = total_memory / len(processes)
            
            stats_text += f"Process Summary:\n"
            stats_text += f"  Total Processes: {len(processes)}\n"
            stats_text += f"  Total CPU Usage: {total_cpu:.1f}%\n"
            stats_text += f"  Total Memory Usage: {total_memory:.1f}%\n"
            stats_text += f"  Average CPU per Process: {avg_cpu:.2f}%\n"
            stats_text += f"  Average Memory per Process: {avg_memory:.2f}%\n\n"
        
        # System info
        if 'system_stats' in data:
            if 'load_average' in data['system_stats']:
                stats_text += f"Load Average: {data['system_stats']['load_average']}\n"
        
        self.system_stats_text.setPlainText(stats_text)
        
        # Resource trends (simple text-based for now)
        trends_text = "Resource Usage Trends\n"
        trends_text += "=" * 30 + "\n\n"
        trends_text += "Top 10 Memory Consumers:\n"
        
        top_memory = sorted(processes, key=lambda p: p['memory_percent'], reverse=True)[:10]
        for i, process in enumerate(top_memory, 1):
            trends_text += f"{i:2d}. {process['name']:<20} {process['memory_percent']:>6.1f}% ({process['memory_kb']/1024:>6.1f} MB)\n"
        
        trends_text += "\nTop 10 CPU Consumers:\n"
        top_cpu = sorted(processes, key=lambda p: p['cpu_percent'], reverse=True)[:10]
        for i, process in enumerate(top_cpu, 1):
            trends_text += f"{i:2d}. {process['name']:<20} {process['cpu_percent']:>6.1f}%\n"
        
        self.resource_trends.setPlainText(trends_text)
    
    def update_dev_tools(self, processes):
        """Update development tools monitoring"""
        # Identify development-related processes
        windsurf_processes = []
        language_servers = []
        arm_processes = []
        ai_helpers = []
        
        # Development tool patterns
        windsurf_patterns = [
            'windsurf', 'codewhisperer', 'cascade', 'windsurfer'
        ]
        
        language_server_patterns = [
            'typescript-language-server', 'python-language-server', 'rust-analyzer',
            'clangd', 'gopls', 'java-language-server', 'omnisharp', 'solargraph',
            'pyright', 'pylsp', 'jedi-language-server', 'vscode-json-languageserver',
            'vscode-html-languageserver', 'vscode-css-languageserver', 'eslint',
            'prettier', 'black', 'autopep8', 'mypy', 'flake8', 'rubocop'
        ]
        
        ai_helper_patterns = [
            'copilot', 'tabnine', 'kite', 'intellicode', 'aiassistant',
            'codeium', 'sourcegraph', 'github-copilot'
        ]
        
        for process in processes:
            name_lower = process['name'].lower()
            command_lower = process['full_command'].lower()
            
            # Check for Windsurf processes
            if any(pattern in name_lower or pattern in command_lower for pattern in windsurf_patterns):
                windsurf_processes.append(process)
            
            # Check for language servers
            elif any(pattern in name_lower or pattern in command_lower for pattern in language_server_patterns):
                language_servers.append(process)
            
            # Check for AI helpers
            elif any(pattern in name_lower or pattern in command_lower for pattern in ai_helper_patterns):
                ai_helpers.append(process)
            
            # Check for ARM processes (look for arm64 or specific ARM indicators)
            if 'arm64' in command_lower or self._is_arm_process(process):
                arm_processes.append(process)
        
        # Update Windsurf table
        self.windsurf_table.setRowCount(len(windsurf_processes))
        for row, process in enumerate(windsurf_processes):
            self.windsurf_table.setItem(row, 0, QTableWidgetItem(process['name']))
            self.windsurf_table.setItem(row, 1, QTableWidgetItem(str(process['pid'])))
            self.windsurf_table.setItem(row, 2, QTableWidgetItem(f"{process['cpu_percent']:.1f}"))
            self.windsurf_table.setItem(row, 3, QTableWidgetItem(f"{process['memory_percent']:.1f}"))
            self.windsurf_table.setItem(row, 4, QTableWidgetItem(f"{process['memory_kb'] / 1024:.1f}"))
            
            # Status based on resource usage
            if process['cpu_percent'] > 50 or process['memory_percent'] > 10:
                status = "🔥 High Load"
                status_item = QTableWidgetItem(status)
                status_item.setBackground(QColor(255, 200, 100))
            elif process['cpu_percent'] > 10 or process['memory_percent'] > 2:
                status = "⚡ Active"
                status_item = QTableWidgetItem(status)
                status_item.setBackground(QColor(100, 255, 100))
            else:
                status = "💤 Idle"
                status_item = QTableWidgetItem(status)
            
            self.windsurf_table.setItem(row, 5, status_item)
            
            # Description based on process name
            description = self._get_windsurf_description(process['name'])
            self.windsurf_table.setItem(row, 6, QTableWidgetItem(description))
        
        # Update Language Servers table
        all_lang_processes = language_servers + [p for p in arm_processes if p not in language_servers]
        self.language_table.setRowCount(len(all_lang_processes))
        
        for row, process in enumerate(all_lang_processes):
            # Determine language/tool type
            lang_type = self._identify_language_tool(process['name'], process['full_command'])
            self.language_table.setItem(row, 0, QTableWidgetItem(lang_type))
            
            self.language_table.setItem(row, 1, QTableWidgetItem(process['name']))
            self.language_table.setItem(row, 2, QTableWidgetItem(str(process['pid'])))
            self.language_table.setItem(row, 3, QTableWidgetItem(f"{process['cpu_percent']:.1f}"))
            self.language_table.setItem(row, 4, QTableWidgetItem(f"{process['memory_percent']:.1f}"))
            
            # Architecture detection
            arch = self._detect_architecture(process)
            arch_item = QTableWidgetItem(arch)
            if 'ARM64' in arch:
                arch_item.setBackground(QColor(100, 200, 255))  # Blue for ARM
            self.language_table.setItem(row, 5, arch_item)
            
            # Status
            if process in language_servers:
                status = "🔤 Language Server"
            elif process in arm_processes:
                status = "🏗️ ARM Process"
            else:
                status = "🛠️ Dev Tool"
            self.language_table.setItem(row, 6, QTableWidgetItem(status))
            
            # Path (truncated)
            path = process['full_command'][:80] + "..." if len(process['full_command']) > 80 else process['full_command']
            self.language_table.setItem(row, 7, QTableWidgetItem(path))
        
        # Update statistics
        self.windsurf_count_label.setText(f"Windsurf Processes: {len(windsurf_processes)}")
        self.lang_server_count_label.setText(f"Language Servers: {len(language_servers)}")
        self.arm_process_count_label.setText(f"ARM Processes: {len(arm_processes)}")
        self.ai_helper_count_label.setText(f"AI Helpers: {len(ai_helpers)}")
        
        # Generate development insights
        insights = self._generate_dev_insights(windsurf_processes, language_servers, arm_processes, ai_helpers)
        self.dev_insights.setPlainText(insights)
    
    def _is_arm_process(self, process):
        """Check if process is running on ARM architecture"""
        # Check for ARM-specific indicators in the process
        command = process['full_command'].lower()
        name = process['name'].lower()
        
        arm_indicators = [
            'arm64', 'aarch64', '/opt/homebrew/', 'apple silicon',
            'rosetta', 'translated'
        ]
        
        return any(indicator in command or indicator in name for indicator in arm_indicators)
    
    def _get_windsurf_description(self, process_name):
        """Get description for Windsurf-related processes"""
        name_lower = process_name.lower()
        
        descriptions = {
            'windsurf': '🌊 Main Windsurf IDE Process',
            'cascade': '🤖 Cascade AI Assistant',
            'codewhisperer': '💡 AWS CodeWhisperer Integration',
            'electron': '⚡ Electron Framework (IDE UI)',
            'node': '🟢 Node.js Runtime (Extensions)',
            'python': '🐍 Python Language Support'
        }
        
        for key, desc in descriptions.items():
            if key in name_lower:
                return desc
        
        return '🛠️ Development Tool Component'
    
    def _identify_language_tool(self, name, command):
        """Identify the language or tool type"""
        name_lower = name.lower()
        command_lower = command.lower()
        
        language_map = {
            'python': '🐍 Python',
            'node': '🟢 Node.js',
            'typescript': '🔷 TypeScript',
            'rust': '🦀 Rust',
            'go': '🐹 Go',
            'java': '☕ Java',
            'clang': '🔧 C/C++',
            'swift': '🦉 Swift',
            'ruby': '💎 Ruby',
            'php': '🐘 PHP',
            'eslint': '📏 ESLint',
            'prettier': '💅 Prettier',
            'black': '⚫ Black (Python)',
            'mypy': '🔍 MyPy',
            'arm64': '🏗️ ARM64',
            'rosetta': '🔄 Rosetta Translation'
        }
        
        for key, lang in language_map.items():
            if key in name_lower or key in command_lower:
                return lang
        
        return '🛠️ Dev Tool'
    
    def _detect_architecture(self, process):
        """Detect process architecture"""
        command = process['full_command'].lower()
        
        if 'arm64' in command or 'aarch64' in command:
            return '🏗️ ARM64 Native'
        elif '/opt/homebrew/' in command:
            return '🏗️ ARM64 (Homebrew)'
        elif 'rosetta' in command or 'translated' in command:
            return '🔄 x86_64 (Rosetta)'
        elif 'x86_64' in command:
            return '💻 x86_64 Native'
        else:
            return '❓ Unknown'
    
    def _generate_dev_insights(self, windsurf_processes, language_servers, arm_processes, ai_helpers):
        """Generate development environment insights"""
        insights = []
        insights.append("🧠 DEVELOPMENT ENVIRONMENT ANALYSIS")
        insights.append("=" * 45)
        insights.append("")
        
        # Windsurf analysis
        if windsurf_processes:
            total_windsurf_memory = sum(p['memory_percent'] for p in windsurf_processes)
            total_windsurf_cpu = sum(p['cpu_percent'] for p in windsurf_processes)
            
            insights.append(f"🌊 WINDSURF IDE STATUS:")
            insights.append(f"  • Active Processes: {len(windsurf_processes)}")
            insights.append(f"  • Total Memory Usage: {total_windsurf_memory:.1f}%")
            insights.append(f"  • Total CPU Usage: {total_windsurf_cpu:.1f}%")
            
            if total_windsurf_memory > 20:
                insights.append("  ⚠️  HIGH MEMORY USAGE - Consider restarting IDE")
            elif total_windsurf_memory > 10:
                insights.append("  💡 MODERATE MEMORY USAGE - Normal for large projects")
            else:
                insights.append("  ✅ OPTIMAL MEMORY USAGE")
            
            insights.append("")
        else:
            insights.append("🌊 WINDSURF IDE: Not detected")
            insights.append("")
        
        # Language servers analysis
        if language_servers:
            insights.append(f"🔤 LANGUAGE SERVERS ({len(language_servers)} active):")
            for server in language_servers[:5]:  # Show top 5
                lang_type = self._identify_language_tool(server['name'], server['full_command'])
                insights.append(f"  • {lang_type}: {server['memory_percent']:.1f}% memory, {server['cpu_percent']:.1f}% CPU")
            
            if len(language_servers) > 5:
                insights.append(f"  ... and {len(language_servers) - 5} more")
            insights.append("")
        
        # ARM analysis
        if arm_processes:
            native_arm = len([p for p in arm_processes if 'arm64' in p['full_command'].lower()])
            rosetta = len([p for p in arm_processes if 'rosetta' in p['full_command'].lower()])
            
            insights.append(f"🏗️ ARM ARCHITECTURE ANALYSIS:")
            insights.append(f"  • Total ARM-related processes: {len(arm_processes)}")
            insights.append(f"  • Native ARM64 processes: {native_arm}")
            insights.append(f"  • Rosetta translated processes: {rosetta}")
            
            if rosetta > native_arm:
                insights.append("  💡 Consider using ARM-native development tools for better performance")
            else:
                insights.append("  ✅ Good ARM64 native adoption")
            
            insights.append("")
        
        # AI helpers analysis
        if ai_helpers:
            insights.append(f"🤖 AI DEVELOPMENT ASSISTANTS:")
            for helper in ai_helpers:
                insights.append(f"  • {helper['name']}: {helper['memory_percent']:.1f}% memory")
            insights.append("")
        
        # Performance recommendations
        insights.append("📈 PERFORMANCE RECOMMENDATIONS:")
        total_dev_memory = sum(p['memory_percent'] for p in windsurf_processes + language_servers + ai_helpers)
        
        if total_dev_memory > 40:
            insights.append("  🔥 HIGH: Development tools using >40% memory")
            insights.append("  💡 Restart IDE or close unused language servers")
        elif total_dev_memory > 20:
            insights.append("  ⚡ MODERATE: Development tools using >20% memory")
            insights.append("  💡 Monitor for memory leaks in extensions")
        else:
            insights.append("  ✅ OPTIMAL: Development tools memory usage is healthy")
        
        return '\n'.join(insights)
    
    def update_interval(self, value):
        """Update monitoring interval"""
        self.monitor_thread.update_interval = value * 1000  # Convert to milliseconds
    
    def manual_refresh(self):
        """Force immediate refresh"""
        # This would trigger an immediate data collection
        pass
    
    def configure_alerts(self):
        """Configure alert thresholds"""
        QMessageBox.information(self, "Alert Configuration", 
                              "Alert configuration dialog would open here.\n\n" +
                              "Current thresholds:\n" +
                              f"• Memory: {self.alert_thresholds['memory_percent']}%\n" +
                              f"• CPU: {self.alert_thresholds['cpu_percent']}%\n" +
                              f"• Suspicion Score: {self.alert_thresholds['suspicious_score']}/10")
    
    def closeEvent(self, event):
        """Clean shutdown"""
        self.monitor_thread.stop()
        self.monitor_thread.wait()
        event.accept()

def main():
    """Launch the system monitor"""
    app = QApplication(sys.argv)
    
    # Dark theme
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
            padding: 8px 16px; 
            border-radius: 6px; 
            font-weight: bold; 
        }
        QPushButton:hover { 
            background-color: #106ebe; 
        }
        QTableWidget { 
            background-color: #1e1e1e; 
            color: white; 
            border: 1px solid #555; 
            border-radius: 6px;
            gridline-color: #444;
        }
        QTableWidget::item {
            padding: 4px;
        }
        QTableWidget::item:selected {
            background-color: #0078d4;
        }
        QHeaderView::section {
            background-color: #444;
            color: white;
            padding: 8px;
            border: 1px solid #555;
            font-weight: bold;
        }
        QTextEdit { 
            background-color: #1e1e1e; 
            color: white; 
            border: 1px solid #555; 
            border-radius: 6px;
            padding: 8px;
        }
        QTabWidget::pane {
            border: 1px solid #555;
            background-color: #2b2b2b;
        }
        QTabBar::tab {
            background-color: #3c3c3c;
            color: white;
            padding: 8px 16px;
            margin-right: 2px;
            border-radius: 6px 6px 0 0;
        }
        QTabBar::tab:selected {
            background-color: #0078d4;
        }
        QCheckBox, QSpinBox, QLabel {
            color: white;
        }
        QSpinBox {
            background-color: #1e1e1e;
            border: 1px solid #555;
            border-radius: 4px;
            padding: 4px;
        }
    """)
    
    monitor = SystemMonitorGUI()
    monitor.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
