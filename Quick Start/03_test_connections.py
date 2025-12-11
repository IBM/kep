#!/usr/bin/env python3
"""
03_test_connections.py - LLM Provider Connection Testing

This script tests connections to LLM providers (WatsonX, RITS) with
comprehensive error diagnosis and retry logic.

Run this script to:
- Test IBM Cloud authentication
- Validate WatsonX connection and model access
- Test RITS connection (if available)
- Discover available models
- Diagnose connection issues with specific solutions

Usage:
    python "03_test_connections.py"
    python "03_test_connections.py" --provider watsonx    # Test specific provider
    python "03_test_connections.py" --verbose            # Detailed output
    python "03_test_connections.py" --retry 5            # Custom retry count
"""

import sys
import os
import time
import requests
import yaml
import traceback
import argparse
from pathlib import Path

def print_header(title):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print('='*60)

def print_step(step_num, title):
    """Print step header"""
    print(f"\n{step_num}️⃣ {title}")
    print("-" * (len(title) + 4))

def print_check(status, message, details=""):
    """Print check result"""
    status_char = "✅" if status else "❌"
    print(f"{status_char} {message}")
    if details:
        print(f"   {details}")

def find_kep_root():
    """Find KEP root directory"""
    current_dir = Path.cwd()
    if current_dir.name == "Quick Start":
        return current_dir.parent
    return current_dir

def load_config(kep_root, provider):
    """Load configuration for specified provider"""
    config_path = kep_root / "llm" / provider / "config.yaml"
    
    if not config_path.exists():
        return None, f"Config file not found: {config_path}"
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config, None
    except Exception as e:
        return None, f"Failed to parse config: {e}"

def test_iam_authentication(api_key, verbose=False):
    """Test IBM Cloud IAM token generation"""
    print_step("1", "IBM Cloud IAM Authentication Test")
    
    if not api_key or api_key.startswith('YOUR_'):
        print_check(False, "Invalid API key")
        print("   💡 Set valid API key in config.yaml or environment variable")
        return False, None
    
    print(f"🔑 Testing API key: {api_key[:8]}*** (length: {len(api_key)})")
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }
    
    data = {
        'grant_type': 'urn:ibm:params:oauth:grant-type:apikey',
        'apikey': api_key
    }
    
    try:
        print("🌐 Requesting IAM token...")
        response = requests.post(
            'https://iam.cloud.ibm.com/identity/token',
            headers=headers,
            data=data,
            timeout=30
        )
        
        if verbose:
            print(f"   Response status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            print_check(True, "IAM token generated successfully")
            if verbose:
                print(f"   Token type: {token_data.get('token_type')}")
                print(f"   Expires in: {token_data.get('expires_in')} seconds")
            return True, token_data.get('access_token')
        else:
            print_check(False, f"IAM authentication failed (HTTP {response.status_code})")
            
            if response.status_code == 400:
                print("   🔧 Troubleshooting HTTP 400:")
                print("     • API key is invalid or expired")
                print("     • Generate new key: https://cloud.ibm.com/iam/apikeys")
            elif response.status_code == 401:
                print("   🔧 Troubleshooting HTTP 401:")
                print("     • API key format is incorrect")
                print("     • Check for extra spaces or characters")
            elif response.status_code == 429:
                print("   🔧 Troubleshooting HTTP 429:")
                print("     • Rate limit exceeded - wait and retry")
            
            if verbose:
                print(f"   Response: {response.text}")
            
            return False, None
            
    except requests.exceptions.Timeout:
        print_check(False, "Request timed out")
        print("   🔧 Check your internet connection")
        return False, None
    except requests.exceptions.ConnectionError:
        print_check(False, "Connection error")
        print("   🔧 Check internet connection and firewall settings")
        return False, None
    except Exception as e:
        print_check(False, f"Unexpected error: {e}")
        return False, None

def discover_watsonx_models(config, verbose=False):
    """Discover available WatsonX models by attempting invalid model"""
    print_step("2", "WatsonX Model Discovery")
    
    try:
        # Add KEP to path for imports
        kep_root = find_kep_root()
        if str(kep_root) not in sys.path:
            sys.path.insert(0, str(kep_root))
        
        from ibm_watsonx_ai.foundation_models import ModelInference
        
        api_key = os.getenv('WATSONX_APIKEY') or config.get('apikey')
        project_id = os.getenv('WATSONX_PROJECT_ID') or config.get('project_id')
        url = os.getenv('WATSONX_URL') or config.get('url')
        
        print("🔍 Discovering available models...")
        
        try:
            # Use invalid model to trigger error with model list
            model = ModelInference(
                model_id="invalid-model-for-discovery",
                params={'max_new_tokens': 50},
                credentials={"url": url, "apikey": api_key},
                project_id=project_id,
            )
        except Exception as e:
            error_msg = str(e)
            if "Supported models:" in error_msg:
                # Extract models from error message
                start = error_msg.find("Supported models: [") + len("Supported models: [")
                end = error_msg.find("]", start)
                models_str = error_msg[start:end]
                
                # Parse models list
                models = [m.strip().strip("'\"") for m in models_str.split(',')]
                models = [m for m in models if m]  # Remove empty strings
                
                print_check(True, f"Found {len(models)} available models")
                
                if verbose:
                    # Group by provider
                    model_groups = {}
                    for model in models:
                        provider = model.split('/')[0] if '/' in model else 'other'
                        if provider not in model_groups:
                            model_groups[provider] = []
                        model_groups[provider].append(model)
                    
                    print("\n📋 Available models by provider:")
                    for provider, provider_models in sorted(model_groups.items()):
                        print(f"   {provider.upper()}:")
                        for model in sorted(provider_models)[:5]:  # Show max 5 per provider
                            print(f"     • {model}")
                        if len(provider_models) > 5:
                            print(f"     ... and {len(provider_models)-5} more")
                
                # Recommend good models
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
                    print(f"\n⭐ Recommended models for KEP:")
                    for model in recommended[:3]:
                        print(f"   • {model}")
                
                return models, recommended[0] if recommended else models[0]
            else:
                print_check(False, f"Model discovery failed: {e}")
                return [], None
                
    except ImportError:
        print_check(False, "ibm_watsonx_ai not installed")
        print("   💡 Install with: pip install ibm-watsonx-ai")
        return [], None
    except Exception as e:
        print_check(False, f"Discovery error: {e}")
        if verbose:
            traceback.print_exc()
        return [], None

def test_watsonx_connection(config, model_name=None, max_retries=3, verbose=False):
    """Test WatsonX connection with retry logic"""
    print_step("3", f"WatsonX Connection Test")
    
    # Get credentials
    api_key = os.getenv('WATSONX_APIKEY') or config.get('apikey')
    project_id = os.getenv('WATSONX_PROJECT_ID') or config.get('project_id')
    url = os.getenv('WATSONX_URL') or config.get('url')
    
    print(f"🔧 Configuration:")
    print(f"   URL: {url}")
    print(f"   Project ID: {project_id}")
    print(f"   Model: {model_name}")
    
    if not model_name:
        print_check(False, "No model specified for testing")
        return False
    
    for attempt in range(max_retries):
        print(f"\n🔄 Attempt {attempt + 1}/{max_retries}:")
        
        try:
            # Add KEP to path for imports
            kep_root = find_kep_root()
            if str(kep_root) not in sys.path:
                sys.path.insert(0, str(kep_root))
            
            from llm.factory import LLMFactory
            
            print("   Creating WatsonX client...")
            client = LLMFactory.create(
                provider="watsonx",
                model_name=model_name,
                config_dir=str(kep_root / "llm")
            )
            print_check(True, "Client created successfully")
            
            # Test inference
            print("   Testing inference...")
            test_prompt = "Say 'Hello KEP!' and nothing else."
            result = client.inference(test_prompt)
            response = result.get('generated_text', 'No response').strip()
            
            print_check(True, "Inference successful")
            print(f"   📤 Prompt: '{test_prompt}'")
            print(f"   📥 Response: '{response[:100]}{'...' if len(response) > 100 else ''}'")
            
            return True
            
        except Exception as e:
            error_msg = str(e)
            print_check(False, f"Attempt {attempt + 1} failed: {e}")
            
            # Analyze error type
            if "IAM Token" in error_msg:
                print("   💡 Authentication issue - check API key")
                break  # Don't retry auth issues
            elif "not supported" in error_msg.lower():
                print("   💡 Model not available - try different model")
                break  # Don't retry model issues
            elif "timeout" in error_msg.lower() or "connection" in error_msg.lower():
                print("   💡 Network issue - retrying...")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"   ⏱️ Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
            else:
                print("   💡 Unexpected error")
                if verbose:
                    print(f"   📋 Details: {traceback.format_exc()}")
                if attempt < max_retries - 1:
                    time.sleep(1)
    
    print_check(False, f"All {max_retries} attempts failed")
    return False

def test_rits_connection(config, verbose=False):
    """Test RITS connection"""
    print_step("4", "RITS Connection Test")
    
    try:
        # Add KEP to path for imports
        kep_root = find_kep_root()
        if str(kep_root) not in sys.path:
            sys.path.insert(0, str(kep_root))
        
        from llm.factory import LLMFactory
        
        print("🔧 Testing RITS connection...")
        client = LLMFactory.create(
            provider="rits",
            model_name="mistralai/mistral-large",  # Default model
            config_dir=str(kep_root / "llm")
        )
        print_check(True, "RITS client created")
        
        # Test inference
        result = client.inference("Say 'Hello from RITS!' and nothing else.")
        response = result.get('generated_text', 'No response').strip()
        
        print_check(True, "RITS inference successful")
        print(f"   📥 Response: '{response[:100]}{'...' if len(response) > 100 else ''}'")
        return True
        
    except Exception as e:
        print_check(False, f"RITS connection failed: {e}")
        if "config" in str(e).lower():
            print("   💡 Check RITS configuration in llm/rits/config.yaml")
        elif "credentials" in str(e).lower():
            print("   💡 Check RITS API credentials")
        else:
            print("   💡 RITS may not be available in your environment")
        
        if verbose:
            traceback.print_exc()
        return False

def generate_connection_report(results):
    """Generate comprehensive connection report"""
    print_header("📊 Connection Test Summary")
    
    iam_success = results.get('iam', False)
    watsonx_success = results.get('watsonx', False)
    rits_success = results.get('rits', False)
    available_models = results.get('models', [])
    recommended_model = results.get('recommended_model')
    
    # Overall status
    if watsonx_success:
        print("🎉 Excellent! WatsonX is fully operational")
        if rits_success:
            print("🎉 Bonus: RITS is also available")
    elif rits_success:
        print("✅ Good! RITS is operational (WatsonX has issues)")
    elif iam_success:
        print("⚠️ Authentication works but model access failed")
    else:
        print("❌ Connection issues detected - needs attention")
    
    print()
    
    # Detailed results
    print("📋 Detailed Results:")
    test_results = [
        ("IBM Cloud Authentication", iam_success),
        ("WatsonX Connection", watsonx_success),
        ("RITS Connection", rits_success if 'rits' in results else None)
    ]
    
    for test_name, result in test_results:
        if result is True:
            print(f"   ✅ {test_name}: PASS")
        elif result is False:
            print(f"   ❌ {test_name}: FAIL")
        else:
            print(f"   ⚪ {test_name}: NOT TESTED")
    
    # Model information
    if available_models:
        print(f"\n🤖 Available Models: {len(available_models)} total")
        if recommended_model:
            print(f"   ⭐ Recommended: {recommended_model}")
    
    # Next steps
    print(f"\n🎯 Next Steps:")
    if watsonx_success or rits_success:
        print("   ✅ Connections working - ready for pipeline testing")
        print("   📋 Next: python \"04_understanding_schemas.py\"")
    else:
        print("   🔧 Fix connection issues before proceeding")
        print("   💡 Check API keys and network connectivity")
        print("   🆘 Run python \"08_troubleshooting.py\" for detailed help")

def main():
    """Main connection testing function"""
    parser = argparse.ArgumentParser(description='KEP Provider Connection Testing')
    parser.add_argument('--provider', choices=['watsonx', 'rits', 'all'], 
                       default='all', help='Provider to test')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Detailed output')
    parser.add_argument('--retry', type=int, default=3,
                       help='Number of retry attempts')
    
    args = parser.parse_args()
    
    print("🔍 KEP Provider Connection Test")
    print("Testing LLM provider connections and authentication...")
    
    kep_root = find_kep_root()
    results = {}
    
    # Test WatsonX if requested
    if args.provider in ['watsonx', 'all']:
        print_header("🤖 WatsonX Testing")
        
        # Load config
        config, error = load_config(kep_root, 'watsonx')
        if not config:
            print_check(False, f"WatsonX config error: {error}")
            results['watsonx'] = False
        else:
            # Test IAM authentication
            api_key = os.getenv('WATSONX_APIKEY') or config.get('apikey')
            iam_success, token = test_iam_authentication(api_key, args.verbose)
            results['iam'] = iam_success
            
            if iam_success:
                # Discover models
                models, recommended = discover_watsonx_models(config, args.verbose)
                results['models'] = models
                results['recommended_model'] = recommended
                
                # Test connection
                if recommended:
                    watsonx_success = test_watsonx_connection(
                        config, recommended, args.retry, args.verbose
                    )
                    results['watsonx'] = watsonx_success
                else:
                    print_check(False, "No recommended model found")
                    results['watsonx'] = False
            else:
                results['watsonx'] = False
    
    # Test RITS if requested
    if args.provider in ['rits', 'all']:
        print_header("🔬 RITS Testing")
        
        config, error = load_config(kep_root, 'rits')
        if not config:
            print_check(False, f"RITS config error: {error}")
            results['rits'] = False
        else:
            rits_success = test_rits_connection(config, args.verbose)
            results['rits'] = rits_success
    
    # Generate report
    generate_connection_report(results)
    
    # Return success if any provider works
    success = results.get('watsonx', False) or results.get('rits', False)
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)