"""
JARVIS UI System Package

Provides futuristic HUD interface, animations, and visualizations.
"""

try:
    from .hud import JARVISHUD, HUDManager, get_hud_manager, PYQT_AVAILABLE
except ImportError:
    PYQT_AVAILABLE = False
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
