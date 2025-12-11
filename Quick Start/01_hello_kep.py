#!/usr/bin/env python3
"""
01_hello_kep.py - Introduction to the Knowledge Extraction Pipeline

This script provides a comprehensive introduction to KEP, explaining its
capabilities, architecture, and use cases.

Run this script to learn:
- What KEP does and why it's useful
- How the pipeline works (Convert → Classify → Extract)
- Real-world applications and examples
- System requirements and setup overview

Usage:
    python "01_hello_kep.py"
"""

import sys
import os
from pathlib import Path

# ASCII Art Logo
LOGO = """
    ██╗  ██╗███████╗██████╗ 
    ██║ ██╔╝██╔════╝██╔══██╗
    █████╔╝ █████╗  ██████╔╝
    ██╔═██╗ ██╔══╝  ██╔═══╝ 
    ██║  ██╗███████╗██║     
    ╚═╝  ╚═╝╚══════╝╚═╝     
                            
Knowledge Extraction Pipeline
"""

def print_header(title, char="=", width=60):
    """Print a formatted header"""
    print()
    print(char * width)
    print(f" {title}")
    print(char * width)

def print_section(title, char="-", width=50):
    """Print a formatted section header"""
    print()
    print(f"{title}")
    print(char * len(title))

def main():
    """Main introduction to KEP"""
    
    # Welcome
    print(LOGO)
    print("🚀 Welcome to the Knowledge Extraction Pipeline!")
    print("   A scalable system for transforming unstructured scientific")
    print("   documents into structured knowledge using foundation models.")
    print()
    
    # What is KEP?
    print_header("📋 What is KEP?")
    print()
    print("The Knowledge Extraction Pipeline (KEP) is an end-to-end system that")
    print("processes scientific documents and extracts structured information using")
    print("Large Language Models (LLMs).")
    print()
    print("🎯 Core Mission:")
    print("   Transform PDFs full of unstructured text into clean,")
    print("   structured JSON data that follows YOUR custom schema.")
    
    # How it works
    print_header("🔄 How KEP Works - The Three-Stage Pipeline")
    print()
    print("KEP follows a simple but powerful three-stage process:")
    print()
    print("┌─────────────┐    ┌──────────────┐    ┌─────────────┐")
    print("│   CONVERT   │ -> │   CLASSIFY   │ -> │   EXTRACT   │")
    print("│   PDF → MD  │    │ Relevant vs  │    │ Structured  │")
    print("│   + Chunks  │    │ Irrelevant   │    │    JSON     │")
    print("└─────────────┘    └──────────────┘    └─────────────┘")
    print()
    
    print_section("Stage 1: CONVERT 📄")
    print("• Converts PDF files to Markdown using Docling")
    print("• Splits documents into logical paragraphs or chunks")
    print("• Preserves structure while making text LLM-friendly")
    print("• Handles tables, figures, and complex layouts")
    
    print_section("Stage 2: CLASSIFY 🏷️")
    print("• Uses LLM to classify each paragraph as 'relevant' or 'irrelevant'")
    print("• Based on YOUR classification schema and examples")
    print("• Filters out noise, keeping only content that matters")
    print("• Supports both zero-shot and few-shot classification")
    
    print_section("Stage 3: EXTRACT 🏗️")
    print("• Processes only the 'relevant' paragraphs from Stage 2")
    print("• Extracts structured data following YOUR custom JSON schema")
    print("• Returns clean, consistent JSON output")
    print("• Includes metadata and provenance tracking")
    
    # Key Features
    print_header("✨ Key Features")
    print()
    features = [
        ("🌊 Fully Streamed", "No intermediate databases, minimal memory usage"),
        ("🔌 Provider Agnostic", "Works with WatsonX, RITS, and extensible to others"),
        ("📋 Schema-Driven", "Define your own classification and extraction schemas"),
        ("🎯 Few-Shot Learning", "Include examples directly in schema files"),
        ("📊 Rich Logging", "Comprehensive metadata and debugging support"),
        ("⚡ Scalable", "Process single PDFs or large document collections"),
        ("🔧 Customizable", "Flexible chunking, prompting, and model selection"),
        ("🛡️ Robust", "Error handling, retry logic, and graceful degradation")
    ]
    
    for feature, description in features:
        print(f"   {feature}: {description}")
    
    # Real-world applications
    print_header("🔬 Real-World Applications")
    print()
    
    applications = [
        ("🧪 Materials Science", "Extract material properties, synthesis methods, performance metrics"),
        ("💊 Drug Discovery", "Identify compounds, mechanisms, clinical trial results"),
        ("🌱 Environmental Research", "Parse pollution data, environmental impacts, policy measures"),
        ("⚡ Energy Research", "Extract battery specifications, solar cell efficiency, energy storage"),
        ("🏭 Manufacturing", "Process protocols, quality metrics, operational parameters"),
        ("📚 Literature Reviews", "Systematic extraction across hundreds of research papers"),
        ("🏥 Medical Research", "Clinical data, treatment outcomes, diagnostic information"),
        ("🔬 Chemical Engineering", "Process conditions, reaction parameters, optimization results")
    ]
    
    for domain, description in applications:
        print(f"   {domain}")
        print(f"      {description}")
        print()
    
    # Example workflow
    print_header("📖 Example: Battery Research Workflow")
    print()
    print("Scenario: You have 50 PDFs about lithium-ion battery materials")
    print("Goal: Extract all battery performance data into a structured database")
    print()
    print("1️⃣ SETUP:")
    print("   • Create classification schema: 'battery_related' vs 'not_battery_related'")
    print("   • Create extraction schema: materials, capacity, voltage, cycle_life")
    print("   • Add example paragraphs to schemas for few-shot learning")
    print()
    print("2️⃣ EXECUTION:")
    print("   • Run: python run_pipeline.py --pdf-dir ./battery_pdfs \\")
    print("           --cls-schema ./schemas/battery_classification.json \\")
    print("           --ext-schema ./schemas/battery_extraction.json")
    print()
    print("3️⃣ RESULTS:")
    print("   • classified_relevant.json: Only battery-related paragraphs")
    print("   • structured.json: Clean JSON with all extracted data")
    print("   • Rich metadata: Processing stats, model info, debug logs")
    print()
    print("4️⃣ IMPACT:")
    print("   • Hours → Minutes: What took days of manual reading now takes minutes")
    print("   • Consistency: No human bias or fatigue in extraction")
    print("   • Scalability: Process thousands of papers with same effort")
    print("   • Traceability: Every extraction links back to source paragraph")
    
    # Architecture overview
    print_header("🏗️ System Architecture")
    print()
    print("KEP is built with a modular, extensible architecture:")
    print()
    print("📁 Core Components:")
    print("   • ingest/: PDF processing and text chunking (Docling integration)")
    print("   • llm/: Provider-agnostic LLM interfaces (WatsonX, RITS, extensible)")
    print("   • extractor/: Classification and extraction logic")
    print("   • prompter/: Template-based prompting system")
    print("   • common/: Logging, metadata, and utility functions")
    print()
    print("🔌 LLM Provider System:")
    print("   • Factory pattern for easy provider switching")
    print("   • Unified interface regardless of backend")
    print("   • Environment-based configuration")
    print("   • Extensible to new providers (OpenAI, Anthropic, etc.)")
    print()
    print("📋 Schema System:")
    print("   • JSON-based schema definitions")
    print("   • Embedded examples for few-shot learning")
    print("   • Validation and error checking")
    print("   • Version control friendly")
    
    # What makes KEP special
    print_header("🌟 What Makes KEP Special?")
    print()
    special_features = [
        ("Research-First Design", "Built specifically for scientific document processing"),
        ("Production Ready", "Robust error handling, logging, and monitoring"),
        ("Schema-Driven Approach", "Your domain knowledge guides the extraction"),
        ("Transparent Processing", "Full audit trail from input to output"),
        ("Provider Independence", "Not locked into any single LLM service"),
        ("Extensible Architecture", "Easy to add new providers, models, or features"),
        ("Example-Driven Learning", "Few-shot examples improve accuracy significantly"),
        ("Comprehensive Tooling", "Complete ecosystem from setup to analysis")
    ]
    
    for feature, description in special_features:
        print(f"   🎯 {feature}:")
        print(f"      {description}")
        print()
    
    # System requirements
    print_header("💻 System Requirements")
    print()
    print("📋 Minimum Requirements:")
    print("   • Python 3.8 or higher")
    print("   • 4GB RAM (8GB+ recommended for large documents)")
    print("   • Internet connection for LLM API calls")
    print("   • ~500MB disk space for dependencies")
    print()
    print("🔑 Required Access:")
    print("   • IBM Cloud account with WatsonX access, OR")
    print("   • RITS API access, OR")
    print("   • Custom LLM provider (extensible)")
    print()
    print("📦 Dependencies:")
    print("   • ibm-watsonx-ai: WatsonX integration")
    print("   • docling: Advanced PDF processing")
    print("   • nltk: Natural language processing")
    print("   • pyyaml: Configuration management")
    print("   • rich: Beautiful terminal output")
    print("   • See requirements.txt for complete list")
    
    # Next steps
    print_header("🎯 Next Steps")
    print()
    print("Ready to get started? Here's your roadmap:")
    print()
    print("1️⃣ Environment Check:")
    print("   python \"02_environment_check.py\"")
    print("   → Verify Python, dependencies, and KEP installation")
    print()
    print("2️⃣ Test Connections:")
    print("   python \"03_test_connections.py\"")
    print("   → Validate LLM provider access and authentication")
    print()
    print("3️⃣ Understand Schemas:")
    print("   python \"04_understanding_schemas.py\"")
    print("   → Learn how to create effective schemas")
    print()
    print("4️⃣ Run Demo Pipeline:")
    print("   python \"05_pipeline_demo.py\"")
    print("   → Execute your first complete extraction")
    print()
    print("5️⃣ Explore Results:")
    print("   python \"06_results_explorer.py\"")
    print("   → Understand and analyze pipeline outputs")
    print()
    print("6️⃣ Create Custom Schemas:")
    print("   python \"07_custom_schemas.py\"")
    print("   → Build schemas for your specific domain")
    print()
    print("7️⃣ Advanced Diagnostics:")
    print("   python \"08_troubleshooting.py\"")
    print("   → Comprehensive system health check")
    
    # Success stories
    print_header("📈 Success Stories")
    print()
    print("KEP has been successfully used for:")
    print()
    print("🏆 PFAS Research:")
    print("   • Processed 1000+ environmental papers")
    print("   • Extracted chemical properties and health impacts")
    print("   • Reduced analysis time from weeks to hours")
    print()
    print("🏆 Battery Materials:")
    print("   • Analyzed 500+ papers on energy storage")
    print("   • Built comprehensive materials database")
    print("   • Identified performance trends across decades")
    print()
    print("🏆 Synthesis Protocols:")
    print("   • Extracted reaction conditions from 200+ papers")
    print("   • Standardized diverse reporting formats")
    print("   • Enabled systematic optimization studies")
    
    # Getting help
    print_header("🆘 Getting Help")
    print()
    print("If you need assistance:")
    print()
    print("📧 Contact the KEP Team:")
    print("   • Viviane Torres (Manager): vivianet@br.ibm.com")
    print("   • Marcelo Archanjo: marcelo.archanjo@ibm.com")
    print("   • Anaximandro Souza: anaximandrosouza@ibm.com")
    print()
    print("📚 Documentation:")
    print("   • README.md: Complete system documentation")
    print("   • UNIFIED_SETUP.md: Detailed setup instructions")
    print("   • CLAUDE.md: Developer guidance")
    print()
    print("🔧 Diagnostics:")
    print("   • Run: python \"08_troubleshooting.py\"")
    print("   • Check logs in runs/*/run.log")
    print("   • Enable --debug-io for detailed LLM traces")
    
    # Conclusion
    print_header("🎉 Ready to Extract Knowledge?")
    print()
    print("You now understand what KEP can do for your research!")
    print()
    print("KEP transforms the tedious task of reading hundreds of papers")
    print("into an automated, scalable, and accurate extraction process.")
    print()
    print("🚀 Start your journey:")
    print("   python \"02_environment_check.py\"")
    print()
    print("🌟 Join the community of researchers using KEP to accelerate")
    print("   scientific discovery through automated knowledge extraction!")
    print()
    print("=" * 60)
    print(" Happy Knowledge Extracting! 🧠✨")
    print("=" * 60)

if __name__ == "__main__":
    main()