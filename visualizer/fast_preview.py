"""
Fast Knowledge Graph Preview

Provides rapid static visualization of knowledge graph structure using matplotlib.
Designed for quick structure validation and preview before generating full interactive graphs.

Features:
- Fast sampling from structured.json (2-3 second generation)
- Multiple layout algorithms (hierarchical, spring, circular, shell)
- Static image output (PNG, SVG, PDF)
- Configurable relationship structure
- Auto-display capability

Example:
    preview = FastGraphPreview("runs/demo/structured.json", sample_size=10)
    preview.preview_graph(layout="hierarchical", show=True)
"""

import json
import subprocess
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Any

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx


class FastGraphPreview:
    """
    Fast static knowledge graph preview generator.
    
    This class creates quick static visualizations of knowledge graphs
    by sampling a subset of structured extraction results. It's designed
    for rapid iteration and structure validation.
    
    Attributes:
        structured_data_path (Path): Path to structured.json file
        sample_size (int): Number of entries to sample for preview
        node_colors (dict): Color mapping for different node types
        node_sizes (dict): Size mapping for different node types
    """
    
    def __init__(self, structured_data_path: str, sample_size: int = 15):
        """
        Initialize the fast preview generator.
        
        Args:
            structured_data_path: Path to KEP structured.json results file
            sample_size: Number of entries to sample (5-20 recommended for speed)
        """
        self.structured_data_path = Path(structured_data_path)
        self.sample_size = sample_size
        
        # Visual styling configuration
        self.node_colors = {
            'sources': '#FFEAA7',      # Yellow - document sources
            'materials': '#FF6B6B',    # Red - chemical compounds
            'applications': '#4ECDC4', # Teal - use cases
            'roles': '#45B7D1',        # Blue - functional roles
            'properties': '#96CEB4'    # Green - chemical properties
        }
        
        self.node_sizes = {
            'sources': 800,      # Largest - central documents
            'materials': 300,    # Medium - main entities
            'applications': 400, # Medium-large - important contexts
            'roles': 250,        # Small - functional descriptors
            'properties': 250    # Small - characteristics
        }
    
    def load_sample_data(self) -> List[Dict[str, Any]]:
        """
        Load a sample of structured data for quick preview.
        
        Takes the first N entries from structured.json to ensure
        fast processing while maintaining data variety.
        
        Returns:
            List of sampled extraction entries
            
        Raises:
            FileNotFoundError: If structured.json doesn't exist
            JSONDecodeError: If file contains invalid JSON
        """
        with open(self.structured_data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Take first N entries for speed and consistency
        sample = data[:self.sample_size]
        print(f"📊 Loaded sample: {len(sample)} entries (of {len(data)} total)")
        return sample
    
    def build_simple_graph(self, data: List[Dict[str, Any]]) -> nx.DiGraph:
        """
        Build a simple directed graph with hierarchical relationships.
        
        Creates the relationship structure:
        Sources → Materials → Applications/Roles/Properties
        
        This provides clear hierarchical visualization showing how
        documents contain materials, which have various applications,
        roles, and properties.
        
        Args:
            data: List of structured extraction entries
            
        Returns:
            NetworkX directed graph with hierarchical relationships
        """
        graph = nx.DiGraph()
        
        # Track entities by source for relationship building
        entities_by_source = defaultdict(lambda: defaultdict(set))
        
        # First pass: Add all nodes
        for entry in data:
            source = entry.get('Source', 'Unknown')
            extracted_data = entry.get('data', {})
            
            # Add source node (document/patent)
            if not graph.has_node(source):
                graph.add_node(source, 
                              node_type='sources',
                              label=self._truncate_label(source, 15))
            
            # Add entity nodes from extraction
            for category, items in extracted_data.items():
                for item in items:
                    if not item or not item.strip():
                        continue
                    
                    item_clean = item.strip()
                    
                    if not graph.has_node(item_clean):
                        graph.add_node(item_clean,
                                      node_type=category,
                                      label=self._truncate_label(item_clean, 20))
                    
                    # Track for relationship building
                    entities_by_source[source][category].add(item_clean)
        
        # Second pass: Add hierarchical relationships
        for source, categories in entities_by_source.items():
            materials = categories.get('materials', set())
            
            # Level 1: Source → Materials
            for material in materials:
                graph.add_edge(source, material, relationship='contains')
            
            # Level 2: Materials → Applications/Roles/Properties
            for material in materials:
                for other_type in ['applications', 'roles', 'properties']:
                    for other_entity in categories.get(other_type, set()):
                        graph.add_edge(material, other_entity, relationship='has')
        
        print(f"🔗 Graph built: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
        return graph
    
    def _truncate_label(self, text: str, max_length: int) -> str:
        """
        Truncate labels for better display readability.
        
        Args:
            text: Original text to truncate
            max_length: Maximum characters to display
            
        Returns:
            Truncated string with ellipsis if needed
        """
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
    
    def create_static_visualization(self, graph: nx.DiGraph, 
                                  layout: str = "spring",
                                  output_path: str = "graph_preview.png",
                                  figsize: Tuple[int, int] = (12, 8)) -> str:
        """
        Create static visualization using matplotlib.
        
        Generates a clean, publication-ready graph visualization with
        proper styling, legend, and layout.
        
        Args:
            graph: NetworkX graph to visualize
            layout: Layout algorithm ("spring", "hierarchical", "circular", "shell")
            output_path: Path for output image file
            figsize: Figure dimensions (width, height) in inches
            
        Returns:
            Path to generated image file
        """
        
        # Set up the plot with clean styling
        plt.figure(figsize=figsize, dpi=100)
        plt.clf()
        
        # Choose layout algorithm based on user preference
        if layout == "hierarchical":
            pos = self._hierarchical_layout(graph)
        elif layout == "circular":
            pos = nx.circular_layout(graph)
        elif layout == "shell":
            pos = self._shell_layout(graph)
        else:  # spring (force-directed)
            pos = nx.spring_layout(graph, k=2, iterations=50)
        
        # Prepare node visual attributes
        node_colors = []
        node_sizes = []
        labels = {}
        
        for node in graph.nodes():
            node_type = graph.nodes[node].get('node_type', 'materials')
            node_colors.append(self.node_colors.get(node_type, '#999999'))
            node_sizes.append(self.node_sizes.get(node_type, 300))
            labels[node] = graph.nodes[node].get('label', node)
        
        # Draw graph components
        nx.draw_networkx_nodes(graph, pos, 
                              node_color=node_colors,
                              node_size=node_sizes,
                              alpha=0.8,
                              edgecolors='black',
                              linewidths=0.5)
        
        nx.draw_networkx_edges(graph, pos,
                              edge_color='#666666',
                              arrows=True,
                              arrowsize=20,
                              arrowstyle='->',
                              alpha=0.6,
                              width=1.5)
        
        nx.draw_networkx_labels(graph, pos, labels,
                               font_size=8,
                               font_weight='bold',
                               font_family='sans-serif')
        
        # Create informative legend
        legend_elements = [
            mpatches.Patch(color=self.node_colors['sources'], label='Sources (Documents)'),
            mpatches.Patch(color=self.node_colors['materials'], label='Materials (Compounds)'),
            mpatches.Patch(color=self.node_colors['applications'], label='Applications (Uses)'),
            mpatches.Patch(color=self.node_colors['roles'], label='Roles (Functions)'),
            mpatches.Patch(color=self.node_colors['properties'], label='Properties (Characteristics)')
        ]
        plt.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1, 1))
        
        # Add title and styling
        plt.title(f"Knowledge Graph Preview - {layout.title()} Layout\n"
                 f"{graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges", 
                 fontsize=14, fontweight='bold', pad=20)
        plt.axis('off')
        plt.tight_layout()
        
        # Save with high quality
        output_file = Path(output_path)
        plt.savefig(output_file, dpi=150, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        
        print(f"💾 Static graph saved: {output_file}")
        return str(output_file)
    
    def _hierarchical_layout(self, graph: nx.DiGraph) -> Dict:
        """
        Create hierarchical layout with sources at top.
        
        Arranges nodes in clear hierarchy:
        - Level 0: Sources (top)
        - Level 1: Materials (middle) 
        - Level 2: Applications/Roles/Properties (bottom)
        
        Args:
            graph: NetworkX graph to layout
            
        Returns:
            Dictionary mapping nodes to (x, y) positions
        """
        pos = {}
        
        # Identify node types
        sources = [n for n in graph.nodes() if graph.nodes[n].get('node_type') == 'sources']
        materials = [n for n in graph.nodes() if graph.nodes[n].get('node_type') == 'materials']
        others = [n for n in graph.nodes() if graph.nodes[n].get('node_type') not in ['sources', 'materials']]
        
        # Level 0: Sources (top center)
        for i, source in enumerate(sources):
            pos[source] = (i * 2, 2)
        
        # Level 1: Materials (middle, spread horizontally)
        materials_per_row = max(8, len(materials) // 2)
        for i, material in enumerate(materials):
            x = (i % materials_per_row) * 1.5
            y = 1 - (i // materials_per_row) * 0.3
            pos[material] = (x, y)
        
        # Level 2: Others (bottom, compact arrangement)
        others_per_row = max(10, len(others) // 3)
        for i, other in enumerate(others):
            x = (i % others_per_row) * 1.2
            y = 0 - (i // others_per_row) * 0.25
            pos[other] = (x, y)
        
        return pos
    
    def _shell_layout(self, graph: nx.DiGraph) -> Dict:
        """
        Create shell layout with node types in concentric circles.
        
        Places node types in shells:
        - Center: Sources
        - Inner ring: Materials
        - Outer ring: Applications/Roles/Properties
        
        Args:
            graph: NetworkX graph to layout
            
        Returns:
            Dictionary mapping nodes to (x, y) positions
        """
        # Group nodes by type
        node_groups = defaultdict(list)
        for node in graph.nodes():
            node_type = graph.nodes[node].get('node_type', 'materials')
            node_groups[node_type].append(node)
        
        # Create concentric shells
        shells = []
        if node_groups['sources']:
            shells.append(node_groups['sources'])
        if node_groups['materials']:
            shells.append(node_groups['materials'])
        
        # Combine other types in outer shell
        others = []
        for node_type in ['applications', 'roles', 'properties']:
            others.extend(node_groups[node_type])
        if others:
            shells.append(others)
        
        return nx.shell_layout(graph, shells)
    
    def preview_graph(self, layout: str = "spring", 
                     output_format: str = "png",
                     show: bool = False) -> str:
        """
        Generate complete preview visualization.
        
        Main entry point for creating fast graph previews. Handles the
        complete pipeline from data loading to image generation.
        
        Args:
            layout: Layout algorithm ("spring", "hierarchical", "circular", "shell")
            output_format: Image format ("png", "svg", "pdf")
            show: Whether to auto-open the generated image
            
        Returns:
            Path to generated image file
            
        Raises:
            ValueError: If no data found or graph is empty
        """
        
        # Load and validate sample data
        data = self.load_sample_data()
        if not data:
            raise ValueError("No data found in structured file")
        
        # Build graph with relationships
        graph = self.build_simple_graph(data)
        if graph.number_of_nodes() == 0:
            raise ValueError("No nodes found in sample data")
        
        # Generate visualization
        output_file = f"graph_preview_{layout}.{output_format}"
        result_path = self.create_static_visualization(graph, layout, output_file)
        
        # Auto-display if requested
        if show:
            self._show_image(result_path)
        
        return result_path
    
    def _show_image(self, image_path: str):
        """
        Open image in default system viewer.
        
        Cross-platform image opening with graceful fallback.
        
        Args:
            image_path: Path to image file to open
        """
        try:
            if sys.platform == "darwin":  # macOS
                subprocess.run(["open", image_path])
            elif sys.platform == "win32":  # Windows
                subprocess.run(["start", image_path], shell=True)
            else:  # Linux
                subprocess.run(["xdg-open", image_path])
            print(f"🖼️  Opening image: {image_path}")
        except Exception as e:
            print(f"⚠️  Could not auto-open image: {e}")
            print(f"   Manually open: {image_path}")


# Layout algorithm recommendations for different use cases
LAYOUT_RECOMMENDATIONS = {
    "structure_analysis": "hierarchical",
    "relationship_discovery": "spring", 
    "simple_overview": "circular",
    "type_comparison": "shell"
}