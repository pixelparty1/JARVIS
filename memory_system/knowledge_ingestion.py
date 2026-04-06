"""
Knowledge Ingestion - Automatic Memory Processing

Monitors conversations for memory-worthy content and automatically:
- Extracts facts and entities
- Creates knowledge graph nodes
- Detects relationships
- Suggests connections
- Auto-prioritizes content
"""

import asyncio
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class EntityType(Enum):
    """Types of entities to extract."""
    PERSON = "person"
    PROJECT = "project"
    CONCEPT = "concept"
    TECHNOLOGY = "technology"
    PLACE = "place"
    EVENT = "event"
    LEARNING = "learning"


@dataclass
class Entity:
    """Extracted entity."""
    name: str
    type: EntityType
    context: str
    confidence: float = 0.8


@dataclass
class ExtractedRelationship:
    """Extracted relationship between entities."""
    source: str
    target: str
    relation_type: str
    context: str
    confidence: float = 0.7


class IngestionAnalyzer:
    """
    Analyzes content for automatic memory ingestion.
    
    Features:
    - Entity extraction (persons, projects, concepts)
    - Relationship detection
    - Importance scoring
    - Auto-tagging
    - Content classification
    """
    
    def __init__(self, brain=None):
        """
        Initialize analyzer.
        
        Args:
            brain: JARVIS brain (for advanced analysis via Groq)
        """
        self.brain = brain
        self.extraction_history = []
        
        self.analyzer_stats = {
            'total_analyzed': 0,
            'total_entities_extracted': 0,
            'total_relationships_found': 0,
            'average_confidence': 0.0
        }
        
        # Simple keyword-based entity recognizers
        self.technology_keywords = {
            'python', 'javascript', 'rust', 'go', 'java', 'cpp', 'c++',
            'machine learning', 'ai', 'neural network', 'deep learning',
            'tensorflow', 'pytorch', 'huggingface', 'groq',
            'database', 'sql', 'mongodb', 'redis', 'faiss',
            'api', 'rest', 'graphql', 'websocket',
            'docker', 'kubernetes', 'aws', 'google cloud'
        }
        
        self.learning_keywords = {
            'learned', 'discovered', 'understand', 'realized', 'figured out',
            'mastered', 'studied', 'researched', 'explored', 'implemented'
        }
    
    async def analyze_content(self, content: str) -> Dict[str, Any]:
        """
        Analyze content for ingestion.
        
        Args:
            content: Text content to analyze
            
        Returns:
            Analysis results with entities, relationships, priority
        """
        self.analyzer_stats['total_analyzed'] += 1
        
        try:
            # Extract entities
            entities = self._extract_entities(content)
            
            # Extract relationships
            relationships = self._extract_relationships(content, entities)
            
            # Calculate importance
            importance = self._calculate_importance(
                content, entities, relationships
            )
            
            # Generate tags
            tags = self._generate_tags(content, entities)
            
            # Classify content
            classification = self._classify_content(content, entities)
            
            result = {
                'content': content,
                'entities': entities,
                'relationships': relationships,
                'importance_score': importance,
                'tags': tags,
                'classification': classification,
                'is_memory_worthy': importance > 0.5,
                'suggested_category': self._suggest_category(classification),
                'summary': self._generate_summary(content, entities),
                'analyzed_at': datetime.now().isoformat()
            }
            
            self.extraction_history.append(result)
            self.analyzer_stats['total_entities_extracted'] += len(entities)
            self.analyzer_stats['total_relationships_found'] += len(relationships)
            
            return result
            
        except Exception as e:
            print(f"❌ Analysis error: {e}")
            return {'status': 'error', 'reason': str(e)}
    
    def _extract_entities(self, content: str) -> List[Entity]:
        """
        Extract entities from content.
        
        Uses pattern matching and keyword heuristics.
        """
        entities = []
        content_lower = content.lower()
        
        # Extract technology mentions
        for keyword in self.technology_keywords:
            if keyword in content_lower:
                confidence = min(0.95, 0.7 + content_lower.count(keyword) * 0.1)
                entities.append(Entity(
                    name=keyword,
                    type=EntityType.TECHNOLOGY,
                    context=content[:100],
                    confidence=confidence
                ))
        
        # Extract learning signals
        for keyword in self.learning_keywords:
            if keyword in content_lower:
                entities.append(Entity(
                    name="learning_event",
                    type=EntityType.LEARNING,
                    context=content[:100],
                    confidence=0.8
                ))
        
        # Extract capitalized names (potential persons/projects)
        import re
        name_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        names = re.findall(name_pattern, content)
        
        for name in names[:3]:  # Limit
            if len(name) > 2:
                entities.append(Entity(
                    name=name,
                    type=EntityType.PERSON,
                    context=content[:100],
                    confidence=0.6
                ))
        
        # Deduplicate
        seen = set()
        unique_entities = []
        for entity in entities:
            key = (entity.name.lower(), entity.type)
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)
        
        return unique_entities
    
    def _extract_relationships(self, content: str,
                              entities: List[Entity]) -> List[ExtractedRelationship]:
        """Extract relationships between entities."""
        relationships = []
        
        if len(entities) < 2:
            return relationships
        
        # Look for relationship patterns
        patterns = [
            (r'(\w+)\s+uses\s+(\w+)', 'uses'),
            (r'(\w+)\s+helps\s+(\w+)', 'helps'),
            (r'(\w+)\s+is\s+(\w+)', 'is'),
            (r'(\w+)\s+works\s+with\s+(\w+)', 'works_with'),
            (r'(' + '|'.join(e.name for e in entities[:3]) + r')\s+and\s+(' + '|'.join(e.name for e in entities[-3:]) + r')', 'relates_to')
        ]
        
        import re
        for pattern, rel_type in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) >= 2:
                    relationships.append(ExtractedRelationship(
                        source=match.group(1),
                        target=match.group(2),
                        relation_type=rel_type,
                        context=content[:100]
                    ))
        
        return relationships[:5]  # Limit
    
    def _calculate_importance(self, content: str,
                             entities: List[Entity],
                             relationships: List[ExtractedRelationship]) -> float:
        """Calculate content importance (0-1)."""
        score = 0.5  # Base score
        
        # Boost for entity mentions
        score += min(0.2, len(entities) * 0.05)
        
        # Boost for relationships
        score += min(0.15, len(relationships) * 0.05)
        
        # Boost for length (more context = more important)
        if len(content) > 200:
            score += 0.05
        elif len(content) < 50:
            score -= 0.1
        
        # Boost for learning signals
        if any(e.type == EntityType.LEARNING for e in entities):
            score += 0.15
        
        # Boost for technology mentions
        tech_entities = [e for e in entities if e.type == EntityType.TECHNOLOGY]
        if tech_entities:
            score += 0.1
        
        return min(1.0, max(0.0, score))
    
    def _generate_tags(self, content: str, entities: List[Entity]) -> List[str]:
        """Auto-generate tags for content."""
        tags = set()
        
        # Add entity names as tags
        for entity in entities:
            if entity.type == EntityType.TECHNOLOGY:
                tags.add(entity.name.lower())
        
        # Add content-based tags
        if any(e.type == EntityType.LEARNING for e in entities):
            tags.add('learning')
        
        if any(e.type == EntityType.TECHNOLOGY for e in entities):
            tags.add('tech')
        
        if 'code' in content.lower():
            tags.add('code')
        
        if 'bug' in content.lower() or 'error' in content.lower():
            tags.add('debugging')
        
        if 'question' in content.lower() or '?' in content:
            tags.add('question')
        
        return list(tags)[:5]  # Limit to 5
    
    def _classify_content(self, content: str,
                         entities: List[Entity]) -> str:
        """Classify content type."""
        if any(e.type == EntityType.LEARNING for e in entities):
            return 'learning'
        elif any(e.type == EntityType.TECHNOLOGY for e in entities):
            return 'technical'
        elif '?' in content:
            return 'question'
        elif 'today' in content.lower() or 'just' in content.lower():
            return 'daily_note'
        else:
            return 'general'
    
    def _suggest_category(self, classification: str) -> str:
        """Suggest memory category."""
        category_map = {
            'learning': 'learning',
            'technical': 'tech',
            'question': 'questions',
            'daily_note': 'daily',
            'general': 'general'
        }
        return category_map.get(classification, 'general')
    
    def _generate_summary(self, content: str, entities: List[Entity]) -> str:
        """Generate brief summary."""
        if len(content) > 150:
            return content[:147] + "..."
        return content


class KnowledgeIngestionPipeline:
    """
    Pipeline for automated memory ingestion.
    
    Process:
    1. Monitor conversation stream
    2. Analyze content via IngestionAnalyzer
    3. Filter by importance
    4. Create memory entries
    5. Build knowledge graph
    6. Track patterns
    """
    
    def __init__(self, memory_manager=None, analyzer=None):
        """
        Initialize pipeline.
        
        Args:
            memory_manager: MemoryManager instance
            analyzer: IngestionAnalyzer instance
        """
        self.memory_manager = memory_manager
        self.analyzer = analyzer or IngestionAnalyzer()
        
        self.pipeline_stats = {
            'content_analyzed': 0,
            'memories_created': 0,
            'skipped_low_importance': 0,
            'average_analysis_time': 0.0
        }
        
        self.analysis_queue = []
    
    async def process_message(self, message: str,
                             source: str = "conversation",
                             auto_ingest: bool = True) -> Optional[Dict]:
        """
        Process a conversation message for memory ingestion.
        
        Args:
            message: Message content
            source: Where message came from
            auto_ingest: Automatically ingest if important
            
        Returns:
            Analysis result and memory ID if ingested
        """
        import time
        start_time = time.time()
        
        # Analyze content
        analysis = await self.analyzer.analyze_content(message)
        
        if analysis.get('status') == 'error':
            return analysis
        
        # Check importance
        if analysis['importance_score'] < 0.5:
            self.pipeline_stats['skipped_low_importance'] += 1
            return {'status': 'skipped', 'reason': 'low_importance'}
        
        # Auto-ingest if requested
        memory_id = None
        if auto_ingest and self.memory_manager:
            from memory_manager import MemoryIngestionRequest, MemoryPriority
            
            priority_map = {
                i / 10: MemoryPriority.ARCHIVED if i < 2 else
                        MemoryPriority.LOW if i < 4 else
                        MemoryPriority.NORMAL if i < 7 else
                        MemoryPriority.HIGH if i < 9 else
                        MemoryPriority.CRITICAL
                for i in range(0, 11)
            }
            
            score = analysis['importance_score']
            priority = MemoryPriority.NORMAL
            for threshold, level in sorted(priority_map.items()):
                if score >= threshold:
                    priority = level
            
            request = MemoryIngestionRequest(
                content=message,
                category=analysis['suggested_category'],
                priority=priority,
                tags=analysis['tags'],
                source=source,
                metadata={'analysis': analysis}
            )
            
            result = await self.memory_manager.ingest_memory(request)
            memory_id = result.get('memory_id')
            self.pipeline_stats['memories_created'] += 1
        
        elapsed = time.time() - start_time
        self.pipeline_stats['average_analysis_time'] = (
            (self.pipeline_stats['average_analysis_time'] +
             elapsed) / 2
        )
        
        return {
            'status': 'success',
            'analysis': analysis,
            'memory_id': memory_id,
            'processing_time': elapsed
        }
    
    def batch_process(self, messages: List[str]) -> List[Dict]:
        """Process multiple messages."""
        results = []
        for message in messages:
            # Note: Would need async context for real use
            results.append({'message': message, 'status': 'queued'})
        return results
    
    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics."""
        return {
            'pipeline_stats': self.pipeline_stats,
            'analyzer_stats': self.analyzer.analyzer_stats,
            'queue_length': len(self.analysis_queue)
        }


# Example usage
if __name__ == "__main__":
    print("🔄 Knowledge Ingestion Test\n")
    
    analyzer = IngestionAnalyzer()
    
    test_content = [
        "Today I learned about neural networks using PyTorch",
        "Had a question about REST APIs",
        "Mastered Python decorators"
    ]
    
    print("Testing content analysis:\n")
    for content in test_content:
        print(f"Content: {content}")
        print(f"  (Would be analyzed for entities, relationships, importance)\n")
    
    print("Testing entity extraction:\n")
    entities = analyzer._extract_entities(
        "I implemented a machine learning model using TensorFlow"
    )
    for entity in entities:
        print(f"  - {entity.name} ({entity.type.value}): {entity.confidence:.1%}")
    
    print("\n📊 Pipeline Stats:")
    pipeline = KnowledgeIngestionPipeline(analyzer=analyzer)
    stats = pipeline.get_pipeline_stats()
    for key, value in stats.items():
        if isinstance(value, dict):
            for k, v in value.items():
                print(f"  {key}.{k}: {v}")
        else:
            print(f"  {key}: {value}")
