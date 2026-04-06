"""
JARVIS AI Operating System - Futuristic Desktop UI

A premium, responsive PyQt6 application with modern design
- Frameless window with animations
- Chat-like interface
- Voice interaction
- Live status display
- Features panel
- Dark futuristic theme (Iron Man style)
"""

import sys
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum
import threading
import queue

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel, QScrollArea, QFrame,
    QStackedWidget, QTabWidget, QListWidget, QListWidgetItem, QSplitter
)
from PyQt6.QtCore import (
    Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve,
    QSize, QPoint, QRect, QEvent, QTextStream, QIODevice
)
from PyQt6.QtGui import (
    QFont, QColor, QIcon, QPixmap, QGradient, QPalette, QBrush,
    QLinearGradient, QRadialGradient, QPen, QFontMetrics
)
from PyQt6.QtCore import QTimer as QtTimer


class Status(Enum):
    """JARVIS Status states"""
    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    EXECUTING = "executing"
    SPEAKING = "speaking"


@dataclass
class Message:
    """Chat message model"""
    sender: str  # "user" or "jarvis"
    text: str
    timestamp: datetime


class SignalBridge(threading.Thread):
    """Bridge between UI signals and orchestrator"""
    
    def __init__(self, orchestrator=None):
        super().__init__(daemon=True)
        self.orchestrator = orchestrator
        self.queue = queue.Queue()
        self.running = True
    
    def run(self):
        """Process queued tasks"""
        while self.running:
            try:
                task = self.queue.get(timeout=0.1)
                if task:
                    asyncio.run(self._process(task))
            except queue.Empty:
                pass
    
    async def _process(self, task):
        """Process orchestrator task"""
        if self.orchestrator and hasattr(self.orchestrator, 'process_input'):
            await self.orchestrator.process_input(*task)


class ChatBubble(QFrame):
    """Custom chat message bubble widget"""
    
    def __init__(self, message: Message, parent=None):
        super().__init__(parent)
        self.message = message
        self.is_user = message.sender == "user"
        
        self.setObjectName("chatBubble")
        if self.is_user:
            self.setProperty("userMessage", True)
        else:
            self.setProperty("jarvisMessage", True)
        
        layout = QVBoxLayout()
        
        # Timestamp
        time_label = QLabel(message.timestamp.strftime("%H:%M:%S"))
        time_label.setObjectName("messageTime")
        
        # Message text
        text_label = QLabel(message.text)
        text_label.setWordWrap(True)
        text_label.setObjectName("messageText")
        
        layout.addWidget(time_label)
        layout.addWidget(text_label)
        layout.setContentsMargins(15, 10, 15, 10)
        
        self.setLayout(layout)
        self.setCursor(Qt.CursorShape.Default)


class ChatPanel(QWidget):
    """Main chat interface"""
    
    message_submitted = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.messages: list[Message] = []
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Chat history scroll area
        scroll = QScrollArea()
        scroll.setObjectName("chatScroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setSpacing(10)
        self.chat_layout.addStretch()
        
        scroll.setWidget(self.chat_container)
        layout.addWidget(scroll, 1)
        
        # Input area
        input_frame = QFrame()
        input_frame.setObjectName("inputFrame")
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(15, 15, 15, 15)
        input_layout.setSpacing(10)
        
        # Text input
        self.input_field = QLineEdit()
        self.input_field.setObjectName("chatInput")
        self.input_field.setPlaceholderText("Type a command or question...")
        self.input_field.returnPressed.connect(self._on_send)
        self.input_field.setMinimumHeight(45)
        
        # Send button
        self.send_button = QPushButton("Send")
        self.send_button.setObjectName("sendButton")
        self.send_button.clicked.connect(self._on_send)
        self.send_button.setMaximumWidth(100)
        self.send_button.setMinimumHeight(45)
        
        # Voice button
        self.voice_button = QPushButton("🎤")
        self.voice_button.setObjectName("voiceButton")
        self.voice_button.setMaximumWidth(50)
        self.voice_button.setMinimumHeight(45)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.voice_button)
        input_layout.addWidget(self.send_button)
        
        layout.addWidget(input_frame)
        
        self.setLayout(layout)
    
    def add_message(self, text: str, sender: str = "user"):
        """Add message to chat"""
        msg = Message(sender=sender, text=text, timestamp=datetime.now())
        self.messages.append(msg)
        
        bubble = ChatBubble(msg)
        
        # Right-align user messages, left-align JARVIS
        bubble_layout = QHBoxLayout()
        if sender == "user":
            bubble_layout.addStretch()
        bubble_layout.addWidget(bubble, 0 if sender == "jarvis" else 1)
        if sender == "jarvis":
            bubble_layout.addStretch()
        
        container = QWidget()
        container.setLayout(bubble_layout)
        
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, container)
    
    def _on_send(self):
        """Handle message send"""
        text = self.input_field.text().strip()
        if text:
            self.add_message(text, sender="user")
            self.message_submitted.emit(text)
            self.input_field.clear()


class StatusBar(QFrame):
    """Top status bar with system info"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("statusBar")
        self.setMaximumHeight(60)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(20)
        
        # Time
        self.time_label = QLabel()
        self.time_label.setObjectName("statusText")
        layout.addWidget(self.time_label)
        
        # Mode indicator
        self.mode_label = QLabel("🟢 Ready")
        self.mode_label.setObjectName("statusText")
        layout.addWidget(self.mode_label)
        
        layout.addStretch()
        
        # CPU/Memory
        self.system_label = QLabel()
        self.system_label.setObjectName("statusText")
        layout.addWidget(self.system_label)
        
        # Status animation
        self.status_indicator = QLabel("●")
        self.status_indicator.setObjectName("statusIndicator")
        layout.addWidget(self.status_indicator)
        
        self.setLayout(layout)
        
        # Update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_time)
        self.timer.start(1000)
    
    def _update_time(self):
        """Update time display"""
        self.time_label.setText(datetime.now().strftime("%H:%M:%S"))
    
    def set_status(self, status: Status):
        """Set status and animate indicator"""
        text_map = {
            Status.IDLE: "🟢 Ready",
            Status.LISTENING: "🔵 Listening...",
            Status.THINKING: "🟡 Thinking...",
            Status.EXECUTING: "🟠 Executing...",
            Status.SPEAKING: "🔴 Speaking...",
        }
        
        self.mode_label.setText(text_map.get(status, "Ready"))
        self.mode_label.setProperty("status", status.value)
        self.mode_label.style().polish(self.mode_label)


class FeaturesPanel(QWidget):
    """Side panel with tasks, notes, memory, logs"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("featuresPanel")
        self.setMaximumWidth(300)
        self.setMinimumWidth(250)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setObjectName("featuresTabs")
        
        # Tasks tab
        self.tasks_list = QListWidget()
        self.tasks_list.setObjectName("tasksList")
        self.tabs.addTab(self.tasks_list, "📋 Tasks")
        
        # Notes tab
        self.notes_list = QListWidget()
        self.notes_list.setObjectName("notesList")
        self.tabs.addTab(self.notes_list, "📝 Notes")
        
        # Memory tab
        self.memory_list = QListWidget()
        self.memory_list.setObjectName("memoryList")
        self.tabs.addTab(self.memory_list, "🧠 Memory")
        
        # Logs tab
        self.logs_text = QTextEdit()
        self.logs_text.setObjectName("logsText")
        self.logs_text.setReadOnly(True)
        self.tabs.addTab(self.logs_text, "📋 Logs")
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
    
    def add_task(self, task: str):
        """Add task to list"""
        item = QListWidgetItem(task)
        self.tasks_list.addItem(item)
    
    def add_note(self, note: str):
        """Add note to list"""
        item = QListWidgetItem(note)
        self.notes_list.addItem(item)
    
    def add_memory(self, memory: str):
        """Add memory entry"""
        item = QListWidgetItem(memory)
        self.memory_list.addItem(item)
    
    def add_log(self, log: str):
        """Add log entry"""
        self.logs_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] {log}")


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, orchestrator=None, parent=None):
        super().__init__(parent)
        self.orchestrator = orchestrator
        self.signal_bridge = SignalBridge(orchestrator)
        self.signal_bridge.start()
        
        self.setWindowTitle("JARVIS AI Operating System")
        self.setGeometry(100, 100, 1400, 900)
        
        # Frameless window
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        
        # Main widget
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Status bar
        self.status_bar_widget = StatusBar()
        main_layout.addWidget(self.status_bar_widget)
        
        # Content area with splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Chat area
        self.chat_panel = ChatPanel()
        self.chat_panel.message_submitted.connect(self._on_user_input)
        splitter.addWidget(self.chat_panel)
        
        # Features panel
        self.features_panel = FeaturesPanel()
        splitter.addWidget(self.features_panel)
        
        splitter.setCollapsible(1, True)
        splitter.setSizes([900, 300])
        
        main_layout.addWidget(splitter, 1)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Apply stylesheet
        self._apply_stylesheet()
        
        # Status animation timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._animate_status)
        self.current_status = Status.IDLE
    
    def _apply_stylesheet(self):
        """Apply futuristic dark theme"""
        stylesheet = """
        QMainWindow {
            background-color: #0a0e27;
            color: #e0e0e0;
        }
        
        #statusBar {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #1a1f3a, stop:1 #0a0e27);
            border-bottom: 2px solid #00d9ff;
        }
        
        #statusText {
            color: #00d9ff;
            font-weight: bold;
            font-size: 11pt;
            margin: 0px;
        }
        
        #statusIndicator {
            color: #00ff88;
            font-size: 16pt;
            animation: pulse 1s infinite;
        }
        
        /* Chat Interface */
        #chatScroll {
            background-color: #0a0e27;
            border: none;
        }
        
        #chatScroll::ScrollBar:vertical {
            background-color: transparent;
            width: 8px;
        }
        
        #chatScroll::ScrollBar:vertical::handle {
            background-color: #00d9ff;
            border-radius: 4px;
        }
        
        #chatBubble {
            border-radius: 12px;
            margin: 5px;
            padding: 0px;
        }
        
        #chatBubble[userMessage="true"] {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #0066ff, stop:1 #0044cc);
            border: 1px solid #0088ff;
        }
        
        #chatBubble[jarvisMessage="true"] {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #1a1f3a, stop:1 #0a0e27);
            border: 1px solid #00d9ff;
        }
        
        #messageText {
            color: #e0e0e0;
            font-size: 10pt;
            background: transparent;
            border: none;
        }
        
        #messageTime {
            color: #00d9ff;
            font-size: 8pt;
            background: transparent;
            border: none;
        }
        
        /* Input Frame */
        #inputFrame {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #1a1f3a, stop:1 #0a0e27);
            border-top: 2px solid #00d9ff;
        }
        
        #chatInput {
            background-color: #1a1f3a;
            border: 2px solid #00d9ff;
            border-radius: 8px;
            color: #e0e0e0;
            padding: 8px 12px;
            font-size: 10pt;
            selection-background-color: #0066ff;
        }
        
        #chatInput:focus {
            border: 2px solid #00ff88;
            background-color: #242a45;
        }
        
        #chatInput::placeholder {
            color: #606070;
        }
        
        /* Buttons */
        #sendButton, #voiceButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #0066ff, stop:1 #0044cc);
            border: 1px solid #0088ff;
            border-radius: 6px;
            color: #e0e0e0;
            font-weight: bold;
            font-size: 10pt;
        }
        
        #sendButton:hover, #voiceButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #0088ff, stop:1 #0066ff);
            border: 1px solid #00d9ff;
        }
        
        #sendButton:pressed, #voiceButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #0044cc, stop:1 #003399);
        }
        
        /* Features Panel */
        #featuresPanel {
            background-color: #0a0e27;
            border-left: 2px solid #00d9ff;
        }
        
        #featuresTabs {
            background-color: #0a0e27;
        }
        
        #featuresTabs::pane {
            border: 1px solid #00d9ff;
        }
        
        #featuresTabs::tab-bar {
            background-color: #1a1f3a;
        }
        
        QTabBar::tab {
            background-color: #1a1f3a;
            color: #00d9ff;
            padding: 8px 20px;
            border: 1px solid #00d9ff;
            border-radius: 4px;
            margin-right: 2px;
        }
        
        QTabBar::tab:selected {
            background-color: #0066ff;
            border: 1px solid #00ff88;
            color: #fff;
        }
        
        #tasksList, #notesList, #memoryList {
            background-color: #1a1f3a;
            border: 1px solid #00d9ff;
            color: #e0e0e0;
        }
        
        #tasksList::item:hover, #notesList::item:hover, #memoryList::item:hover {
            background-color: #0066ff;
        }
        
        #tasksList::item:selected, #notesList::item:selected, #memoryList::item:selected {
            background-color: #0088ff;
            border: 1px solid #00ff88;
        }
        
        #logsText {
            background-color: #1a1f3a;
            border: 1px solid #00d9ff;
            color: #00ff88;
            font-family: Courier New;
            font-size: 9pt;
        }
        
        /* Splitter */
        QSplitter::handle {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #00d9ff, stop:0.5 #00ff88, stop:1 #00d9ff);
            width: 3px;
        }
        """
        
        self.setStyleSheet(stylesheet)
    
    def _on_user_input(self, text: str):
        """Handle user input"""
        self.features_panel.add_log(f"User: {text}")
        self.set_status(Status.THINKING)
        
        if self.orchestrator:
            from ai_os import InputType
            # Queue task for orchestrator
            self.signal_bridge.queue.put((InputType.TEXT, text))
        
        # Simulate JARVIS response
        QTimer.singleShot(1000, lambda: self._add_jarvis_response())
    
    def _add_jarvis_response(self):
        """Add JARVIS response"""
        self.set_status(Status.IDLE)
        self.chat_panel.add_message(
            "Processing your request. I've analyzed the context and I'm working on the best approach.",
            sender="jarvis"
        )
        self.features_panel.add_log("JARVIS: Response generated")
    
    def _animate_status(self):
        """Animate status indicator"""
        pass
    
    def set_status(self, status: Status):
        """Set system status"""
        self.current_status = status
        self.status_bar_widget.set_status(status)
    
    def add_message(self, text: str, sender: str = "user"):
        """Add message from backend"""
        self.chat_panel.add_message(text, sender)
    
    def set_system_status(self, cpu: float, memory: float):
        """Update system metrics"""
        self.status_bar_widget.system_label.setText(
            f"CPU: {cpu:.1f}% | Memory: {memory:.1f}%"
        )
    
    def add_task_ui(self, task: str):
        """Add task to UI"""
        self.features_panel.add_task(task)
    
    def add_log(self, log: str):
        """Add log entry"""
        self.features_panel.add_log(log)
    
    def closeEvent(self, event):
        """Handle window close"""
        self.signal_bridge.running = False
        event.accept()


def create_app(orchestrator=None):
    """Create and configure application"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create main window
    window = MainWindow(orchestrator)
    window.show()
    
    return app, window


if __name__ == "__main__":
    app, window = create_app()
    sys.exit(app.exec())
