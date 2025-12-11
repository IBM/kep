# 🚀 KEP Quick Start Guide

Welcome to the Knowledge Extraction Pipeline (KEP) Quick Start! This directory contains a series of standalone Python scripts that will guide you through understanding and using KEP.

## 📋 Overview

KEP transforms unstructured scientific documents into structured knowledge using foundation models:

**PDF → Classify → Extract → JSON**

## 🗂️ Quick Start Files

Run these files in order for the best learning experience:

### 1️⃣ `01_hello_kep.py` - Introduction
- 📖 Overview of KEP capabilities
- 🏗️ Architecture explanation
- 🎯 Use cases and examples

### 2️⃣ `02_environment_check.py` - Environment Setup
- 🔍 Check Python version and dependencies
- 📦 Verify KEP installation
- 🛠️ Installation guidance

### 3️⃣ `03_test_connections.py` - Provider Testing
- 🔐 Test IBM Cloud authentication
- 🤖 Test WatsonX connection
- 🔍 Discover available models
- 🚨 Comprehensive error diagnosis

### 4️⃣ `04_understanding_schemas.py` - Schema Deep Dive
- 📋 Classification schema structure
- 🏗️ Extraction schema structure
- 📚 Examples and best practices
- 🎯 Few-shot vs zero-shot modes

### 5️⃣ `05_pipeline_demo.py` - Pipeline Execution
- 🚀 Run complete KEP pipeline
- ⚙️ Configuration options
- 📊 Monitor progress
- 🔧 Command-line generation

### 6️⃣ `06_results_explorer.py` - Output Analysis
- 📂 Understand output structure
- 📊 Analyze results
- 📈 Extract insights
- 🔍 Debug failed extractions

### 7️⃣ `07_custom_schemas.py` - Schema Creation
- ✏️ Create custom classification schemas
- 🏗️ Build extraction schemas
- 🧪 Test schema effectiveness
- 💾 Save and manage schemas

### 8️⃣ `08_troubleshooting.py` - Advanced Diagnostics
- 🏥 Comprehensive health check
- 🔧 Fix common issues
- 📞 Support information
- 🎯 Performance optimization

## 🚀 Quick Start

1. **Check your environment:**
   ```bash
   python "02_environment_check.py"
   ```

2. **Test connections:**
   ```bash
   python "03_test_connections.py"
   ```

3. **Run your first pipeline:**
   ```bash
   python "05_pipeline_demo.py"
   ```

## 📋 Prerequisites

- **Python 3.8+**
- **KEP dependencies** (install with `pip install -r ../requirements.txt`)
- **IBM WatsonX or RITS access**
- **API credentials configured**

## 🔧 Configuration

Each script will guide you through the necessary configuration. You can set credentials via:

1. **Environment variables:**
   ```bash
   export WATSONX_APIKEY="your-api-key"
   export WATSONX_PROJECT_ID="your-project-id"
   ```

2. **Config files:** Update `../llm/watsonx/config.yaml`

3. **Manual input:** Scripts will prompt if needed

## 💡 Tips

- **Run scripts individually** - Each is standalone and self-contained
- **Follow the numbered order** - Each builds on previous knowledge
- **Check output carefully** - Scripts provide detailed feedback
- **Use debug mode** - Many scripts have verbose options

## 🆘 Getting Help

If you encounter issues:

1. **Run diagnostics:** `python "08_troubleshooting.py"`
2. **Check logs:** Look for error messages and suggestions
3. **Review docs:** See `../README.md` and `../UNIFIED_SETUP.md`
4. **Contact support:** Team contacts in `08_troubleshooting.py`

## 🎯 Next Steps

After completing the Quick Start:

- **Process your own PDFs** - Add files to `../pdfs/`
- **Create custom schemas** - Design for your domain
- **Integrate into workflows** - Use programmatically
- **Scale up processing** - Handle larger document sets

---

**Happy Knowledge Extracting! 🧠✨**