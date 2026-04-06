"""
Main JARVIS Desktop Application Window
Modern chat interface with voice integration
"""

import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QApplication
)
from PyQt5.QtCore import Qt, pyqtSlot, QTimer
from PyQt5.QtGui import QIcon, QFont, QPixmap, QColor
from .chat_widget import ChatWidget
from .worker_threads import JarvisWorkerThread, VoiceListenerThread, VoiceOutputThread


class JarvisMainWindow(QMainWindow):
    """Main JARVIS application window"""
    
    def __init__(self):
        super().__init__()
        self.chat_widget = None
        self.input_field = None
        self.send_button = None
        self.voice_button = None
        self.status_label = None
        
        # Worker threads
        self.query_thread = None
        self.voice_thread = None
        self.tts_thread = None
        
        # State
        self.is_listening = False
        self.listening_timeout = None
        
        self.init_ui()
        self.apply_styles()
    
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("J.A.R.V.I.S - AI Operating System")
        self.setGeometry(100, 100, 900, 700)
        
        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ==================== HEADER ====================
        header_widget = QWidget()
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 15, 20, 15)
        header_layout.setSpacing(10)
        
        title_label = QLabel("J.A.R.V.I.S")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title_label.setStyleSheet("color: #0D47A1;")
        
        self.status_label = QLabel("Ready")
        self.status_label.setFont(QFont("Segoe UI", 10))
        self.status_label.setStyleSheet("color: #999999;")
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.status_label)
        
        header_widget.setLayout(header_layout)
        header_widget.setStyleSheet("background-color: #1E1E1E;")
        
        main_layout.addWidget(header_widget)
        
        # ==================== CHAT AREA ====================
        self.chat_widget = ChatWidget()
        main_layout.addWidget(self.chat_widget, 1)
        
        # ==================== INPUT AREA ====================
        input_widget = QWidget()
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(15, 10, 15, 10)
        input_layout.setSpacing(10)
        
        # Text input
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type a message or press the mic button...")
        self.input_field.setFont(QFont("Segoe UI", 11))
        self.input_field.returnPressed.connect(self.send_message)
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #2C2C2C;
                color: #FFFFFF;
                border: 1px solid #444444;
                border-radius: 6px;
                padding: 10px;
                selection-background-color: #0D47A1;
            }
            QLineEdit:focus {
                border: 2px solid #0D47A1;
            }
        """)
        
        # Voice button
        self.voice_button = QPushButton("🎤")
        self.voice_button.setFont(QFont("Segoe UI", 14))
        self.voice_button.setFixedSize(50, 50)
        self.voice_button.clicked.connect(self.toggle_voice_listening)
        self.voice_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: #FFFFFF;
                border: none;
                border-radius: 25px;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        
        # Send button
        self.send_button = QPushButton("Send")
        self.send_button.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.send_button.setFixedSize(80, 50)
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #0D47A1;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0A3D91;
            }
            QPushButton:pressed {
                background-color: #082555;
            }
        """)
        
        input_layout.addWidget(self.input_field, 1)
        input_layout.addWidget(self.voice_button)
        input_layout.addWidget(self.send_button)
        
        input_widget.setLayout(input_layout)
        input_widget.setStyleSheet("background-color: #1E1E1E;")
        
        main_layout.addWidget(input_widget)
        
        main_widget.setLayout(main_layout)
        main_widget.setStyleSheet("background-color: #121212;")
        
        # Show initial message
        self.chat_widget.add_message("Hello! I'm JARVIS. How can I assist you today?", is_user=False)
    
    def apply_styles(self):
        """Apply global styles"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }
        """)
    
    @pyqtSlot()
    def send_message(self):
        """Handle message sending"""
        message = self.input_field.text().strip()
        
        if not message:
            return
        
        # Add user message to chat
        self.chat_widget.add_message(message, is_user=True)
        self.input_field.clear()
        
        # Update status
        self.update_status("Thinking...")
        self.chat_widget.add_thinking_indicator()
        
        # Start background thread for AI response
        self.query_thread = JarvisWorkerThread(message)
        self.query_thread.response_ready.connect(self.on_response_ready)
        self.query_thread.error_occurred.connect(self.on_error)
        self.query_thread.start()
        
        # Disable input while processing
        self.input_field.setEnabled(False)
        self.send_button.setEnabled(False)
    
    @pyqtSlot(str)
    def on_response_ready(self, response: str):
        """Handle AI response"""
        self.chat_widget.remove_thinking_indicator()
        self.chat_widget.add_message(response, is_user=False)
        
        # Update status
        self.update_status("Ready")
        
        # Re-enable input
        self.input_field.setEnabled(True)
        self.send_button.setEnabled(True)
        self.input_field.setFocus()
        
        # Optional: Play voice response
        # self.play_voice_response(response)
    
    @pyqtSlot(str)
    def on_error(self, error_msg: str):
        """Handle error"""
        self.chat_widget.remove_thinking_indicator()
        self.chat_widget.add_message(f"Error: {error_msg}", is_user=False)
        
        self.update_status("Ready")
        
        # Re-enable input
        self.input_field.setEnabled(True)
        self.send_button.setEnabled(True)
        self.input_field.setFocus()
    
    def toggle_voice_listening(self):
        """Toggle voice listening"""
        if self.is_listening:
            self.stop_voice_listening()
        else:
            self.start_voice_listening()
    
    def start_voice_listening(self):
        """Start listening for voice input"""
        self.is_listening = True
        self.voice_button.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: #FFFFFF;
                border: none;
                border-radius: 25px;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #E68900;
            }
        """)
        self.voice_button.setText("🔴")
        
        self.update_status("Listening...")
        
        # Start voice listener thread
        self.voice_thread = VoiceListenerThread()
        self.voice_thread.speech_recognized.connect(self.on_speech_recognized)
        self.voice_thread.error_occurred.connect(self.on_voice_error)
        self.voice_thread.listening_stopped.connect(self.stop_voice_listening)
        self.voice_thread.start()
        
        # Set timeout (30 seconds)
        self.listening_timeout = QTimer()
        self.listening_timeout.setSingleShot(True)
        self.listening_timeout.timeout.connect(self.stop_voice_listening)
        self.listening_timeout.start(30000)
    
    def stop_voice_listening(self):
        """Stop listening for voice input"""
        self.is_listening = False
        self.voice_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: #FFFFFF;
                border: none;
                border-radius: 25px;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.voice_button.setText("🎤")
        
        self.update_status("Ready")
        
        if self.listening_timeout:
            self.listening_timeout.stop()
    
    @pyqtSlot(str)
    def on_speech_recognized(self, text: str):
        """Handle recognized speech"""
        self.stop_voice_listening()
        self.input_field.setText(text)
        self.input_field.setFocus()
    
    @pyqtSlot(str)
    def on_voice_error(self, error_msg: str):
        """Handle voice error"""
        self.stop_voice_listening()
        self.chat_widget.add_message(f"Voice Error: {error_msg}", is_user=False)
    
    def play_voice_response(self, text: str):
        """Play voice response (optional)"""
        try:
            from config import ENABLE_VOICE
            if not ENABLE_VOICE:
                return
            
            self.tts_thread = VoiceOutputThread(text)
            self.tts_thread.start()
        except Exception as e:
            print(f"TTS Error: {e}")
    
    def update_status(self, status: str):
        """Update status label"""
        self.status_label.setText(status)
    
    def closeEvent(self, event):
        """Handle window close"""
        # Cleanup threads
        if self.query_thread and self.query_thread.isRunning():
            self.query_thread.quit()
            self.query_thread.wait()
        
        if self.voice_thread and self.voice_thread.isRunning():
            self.voice_thread.quit()
            self.voice_thread.wait()
        
        if self.tts_thread and self.tts_thread.isRunning():
            self.tts_thread.quit()
            self.tts_thread.wait()
        
        event.accept()


def main():
    """Main entry point for GUI"""
    app = QApplication(sys.argv)
    window = JarvisMainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
