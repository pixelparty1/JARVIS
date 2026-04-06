"""
JARVIS Memory System - Example Scenarios

Demonstrates practical use cases and complete workflows
for the knowledge system in real conversations.
"""


# ============================================================================
# SCENARIO 1: Learning & Knowledge Retention
# ============================================================================

SCENARIO_1_LEARNING = """
USER: "I just learned about transformer architectures - they're like 
attention-based neural networks that revolutionized NLP. Each transformer 
has an encoder and decoder stack with multi-head attention mechanisms."

SYSTEM PROCESS:
1. IngestionAnalyzer extracts:
   - Entities: ["transformers", "neural networks", "NLP", "attention", "encoder", "decoder"]
   - Relationships: transformers → USED_FOR → NLP, transformers → PART_OF → neural networks
   - Importance: 0.85 (learning signal + multiple entities)
   - Tags: ["ml", "transformers", "attention", "nlp", "learning"]

2. MemoryManager:
   - Summarizes if needed (already short)
   - Stores in VectorStore with embedding
   - Creates graph nodes: Transformers, Attention, NLP
   - Links to existing nodes about neural networks
   
3. Knowledge Graph:
   - Node: "Transformers" (type: concept, importance: 0.85)
   - Node: "Attention" (type: concept)
   - Node: "NLP" (type: domain)
   - Edges: Transformers → USED_FOR → NLP, Transformers → PART_OF → NN

4. Vector Store:
   - Memory ID: mem_a1b2c3d4
   - Content: "Transformers are attention-based neural networks..."
   - Embedding: [0.123, 0.456, ...]
   - Embedding similarity matches other ML concepts

FUTURE QUERIES:
USER: "How did that attention mechanism work again?"

JARVIS RECALLS:
- Semantic search: ✅ Finds transformer memory (0.92 similarity)
- Graph search: ✅ Connects from Attention node
- Answer: "From your notes, Transformers use multi-head attention 
  mechanisms in encoder/decoder stacks for parallel processing..."
"""


# ============================================================================
# SCENARIO 2: Project Management & Context Awareness
# ============================================================================

SCENARIO_2_PROJECTS = """
USER (Monday): "Starting a new project - building a recommendation system 
using collaborative filtering. I'll be using Python, scikit-learn, and 
storing data in MongoDB."

SYSTEM INGESTION:
1. Extracted:
   - Project: Recommendation System
   - Technologies: Python, scikit-learn, MongoDB
   - Relationships: Python → USED_FOR → ML, scikit-learn → PART_OF → ML
   - Importance: HIGH (project initiation)

2. Knowledge Graph:
   - Node: "RecommendSys_2024" (type: project, importance: 0.9)
   - Connects to: Python, scikit-learn, MongoDB, collaborative_filtering

USER (Wednesday): "The collaborative filtering model is giving bad results 
on cold start problems."

SYSTEM FINDS:
1. Graph traversal: RecommendSys_2024 → collaborative_filtering → cold_start
2. Knowledge search: "Have you dealt with cold start before?"
3. Contextual response: "This is your recommendation project. Cold start 
   is common with collaborative filtering. Have you considered hybrid 
   approaches combining content-based and collaborative methods?"

USER (Friday): "Need to summarize progress for the team"

JARVIS SYNTHESIZES:
1. Searches all memories tagged "RecommendSys_2024"
2. Finds: Monday's plan, Wed debugging session, Thu implementation notes
3. Groq synthesis: "This week you've built a Python-based recommendation 
   system with scikit-learn. You're currently debugging cold start 
   problems in the collaborative filtering model. Considered: hybrid 
   approaches combining content + collaborative methods."
"""


# ============================================================================
# SCENARIO 3: Decision Support & Pattern Recognition
# ============================================================================

SCENARIO_3_PATTERNS = """
USER: "I've been having trouble focusing in the mornings lately"

JARVIS RECALLS (from previous memories):
- Apr 12: "Started going to bed later, been coding until midnight"
- Apr 15: "Noticed I'm tired, started afternoon slump around 3pm"
- Apr 18: "Been drinking less water, more caffeine"
- Apr 22: "Sleep quality seems worse, dream recall is down"

JARVIS SYNTHESIZES PATTERN:
- Nodes: Sleep, Coffee, Focus, Morning
- Relationships detected:
  - Late bed → Worse sleep → Morning fatigue
  - More caffeine → Sleep disruption → Daytime tiredness
- Confidence: 0.78

JARVIS RESPONSE:
"Looking at your recent notes, there's a pattern: you've been coding 
later (midnight+), which has affected sleep quality. Combined with 
increased caffeine intake, this might explain the morning focus issues.
Pattern timeline:
- Apr 12: Changed sleep schedule
- Apr 15-22: Increasing fatigue noted
- Current: Morning focus problems

Hypothesis: Earlier bedtime + consistent sleep might help.
Your past notes show you focus best when sleeping by 11pm."
"""


# ============================================================================
# SCENARIO 4: Cross-domain Knowledge Synthesis
# ============================================================================

SCENARIO_4_SYNTHESIS = """
USER (from Physics class): "Quantum superposition means particles exist 
in multiple states simultaneously until measured"

USER (from ML study): "Neural networks process multiple weighted inputs 
to generate outputs"

USER: "Is there any connection between quantum superposition and how 
neural networks work?"

JARVIS KNOWLEDGE GRAPH:
- Node: Superposition (type: physics concept)
- Node: Neural Networks (type: ml concept)
- Node: Multiple States (type: abstract concept)
- Node: Quantum Computing (type: domain)

GRAPH TRAVERSAL:
Superposition → Multiple States → (potential bridge) → 
Neural Network Uncertainty → Regularization

GROQ SYNTHESIS:
"While quantum superposition and neural networks operate on different 
principles, there are interesting conceptual parallels:

Superposition: Particles exist in multiple states simultaneously
Neural Networks: Hidden units represent multiple possibilities/features

Practical connection: Quantum machine learning explores using quantum 
superposition to compute multiple neural network paths simultaneously 
for exponential speedup.

Your notes mention: [quotes relevant parts]"
"""


# ============================================================================
# SCENARIO 5: Auto-generated Reminders & Proactive Knowledge
# ============================================================================

SCENARIO_5_PROACTIVE = """
SYSTEM LEARNS (from past memories):
- User always forgets to drink water when coding
- User's focus drops after 6 hours
- User studies best in morning
- User is interested in NLP but hasn't touched it in 2 weeks

PROACTIVE MEMORY CHECK (weekly):
1. Pattern: "You haven't mentioned NLP in 14 days, but you've 
   expressed strong interest"
2. Opportunity detection: Recent breakthrough in LLMs might interest you
3. Graph suggests: NLP → Transformers (you studied), LLMs → Transformers

PROACTIVE RESPONSE:
"📚 Learning reminder: You were interested in NLP and recently learned 
about transformers. There's been new developments in LLMs that might 
build nicely on what you know.

💧 Habit reminder: Your notes show you often forget water when focused 
on coding. After 5-6 hours of coding sessions, your focus drops 
noticeably.

🎯 Opportunity: Your schedule shows mornings are prime focus time. 
Consider morning NLP study sessions?"
"""


# ============================================================================
# SCENARIO 6: Conversation with Memory Enhancement
# ============================================================================

SCENARIO_6_FULL_CONVERSATION = """
USER: "I'm trying to decide between TensorFlow and PyTorch for my 
new project"

STEP 1 - INGESTION (automatic):
- Message ingested as memory
- Entities: TensorFlow, PyTorch, decision making
- Tags: ["frameworks", "comparison", "decision"]
- Importance: 0.6 (question/decision)

STEP 2 - CONTEXT RETRIEVAL:
Vector search: "tensorflow pytorch comparison"
Results:
- Past memory 1: "Tried PyTorch for NN, easier to debug"
- Past memory 2: "TensorFlow for production ML pipeline"
- Past memory 3: "PyTorch community is more academic-focused"

STEP 3 - GRAPH TRAVERSAL:
- PyTorch connected to: Academic, Debugging, Dynamic Graphs
- TensorFlow connected to: Production, Deployment, Ecosystem

STEP 4 - GROQ SYNTHESIS:
Enhanced prompt to Groq:
"User context:
- You tried PyTorch for neural networks and found it easier to debug
- You used TensorFlow for production ML pipelines
- You note PyTorch community is more academic-focused

User question: Deciding between TensorFlow and PyTorch

Based on your experience, synthesize a recommendation..."

GROQ RESPONSE:
"Based on your experience: You found PyTorch easier to debug and better 
for experimentation, but valued TensorFlow for production deployments.

Recommendation: 
- PyTorch for development/experimentation (your preference)
- TensorFlow if production deployment is priority

For your specific project... [synthesized response]"

STEP 5 - RESPONSE & FOLLOW-UP MEMORY:
User: "I'll go with PyTorch for this exploratory phase"

System creates memory:
- "Chose PyTorch for exploratory phase of [project]"
- Links to: PyTorch node, project node
- Reinforces PyTorch→experimentation relationship
"""


# ============================================================================
# CODE EXAMPLES FOR SCENARIOS
# ============================================================================

CODE_EXAMPLE = """
# Import everything
from memory_system import (
    MemoryManager, MemoryIngestionRequest, MemoryPriority,
    RecallMode, IngestionAnalyzer, KnowledgeGraph
)
from memory_system.integration import setup_memory_system

# Setup
integration = setup_memory_system(orchestrator, use_mock_embeddings=False)
memory_manager = integration.memory_manager

# --- SCENARIO 1: Learning ---
async def handle_learning():
    request = MemoryIngestionRequest(
        content="Learned about transformer architectures...",
        category="learning",
        priority=MemoryPriority.HIGH,
        tags=["ml", "transformers", "learning"]
    )
    result = await memory_manager.ingest_memory(request)
    print(f"✅ Stored memory: {result['memory_id']}")
    
    # Later retrieve
    recall_result = await memory_manager.retrieve_memory(
        query="How do transformers work?",
        enhance=True
    )
    print(f"💡 Answer: {recall_result.enhanced_answer}")


# --- SCENARIO 2: Projects ---
async def handle_project():
    # Log project start
    request = MemoryIngestionRequest(
        content="Building recommendation system with Python, scikit-learn, MongoDB",
        category="project",
        priority=MemoryPriority.HIGH,
        tags=["project", "python", "ml"],
        metadata={"project_name": "RecommendSys_2024"}
    )
    result = await memory_manager.ingest_memory(request)
    
    # Later - problem encountered
    await memory_manager.ingest_memory(
        MemoryIngestionRequest(
            content="Cold start problem with collaborative filtering",
            category="debugging",
            priority=MemoryPriority.NORMAL,
            tags=["cold_start", "recommenders"]
        )
    )
    
    # Get context-aware help
    help_result = await integration.enhance_groq_response(
        "How do I fix cold start problems?",
        brain=brain
    )


# --- SCENARIO 3: Patterns ---
async def handle_patterns():
    # System learns patterns from multiple memories
    result = await memory_manager.retrieve_memory(
        query="Why is my morning focus bad?",
        limit=10  # Get more context
    )
    
    # Groq can synthesize patterns from all memories


# --- SCENARIO 4: Cross-domain ---
async def handle_synthesis():
    # Query about connection between topics
    recall_result = await memory_manager.recall_engine.recall(
        query="Connection between quantum superposition and neural networks",
        mode=RecallMode.HYBRID,  # Use both vector and graph
        enhance_with_groq=True
    )
    
    print(recall_result.enhanced_answer)


# --- SCENARIO 6: Full conversation ---
async def handle_conversation():
    message = "Trying to decide between TensorFlow and PyTorch"
    
    # Process with all integration
    response = await integration.process_user_message(message)
    print(f"Response: {response}")
    
    # Get enhanced response
    enhanced = await integration.enhance_groq_response(message, brain)
    print(f"Enhanced: {enhanced}")
"""


if __name__ == "__main__":
    print("📖 JARVIS Memory System - Example Scenarios\n")
    
    scenarios = [
        ("Learning & Knowledge Retention", SCENARIO_1_LEARNING),
        ("Project Management & Context Awareness", SCENARIO_2_PROJECTS),
        ("Decision Support & Pattern Recognition", SCENARIO_3_PATTERNS),
        ("Cross-domain Knowledge Synthesis", SCENARIO_4_SYNTHESIS),
        ("Auto-generated Reminders & Proactive Knowledge", SCENARIO_5_PROACTIVE),
        ("Full Conversation with Memory Enhancement", SCENARIO_6_FULL_CONVERSATION),
    ]
    
    for i, (title, scenario) in enumerate(scenarios, 1):
        print(f"{'='*70}")
        print(f"SCENARIO {i}: {title}")
        print(f"{'='*70}")
        print(scenario)
        print()
    
    print("="*70)
    print("CODE EXAMPLES")
    print("="*70)
    print(CODE_EXAMPLE)
