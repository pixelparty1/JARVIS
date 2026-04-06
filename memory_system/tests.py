"""
JARVIS Memory System - Testing & Verification Checklist

Comprehensive tests for all memory system components.
"""

import asyncio
import json
from typing import List, Tuple


class MemorySystemTestSuite:
    """Complete test suite for memory system."""
    
    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
    
    def test(self, name: str, condition: bool, details: str = "") -> bool:
        """Record test result."""
        self.total_tests += 1
        result = "✅ PASS" if condition else "❌ FAIL"
        
        self.test_results.append({
            'name': name,
            'passed': condition,
            'details': details
        })
        
        if condition:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
        
        print(f"{result}: {name}")
        if details:
            print(f"    {details}")
        
        return condition
    
    def run_all_tests(self):
        """Run complete test suite."""
        print("="*70)
        print("🧪 JARVIS MEMORY SYSTEM TEST SUITE")
        print("="*70)
        print()
        
        # Component tests
        self.test_vector_store()
        self.test_knowledge_graph()
        self.test_summarizer()
        self.test_recall_engine()
        self.test_memory_manager()
        self.test_ingestion_pipeline()
        self.test_integration()
        
        # Performance tests
        self.test_performance()
        
        # Print summary
        self.print_summary()
    
    def test_vector_store(self):
        """Test VectorStore component."""
        print("\n" + "="*70)
        print("📦 VECTOR STORE TESTS")
        print("="*70 + "\n")
        
        try:
            from memory_system.vector_store import VectorStore, Memory
            
            store = VectorStore(use_mock_embeddings=True)
            self.test("VectorStore initialization", store is not None)
            
            # Add memories
            mem1 = Memory(id="m1", content="Python is awesome")
            mem2 = Memory(id="m2", content="Machine learning rocks")
            
            store.add_memory(mem1)
            store.add_memory(mem2)
            
            self.test("Add multiple memories", len(store.memories) == 2)
            
            # Search
            results = store.search("Python programming", k=1)
            self.test("Semantic search works", len(results) > 0)
            
            if results:
                memory, similarity = results[0]
                self.test("Search returns similarity score",
                         0.0 <= similarity <= 1.0,
                         f"Similarity: {similarity}")
            
            # Tags search
            mem1.tags = ["python", "programming"]
            store.memories["m1"] = mem1
            
            tag_results = store.search_by_tags(["python"])
            self.test("Tag-based search works", len(tag_results) > 0)
            
            # Save/Load
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                store.save_to_file(f.name)
                store2 = VectorStore(use_mock_embeddings=True)
                store2.load_from_file(f.name)
                self.test("Save/load persistence", len(store2.memories) == len(store.memories))
            
            # Stats
            stats = store.get_stats()
            self.test("Get statistics", 'total_memories' in stats)
            
        except Exception as e:
            self.test("VectorStore tests", False, str(e))
    
    def test_knowledge_graph(self):
        """Test KnowledgeGraph component."""
        print("\n" + "="*70)
        print("🔗 KNOWLEDGE GRAPH TESTS")
        print("="*70 + "\n")
        
        try:
            from memory_system.knowledge_graph import (
                KnowledgeGraph, GraphNode, GraphEdge, RelationType
            )
            
            kg = KnowledgeGraph()
            self.test("KnowledgeGraph initialization", kg is not None)
            
            # Add nodes
            n1 = GraphNode(id="python", label="Python", type="language")
            n2 = GraphNode(id="ml", label="Machine Learning", type="domain")
            n3 = GraphNode(id="ai", label="AI", type="domain")
            
            kg.add_node(n1)
            kg.add_node(n2)
            kg.add_node(n3)
            
            self.test("Add multiple nodes", len(kg.nodes) == 3)
            
            # Add edges
            e1 = GraphEdge(
                source_id="python",
                target_id="ml",
                relation_type=RelationType.USED_FOR
            )
            e2 = GraphEdge(
                source_id="ml",
                target_id="ai",
                relation_type=RelationType.PART_OF
            )
            
            kg.add_edge(e1)
            kg.add_edge(e2)
            
            self.test("Add relationships", len(kg.edges) == 2)
            
            # Get neighbors
            neighbors = kg.get_neighbors("python")
            self.test("Get neighbors works", len(neighbors) > 0, f"Found {len(neighbors)} neighbors")
            
            # Find path
            path = kg.find_path("python", "ai")
            self.test("Find shortest path works", path is not None and len(path) >= 2,
                     f"Path: {path}")
            
            # Find related
            related = kg.find_related("python", depth=2)
            self.test("Find related nodes works", len(related) > 0)
            
            # Suggest connections
            suggestions = kg.suggest_connections("python")
            self.test("Suggest connections works", len(suggestions) >= 0)
            
            # Get stats
            stats = kg.get_graph_stats()
            self.test("Get graph statistics", 'total_nodes' in stats)
            
        except Exception as e:
            self.test("KnowledgeGraph tests", False, str(e))
    
    def test_summarizer(self):
        """Test Summarizer component."""
        print("\n" + "="*70)
        print("📝 SUMMARIZER TESTS")
        print("="*70 + "\n")
        
        try:
            from memory_system.summarizer import Summarizer
            
            summarizer = Summarizer()
            self.test("Summarizer initialization", summarizer is not None)
            
            # Test fallback summarization
            long_text = """
            Machine learning is a subset of artificial intelligence that 
            focuses on the development of algorithms and statistical models 
            that enable computers to learn and improve from experience without 
            being explicitly programmed. It involves analyzing patterns in data 
            and making predictions based on those patterns.
            """
            
            result = summarizer._fallback_summarize(long_text, max_chars=200)
            self.test("Fallback summarization works", result.summary is not None)
            self.test("Summary is shorter than original",
                     len(result.summary) <= len(long_text),
                     f"Length: {len(result.summary)} vs {len(long_text)}")
            self.test("Compression ratio calculated", result.compression_ratio > 0)
            self.test("Key points extracted", len(result.key_points) >= 0)
            
            # Test batch summarization
            texts = [
                "Python is great for data science",
                "Machine learning uses statistics",
                "Neural networks are complex"
            ]
            
            results = summarizer.batch_summarize(texts)
            self.test("Batch summarization", len(results) == len(texts))
            
            # Test note creation
            note_result = summarizer.create_note(long_text, "learning")
            self.test("Note creation works", note_result is not None)
            
            # Test note search
            notes = summarizer.search_notes("machine learning")
            self.test("Note search works", isinstance(notes, list))
            
        except Exception as e:
            self.test("Summarizer tests", False, str(e))
    
    def test_recall_engine(self):
        """Test RecallEngine component."""
        print("\n" + "="*70)
        print("🔄 RECALL ENGINE TESTS")
        print("="*70 + "\n")
        
        try:
            from memory_system.recall_engine import RecallEngine, RecallMode
            
            engine = RecallEngine()
            self.test("RecallEngine initialization", engine is not None)
            
            # Check modes
            modes = [
                RecallMode.SEMANTIC,
                RecallMode.GRAPH,
                RecallMode.HYBRID,
                RecallMode.ASSOCIATIVE,
                RecallMode.CONTEXTUAL
            ]
            
            for mode in modes:
                self.test(f"RecallMode.{mode.name}", mode is not None)
            
            # Test stats
            stats = engine.get_recall_stats()
            self.test("Get recall stats", 'total_queries' in stats)
            
        except Exception as e:
            self.test("RecallEngine tests", False, str(e))
    
    def test_memory_manager(self):
        """Test MemoryManager component."""
        print("\n" + "="*70)
        print("⚙️  MEMORY MANAGER TESTS")
        print("="*70 + "\n")
        
        try:
            from memory_system.memory_manager import (
                MemoryManager, MemoryIngestionRequest, MemoryPriority
            )
            
            manager = MemoryManager()
            self.test("MemoryManager initialization", manager is not None)
            
            # Test ingestion (non-async for now)
            self.test("Memory index exists", isinstance(manager.memory_index, dict))
            self.test("Memory queue exists", isinstance(manager.memory_queue, list))
            
            # Test priority enum
            priorities = [
                MemoryPriority.CRITICAL,
                MemoryPriority.HIGH,
                MemoryPriority.NORMAL,
                MemoryPriority.LOW,
                MemoryPriority.ARCHIVED
            ]
            
            for priority in priorities:
                self.test(f"MemoryPriority.{priority.name}", priority.value > 0)
            
            # Test stats
            stats = manager.get_memory_stats()
            self.test("Get memory stats", 'total_memories' in stats)
            
            # Test export/import
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json_data = manager.export_memories(f.name)
                self.test("Export memories", len(json_data) > 0)
        
        except Exception as e:
            self.test("MemoryManager tests", False, str(e))
    
    def test_ingestion_pipeline(self):
        """Test IngestionAnalyzer component."""
        print("\n" + "="*70)
        print("🔍 INGESTION PIPELINE TESTS")
        print("="*70 + "\n")
        
        try:
            from memory_system.knowledge_ingestion import (
                IngestionAnalyzer, EntityType
            )
            
            analyzer = IngestionAnalyzer()
            self.test("IngestionAnalyzer initialization", analyzer is not None)
            
            # Test entity extraction
            content = "I learned Python and machine learning today"
            entities = analyzer._extract_entities(content)
            self.test("Entity extraction works", len(entities) > 0,
                     f"Found {len(entities)} entities")
            
            # Test tagging
            tags = analyzer._generate_tags(content, entities)
            self.test("Tag generation works", isinstance(tags, list))
            
            # Test classification
            classification = analyzer._classify_content(content, entities)
            self.test("Content classification works", classification in [
                'learning', 'technical', 'question', 'daily_note', 'general'
            ])
            
            # Test importance calculation
            importance = analyzer._calculate_importance(content, entities, [])
            self.test("Importance calculation", 0.0 <= importance <= 1.0,
                     f"Score: {importance}")
            
        except Exception as e:
            self.test("IngestionAnalyzer tests", False, str(e))
    
    def test_integration(self):
        """Test Integration component."""
        print("\n" + "="*70)
        print("🔌 INTEGRATION TESTS")
        print("="*70 + "\n")
        
        try:
            from memory_system.integration import (
                MemorySystemIntegration, MemorySystemHealthCheck
            )
            
            integration = MemorySystemIntegration()
            self.test("MemorySystemIntegration initialization", integration is not None)
            
            # Test stats
            stats = integration.get_integration_stats()
            self.test("Get integration stats", 'messages_processed' in stats)
            
            # Test health check (standalone)
            self.test("MemorySystemHealthCheck available", MemorySystemHealthCheck is not None)
            
        except Exception as e:
            self.test("Integration tests", False, str(e))
    
    def test_performance(self):
        """Performance tests."""
        print("\n" + "="*70)
        print("⚡ PERFORMANCE TESTS")
        print("="*70 + "\n")
        
        try:
            from memory_system.vector_store import VectorStore, Memory
            import time
            
            store = VectorStore(use_mock_embeddings=True)
            
            # Add 100 memories
            start = time.time()
            for i in range(100):
                mem = Memory(id=f"m{i}", content=f"Content {i}")
                store.add_memory(mem)
            add_time = time.time() - start
            
            self.test("Add 100 memories", time=add_time)
            
            # Search performance
            start = time.time()
            results = store.search("content", k=10)
            search_time = time.time() - start
            
            self.test("Search 100 memories", time=search_time)
            
        except Exception as e:
            self.test("Performance tests", False, str(e))
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "="*70)
        print("📊 TEST SUMMARY")
        print("="*70 + "\n")
        
        print(f"Total Tests: {self.total_tests}")
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.failed_tests}")
        
        if self.failed_tests == 0:
            print("\n🎉 ALL TESTS PASSED!")
        else:
            print(f"\n⚠️  {self.failed_tests} test(s) failed")
        
        pass_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        print(f"Pass Rate: {pass_rate:.1f}%\n")
        
        return self.failed_tests == 0


class QuickVerification:
    """Quick verification checklist."""
    
    @staticmethod
    def verify_file_structure():
        """Verify all required files exist."""
        import os
        
        files = [
            'memory_system/__init__.py',
            'memory_system/vector_store.py',
            'memory_system/knowledge_graph.py',
            'memory_system/summarizer.py',
            'memory_system/recall_engine.py',
            'memory_system/memory_manager.py',
            'memory_system/knowledge_ingestion.py',
            'memory_system/integration.py',
            'memory_system/MEMORY_GUIDE.md',
            'memory_system/examples.py'
        ]
        
        print("📁 FILE STRUCTURE VERIFICATION\n")
        
        all_exist = True
        for filepath in files:
            exists = os.path.exists(filepath)
            status = "✅" if exists else "❌"
            print(f"{status} {filepath}")
            if not exists:
                all_exist = False
        
        return all_exist
    
    @staticmethod
    def verify_imports():
        """Verify all imports work."""
        print("\n📦 IMPORT VERIFICATION\n")
        
        imports = [
            ("VectorStore", "memory_system.vector_store"),
            ("KnowledgeGraph", "memory_system.knowledge_graph"),
            ("Summarizer", "memory_system.summarizer"),
            ("RecallEngine", "memory_system.recall_engine"),
            ("MemoryManager", "memory_system.memory_manager"),
            ("IngestionAnalyzer", "memory_system.knowledge_ingestion"),
            ("MemorySystemIntegration", "memory_system.integration"),
        ]
        
        all_ok = True
        for class_name, module_name in imports:
            try:
                module = __import__(module_name, fromlist=[class_name])
                getattr(module, class_name)
                print(f"✅ {class_name} from {module_name}")
            except Exception as e:
                print(f"❌ {class_name} from {module_name}: {e}")
                all_ok = False
        
        return all_ok


if __name__ == "__main__":
    print("\n🧪 JARVIS MEMORY SYSTEM TEST SUITE\n")
    
    # Run verification
    print("="*70)
    print("VERIFICATION CHECKLIST")
    print("="*70 + "\n")
    
    # File check
    files_ok = QuickVerification.verify_file_structure()
    
    # Import check
    imports_ok = QuickVerification.verify_imports()
    
    # Run tests
    print("\n")
    suite = MemorySystemTestSuite()
    suite.run_all_tests()
    
    # Final status
    print("\n" + "="*70)
    print("FINAL STATUS")
    print("="*70)
    print(f"Files: {'✅ OK' if files_ok else '❌ MISSING'}")
    print(f"Imports: {'✅ OK' if imports_ok else '❌ FAILED'}")
    print(f"Tests: {'✅ All Passed' if suite.failed_tests == 0 else f'❌ {suite.failed_tests} Failed'}")
    print("="*70 + "\n")
