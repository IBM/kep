#!/usr/bin/env python3
"""
08_troubleshooting.py - KEP Advanced Diagnostics & Support

This script provides comprehensive diagnostics, troubleshooting guidance,
and automated fixes for common KEP issues.

Features:
- Complete system health assessment
- Network and authentication diagnostics
- Performance analysis and optimization tips
- Automated issue resolution
- Support information and contacts

Usage:
    python "08_troubleshooting.py"                    # Full diagnostic
    python "08_troubleshooting.py" --quick            # Quick health check
    python "08_troubleshooting.py" --fix              # Auto-fix issues
    python "08_troubleshooting.py" --network          # Network diagnostics
    python "08_troubleshooting.py" --performance      # Performance analysis
"""

import sys
import os
import subprocess
import json
import time
import requests
from pathlib import Path
import argparse
import platform
import socket
from datetime import datetime

def print_header(title):
    """Print formatted header"""
    print(f"\n{'='*70}")
    print(f" {title}")
    print('='*70)

def print_section(title):
    """Print section header"""
    print(f"\n{title}")
    print("-" * len(title))

def print_check(status, message, details=""):
    """Print check result"""
    if status == "pass":
        icon = "✅"
    elif status == "warn":
        icon = "⚠️"
    elif status == "fail":
        icon = "❌"
    else:
        icon = "ℹ️"
    
    print(f"{icon} {message}")
    if details:
        print(f"   {details}")

def find_kep_root():
    """Find KEP root directory"""
    current_dir = Path.cwd()
    if current_dir.name == "Quick Start":
        return current_dir.parent
    return current_dir

def system_information():
    """Collect system information"""
    print_header("💻 System Information")
    
    info = {
        "platform": platform.platform(),
        "python_version": sys.version,
        "python_executable": sys.executable,
        "working_directory": os.getcwd(),
        "user": os.getenv("USER", os.getenv("USERNAME", "unknown")),
        "timestamp": datetime.now().isoformat()
    }
    
    print(f"🖥️ Platform: {info['platform']}")
    print(f"🐍 Python: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    print(f"📁 Working Directory: {info['working_directory']}")
    print(f"👤 User: {info['user']}")
    print(f"⏰ Timestamp: {info['timestamp']}")
    
    return info

def comprehensive_health_check():
    """Perform comprehensive system health check"""
    print_header("🏥 Comprehensive Health Assessment")
    
    checks = []
    
    # 1. Python environment
    print_section("🐍 Python Environment")
    python_version = sys.version_info
    if python_version >= (3, 8):
        checks.append(("pass", "Python Version", f"{python_version.major}.{python_version.minor}.{python_version.micro}"))
    else:
        checks.append(("fail", "Python Version", f"{python_version.major}.{python_version.minor} - Requires 3.8+"))
    
    # 2. KEP installation
    print_section("📦 KEP Installation")
    kep_root = find_kep_root()
    
    essential_files = [
        "run_pipeline.py",
        "requirements.txt",
        "llm/factory.py",
        "extractor/pipeline.py"
    ]
    
    missing_files = []
    for file_path in essential_files:
        if not (kep_root / file_path).exists():
            missing_files.append(file_path)
    
    if not missing_files:
        checks.append(("pass", "Core Files", "All essential files present"))
    else:
        checks.append(("fail", "Core Files", f"Missing: {', '.join(missing_files)}"))
    
    # 3. Dependencies
    print_section("📚 Dependencies")
    critical_deps = [
        "yaml", "requests", "pathlib",
        "ibm_watsonx_ai", "docling", "nltk"
    ]
    
    missing_deps = []
    for dep in critical_deps:
        try:
            if dep == "pathlib":
                import pathlib
            else:
                __import__(dep)
        except ImportError:
            missing_deps.append(dep)
    
    if not missing_deps:
        checks.append(("pass", "Dependencies", "All critical packages available"))
    else:
        checks.append(("fail", "Dependencies", f"Missing: {', '.join(missing_deps)}"))
    
    # 4. Configuration
    print_section("⚙️ Configuration")
    config_issues = check_configuration(kep_root)
    if not config_issues:
        checks.append(("pass", "Configuration", "All configs properly set"))
    else:
        checks.append(("warn", "Configuration", f"{len(config_issues)} issues found"))
    
    # 5. Network connectivity
    print_section("🌐 Network Connectivity")
    network_status = check_network_connectivity()
    if network_status:
        checks.append(("pass", "Network", "Internet connectivity confirmed"))
    else:
        checks.append(("fail", "Network", "Internet connectivity issues"))
    
    # 6. LLM Provider access
    print_section("🤖 LLM Provider Access")
    provider_status = check_provider_access(kep_root)
    if provider_status["success"]:
        checks.append(("pass", "LLM Access", f"Working with {provider_status['provider']}"))
    else:
        checks.append(("fail", "LLM Access", provider_status["error"]))
    
    # 7. Data availability
    print_section("📄 Data Availability")
    data_status = check_data_availability(kep_root)
    if data_status["pdfs"] > 0:
        checks.append(("pass", "PDF Data", f"{data_status['pdfs']} PDF files available"))
    else:
        checks.append(("warn", "PDF Data", "No PDF files found for testing"))
    
    if data_status["schemas"] > 0:
        checks.append(("pass", "Schemas", f"{data_status['schemas']} schema files available"))
    else:
        checks.append(("warn", "Schemas", "No schema files found"))
    
    # Display results
    print_header("📊 Health Check Summary")
    
    passed = sum(1 for status, _, _ in checks if status == "pass")
    warnings = sum(1 for status, _, _ in checks if status == "warn")
    failed = sum(1 for status, _, _ in checks if status == "fail")
    total = len(checks)
    
    for status, component, details in checks:
        print_check(status, component, details)
    
    print(f"\n📈 Overall Score: {passed}/{total} passed, {warnings} warnings, {failed} failed")
    
    # Health assessment
    health_score = (passed * 100 + warnings * 50) / (total * 100)
    
    if health_score >= 0.9:
        print("🎉 Excellent health! KEP is fully operational.")
        return "excellent"
    elif health_score >= 0.7:
        print("✅ Good health with minor issues.")
        return "good"
    elif health_score >= 0.5:
        print("⚠️ Moderate issues detected - needs attention.")
        return "moderate"
    else:
        print("❌ Significant problems detected - requires intervention.")
        return "poor"

def check_configuration(kep_root):
    """Check configuration files for issues"""
    issues = []
    
    # Check WatsonX config
    watsonx_config = kep_root / "llm" / "watsonx" / "config.yaml"
    if watsonx_config.exists():
        try:
            import yaml
            with open(watsonx_config, 'r') as f:
                config = yaml.safe_load(f)
            
            # Check for placeholders
            for key, value in config.items():
                if isinstance(value, str) and value.startswith("YOUR_"):
                    issues.append(f"WatsonX config has placeholder: {key}")
            
            # Check required fields
            required_fields = ["url", "apikey", "project_id"]
            for field in required_fields:
                if field not in config or not config[field]:
                    issues.append(f"WatsonX config missing: {field}")
                    
        except Exception as e:
            issues.append(f"WatsonX config error: {e}")
    else:
        issues.append("WatsonX config file not found")
    
    # Check RITS config
    rits_config = kep_root / "llm" / "rits" / "config.yaml"
    if not rits_config.exists():
        issues.append("RITS config file not found (optional)")
    
    return issues

def check_network_connectivity():
    """Test network connectivity"""
    test_urls = [
        "https://www.google.com",
        "https://iam.cloud.ibm.com",
        "https://us-south.ml.cloud.ibm.com"
    ]
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return True
        except:
            continue
    
    return False

def check_provider_access(kep_root):
    """Test LLM provider access"""
    try:
        # Add KEP to path
        if str(kep_root) not in sys.path:
            sys.path.insert(0, str(kep_root))
        
        from llm.factory import LLMFactory
        
        # Try WatsonX
        try:
            client = LLMFactory.create(
                provider="watsonx",
                model_name="mistralai/mistral-large",
                config_dir=str(kep_root / "llm")
            )
            
            # Quick test
            result = client.inference("Test")
            return {"success": True, "provider": "WatsonX", "error": None}
            
        except Exception as e:
            # Try RITS
            try:
                client = LLMFactory.create(
                    provider="rits",
                    model_name="mistralai/mistral-large",
                    config_dir=str(kep_root / "llm")
                )
                
                result = client.inference("Test")
                return {"success": True, "provider": "RITS", "error": None}
                
            except Exception as e2:
                return {"success": False, "provider": None, "error": f"Both providers failed: {e}, {e2}"}
                
    except ImportError as e:
        return {"success": False, "provider": None, "error": f"Import error: {e}"}

def check_data_availability(kep_root):
    """Check for available data files"""
    status = {"pdfs": 0, "schemas": 0}
    
    # Count PDFs
    pdfs_dir = kep_root / "pdfs"
    if pdfs_dir.exists():
        status["pdfs"] = len(list(pdfs_dir.glob("*.pdf")))
    
    # Count schemas
    schemas_dir = kep_root / "schemas"
    if schemas_dir.exists():
        status["schemas"] = len(list(schemas_dir.glob("*.json")))
    
    return status

def network_diagnostics():
    """Detailed network diagnostics"""
    print_header("🌐 Network Diagnostics")
    
    # Basic connectivity
    print_section("🔌 Basic Connectivity")
    
    # DNS resolution
    try:
        socket.gethostbyname("google.com")
        print_check("pass", "DNS Resolution", "Can resolve domain names")
    except:
        print_check("fail", "DNS Resolution", "Cannot resolve domain names")
    
    # Test specific endpoints
    endpoints = {
        "IBM Cloud IAM": "https://iam.cloud.ibm.com",
        "WatsonX US-South": "https://us-south.ml.cloud.ibm.com",
        "RITS": "https://rits.fmaas.res.ibm.com"
    }
    
    print_section("🎯 Endpoint Testing")
    
    for name, url in endpoints.items():
        try:
            start_time = time.time()
            response = requests.get(url, timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                print_check("pass", name, f"Accessible ({response_time:.0f}ms)")
            else:
                print_check("warn", name, f"HTTP {response.status_code} ({response_time:.0f}ms)")
                
        except requests.exceptions.Timeout:
            print_check("fail", name, "Timeout (>10s)")
        except requests.exceptions.ConnectionError:
            print_check("fail", name, "Connection error")
        except Exception as e:
            print_check("fail", name, f"Error: {e}")
    
    # Firewall/proxy detection
    print_section("🛡️ Firewall/Proxy Detection")
    
    # Check for common proxy environment variables
    proxy_vars = ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"]
    proxy_detected = False
    
    for var in proxy_vars:
        if os.getenv(var):
            print_check("info", f"Proxy Variable", f"{var}={os.getenv(var)}")
            proxy_detected = True
    
    if not proxy_detected:
        print_check("pass", "Proxy Detection", "No proxy environment variables found")

def performance_analysis():
    """Analyze system performance for KEP"""
    print_header("⚡ Performance Analysis")
    
    # System resources
    print_section("💾 System Resources")
    
    try:
        import psutil
        
        # Memory
        memory = psutil.virtual_memory()
        print_check("info", "Total RAM", f"{memory.total / (1024**3):.1f} GB")
        print_check("info", "Available RAM", f"{memory.available / (1024**3):.1f} GB")
        
        if memory.available < 2 * (1024**3):  # Less than 2GB
            print_check("warn", "Memory Warning", "Low available memory may affect performance")
        
        # CPU
        cpu_count = psutil.cpu_count()
        cpu_usage = psutil.cpu_percent(interval=1)
        print_check("info", "CPU Cores", str(cpu_count))
        print_check("info", "CPU Usage", f"{cpu_usage}%")
        
        # Disk space
        disk = psutil.disk_usage('/')
        free_gb = disk.free / (1024**3)
        print_check("info", "Free Disk Space", f"{free_gb:.1f} GB")
        
        if free_gb < 5:
            print_check("warn", "Disk Warning", "Low disk space may affect processing")
            
    except ImportError:
        print_check("info", "Performance Monitoring", "Install psutil for detailed metrics")
    
    # Python performance
    print_section("🐍 Python Performance")
    
    # Test JSON processing speed
    start_time = time.time()
    test_data = {"test": "data"} * 1000
    json.dumps(test_data)
    json_time = (time.time() - start_time) * 1000
    
    print_check("info", "JSON Processing", f"{json_time:.1f}ms for 1000 objects")
    
    # Test import speed
    start_time = time.time()
    import json as json_test
    import_time = (time.time() - start_time) * 1000
    
    print_check("info", "Module Import Speed", f"{import_time:.1f}ms")
    
    # Performance recommendations
    print_section("💡 Performance Recommendations")
    
    recommendations = [
        "Use SSD storage for better I/O performance",
        "Ensure at least 8GB RAM for processing large documents",
        "Close unnecessary applications during pipeline runs",
        "Use --debug-io sparingly (increases processing time)",
        "Process documents in batches rather than all at once",
        "Monitor CPU and memory usage during long runs"
    ]
    
    for rec in recommendations:
        print(f"   💡 {rec}")

def automated_fixes():
    """Attempt automated fixes for common issues"""
    print_header("🔧 Automated Issue Resolution")
    
    kep_root = find_kep_root()
    fixes_applied = []
    
    # 1. Install missing dependencies
    print_section("📦 Dependency Installation")
    
    requirements_file = kep_root / "requirements.txt"
    if requirements_file.exists():
        try:
            print("Installing/updating dependencies...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print_check("pass", "Dependencies", "Successfully installed/updated")
                fixes_applied.append("Updated dependencies")
            else:
                print_check("fail", "Dependencies", f"Installation failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            print_check("warn", "Dependencies", "Installation timed out")
        except Exception as e:
            print_check("fail", "Dependencies", f"Error: {e}")
    
    # 2. Download NLTK data
    print_section("📚 NLTK Data")
    
    try:
        import nltk
        print("Downloading NLTK data...")
        
        # Download required datasets
        datasets = ['punkt', 'stopwords', 'wordnet']
        for dataset in datasets:
            try:
                nltk.download(dataset, quiet=True)
                print_check("pass", f"NLTK {dataset}", "Downloaded successfully")
            except Exception as e:
                print_check("warn", f"NLTK {dataset}", f"Download failed: {e}")
        
        fixes_applied.append("Downloaded NLTK data")
        
    except ImportError:
        print_check("warn", "NLTK", "Not available - install with: pip install nltk")
    
    # 3. Create missing directories
    print_section("📁 Directory Structure")
    
    required_dirs = [
        "pdfs", "runs", "schemas/custom"
    ]
    
    for dir_path in required_dirs:
        full_path = kep_root / dir_path
        if not full_path.exists():
            try:
                full_path.mkdir(parents=True, exist_ok=True)
                print_check("pass", f"Created {dir_path}", "Directory created")
                fixes_applied.append(f"Created {dir_path} directory")
            except Exception as e:
                print_check("fail", f"Create {dir_path}", f"Failed: {e}")
        else:
            print_check("pass", f"Directory {dir_path}", "Already exists")
    
    # 4. Fix file permissions (Unix-like systems)
    if platform.system() != "Windows":
        print_section("🔐 File Permissions")
        
        script_files = [
            "run_pipeline.py"
        ]
        
        for script in script_files:
            script_path = kep_root / script
            if script_path.exists():
                try:
                    # Make executable
                    os.chmod(script_path, 0o755)
                    print_check("pass", f"Permissions {script}", "Made executable")
                except Exception as e:
                    print_check("warn", f"Permissions {script}", f"Could not modify: {e}")
    
    # Summary
    print_section("📊 Fix Summary")
    
    if fixes_applied:
        print("✅ Applied fixes:")
        for fix in fixes_applied:
            print(f"   • {fix}")
        print("\n💡 Re-run diagnostics to verify fixes")
    else:
        print("ℹ️ No automated fixes were needed or applicable")

def common_issues_guide():
    """Provide guidance for common issues"""
    print_header("🆘 Common Issues & Solutions")
    
    issues = {
        "Authentication Errors": {
            "symptoms": [
                "Error getting IAM Token",
                "HTTP 400/401 responses",
                "Credentials missing errors"
            ],
            "solutions": [
                "Check API key in llm/watsonx/config.yaml",
                "Generate new API key: https://cloud.ibm.com/iam/apikeys",
                "Verify project ID is correct",
                "Set environment variables: WATSONX_APIKEY, WATSONX_PROJECT_ID",
                "Test authentication: python \"03_test_connections.py\""
            ]
        },
        
        "Network/Connection Issues": {
            "symptoms": [
                "Connection timeout errors",
                "DNS resolution failures", 
                "Proxy/firewall blocking"
            ],
            "solutions": [
                "Check internet connectivity",
                "Test network: python \"08_troubleshooting.py\" --network",
                "Configure proxy settings if behind corporate firewall",
                "Try different network (mobile hotspot) to isolate issues",
                "Check firewall rules for outbound HTTPS"
            ]
        },
        
        "Import/Dependency Errors": {
            "symptoms": [
                "ModuleNotFoundError",
                "Import errors for KEP modules",
                "Missing package errors"
            ],
            "solutions": [
                "Install requirements: pip install -r requirements.txt",
                "Check Python environment: python \"02_environment_check.py\"",
                "Verify correct Python version (3.8+)",
                "Use virtual environment to isolate dependencies",
                "Auto-fix: python \"08_troubleshooting.py\" --fix"
            ]
        },
        
        "Pipeline Execution Errors": {
            "symptoms": [
                "Pipeline crashes during execution",
                "Incomplete outputs",
                "Schema validation errors"
            ],
            "solutions": [
                "Start with small test (1-2 PDFs)",
                "Validate schemas: python \"04_understanding_schemas.py\" --validate",
                "Use --debug-io to see detailed LLM interactions",
                "Check available disk space and memory",
                "Review run.log for specific error messages"
            ]
        },
        
        "Poor Extraction Quality": {
            "symptoms": [
                "Empty or meaningless extractions",
                "High irrelevant classification rate",
                "Inconsistent results"
            ],
            "solutions": [
                "Add more examples to schemas (few-shot learning)",
                "Refine classification criteria and instructions",
                "Review and improve schema field definitions",
                "Test with different models",
                "Analyze results: python \"06_results_explorer.py\""
            ]
        }
    }
    
    for issue_type, info in issues.items():
        print_section(f"❗ {issue_type}")
        
        print("🔍 Symptoms:")
        for symptom in info["symptoms"]:
            print(f"   • {symptom}")
        
        print("\n💡 Solutions:")
        for solution in info["solutions"]:
            print(f"   • {solution}")
        
        print()

def support_information():
    """Provide support contact information"""
    print_header("📞 Support & Resources")
    
    print_section("👥 KEP Development Team")
    
    contacts = [
        {
            "name": "Viviane Torres",
            "role": "Senior Research Scientist, Manager",
            "email": "vivianet@br.ibm.com",
            "specialty": "Project management, strategic direction"
        },
        {
            "name": "Marcelo Archanjo", 
            "role": "Senior Research Scientist",
            "email": "marcelo.archanjo@ibm.com",
            "specialty": "Technical architecture, LLM integration"
        },
        {
            "name": "Anaximandro Souza",
            "role": "PhD Researcher",
            "email": "anaximandrosouza@ibm.com", 
            "specialty": "Pipeline development, schema design"
        }
    ]
    
    for contact in contacts:
        print(f"👤 {contact['name']} ({contact['role']})")
        print(f"   📧 {contact['email']}")
        print(f"   🎯 {contact['specialty']}")
        print()
    
    print_section("📚 Documentation Resources")
    
    resources = [
        ("README.md", "Complete system documentation and quick start"),
        ("UNIFIED_SETUP.md", "Detailed setup for multi-repository environment"),
        ("CLAUDE.md", "Developer guidance and architecture notes"),
        ("Quick Start/", "Interactive learning scripts and tutorials"),
        ("schemas/", "Example schemas for different domains"),
        ("IBM Box", "https://ibm.box.com/s/1gltzx4paq75wqhp65tr2osjo7vf69ni")
    ]
    
    for resource, description in resources:
        print(f"📄 {resource}")
        print(f"   {description}")
        print()
    
    print_section("🔧 Self-Help Tools")
    
    tools = [
        ("Environment Check", "python \"02_environment_check.py\""),
        ("Connection Test", "python \"03_test_connections.py\""),
        ("Schema Validation", "python \"04_understanding_schemas.py\" --validate"),
        ("Results Analysis", "python \"06_results_explorer.py\""),
        ("Health Diagnostics", "python \"08_troubleshooting.py\"")
    ]
    
    for tool, command in tools:
        print(f"🛠️ {tool}")
        print(f"   {command}")
        print()
    
    print_section("🆘 When to Contact Support")
    
    scenarios = [
        "Persistent authentication failures after trying all solutions",
        "Unexpected crashes or errors not covered in documentation",
        "Performance issues with large document collections",
        "Custom schema design consultation",
        "Integration with new LLM providers",
        "Research collaboration opportunities"
    ]
    
    print("Contact the team when you encounter:")
    for scenario in scenarios:
        print(f"   • {scenario}")

def main():
    """Main troubleshooting function"""
    parser = argparse.ArgumentParser(description='KEP Advanced Diagnostics & Troubleshooting')
    parser.add_argument('--quick', action='store_true',
                       help='Quick health check only')
    parser.add_argument('--fix', action='store_true',
                       help='Attempt automated fixes')
    parser.add_argument('--network', action='store_true',
                       help='Network diagnostics only')
    parser.add_argument('--performance', action='store_true',
                       help='Performance analysis only')
    
    args = parser.parse_args()
    
    print("🔧 KEP Advanced Diagnostics & Troubleshooting")
    print("Comprehensive system analysis and issue resolution...")
    
    # Collect system info
    sys_info = system_information()
    
    if args.quick:
        # Quick health check only
        health_status = comprehensive_health_check()
        return health_status in ["excellent", "good"]
    
    if args.network:
        # Network diagnostics only
        network_diagnostics()
        return True
    
    if args.performance:
        # Performance analysis only
        performance_analysis()
        return True
    
    if args.fix:
        # Automated fixes only
        automated_fixes()
        return True
    
    # Full diagnostic suite
    health_status = comprehensive_health_check()
    
    if health_status in ["moderate", "poor"]:
        print("\n🔧 Running automated fixes...")
        automated_fixes()
        
        print("\n🔄 Re-checking health after fixes...")
        health_status = comprehensive_health_check()
    
    # Additional diagnostics for problematic systems
    if health_status in ["moderate", "poor"]:
        network_diagnostics()
        performance_analysis()
    
    # Always show common issues guide and support info
    common_issues_guide()
    support_information()
    
    # Final assessment
    print_header("🎯 Final Assessment & Next Steps")
    
    if health_status == "excellent":
        print("🎉 Your KEP installation is in excellent condition!")
        print("   Ready for production use with large document collections.")
        
    elif health_status == "good":
        print("✅ Your KEP installation is working well!")
        print("   Minor tweaks may improve performance, but system is functional.")
        
    elif health_status == "moderate":
        print("⚠️ Your KEP installation has some issues that need attention.")
        print("   Address the failed checks above before processing important documents.")
        
    else:  # poor
        print("❌ Your KEP installation has significant problems.")
        print("   Please address critical issues or contact support for assistance.")
    
    print(f"\n📋 Recommended next steps:")
    if health_status in ["excellent", "good"]:
        print("   1. Test with sample documents: python \"05_pipeline_demo.py\"")
        print("   2. Create custom schemas: python \"07_custom_schemas.py\"")
        print("   3. Process your research documents")
    else:
        print("   1. Fix critical issues identified above")
        print("   2. Re-run diagnostics: python \"08_troubleshooting.py\"")
        print("   3. Contact support if problems persist")
    
    return health_status in ["excellent", "good"]

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)