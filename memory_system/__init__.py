"""
JARVIS Knowledge System - Phase 5

A comprehensive memory management system that combines:
- Semantic search using FAISS vectors
- Knowledge graphs using NetworkX
- Intelligent summarization using Groq
- Automatic ingestion and relationship detection
- Context-aware retrieval and reasoning

Modules:
- vector_store: Semantic search and embedding storage
- knowledge_graph: Relationship modeling and graph traversal
- summarizer: Intelligent text compression and note management
- recall_engine: Multi-mode memory retrieval with Groq synthesis
- memory_manager: Central orchestration and lifecycle management
- knowledge_ingestion: Automatic analysis and ingestion
"""

__version__ = "1.0.0"
__author__ = "JARVIS"

from .vector_store import VectorStore, Memory
from .knowledge_graph import KnowledgeGraph, GraphNode, GraphEdge, RelationType
from .summarizer import Summarizer, SmartNoter, SummaryResult
from .recall_engine import RecallEngine, RecallMode, RecallResult
from .memory_manager import MemoryManager, MemoryIngestionRequest, MemoryPriority
from .knowledge_ingestion import (
    IngestionAnalyzer, KnowledgeIngestionPipeline, Entity, EntityType
)

__all__ = [
    # Vector Store
    "VectorStore",
    "Memory",
    
    # Knowledge Graph
    "KnowledgeGraph",
    "GraphNode",
    "GraphEdge",
    "RelationType",
    
    # Summarizer
    "Summarizer",
    "SmartNoter",
    "SummaryResult",
    
    # Recall Engine
    "RecallEngine",
    "RecallMode",
    "RecallResult",
    
    # Memory Manager
    "MemoryManager",
    "MemoryIngestionRequest",
    "MemoryPriority",
    
    # Knowledge Ingestion
    "IngestionAnalyzer",
    "KnowledgeIngestionPipeline",
    "Entity",
    "EntityType",
]
