"""
Memory Agent - Long-term learning and pattern storage

Manages persistent behavioral learning and knowledge accumulation.
Enables JARVIS to improve and adapt over time.
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from agents.base_agent import BaseAgent, AgentMessage


class KnowledgeEntry:
    """Represents a knowledge entry in memory."""
    
    def __init__(self, key: str, value: Any, timestamp: datetime = None,
                 confidence: float = 0.5, category: str = "general"):
        """Initialize knowledge entry."""
        self.key = key
        self.value = value
        self.timestamp = timestamp or datetime.now()
        self.confidence = confidence
        self.category = category
        self.access_count = 0
        self.last_accessed = datetime.now()
    
    def update(self, value: Any, confidence: float = None):
        """Update value and confidence."""
        old_confidence = self.confidence
        self.value = value
        
        if confidence is not None:
            # Exponential moving average for confidence
            self.confidence = (old_confidence * 0.7) + (confidence * 0.3)
        
        self.timestamp = datetime.now()
    
    def record_access(self):
        """Record access for usage tracking."""
        self.access_count += 1
        self.last_accessed = datetime.now()


class MemoryAgent(BaseAgent):
    """
    Maintains long-term memory and learning.
    
    Features:
    - Persistent knowledge storage
    - Pattern recognition and learning
    - Adaptive behavior adjustment
    - User preference tracking
    - Performance analysis
    """
    
    def __init__(self, agent_id: str = "memory", brain=None):
        """Initialize memory agent."""
        super().__init__(agent_id, "memory", brain)
        
        # Knowledge base indexed by category
        self.knowledge_base: Dict[str, Dict[str, KnowledgeEntry]] = {
            'user_preferences': {},
            'behavior_patterns': {},
            'learned_tasks': {},
            'performance_metrics': {},
            'error_recovery': {},
            'optimization_tips': {},
            'general_knowledge': {}
        }
        
        self.learning_history = []
        self.consolidation_count = 0
    
    def get_capabilities(self) -> List[str]:
        """Get memory agent capabilities."""
        return [
            "store_knowledge",
            "retrieve_knowledge",
            "update_confidence",
            "forget_entry",
            "get_patterns",
            "consolidate_memory",
            "export_knowledge",
            "import_knowledge"
        ]
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute memory-related task.
        
        Args:
            task: Task dict with:
              - type: operation type
              - key: knowledge key
              - value: value to store
              - etc.
              
        Returns:
            Operation result
        """
        self.update_state("busy")
        start_time = __import__('time').time()
        
        try:
            task_type = task.get('type', 'store')
            
            if task_type == 'store':
                result = self._store_knowledge(task)
            elif task_type == 'retrieve':
                result = self._retrieve_knowledge(task)
            elif task_type == 'update':
                result = self._update_knowledge(task)
            elif task_type == 'forget':
                result = self._forget_knowledge(task)
            elif task_type == 'get_patterns':
                result = self._get_patterns(task)
            elif task_type == 'consolidate':
                result = await self._consolidate_memory(task)
            else:
                result = {'error': f'Unknown task type: {task_type}'}
            
            exec_time = __import__('time').time() - start_time
            self.record_success(exec_time)
            self.update_state("idle")
            
            return result
            
        except Exception as e:
            self.record_failure(str(e))
            self.update_state("error")
            return {'error': str(e)}
    
    def store_knowledge(self, key: str, value: Any, 
                       category: str = "general",
                       confidence: float = 0.5) -> bool:
        """
        Store knowledge in memory.
        
        Args:
            key: Knowledge identifier
            value: Value to store
            category: Category for organization
            confidence: Confidence score 0-1
        """
        if category not in self.knowledge_base:
            self.knowledge_base[category] = {}
        
        entry = KnowledgeEntry(
            key=key,
            value=value,
            confidence=confidence,
            category=category
        )
        
        self.knowledge_base[category][key] = entry
        
        self.learning_history.append({
            'timestamp': datetime.now(),
            'action': 'store',
            'key': key,
            'category': category,
            'confidence': confidence
        })
        
        self._broadcast_knowledge_event("stored", key, category)
        return True
    
    def retrieve_knowledge(self, key: str, 
                          category: Optional[str] = None) -> Optional[Any]:
        """
        Retrieve knowledge from memory.
        
        Args:
            key: Knowledge identifier
            category: Optional category filter
            
        Returns:
            Knowledge value or None
        """
        if category:
            if category in self.knowledge_base:
                if key in self.knowledge_base[category]:
                    entry = self.knowledge_base[category][key]
                    entry.record_access()
                    return entry.value
        else:
            # Search all categories
            for cat_dict in self.knowledge_base.values():
                if key in cat_dict:
                    entry = cat_dict[key]
                    entry.record_access()
                    return entry.value
        
        return None
    
    def update_knowledge(self, key: str, value: Any,
                        confidence: float = None,
                        category: Optional[str] = None) -> bool:
        """Update existing knowledge entry."""
        if category:
            if category in self.knowledge_base and key in self.knowledge_base[category]:
                self.knowledge_base[category][key].update(value, confidence)
                return True
        else:
            # Search all categories
            for cat_dict in self.knowledge_base.values():
                if key in cat_dict:
                    cat_dict[key].update(value, confidence)
                    return True
        
        return False
    
    def forget_knowledge(self, key: str, category: Optional[str] = None) -> bool:
        """Remove knowledge entry (forgetting)."""
        if category:
            if category in self.knowledge_base and key in self.knowledge_base[category]:
                del self.knowledge_base[category][key]
                return True
        else:
            # Search all categories
            for cat_dict in self.knowledge_base.values():
                if key in cat_dict:
                    del cat_dict[key]
                    return True
        
        return False
    
    def _store_knowledge(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle store operation."""
        key = task.get('key')
        value = task.get('value')
        category = task.get('category', 'general')
        confidence = task.get('confidence', 0.5)
        
        if not key:
            return {'error': 'No key provided'}
        
        success = self.store_knowledge(key, value, category, confidence)
        
        return {
            'status': 'success' if success else 'failed',
            'key': key,
            'category': category
        }
    
    def _retrieve_knowledge(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle retrieve operation."""
        key = task.get('key')
        category = task.get('category')
        
        if not key:
            return {'error': 'No key provided'}
        
        value = self.retrieve_knowledge(key, category)
        
        if value is not None:
            return {
                'status': 'found',
                'key': key,
                'value': value,
                'category': category
            }
        else:
            return {
                'status': 'not_found',
                'key': key
            }
    
    def _update_knowledge(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle update operation."""
        key = task.get('key')
        value = task.get('value')
        confidence = task.get('confidence')
        category = task.get('category')
        
        success = self.update_knowledge(key, value, confidence, category)
        
        return {
            'status': 'success' if success else 'not_found',
            'key': key
        }
    
    def _forget_knowledge(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Handle forget operation."""
        key = task.get('key')
        category = task.get('category')
        
        success = self.forget_knowledge(key, category)
        
        return {
            'status': 'success' if success else 'not_found',
            'key': key
        }
    
    def _get_patterns(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze and return behavior patterns."""
        category = task.get('category', 'behavior_patterns')
        
        patterns = []
        if category in self.knowledge_base:
            for key, entry in self.knowledge_base[category].items():
                patterns.append({
                    'pattern': key,
                    'confidence': entry.confidence,
                    'access_count': entry.access_count,
                    'last_seen': entry.last_accessed.isoformat()
                })
        
        # Sort by confidence
        patterns.sort(key=lambda x: x['confidence'], reverse=True)
        
        return {
            'category': category,
            'patterns': patterns,
            'total_patterns': len(patterns)
        }
    
    async def _consolidate_memory(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Consolidate memory using Groq for analysis.
        
        Looks for patterns, identifies high-confidence vs low-confidence knowledge,
        and suggests optimizations.
        """
        if not self.brain:
            return {'error': 'Brain not available'}
        
        # Gather statistics
        stats = self._analyze_memory_stats()
        
        # Use Groq to suggest consolidations
        prompt = f"""Analyze this memory system state and suggest optimizations:

Total knowledge entries: {stats['total_entries']}
High confidence entries (>0.8): {stats['high_confidence']}
Low confidence entries (<0.3): {stats['low_confidence']}
Most accessed patterns: {stats['top_patterns']}
Unused entries: {stats['unused']}

What knowledge should be:
1. Forgotten (low value, unused)
2. Consolidated (similar knowledge merged)
3. Promoted (high confidence, frequently used)

Provide suggestions as JSON:
{{ "forget": ["key1", "key2"], "consolidate": [["key1", "key2"]], "promote": ["key3"] }}"""
        
        response = await asyncio.to_thread(self.brain.ask_groq, prompt, 0.5)
        
        try:
            suggestions = json.loads(response)
            
            # Apply suggestions
            forgotten = 0
            for key in suggestions.get('forget', []):
                if self.forget_knowledge(key):
                    forgotten += 1
            
            self.consolidation_count += 1
            
            return {
                'status': 'consolidated',
                'forgotten': forgotten,
                'suggestions': suggestions,
                'consolidation_count': self.consolidation_count
            }
            
        except json.JSONDecodeError:
            return {'error': 'Could not parse consolidation suggestions'}
    
    def _analyze_memory_stats(self) -> Dict[str, Any]:
        """Analyze memory statistics."""
        total = 0
        high_conf = 0
        low_conf = 0
        unused = 0
        access_counts = {}
        
        for category, entries in self.knowledge_base.items():
            for key, entry in entries.items():
                total += 1
                
                if entry.confidence > 0.8:
                    high_conf += 1
                if entry.confidence < 0.3:
                    low_conf += 1
                if entry.access_count == 0:
                    unused += 1
                
                access_counts[key] = entry.access_count
        
        # Top patterns by access count
        top_patterns = sorted(
            access_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        return {
            'total_entries': total,
            'high_confidence': high_conf,
            'low_confidence': low_conf,
            'unused': unused,
            'top_patterns': [k for k, v in top_patterns]
        }
    
    def _broadcast_knowledge_event(self, action: str, key: str, category: str):
        """Broadcast knowledge event to shared memory."""
        msg = AgentMessage(
            sender_id=self.agent_id,
            recipient_id="orchestrator",
            message_type="knowledge_event",
            content={
                'action': action,
                'key': key,
                'category': category,
                'timestamp': datetime.now().isoformat()
            }
        )
        self.shared_memory.broadcast_message(msg)
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        stats = {
            'categories': {},
            'total_entries': 0,
            'learning_events': len(self.learning_history),
            'consolidations': self.consolidation_count
        }
        
        for category, entries in self.knowledge_base.items():
            stats['categories'][category] = {
                'entries': len(entries),
                'avg_confidence': sum(e.confidence for e in entries.values()) / len(entries) if entries else 0
            }
            stats['total_entries'] += len(entries)
        
        return stats
    
    def export_knowledge(self, format: str = "json") -> str:
        """Export knowledge base."""
        data = {}
        
        for category, entries in self.knowledge_base.items():
            data[category] = {
                key: {
                    'value': entry.value,
                    'confidence': entry.confidence,
                    'access_count': entry.access_count,
                    'timestamp': entry.timestamp.isoformat()
                }
                for key, entry in entries.items()
            }
        
        if format == "json":
            return json.dumps(data, indent=2)
        else:
            return str(data)


# Example usage
if __name__ == "__main__":
    print("🧠 Memory Agent Test\n")
    
    agent = MemoryAgent()
    
    # Test 1: Store knowledge
    print("📝 Test 1: Store Knowledge")
    agent.store_knowledge(
        'vscode_open_time',
        '09:00',
        category='user_preferences',
        confidence=0.8
    )
    print("  Stored: User opens VS Code at 9 AM")
    
    # Test 2: Retrieve knowledge
    print("\n📝 Test 2: Retrieve Knowledge")
    value = agent.retrieve_knowledge('vscode_open_time')
    print(f"  Retrieved: {value}")
    
    # Test 3: Store multiple patterns
    print("\n📝 Test 3: Store Multiple Patterns")
    patterns = [
        ('firefox_after_vscode', True, 'behavior_patterns', 0.75),
        ('coffee_break_after_2h', True, 'behavior_patterns', 0.6),
        ('meeting_check_emails', True, 'behavior_patterns', 0.85)
    ]
    
    for key, value, cat, conf in patterns:
        agent.store_knowledge(key, value, cat, conf)
    print(f"  Stored {len(patterns)} behavior patterns")
    
    # Test 4: Statistics
    print("\n📊 Memory Statistics:")
    stats = agent.get_memory_stats()
    for key, value in stats.items():
        if key != 'categories':
            print(f"  {key}: {value}")
    
    print("\n  Categories:")
    for cat, cat_stats in stats['categories'].items():
        if cat_stats['entries'] > 0:
            print(f"    {cat}: {cat_stats['entries']} entries (avg confidence: {cat_stats['avg_confidence']:.2f})")
