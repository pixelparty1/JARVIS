"""
JARVIS Multi-Modal Vision System - Comprehensive Demo

Demonstrates all features of the vision and HUD system.
"""

import time
import sys
from typing import Optional


def demo_screen_capture():
    """Demo: Screen capture capabilities."""
    print("\n" + "="*60)
    print("🎥 DEMO 1: Screen Capture")
    print("="*60)
    
    from vision.screen_capture import ScreenCapture
    
    capture = ScreenCapture(cache_dir="screenshots")
    
    print("\n📊 Monitor Configuration:")
    info = capture.get_capture_info()
    print(f"   Connected monitors: {info['monitor_count']}")
    for monitor in info['monitors']:
        print(f"   - Monitor {monitor['index']}: {monitor['width']}x{monitor['height']}")
    
    print("\n📸 Capturing full screen...")
    screenshot = capture.capture_full_screen(resize=(800, 600))
    if screenshot is not None:
        print(f"   ✅ Screenshot captured: {screenshot.shape} pixels")
        
        print("\n💾 Saving screenshot...")
        path = capture.save_screenshot()
        print(f"   ✅ Saved to: {path}")
    else:
        print("   ❌ Failed to capture")
    
    print("\n📊 Cache Status:")
    print(f"   Cached images: {len(capture.cache)}")
    print(f"   Caching enabled: {capture.enable_caching}")
    print(f"   Min capture interval: {capture.min_capture_interval}s")


def demo_ocr():
    """Demo: OCR text extraction."""
    print("\n" + "="*60)
    print("🔍 DEMO 2: OCR Text Extraction")
    print("="*60)
    
    from vision.screen_capture import ScreenCapture
    from vision.ocr import OCREngine
    
    # Capture
    print("\n📸 Capturing screen for OCR...")
    capture = ScreenCapture()
    screenshot = capture.capture_full_screen(resize=(800, 600))
    
    if screenshot is None:
        print("❌ Could not capture screen")
        return
    
    # Initialize OCR
    print("🔤 Initializing OCR engine...")
    ocr = OCREngine()
    
    # Extract text
    print("\n📝 Extracting text...")
    text = ocr.extract_text(screenshot)
    if text:
        print(f"   ✅ Extracted {len(text)} characters")
        print(f"   Preview: {text[:100]}...")
    else:
        print("   ⚠️  No text found (or OCR not configured)")
    
    # Extract structured data
    print("\n🔗 Extracting URLs...")
    urls = ocr.extract_urls(screenshot)
    if urls:
        for url in urls[:3]:
            print(f"   - {url}")
    else:
        print("   (No URLs found)")
    
    print("\n📧 Extracting emails...")
    emails = ocr.extract_emails(screenshot)
    if emails:
        for email in emails[:3]:
            print(f"   - {email}")
    else:
        print("   (No emails found)")
    
    print("\n🔢 Extracting numbers...")
    numbers = ocr.extract_numbers(screenshot)
    if numbers:
        print(f"   Found {len(numbers)} numbers: {', '.join(numbers[:5])}...")
    else:
        print("   (No numbers found)")
    
    print("\n📊 OCR Settings:")
    print(f"   Languages: {ocr.languages}")
    print(f"   Confidence threshold: {ocr.confidence_threshold}")
    print(f"   Preprocessing: {ocr.preprocessing_enabled}")


def demo_vision_analyzer():
    """Demo: Vision analyzer and activity detection."""
    print("\n" + "="*60)
    print("🧠 DEMO 3: Vision Analysis & Activity Detection")
    print("="*60)
    
    from vision.vision_analyzer import VisionAnalyzer
    
    analyzer = VisionAnalyzer()
    
    # Test samples
    samples = [
        ("def fibonacci(n):\n    return n if n <= 1 else fib(n-1)+fib(n-2)", "VS Code"),
        ("Python is a great language for data science", "Browser - Article"),
        ("Traceback (most recent call last):\n  File main.py line 42", "Terminal"),
        ("Watch this amazing video", "YouTube"),
    ]
    
    print("\n📊 Analyzing different screen contents:\n")
    
    for text, window_name in samples:
        print(f"Window: {window_name}")
        print(f"Content: {text[:40]}...")
        
        analysis = analyzer.analyze(text, window_name)
        
        if analysis:
            print(f"  Activity: {analysis.activity}")
            print(f"  Context: {analysis.context}")
            print(f"  Confidence: {analysis.confidence:.2f}")
            print(f"  Suggestions: {analysis.suggestions[:2]}")
        print()
    
    # Activity summary
    print("📈 Activity Summary:")
    summary = analyzer.get_activity_summary()
    if summary['total_activities'] > 0:
        print(f"   Total activities: {summary['total_activities']}")
        print(f"   Activity types: {summary['activity_types']}")
        pattern = analyzer.get_activity_pattern()
        if pattern:
            print(f"   Pattern: {pattern}")


def demo_animations():
    """Demo: Animation system."""
    print("\n" + "="*60)
    print("🎬 DEMO 4: Animation System")
    print("="*60)
    
    from ui.animations import Animator, EasingFunction, FadeTransition, SlideTransition
    
    print("\n📊 Testing different easing functions:")
    
    animator = Animator()
    
    # Create animations with different easing
    anims = {
        'Linear': animator.animate(0, 100, 1.0, EasingFunction.LINEAR),
        'Ease In': animator.animate(0, 100, 1.0, EasingFunction.EASE_IN),
        'Ease Out': animator.animate(0, 100, 1.0, EasingFunction.EASE_OUT),
        'Ease In Out': animator.animate(0, 100, 1.0, EasingFunction.EASE_IN_OUT),
        'Smooth': animator.animate(0, 100, 1.0, EasingFunction.SMOOTH),
    }
    
    print("\n Progress | Linear | EaseIn | EaseOut | EaseInOut | Smooth")
    print("-" * 70)
    
    for i in range(11):
        animator.update(0.1)
        
        progress = f"{i*10}%".rjust(8)
        values = [f"{animator.get_value(anim_id):.1f}" for anim_id in anims.values()]
        
        print(f" {progress} | " + " | ".join(f"{v:>6}" for v in values))
    
    print("\n🔄 Fade Transition:")
    fade = FadeTransition(duration=1.0)
    print("   ", end="")
    for i in range(5):
        fade.update(0.2)
        opacity = fade.get_opacity()
        bar_len = int(opacity * 20)
        print(f"[{'█'*bar_len}{' '*(20-bar_len)}] ", end="")
    print()
    
    print("\n↔️  Slide Transition:")
    slide = SlideTransition(dx=100, dy=50, duration=1.0)
    print("   ", end="")
    for i in range(5):
        slide.update(0.2)
        offset = slide.get_offset()
        print(f"({offset[0]:>3.0f},{offset[1]:>3.0f}) ", end="")
    print()


def demo_waveform():
    """Demo: Waveform visualization."""
    print("\n" + "="*60)
    print("🌊 DEMO 5: Voice Waveform Visualization")
    print("="*60)
    
    from ui.waveform import WaveformVisualizer, CircleWaveform
    
    print("\n📊 Linear Waveform:")
    waveform = WaveformVisualizer(width=60, height=15, bars=15)
    
    print("\n🎤 Listening State:")
    waveform.set_listening()
    for i in range(3):
        waveform.update(0.1)
        print(waveform.get_ascii_art())
        print()
    
    print("\n🗣️  Speaking State:")
    waveform.set_speaking()
    for i in range(3):
        waveform.update(0.1)
        print(waveform.get_ascii_art())
        print()
    
    print("\n🧠 Processing State:")
    waveform.set_processing()
    for i in range(3):
        waveform.update(0.1)
        print(waveform.get_ascii_art())
        print()
    
    print("\n⭕ Circular Waveform:")
    circle = CircleWaveform(radius=50, segments=12)
    circle.state = "speaking"
    
    # Show state info
    for state in ['idle', 'listening', 'speaking', 'processing']:
        circle.state = state
        circle.update(0.1)
        print(f"\n   State: {state.upper()}")
        print(f"   Color: ", end="")
        colors = {
            'idle': "BLUE",
            'listening': "GREEN",
            'speaking': "ORANGE",
            'processing': "PURPLE"
        }
        print(colors[state])


def demo_hud():
    """Demo: HUD interface."""
    print("\n" + "="*60)
    print("🎨 DEMO 6: HUD Interface")
    print("="*60)
    
    try:
        from ui.hud import get_hud_manager, HUDMessage
        
        print("\n🖼️  Creating HUD...")
        hud_mgr = get_hud_manager()
        
        if hud_mgr and hud_mgr.hud:
            print("   ✅ HUD initialized")
            
            # Show demo messages
            print("\n💬 Displaying demo messages...")
            
            hud_mgr.display_message("👋 Welcome to JARVIS Vision System!", "info", duration=3)
            time.sleep(1)
            
            hud_mgr.display_message("📸 Screen monitoring active", "info")
            time.sleep(1)
            
            hud_mgr.display_suggestion("Summarize this page?")
            hud_mgr.display_suggestion("Extract key points?")
            
            print("   ✅ Messages displayed")
            
            # Test states
            print("\n🎭 Testing AI states...")
            
            print("   Setting: Listening...")
            hud_mgr.set_listening(True)
            time.sleep(1)
            
            print("   Setting: Processing...")
            hud_mgr.set_listening(False)
            hud_mgr.set_processing(True)
            time.sleep(1)
            
            print("   Setting: Speaking...")
            hud_mgr.set_processing(False)
            hud_mgr.set_speaking(True)
            time.sleep(1)
            
            print("   Setting: Ready")
            hud_mgr.set_speaking(False)
            
            print("\n✅ HUD demo complete")
            print("   Leave HUD window open for 5 seconds to see effects...")
            time.sleep(5)
        else:
            print("   ⚠️  HUD not available (PyQt5 may not be installed)")
            
    except Exception as e:
        print(f"   ⚠️  HUD demo error: {e}")


def demo_multimodal():
    """Demo: Multi-modal integration."""
    print("\n" + "="*60)
    print("🎯 DEMO 7: Multi-Modal Integration")
    print("="*60)
    
    from multimodal import MultiModalJARVIS
    
    print("\n🤖 Initializing Multi-Modal JARVIS...")
    
    try:
        mm_jarvis = MultiModalJARVIS(enable_hud=False)  # No HUD for demo
        
        print("✅ Multi-Modal JARVIS initialized")
        
        print("\n📡 Starting screen monitoring (10 seconds)...")
        mm_jarvis.start_monitoring()
        
        # Monitor for a bit
        for i in range(10):
            time.sleep(1)
            if i % 5 == 0:
                context = mm_jarvis.get_context()
                if context:
                    print(f"\n   Current Activity: {context.get('activity', 'unknown')}")
        
        print("\n📊 Activity Summary:")
        summary = mm_jarvis.get_activity_summary()
        print(f"   Total Records: {summary.get('total_records', 0)}")
        print(f"   Activities: {summary.get('activities', {})}")
        
        print("\n💾 Exporting session...")
        mm_jarvis.export_session("demo_session.json")
        
        print("\n🛑 Stopping monitoring...")
        mm_jarvis.close()
        
        print("✅ Multi-Modal demo complete")
        
    except Exception as e:
        print(f"   ⚠️  Error: {e}")
        print("   (This may happen if OCR/dependencies not configured)")


def demo_integration():
    """Demo: Integration with autonomous agent."""
    print("\n" + "="*60)
    print("🔗 DEMO 8: Integration with Agent System")
    print("="*60)
    
    print("\n📝 Code example for integration:")
    print("""
from agent_main import JARVISAgent
from multimodal import MultiModalJARVIS

# Create agent
agent = JARVISAgent()

# Create multi-modal system
mm_jarvis = MultiModalJARVIS(
    agent_system=agent.agent,
    enable_hud=True
)

# Start monitoring
mm_jarvis.start_monitoring()

# Enable auto-execution
mm_jarvis.toggle_auto_execute(True)

# Now when you ask via voice with visual context:
# "Summarize this"
# JARVIS will:
# 1. See what's on screen
# 2. Understand you're reading an article
# 3. Execute: "Summarize the article on screen"
# 4. Show result in HUD

# Stop when done
mm_jarvis.close()
    """)
    
    print("\n✅ Integration demo (code example)")


def run_all_demos():
    """Run all demos."""
    print("\n")
    print("█" * 60)
    print("🎬 JARVIS Multi-Modal Vision System - Complete Demo")
    print("█" * 60)
    
    demos = [
        ("Screen Capture", demo_screen_capture),
        ("OCR Text Extraction", demo_ocr),
        ("Vision Analysis", demo_vision_analyzer),
        ("Animations", demo_animations),
        ("Waveforms", demo_waveform),
        ("HUD Interface", demo_hud),
        ("Multi-Modal", demo_multimodal),
        ("Agent Integration", demo_integration),
    ]
    
    for idx, (name, demo_func) in enumerate(demos):
        try:
            print(f"\n[{idx+1}/{len(demos)}] Running demo: {name}")
            demo_func()
        except Exception as e:
            print(f"\n❌ Demo error: {e}")
            import traceback
            traceback.print_exc()
        
        # Clear any processing state
        time.sleep(0.5)
    
    # Summary
    print("\n" + "█" * 60)
    print("✨ Demo Complete!")
    print("█" * 60)
    print("""
Next Steps:
1. Review the code in vision/ and ui/ directories
2. Read MULTIMODAL_SETUP.md for detailed documentation
3. Try the integration demo with actual agent system
4. Customize vision analysis for your needs
5. Extend with custom analyzers and UI modifications

Key Files:
- multimodal.py              - Main integration
- vision/screen_capture.py   - Screenshot system
- vision/ocr.py              - Text extraction
- vision/vision_analyzer.py  - AI analysis
- ui/hud.py                  - Floating UI
- ui/animations.py           - Smooth transitions
- ui/waveform.py             - Voice visualization

Ready for production use! 🚀
    """)


if __name__ == "__main__":
    try:
        run_all_demos()
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
