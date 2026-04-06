"""
JARVIS Configuration Module
Centralized configuration for all JARVIS components
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================
# API CONFIGURATION
# ============================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

# ============================================
# VOICE CONFIGURATION
# ============================================
WAKE_WORD = "jarvis"
SPEECH_RECOGNITION_TIMEOUT = 10  # seconds
SPEECH_RECOGNITION_PHRASE_TIME_LIMIT = 30
VOICE_ENGINE = "pyttsx3"  # Options: pyttsx3, edge-tts
VOICE_RATE = 150  # Words per minute for pyttsx3
VOICE_VOLUME = 1.0  # 0.0 to 1.0

# ============================================
# AI BEHAVIOR
# ============================================
SYSTEM_PROMPT = """You are JARVIS, an advanced AI assistant. You are calm, precise, intelligent, and slightly witty. 
You respond concisely but helpfully. You can control the system, manage tasks, and assist the user intelligently.
Keep responses brief (1-3 sentences max unless detailed information is requested).
Be professional but with subtle humor when appropriate."""

CONVERSATION_HISTORY_LIMIT = 10
TEMPERATURE = 0.7
MAX_TOKENS = 2048
TOP_P = 1.0

# ============================================
# MEMORY CONFIGURATION
# ============================================
MEMORY_DB_TYPE = "json"  # Options: json, sqlite
MEMORY_FILE = "jarvis_memory.json"
LOG_FILE = "jarvis_log.txt"
CLIPBOARD_HISTORY_FILE = "clipboard_history.json"
MAX_CLIPBOARD_ENTRIES = 50

# ============================================
# TASK CONFIGURATION
# ============================================
TASKS_FILE = "tasks.json"
NOTES_FILE = "notes.json"

# ============================================
# SYSTEM CONTROL
# ============================================
COMMON_APP_PATHS = {
    "chrome": [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ],
    "firefox": [
        r"C:\Program Files\Mozilla Firefox\firefox.exe",
        r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
    ],
    "notepad": [r"C:\Windows\System32\notepad.exe"],
    "calculator": [r"C:\Windows\System32\calc.exe"],
    "vscode": [
        r"C:\Users\{user}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    ],
    "spotify": [r"C:\Users\{user}\AppData\Roaming\Spotify\Spotify.exe"],
}

# ============================================
# LOGGING
# ============================================
ENABLE_LOGGING = True
LOG_LEVEL = "INFO"

# ============================================
# WEB SEARCH
# ============================================
WEB_SEARCH_TIMEOUT = 10  # seconds
WEB_SEARCH_RESULTS_COUNT = 5

# ============================================
# SAFETY & PERMISSIONS
# ============================================
CONFIRMATION_REQUIRED_FOR = [
    "delete_file",
    "uninstall_app",
    "modify_system",
    "shutdown",
    "restart"
]

DISABLE_CONFIRMATION_FOR = [
    "open_app",
    "play_music",
    "pause_music",
    "volume_control",
    "get_weather",
    "tell_time",
    "add_note",
    "read_note",
]

# ============================================
# DEBUG MODE
# ============================================
DEBUG = False
PRINT_STREAM = True  # Print streaming responses in real-time

# ============================================
# GREETING RESPONSES
# ============================================
GREETING_RESPONSES = [
    "Yes, I'm here.",
    "I'm ready to assist.",
    "How can I help?",
    "At your service.",
    "Present and accounted for.",
]

# ============================================
# WAKE WORD & VOICE SETTINGS
# ============================================
WAKE_WORD_TIMEOUT = 60  # seconds to listen after wake word
ENABLE_VOICE = False  # Set to True to enable voice (requires microphone setup)
DEBUG_MODE = False  # Enable debug logging

# ============================================
# SYSTEM VALIDATION
# ============================================
def validate_config():
    """Validate configuration on startup"""
    if DEBUG:
        print("✅ Configuration validated")
    return True
