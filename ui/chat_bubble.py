"""
Chat Bubble Widget for JARVIS UI
Displays messages as bubbles (user right, JARVIS left)
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPalette, QColor
from datetime import datetime


class ChatBubble(QWidget):
    """Single chat message bubble"""
    
    def __init__(self, message: str, is_user: bool = False, parent=None):
        super().__init__(parent)
        self.message = message
        self.is_user = is_user
        self.timestamp = datetime.now().strftime("%H:%M")
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI layout"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        # Message text
        message_label = QLabel(self.message)
        message_label.setWordWrap(True)
        message_label.setFont(QFont("Segoe UI", 10))
        
        # Timestamp (optional)
        timestamp_label = QLabel(self.timestamp)
        timestamp_label.setFont(QFont("Segoe UI", 8))
        timestamp_label.setAlignment(Qt.AlignRight if self.is_user else Qt.AlignLeft)
        
        layout.addWidget(message_label)
        layout.addWidget(timestamp_label)
        
        # Apply styling
        if self.is_user:
            # User message - right side, blue
            message_label.setStyleSheet("""
                QLabel {
                    background-color: #0D47A1;
                    color: #FFFFFF;
                    padding: 10px 12px;
                    border-radius: 12px;
                    margin: 4px 0px;
                }
            """)
            timestamp_label.setStyleSheet("""
                QLabel {
                    color: #999999;
                    padding: 0px 4px;
                }
            """)
            layout.setAlignment(Qt.AlignRight)
        else:
            # JARVIS message - left side, dark gray
            message_label.setStyleSheet("""
                QLabel {
                    background-color: #2C2C2C;
                    color: #FFFFFF;
                    padding: 10px 12px;
                    border-radius: 12px;
                    margin: 4px 0px;
                }
            """)
            timestamp_label.setStyleSheet("""
                QLabel {
                    color: #999999;
                    padding: 0px 4px;
                }
            """)
            layout.setAlignment(Qt.AlignLeft)
        
        self.setLayout(layout)
    
    def sizeHint(self):
        """Suggest size"""
        return QSize(400, 60)
