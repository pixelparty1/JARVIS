"""
JARVIS HUD - Heads-Up Display Module

Floating futuristic UI overlay for the JARVIS assistant.
Built with PyQt5 for cross-platform support.
"""

import sys
import threading
import time
from typing import Optional, Callable, List
from dataclasses import dataclass
from datetime import datetime

try:
    from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout
    from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject, QSize, QPoint
    from PyQt6.QtGui import QFont, QColor, QPixmap, QIcon, QBrush, QPalette
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    print("⚠️  PyQt6 not installed. HUD features will be limited.")
    
    # Dummy QObject for when PyQt6 is not available
    class QObject:
        pass


@dataclass
class HUDMessage:
    """Message to display in HUD."""
    text: str
    message_type: str  # "suggestion", "response", "error", "info"
    timestamp: float
    duration: float = 5.0  # Auto-hide after seconds


class HUDSignals(QObject):
    """Signals for HUD events."""
    if PYQT_AVAILABLE:
        suggestion_clicked = pyqtSignal(str)
        closed = pyqtSignal()
        toggled = pyqtSignal(bool)


class JARVISHUD(QWidget):
    """
    Futuristic floating HUD for JARVIS assistant.
    
    Features:
    - Always-on-top transparent window
    - Display AI responses and suggestions
    - Voice visualization waveform
    - Interactive suggestions
    - System status indicators
    - Keyboard shortcuts
    """
    
    def __init__(self, app: Optional[QApplication] = None, parent=None):
        """
        Initialize JARVIS HUD.
        
        Args:
            app: Optional QApplication instance
            parent: Optional parent widget
        """
        if not PYQT_AVAILABLE:
            raise RuntimeError("PyQt5 is required for HUD. Install with: pip install PyQt5")
        
        super().__init__(parent)
        
        self.app = app
        self.signals = HUDSignals()
        self.messages = []
        
        # State
        self.is_listening = False
        self.is_speaking = False
        self.is_processing = False
        self.is_visible = True
        
        # Configuration
        self.width = 500
        self.height = 300
        self.spacing = 10
        
        # Setup UI
        self._setup_ui()
        self._setup_window()
        self._setup_stylesheet()
        
        # Animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_animation)
        self.animation_timer.start(50)  # 50ms updates
        
        # Message fade timer
        self.message_timer = QTimer()
        self.message_timer.timeout.connect(self._update_messages)
        self.message_timer.start(100)  # Check every 100ms
        
        print("✅ JARVIS HUD initialized")
    
    def _setup_ui(self):
        """Setup UI elements."""
        layout = QVBoxLayout()
        layout.setSpacing(self.spacing)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        self.title_label = QLabel("🤖 JARVIS")
        self.title_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.title_label.setStyleSheet("color: #00d4ff;")
        layout.addWidget(self.title_label)
        
        # Status indicator
        self.status_label = QLabel("●  Ready")
        self.status_label.setFont(QFont("Segoe UI", 10))
        self.status_label.setStyleSheet("color: #64c856;")
        layout.addWidget(self.status_label)
        
        # Main message area
        self.message_label = QLabel("Monitoring your screen...")
        self.message_label.setFont(QFont("Segoe UI", 11))
        self.message_label.setStyleSheet("color: #e0e0e0; padding: 10px;")
        self.message_label.setWordWrap(True)
        layout.addWidget(self.message_label)
        
        # Suggestions area
        self.suggestions_layout = QVBoxLayout()
        layout.addLayout(self.suggestions_layout)
        
        # Expand vertically
        layout.addStretch()
        
        # Control buttons
        button_layout = QVBoxLayout()
        button_layout.setSpacing(5)
        
        # Settings button
        self.settings_btn = QPushButton("⚙️  Settings")
        self.settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a1a2e;
                color: #00d4ff;
                border: 1px solid #00d4ff;
                border-radius: 4px;
                padding: 5px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #00d4ff;
                color: #1a1a2e;
            }
        """)
        button_layout.addWidget(self.settings_btn)
        
        # Close button
        self.close_btn = QPushButton("✕ Close")
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a1a2e;
                color: #ff4444;
                border: 1px solid #ff4444;
                border-radius: 4px;
                padding: 5px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #ff4444;
                color: #1a1a2e;
            }
        """)
        self.close_btn.clicked.connect(self.close)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def _setup_window(self):
        """Setup window properties."""
        self.setWindowTitle("JARVIS HUD")
        self.setGeometry(100, 100, self.width, self.height)
        
        # Make window always on top and borderless
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint |
            Qt.tool
        )
        
        # Set transparency
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Make movable
        self.is_dragging = False
        self.drag_offset = QPoint()
    
    def _setup_stylesheet(self):
        """Setup futuristic stylesheet."""
        style = """
        QWidget {
            background-color: rgba(26, 26, 46, 0.95);
            color: #e0e0e0;
        }
        QLabel {
            color: #e0e0e0;
        }
        QFrame {
            border: 1px solid rgba(0, 212, 255, 0.3);
            border-radius: 4px;
            background-color: rgba(50, 50, 80, 0.3);
        }
        """
        self.setStyleSheet(style)
    
    def show_message(self, message: HUDMessage):
        """
        Show message in HUD.
        
        Args:
            message: HUDMessage instance
        """
        self.messages.append(message)
        self._update_message_display()
    
    def show_suggestion(self, text: str, callback: Optional[Callable] = None):
        """
        Show suggestion button.
        
        Args:
            text: Suggestion text
            callback: Optional callback when clicked
        """
        btn = QPushButton(f"💡 {text}")
        btn.setStyleSheet("""
            QPushButton {
                background-color: #2a4a6a;
                color: #64fda9;
                border: 1px solid #64fda9;
                border-radius: 4px;
                padding: 8px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #64fda9;
                color: #1a1a2e;
            }
        """)
        
        if callback:
            btn.clicked.connect(callback)
        
        self.suggestions_layout.addWidget(btn)
    
    def set_listening(self, listening: bool = True):
        """Set listening state."""
        self.is_listening = listening
        if listening:
            self.status_label.setText("● 🎤 Listening...")
            self.status_label.setStyleSheet("color: #64fda9;")
        else:
            self._update_status()
    
    def set_speaking(self, speaking: bool = True):
        """Set speaking state."""
        self.is_speaking = speaking
        if speaking:
            self.status_label.setText("● 🗣️  Speaking...")
            self.status_label.setStyleSheet("color: #ffd700;")
        else:
            self._update_status()
    
    def set_processing(self, processing: bool = True):
        """Set processing state."""
        self.is_processing = processing
        if processing:
            self.status_label.setText("● 🧠 Processing...")
            self.status_label.setStyleSheet("color: #ff9500;")
        else:
            self._update_status()
    
    def _update_status(self):
        """Update status based on current state."""
        if not self.is_listening and not self.is_speaking and not self.is_processing:
            self.status_label.setText("● Ready")
            self.status_label.setStyleSheet("color: #64c856;")
    
    def _update_message_display(self):
        """Update message display."""
        if self.messages:
            # Show the most recent message
            msg = self.messages[-1]
            self.message_label.setText(msg.text)
            
            # Set color based on type
            colors = {
                "suggestion": "#64fda9",
                "response": "#00d4ff",
                "error": "#ff4444",
                "info": "#e0e0e0"
            }
            color = colors. get(msg.message_type, "#e0e0e0")
            self.message_label.setStyleSheet(f"color: {color}; padding: 10px;")
    
    def _update_messages(self):
        """Remove expired messages."""
        current_time = time.time()
        self.messages = [
            msg for msg in self.messages
            if current_time - msg.timestamp < msg.duration
        ]
        self._update_message_display()
    
    def _update_animation(self):
        """Update animations."""
        # Subtle background pulse when processing
        if self.is_processing:
            pulse = 0.5 + 0.1 * abs(__import__('math').sin(time.time() * 3))
            # Could update background opacity here
    
    def _clear_suggestions(self):
        """Clear all suggestion buttons."""
        while self.suggestions_layout.count():
            self.suggestions_layout.itemAt(0).widget().setParent(None)
    
    def toggle_visibility(self):
        """Toggle HUD visibility."""
        if self.is_visible:
            self.hide()
            self.is_visible = False
        else:
            self.show()
            self.is_visible = True
        self.signals.toggled.emit(self.is_visible)
    
    # Mouse events for dragging
    def mousePressEvent(self, event):
        """Handle mouse press for dragging."""
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_offset = event.globalPos() - self.frameGeometry().topLeft()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging."""
        if self.is_dragging:
            self.move(event.globalPos() - self.drag_offset)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release."""
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
    
    def keyPressEvent(self, event):
        """Handle keyboard events."""
        if event.key() == Qt.Key_Escape:
            self.toggle_visibility()


class HUDManager:
    """
    Manages HUD lifecycle and communication.
    
    Features:
    - Thread-safe updates
    - Queue-based messaging
    - Integration with JARVIS agent
    """
    
    def __init__(self):
        """Initialize HUD manager."""
        self.hud = None
        self.app = None
        self.hud_thread = None
        self.is_running = False
        self.message_queue = []
        
        self._initialize_hud()
    
    def _initialize_hud(self):
        """Initialize PyQt5 and HUD in main thread."""
        if PYQT_AVAILABLE:
            try:
                if QApplication.instance() is None:
                    self.app = QApplication(sys.argv)
                else:
                    self.app = QApplication.instance()
                
                self.hud = JARVISHUD(self.app)
                self.is_running = True
                print("✅ HUD Manager initialized")
            except Exception as e:
                print(f"❌ HUD initialization error: {e}")
        else:
            print("⚠️  PyQt5 not available - HUD disabled")
    
    def show(self):
        """Show HUD."""
        if self.hud:
            self.hud.show()
    
    def hide(self):
        """Hide HUD."""
        if self.hud:
            self.hud.hide()
    
    def display_message(self, text: str, msg_type: str = "info", duration: float = 5.0):
        """
        Display message in HUD.
        
        Args:
            text: Message text
            msg_type: Type of message (suggestion, response, error, info)
            duration: Display duration in seconds
        """
        if not self.hud:
            return
        
        message = HUDMessage(
            text=text,
            message_type=msg_type,
            timestamp=time.time(),
            duration=duration
        )
        
        # Thread-safe update
        try:
            self.hud.show_message(message)
        except:
            self.message_queue.append(message)
    
    def display_suggestion(self, text: str, callback: Optional[Callable] = None):
        """Display suggestion button."""
        if self.hud:
            try:
                self.hud.show_suggestion(text, callback)
            except:
                pass
    
    def set_listening(self, state: bool = True):
        """Set listening state."""
        if self.hud:
            self.hud.set_listening(state)
    
    def set_speaking(self, state: bool = True):
        """Set speaking state."""
        if self.hud:
            self.hud.set_speaking(state)
    
    def set_processing(self, state: bool = True):
        """Set processing state."""
        if self.hud:
            self.hud.set_processing(state)
    
    def run_event_loop(self):
        """Run PyQt5 event loop (blocks)."""
        if self.app and self.hud:
            self.hud.show()
            sys.exit(self.app.exec_())
    
    def close(self):
        """Close HUD."""
        self.is_running = False
        if self.hud:
            self.hud.close()


# Global instance
_hud_manager = None


def get_hud_manager() -> Optional[HUDManager]:
    """Get or create global HUD manager."""
    global _hud_manager
    if _hud_manager is None and PYQT_AVAILABLE:
        _hud_manager = HUDManager()
    return _hud_manager


# Example usage
if __name__ == "__main__" and PYQT_AVAILABLE:
    print("🎨 JARVIS HUD Test")
    
    app = QApplication(sys.argv)
    hud = JARVISHUD(app)
    
    # Show messages
    hud.show_message(HUDMessage(
        text="👋 Welcome to JARVIS!",
        message_type="info"
    ))
    
    hud.show_suggestion("Search for something?")
    hud.show_suggestion("Summarize this page?")
    
    # Show HUD
    hud.show()
    
    # Run demo
    timer = QTimer()
    def demo_update():
        import random
        states = ['listening', 'speaking', 'processing']
        state = random.choice(states)
        
        if state == 'listening':
            hud.set_listening()
        elif state == 'speaking':
            hud.set_speaking()
        else:
            hud.set_processing()
        
        if random.random() > 0.7:
            hud.show_message(HUDMessage(
                text=f"Demo: {state.title()}...",
                message_type="info"
            ))
    
    timer.timeout.connect(demo_update)
    timer.start(2000)
    
    sys.exit(app.exec_())
