# JARVIS Knowledge System Guide 📚

## Overview

Phase 5 transforms JARVIS into an intelligent knowledge management system. The Memory System combines semantic search, knowledge graphs, and Groq reasoning to create a "second brain" that remembers, learns, and makes connections.

**Key Capabilities:**
- 🔍 **Semantic Search** - Find memories by meaning, not keywords
- 🧠 **Knowledge Graphs** - Model relationships between concepts
- 🤖 **Groq Reasoning** - Intelligent synthesis and analysis
- 📥 **Automatic Ingestion** - Learn from conversations
- 💾 **Persistent Storage** - Everything saved locally
- 🔗 **Smart Connections** - Auto-detect relationships

---

## Architecture

### System Components

```
┌──────────────────────────────────────────────────┐
│           JARVIS CONVERSATION LAYER               │
│        (User Interaction / Voice Input)           │
└──────────────────────┬───────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────┐
│      Knowledge Ingestion Pipeline                │
│  - Entity extraction                             │
│  - Relationship detection                        │
│  - Importance scoring                            │
├──────────────────────────────────────────────────┤
│  IngestionAnalyzer → Memory Analysis             │
└──────────────┬──────────────────────┬────────────┘
               │                      │
     ┌─────────▼────────┐    ┌────────▼─────────┐
     │  Vector Store    │    │ Knowledge Graph  │
     │  (FAISS)         │    │ (NetworkX)       │
     │                  │    │                  │
     │ - Embeddings     │    │ - Nodes          │
     │ - Similarity     │    │ - Edges          │
     │ - Fast Search    │    │ - Path Finding   │
     └─────────┬────────┘    └────────┬─────────┘
               │                      │
               └──────┬───────────────┘
                      │
        ┌─────────────▼──────────────┐
        │    Recall Engine           │
        │                            │
        │ - Semantic retrieval       │
        │ - Graph traversal          │
        │ - Hybrid search            │
        │ - Groq synthesis           │
        └─────────────┬──────────────┘
                      │
        ┌─────────────▼──────────────┐
        │    Memory Manager          │
        │                            │
        │ - Orchestration            │
        │ - Priority scoring         │
        │ - Lifecycle management     │
        │ - Import/export            │
        └─────────────┬──────────────┘
                      │
        ┌─────────────▼──────────────┐
        │     JARVIS Response        │
        │  (Context-Aware Answer)    │
        └───────────────────────────┘
```

### Core Modules

#### 1. **vector_store.py** - Semantic Search
Stores memories as embeddings using FAISS for fast similarity search.

**Key Classes:**
- `Memory` - Individual memory with embedding
- `VectorStore` - FAISS-backed search engine

**Key Methods:**
```python
add_memory(memory)           # Store new memory with embedding
search(query, k=5)           # Find semantically similar memories
search_by_tags(tags)         # Filter by tags
search_by_category(cat)      # Filter by category
```

**Performance:**
- Vector dimension: 384 (sentence-transformers)
- Search speed: ~100ms for 10K memories
- Index type: FAISS IndexFlatL2

---

#### 2. **knowledge_graph.py** - Relationship Modeling
Uses NetworkX to model concepts and their relationships.

**Key Classes:**
- `GraphNode` - Concept or entity
- `GraphEdge` - Relationship between nodes
- `KnowledgeGraph` - Relationship manager

**Relationship Types:**
- `RELATED_TO` - General association
- `USED_FOR` - Tool/technology purpose
- `PART_OF` - Hierarchical containment
- `CAUSES` - Causal relationship
- `SIMILAR_TO` - Similarity
- `DEPENDS_ON` - Dependency
- `MENTIONED_IN` - Referenced in
- `CREATED_BY` - Authorship
- `KNOWS` - Social connections
- `INTERESTED_IN` - Interest areas

**Key Methods:**
```python
add_node(node)               # Add concept
add_edge(edge)               # Add relationship
get_neighbors(node_id)       # Connected concepts
find_path(source, target)    # Shortest path (Dijkstra)
find_related(node_id, depth) # Concepts within N hops
suggest_connections(node_id) # Recommend new relationships
```

**Algorithms:**
- Shortest path: Dijkstra via NetworkX
- Suggestions: Common neighbor analysis
- Traversal: BFS for related discovery

---

#### 3. **summarizer.py** - Information Compression
Uses Groq AI to intelligently compress information.

**Key Classes:**
- `Summarizer` - Text compression engine
- `SmartNoter` - Structured note system
- `SummaryResult` - Compression with metadata

**Key Methods:**
```python
summarize(text, max_chars=500)      # Compress text
extract_points(text)                # Key points
batch_summarize(texts)              # Multiple compressions
create_note(content, category)      # Note with auto-summary
search_notes(query)                 # Find notes
```

**Compression:**
- Typical ratio: 2-3x (400 chars → 130-200 chars)
- Preserves key concepts
- Auto-tags generated

---

#### 4. **recall_engine.py** - Intelligent Retrieval
Combines all systems to retrieve context-aware memories.

**Recall Modes:**
- `SEMANTIC` - Vector similarity search
- `GRAPH` - Relationship-based traversal
- `HYBRID` - Combined scoring
- `ASSOCIATIVE` - Loose connections
- `CONTEXTUAL` - Time/category aware

**Key Methods:**
```python
await recall(query, mode=RecallMode.HYBRID, limit=5)
```

**Process:**
1. Query enters recall engine
2. Vector store: Find semantically similar memories
3. Knowledge graph: Discover related concepts
4. Combine results with relevance scoring
5. Groq enhancement: Synthesize intelligent answer
6. Return context + reasoning

---

#### 5. **memory_manager.py** - Central Orchestration
Coordinates all memory components with lifecycle management.

**Key Classes:**
- `MemoryManager` - Main coordinator
- `MemoryIngestionRequest` - Ingest request

**Key Methods:**
```python
await ingest_memory(request)         # Add new memory with processing
await retrieve_memory(query, limit)  # Smart retrieval
update_memory_priority(id, priority) # Adjust importance
access_memory(id)                    # Track access
prune_memory(older_than_days)        # Cleanup old memories
export_memories(filepath)            # Save to JSON
import_memories(filepath)            # Load from JSON
```

**Features:**
- Automatic summarization
- Tag generation
- Relationship detection
- Priority scoring
- Lifecycle management

---

#### 6. **knowledge_ingestion.py** - Automatic Processing
Analyzes conversations for memory-worthy content.

**Key Classes:**
- `IngestionAnalyzer` - Content analysis
- `KnowledgeIngestionPipeline` - Processing pipeline
- `Entity` - Extracted concept
- `ExtractedRelationship` - Detected connection

**Process:**
1. Monitor conversation stream
2. Extract entities and relationships
3. Score importance
4. Auto-tag with topics
5. Create memory entries
6. Build graph connections

**Extraction:**
- Technology mentions (Python, ML, etc.)
- Learning signals ("learned", "discovered")
- Named entities (capitalized names)
- Relationships (uses, helps, is, works_with)

---

## Usage Examples

### Basic Memory Storage

```python
from memory_system.memory_manager import MemoryManager, MemoryIngestionRequest, MemoryPriority

# Initialize manager
manager = MemoryManager(vector_store, knowledge_graph, summarizer, recall_engine)

# Create memory request
request = MemoryIngestionRequest(
    content="Learned about transformer architectures today",
    category="learning",
    priority=MemoryPriority.HIGH,
    tags=["ml", "transformers", "ai"]
)

# Ingest memory
result = await manager.ingest_memory(request)
print(f"Memory stored: {result['memory_id']}")
```

### Semantic Search

```python
# Find similar memories
results = vector_store.search("neural networks", k=5)

for memory, similarity in results:
    print(f"Memory: {memory.content[:50]}")
    print(f"Similarity: {similarity:.1%}")
```

### Knowledge Graph Exploration

```python
# Add concepts
kg.add_node(GraphNode(id="python", label="Python", type="language"))
kg.add_node(GraphNode(id="ml", label="Machine Learning", type="domain"))

# Connect them
edge = GraphEdge("python", "ml", RelationType.USED_FOR)
kg.add_edge(edge)

# Find paths
path = kg.find_path("python", "deep_learning")  # Returns: python → ml → nn → deep_learning

# Get suggestions
suggestions = kg.suggest_connections("python")  # Recommends related nodes
```

### Intelligent Recall

```python
from memory_system.recall_engine import RecallMode

# Query with automatic enhancement
result = await recall_engine.recall(
    query="How does machine learning relate to my past projects?",
    mode=RecallMode.HYBRID,
    enhance_with_groq=True
)

print(f"Found {len(result.retrieved_memories)} relevant memories")
print(f"Reasoning: {result.reasoning}")
print(f"Enhanced answer:\n{result.enhanced_answer}")
```

### Automatic Ingestion

```python
from memory_system.knowledge_ingestion import KnowledgeIngestionPipeline

pipeline = KnowledgeIngestionPipeline(memory_manager, analyzer)

# Process conversation message
result = await pipeline.process_message(
    "Today I implemented a REST API in Python",
    source="conversation",
    auto_ingest=True
)

if result['status'] == 'success':
    print(f"Memory created: {result['memory_id']}")
    print(f"Entities found: {result['analysis']['entities']}")
```

### Export/Import

```python
# Export all memories
json_data = manager.export_memories("backup.json")

# Import from backup
manager.import_memories("backup.json")
```

---

## Integration with JARVIS

### Phase 5 Integration Points

#### 1. **Conversation Hook**
```python
# In orchestrator.py
async def _process_user_message(self, message):
    # Process memory ingestion
    await self.ingestion_pipeline.process_message(
        message,
        source="user_input"
    )
```

#### 2. **Context Retrieval**
```python
# In brain.py (ask_groq)
async def ask_groq(self, prompt, add_context=True):
    context = ""
    if add_context:
        # Recall related memories
        result = await self.recall_engine.recall(
            query=prompt,
            limit=3
        )
        context = format_memories(result.retrieved_memories)
    
    # Enhance prompt with context
    enhanced_prompt = f"{context}\n\nUser: {prompt}"
    return await groq_call(enhanced_prompt)
```

#### 3. **Proactive Knowledge Updates**
```python
# In predictor.py
async def _learn_from_patterns(self):
    # Store behavior patterns as memories
    for pattern in self.patterns:
        await self.memory_manager.ingest_memory(
            MemoryIngestionRequest(
                content=f"Your typical pattern: {pattern.description}",
                category="patterns",
                priority=MemoryPriority.NORMAL
            )
        )
```

---

## Configuration

### Environment Variables
```bash
GROQ_API_KEY=gsk_xxxx          # Groq AI API key
MEMORY_CHUNK_SIZE=500           # Max chars for summarization
FAISS_BATCH_SIZE=100            # FAISS indexing batch
RECALL_LIMIT=10                 # Default recall results
```

### Vector Store Setup
```python
from memory_system.vector_store import VectorStore

# Standard setup
store = VectorStore(use_mock_embeddings=False)

# Development setup (no model download)
store = VectorStore(use_mock_embeddings=True)

# Load from file
store.load_from_file("memory_vectors.json")
```

### Knowledge Graph Setup
```python
from memory_system.knowledge_graph import KnowledgeGraph

kg = KnowledgeGraph()

# Load from file
kg.load_from_file("knowledge_graph.json")

# Get statistics
stats = kg.get_graph_stats()
print(f"Nodes: {stats['total_nodes']}, Edges: {stats['total_edges']}")
```

---

## Performance Tuning

### Vector Store Optimization
```python
# Increase FAISS probe count for higher accuracy
store.vector_index.nprobe = 10  # Default: 1

# Use GPU acceleration (if available)
import faiss
faiss.omp_set_num_threads(8)
```

### Knowledge Graph Optimization
```python
# Limit graph depth for faster traversal
neighbors = kg.get_neighbors(node_id, max_depth=2)

# Use indexed lookups
nodes_by_type = kg.get_nodes_by_type("language")
```

### Memory Management
```python
# Prune old memories periodically
pruned = manager.prune_memory(
    older_than_days=90,
    min_priority=MemoryPriority.LOW
)

# Archive less important memories
for mem_id in old_memories:
    manager.update_memory_priority(
        mem_id,
        MemoryPriority.ARCHIVED
    )
```

---

## Troubleshooting

### Issue: Embeddings Taking Too Long to Load

**Solution:** Use mock embeddings for development
```python
store = VectorStore(use_mock_embeddings=True)
```

### Issue: FAISS Not Available

**Solution:** Vectorstore falls back to cosine similarity
```python
# Automatic fallback - no action needed
results = store.search(query)  # Uses cosine if FAISS unavailable
```

### Issue: Knowledge Graph Getting Too Large

**Solution:** Prune low-importance nodes
```python
kg.nodes = {
    k: v for k, v in kg.nodes.items()
    if v.importance >= 0.3
}
```

### Issue: Recall Engine Slow

**Solution:** Limit recalled memories and depth
```python
result = await recall_engine.recall(
    query,
    limit=3,  # Reduce from default 10
    mode=RecallMode.SEMANTIC  # Skip expensive graph traversal
)
```

---

## API Reference

### MemoryManager

```python
class MemoryManager:
    async def ingest_memory(request: MemoryIngestionRequest) → Dict
    async def retrieve_memory(query: str, limit: int, enhance: bool) → Dict
    def update_memory_priority(memory_id: str, priority: MemoryPriority) → bool
    def access_memory(memory_id: str) → Optional[Dict]
    def prune_memory(older_than_days: int, min_priority: MemoryPriority) → int
    def export_memories(filepath: str = None) → str
    def import_memories(filepath: str) → int
    def get_memory_stats() → Dict[str, Any]
```

### RecallEngine

```python
class RecallEngine:
    async def recall(query: str, mode: RecallMode, limit: int, enhance_with_groq: bool) → RecallResult
    def get_recall_stats() → Dict[str, Any]
```

### VectorStore

```python
class VectorStore:
    def add_memory(memory: Memory) → None
    def search(query: str, k: int, threshold: float) → List[Tuple[Memory, float]]
    def search_by_tags(tags: List[str]) → List[Memory]
    def search_by_category(category: str) → List[Memory]
    def save_to_file(filepath: str) → None
    def load_from_file(filepath: str) → None
    def get_stats() → Dict[str, Any]
```

### KnowledgeGraph

```python
class KnowledgeGraph:
    def add_node(node: GraphNode) → None
    def add_edge(edge: GraphEdge) → None
    def get_neighbors(node_id: str) → List[Tuple[str, str]]
    def find_path(source: str, target: str) → List[str]
    def find_related(node_id: str, depth: int) → List[Tuple[str, int]]
    def suggest_connections(node_id: str) → List[Tuple[str, float]]
    def save_to_file(filepath: str) → None
    def load_from_file(filepath: str) → None
    def get_graph_stats() → Dict[str, Any]
```

---

## Data Format

### Memory JSON Structure
```json
{
  "id": "mem_abc123",
  "content": "Original full content here",
  "summary": "Compressed version",
  "tags": ["python", "ai", "learning"],
  "category": "learning",
  "importance": 0.8,
  "embedding": [0.123, 0.456, ...],
  "timestamp": "2024-01-15T10:30:00",
  "source": "conversation",
  "metadata": {}
}
```

### Knowledge Graph JSON Structure
```json
{
  "nodes": [
    {
      "id": "python",
      "label": "Python",
      "type": "language",
      "description": "Programming language",
      "importance": 0.9
    }
  ],
  "edges": [
    {
      "source_id": "python",
      "target_id": "ml",
      "relation_type": "USED_FOR",
      "weight": 0.8
    }
  ]
}
```

---

## Next Steps

### Phase 5 Continuation
1. ✅ Vector store (complete)
2. ✅ Knowledge graph (complete)
3. ✅ Summarizer (complete)
4. ✅ Recall engine (complete)
5. ✅ Memory manager (complete)
6. ✅ Knowledge ingestion (complete)
7. 🔄 **Integration with JARVIS** (in progress)
8. 🔄 **Example queries and scenarios** (in progress)

### Future Enhancements
- Multi-modal embedding (text + images + audio)
- Causal relationship discovery
- Temporal memory organization
- Social network analysis
- Personalized learning recommendations

---

## Support & Resources

**Files:**
- Core modules: `memory_system/[vector_store|knowledge_graph|summarizer|recall_engine|memory_manager|knowledge_ingestion].py`
- Integration: `jarvis/orchestrator.py`, `jarvis/brain.py`

**Testing:**
- Run individual test suites: `python memory_system/<module>.py`
- Integration tests: `tests/memory_integration_test.py`

**Documentation:**
- This guide (MEMORY_GUIDE.md)
- Docstrings in each module
- Example code in main blocks of each file

---

**Memory System Built with ❤️ for JARVIS | Phase 5**
