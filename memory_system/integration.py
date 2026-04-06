"""
Memory System Integration - Wiring Everything Together

This module demonstrates how to integrate the memory system with JARVIS
and shows practical integration patterns.
"""

import asyncio
from typing import Optional, Dict, Any
from datetime import datetime


class MemorySystemIntegration:
    """
    Integrates memory system with JARVIS orchestrator.
    
    Handles:
    - Memory ingestion from conversations
    - Context injection into Groq prompts
    - Proactive knowledge updates
    - Learning from patterns
    """
    
    def __init__(self, orchestrator=None, memory_manager=None):
        """
        Initialize integration.
        
        Args:
            orchestrator: JARVIS orchestrator instance
            memory_manager: MemoryManager instance
        """
        self.orchestrator = orchestrator
        self.memory_manager = memory_manager
        
        self.integration_stats = {
            'messages_processed': 0,
            'memories_ingested': 0,
            'context_injections': 0,
            'groq_enhancements': 0
        }
    
    async def process_user_message(self, message: str) -> str:
        """
        Process user message with memory ingestion and context.
        
        Pipeline:
        1. Ingest message as memory
        2. Extract context from similar memories
        3. Enhance Groq prompts with context
        4. Return response
        
        Args:
            message: User input
            
        Returns:
            Enhanced response with context
        """
        self.integration_stats['messages_processed'] += 1
        
        # Step 1: Ingest message as memory
        if self.memory_manager:
            try:
                from memory_system.knowledge_ingestion import KnowledgeIngestionPipeline
                pipeline = KnowledgeIngestionPipeline(self.memory_manager)
                
                result = await pipeline.process_message(
                    message,
                    source="user_input",
                    auto_ingest=True
                )
                
                if result.get('status') == 'success':
                    self.integration_stats['memories_ingested'] += 1
            except Exception as e:
                print(f"⚠️ Memory ingestion failed: {e}")
        
        # Step 2: Get response from orchestrator
        if self.orchestrator:
            response = await self.orchestrator.process(message)
        else:
            response = "Memory system ready, but no orchestrator connected."
        
        return response
    
    async def inject_memory_context(self, prompt: str,
                                   memory_limit: int = 3) -> str:
        """
        Inject relevant memory context into prompt.
        
        Args:
            prompt: Original prompt
            memory_limit: Max memories to include
            
        Returns:
            Enhanced prompt with context
        """
        if not self.memory_manager:
            return prompt
        
        try:
            # Retrieve relevant memories
            recall_result = await self.memory_manager.retrieve_memory(
                query=prompt,
                limit=memory_limit,
                enhance=False  # Don't enhance in this step
            )
            
            if not recall_result or not recall_result.retrieved_memories:
                return prompt
            
            # Format memories for context
            context_parts = []
            for mem in recall_result.retrieved_memories:
                content = mem.get('content', mem.get('label', ''))
                context_parts.append(f"- {content}")
            
            context = "\n".join(context_parts)
            
            # Inject into prompt
            enhanced_prompt = f"""Here's relevant context from your memory:
{context}

Now, considering this context, please respond to:
{prompt}"""
            
            self.integration_stats['context_injections'] += 1
            return enhanced_prompt
            
        except Exception as e:
            print(f"⚠️ Context injection failed: {e}")
            return prompt
    
    async def enhance_groq_response(self, prompt: str,
                                   brain=None) -> Optional[str]:
        """
        Get Groq response with memory context.
        
        Args:
            prompt: Original prompt
            brain: JARVIS brain (has ask_groq method)
            
        Returns:
            Enhanced response
        """
        if not brain:
            return None
        
        try:
            # Inject memory context
            enhanced_prompt = await self.inject_memory_context(
                prompt,
                memory_limit=3
            )
            
            # Get Groq response
            response = await asyncio.to_thread(
                brain.ask_groq,
                enhanced_prompt,
                temperature=0.7
            )
            
            self.integration_stats['groq_enhancements'] += 1
            return response
            
        except Exception as e:
            print(f"❌ Groq enhancement failed: {e}")
            return None
    
    async def learn_from_behavior(self, behavior_data: Dict[str, Any]) -> bool:
        """
        Store learned behaviors as memories.
        
        Args:
            behavior_data: Behavior pattern data
            
        Returns:
            Success status
        """
        if not self.memory_manager:
            return False
        
        try:
            from memory_system.memory_manager import (
                MemoryIngestionRequest, MemoryPriority
            )
            
            request = MemoryIngestionRequest(
                content=f"Behavior pattern: {behavior_data.get('description', '')}",
                category="patterns",
                priority=MemoryPriority.NORMAL,
                tags=["pattern", "behavior"],
                source="behavior_learning",
                metadata=behavior_data
            )
            
            result = await self.memory_manager.ingest_memory(request)
            return result.get('status') == 'success'
            
        except Exception as e:
            print(f"❌ Behavior learning failed: {e}")
            return False
    
    def get_integration_stats(self) -> Dict[str, Any]:
        """Get integration statistics."""
        return {
            **self.integration_stats,
            'memory_system_status': 'connected' if self.memory_manager else 'disconnected',
            'orchestrator_status': 'connected' if self.orchestrator else 'disconnected'
        }


# Example initialization code
INTEGRATION_EXAMPLE = """
# In main JARVIS orchestrator:

from memory_system import MemoryManager, VectorStore, KnowledgeGraph, RecallEngine, Summarizer
from memory_system.integration import MemorySystemIntegration

class JARVISOrchestrator:
    def __init__(self):
        # Initialize memory system components
        self.vector_store = VectorStore(use_mock_embeddings=False)
        self.knowledge_graph = KnowledgeGraph()
        self.summarizer = Summarizer()
        self.recall_engine = RecallEngine(self.vector_store, self.knowledge_graph)
        self.memory_manager = MemoryManager(
            self.vector_store,
            self.knowledge_graph,
            self.summarizer,
            self.recall_engine
        )
        
        # Initialize integration
        self.memory_integration = MemorySystemIntegration(self, self.memory_manager)
    
    async def process_user_input(self, message: str) -> str:
        # Process with memory ingestion and context
        return await self.memory_integration.process_user_message(message)
    
    async def ask_groq_with_context(self, prompt: str) -> str:
        # Get response with memory context
        return await self.memory_integration.enhance_groq_response(
            prompt,
            brain=self.brain
        )
"""


class MemorySystemHealthCheck:
    """Health check for memory system integration."""
    
    @staticmethod
    def check_components(memory_manager) -> Dict[str, bool]:
        """
        Check all memory system components.
        
        Args:
            memory_manager: MemoryManager instance
            
        Returns:
            Status of each component
        """
        checks = {}
        
        try:
            checks['vector_store'] = (
                memory_manager.vector_store is not None and
                hasattr(memory_manager.vector_store, 'search')
            )
        except:
            checks['vector_store'] = False
        
        try:
            checks['knowledge_graph'] = (
                memory_manager.knowledge_graph is not None and
                hasattr(memory_manager.knowledge_graph, 'find_path')
            )
        except:
            checks['knowledge_graph'] = False
        
        try:
            checks['summarizer'] = (
                memory_manager.summarizer is not None and
                hasattr(memory_manager.summarizer, 'summarize')
            )
        except:
            checks['summarizer'] = False
        
        try:
            checks['recall_engine'] = (
                memory_manager.recall_engine is not None and
                hasattr(memory_manager.recall_engine, 'recall')
            )
        except:
            checks['recall_engine'] = False
        
        try:
            checks['memory_index'] = isinstance(memory_manager.memory_index, dict)
        except:
            checks['memory_index'] = False
        
        return checks
    
    @staticmethod
    def get_system_status(memory_manager) -> Dict[str, Any]:
        """Get comprehensive system status."""
        checks = MemorySystemHealthCheck.check_components(memory_manager)
        
        all_ok = all(checks.values())
        
        return {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy' if all_ok else 'degraded',
            'component_checks': checks,
            'memory_count': len(memory_manager.memory_index) if memory_manager else 0,
            'manager_stats': memory_manager.get_memory_stats() if memory_manager else {}
        }


def setup_memory_system(orchestrator, use_mock_embeddings: bool = False):
    """
    Complete setup of memory system with orchestrator.
    
    Args:
        orchestrator: JARVIS orchestrator instance
        use_mock_embeddings: Use mock embeddings for testing
        
    Returns:
        Integration instance
    """
    from memory_system import (
        VectorStore, KnowledgeGraph, Summarizer,
        RecallEngine, MemoryManager
    )
    from memory_system.integration import MemorySystemIntegration
    
    print("🧠 Setting up JARVIS Memory System...")
    
    # Initialize components
    print("  📦 Initializing Vector Store...")
    vector_store = VectorStore(use_mock_embeddings=use_mock_embeddings)
    
    print("  🔗 Initializing Knowledge Graph...")
    knowledge_graph = KnowledgeGraph()
    
    print("  📝 Initializing Summarizer...")
    summarizer = Summarizer()
    
    print("  🔄 Initializing Recall Engine...")
    recall_engine = RecallEngine(vector_store, knowledge_graph)
    
    print("  ⚙️  Initializing Memory Manager...")
    memory_manager = MemoryManager(
        vector_store,
        knowledge_graph,
        summarizer,
        recall_engine
    )
    
    # Initialize integration
    print("  🔌 Initializing Integration...")
    integration = MemorySystemIntegration(orchestrator, memory_manager)
    
    # Run health check
    print("\n  🏥 Running health check...")
    health = MemorySystemHealthCheck.get_system_status(memory_manager)
    
    if health['overall_status'] == 'healthy':
        print("  ✅ All components operational!")
    else:
        print("  ⚠️  Some components degraded")
        for component, ok in health['component_checks'].items():
            status = "✅" if ok else "❌"
            print(f"    {status} {component}")
    
    print("\n✨ Memory System Ready!\n")
    
    return integration


# Example usage
if __name__ == "__main__":
    print("🧠 JARVIS Memory System Integration\n")
    
    print("Integration Example:")
    print(INTEGRATION_EXAMPLE)
    
    print("\n📊 Health Check Example:")
    print("  Use: MemorySystemHealthCheck.get_system_status(memory_manager)")
    print("  Returns: {'overall_status': 'healthy', 'component_checks': {...}}")
    
    print("\n🔧 Setup Example:")
    print("  Use: integration = setup_memory_system(orchestrator)")
    print("  Returns: MemorySystemIntegration instance ready to use")
