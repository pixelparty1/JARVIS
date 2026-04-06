"""
Memory Manager - Central Orchestration

Coordinates all memory system components:
- Ingestion (adding new memories)
- Summarization (compressing information)
- Storage (vector store + knowledge graph)
- Retrieval (recall engine)
- Management (priority, lifecycle, export/import)
"""

import asyncio
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import json


class MemoryPriority(Enum):
    """Memory importance levels."""
    CRITICAL = 5
    HIGH = 4
    NORMAL = 3
    LOW = 2
    ARCHIVED = 1


@dataclass
class MemoryIngestionRequest:
    """Request to ingest a memory."""
    content: str
    category: str = "general"
    priority: MemoryPriority = MemoryPriority.NORMAL
    tags: List[str] = None
    source: str = "manual"
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}


class MemoryManager:
    """
    Central memory system orchestrator.
    
    Manages memory lifecycle:
    - Ingestion and processing
    - Auto-tagging and categorization
    - Vector storage and indexing
    - Knowledge graph integration
    - Priority scoring and lifecycle
    - Recall and retrieval
    """
    
    def __init__(self, vector_store=None, knowledge_graph=None,
                 summarizer=None, recall_engine=None):
        """
        Initialize memory manager.
        
        Args:
            vector_store: VectorStore instance
            knowledge_graph: KnowledgeGraph instance
            summarizer: Summarizer instance
            recall_engine: RecallEngine instance
        """
        self.vector_store = vector_store
        self.knowledge_graph = knowledge_graph
        self.summarizer = summarizer
        self.recall_engine = recall_engine
        
        self.memory_index = {}  # id -> memory metadata
        self.memory_queue = []  # Pending memories
        self.processing_history = []
        
        self.manager_stats = {
            'total_ingested': 0,
            'total_summarized': 0,
            'total_stored': 0,
            'total_retrieved': 0,
            'auto_connections_created': 0,
            'tags_generated': 0
        }
    
    async def ingest_memory(self, request: MemoryIngestionRequest) -> Dict[str, Any]:
        """
        Ingest a new memory.
        
        Pipeline:
        1. Validate input
        2. Summarize if long
        3. Extract metadata
        4. Store in vector store
        5. Create graph nodes
        6. Auto-tag
        
        Args:
            request: MemoryIngestionRequest
            
        Returns:
            Memory metadata
        """
        try:
            print(f"📥 Ingesting memory: {request.content[:50]}...")
            
            # Validate content
            if not request.content or len(request.content.strip()) < 5:
                return {'status': 'error', 'reason': 'Content too short'}
            
            memory_id = self._generate_memory_id()
            
            # Summarize if needed
            summary = request.content
            key_points = []
            
            if len(request.content) > 300 and self.summarizer:
                try:
                    result = await asyncio.to_thread(
                        self.summarizer._fallback_summarize,
                        request.content,
                        max_chars=300
                    )
                    summary = result.summary
                    key_points = result.key_points
                    self.manager_stats['total_summarized'] += 1
                except Exception as e:
                    print(f"  ⚠️  Summarization failed: {e}")
            
            # Generate tags if not provided
            all_tags = request.tags.copy()
            if not all_tags and self.summarizer:
                try:
                    result = await asyncio.to_thread(
                        self.summarizer._fallback_summarize,
                        request.content
                    )
                    all_tags = result.tags
                    self.manager_stats['tags_generated'] += len(all_tags)
                except:
                    pass
            
            # Store in vector store
            if self.vector_store:
                try:
                    from vector_store import Memory
                    memory = Memory(
                        id=memory_id,
                        content=summary,
                        tags=all_tags,
                        category=request.category,
                        importance=request.priority.value / 5.0,
                        source=request.source,
                        metadata=request.metadata
                    )
                    
                    await asyncio.to_thread(
                        self.vector_store.add_memory,
                        memory
                    )
                    self.manager_stats['total_stored'] += 1
                except Exception as e:
                    print(f"  ❌ Vector storage failed: {e}")
            
            # Update knowledge graph
            if self.knowledge_graph:
                try:
                    # Add node for this memory
                    from knowledge_graph import GraphNode, GraphEdge, RelationType
                    
                    node = GraphNode(
                        id=memory_id,
                        label=request.category,
                        type="memory",
                        description=summary[:100],
                        importance=request.priority.value / 5.0
                    )
                    
                    await asyncio.to_thread(
                        self.knowledge_graph.add_node,
                        node
                    )
                    
                    # Auto-connect related tags
                    connections = await self._find_related_concepts(
                        summary, all_tags
                    )
                    
                    for related_id, rel_type in connections:
                        try:
                            edge = GraphEdge(
                                source_id=memory_id,
                                target_id=related_id,
                                relation_type=rel_type,
                                weight=0.8
                            )
                            await asyncio.to_thread(
                                self.knowledge_graph.add_edge,
                                edge
                            )
                            self.manager_stats['auto_connections_created'] += 1
                        except:
                            pass
                
                except Exception as e:
                    print(f"  ⚠️  Graph integration failed: {e}")
            
            # Record memory metadata
            memory_metadata = {
                'id': memory_id,
                'original_content': request.content,
                'summary': summary,
                'key_points': key_points,
                'tags': all_tags,
                'category': request.category,
                'priority': request.priority.name,
                'source': request.source,
                'ingested_at': datetime.now().isoformat(),
                'last_accessed': datetime.now().isoformat(),
                'access_count': 0,
                'metadata': request.metadata
            }
            
            self.memory_index[memory_id] = memory_metadata
            self.manager_stats['total_ingested'] += 1
            
            print(f"✅ Memory ingested: {memory_id}")
            return {'status': 'success', 'memory_id': memory_id, **memory_metadata}
            
        except Exception as e:
            print(f"❌ Ingestion error: {e}")
            return {'status': 'error', 'reason': str(e)}
    
    async def _find_related_concepts(self, content: str,
                                     tags: List[str]) -> List[Tuple[str, str]]:
        """
        Find existing memories related to this content.
        
        Args:
            content: Memory content
            tags: Memory tags
            
        Returns:
            List of (memory_id, relation_type) tuples
        """
        connections = []
        
        if not self.memory_index:
            return connections
        
        # Look for tag matches
        for memory_id, metadata in list(self.memory_index.items())[:20]:
            existing_tags = metadata.get('tags', [])
            shared_tags = set(tags) & set(existing_tags)
            
            if shared_tags and len(shared_tags) >= 1:
                connections.append((memory_id, "RELATED_TO"))
        
        return connections[:5]  # Limit connections
    
    async def retrieve_memory(self, query: str,
                             limit: int = 5,
                             enhance: bool = True) -> Optional[Dict]:
        """
        Retrieve memories using recall engine.
        
        Args:
            query: Search query
            limit: Max results
            enhance: Use Groq enhancement
            
        Returns:
            Recall result
        """
        self.manager_stats['total_retrieved'] += 1
        
        if not self.recall_engine:
            return None
        
        result = await self.recall_engine.recall(
            query=query,
            mode=RecallMode.HYBRID,
            limit=limit,
            enhance_with_groq=enhance
        )
        
        return result
    
    def update_memory_priority(self, memory_id: str,
                              priority: MemoryPriority) -> bool:
        """Update memory priority."""
        if memory_id in self.memory_index:
            self.memory_index[memory_id]['priority'] = priority.name
            return True
        return False
    
    def access_memory(self, memory_id: str) -> Optional[Dict]:
        """
        Access memory and update stats.
        
        Args:
            memory_id: Memory ID
            
        Returns:
            Memory metadata
        """
        if memory_id in self.memory_index:
            metadata = self.memory_index[memory_id]
            metadata['last_accessed'] = datetime.now().isoformat()
            metadata['access_count'] = metadata.get('access_count', 0) + 1
            return metadata
        return None
    
    def prune_memory(self, older_than_days: int = 90,
                    min_priority: MemoryPriority = MemoryPriority.LOW) -> int:
        """
        Prune old, low-priority memories.
        
        Args:
            older_than_days: Remove if older than this
            min_priority: Remove if priority lower than this
            
        Returns:
            Number pruned
        """
        pruned = 0
        now = datetime.now()
        to_delete = []
        
        for memory_id, metadata in self.memory_index.items():
            try:
                ingested_at = datetime.fromisoformat(
                    metadata['ingested_at']
                )
                age_days = (now - ingested_at).days
                
                priority = MemoryPriority[metadata.get('priority', 'NORMAL')]
                
                if (age_days > older_than_days and
                    priority.value <= min_priority.value):
                    to_delete.append(memory_id)
                    pruned += 1
            except:
                pass
        
        for memory_id in to_delete:
            del self.memory_index[memory_id]
        
        return pruned
    
    def export_memories(self, filepath: str = None) -> str:
        """
        Export all memories to JSON file.
        
        Args:
            filepath: Export destination
            
        Returns:
            JSON string
        """
        export_data = {
            'exported_at': datetime.now().isoformat(),
            'memory_count': len(self.memory_index),
            'manager_stats': self.manager_stats,
            'memories': self.memory_index
        }
        
        json_data = json.dumps(export_data, indent=2, default=str)
        
        if filepath:
            try:
                with open(filepath, 'w') as f:
                    f.write(json_data)
                print(f"✅ Memories exported to {filepath}")
            except Exception as e:
                print(f"❌ Export failed: {e}")
        
        return json_data
    
    def import_memories(self, filepath: str) -> int:
        """
        Import memories from JSON file.
        
        Args:
            filepath: Import source
            
        Returns:
            Number imported
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            imported = 0
            for memory_id, metadata in data.get('memories', {}).items():
                self.memory_index[memory_id] = metadata
                imported += 1
            
            print(f"✅ Imported {imported} memories")
            return imported
            
        except Exception as e:
            print(f"❌ Import failed: {e}")
            return 0
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics."""
        total_content_size = sum(
            len(m.get('original_content', ''))
            for m in self.memory_index.values()
        )
        
        priorities = {}
        categories = {}
        
        for metadata in self.memory_index.values():
            priority = metadata.get('priority', 'NORMAL')
            category = metadata.get('category', 'general')
            
            priorities[priority] = priorities.get(priority, 0) + 1
            categories[category] = categories.get(category, 0) + 1
        
        return {
            'total_memories': len(self.memory_index),
            'total_content_size_bytes': total_content_size,
            'ingestion_stats': self.manager_stats,
            'priority_distribution': priorities,
            'category_distribution': categories,
            'pending_queue_size': len(self.memory_queue)
        }
    
    def _generate_memory_id(self) -> str:
        """Generate unique memory ID."""
        import uuid
        return f"mem_{uuid.uuid4().hex[:8]}"


# Import RecallMode from recall_engine
try:
    from recall_engine import RecallMode
except ImportError:
    class RecallMode:
        HYBRID = "hybrid"


# Example usage
if __name__ == "__main__":
    print("📦 Memory Manager Test\n")
    
    manager = MemoryManager()
    
    requests = [
        MemoryIngestionRequest(
            content="Learned about machine learning algorithms today",
            category="learning",
            priority=MemoryPriority.HIGH,
            tags=["ml", "ai", "learning"]
        ),
        MemoryIngestionRequest(
            content="Python is powerful for data science projects",
            category="tech",
            priority=MemoryPriority.NORMAL,
            tags=["python", "data-science"]
        )
    ]
    
    print("Testing memory ingestion (non-async):\n")
    for req in requests:
        print(f"Request: {req.content[:40]}...")
        print(f"  Category: {req.category}, Priority: {req.priority.name}\n")
    
    print("📊 Manager Stats:")
    stats = manager.get_memory_stats()
    for key, value in stats.items():
        if key != 'ingestion_stats':
            print(f"  {key}: {value}")
