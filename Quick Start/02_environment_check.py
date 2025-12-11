#!/usr/bin/env python3
"""
02_environment_check.py - KEP Environment Validation

This script validates your Python environment and KEP installation,
checking all dependencies and configuration requirements.

Run this script to verify:
- Python version compatibility
- Required packages installation
- KEP directory structure
- Configuration files presence
- Import functionality

Usage:
    python "02_environment_check.py"
    python "02_environment_check.py" --verbose    # Detailed output
    python "02_environment_check.py" --fix        # Auto-fix issues
"""

import sys
import os
import subprocess
from pathlib import Path
import importlib.util
import argparse

def print_header(title):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print('='*60)

def print_check(status, message, details=""):
    """Print check result with consistent formatting"""
    status_char = "✅" if status else "❌"
    print(f"{status_char} {message}")
    if details:
        print(f"   {details}")

def check_python_version():
    """Check if Python version is compatible"""
    print_header("🐍 Python Version Check")
    
    version = sys.version_info
    required_major, required_minor = 3, 8
    
    current = f"{version.major}.{version.minor}.{version.micro}"
    required = f"{required_major}.{required_minor}+"
    
    is_compatible = version >= (required_major, required_minor)
    
    print_check(is_compatible, f"Python version: {current}")
    
    if not is_compatible:
        print(f"   ⚠️ KEP requires Python {required}")
        print(f"   💡 Please upgrade your Python installation")
        return False
    
    print(f"   ✨ Perfect! Python {current} is fully compatible")
    return True

def check_kep_installation():
    """Check KEP directory structure and core files"""
    print_header("📁 KEP Installation Check")
    
    # Determine KEP root directory
    current_dir = Path.cwd()
    if current_dir.name == "Quick Start":
        kep_root = current_dir.parent
    else:
        kep_root = current_dir
    
    print(f"🔍 Checking KEP installation at: {kep_root}")
    
    # Required directories
    required_dirs = [
        'llm', 'schemas', 'extractor', 'ingest', 'common', 'prompter'
    ]
    
    # Required files
    required_files = [
        'run_pipeline.py',
        'requirements.txt',
        'README.md',
        'llm/factory.py',
        'llm/base.py',
        'extractor/pipeline.py',
        'ingest/pdf_converter.py'
    ]
    
    all_good = True
    
    # Check directories
    print("\n📂 Directory Structure:")
    for dir_name in required_dirs:
        dir_path = kep_root / dir_name
        exists = dir_path.exists() and dir_path.is_dir()
        print_check(exists, f"Directory: {dir_name}/")
        if not exists:
            all_good = False
    
    # Check core files
    print("\n📄 Core Files:")
    for file_name in required_files:
        file_path = kep_root / file_name
        exists = file_path.exists() and file_path.is_file()
        print_check(exists, f"File: {file_name}")
        if not exists:
            all_good = False
    
    # Check configuration files
    print("\n⚙️ Configuration Files:")
    config_files = [
        'llm/watsonx/config.yaml',
        'llm/rits/config.yaml'
    ]
    
    for config_file in config_files:
        config_path = kep_root / config_file
        exists = config_path.exists()
        print_check(exists, f"Config: {config_file}")
        
        if exists:
            # Check for placeholder values
            try:
                with open(config_path, 'r') as f:
                    content = f.read()
                has_placeholders = 'YOUR_' in content
                if has_placeholders:
                    print(f"   ⚠️ Contains placeholder values - needs configuration")
                else:
                    print(f"   ✨ Configured with real values")
            except Exception as e:
                print(f"   ⚠️ Could not read config: {e}")
    
    if all_good:
        print(f"\n🎉 KEP installation is complete and properly structured!")
    else:
        print(f"\n❌ KEP installation has missing components")
        print(f"   💡 Ensure you're in the correct directory")
        print(f"   💡 Check if KEP was cloned/downloaded completely")
    
    return all_good, kep_root

def check_dependencies(kep_root, verbose=False):
    """Check if all required packages are installed"""
    print_header("📦 Dependency Check")
    
    # Read requirements.txt
    requirements_file = kep_root / 'requirements.txt'
    if not requirements_file.exists():
        print_check(False, "requirements.txt not found")
        return False
    
    # Core packages that are critical for KEP
    critical_packages = {
        'yaml': 'PyYAML - Configuration file parsing',
        'docling': 'Docling - Advanced PDF processing',
        'nltk': 'NLTK - Natural language processing',
        'ibm_watsonx_ai': 'IBM WatsonX AI - LLM provider',
        'requests': 'HTTP requests library',
        'pathlib': 'Path handling (built-in)',
        'tqdm': 'Progress bars',
        'rich': 'Terminal formatting'
    }
    
    # Optional packages
    optional_packages = {
        'pandas': 'Data manipulation (nice to have)',
        'numpy': 'Numerical computing (nice to have)',
        'pytest': 'Testing framework (development)',
        'black': 'Code formatting (development)',
        'flake8': 'Code linting (development)'
    }
    
    print("🔍 Checking critical packages:")
    critical_missing = []
    
    for package, description in critical_packages.items():
        try:
            if package == 'pathlib':
                # pathlib is built-in since Python 3.4
                status = True
            else:
                __import__(package)
                status = True
        except ImportError:
            status = False
            critical_missing.append(package)
        
        print_check(status, f"{package}: {description}")
        
        if verbose and status:
            try:
                if package not in ['pathlib']:
                    module = __import__(package)
                    if hasattr(module, '__version__'):
                        print(f"   Version: {module.__version__}")
            except:
                pass
    
    if verbose:
        print("\n🔍 Checking optional packages:")
        for package, description in optional_packages.items():
            try:
                __import__(package)
                status = True
            except ImportError:
                status = False
            
            print_check(status, f"{package}: {description}")
    
    if critical_missing:
        print(f"\n❌ Missing critical packages: {', '.join(critical_missing)}")
        print(f"💡 Install with: pip install -r {requirements_file}")
        return False
    else:
        print(f"\n✅ All critical packages are installed!")
        return True

def check_kep_imports(kep_root):
    """Test importing KEP modules"""
    print_header("🔧 KEP Module Import Test")
    
    # Add KEP root to Python path temporarily
    original_path = sys.path.copy()
    if str(kep_root) not in sys.path:
        sys.path.insert(0, str(kep_root))
    
    # Modules to test
    test_modules = {
        'llm.factory': 'LLM Factory - Provider management',
        'extractor.pipeline': 'Pipeline - Core extraction logic',
        'ingest.pdf_converter': 'PDF Converter - Document processing',
        'extractor.classifier': 'Classifier - Relevance classification',
        'extractor.structurer': 'Structurer - JSON extraction',
        'common.file_logger': 'File Logger - Logging system',
        'common.metadata': 'Metadata - Processing metadata'
    }
    
    import_success = True
    
    for module_name, description in test_modules.items():
        try:
            importlib.import_module(module_name)
            print_check(True, f"{module_name}: {description}")
        except ImportError as e:
            print_check(False, f"{module_name}: {description}")
            print(f"   Error: {e}")
            import_success = False
        except Exception as e:
            print_check(False, f"{module_name}: {description}")
            print(f"   Unexpected error: {e}")
            import_success = False
    
    # Restore original path
    sys.path = original_path
    
    if import_success:
        print(f"\n✅ All KEP modules import successfully!")
    else:
        print(f"\n❌ Some KEP modules failed to import")
        print(f"   💡 Check for missing dependencies")
        print(f"   💡 Verify KEP installation is complete")
    
    return import_success

def check_environment_variables():
    """Check for configured environment variables"""
    print_header("🔑 Environment Variables")
    
    env_vars = {
        'WATSONX_APIKEY': 'WatsonX API Key',
        'WATSONX_PROJECT_ID': 'WatsonX Project ID',
        'WATSONX_URL': 'WatsonX Service URL',
        'RITS_API_KEY': 'RITS API Key',
        'RITS_API_URL': 'RITS API URL',
        'PIPELINE_SEED': 'Pipeline Random Seed'
    }
    
    configured_vars = 0
    
    for var, description in env_vars.items():
        value = os.getenv(var)
        is_set = bool(value)
        
        if is_set:
            if 'key' in var.lower():
                masked_value = f"{value[:8]}***"
            else:
                masked_value = value
            print_check(True, f"{var}: {masked_value}")
            configured_vars += 1
        else:
            print_check(False, f"{var}: Not set")
    
    print(f"\n📊 Summary: {configured_vars}/{len(env_vars)} environment variables configured")
    
    if configured_vars == 0:
        print("💡 Environment variables are optional if config files are properly set")
        print("💡 You can configure credentials via llm/<provider>/config.yaml files")
    
    return configured_vars > 0

def auto_fix_issues(kep_root):
    """Attempt to automatically fix common issues"""
    print_header("🔧 Auto-Fix Attempt")
    
    print("Attempting to fix common issues...")
    
    # Try to install missing dependencies
    requirements_file = kep_root / 'requirements.txt'
    if requirements_file.exists():
        print("\n📦 Installing/updating dependencies...")
        try:
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print("✅ Dependencies installation completed")
            else:
                print("❌ Dependencies installation failed")
                print(f"Error: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("⏱️ Installation timed out")
        except Exception as e:
            print(f"❌ Installation error: {e}")
    
    # Download NLTK data if NLTK is available
    try:
        import nltk
        print("\n📚 Downloading NLTK data...")
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        print("✅ NLTK data downloaded")
    except ImportError:
        print("⚠️ NLTK not available for data download")
    except Exception as e:
        print(f"⚠️ NLTK data download failed: {e}")

def generate_summary(checks):
    """Generate overall assessment summary"""
    print_header("📊 Environment Assessment Summary")
    
    total_checks = len(checks)
    passed_checks = sum(checks.values())
    
    print(f"Overall Score: {passed_checks}/{total_checks} ({passed_checks/total_checks*100:.0f}%)")
    print()
    
    for check_name, passed in checks.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {check_name}")
    
    print()
    
    if passed_checks == total_checks:
        print("🎉 Excellent! Your environment is fully ready for KEP!")
        print("Next step: python \"03_test_connections.py\"")
    elif passed_checks >= total_checks * 0.8:
        print("✅ Good! Minor issues detected, but KEP should work.")
        print("Consider addressing the failed checks for optimal performance.")
        print("Next step: python \"03_test_connections.py\"")
    elif passed_checks >= total_checks * 0.6:
        print("⚠️ Functional but needs attention.")
        print("Address failed checks before proceeding.")
    else:
        print("❌ Significant issues detected.")
        print("KEP may not work properly. Address failed checks first.")
        print("Consider using --fix option or manual installation.")

def main():
    """Main environment check function"""
    parser = argparse.ArgumentParser(description='KEP Environment Validation')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Show detailed information')
    parser.add_argument('--fix', action='store_true',
                       help='Attempt to auto-fix issues')
    
    args = parser.parse_args()
    
    print("🔍 KEP Environment Check")
    print("Validating your system for Knowledge Extraction Pipeline usage...")
    
    # Run all checks
    checks = {}
    
    # 1. Python version
    checks['Python Version'] = check_python_version()
    
    # 2. KEP installation
    kep_good, kep_root = check_kep_installation()
    checks['KEP Installation'] = kep_good
    
    # 3. Dependencies
    if kep_good:
        checks['Dependencies'] = check_dependencies(kep_root, args.verbose)
        
        # 4. KEP imports
        checks['KEP Modules'] = check_kep_imports(kep_root)
        
        # 5. Environment variables
        checks['Environment Variables'] = check_environment_variables()
    else:
        print("⚠️ Skipping dependency and import checks due to installation issues")
        checks['Dependencies'] = False
        checks['KEP Modules'] = False
        checks['Environment Variables'] = False
    
    # Auto-fix if requested
    if args.fix and kep_good:
        auto_fix_issues(kep_root)
        print("\n🔄 Re-running checks after auto-fix...")
        # Re-run dependency check
        checks['Dependencies'] = check_dependencies(kep_root, args.verbose)
        checks['KEP Modules'] = check_kep_imports(kep_root)
    
    # Generate summary
    generate_summary(checks)
    
    return all(checks.values())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)