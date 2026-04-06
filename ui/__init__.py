"""
JARVIS UI System Package

Provides futuristic HUD interface, animations, visualizations, and desktop chat application.
"""

# Try loading HUD (requires PyQt6)
try:
    from .hud import JARVISHUD, HUDManager, get_hud_manager, PYQT_AVAILABLE
except Exception as e:
    PYQT_AVAILABLE = False

# New chat UI components (requires PyQt5)
try:
    from .main_window import JarvisMainWindow
    from .chat_widget import ChatWidget
    from .chat_bubble import ChatBubble
    from .worker_threads import JarvisWorkerThread, VoiceListenerThread, VoiceOutputThread
except Exception as e:
    pass  # PyQt5 may not be installed
    JARVISHUD = None
    HUDManager = None
    get_hud_manager = None

from .animations import Animator, EasingFunction, Keyframe, Sequence
from .animations import FadeTransition, SlideTransition, ScaleTransition
from .waveform import WaveformVisualizer, CircleWaveform

__all__ = [
    'Animator',
    'EasingFunction',
    'Keyframe',
    'Sequence',
    'FadeTransition',
    'SlideTransition',
    'ScaleTransition',
    'WaveformVisualizer',
    'CircleWaveform',
    'JARVISHU D',
    'HUDManager',
    'get_hud_manager',
    'PYQT_AVAILABLE',
]

__version__ = "1.0.0"
