#!/usr/bin/env python3
"""
05_pipeline_demo.py - KEP Pipeline Execution Demo

This script demonstrates how to run the complete KEP pipeline,
from PDF input to structured JSON output.

Features:
- Automated pipeline execution
- Real-time progress monitoring
- Configuration validation
- Error handling and recovery
- Results preview and analysis

Usage:
    python "05_pipeline_demo.py"                    # Interactive demo
    python "05_pipeline_demo.py" --auto             # Auto-run with defaults
    python "05_pipeline_demo.py" --config custom    # Use custom configuration
    python "05_pipeline_demo.py" --dry-run          # Show command without running
"""

import sys
import os
import subprocess
import json
import time
from pathlib import Path
import argparse

def print_header(title):
    """Print formatted header"""
    print(f"\n{'='*70}")
    print(f" {title}")
    print('='*70)

def print_step(step_num, title):
    """Print step header"""
    print(f"\n{step_num}️⃣ {title}")
    print("-" * (len(title) + 4))

def find_kep_root():
    """Find KEP root directory"""
    current_dir = Path.cwd()
    if current_dir.name == "Quick Start":
        return current_dir.parent
    return current_dir

def check_prerequisites():
    """Check if system is ready for pipeline execution"""
    print_step("1", "Prerequisites Check")
    
    kep_root = find_kep_root()
    issues = []
    
    # Check run_pipeline.py
    pipeline_script = kep_root / "run_pipeline.py"
    if not pipeline_script.exists():
        issues.append("run_pipeline.py not found")
    else:
        print("✅ Pipeline script found")
    
    # Check schemas directory
    schemas_dir = kep_root / "schemas"
    if not schemas_dir.exists():
        issues.append("schemas directory not found")
    else:
        schema_files = list(schemas_dir.glob("*.json"))
        if schema_files:
            print(f"✅ Found {len(schema_files)} schema files")
        else:
            issues.append("No schema files found")
    
    # Check for PDFs
    pdfs_dir = kep_root / "pdfs"
    if not pdfs_dir.exists():
        issues.append("pdfs directory not found")
    else:
        pdf_files = list(pdfs_dir.glob("*.pdf"))
        if pdf_files:
            total_size = sum(f.stat().st_size for f in pdf_files) / (1024 * 1024)
            print(f"✅ Found {len(pdf_files)} PDF files ({total_size:.1f} MB)")
        else:
            issues.append("No PDF files found in ./pdfs")
    
    # Check LLM configuration
    watsonx_config = kep_root / "llm" / "watsonx" / "config.yaml"
    if watsonx_config.exists():
        print("✅ WatsonX configuration found")
    else:
        issues.append("WatsonX configuration missing")
    
    if issues:
        print("\n❌ Issues found:")
        for issue in issues:
            print(f"   • {issue}")
        
        print("\n🔧 Quick fixes:")
        if "pdfs directory not found" in issues:
            print("   • Create pdfs directory: mkdir pdfs")
        if "No PDF files found" in issues:
            print("   • Add PDF files to ./pdfs directory")
        if "No schema files found" in issues:
            print("   • Check schemas in ./schemas directory")
        
        return False
    
    print("\n✅ All prerequisites met - ready to run!")
    return True

def discover_available_models():
    """Discover available models using connection test"""
    print_step("2", "Model Discovery")
    
    try:
        # Import KEP modules
        kep_root = find_kep_root()
        if str(kep_root) not in sys.path:
            sys.path.insert(0, str(kep_root))
        
        from llm.factory import LLMFactory
        from ibm_watsonx_ai.foundation_models import ModelInference
        import yaml
        
        # Load config
        config_path = kep_root / "llm" / "watsonx" / "config.yaml"
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        api_key = os.getenv('WATSONX_APIKEY') or config.get('apikey')
        project_id = os.getenv('WATSONX_PROJECT_ID') or config.get('project_id')
        url = os.getenv('WATSONX_URL') or config.get('url')
        
        print("🔍 Discovering available models...")
        
        try:
            # Use invalid model to get model list
            model = ModelInference(
                model_id="invalid-model-discovery",
                params={'max_new_tokens': 50},
                credentials={"url": url, "apikey": api_key},
                project_id=project_id,
            )
        except Exception as e:
            error_msg = str(e)
            if "Supported models:" in error_msg:
                start = error_msg.find("Supported models: [") + len("Supported models: [")
                end = error_msg.find("]", start)
                models_str = error_msg[start:end]
                
                models = [m.strip().strip("'\"") for m in models_str.split(',')]
                models = [m for m in models if m]
                
                print(f"✅ Found {len(models)} available models")
                
                # Recommend best models
                recommended = []
                priority_models = [
                    'mistralai/mistral-large',
                    'meta-llama/llama-3-3-70b-instruct',
                    'ibm/granite-13b-instruct-v2',
                    'meta-llama/llama-3-2-3b-instruct'
                ]
                
                for model in priority_models:
                    if model in models:
                        recommended.append(model)
                
                if recommended:
                    print(f"⭐ Recommended for KEP: {recommended[0]}")
                    return models, recommended[0]
                else:
                    print(f"⭐ Using first available: {models[0]}")
                    return models, models[0]
            else:
                print(f"❌ Model discovery failed: {e}")
                return [], "mistralai/mistral-large"  # Default fallback
                
    except ImportError:
        print("❌ Cannot discover models - ibm_watsonx_ai not available")
        return [], "mistralai/mistral-large"
    except Exception as e:
        print(f"❌ Model discovery error: {e}")
        return [], "mistralai/mistral-large"

def select_configuration(auto_mode=False):
    """Select pipeline configuration"""
    print_step("3", "Configuration Selection")
    
    kep_root = find_kep_root()
    
    # Default configuration
    config = {
        "pdf_dir": "./pdfs",
        "work_dir": "./runs/quick_start_demo",
        "provider": "watsonx",
        "model_id": "mistralai/mistral-large",
        "prompt_mode": "few",
        "debug_io": True
    }
    
    # Find available schemas
    schemas_dir = kep_root / "schemas"
    schema_files = list(schemas_dir.glob("*.json"))
    
    # Use PFAS schemas specifically
    config["cls_schema"] = "./schemas/pfas_classification.json"
    config["ext_schema"] = "./schemas/pfas_extraction.json"
    
    # Get recommended model
    models, recommended_model = discover_available_models()
    if recommended_model:
        config["model_id"] = recommended_model
    
    if auto_mode:
        print("🤖 Using automatic configuration:")
    else:
        print("📋 Default configuration:")
    
    for key, value in config.items():
        print(f"   {key}: {value}")
    
    if not auto_mode:
        print("\n🔧 Customization options:")
        print("   p - Change prompt mode (zero/few)")
        print("   m - Change model")
        print("   s - Change schemas")
        print("   d - Change output directory")
        print("   Enter - Use defaults")
        
        choice = input("\nCustomize configuration? ").lower()
        
        if choice == 'p':
            mode = input("Prompt mode (zero/few): ").lower()
            if mode in ['zero', 'few']:
                config["prompt_mode"] = mode
        
        elif choice == 'm':
            if models:
                print("\n📋 Available models:")
                for i, model in enumerate(models[:10]):  # Show first 10
                    print(f"   {i+1}. {model}")
                try:
                    selection = int(input("Select model number: ")) - 1
                    if 0 <= selection < len(models):
                        config["model_id"] = models[selection]
                except ValueError:
                    print("Invalid selection, using default")
        
        elif choice == 's':
            print("\n📋 Available schemas:")
            for i, schema in enumerate(schema_files):
                print(f"   {i+1}. {schema.name}")
            
            try:
                cls_choice = int(input("Classification schema number: ")) - 1
                ext_choice = int(input("Extraction schema number: ")) - 1
                
                if 0 <= cls_choice < len(schema_files):
                    config["cls_schema"] = f"./schemas/{schema_files[cls_choice].name}"
                if 0 <= ext_choice < len(schema_files):
                    config["ext_schema"] = f"./schemas/{schema_files[ext_choice].name}"
            except ValueError:
                print("Invalid selection, using defaults")
        
        elif choice == 'd':
            work_dir = input("Output directory: ").strip()
            if work_dir:
                config["work_dir"] = work_dir
    
    return config

def generate_pipeline_command(config):
    """Generate the pipeline command"""
    cmd_parts = [
        "python", "run_pipeline.py",
        "--pdf-dir", config["pdf_dir"],
        "--cls-schema", config["cls_schema"],
        "--ext-schema", config["ext_schema"],
        "--work-dir", config["work_dir"],
        "--provider", config["provider"],
        "--model-id", config["model_id"],
        "--prompt-mode", config["prompt_mode"]
    ]
    
    if config.get("debug_io"):
        cmd_parts.append("--debug-io")
    
    return cmd_parts

def estimate_execution_time(kep_root, config):
    """Estimate pipeline execution time"""
    print_step("4", "Execution Time Estimation")
    
    # Count PDFs
    pdfs_dir = kep_root / config["pdf_dir"].replace("./", "")
    pdf_files = list(pdfs_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("❌ No PDF files found")
        return 0
    
    # Estimate based on file sizes and complexity
    total_size_mb = sum(f.stat().st_size for f in pdf_files) / (1024 * 1024)
    
    # Rough estimates (very approximate)
    conversion_time = len(pdf_files) * 30  # ~30 seconds per PDF for conversion
    classification_time = total_size_mb * 20  # ~20 seconds per MB for classification
    extraction_time = total_size_mb * 40  # ~40 seconds per MB for extraction (more complex)
    
    total_estimate = conversion_time + classification_time + extraction_time
    
    print(f"📊 Estimation for {len(pdf_files)} PDFs ({total_size_mb:.1f} MB):")
    print(f"   • Conversion: ~{conversion_time//60}m {conversion_time%60}s")
    print(f"   • Classification: ~{classification_time//60}m {classification_time%60}s")
    print(f"   • Extraction: ~{extraction_time//60}m {extraction_time%60}s")
    print(f"   • Total estimate: ~{total_estimate//60}m {total_estimate%60}s")
    
    print(f"\n💡 Actual time may vary based on:")
    print(f"   • Model response speed")
    print(f"   • Document complexity")
    print(f"   • Network conditions")
    print(f"   • Number of relevant paragraphs found")
    
    return total_estimate

def run_pipeline(config, dry_run=False):
    """Execute the pipeline"""
    print_step("5", "Pipeline Execution")
    
    kep_root = find_kep_root()
    cmd = generate_pipeline_command(config)
    
    print("🚀 Pipeline Command:")
    print("   " + " ".join(cmd))
    
    if dry_run:
        print("\n🔍 Dry run mode - command shown above")
        print("💡 Remove --dry-run to execute the pipeline")
        return True
    
    # Confirm execution
    print(f"\n📁 Output will be saved to: {config['work_dir']}")
    
    confirm = input("\n🚀 Execute pipeline? (y/n): ").lower()
    if confirm != 'y':
        print("❌ Pipeline execution cancelled")
        return False
    
    print("\n▶️ Starting pipeline execution...")
    print("=" * 50)
    
    start_time = time.time()
    
    try:
        # Execute pipeline
        process = subprocess.Popen(
            cmd,
            cwd=kep_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Stream output in real-time
        for line in process.stdout:
            print(line.rstrip())
        
        # Wait for completion
        return_code = process.wait()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print("=" * 50)
        print(f"⏱️ Execution completed in {execution_time//60:.0f}m {execution_time%60:.0f}s")
        
        if return_code == 0:
            print("✅ Pipeline executed successfully!")
            return True
        else:
            print(f"❌ Pipeline failed with exit code {return_code}")
            return False
            
    except KeyboardInterrupt:
        print("\n⚠️ Pipeline interrupted by user")
        process.terminate()
        return False
    except Exception as e:
        print(f"\n❌ Execution error: {e}")
        return False

def preview_results(config):
    """Preview pipeline results"""
    print_step("6", "Results Preview")
    
    kep_root = find_kep_root()
    work_dir = kep_root / config["work_dir"].replace("./", "")
    
    if not work_dir.exists():
        print("❌ Results directory not found")
        return
    
    # Check output files
    output_files = {
        "ingest/all_paragraphs.json": "Converted PDF paragraphs",
        "classified_full.json": "All paragraphs with classifications",
        "classified_relevant.json": "Relevant paragraphs only",
        "structured.json": "Final structured data",
        "general_metadata.json": "Processing statistics",
        "llm_metadata.json": "Model and prompt information",
        "run.log": "Execution log"
    }
    
    print("📊 Output Files:")
    for file_path, description in output_files.items():
        full_path = work_dir / file_path
        if full_path.exists():
            if full_path.suffix == '.json':
                try:
                    with open(full_path, 'r') as f:
                        data = json.load(f)
                    
                    if isinstance(data, list):
                        print(f"   ✅ {file_path}: {len(data)} items")
                    else:
                        print(f"   ✅ {file_path}: {description}")
                except:
                    print(f"   ⚠️ {file_path}: exists but couldn't read")
            else:
                size_kb = full_path.stat().st_size / 1024
                print(f"   ✅ {file_path}: {size_kb:.1f} KB")
        else:
            print(f"   ❌ {file_path}: missing")
    
    # Show summary statistics
    metadata_file = work_dir / "general_metadata.json"
    if metadata_file.exists():
        try:
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            print(f"\n📈 Processing Summary:")
            if isinstance(metadata, dict):
                for key, value in metadata.items():
                    if any(word in key.lower() for word in ['total', 'count', 'time']):
                        print(f"   • {key}: {value}")
        except:
            pass
    
    # Preview structured data
    structured_file = work_dir / "structured.json"
    if structured_file.exists():
        try:
            with open(structured_file, 'r') as f:
                structured_data = json.load(f)
            
            print(f"\n🏗️ Structured Data Preview:")
            if isinstance(structured_data, list) and structured_data:
                # Show first item structure
                first_item = structured_data[0]
                if isinstance(first_item, dict):
                    print("   Structure of extracted data:")
                    for key in first_item.keys():
                        print(f"     • {key}")
                
                print(f"\n   📝 Sample extraction:")
                print(f"   {json.dumps(first_item, indent=6)[:300]}...")
        except:
            print("   ⚠️ Could not preview structured data")
    
    print(f"\n🔍 Full results available in: {work_dir}")

def main():
    """Main pipeline demo function"""
    parser = argparse.ArgumentParser(description='KEP Pipeline Demo')
    parser.add_argument('--auto', action='store_true',
                       help='Run automatically with defaults')
    parser.add_argument('--config', default='default',
                       help='Configuration preset to use')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show command without executing')
    
    args = parser.parse_args()
    
    print("🚀 KEP Pipeline Demo")
    print("Experience the complete knowledge extraction process!")
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please address issues before continuing.")
        return False
    
    # Select configuration
    config = select_configuration(args.auto)
    
    # Estimate execution time
    kep_root = find_kep_root()
    estimate_execution_time(kep_root, config)
    
    # Run pipeline
    success = run_pipeline(config, args.dry_run)
    
    if success and not args.dry_run:
        # Preview results
        preview_results(config)
        
        print_header("🎉 Demo Complete!")
        print(f"""
Congratulations! You've successfully run the KEP pipeline.

📊 What happened:
   1. PDFs were converted to structured paragraphs
   2. Each paragraph was classified for relevance
   3. Relevant content was extracted to structured JSON
   4. Complete audit trail and metadata were generated

🎯 Next steps:
   • Analyze results in {config['work_dir']}
   • Experiment with different schemas
   • Process your own research documents
   • Scale up to larger document collections

📚 Continue learning:
   python "06_results_explorer.py" - Deep dive into results
   python "07_custom_schemas.py"   - Create domain-specific schemas
""")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)