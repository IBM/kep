"""
Knowledge Graph Visualization Module

This module provides tools for creating knowledge graphs from KEP (Knowledge Extraction Pipeline) results.
It includes both fast static previews and full interactive visualizations with configurable relationships.

Main Components:
- FastGraphPreview: Quick static image generation for structure preview
- KnowledgeGraphVisualizer: Full interactive HTML visualizations with relationships

Quick Start:
    # Fast preview (2-3 seconds)
    from visualizer.fast_preview import FastGraphPreview
    preview = FastGraphPreview("runs/demo/structured.json", sample_size=10)
    preview.preview_graph(layout="hierarchical", show=True)
    
    # Full interactive graph
    from visualizer.knowledge_graph import KnowledgeGraphVisualizer  
    viz = KnowledgeGraphVisualizer("runs/demo/structured.json", "output_dir")
    viz.visualize()
"""

from .fast_preview import FastGraphPreview
from .knowledge_graph import KnowledgeGraphVisualizer

__all__ = ['FastGraphPreview', 'KnowledgeGraphVisualizer']
__version__ = '1.0.0'