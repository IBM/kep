"""
Full Interactive Knowledge Graph Visualization

Provides complete interactive HTML visualizations of knowledge graphs
with configurable relationships, filtering, and advanced features.

Features:
- Interactive HTML graphs with pyvis
- Configurable relationship structures
- Node filtering and sampling
- Multiple output formats
- Statistics generation
- Relationship styling

Example:
    viz = KnowledgeGraphVisualizer("runs/demo/structured.json", "output_dir")
    html_file, stats = viz.visualize()
"""

import json
import networkx as nx
from pyvis.network import Network
from collections import defaultdict, Counter
from pathlib import Path
import logging
from typing import Dict, List, Set, Tuple, Any, Optional


class KnowledgeGraphVisualizer:
    """
    Full-featured interactive knowledge graph visualizer.
    
    Creates interactive HTML visualizations from KEP extraction results
    with configurable relationship structures, filtering capabilities,
    and comprehensive statistics generation.
    
    Attributes:
        structured_data_path (Path): Path to structured.json results
        output_dir (Path): Directory for output files
        graph (nx.DiGraph): NetworkX directed graph
        node_types (dict): Visual styling for different node types
        relationship_config (dict): Configuration for graph relationships
    """
    
    def __init__(self, structured_data_path: str, output_dir: str = "graph_output", 
                 relationship_config: Optional[Dict] = None, schema_path: Optional[str] = None):
        self.structured_data_path = Path(structured_data_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.graph = nx.DiGraph()  # Use directed graph for relationship hierarchy
        self.node_types = {
            'materials': {'color': '#FF6B6B', 'shape': 'box'},
            'applications': {'color': '#4ECDC4', 'shape': 'circle'},
            'roles': {'color': '#45B7D1', 'shape': 'triangle'},
            'properties': {'color': '#96CEB4', 'shape': 'diamond'},
            'sources': {'color': '#FFEAA7', 'shape': 'star'}
        }
        
        # Load relationship configuration
        self.relationship_config = self._load_relationship_config(relationship_config, schema_path)
        
        self.logger = logging.getLogger(__name__)
    
    def _load_relationship_config(self, relationship_config: Optional[Dict], 
                                schema_path: Optional[str]) -> Dict:
        """Load relationship configuration from schema or provided config."""
        if relationship_config:
            return relationship_config
        
        if schema_path and Path(schema_path).exists():
            try:
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schema = json.load(f)
                    if 'GRAPH_RELATIONSHIPS' in schema:
                        return schema['GRAPH_RELATIONSHIPS']
            except Exception as e:
                self.logger.warning(f"Could not load relationship config from schema: {e}")
        
        # Default relationship configuration (your requested structure)
        return {
            "description": "Default hierarchical relationship configuration",
            "relationship_rules": [
                {
                    "name": "source_to_materials",
                    "from_type": "sources",
                    "to_type": "materials",
                    "relationship_label": "contains_material",
                    "edge_style": {"color": "#FF6B6B", "width": 2}
                },
                {
                    "name": "materials_to_others",
                    "from_type": "materials",
                    "to_type": ["applications", "roles", "properties"],
                    "relationship_label": "relates_to",
                    "edge_style": {"color": "#666666", "width": 1.5}
                }
            ]
        }
    
    def load_structured_data(self) -> List[Dict[str, Any]]:
        """Load structured JSON data from KEP pipeline output."""
        try:
            with open(self.structured_data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.logger.info(f"Loaded {len(data)} structured entries")
            return data
        except Exception as e:
            self.logger.error(f"Error loading structured data: {e}")
            raise
    
    def build_graph(self, data: List[Dict[str, Any]]) -> None:
        """Build NetworkX graph from structured data using relationship configuration."""
        # Track nodes by type and source for relationship building
        nodes_by_type = defaultdict(set)
        nodes_by_source = defaultdict(lambda: defaultdict(set))
        
        # First pass: Add all nodes
        for entry in data:
            source = entry.get('Source', 'Unknown')
            extracted_data = entry.get('data', {})
            
            # Add source node
            if not self.graph.has_node(source):
                self.graph.add_node(source, 
                                  node_type='sources',
                                  title=f"Source: {source}",
                                  size=20,
                                  frequency=1)
            
            nodes_by_type['sources'].add(source)
            
            # Process each category
            for category, items in extracted_data.items():
                if not items:
                    continue
                    
                for item in items:
                    if not item or item.strip() == "":
                        continue
                    
                    item_clean = item.strip()
                    
                    # Add node if not exists
                    if not self.graph.has_node(item_clean):
                        self.graph.add_node(item_clean,
                                          node_type=category,
                                          title=f"{category.title()}: {item_clean}",
                                          size=10,
                                          frequency=1)
                    else:
                        # Increment frequency for existing nodes
                        self.graph.nodes[item_clean]['frequency'] += 1
                        self.graph.nodes[item_clean]['size'] = min(30, 
                            10 + self.graph.nodes[item_clean]['frequency'] * 2)
                    
                    # Track for relationship building
                    nodes_by_type[category].add(item_clean)
                    nodes_by_source[source][category].add(item_clean)
        
        # Second pass: Add edges based on relationship rules
        self._build_relationships(nodes_by_source, nodes_by_type)
        
        self.logger.info(f"Built graph with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges")
    
    def _build_relationships(self, nodes_by_source: Dict, nodes_by_type: Dict) -> None:
        """Build relationships according to configuration rules."""
        relationship_rules = self.relationship_config.get('relationship_rules', [])
        
        for rule in relationship_rules:
            from_type = rule['from_type']
            to_types = rule['to_type']
            relationship_label = rule.get('relationship_label', 'connected')
            edge_style = rule.get('edge_style', {})
            
            # Ensure to_types is a list
            if isinstance(to_types, str):
                to_types = [to_types]
            
            # Apply rule based on structure
            if from_type == 'sources':
                # Connect sources to target types
                for source in nodes_by_type.get('sources', []):
                    for to_type in to_types:
                        for target_node in nodes_by_source[source].get(to_type, []):
                            self._add_styled_edge(source, target_node, relationship_label, edge_style)
            
            elif from_type in nodes_by_type:
                # Connect within same source context
                for source, source_nodes in nodes_by_source.items():
                    from_nodes = source_nodes.get(from_type, set())
                    
                    for from_node in from_nodes:
                        for to_type in to_types:
                            to_nodes = source_nodes.get(to_type, set())
                            for to_node in to_nodes:
                                if from_node != to_node:
                                    self._add_styled_edge(from_node, to_node, relationship_label, edge_style)
    
    def _add_styled_edge(self, from_node: str, to_node: str, relationship_label: str, 
                        edge_style: Dict) -> None:
        """Add edge with styling information."""
        if not self.graph.has_edge(from_node, to_node):
            self.graph.add_edge(from_node, to_node,
                              relationship=relationship_label,
                              color=edge_style.get('color', '#666666'),
                              width=edge_style.get('width', 1),
                              style=edge_style.get('style', 'solid'),
                              weight=1)
    
    def create_interactive_visualization(self, 
                                       height: str = "800px",
                                       width: str = "100%",
                                       show_buttons: bool = True) -> str:
        """Create interactive HTML visualization using pyvis."""
        net = Network(height=height, width=width, bgcolor="#222222", font_color="white")
        
        # Add nodes with styling
        for node, data in self.graph.nodes(data=True):
            node_type = data.get('node_type', 'materials')
            style = self.node_types.get(node_type, self.node_types['materials'])
            
            net.add_node(node,
                        label=self._truncate_label(node),
                        title=data.get('title', node),
                        color=style['color'],
                        size=data.get('size', 10))
        
        # Add edges with styling
        for source, target, data in self.graph.edges(data=True):
            edge_width = data.get('width', 1)
            edge_color = data.get('color', '#666666')
            relationship = data.get('relationship', 'connected')
            
            net.add_edge(source, target, 
                        width=min(5, edge_width),
                        color=edge_color,
                        title=f"Relationship: {relationship}")
        
        # Generate HTML file
        output_file = self.output_dir / "knowledge_graph.html"
        
        # Use write_html instead of show to avoid template issues
        try:
            net.write_html(str(output_file))
        except Exception as e:
            self.logger.warning(f"Error with pyvis write_html: {e}")
            # Fallback: create basic HTML
            self._create_basic_html(output_file)
        
        # Add custom CSS and controls
        self._enhance_html_output(output_file)
        
        return str(output_file)
    
    def _create_basic_html(self, output_file: Path) -> None:
        """Create basic HTML visualization as fallback."""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Knowledge Graph</title>
            <style>
                body {{ background-color: #222; color: white; font-family: Arial, sans-serif; }}
                .info {{ padding: 20px; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="info">
                <h1>Knowledge Graph</h1>
                <p>Graph contains {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges</p>
                <p>Please use the statistics JSON file for detailed analysis</p>
            </div>
        </body>
        </html>
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _truncate_label(self, label: str, max_length: int = 30) -> str:
        """Truncate long labels for better visualization."""
        if len(label) <= max_length:
            return label
        return label[:max_length-3] + "..."
    
    def _enhance_html_output(self, html_file: Path) -> None:
        """Add custom CSS and JavaScript enhancements."""
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add custom CSS and legend
        custom_additions = """
        <style>
        .legend {
            position: fixed;
            top: 10px;
            right: 10px;
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 15px;
            border-radius: 8px;
            font-family: Arial, sans-serif;
            z-index: 1000;
        }
        .legend h3 { margin-top: 0; font-size: 16px; }
        .legend-item { margin: 5px 0; display: flex; align-items: center; }
        .legend-color { width: 15px; height: 15px; margin-right: 8px; border-radius: 3px; }
        .stats-panel {
            position: fixed;
            top: 10px;
            left: 10px;
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 15px;
            border-radius: 8px;
            font-family: Arial, sans-serif;
            z-index: 1000;
        }
        </style>
        <div class="legend">
            <h3>Node Types</h3>
            <div class="legend-item"><div class="legend-color" style="background: #FF6B6B;"></div>Materials</div>
            <div class="legend-item"><div class="legend-color" style="background: #4ECDC4;"></div>Applications</div>
            <div class="legend-item"><div class="legend-color" style="background: #45B7D1;"></div>Roles</div>
            <div class="legend-item"><div class="legend-color" style="background: #96CEB4;"></div>Properties</div>
            <div class="legend-item"><div class="legend-color" style="background: #FFEAA7;"></div>Sources</div>
        </div>
        <div class="stats-panel">
            <h3>Graph Statistics</h3>
            <div>Nodes: """ + str(self.graph.number_of_nodes()) + """</div>
            <div>Edges: """ + str(self.graph.number_of_edges()) + """</div>
        </div>
        """
        
        # Insert before closing body tag
        content = content.replace("</body>", custom_additions + "</body>")
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def generate_statistics(self) -> Dict[str, Any]:
        """Generate graph statistics and insights."""
        stats = {
            'total_nodes': self.graph.number_of_nodes(),
            'total_edges': self.graph.number_of_edges(),
            'node_types': {},
            'most_connected_nodes': [],
            'isolated_nodes': [],
            'clustering_coefficient': nx.average_clustering(self.graph)
        }
        
        # Node type distribution
        for node, data in self.graph.nodes(data=True):
            node_type = data.get('node_type', 'unknown')
            stats['node_types'][node_type] = stats['node_types'].get(node_type, 0) + 1
        
        # Most connected nodes
        degree_centrality = nx.degree_centrality(self.graph)
        stats['most_connected_nodes'] = sorted(
            [(node, centrality) for node, centrality in degree_centrality.items()],
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # Isolated nodes
        stats['isolated_nodes'] = list(nx.isolates(self.graph))
        
        return stats
    
    def create_filtered_visualization(self, 
                                    node_types: List[str] = None,
                                    min_frequency: int = 1,
                                    output_name: str = "filtered_graph.html") -> str:
        """Create filtered visualization based on criteria."""
        filtered_graph = self.graph.copy()
        
        # Filter by node types
        if node_types:
            nodes_to_remove = [
                node for node, data in filtered_graph.nodes(data=True)
                if data.get('node_type') not in node_types
            ]
            filtered_graph.remove_nodes_from(nodes_to_remove)
        
        # Filter by frequency
        if min_frequency > 1:
            nodes_to_remove = [
                node for node, data in filtered_graph.nodes(data=True)
                if data.get('frequency', 1) < min_frequency
            ]
            filtered_graph.remove_nodes_from(nodes_to_remove)
        
        # Create visualization with filtered graph
        original_graph = self.graph
        self.graph = filtered_graph
        
        output_file = self.create_interactive_visualization()
        output_file = str(self.output_dir / output_name)
        
        # Restore original graph
        self.graph = original_graph
        
        return output_file
    
    def visualize(self, **kwargs) -> Tuple[str, Dict[str, Any]]:
        """Main method to create complete visualization."""
        data = self.load_structured_data()
        self.build_graph(data)
        
        html_file = self.create_interactive_visualization(**kwargs)
        stats = self.generate_statistics()
        
        # Save statistics
        stats_file = self.output_dir / "graph_statistics.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2)
        
        self.logger.info(f"Visualization saved to: {html_file}")
        self.logger.info(f"Statistics saved to: {stats_file}")
        
        return html_file, stats


def main():
    """Example usage of the KnowledgeGraphVisualizer."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Create knowledge graph from KEP structured data")
    parser.add_argument("--input", required=True, help="Path to structured.json file")
    parser.add_argument("--output-dir", default="graph_output", help="Output directory")
    parser.add_argument("--height", default="800px", help="Graph height")
    parser.add_argument("--width", default="100%", help="Graph width")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Create visualizer
    visualizer = KnowledgeGraphVisualizer(args.input, args.output_dir)
    
    # Generate visualization
    html_file, stats = visualizer.visualize(height=args.height, width=args.width)
    
    print(f"\nKnowledge Graph Generated!")
    print(f"HTML file: {html_file}")
    print(f"\nGraph Statistics:")
    print(f"- Total nodes: {stats['total_nodes']}")
    print(f"- Total edges: {stats['total_edges']}")
    print(f"- Node types: {stats['node_types']}")
    print(f"- Clustering coefficient: {stats['clustering_coefficient']:.3f}")
    
    if stats['most_connected_nodes']:
        print(f"\nMost connected nodes:")
        for node, centrality in stats['most_connected_nodes'][:5]:
            print(f"- {node}: {centrality:.3f}")


if __name__ == "__main__":
    main()