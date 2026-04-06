"""
Recall Engine - Intelligent Memory Retrieval

Uses vector similarity, knowledge graph, and Groq reasoning to retrieve
and contextualize memories. Acts as the "thinking engine" for JARVIS.
"""

import asyncio
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class RecallMode(Enum):
    """Different retrieval modes."""
    SEMANTIC = "semantic"      # Vector similarity
    GRAPH = "graph"             # Knowledge graph relationships
    HYBRID = "hybrid"           # Combine both
    ASSOCIATIVE = "associative" # Free association
    CONTEXTUAL = "contextual"   # Based on current context


@dataclass
class RecallResult:
    """Result of memory recall."""
    query: str
    mode: str
    retrieved_memories: List[Dict[str, Any]]
    reasoning: str
    enhanced_answer: Optional[str] = None
    confidence: float = 0.7
    sources: List[str] = None
    retrieved_at: str = None
    
    def __post_init__(self):
        if self.sources is None:
            self.sources = []
        if self.retrieved_at is None:
            self.retrieved_at = datetime.now().isoformat()


class RecallEngine:
    """
    Intelligent memory retrieval system.
    
    Features:
    - Semantic search using vectors
    - Graph-based relationship retrieval
    - Hybrid retrieval combining multiple sources
    - Groq-powered reasoning for contextualization
    - Automatic relevance scoring
    """
    
    def __init__(self, vector_store=None, knowledge_graph=None, brain=None):
        """
        Initialize recall engine.
        
        Args:
            vector_store: VectorStore instance
            knowledge_graph: KnowledgeGraph instance
            brain: JARVIS brain (has ask_groq method)
        """
        self.vector_store = vector_store
        self.knowledge_graph = knowledge_graph
        self.brain = brain
        
        self.recall_history = []
        self.retrieval_stats = {
            'total_queries': 0,
            'semantic_uses': 0,
            'graph_uses': 0,
            'hybrid_uses': 0
        }
    
    async def recall(self, query: str,
                    mode: RecallMode = RecallMode.HYBRID,
                    limit: int = 5,
                    enhance_with_groq: bool = True) -> Optional[RecallResult]:
        """
        Retrieve relevant memories using specified mode.
        
        Args:
            query: Query string
            mode: Retrieval mode
            limit: Max memories to retrieve
            enhance_with_groq: Use Groq to enhance results
            
        Returns:
            RecallResult
        """
        self.retrieval_stats['total_queries'] += 1
        
        retrieved_memories = []
        reasoning = ""
        sources = []
        
        try:
            if mode == RecallMode.SEMANTIC:
                retrieved_memories, sources = await self._semantic_recall(
                    query, limit
                )
                self.retrieval_stats['semantic_uses'] += 1
            
            elif mode == RecallMode.GRAPH:
                retrieved_memories, sources = await self._graph_recall(
                    query, limit
                )
                self.retrieval_stats['graph_uses'] += 1
            
            elif mode == RecallMode.HYBRID:
                retrieved_memories, sources = await self._hybrid_recall(
                    query, limit
                )
                self.retrieval_stats['hybrid_uses'] += 1
            
            elif mode == RecallMode.ASSOCIATIVE:
                retrieved_memories, sources = await self._associative_recall(
                    query, limit
                )
            
            elif mode == RecallMode.CONTEXTUAL:
                retrieved_memories, sources = await self._contextual_recall(
                    query, limit
                )
            
            # Generate reasoning
            reasoning = self._generate_reasoning(
                query, retrieved_memories, mode
            )
            
            # Enhance with Groq if requested
            enhanced_answer = None
            if enhance_with_groq and retrieved_memories and self.brain:
                enhanced_answer = await self._enhance_with_groq(
                    query, retrieved_memories
                )
            
            # Create result
            result = RecallResult(
                query=query,
                mode=mode.value,
                retrieved_memories=retrieved_memories,
                reasoning=reasoning,
                enhanced_answer=enhanced_answer,
                sources=sources
            )
            
            self.recall_history.append(result)
            return result
            
        except Exception as e:
            print(f"❌ Recall error: {e}")
            return None
    
    async def _semantic_recall(self, query: str, 
                              limit: int) -> Tuple[List[Dict], List[str]]:
        """
        Retrieve via semantic similarity search.
        
        Args:
            query: Query string
            limit: Max results
            
        Returns:
            (memories, sources)
        """
        if self.vector_store is None:
            return [], []
        
        try:
            # Search vector store
            results = await asyncio.to_thread(
                self.vector_store.search,
                query,
                k=limit,
                threshold=0.3
            )
            
            memories = []
            sources = []
            
            for memory, similarity in results:
                memory_dict = {
                    'id': memory.id,
                    'content': memory.content,
                    'tags': memory.tags,
                    'category': memory.category,
                    'importance': memory.importance,
                    'timestamp': memory.timestamp,
                    'relevance_score': similarity
                }
                memories.append(memory_dict)
                sources.append(f"vector_store ({similarity:.2%})")
            
            return memories, sources
            
        except Exception as e:
            print(f"❌ Semantic recall error: {e}")
            return [], []
    
    async def _graph_recall(self, query: str,
                           limit: int) -> Tuple[List[Dict], List[str]]:
        """
        Retrieve via knowledge graph relationships.
        
        Args:
            query: Query string
            limit: Max results
            
        Returns:
            (memories, sources)
        """
        if self.knowledge_graph is None:
            return [], []
        
        try:
            # Try to find matching node
            query_lower = query.lower()
            matching_nodes = []
            
            for node_id, node in self.knowledge_graph.nodes.items():
                if (query_lower in node.label.lower() or
                    query_lower in node.description.lower()):
                    matching_nodes.append((node_id, node))
            
            if not matching_nodes:
                return [], []
            
            # Get related nodes
            related_memories = {}
            
            for node_id, node in matching_nodes:
                # Get neighbors
                neighbors = self.knowledge_graph.get_neighbors(node_id)
                incoming = self.knowledge_graph.get_incoming(node_id)
                
                for neighbor_id, rel_type in neighbors + incoming:
                    if neighbor_id not in related_memories:
                        related_node = self.knowledge_graph.get_node(neighbor_id)
                        if related_node:
                            related_memories[neighbor_id] = {
                                'id': neighbor_id,
                                'label': related_node.label,
                                'type': related_node.type,
                                'description': related_node.description,
                                'importance': related_node.importance,
                                'relation': rel_type
                            }
            
            # Sort by importance
            sorted_memories = sorted(
                related_memories.values(),
                key=lambda x: x['importance'],
                reverse=True
            )[:limit]
            
            sources = [f"knowledge_graph ({m['relation']})" for m in sorted_memories]
            
            return sorted_memories, sources
            
        except Exception as e:
            print(f"❌ Graph recall error: {e}")
            return [], []
    
    async def _hybrid_recall(self, query: str,
                            limit: int) -> Tuple[List[Dict], List[str]]:
        """
        Retrieve using both semantic and graph modes.
        
        Combines results and ranks by relevance.
        
        Args:
            query: Query string
            limit: Max results
            
        Returns:
            (memories, sources)
        """
        # Get results from both modes
        semantic_results, semantic_sources = await self._semantic_recall(
            query, limit
        )
        graph_results, graph_sources = await self._graph_recall(
            query, limit
        )
        
        # Combine and deduplicate
        combined = {}
        sources = {}
        
        # Add semantic results
        for mem in semantic_results:
            mem_id = mem.get('id')
            if mem_id not in combined:
                combined[mem_id] = mem
                sources[mem_id] = 'semantic'
            else:
                # Boost score if found in both
                combined[mem_id]['relevance_score'] = (
                    combined[mem_id].get('relevance_score', 0.5) * 0.8 + 0.2
                )
        
        # Add graph results
        for mem in graph_results:
            mem_id = mem.get('id')
            if mem_id not in combined:
                combined[mem_id] = mem
                sources[mem_id] = 'graph'
            else:
                sources[mem_id] = 'hybrid'
        
        # Sort by relevance
        sorted_memories = sorted(
            combined.values(),
            key=lambda x: x.get('relevance_score', x.get('importance', 0.5)),
            reverse=True
        )[:limit]
        
        result_sources = [
            f"{sources.get(m.get('id'), 'unknown')}"
            for m in sorted_memories
        ]
        
        return sorted_memories, result_sources
    
    async def _associative_recall(self, query: str,
                                 limit: int) -> Tuple[List[Dict], List[str]]:
        """
        Free-form associative retrieval (loose associations).
        
        Args:
            query: Query string
            limit: Max results
            
        Returns:
            (memories, sources)
        """
        # Use semantic search with lower threshold
        if self.vector_store is None:
            return [], []
        
        try:
            # Search with low threshold
            results = await asyncio.to_thread(
                self.vector_store.search,
                query,
                k=limit * 2,  # Get more to filter
                threshold=0.1  # Very loose threshold
            )
            
            # Sample for associative feel
            import random
            if results:
                sampled = random.sample(results, min(limit, len(results)))
            else:
                sampled = []
            
            memories = []
            sources = []
            
            for memory, similarity in sampled:
                memories.append({
                    'id': memory.id,
                    'content': memory.content,
                    'category': memory.category,
                    'association_strength': similarity
                })
                sources.append('associative')
            
            return memories, sources
            
        except Exception as e:
            print(f"❌ Associative recall error: {e}")
            return [], []
    
    async def _contextual_recall(self, query: str,
                                limit: int) -> Tuple[List[Dict], List[str]]:
        """
        Context-aware retrieval (time, category-based).
        
        Args:
            query: Query string
            limit: Max results
            
        Returns:
            (memories, sources)
        """
        # Start with semantic search
        memories, sources = await self._semantic_recall(query, limit)
        
        # Boost recent memories
        for mem in memories:
            if 'timestamp' in mem:
                from datetime import datetime, timedelta
                try:
                    mem_time = datetime.fromisoformat(mem['timestamp'])
                    now = datetime.now()
                    days_old = (now - mem_time).days
                    
                    # Recency boost
                    if days_old < 7:
                        mem['relevance_score'] = mem.get('relevance_score', 0.5) * 1.3
                    elif days_old < 30:
                        mem['relevance_score'] = mem.get('relevance_score', 0.5) * 1.1
                except:
                    pass
        
        # Re-sort
        memories.sort(
            key=lambda x: x.get('relevance_score', 0.5),
            reverse=True
        )
        
        return memories[:limit], sources[:limit]
    
    def _generate_reasoning(self, query: str,
                           memories: List[Dict],
                           mode: RecallMode) -> str:
        """Generate reasoning for retrieval."""
        if not memories:
            return f"No relevant memories found for: {query}"
        
        memory_count = len(memories)
        
        if mode == RecallMode.SEMANTIC:
            return f"Found {memory_count} semantically similar memories based on content similarity."
        elif mode == RecallMode.GRAPH:
            return f"Found {memory_count} related memories through knowledge connections."
        elif mode == RecallMode.HYBRID:
            return f"Found {memory_count} memories through both semantic and relationship analysis."
        elif mode == RecallMode.ASSOCIATIVE:
            return f"Generated {memory_count} associated memories through loose connections."
        else:
            return f"Retrieved {memory_count} relevant memories."
    
    async def _enhance_with_groq(self, query: str,
                                memories: List[Dict]) -> Optional[str]:
        """
        Use Groq to generate enhanced answer using retrieved memories.
        
        Args:
            query: Original query
            memories: Retrieved memories
            
        Returns:
            Enhanced answer or None
        """
        if self.brain is None:
            return None
        
        try:
            # Format memories
            memory_context = "\n".join([
                f"- {mem.get('content', mem.get('label', ''))}"
                for mem in memories[:3]  # Use top 3
            ])
            
            prompt = f"""Use this past knowledge to answer the question intelligently:

RELEVANT MEMORIES:
{memory_context}

QUESTION: {query}

Provide a thoughtful answer that incorporates the relevant memories."""
            
            answer = await asyncio.to_thread(
                self.brain.ask_groq,
                prompt,
                temperature=0.7
            )
            
            return answer
            
        except Exception as e:
            print(f"❌ Groq enhancement error: {e}")
            return None
    
    def get_recall_stats(self) -> Dict[str, Any]:
        """Get retrieval statistics."""
        return {
            'total_queries': self.retrieval_stats['total_queries'],
            'semantic_uses': self.retrieval_stats['semantic_uses'],
            'graph_uses': self.retrieval_stats['graph_uses'],
            'hybrid_uses': self.retrieval_stats['hybrid_uses'],
            'recall_history_length': len(self.recall_history)
        }


# Example usage
if __name__ == "__main__":
    print("🧠 Recall Engine Test\n")
    
    engine = RecallEngine()
    
    # Simulate recalls
    print("Testing recall modes:\n")
    
    modes = [
        RecallMode.SEMANTIC,
        RecallMode.GRAPH,
        RecallMode.HYBRID,
        RecallMode.ASSOCIATIVE
    ]
    
    for mode in modes:
        print(f"Mode: {mode.value}")
        print(f"  (Would retrieve memories using {mode.value} approach)")
    
    print("\n📊 Recall Stats:")
    stats = engine.get_recall_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
