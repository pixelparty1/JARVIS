"""
Multi-Modal JARVIS Integration Module

Integrates vision capabilities, HUD, and autonomous agent into one cohesive system.
"""

import threading
import time
from typing import Optional, Dict, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class MultiModalContext:
    """Current multi-modal context."""
    screen_activity: str
    screen_context: str
    suggestions: List[str]
    last_update: float
    confidence: float


class MultiModalJARVIS:
    """
    Multi-modal JARVIS assistant with screen understanding and HUD.
    
    Integrates:
    - Screen capture and analysis
    - OCR text extraction
    - Vision-based understanding
    - Floating HUD interface
    - Autonomous agent system
    
    Features:
    - Real-time screen understanding
    - Context-aware suggestions
    - Proactive assistance
    - Always-on-top UI
    - Seamless agent integration
    """
    
    def __init__(self, agent_system=None, enable_hud: bool = True):
        """
        Initialize Multi-Modal JARVIS.
        
        Args:
            agent_system: Optional AgentLoop instance
            enable_hud: Whether to enable HUD display
        """
        self.agent_system = agent_system
        self.enable_hud = enable_hud
        
        # Import vision modules
        from vision.screen_capture import get_screen_capture
        from vision.ocr import get_ocr_engine
        from vision.vision_analyzer import get_vision_analyzer
        
        # Initialize vision components
        self.screen_capture = get_screen_capture()
        self.ocr_engine = get_ocr_engine()
        self.vision_analyzer = get_vision_analyzer(
            brain=agent_system.agent.planner.brain if agent_system else None
        )
        
        # Initialize HUD if enabled
        if enable_hud:
            try:
                from ui.hud import get_hud_manager
                self.hud_manager = get_hud_manager()
                self.hud_manager.show()
            except Exception as e:
                print(f"⚠️  HUD initialization failed: {e}")
                self.hud_manager = None
        else:
            self.hud_manager = None
        
        # Settings
        self.analysis_interval = 3.0  # Analyze screen every 3 seconds
        self.enable_ocr = True
        self.enable_suggestions = True
        self.auto_execute = False  # Auto-execute suggestions
        
        # State
        self.is_running = False
        self.monitoring_thread = None
        self.current_context: Optional[MultiModalContext] = None
        self.last_analysis_time = 0
        
        # History
        self.activity_history = []
        self.max_history = 100
        
        print("✅ Multi-Modal JARVIS initialized")
    
    def start_monitoring(self):
        """Start screen monitoring in background thread."""
        if self.is_running:
            print("⚠️  Monitoring already running")
            return
        
        self.is_running = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        print("📡 Screen monitoring started")
    
    def stop_monitoring(self):
        """Stop screen monitoring."""
        self.is_running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        print("🛑 Screen monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.is_running:
            try:
                # Check if it's time to analyze
                current_time = time.time()
                if current_time - self.last_analysis_time >= self.analysis_interval:
                    self._analyze_screen()
                    self.last_analysis_time = current_time
                
                time.sleep(0.5)  # Prevent CPU spinning
                
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                time.sleep(1)
    
    def _analyze_screen(self):
        """Analyze current screen content."""
        try:
            # Capture screen
            if not self.screen_capture.should_capture_now():
                return
            
            screenshot = self.screen_capture.capture_full_screen(resize=(800, 600))
            if screenshot is None:
                return
            
            # Extract text with OCR
            text = ""
            if self.enable_ocr:
                text = self.ocr_engine.extract_text(screenshot)
            
            # Skip if not enough text
            if len(text.strip()) < 20:
                return
            
            # Analyze with vision system
            analysis = self.vision_analyzer.analyze(
                text,
                "Active Window"
            )
            
            if analysis:
                self._process_analysis(analysis)
            
        except Exception as e:
            print(f"⚠️  Screen analysis error: {e}")
    
    def _process_analysis(self, analysis):
        """Process vision analysis results."""
        # Store in context
        self.current_context = MultiModalContext(
            screen_activity=analysis.activity,
            screen_context=analysis.context,
            suggestions=analysis.suggestions,
            last_update=time.time(),
            confidence=analysis.confidence
        )
        
        # Store in history
        self.activity_history.append({
            'activity': analysis.activity,
            'timestamp': self.current_context.last_update,
            'suggestions': analysis.suggestions
        })
        
        # Keep history size manageable
        if len(self.activity_history) > self.max_history:
            self.activity_history = self.activity_history[-self.max_history:]
        
        # Update HUD
        if self.hud_manager:
            try:
                self._update_hud(analysis)
            except:
                pass
        
        # Auto-execute if enabled
        if self.auto_execute and self.agent_system:
            self._maybe_execute_suggestion(analysis)
    
    def _update_hud(self, analysis):
        """Update HUD with analysis results."""
        # Show activity
        hud_text = f"📊 {analysis.activity.title()}\n{analysis.context}"
        self.hud_manager.display_message(hud_text, "info", duration=self.analysis_interval)
        
        # Show suggestions
        if self.enable_suggestions and analysis.suggestions:
            # Clear old suggestions
            # Note: Would need to implement this in HUD
            
            for suggestion in analysis.suggestions[:2]:  # Show top 2
                def make_callback(sugg):
                    def callback():
                        self._execute_suggestion(sugg)
                    return callback
                
                self.hud_manager.display_suggestion(
                    suggestion[:50],  # Truncate long suggestions
                    make_callback(suggestion)
                )
    
    def _maybe_execute_suggestion(self, analysis):
        """Possibly auto-execute a suggestion."""
        # Simple heuristic: auto-execute summarization for reading
        if "summarize" in ', '.join(analysis.suggestions).lower():
            if analysis.activity == "reading":
                self._execute_suggestion("Summarize this page")
    
    def _execute_suggestion(self, suggestion: str):
        """Execute a suggestion using agent system."""
        if not self.agent_system:
            print("❌ Agent system not available")
            return
        
        try:
            print(f"🚀 Executing suggestion: {suggestion}")
            
            # Show processing state
            if self.hud_manager:
                self.hud_manager.set_processing(True)
                self.hud_manager.display_message(f"Executing: {suggestion}", "info")
            
            # Execute goal with agent
            success, output = self.agent_system.execute_goal(suggestion)
            
            # Show result
            if self.hud_manager:
                self.hud_manager.set_processing(False)
                result_msg = "✅ Done!" if success else "❌ Failed"
                self.hud_manager.display_message(
                    f"{result_msg}\n{output[:100]}",
                    "response" if success else "error"
                )
            
            return success
            
        except Exception as e:
            print(f"❌ Suggestion execution error: {e}")
            if self.hud_manager:
                self.hud_manager.set_processing(False)
                self.hud_manager.display_message("Error executing suggestion", "error")
            return False
    
    def process_voice_input(self, text: str):
        """
        Process voice input in context of current screen.
        
        Args:
            text: Voice input text
        """
        if not self.agent_system:
            return
        
        try:
            # Enhance goal with screen context
            enhanced_goal = text
            
            if self.current_context:
                # Add context to goal
                enhanced_goal = f"{text} (Currently viewing: {self.current_context.screen_activity})"
            
            # Show as listening
            if self.hud_manager:
                self.hud_manager.set_listening(True)
                self.hud_manager.display_message(f"Heard: {text}", "info")
            
            # Execute with agent
            if self.hud_manager:
                self.hud_manager.set_listening(False)
                self.hud_manager.set_processing(True)
            
            success, output = self.agent_system.execute_goal(enhanced_goal)
            
            # Display result
            if self.hud_manager:
                self.hud_manager.set_processing(False)
                self.hud_manager.display_message(output, "response")
            
            print(f"✅ Voice input processed: {success}")
            
        except Exception as e:
            print(f"❌ Voice input error: {e}")
    
    def get_context(self) -> Optional[Dict]:
        """Get current multi-modal context."""
        if not self.current_context:
            return None
        
        return {
            'activity': self.current_context.screen_activity,
            'context': self.current_context.screen_context,
            'suggestions': self.current_context.suggestions,
            'confidence': self.current_context.confidence,
            'timestamp': self.current_context.last_update
        }
    
    def set_analysis_interval(self, interval: float):
        """Set screen analysis interval."""
        self.analysis_interval = max(1.0, interval)
        print(f"🔧 Analysis interval set to {interval}s")
    
    def toggle_suggestions(self, enabled: bool = True):
        """Toggle suggestion display."""
        self.enable_suggestions = enabled
        state = "enabled" if enabled else "disabled"
        print(f"💡 Suggestions {state}")
    
    def toggle_ocr(self, enabled: bool = True):
        """Toggle OCR."""
        self.enable_ocr = enabled
        state = "enabled" if enabled else "disabled"
        print(f"🔠 OCR {state}")
    
    def toggle_auto_execute(self, enabled: bool = False):
        """Toggle auto-execution of suggestions."""
        self.auto_execute = enabled
        state = "enabled" if enabled else "disabled"
        print(f"⚡ Auto-execution {state}")
    
    def screenshot_and_analyze(self) -> Dict:
        """
        Manually trigger screenshot and analysis.
        
        Returns:
            Analysis results
        """
        try:
            screenshot = self.screen_capture.capture_full_screen(resize=(800, 600))
            if screenshot is None:
                return None
            
            text = self.ocr_engine.extract_text(screenshot) if self.enable_ocr else ""
            analysis = self.vision_analyzer.analyze(text, "Manual Capture")
            
            if analysis:
                self._process_analysis(analysis)
                return {
                    'activity': analysis.activity,
                    'context': analysis.context,
                    'suggestions': analysis.suggestions,
                    'confidence': analysis.confidence
                }
            
            return None
            
        except Exception as e:
            print(f"❌ Manual analysis error: {e}")
            return None
    
    def get_activity_summary(self) -> Dict:
        """Get summary of monitored activities."""
        if not self.activity_history:
            return {'total': 0}
        
        activity_counts = {}
        for record in self.activity_history:
            activity = record['activity']
            activity_counts[activity] = activity_counts.get(activity, 0) + 1
        
        return {
            'total_records': len(self.activity_history),
            'activities': activity_counts,
            'current_activity': self.current_context.screen_activity if self.current_context else None,
            'recent': self.activity_history[-5:]
        }
    
    def export_session(self, filepath: str):
        """Export session data to file."""
        import json
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'activity_history': self.activity_history,
            'current_context': self.get_context() if self.current_context else None,
            'settings': {
                'analysis_interval': self.analysis_interval,
                'enable_ocr': self.enable_ocr,
                'enable_suggestions': self.enable_suggestions,
                'auto_execute': self.auto_execute
            }
        }
        
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"✅ Session exported to {filepath}")
            return filepath
        except Exception as e:
            print(f"❌ Export error: {e}")
            return None
    
    def close(self):
        """Close Multi-Modal JARVIS."""
        self.stop_monitoring()
        if self.hud_manager:
            self.hud_manager.close()
        print("👋 Multi-Modal JARVIS closed")


# Example usage
if __name__ == "__main__":
    print("🎯 Multi-Modal JARVIS Test")
    
    # Note: Requires agent_system to be fully functional
    # This is demonstration code
    
    try:
        # Initialize without agent (demo mode)
        mm_jarvis = MultiModalJARVIS(enable_hud=True)
        
        print("\n📡 Starting screen monitoring...")
        mm_jarvis.start_monitoring()
        
        # Run for 10 seconds
        for i in range(10):
            time.sleep(1)
            context = mm_jarvis.get_context()
            if context:
                print(f"Context: {context['activity']}")
        
        # Export session
        mm_jarvis.export_session("multimodal_session.json")
        
        # Cleanup
        mm_jarvis.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
