"""
Chat Display Widget for JARVIS
Scrollable area with message bubbles
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLabel
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from .chat_bubble import ChatBubble


class ChatWidget(QWidget):
    """Main chat display area"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.messages = []
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI layout"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #121212;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #1E1E1E;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #555555;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #777777;
            }
        """)
        
        # Container for messages
        self.message_container = QWidget()
        self.message_layout = QVBoxLayout()
        self.message_layout.setContentsMargins(0, 0, 0, 0)
        self.message_layout.setSpacing(8)
        
        self.message_container.setLayout(self.message_layout)
        self.message_container.setStyleSheet("background-color: #121212;")
        
        scroll_area.setWidget(self.message_container)
        
        layout.addWidget(scroll_area)
        
        self.setLayout(layout)
        self.setStyleSheet("background-color: #121212;")
        self.scroll_area = scroll_area
    
    def add_message(self, text: str, is_user: bool = False):
        """Add a message bubble to the chat"""
        bubble = ChatBubble(text, is_user)
        self.message_layout.addWidget(bubble)
        self.messages.append((text, is_user))
        
        # Auto-scroll to bottom
        self.scroll_to_bottom()
    
    def add_thinking_indicator(self):
        """Show thinking indicator"""
        thinking_label = QLabel("🤖 Thinking...")
        thinking_label.setFont(QFont("Segoe UI", 10))
        thinking_label.setStyleSheet("""
            QLabel {
                color: #888888;
                padding: 10px;
                font-style: italic;
            }
        """)
        self.message_layout.addWidget(thinking_label)
        self.scroll_to_bottom()
        self.thinking_label = thinking_label
    
    def remove_thinking_indicator(self):
        """Remove thinking indicator"""
        if hasattr(self, 'thinking_label'):
            self.message_layout.removeWidget(self.thinking_label)
            self.thinking_label.deleteLater()
    
    def scroll_to_bottom(self):
        """Auto-scroll to latest message"""
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )
    
    def clear_chat(self):
        """Clear all messages"""
        while self.message_layout.count():
            child = self.message_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.messages = []
