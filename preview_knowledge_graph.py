#!/usr/bin/env python3
"""
Fast Knowledge Graph Preview - Command Line Interface

Creates quick static images of knowledge graphs from KEP results.
No interactive features - just fast, simple visualization for structure preview.

Usage:
    python preview_knowledge_graph.py runs/demo
    python preview_knowledge_graph.py runs/demo --sample 10 --show
    python preview_knowledge_graph.py runs/demo --layout hierarchical --format svg
"""

import argparse
import sys
from pathlib import Path

# Import the visualization module
from visualizer.fast_preview import FastGraphPreview


def main():
    parser = argparse.ArgumentParser(
        description="Generate fast static preview of knowledge graph",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python preview_knowledge_graph.py runs/demo
  python preview_knowledge_graph.py runs/demo --sample 10 --layout hierarchical
  python preview_knowledge_graph.py runs/demo --show --format svg
        """
    )
    
    parser.add_argument(
        "results_dir",
        help="Path to KEP results directory (should contain structured.json)"
    )
    
    parser.add_argument(
        "--sample", "-s",
        type=int,
        default=15,
        help="Number of entries to sample from structured.json (default: 15)"
    )
    
    parser.add_argument(
        "--layout", "-l",
        choices=["spring", "hierarchical", "circular", "shell"],
        default="hierarchical",
        help="Layout algorithm (default: hierarchical)"
    )
    
    parser.add_argument(
        "--format", "-f",
        choices=["png", "svg", "pdf"],
        default="png",
        help="Output format (default: png)"
    )
    
    parser.add_argument(
        "--show",
        action="store_true",
        help="Automatically open the generated image"
    )
    
    parser.add_argument(
        "--size",
        nargs=2,
        type=int,
        default=[12, 8],
        help="Figure size as width height (default: 12 8)"
    )
    
    args = parser.parse_args()
    
    # Validate inputs
    results_path = Path(args.results_dir)
    if not results_path.exists():
        print(f"❌ Error: Results directory '{results_path}' does not exist")
        return 1
    
    structured_file = results_path / "structured.json"
    if not structured_file.exists():
        print(f"❌ Error: No structured.json found in '{results_path}'")
        return 1
    
    try:
        print(f"⚡ Fast Knowledge Graph Preview")
        print(f"📁 Input: {structured_file}")
        print(f"📊 Sample size: {args.sample}")
        print(f"🎨 Layout: {args.layout}")
        
        # Create preview generator
        preview = FastGraphPreview(str(structured_file), args.sample)
        
        # Generate preview
        result_path = preview.preview_graph(
            layout=args.layout,
            output_format=args.format,
            show=args.show
        )
        
        print(f"✅ Preview generated: {result_path}")
        
        if not args.show:
            print(f"💡 Use --show to auto-open the image")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error creating preview: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())