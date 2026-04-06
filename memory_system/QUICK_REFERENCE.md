"""
JARVIS Memory System - Quick Reference Card

Fast lookup for common operations
"""

QUICK_REFERENCE = """
╔═══════════════════════════════════════════════════════════════════════════╗
║                    JARVIS MEMORY SYSTEM QUICK REFERENCE                   ║
╚═══════════════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. SETUP & INITIALIZATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Quick Setup (Production)
from memory_system.integration import setup_memory_system
integration = setup_memory_system(orchestrator, use_mock_embeddings=False)

# Quick Setup (Testing)
integration = setup_memory_system(orchestrator, use_mock_embeddings=True)

# Access Components
memory_manager = integration.memory_manager
vector_store = memory_manager.vector_store
knowledge_graph = memory_manager.knowledge_graph
recall_engine = memory_manager.recall_engine


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2. INGESTING MEMORIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Basic Ingestion
from memory_system import MemoryIngestionRequest, MemoryPriority

request = MemoryIngestionRequest(
    content="Your content here",
    category="learning",
    priority=MemoryPriority.HIGH,
    tags=["tag1", "tag2"]
)

result = await memory_manager.ingest_memory(request)
memory_id = result['memory_id']

# Priority Levels
MemoryPriority.CRITICAL = 5  # Most important
MemoryPriority.HIGH = 4
MemoryPriority.NORMAL = 3    # Default
MemoryPriority.LOW = 2
MemoryPriority.ARCHIVED = 1  # Least important

# Auto-ingestion from Conversation
result = await integration.process_user_message(message)


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
3. RETRIEVING MEMORIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Simple Search (Hybrid)
result = await memory_manager.retrieve_memory(
    query="How do I use Python?",
    limit=5,
    enhance=True  # Use Groq for synthesis
)

# Direct Vector Search
results = vector_store.search("python programming", k=5)
for memory, similarity in results:
    print(f"Content: {memory.content}")
    print(f"Similarity: {similarity:.1%}")

# Specific Recall Modes
from memory_system import RecallMode

result = await recall_engine.recall(
    query="Your question",
    mode=RecallMode.HYBRID,           # SEMANTIC, GRAPH, HYBRID, ASSOCIATIVE, CONTEXTUAL
    limit=3,
    enhance_with_groq=True
)

# Graph Search
neighbors = knowledge_graph.get_neighbors("python")
path = knowledge_graph.find_path("python", "machine_learning")
related = knowledge_graph.find_related("python", depth=2)


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
4. WORKING WITH THE KNOWLEDGE GRAPH
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Add Concepts
from memory_system import GraphNode, GraphEdge, RelationType

node = GraphNode(id="python", label="Python", type="language")
knowledge_graph.add_node(node)

# Create Relationships
edge = GraphEdge(
    source_id="python",
    target_id="ml",
    relation_type=RelationType.USED_FOR,
    weight=0.9
)
knowledge_graph.add_edge(edge)

# Relationship Types
RelationType.RELATED_TO      # General association
RelationType.USED_FOR        # Purpose
RelationType.PART_OF         # Composition
RelationType.CAUSES          # Causation
RelationType.SIMILAR_TO      # Similarity
RelationType.DEPENDS_ON      # Dependency
RelationType.MENTIONED_IN    # Reference
RelationType.CREATED_BY      # Authorship
RelationType.KNOWS           # Social
RelationType.INTERESTED_IN   # Interest

# Traversal
path = knowledge_graph.find_path("source", "target")
suggestions = knowledge_graph.suggest_connections("node_id")


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
5. ENHANCING GROQ RESPONSES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Auto-inject Context
response = await integration.enhance_groq_response(
    prompt="Your question",
    brain=brain_instance
)

# Manual Context Injection
enhanced_prompt = await integration.inject_memory_context(
    prompt="Your question",
    memory_limit=3
)
response = await brain.ask_groq(enhanced_prompt)


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
6. MEMORY MANAGEMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Update Priority
memory_manager.update_memory_priority(memory_id, MemoryPriority.HIGH)

# Track Access (updates last_accessed and access_count)
metadata = memory_manager.access_memory(memory_id)

# Prune Old Memories
pruned = memory_manager.prune_memory(older_than_days=90, min_priority=MemoryPriority.LOW)

# Export All
json_str = memory_manager.export_memories("backup.json")

# Import All
count = memory_manager.import_memories("backup.json")

# Statistics
stats = memory_manager.get_memory_stats()
print(f"Total memories: {stats['total_memories']}")
print(f"By priority: {stats['priority_distribution']}")
print(f"By category: {stats['category_distribution']}")


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
7. SUMMARIZATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Summarize Text
from memory_system import Summarizer
summarizer = Summarizer()

result = summarizer._fallback_summarize(
    text="Long text here",
    max_chars=200,
    max_points=3
)
print(result.summary)
print(result.key_points)
print(result.tags)
print(f"Compression: {result.compression_ratio}x")

# Batch Summarize
results = summarizer.batch_summarize(text_list)

# Create Note
note = summarizer.create_note(
    content="Your content",
    category="learning"
)

# Search Notes
notes = summarizer.search_notes("query")


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
8. AUTOMATIC INGESTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Analyze Content for Memory-worthiness
from memory_system import IngestionAnalyzer
analyzer = IngestionAnalyzer()

result = await analyzer.analyze_content("Your text")
print(f"Memory-worthy: {result['is_memory_worthy']}")
print(f"Importance: {result['importance_score']}")
print(f"Entities: {result['entities']}")
print(f"Category: {result['suggested_category']}")

# Process Through Pipeline
from memory_system import KnowledgeIngestionPipeline
pipeline = KnowledgeIngestionPipeline(memory_manager, analyzer)

result = await pipeline.process_message(
    message="Your message",
    source="conversation",
    auto_ingest=True
)


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
9. MONITORING & HEALTH
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Health Check
from memory_system.integration import MemorySystemHealthCheck

status = MemorySystemHealthCheck.get_system_status(memory_manager)
print(f"Overall: {status['overall_status']}")
print(f"Components: {status['component_checks']}")

# Integration Stats
stats = integration.get_integration_stats()
print(f"Messages processed: {stats['messages_processed']}")
print(f"Memories ingested: {stats['memories_ingested']}")

# Component Stats
vector_stats = vector_store.get_stats()
kg_stats = knowledge_graph.get_graph_stats()
recall_stats = recall_engine.get_recall_stats()


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
10. COMMON WORKFLOWS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WORKFLOW A: User Asks Question with Context
1. integration.process_user_message(question)
   → Auto-ingests question as memory
   → Retrieves related memories
   → Gets Groq response with context
   → Returns enhanced answer

WORKFLOW B: Store Learning Session
1. Create MemoryIngestionRequest(category="learning", priority=HIGH)
2. memory_manager.ingest_memory(request)
   → Summarizes content
   → Generates tags
   → Stores in vector store
   → Creates graph nodes
   → Links to related concepts

WORKFLOW C: Project Management
1. Start: ingest_memory(content="Project X", category="project")
2. During: ingest_memory(content="Progress note", linked_project=X)
3. Recall: retrieve_memory("Project X status")
   → Gets all project memories
   → Synthesizes summary
   → Returns with graph context

WORKFLOW D: Pattern Recognition
1. System ingests multiple memories over time
2. memory_manager.recall_engine.recall(query, mode=HYBRID)
   → Searches semantically similar
   → Finds graph paths between concepts
   → Groq synthesizes patterns
   → Returns insight


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
11. PERFORMANCE TIPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Use RecallMode.SEMANTIC for fast retrieval
✅ Limit recall results (default 5, rarely need >10)
✅ Use RecallMode.HYBRID for best quality
✅ Use SEMANTIC for time-sensitive operations
✅ Prune old memories regularly (90+ days old)
✅ Use mock embeddings for testing
✅ Save/load vector store for persistence
✅ Export memories before major updates


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
12. TROUBLESHOOTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Q: Embeddings slow?
A: Use use_mock_embeddings=True for dev/testing

Q: FAISS not available?
A: Automatically falls back to cosine similarity

Q: Memory store too large?
A: Run memory_manager.prune_memory() to clean up

Q: Recall responses slow?
A: Use RecallMode.SEMANTIC instead of HYBRID
   Or reduce limit parameter

Q: Graph getting huge?
A: Remove low-importance nodes or prune old memories

Q: How to backup?
A: memory_manager.export_memories("path.json")

Q: How to reset?
A: Delete memory_index, re-export/import as needed


╔═══════════════════════════════════════════════════════════════════════════╗
║                    JARVIS MEMORY SYSTEM READY TO USE! 🚀                  ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

if __name__ == "__main__":
    print(QUICK_REFERENCE)
