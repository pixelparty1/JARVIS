"""
Vector Store - Semantic Search Engine

Manages embeddings and similarity search for intelligent memory retrieval.
Stores text embeddings in FAISS for fast similarity matching.
"""

import json
import os
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import numpy as np

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("⚠️ FAISS not installed. Install with: pip install faiss-cpu")


@dataclass
class Memory:
    """Represents a stored memory item."""
    id: str
    content: str
    timestamp: str
    embedding: Optional[List[float]] = None
    tags: List[str] = None
    category: str = "general"
    importance: float = 0.5  # 0-1 scale
    source: str = "user_input"
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}


class VectorStore:
    """
    Semantic search engine using FAISS.
    
    Converts text to embeddings and performs similarity search.
    """
    
    def __init__(self, embedding_dim: int = 384, 
                 use_mock_embeddings: bool = False):
        """
        Initialize vector store.
        
        Args:
            embedding_dim: Dimension of embeddings (default 384 for sentence-transformers)
            use_mock_embeddings: Use fake embeddings if no real embedder available
        """
        self.embedding_dim = embedding_dim
        self.use_mock = use_mock_embeddings
        self.memories: Dict[str, Memory] = {}
        self.memory_list: List[Memory] = []
        self.embedding_index = None
        self.id_mapping = {}  # Map index -> memory id
        
        # Initialize FAISS index
        self._init_faiss()
        
        # Try to load embedding model
        self.embedder = None
        if not use_mock_embeddings:
            self._load_embedder()
    
    def _init_faiss(self):
        """Initialize FAISS index."""
        if FAISS_AVAILABLE:
            # Use IndexFlatL2 for exact Euclidean search
            self.embedding_index = faiss.IndexFlatL2(self.embedding_dim)
        else:
            self.embedding_index = None
    
    def _load_embedder(self):
        """Load embedding model."""
        try:
            from sentence_transformers import SentenceTransformer
            self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
            print("✅ Embedding model loaded: all-MiniLM-L6-v2")
        except ImportError:
            print("⚠️ sentence-transformers not installed.")
            print("   Install with: pip install sentence-transformers")
            self.use_mock = True
        except Exception as e:
            print(f"⚠️ Could not load embedder: {e}")
            self.use_mock = True
    
    def get_embedding(self, text: str) -> np.ndarray:
        """
        Convert text to embedding vector.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        if self.use_mock or self.embedder is None:
            return self._mock_embedding(text)
        
        try:
            embedding = self.embedder.encode(text)
            return embedding.astype('float32')
        except Exception as e:
            print(f"❌ Embedding error: {e}")
            return self._mock_embedding(text)
    
    def _mock_embedding(self, text: str) -> np.ndarray:
        """
        Create mock embedding based on text hash.
        
        For testing without sentence-transformers.
        """
        # Use hash to create deterministic embedding
        hash_val = hash(text.lower())
        np.random.seed(abs(hash_val) % (2**32))
        return np.random.randn(self.embedding_dim).astype('float32')
    
    def add_memory(self, memory: Memory) -> bool:
        """
        Add memory to store with embedding.
        
        Args:
            memory: Memory object to store
            
        Returns:
            Success flag
        """
        try:
            # Generate embedding if not provided
            if memory.embedding is None:
                embedding = self.get_embedding(memory.content)
                memory.embedding = embedding.tolist()
            else:
                embedding = np.array(memory.embedding, dtype='float32')
            
            # Store memory
            self.memories[memory.id] = memory
            self.memory_list.append(memory)
            
            # Add to FAISS index
            if self.embedding_index is not None:
                idx = len(self.memory_list) - 1
                self.id_mapping[idx] = memory.id
                
                # Reshape for FAISS (1, dim)
                embedding_reshaped = embedding.reshape(1, -1)
                self.embedding_index.add(embedding_reshaped)
            
            return True
            
        except Exception as e:
            print(f"❌ Error adding memory: {e}")
            return False
    
    def search(self, query: str, k: int = 5, 
               threshold: float = 0.0) -> List[Tuple[Memory, float]]:
        """
        Search for similar memories.
        
        Args:
            query: Search query text
            k: Number of results
            threshold: Minimum similarity (0-1)
            
        Returns:
            List of (Memory, similarity) tuples
        """
        if not self.memory_list:
            return []
        
        try:
            # Get query embedding
            query_embedding = self.get_embedding(query)
            query_embedding = query_embedding.reshape(1, -1)
            
            if self.embedding_index is None:
                # Fallback: simple similarity search
                return self._simple_search(query_embedding, k, threshold)
            
            # FAISS search
            distances, indices = self.embedding_index.search(query_embedding, min(k, len(self.memory_list)))
            
            results = []
            for i, dist in zip(indices[0], distances[0]):
                if i < 0:  # Invalid index
                    continue
                
                memory_id = self.id_mapping.get(i)
                if memory_id and memory_id in self.memories:
                    memory = self.memories[memory_id]
                    
                    # Convert L2 distance to similarity (0-1)
                    # L2 distance: 0 = identical, larger = more different
                    similarity = 1.0 / (1.0 + float(dist))
                    
                    if similarity >= threshold:
                        results.append((memory, similarity))
            
            # Sort by similarity descending
            results.sort(key=lambda x: x[1], reverse=True)
            return results
            
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []
    
    def _simple_search(self, query_embedding: np.ndarray, 
                      k: int, threshold: float) -> List[Tuple[Memory, float]]:
        """
        Simple similarity search without FAISS (fallback).
        """
        results = []
        
        for memory in self.memory_list:
            if memory.embedding is None:
                continue
            
            memory_emb = np.array(memory.embedding, dtype='float32')
            
            # Cosine similarity
            query_norm = query_embedding / (np.linalg.norm(query_embedding) + 1e-10)
            memory_norm = memory_emb / (np.linalg.norm(memory_emb) + 1e-10)
            
            similarity = float(np.dot(query_norm, memory_norm))
            
            if similarity >= threshold:
                results.append((memory, similarity))
        
        # Sort by similarity
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:k]
    
    def search_by_tags(self, tags: List[str], k: int = 10) -> List[Memory]:
        """
        Search memories by tags.
        
        Args:
            tags: Tags to search for
            k: Max results
            
        Returns:
            List of memories with matching tags
        """
        results = []
        tag_set = set(tags)
        
        for memory in self.memory_list:
            memory_tags = set(memory.tags or [])
            if memory_tags & tag_set:  # Intersection
                results.append(memory)
        
        # Sort by importance
        results.sort(key=lambda x: x.importance, reverse=True)
        return results[:k]
    
    def search_by_category(self, category: str, k: int = 10) -> List[Memory]:
        """
        Search memories by category.
        
        Args:
            category: Category to search
            k: Max results
            
        Returns:
            List of memories in category
        """
        results = [
            m for m in self.memory_list 
            if m.category == category
        ]
        
        # Sort by timestamp descending (newest first)
        results.sort(key=lambda x: x.timestamp, reverse=True)
        return results[:k]
    
    def get_memory(self, memory_id: str) -> Optional[Memory]:
        """Get specific memory by ID."""
        return self.memories.get(memory_id)
    
    def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update an existing memory.
        
        Args:
            memory_id: ID of memory to update
            updates: Dict of fields to update
            
        Returns:
            Success flag
        """
        if memory_id not in self.memories:
            return False
        
        memory = self.memories[memory_id]
        
        # Update fields
        for key, value in updates.items():
            if hasattr(memory, key):
                setattr(memory, key, value)
        
        # If content changed, recompute embedding
        if 'content' in updates:
            embedding = self.get_embedding(memory.content)
            memory.embedding = embedding.tolist()
        
        return True
    
    def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a memory.
        
        Note: Doesn't remove from FAISS index (rebuild needed).
        """
        if memory_id not in self.memories:
            return False
        
        memory = self.memories.pop(memory_id)
        self.memory_list = [m for m in self.memory_list if m.id != memory_id]
        return True
    
    def clear_all(self):
        """Clear all memories and rebuild index."""
        self.memories.clear()
        self.memory_list.clear()
        self.id_mapping.clear()
        self._init_faiss()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics."""
        categories = {}
        for memory in self.memory_list:
            cat = memory.category
            categories[cat] = categories.get(cat, 0) + 1
        
        avg_importance = (
            sum(m.importance for m in self.memory_list) / len(self.memory_list)
            if self.memory_list else 0
        )
        
        return {
            'total_memories': len(self.memory_list),
            'dimensions': self.embedding_dim,
            'categories': categories,
            'average_importance': avg_importance,
            'faiss_available': FAISS_AVAILABLE,
            'using_mock_embeddings': self.use_mock,
            'index_status': 'ready' if self.embedding_index else 'unavailable'
        }
    
    def export_memories(self) -> List[Dict[str, Any]]:
        """Export all memories as JSON-serializable dicts."""
        export_list = []
        
        for memory in self.memory_list:
            data = asdict(memory)
            # Embedding stored as list for JSON
            export_list.append(data)
        
        return export_list
    
    def save_to_file(self, filepath: str) -> bool:
        """
        Save all memories to JSON file.
        
        Args:
            filepath: Path to save to
            
        Returns:
            Success flag
        """
        try:
            export_data = {
                'timestamp': datetime.now().isoformat(),
                'version': '1.0',
                'stats': self.get_stats(),
                'memories': self.export_memories()
            }
            
            os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
            
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving memories: {e}")
            return False
    
    def load_from_file(self, filepath: str) -> bool:
        """
        Load memories from JSON file.
        
        Args:
            filepath: Path to load from
            
        Returns:
            Success flag
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            self.clear_all()
            
            for mem_data in data.get('memories', []):
                memory = Memory(**mem_data)
                self.add_memory(memory)
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading memories: {e}")
            return False


# Example usage
if __name__ == "__main__":
    print("🧠 Vector Store Test\n")
    
    # Create store
    store = VectorStore(use_mock_embeddings=True)
    
    # Add some memories
    memories_data = [
        ("Python is great for AI", "programming", ["python", "ai"]),
        ("I love traveling to Japan", "travel", ["travel", "japan"]),
        ("SQL is used for databases", "programming", ["database", "sql"]),
        ("Machine learning uses vectors", "ai", ["ml", "vectors"]),
    ]
    
    for i, (content, category, tags) in enumerate(memories_data):
        mem = Memory(
            id=f"mem_{i}",
            content=content,
            timestamp=datetime.now().isoformat(),
            category=category,
            tags=tags,
            importance=0.7
        )
        store.add_memory(mem)
    
    print("✓ Added 4 memories\n")
    
    # Search
    print("🔍 Search Test: 'Python programming'")
    results = store.search("Python programming", k=3)
    for mem, sim in results:
        print(f"  {mem.content} (similarity: {sim:.2f})")
    
    print("\n📊 Store Stats:")
    stats = store.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
