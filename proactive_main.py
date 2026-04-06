"""
Proactive JARVIS - Main Entry Point

Integrated autonomous AI system combining:
- Multi-modal vision and understanding
- Intelligent behavior prediction
- Risk-managed task execution
- Autonomous background operation
- Long-term learning and adaptation

Version: 2.0 (Proactive Multi-Agent System)
"""

import asyncio
import json
import signal
from typing import Dict, Any, Optional
from datetime import datetime
from agents.base_agent import get_shared_memory, SharedMemory
from agents.orchestrator import Orchestrator
from proactive_behavior_tracker import BehaviorTracker


class ProactiveJARVIS:
    """
    Main controller for proactive JARVIS system.
    
    Manages:
    - System initialization
    - Background autonomous loops
    - User interaction
    - Graceful shutdown
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize proactive JARVIS."""
        self.config = self._load_config(config_path)
        self.shared_memory = get_shared_memory()
        self.orchestrator = Orchestrator(brain=None)  # Brain set later
        self.behavior_tracker = BehaviorTracker()
        
        self.is_running = False
        self.loop_task: Optional[asyncio.Task] = None
        
        print("✨ Proactive JARVIS v2.0 initialized")
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration."""
        default_config = {
            'autonomy_level': 'medium',
            'proactivity_enabled': True,
            'background_loop_interval': 30,
            'max_prediction_confidence': 0.8,
            'behavior_tracking_enabled': True,
            'risk_assessment_enabled': True,
            'debug_mode': False
        }
        
        if config_path:
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                print(f"⚠️ Could not load config: {e}")
        
        return default_config
    
    def start(self):
        """Start proactive JARVIS system."""
        print("\n🚀 Starting Proactive JARVIS...\n")
        
        # Configure based on settings
        self.orchestrator.set_autonomy_level(self.config['autonomy_level'])
        self.orchestrator.set_proactivity(self.config['proactivity_enabled'])
        self.orchestrator.background_loop_interval = self.config['background_loop_interval']
        
        # Start behavior tracking
        if self.config['behavior_tracking_enabled']:
            self.behavior_tracker.start()
            print("📊 Behavior tracking started")
        
        self.is_running = True
        print("✅ Proactive JARVIS is running")
        print("   Type 'help' for commands")
        print()
    
    def stop(self):
        """Stop proactive JARVIS system."""
        print("\n🛑 Stopping Proactive JARVIS...\n")
        
        self.is_running = False
        
        if self.loop_task:
            self.loop_task.cancel()
        
        if self.config['behavior_tracking_enabled']:
            self.behavior_tracker.stop()
            print("📊 Behavior tracking stopped")
        
        print("✅ Proactive JARVIS stopped")
    
    async def run_background_loop(self, duration_seconds: int = 300):
        """
        Run autonomous background loop.
        
        Args:
            duration_seconds: How long to run (None = infinite)
        """
        print(f"\n🔄 Running autonomous loop for {duration_seconds}s...\n")
        
        try:
            loop_task = {
                'type': 'autonomous_loop',
                'duration_seconds': duration_seconds,
                'context': {'user_available': True}
            }
            
            result = await self.orchestrator.execute(loop_task)
            
            print(f"\n📖 Loop Results:")
            print(f"  Status: {result.get('status')}")
            print(f"  Iterations: {result.get('iterations', 0)}")
            print(f"  Tasks Executed: {result.get('tasks_executed', 0)}")
            
            summary = result.get('results_summary', {})
            print(f"  Success Rate: {summary.get('success_rate', 0):.2%}")
            
            return result
            
        except asyncio.CancelledError:
            print("⚠️ Loop cancelled")
        except Exception as e:
            print(f"❌ Loop error: {e}")
    
    def show_status(self):
        """Display current system status."""
        print("\n" + "="*60)
        print("📊 PROACTIVE JARVIS STATUS")
        print("="*60 + "\n")
        
        # Main status
        print(f"Status: {'🟢 Running' if self.is_running else '🔴 Stopped'}")
        print(f"Autonomy Level: {self.orchestrator.autonomy_level}")
        print(f"Proactivity: {'✓ Enabled' if self.orchestrator.proactivity_enabled else '✗ Disabled'}")
        print(f"Debug Mode: {'✓ On' if self.config['debug_mode'] else '✗ Off'}\n")
        
        # Agent status
        print("🤖 Agent Status:")
        status = self.orchestrator.get_orchestrator_status()
        for agent_name, agent_status in status['agents'].items():
            state = agent_status.get('status', 'unknown').upper()
            symbol = "🟢" if state == "IDLE" or state == "READY" else "🟡"
            print(f"  {symbol} {agent_name.capitalize()}: {state}")
        
        print()
        
        # Statistics
        print("📈 Statistics:")
        stats = self.orchestrator.get_agent_stats()
        
        if 'executor_stats' in stats:
            exec_stats = stats['executor_stats']
            print(f"  Executions: {exec_stats.get('total_executions', 0)}")
            print(f"  Success Rate: {exec_stats.get('success_rate', 0):.2%}")
        
        if 'scheduler_stats' in stats:
            sched_stats = stats['scheduler_stats']
            print(f"  Scheduled Tasks: {sched_stats.get('total_scheduled', 0)}")
        
        if 'memory_stats' in stats:
            mem_stats = stats['memory_stats']
            print(f"  Knowledge Entries: {mem_stats.get('total_entries', 0)}")
        
        print("\n" + "="*60 + "\n")
    
    def show_help(self):
        """Show help information."""
        print("""
╔════════════════════════════════════════════════════════════════╗
║                   PROACTIVE JARVIS COMMANDS                    ║
╚════════════════════════════════════════════════════════════════╝

CORE COMMANDS:
  start         - Start the system
  stop          - Stop the system
  loop [time]   - Run autonomous loop (default 300s)
  status        - Show system status
  
CONFIGURATION:
  autonomy [low|medium|high]  - Set autonomy level
  proactive [on|off]          - Enable/disable proactive behavior
  config                      - Show current configuration
  
AGENT COMMANDS:
  predict       - Get behavior predictions
  schedule      - Show scheduled tasks
  memory        - Show knowledge base stats
  
DIAGNOSTICS:
  debug [on|off]  - Enable/disable debug mode
  recent          - Show recent executions
  
SYSTEM:
  help          - Show this help
  exit/quit     - Exit the system
        """)
    
    def handle_command(self, command: str):
        """Handle user command."""
        parts = command.strip().lower().split()
        
        if not parts:
            return
        
        cmd = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        if cmd == 'help':
            self.show_help()
        
        elif cmd == 'status':
            self.show_status()
        
        elif cmd == 'start':
            if not self.is_running:
                self.start()
            else:
                print("⚠️ System already running")
        
        elif cmd == 'stop':
            if self.is_running:
                self.stop()
            else:
                print("⚠️ System not running")
        
        elif cmd == 'config':
            print("\n📋 Current Configuration:")
            for key, value in self.config.items():
                print(f"  {key}: {value}")
            print()
        
        elif cmd == 'autonomy' and args:
            level = args[0]
            if level in ['low', 'medium', 'high']:
                self.orchestrator.set_autonomy_level(level)
                print(f"✅ Autonomy set to {level}")
            else:
                print(f"❌ Invalid autonomy level: {level}")
        
        elif cmd == 'proactive' and args:
            if args[0] == 'on':
                self.orchestrator.set_proactivity(True)
                print("✅ Proactivity enabled")
            elif args[0] == 'off':
                self.orchestrator.set_proactivity(False)
                print("✅ Proactivity disabled")
            else:
                print("❌ Use: proactive [on|off]")
        
        elif cmd == 'exit' or cmd == 'quit':
            return 'exit'
        
        else:
            print(f"❌ Unknown command: {cmd}")
            print("   Type 'help' for available commands")
        
        return None
    
    async def interactive_mode(self):
        """Run in interactive mode."""
        print("\n" + "="*60)
        print("🎤 INTERACTIVE MODE")
        print("="*60)
        self.show_help()
        
        self.start()
        
        loop = asyncio.get_event_loop()
        
        while self.is_running:
            try:
                # Get user input (non-blocking)
                command = await loop.run_in_executor(None, input, ">> ")
                
                # Handle loop command specially
                if command.strip().lower().startswith('loop'):
                    parts = command.split()
                    duration = int(parts[1]) if len(parts) > 1 else 300
                    await self.run_background_loop(duration)
                else:
                    result = self.handle_command(command)
                    if result == 'exit':
                        break
                
            except EOFError:
                break
            except KeyboardInterrupt:
                print("\n⏸️  Interrupted")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
        
        self.stop()
    
    async def daemon_mode(self, duration_seconds: int = 3600):
        """Run in daemon mode (background operation)."""
        print("\n" + "="*60)
        print("👻 DAEMON MODE")
        print("="*60)
        print(f"Running for {duration_seconds}s in background...\n")
        
        self.start()
        
        try:
            result = await self.run_background_loop(duration_seconds)
            print("\n✅ Daemon cycle completed")
            
        except KeyboardInterrupt:
            print("\n⏸️  Interrupted")
        finally:
            self.stop()


async def main():
    """Main entry point."""
    import sys
    
    print("""
╔════════════════════════════════════════════════════════════════╗
║                   🤖 PROACTIVE JARVIS v2.0 🤖                  ║
║               Intelligent Autonomous AI Assistant              ║
║                                                                ║
║  Multi-Modal • Multi-Agent • Predictive • Risk-Aware          ║
╚════════════════════════════════════════════════════════════════╝
    """)
    
    jarvis = ProactiveJARVIS(config_path='jarvis_config.json')
    
    # Check for command-line arguments
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == 'daemon':
            duration = int(sys.argv[2]) if len(sys.argv) > 2 else 3600
            await jarvis.daemon_mode(duration)
        
        elif mode == 'interactive' or mode == 'i':
            await jarvis.interactive_mode()
        
        elif mode == 'status':
            jarvis.show_status()
        
        else:
            print(f"Unknown mode: {mode}")
            print("Usage: python proactive_main.py [interactive|daemon|status] [args]")
    
    else:
        # Default: interactive mode
        await jarvis.interactive_mode()


if __name__ == "__main__":
    asyncio.run(main())
