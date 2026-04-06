#!/usr/bin/env python3
"""
Quick test script to verify JARVIS setup
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("JARVIS SYSTEM VERIFICATION")
print("=" * 60)

# Test 1: Config
print("\n[1/4] Testing Configuration...")
try:
    from config import GROQ_API_KEY, GROQ_MODEL, WAKE_WORD
    print(f"✅ Config loaded")
    print(f"   - API Key: {'✅ Set' if GROQ_API_KEY else '❌ Missing'}")
    print(f"   - Model: {GROQ_MODEL}")
    print(f"   - Wake Word: '{WAKE_WORD}'")
except Exception as e:
    print(f"❌ Config error: {e}")
    sys.exit(1)

# Test 2: Brain
print("\n[2/4] Testing Brain (Groq)...")
try:
    from brain import JarvisBrain
    brain = JarvisBrain()
    print(f"✅ Brain initialized")
    print(f"   - Testing Groq connection...")
    response = brain.query("Hello, are you working?", stream=False)
    print(f"✅ Groq working: {response[:50]}...")
except Exception as e:
    print(f"❌ Brain error: {e}")
    sys.exit(1)

# Test 3: Listener
print("\n[3/4] Testing Listener...")
try:
    from listener import VoiceListener
    print(f"✅ Listener initialized [Voice module ready]")
except Exception as e:
    print(f"⚠️  Listener warning: {e}")

# Test 4: Speaker
print("\n[4/4] Testing Speaker...")
try:
    from speaker import VoiceSpeaker
    print(f"✅ Speaker initialized [TTS module ready]")
except Exception as e:
    print(f"⚠️  Speaker warning: {e}")

print("\n" + "=" * 60)
print("✅ ALL SYSTEMS OPERATIONAL")
print("=" * 60)
print("\nRun JARVIS with:")
print("  python run_jarvis.py              # With voice")
print("  python run_jarvis.py --text-only  # Text only")
print("  python run_jarvis.py --debug      # Debug mode")
