"""
Knowledge Graph - Semantic Relationship Manager

Models knowledge as interconnected nodes and edges.
Enables tracking of relationships between concepts, people, projects, etc.
"""

import json
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

try:
    import networkx as nx
    from networkx.readwrite import json_graph
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    nx = None
    print("⚠️ NetworkX not installed. Install with: pip install networkx")


class RelationType(Enum):
    """Types of relationships in knowledge graph."""
    RELATED_TO = "related_to"
    USED_FOR = "used_for"
    PART_OF = "part_of"
    CAUSES = "causes"
    SIMILAR_TO = "similar_to"
    DEPENDS_ON = "depends_on"
    MENTIONED_IN = "mentioned_in"
    CREATED_BY = "created_by"
    KNOWS = "knows"
    INTERESTED_IN = "interested_in"


@dataclass
class GraphNode:
    """Represents a node in the knowledge graph."""
    id: str
    label: str
    type: str  # concept, person, project, skill, etc.
    description: str = ""
    importance: float = 0.5
    created_at: str = None
    updated_at: str = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.now().isoformat()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class GraphEdge:
    """Represents an edge (relationship) in the knowledge graph."""
    source_id: str
    target_id: str
    relation_type: str
    weight: float = 1.0
    description: str = ""
    created_at: str = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.metadata is None:
            self.metadata = {}


class KnowledgeGraph:
    """
    Semantic knowledge graph for storing relationships.
    
    Enables:
    - Tracking concept relationships
    - Finding related ideas
    - Path discovery between concepts
    - Automatic relationship suggestion
    """
    
    def __init__(self):
        """Initialize knowledge graph."""
        if NETWORKX_AVAILABLE:
            self.graph = nx.DiGraph()
        else:
            self.graph = None
        
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []
        self.node_index: Dict[str, List[str]] = {}  # For type-based lookup
    
    def add_node(self, node: GraphNode, auto_create: bool = True) -> bool:
        """
        Add a node to the graph.
        
        Args:
            node: Node to add
            auto_create: Auto-create if missing
            
        Returns:
            Success flag
        """
        try:
            self.nodes[node.id] = node
            
            # Add to NetworkX if available
            if self.graph is not None:
                self.graph.add_node(
                    node.id,
                    label=node.label,
                    type=node.type,
                    importance=node.importance
                )
            
            # Index by type
            if node.type not in self.node_index:
                self.node_index[node.type] = []
            self.node_index[node.type].append(node.id)
            
            return True
            
        except Exception as e:
            print(f"❌ Error adding node: {e}")
            return False
    
    def add_edge(self, edge: GraphEdge, auto_create_nodes: bool = True) -> bool:
        """
        Add an edge (relationship) to the graph.
        
        Args:
            edge: Edge to add
            auto_create_nodes: Auto-create nodes if missing
            
        Returns:
            Success flag
        """
        try:
            # Auto-create nodes if needed
            if auto_create_nodes:
                if edge.source_id not in self.nodes:
                    node = GraphNode(
                        id=edge.source_id,
                        label=edge.source_id,
                        type="unknown"
                    )
                    self.add_node(node)
                
                if edge.target_id not in self.nodes:
                    node = GraphNode(
                        id=edge.target_id,
                        label=edge.target_id,
                        type="unknown"
                    )
                    self.add_node(node)
            
            # Add to edge list
            self.edges.append(edge)
            
            # Add to NetworkX if available
            if self.graph is not None:
                self.graph.add_edge(
                    edge.source_id,
                    edge.target_id,
                    relation=edge.relation_type,
                    weight=edge.weight,
                    description=edge.description
                )
            
            return True
            
        except Exception as e:
            print(f"❌ Error adding edge: {e}")
            return False
    
    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Get node by ID."""
        return self.nodes.get(node_id)
    
    def get_neighbors(self, node_id: str, 
                     relation_types: Optional[List[str]] = None) -> List[Tuple[str, str]]:
        """
        Get connected nodes.
        
        Args:
            node_id: Node to get neighbors for
            relation_types: Filter by relationship types
            
        Returns:
            List of (neighbor_id, relation_type) tuples
        """
        if self.graph is None:
            # Fallback search
            neighbors = []
            for edge in self.edges:
                if edge.source_id == node_id:
                    if relation_types is None or edge.relation_type in relation_types:
                        neighbors.append((edge.target_id, edge.relation_type))
            return neighbors
        
        neighbors = []
        for successor in self.graph.successors(node_id):
            edge_data = self.graph.get_edge_data(node_id, successor)
            relation = edge_data.get('relation', 'unknown')
            
            if relation_types is None or relation in relation_types:
                neighbors.append((successor, relation))
        
        return neighbors
    
    def get_incoming(self, node_id: str) -> List[Tuple[str, str]]:
        """Get nodes pointing to this node."""
        if self.graph is None:
            incoming = []
            for edge in self.edges:
                if edge.target_id == node_id:
                    incoming.append((edge.source_id, edge.relation_type))
            return incoming
        
        incoming = []
        for predecessor in self.graph.predecessors(node_id):
            edge_data = self.graph.get_edge_data(predecessor, node_id)
            relation = edge_data.get('relation', 'unknown')
            incoming.append((predecessor, relation))
        
        return incoming
    
    def find_path(self, source_id: str, target_id: str) -> Optional[List[str]]:
        """
        Find shortest path between two nodes.
        
        Args:
            source_id: Start node
            target_id: End node
            
        Returns:
            Path as list of node IDs, or None if no path
        """
        if self.graph is None:
            return None
        
        try:
            path = nx.shortest_path(self.graph, source_id, target_id)
            return path
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None
    
    def find_related(self, node_id: str, depth: int = 2) -> Set[str]:
        """
        Find all related nodes within depth.
        
        Args:
            node_id: Starting node
            depth: How deep to search
            
        Returns:
            Set of related node IDs
        """
        if self.graph is None:
            # Simple traversal
            related = set()
            to_visit = [(node_id, 0)]
            visited = set()
            
            while to_visit:
                current, current_depth = to_visit.pop(0)
                if current in visited or current_depth >= depth:
                    continue
                
                visited.add(current)
                related.add(current)
                
                for edge in self.edges:
                    if edge.source_id == current and edge.target_id not in visited:
                        to_visit.append((edge.target_id, current_depth + 1))
            
            related.discard(node_id)  # Remove self
            return related
        
        related = set()
        try:
            for n in nx.single_source_shortest_path_length(
                self.graph, node_id, cutoff=depth
            ).keys():
                if n != node_id:
                    related.add(n)
        except nx.NetworkXError:
            pass
        
        return related
    
    def get_nodes_by_type(self, node_type: str) -> List[GraphNode]:
        """Get all nodes of a specific type."""
        return [
            node for node in self.nodes.values()
            if node.type == node_type
        ]
    
    def get_subgraph(self, node_ids: List[str]):
        """Get induced subgraph for given nodes."""
        if self.graph is None:
            return None
        
        return self.graph.subgraph(node_ids)
    
    def suggest_connections(self, node_id: str, 
                           max_suggestions: int = 5) -> List[Tuple[str, float]]:
        """
        Suggest potential connections based on graph structure.
        
        Uses common neighbors and shortest path length.
        
        Args:
            node_id: Node to get suggestions for
            max_suggestions: Max suggestions to return
            
        Returns:
            List of (node_id, score) tuples
        """
        if node_id not in self.nodes:
            return []
        
        candidates = {}
        
        # Find nodes with common neighbors
        node_neighbors = set(n[0] for n in self.get_neighbors(node_id))
        
        for potential_neighbor_id, potential_node in self.nodes.items():
            if potential_neighbor_id == node_id or potential_neighbor_id in node_neighbors:
                continue
            
            # Count common neighbors
            potential_neighbors = set(n[0] for n in self.get_neighbors(potential_neighbor_id))
            common = len(node_neighbors & potential_neighbors)
            
            # Try to find path
            path_length = None
            if self.graph is not None:
                try:
                    path_length = nx.shortest_path_length(
                        self.graph, node_id, potential_neighbor_id
                    )
                except (nx.NetworkXNoPath, nx.NodeNotFound):
                    path_length = 10  # Large number
            
            # Score based on common neighbors and path
            score = common * 10  # Boost common neighbors
            if path_length:
                score += 1 / path_length  # Closer nodes get higher score
            
            candidates[potential_neighbor_id] = score
        
        # Sort and return top suggestions
        suggestions = sorted(
            candidates.items(),
            key=lambda x: x[1],
            reverse=True
        )[:max_suggestions]
        
        return suggestions
    
    def get_graph_stats(self) -> Dict[str, Any]:
        """Get graph statistics."""
        stats = {
            'total_nodes': len(self.nodes),
            'total_edges': len(self.edges),
            'node_types': {},
            'edge_types': {},
            'avg_degree': 0,
        }
        
        # Count by type
        for node in self.nodes.values():
            node_type = node.type
            stats['node_types'][node_type] = stats['node_types'].get(node_type, 0) + 1
        
        for edge in self.edges:
            rel_type = edge.relation_type
            stats['edge_types'][rel_type] = stats['edge_types'].get(rel_type, 0) + 1
        
        # Calculate metrics
        if len(self.nodes) > 0 and self.graph is not None:
            try:
                avg_degree = sum(dict(self.graph.degree()).values()) / len(self.nodes)
                stats['avg_degree'] = avg_degree
                stats['density'] = nx.density(self.graph)
            except:
                pass
        
        return stats
    
    def export_to_dict(self) -> Dict[str, Any]:
        """Export graph as dictionary."""
        return {
            'nodes': [asdict(node) for node in self.nodes.values()],
            'edges': [
                {
                    'source_id': edge.source_id,
                    'target_id': edge.target_id,
                    'relation_type': edge.relation_type,
                    'weight': edge.weight,
                    'description': edge.description
                }
                for edge in self.edges
            ]
        }
    
    def save_to_file(self, filepath: str) -> bool:
        """Save graph to JSON file."""
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'version': '1.0',
                'stats': self.get_graph_stats(),
                'graph': self.export_to_dict()
            }
            
            import os
            os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"❌ Error saving graph: {e}")
            return False
    
    def load_from_file(self, filepath: str) -> bool:
        """Load graph from JSON file."""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Clear existing
            self.nodes.clear()
            self.edges.clear()
            self.node_index.clear()
            if self.graph is not None:
                self.graph.clear()
            
            # Load nodes
            for node_data in data['graph']['nodes']:
                node = GraphNode(**node_data)
                self.add_node(node)
            
            # Load edges
            for edge_data in data['graph']['edges']:
                edge = GraphEdge(**edge_data)
                self.add_edge(edge, auto_create_nodes=False)
            
            return True
        except Exception as e:
            print(f"❌ Error loading graph: {e}")
            return False


# Example usage
if __name__ == "__main__":
    print("🧠 Knowledge Graph Test\n")
    
    kg = KnowledgeGraph()
    
    # Add nodes
    nodes = [
        GraphNode(id="python", label="Python", type="language"),
        GraphNode(id="ai", label="Artificial Intelligence", type="field"),
        GraphNode(id="ml", label="Machine Learning", type="field"),
        GraphNode(id="nlp", label="Natural Language Processing", type="field"),
    ]
    
    for node in nodes:
        kg.add_node(node)
    
    # Add edges
    edges = [
        GraphEdge("python", "ai", RelationType.USED_FOR.value),
        GraphEdge("ai", "ml", RelationType.PART_OF.value),
        GraphEdge("ml", "nlp", RelationType.RELATED_TO.value),
        GraphEdge("python", "ml", RelationType.USED_FOR.value),
    ]
    
    for edge in edges:
        kg.add_edge(edge)
    
    print("✓ Added 4 nodes and 4 edges\n")
    
    # Find path
    print("🔍 Path from 'python' to 'nlp':")
    path = kg.find_path("python", "nlp")
    if path:
        print(f"  {' → '.join(path)}\n")
    
    # Get neighbors
    print("👥 Neighbors of 'python':")
    neighbors = kg.get_neighbors("python")
    for neighbor_id, rel_type in neighbors:
        print(f"  {neighbor_id} ({rel_type})")
    
    # Get suggestions
    print("\n💡 Suggested connections for 'python':")
    suggestions = kg.suggest_connections("python", max_suggestions=3)
    for node_id, score in suggestions:
        print(f"  {node_id} (score: {score:.2f})")
    
    print("\n📊 Graph Stats:")
    stats = kg.get_graph_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
