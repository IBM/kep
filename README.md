<div align="center">

<h1><strong>Knowledge Extraction Pipeline (KEP)</strong></h1>

<h3>A scalable pipeline for turning unstructured scientific text into structured knowledge with foundation models.</h3>

</div>

---

## 1 · What is KEP ?

KEP ingests PDFs / plain-text, splits them into chunks, calls an LLM for either

* **Extraction** – return JSON that follows a user–defined schema, or  
* **Classification** – tag each paragraph (e.g. “relevant” / “irrelevant”)

## 1.1 What does KEP do?

1. **Convert** Every PDF is rendered to Markdown and split into paragraphs.  
2. **Classify** Each paragraph is labelled *relevant* / *irrelevant* with an LLM.  
3. **Extract** A second LLM call turns every *relevant* paragraph into JSON
   that follows **your** schema.  

Everything is fully streamed: no intermediate database, no GPUs required.

---

## 2 · Getting Started

### 🚀 Quick Start Journey

**New to KEP?** Follow our interactive Quick Start journey for the best learning experience:

```bash
# Navigate to Quick Start directory
cd "Quick Start"

# 1️⃣ Learn about KEP (5 minutes)
python "01_hello_kep.py"

# 2️⃣ Check your environment (2 minutes)
python "02_environment_check.py"

# 3️⃣ Test LLM connections (3 minutes)
python "03_test_connections.py"

# 4️⃣ Understand schemas (10 minutes)
python "04_understanding_schemas.py"

# 5️⃣ Run your first pipeline (15 minutes)
python "05_pipeline_demo.py"

# 6️⃣ Explore results (5 minutes)
python "06_results_explorer.py"

# 7️⃣ Create custom schemas (20 minutes)
python "07_custom_schemas.py"

# 8️⃣ Troubleshooting & support (as needed)
python "08_troubleshooting.py"
```

**Total time: ~60 minutes** to become proficient with KEP!

### ⚡ Direct Command Line Usage

For experienced users or production environments:

```bash
python run_pipeline.py \
  --pdf-dir     ./pdfs                              \   # folder with PDFs
  --cls-schema  ./schemas/pfas_classification.json  \   # relevant / irrelevant
  --ext-schema  ./schemas/pfas_extraction.json      \   # your JSON schema
  --work-dir    ./runs/demo                         \
  --provider    watsonx                             \   # or rits
  --model-id    mistralai/mistral-large             \
  --prompt-mode few                                 \   # zero | few
  --debug-io                                        # dump every prompt + raw reply
```

### 2.1 Prerequisites

Before running KEP, ensure you have:
- Python 3.8+ installed
- Required dependencies: `pip install -r requirements.txt`
- LLM provider access (WatsonX or RITS)
- API credentials configured
- PDF files and schemas ready

> **📋 For complete multi-repository setup including Data_llm_extractor, Docling, and Jupyter Lab, see [UNIFIED_SETUP.md](./UNIFIED_SETUP.md)**
> 
> **🎯 For guided setup and learning, use the [Quick Start journey](#-quick-start-journey) above!**

Resulting tree:

```pgsql
runs/demo/
 ├─ ingest/all_paragraphs.json
 ├─ classified_full.json
 ├─ classified_relevant.json
 ├─ structured.json
 ├─ classification/ …              # per-paragraph logs
 ├─ extraction/     …              # per-paragraph logs
 ├─ general_metadata.json
 ├─ llm_metadata.json
 └─ run.log
```

---

## 3 · Environment setup 

#### Cloning the Repository 

Use one of the following commands:


```bash
# Using Git:
git clone -b master git@github.ibm.com:brl-kbe/Knowledge-Extraction-Pipeline.git
cd knowledge-extraction-pipeline
```

Alternatively, using the GitHub CLI:


```bash
gh repo clone brl-kbe/Knowledge-Extraction-Pipeline -- -b master
cd knowledge-extraction-pipeline
```

#### Creating the Environment and Installing Dependencies 

Set up your environment and install the required packages:

```bash
# Create virtual environment (recommended)
python -m venv kep-env
source kep-env/bin/activate  # On Windows: kep-env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3.1 Configuring Models and API Keys 

All provider settings live **inside the repository** under `llm/<provider>/config.yaml`.

#### WatsonX Configuration

```yaml
# llm/watsonx/config.yaml
url: "https://us-south.ml.cloud.ibm.com"
apikey: "YOUR_WATSONX_API_KEY"
project_id: "YOUR_PROJECT_ID"

parameters:
  decoding_method: greedy
  max_new_tokens: 2000
  temperature: 0.7
  repetition_penalty: 1.1
  stop_sequences: ["\n\n"]
```

#### RITS Configuration

```yaml
# llm/rits/config.yaml (create this file if using RITS)
api_url: "YOUR_RITS_ENDPOINT"
rits_api_key: "YOUR_RITS_API_KEY"

request_defaults:
  temperature: 0.7
  max_tokens: 2000
  top_p: 0.9
```

#### Environment Variables Override

Every config key can be overridden by environment variables:

**WatsonX:**
- `WATSONX_URL`
- `WATSONX_APIKEY` 
- `WATSONX_PROJECT_ID`

**RITS:**
- `RITS_API_URL`
- `RITS_API_KEY`

```bash
# Example: Override API key via environment
export WATSONX_APIKEY="your-actual-key-here"
python run_pipeline.py --provider watsonx ...
```

#### Adding New Providers

1. Create `llm/<provider_name>/client.py` implementing `LLMClient`
2. Add matching `config.yaml` 
3. Register with `@register_provider("provider_name")` decorator

```python
# llm/custom/client.py
from llm.base import LLMClient
from llm.factory import register_provider

@register_provider("custom")
class CustomClient(LLMClient):
    def inference(self, messages):
        # Your implementation
        pass
```

## 4 Requesting Access 

The KEP is currently in its **Beta phase**, and access to the code‑base is **strictly controlled**.  
If you would like to test or contribute, please e‑mail one of the contacts below with a short description of your use‑case and the GitHub (or IBM Git) username you would like to whitelist. 

| Contact | Role | E‑mail |
|---------|------|--------|
| Viviane Torres | Senior Research Scientist, *Manager* | [vivianet@br.ibm.com](mailto:vivianet@br.ibm.com) |
| Marcelo Archanjo | Senior Research Scientist | [marcelo.archanjo@ibm.com](mailto:marcelo.archanjo@ibm.com) |
| Anaximandro Souza | PhD Researcher | [anaximandrosouza@ibm.com](mailto:anaximandrosouza@ibm.com) |

> **Tip:** please use your corporate e‑mail (or the e‑mail associated with the Git account you plan to use) so that the team can locate your profile quickly.

---

## 4.1 · Quick Start Learning Path

The `Quick Start/` directory contains 8 interactive Python scripts designed to teach you KEP progressively:

| Script | Purpose | Time | Description |
|--------|---------|------|-------------|
| **01_hello_kep.py** | Introduction | 5 min | Overview, architecture, use cases, success stories |
| **02_environment_check.py** | Environment | 2 min | Python, dependencies, KEP installation validation |
| **03_test_connections.py** | Connectivity | 3 min | LLM providers, authentication, model discovery |
| **04_understanding_schemas.py** | Schemas | 10 min | Classification vs extraction, few-shot vs zero-shot |
| **05_pipeline_demo.py** | Execution | 15 min | Complete pipeline run with guided configuration |
| **06_results_explorer.py** | Analysis | 5 min | Results exploration, quality assessment, export |
| **07_custom_schemas.py** | Customization | 20 min | Domain-specific schema creation workshop |
| **08_troubleshooting.py** | Support | As needed | Diagnostics, automated fixes, help resources |

### 🎯 Learning Outcomes

After completing the Quick Start journey, you'll be able to:

- ✅ **Understand KEP architecture** and the three-stage pipeline
- ✅ **Configure authentication** for WatsonX and RITS providers  
- ✅ **Design effective schemas** for your research domain
- ✅ **Run complete pipelines** from PDFs to structured JSON
- ✅ **Analyze and export results** for further research
- ✅ **Troubleshoot issues** and optimize performance
- ✅ **Create custom schemas** for specialized domains

### 🚀 Quick Start Usage

```bash
# Navigate to Quick Start
cd "Quick Start"

# Interactive mode (recommended for learning)
python "01_hello_kep.py"

# Command-line options for automation
python "02_environment_check.py" --fix          # Auto-fix issues
python "03_test_connections.py" --verbose       # Detailed output
python "04_understanding_schemas.py" --validate # Check schemas
python "05_pipeline_demo.py" --auto             # Auto-run with defaults
python "06_results_explorer.py" --stats         # Statistics only
python "07_custom_schemas.py" --template bio    # Use biomedical template
python "08_troubleshooting.py" --quick          # Quick health check
```

### 💡 Pro Tips

- **Start with the numbered sequence** - each script builds on previous knowledge
- **Use interactive mode first** - then explore command-line options
- **Run diagnostics early** - `02_environment_check.py` and `03_test_connections.py`
- **Practice with examples** - use provided schemas before creating custom ones
- **Keep scripts handy** - they're useful for ongoing troubleshooting and analysis

---

## 5 · Advanced Configuration

### 5.1 Schema Customization

Schemas define both the extraction structure and provide examples for few-shot prompting.

#### Classification Schema Structure

```json
{
  "PERSONA": "You are a scientific assistant...",
  "TASK": "Classify the paragraph as relevant or irrelevant",
  "INSTRUCTIONS": [
    "Return one valid JSON object",
    "Field classification must be exactly 'relevant' or 'irrelevant'"
  ],
  "SCHEMAS": {
    "classification": "relevant or irrelevant"
  },
  "EXAMPLE": [
    {
      "text": "Sample paragraph text...",
      "classification": "relevant"
    }
  ]
}
```

#### Extraction Schema Structure

```json
{
  "PERSONA": "You are a scientific information-extraction assistant",
  "TASK": "Extract structured data from paragraphs",
  "INSTRUCTIONS": [
    "Strict schema compliance",
    "Valid JSON only",
    "Empty lists for missing data"
  ],
  "SCHEMAS": {
    "materials": ["Material"],
    "properties": ["Property"],
    "applications": ["Application"]
  },
  "EXAMPLE": [
    {
      "text": "Sample paragraph...",
      "output": {
        "materials": ["lithium phosphate"],
        "properties": ["conductive"],
        "applications": ["battery electrolyte"]
      }
    }
  ]
}
```

### 5.2 Model and Hyperparameter Configuration

#### Available Models

**WatsonX Models:** 
- `mistralai/mistral-large`
- `meta-llama/llama-3-70b-instruct`
- `ibm/granite-13b-chat-v2`
- `google/flan-ul2`

**Model Parameters:**

```yaml
parameters:
  decoding_method: greedy        # greedy | sample
  max_new_tokens: 2000          # 1-4000
  temperature: 0.7              # 0.0-2.0 (only for sample)
  top_p: 0.9                    # 0.0-1.0 (only for sample)
  top_k: 50                     # 1-100 (only for sample)
  repetition_penalty: 1.1       # 1.0-2.0
  stop_sequences: ["\n\n"]       # Array of stop strings
```

#### Chunking Strategies

```bash
# Paragraph-based (default)
--chunk-strategy paragraph

# Sentence-based with custom size
--chunk-strategy sentence --chunk-size 5 --chunk-overlap 1

# Fixed character chunks
--chunk-strategy fixed --chunk-size 500 --chunk-overlap 50
```

#### Debugging Options

```bash
# Enable detailed I/O logging
--debug-io

# Set deterministic seed
export PIPELINE_SEED=123

# Custom work directory
--work-dir ./custom-output
```

### 5.3 Pipeline Modes

#### Zero-shot Mode
- Uses only instructions and schema
- Faster execution
- Good for simple extraction tasks

```bash
python run_pipeline.py --prompt-mode zero ...
```

#### Few-shot Mode
- Requires examples in schema JSON
- Better accuracy for complex tasks
- Examples must be in `EXAMPLE` array

```bash
python run_pipeline.py --prompt-mode few ...
```

**Important:** Few-shot mode will fail if schemas lack examples.

---

## 6 · Output Files

Each pipeline run creates the following structure:

```
runs/demo/
├── ingest/
│   └── all_paragraphs.json          # Converted PDF paragraphs
├── classification/                   # Per-paragraph classification logs
├── extraction/                       # Per-paragraph extraction logs
├── classified_full.json              # All paragraphs with classifications
├── classified_relevant.json          # Only relevant paragraphs
├── structured.json                   # Final extracted JSON
├── general_metadata.json             # Processing metadata
├── llm_metadata.json                 # Model and prompt metadata
└── run.log                           # Complete execution log
```

---

## 7 · Changelog

### 2025-06-11 - Quick Start Journey
- **Quick Start learning path added** – 8 interactive Python scripts for guided learning
- **Progressive tutorial system** – from introduction to advanced schema creation
- **Comprehensive diagnostics** – automated environment checking and troubleshooting
- **Interactive schema builders** – domain-specific templates and guided creation
- **Results exploration tools** – quality assessment and export capabilities
- **Robust error handling** – improved authentication testing and network diagnostics

### 2025-05-01 - Pipeline Streamlining
- **Evaluation framework removed** – the repository is now inference-only
- Strict few-shot contract: examples **must** reside inside the schema JSON
- New `ExtractorPipeline` wraps *convert → classify → extract* in ~100 LOC
- `utils/runner.py` simplified to call the new pipeline
- Logging makeover – single file per run (`run.log`) plus rich progress bars

---
Happy extracting 🎉