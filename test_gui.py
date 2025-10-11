#!/usr/bin/env python3
"""
Quick test to see if PyQt6 is available and basic GUI works
"""

try:
    from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget
    from PyQt6.QtCore import Qt
    import sys
    
    print("✅ PyQt6 imported successfully!")
    
    class TestWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("🧪 GUI Test")
            self.setGeometry(300, 300, 400, 200)
            
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            layout = QVBoxLayout(central_widget)
            
            label = QLabel("🛡️ Firewall Generator GUI Test")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)
            
            button = QPushButton("✅ GUI Working!")
            button.clicked.connect(self.on_click)
            layout.addWidget(button)
        
        def on_click(self):
            print("🎉 Button clicked - GUI is working!")
    
    def test_gui():
        app = QApplication(sys.argv)
        window = TestWindow()
        window.show()
        print("🚀 GUI test window created - close window to continue")
        app.exec()
    
    if __name__ == "__main__":
        test_gui()
        
except ImportError as e:
    print(f"❌ PyQt6 not available: {e}")
    print("📦 Install with: pip3 install PyQt6")
except Exception as e:
    print(f"❌ GUI test failed: {e}")
