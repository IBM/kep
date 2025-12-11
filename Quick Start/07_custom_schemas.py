#!/usr/bin/env python3
"""
07_custom_schemas.py - Custom Schema Creation Workshop

This script provides an interactive workshop for creating domain-specific
schemas tailored to your research needs.

Features:
- Interactive schema builder with guidance
- Domain-specific templates (materials, medical, environmental, etc.)
- Schema validation and testing
- Example generation assistance
- Best practices enforcement

Usage:
    python "07_custom_schemas.py"                    # Interactive builder
    python "07_custom_schemas.py" --template bio     # Use biomedical template
    python "07_custom_schemas.py" --validate         # Validate existing schemas
    python "07_custom_schemas.py" --examples         # Show example schemas
"""

import sys
import json
import os
from pathlib import Path
import argparse

def print_header(title):
    """Print formatted header"""
    print(f"\n{'='*70}")
    print(f" {title}")
    print('='*70)

def print_section(title):
    """Print section header"""
    print(f"\n{title}")
    print("-" * len(title))

def find_kep_root():
    """Find KEP root directory"""
    current_dir = Path.cwd()
    if current_dir.name == "Quick Start":
        return current_dir.parent
    return current_dir

def get_domain_templates():
    """Return predefined domain templates"""
    templates = {
        "materials": {
            "name": "Materials Science",
            "description": "For battery materials, semiconductors, catalysts, etc.",
            "classification": {
                "persona": "You are a materials science research assistant specializing in advanced materials characterization and properties.",
                "task": "Classify paragraphs as containing materials science information or not.",
                "categories": ["materials_related", "not_materials_related"],
                "focus_areas": ["material properties", "synthesis methods", "characterization techniques", "performance metrics", "applications"]
            },
            "extraction": {
                "persona": "You are a materials science data extraction specialist with expertise in materials properties and characterization.",
                "task": "Extract structured information about materials, their properties, synthesis, and performance.",
                "fields": {
                    "materials": ["List of material names, formulas, or compositions"],
                    "material_type": "Type/category of material (e.g., ceramic, polymer, metal)",
                    "properties": ["List of material properties mentioned"],
                    "synthesis_method": "Preparation or synthesis method if described",
                    "characterization_techniques": ["Analytical methods used"],
                    "performance_metrics": {
                        "mechanical": "Strength, modulus, hardness with units",
                        "electrical": "Conductivity, resistivity with units",
                        "thermal": "Temperature-related properties with units",
                        "other": "Other performance metrics with units"
                    },
                    "applications": ["Potential or actual applications"],
                    "experimental_conditions": "Temperature, pressure, atmosphere if specified"
                }
            }
        },
        
        "biomedical": {
            "name": "Biomedical Research",
            "description": "For drug discovery, clinical trials, medical devices, etc.",
            "classification": {
                "persona": "You are a biomedical research assistant with expertise in clinical research and drug development.",
                "task": "Classify paragraphs as containing biomedical research information or not.",
                "categories": ["biomedical_related", "not_biomedical_related"],
                "focus_areas": ["drug compounds", "clinical trials", "biological mechanisms", "medical devices", "therapeutic outcomes"]
            },
            "extraction": {
                "persona": "You are a biomedical data extraction specialist with expertise in clinical research and pharmacology.",
                "task": "Extract structured information about drugs, treatments, clinical outcomes, and medical research.",
                "fields": {
                    "compounds": ["Drug names, chemical compounds, or active ingredients"],
                    "indication": "Medical condition or disease being treated",
                    "mechanism_of_action": "How the treatment works biologically",
                    "clinical_trial_info": {
                        "phase": "Clinical trial phase (I, II, III, IV)",
                        "participants": "Number of participants",
                        "duration": "Study duration",
                        "design": "Study design (randomized, placebo-controlled, etc.)"
                    },
                    "outcomes": {
                        "efficacy": "Treatment effectiveness measures",
                        "safety": "Side effects or safety concerns",
                        "biomarkers": "Biological markers measured"
                    },
                    "dosage": "Drug dosage and administration route",
                    "medical_devices": ["Medical devices or equipment mentioned"],
                    "study_population": "Patient demographics or inclusion criteria"
                }
            }
        },
        
        "environmental": {
            "name": "Environmental Science",
            "description": "For pollution studies, climate research, ecology, etc.",
            "classification": {
                "persona": "You are an environmental science research assistant specializing in environmental monitoring and impact assessment.",
                "task": "Classify paragraphs as containing environmental science information or not.",
                "categories": ["environmental_related", "not_environmental_related"],
                "focus_areas": ["pollution data", "environmental impacts", "climate measurements", "ecological studies", "remediation methods"]
            },
            "extraction": {
                "persona": "You are an environmental science data extraction specialist with expertise in environmental monitoring and assessment.",
                "task": "Extract structured information about environmental conditions, pollutants, impacts, and mitigation measures.",
                "fields": {
                    "pollutants": ["Chemical pollutants, contaminants, or substances"],
                    "environmental_matrix": "Where measured (air, water, soil, sediment, biota)",
                    "concentrations": {
                        "values": "Concentration values with units",
                        "detection_limits": "Detection or quantification limits",
                        "reference_standards": "Regulatory limits or guidelines"
                    },
                    "sampling_info": {
                        "location": "Geographic location or coordinates",
                        "date": "Sampling date or period",
                        "methodology": "Sampling and analysis methods"
                    },
                    "environmental_impacts": ["Observed or predicted impacts"],
                    "sources": ["Pollution sources or emission sources"],
                    "mitigation_measures": ["Remediation or control measures"],
                    "regulatory_context": "Relevant regulations or standards"
                }
            }
        },
        
        "energy": {
            "name": "Energy Research",
            "description": "For solar cells, fuel cells, energy storage, etc.",
            "classification": {
                "persona": "You are an energy research assistant specializing in renewable energy technologies and energy storage systems.",
                "task": "Classify paragraphs as containing energy research information or not.",
                "categories": ["energy_related", "not_energy_related"],
                "focus_areas": ["energy conversion", "energy storage", "efficiency metrics", "renewable technologies", "performance optimization"]
            },
            "extraction": {
                "persona": "You are an energy research data extraction specialist with expertise in energy technologies and performance metrics.",
                "task": "Extract structured information about energy systems, performance, and technologies.",
                "fields": {
                    "technology_type": "Type of energy technology (solar, battery, fuel cell, etc.)",
                    "materials": ["Active materials or components"],
                    "performance_metrics": {
                        "efficiency": "Energy conversion efficiency with units",
                        "capacity": "Energy or power capacity with units",
                        "voltage": "Operating voltage with units",
                        "current": "Current density or current with units",
                        "cycle_life": "Cycling stability or lifetime",
                        "degradation": "Performance degradation rates"
                    },
                    "operating_conditions": {
                        "temperature": "Operating temperature range",
                        "pressure": "Operating pressure",
                        "environment": "Operating environment conditions"
                    },
                    "fabrication_method": "Manufacturing or fabrication process",
                    "testing_conditions": "Test protocols or conditions",
                    "cost_metrics": "Cost-related information with units",
                    "applications": ["Target applications or use cases"]
                }
            }
        }
    }
    
    return templates

def show_domain_templates():
    """Display available domain templates"""
    print_header("🏭 Available Domain Templates")
    
    templates = get_domain_templates()
    
    for key, template in templates.items():
        print(f"\n📋 {template['name']} ({key})")
        print(f"   {template['description']}")
        print(f"   Focus: {', '.join(template['classification']['focus_areas'][:3])}...")

def interactive_schema_builder():
    """Interactive schema building workshop"""
    print_header("🛠️ Custom Schema Builder Workshop")
    
    print("""
Welcome to the KEP Schema Builder! I'll guide you through creating
domain-specific schemas for your research.

Let's start by understanding your research domain...
""")
    
    # Step 1: Choose approach
    print("🎯 Schema Creation Approach:")
    print("   1. Start from a domain template")
    print("   2. Build completely from scratch")
    print("   3. Modify an existing schema")
    
    approach = input("\nChoose approach (1-3): ").strip()
    
    if approach == "1":
        return build_from_template()
    elif approach == "2":
        return build_from_scratch()
    elif approach == "3":
        return modify_existing_schema()
    else:
        print("Invalid choice. Starting from scratch...")
        return build_from_scratch()

def build_from_template():
    """Build schema starting from a domain template"""
    print_section("📋 Template-Based Schema Creation")
    
    templates = get_domain_templates()
    
    print("Available templates:")
    for i, (key, template) in enumerate(templates.items(), 1):
        print(f"   {i}. {template['name']} - {template['description']}")
    
    while True:
        try:
            choice = input(f"\nSelect template (1-{len(templates)}): ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(templates):
                template_key = list(templates.keys())[idx]
                template = templates[template_key]
                break
            else:
                print(f"Invalid choice. Enter 1-{len(templates)}")
        except ValueError:
            print("Invalid input. Enter a number.")
    
    print(f"\n✅ Selected: {template['name']}")
    
    # Customize the template
    domain = input(f"\nSpecific research area within {template['name']}: ").strip()
    if not domain:
        domain = template['name']
    
    # Build classification schema
    cls_schema = build_classification_schema_from_template(template, domain)
    
    # Build extraction schema
    ext_schema = build_extraction_schema_from_template(template, domain)
    
    return save_schemas(cls_schema, ext_schema, domain)

def build_classification_schema_from_template(template, domain):
    """Build classification schema from template"""
    print_section("🏷️ Customizing Classification Schema")
    
    cls_template = template['classification']
    
    # Customize persona
    persona = cls_template['persona'].replace("materials science", domain.lower())
    
    # Customize task
    relevance_criteria = input(f"What makes text relevant to your {domain} research? ").strip()
    if not relevance_criteria:
        relevance_criteria = f"{domain} information"
    
    task = f"Classify paragraphs as containing {relevance_criteria} or not."
    
    # Categories
    relevant_category = input("Name for relevant category (e.g., 'battery_related'): ").strip()
    if not relevant_category:
        relevant_category = cls_template['categories'][0]
    
    irrelevant_category = input("Name for irrelevant category (e.g., 'not_battery_related'): ").strip()
    if not irrelevant_category:
        irrelevant_category = cls_template['categories'][1]
    
    # Instructions
    custom_instructions = []
    custom_instructions.append("Return one valid JSON object")
    custom_instructions.append(f"Field 'classification' must be exactly '{relevant_category}' or '{irrelevant_category}'")
    
    focus_input = input("Additional focus areas (comma-separated): ").strip()
    if focus_input:
        focus_areas = [area.strip() for area in focus_input.split(',')]
        custom_instructions.append(f"Focus on: {', '.join(focus_areas)}")
    
    # Build schema
    cls_schema = {
        "PERSONA": persona,
        "TASK": task,
        "INSTRUCTIONS": custom_instructions,
        "SCHEMAS": {
            "classification": f"{relevant_category} or {irrelevant_category}"
        },
        "EXAMPLE": []
    }
    
    # Add examples
    print(f"\n📚 Adding Examples (recommended: 3-5)")
    add_examples_to_classification(cls_schema, relevant_category, irrelevant_category)
    
    return cls_schema

def build_extraction_schema_from_template(template, domain):
    """Build extraction schema from template"""
    print_section("🏗️ Customizing Extraction Schema")
    
    ext_template = template['extraction']
    
    # Customize persona
    persona = ext_template['persona'].replace("materials science", domain.lower())
    
    # Customize task
    data_types = input("What specific data do you want to extract? ").strip()
    if not data_types:
        data_types = f"{domain} properties and metrics"
    
    task = f"Extract structured information about {data_types} from scientific text."
    
    # Instructions
    instructions = [
        "Strict schema compliance required",
        "Return valid JSON only",
        "Use empty lists for missing information",
        "Extract specific values with units when available"
    ]
    
    # Build schema structure
    print(f"\n📋 Schema Structure Design:")
    print("I'll help you design the extraction schema based on the template...")
    
    # Use template fields as starting point
    fields = dict(ext_template['fields'])
    
    # Allow customization
    print("\nTemplate fields:")
    for field, description in fields.items():
        print(f"   • {field}: {description}")
    
    modify = input("\nModify template fields? (y/n): ").lower() == 'y'
    
    if modify:
        fields = customize_extraction_fields(fields)
    
    # Build schema
    ext_schema = {
        "PERSONA": persona,
        "TASK": task,
        "INSTRUCTIONS": instructions,
        "SCHEMAS": fields,
        "EXAMPLE": []
    }
    
    # Add examples
    print(f"\n📚 Adding Examples (recommended: 2-3)")
    add_examples_to_extraction(ext_schema)
    
    return ext_schema

def build_from_scratch():
    """Build schema completely from scratch"""
    print_section("🔨 Building Schema from Scratch")
    
    # Get basic information
    domain = input("Research domain (e.g., 'quantum computing', 'marine biology'): ").strip()
    if not domain:
        domain = "research"
    
    print(f"\nBuilding schemas for: {domain}")
    
    # Build classification schema
    cls_schema = build_classification_from_scratch(domain)
    
    # Build extraction schema
    ext_schema = build_extraction_from_scratch(domain)
    
    return save_schemas(cls_schema, ext_schema, domain)

def build_classification_from_scratch(domain):
    """Build classification schema from scratch"""
    print_section("🏷️ Classification Schema Design")
    
    # Persona
    expertise = input(f"What specific expertise should the AI have in {domain}? ").strip()
    if not expertise:
        expertise = f"{domain} research"
    
    persona = f"You are a research assistant specializing in {expertise}."
    
    # Task
    relevance_criteria = input(f"What makes text relevant to your {domain} research? ").strip()
    task = f"Classify paragraphs as containing information about {relevance_criteria} or not."
    
    # Categories
    relevant = input("Name for relevant category: ").strip() or f"{domain.lower().replace(' ', '_')}_related"
    irrelevant = input("Name for irrelevant category: ").strip() or f"not_{domain.lower().replace(' ', '_')}_related"
    
    # Instructions
    instructions = [
        "Return one valid JSON object",
        f"Field 'classification' must be exactly '{relevant}' or '{irrelevant}'"
    ]
    
    additional_rules = input("Additional classification rules (optional): ").strip()
    if additional_rules:
        instructions.append(additional_rules)
    
    # Build schema
    cls_schema = {
        "PERSONA": persona,
        "TASK": task,
        "INSTRUCTIONS": instructions,
        "SCHEMAS": {
            "classification": f"{relevant} or {irrelevant}"
        },
        "EXAMPLE": []
    }
    
    # Add examples
    add_examples_to_classification(cls_schema, relevant, irrelevant)
    
    return cls_schema

def build_extraction_from_scratch(domain):
    """Build extraction schema from scratch"""
    print_section("🏗️ Extraction Schema Design")
    
    # Persona
    persona = f"You are an information extraction specialist with expertise in {domain}."
    
    # Task
    data_types = input(f"What specific data should be extracted from {domain} texts? ").strip()
    task = f"Extract structured information about {data_types} from scientific text."
    
    # Instructions
    instructions = [
        "Strict schema compliance required",
        "Return valid JSON only",
        "Use empty lists for missing information"
    ]
    
    units_important = input("Are numerical values with units important? (y/n): ").lower() == 'y'
    if units_important:
        instructions.append("Extract specific values with units when available")
    
    # Build schema fields
    print(f"\n📋 Designing extraction fields...")
    fields = design_extraction_fields()
    
    # Build schema
    ext_schema = {
        "PERSONA": persona,
        "TASK": task,
        "INSTRUCTIONS": instructions,
        "SCHEMAS": fields,
        "EXAMPLE": []
    }
    
    # Add examples
    add_examples_to_extraction(ext_schema)
    
    return ext_schema

def design_extraction_fields():
    """Interactive field design for extraction schema"""
    fields = {}
    
    print("Let's design the extraction fields. Enter field names and descriptions.")
    print("Examples: 'materials', 'temperature', 'performance_metrics'")
    print("Press Enter without input when done.")
    
    while True:
        field_name = input(f"\nField name (or Enter to finish): ").strip()
        if not field_name:
            break
        
        print(f"\nField: {field_name}")
        print("Type options:")
        print("   1. List of strings")
        print("   2. Single string")
        print("   3. Nested object (with sub-fields)")
        print("   4. Number with units")
        
        field_type = input("Select type (1-4): ").strip()
        
        if field_type == "1":
            description = input("Description of list items: ").strip()
            fields[field_name] = [description or "List of relevant items"]
        elif field_type == "2":
            description = input("Description: ").strip()
            fields[field_name] = description or "Single value description"
        elif field_type == "3":
            print("Define sub-fields:")
            sub_fields = {}
            while True:
                sub_name = input(f"  Sub-field name (or Enter to finish): ").strip()
                if not sub_name:
                    break
                sub_desc = input(f"  Description for {sub_name}: ").strip()
                sub_fields[sub_name] = sub_desc or "Sub-field description"
            fields[field_name] = sub_fields
        elif field_type == "4":
            unit_type = input("Expected units (e.g., 'mg/L', 'degrees C'): ").strip()
            fields[field_name] = f"Numerical value with units ({unit_type})"
        else:
            fields[field_name] = "Field description"
    
    return fields

def customize_extraction_fields(template_fields):
    """Allow customization of template extraction fields"""
    fields = dict(template_fields)
    
    print("\nField customization:")
    print("   a - Add new field")
    print("   r - Remove field")
    print("   m - Modify field")
    print("   d - Done")
    
    while True:
        action = input("\nAction: ").lower().strip()
        
        if action == 'd':
            break
        elif action == 'a':
            field_name = input("New field name: ").strip()
            if field_name:
                description = input(f"Description for {field_name}: ").strip()
                fields[field_name] = description or "New field"
        elif action == 'r':
            print("Current fields:", list(fields.keys()))
            field_name = input("Field to remove: ").strip()
            if field_name in fields:
                del fields[field_name]
                print(f"Removed {field_name}")
        elif action == 'm':
            print("Current fields:", list(fields.keys()))
            field_name = input("Field to modify: ").strip()
            if field_name in fields:
                new_desc = input(f"New description for {field_name}: ").strip()
                if new_desc:
                    fields[field_name] = new_desc
    
    return fields

def add_examples_to_classification(schema, relevant_cat, irrelevant_cat):
    """Help user add examples to classification schema"""
    print("\nAdding classification examples improves accuracy significantly!")
    
    examples = []
    
    # Add relevant examples
    print(f"\n📝 Examples for '{relevant_cat}':")
    for i in range(3):
        text = input(f"Relevant example {i+1} (or Enter to skip): ").strip()
        if text:
            examples.append({
                "text": text,
                "classification": relevant_cat
            })
    
    # Add irrelevant examples
    print(f"\n📝 Examples for '{irrelevant_cat}':")
    for i in range(2):
        text = input(f"Irrelevant example {i+1} (or Enter to skip): ").strip()
        if text:
            examples.append({
                "text": text,
                "classification": irrelevant_cat
            })
    
    schema["EXAMPLE"] = examples
    print(f"\n✅ Added {len(examples)} examples")

def add_examples_to_extraction(schema):
    """Help user add examples to extraction schema"""
    print("\nAdding extraction examples helps the model understand your schema!")
    
    examples = []
    
    for i in range(2):
        print(f"\n📝 Extraction Example {i+1}:")
        text = input("Source text: ").strip()
        if not text:
            break
        
        print("Now provide the expected extraction for this text.")
        print("You can provide a simplified version - I'll format it properly.")
        
        output = {}
        fields = schema["SCHEMAS"]
        
        for field_name, field_desc in fields.items():
            if isinstance(field_desc, list):
                value = input(f"{field_name} (comma-separated): ").strip()
                if value:
                    output[field_name] = [item.strip() for item in value.split(',')]
                else:
                    output[field_name] = []
            elif isinstance(field_desc, dict):
                print(f"Sub-fields for {field_name}:")
                sub_output = {}
                for sub_field in field_desc.keys():
                    sub_value = input(f"  {sub_field}: ").strip()
                    sub_output[sub_field] = sub_value
                output[field_name] = sub_output
            else:
                value = input(f"{field_name}: ").strip()
                output[field_name] = value
        
        examples.append({
            "text": text,
            "output": output
        })
    
    schema["EXAMPLE"] = examples
    print(f"\n✅ Added {len(examples)} examples")

def modify_existing_schema():
    """Modify an existing schema file"""
    print_section("✏️ Modify Existing Schema")
    
    kep_root = find_kep_root()
    schemas_dir = kep_root / "schemas"
    
    if not schemas_dir.exists():
        print("❌ No schemas directory found")
        return False
    
    schema_files = list(schemas_dir.glob("*.json"))
    if not schema_files:
        print("❌ No schema files found")
        return False
    
    print("Available schemas:")
    for i, schema_file in enumerate(schema_files, 1):
        print(f"   {i}. {schema_file.name}")
    
    while True:
        try:
            choice = input(f"Select schema to modify (1-{len(schema_files)}): ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(schema_files):
                schema_file = schema_files[idx]
                break
            else:
                print(f"Invalid choice. Enter 1-{len(schema_files)}")
        except ValueError:
            print("Invalid input. Enter a number.")
    
    # Load existing schema
    try:
        with open(schema_file, 'r') as f:
            schema = json.load(f)
    except Exception as e:
        print(f"❌ Error loading schema: {e}")
        return False
    
    print(f"\n✅ Loaded: {schema_file.name}")
    print("Current schema structure:")
    for key in schema.keys():
        if key == "EXAMPLE":
            print(f"   {key}: {len(schema[key])} examples")
        else:
            print(f"   {key}: {type(schema[key]).__name__}")
    
    # Modification options
    print(f"\nModification options:")
    print("   1. Add/modify examples")
    print("   2. Update persona")
    print("   3. Modify task description")
    print("   4. Update instructions")
    print("   5. Modify schema structure (extraction only)")
    
    mod_choice = input("Select modification (1-5): ").strip()
    
    if mod_choice == "1":
        modify_examples(schema)
    elif mod_choice == "2":
        new_persona = input("New persona: ").strip()
        if new_persona:
            schema["PERSONA"] = new_persona
    elif mod_choice == "3":
        new_task = input("New task description: ").strip()
        if new_task:
            schema["TASK"] = new_task
    elif mod_choice == "4":
        modify_instructions(schema)
    elif mod_choice == "5":
        if "classification" not in str(schema.get("SCHEMAS", {})).lower():
            modify_schema_structure(schema)
        else:
            print("Schema structure modification not available for classification schemas")
    
    # Save modified schema
    backup_path = schema_file.with_suffix('.json.backup')
    schema_file.rename(backup_path)
    print(f"📄 Backup saved: {backup_path.name}")
    
    with open(schema_file, 'w') as f:
        json.dump(schema, f, indent=2)
    
    print(f"✅ Modified schema saved: {schema_file.name}")
    return True

def modify_examples(schema):
    """Modify examples in a schema"""
    examples = schema.get("EXAMPLE", [])
    
    print(f"\nCurrent examples: {len(examples)}")
    for i, example in enumerate(examples):
        text = example.get("text", "")[:50] + "..."
        print(f"   {i+1}. {text}")
    
    print("\nModification options:")
    print("   a - Add new example")
    print("   r - Remove example")
    print("   c - Clear all examples")
    
    action = input("Action: ").lower().strip()
    
    if action == "a":
        add_new_example(schema)
    elif action == "r":
        try:
            idx = int(input(f"Remove example number (1-{len(examples)}): ")) - 1
            if 0 <= idx < len(examples):
                removed = examples.pop(idx)
                print(f"Removed example: {removed.get('text', '')[:50]}...")
        except (ValueError, IndexError):
            print("Invalid example number")
    elif action == "c":
        confirm = input("Clear all examples? (y/n): ").lower()
        if confirm == "y":
            schema["EXAMPLE"] = []
            print("All examples cleared")

def add_new_example(schema):
    """Add a new example to schema"""
    text = input("Example text: ").strip()
    if not text:
        return
    
    # Determine schema type
    if "classification" in str(schema.get("SCHEMAS", {})).lower():
        # Classification example
        classification = input("Classification result: ").strip()
        if classification:
            new_example = {
                "text": text,
                "classification": classification
            }
            schema.setdefault("EXAMPLE", []).append(new_example)
            print("✅ Classification example added")
    else:
        # Extraction example
        print("Provide extraction output (simplified JSON):")
        output_str = input("Output: ").strip()
        try:
            output = json.loads(output_str)
            new_example = {
                "text": text,
                "output": output
            }
            schema.setdefault("EXAMPLE", []).append(new_example)
            print("✅ Extraction example added")
        except json.JSONDecodeError:
            print("❌ Invalid JSON format for output")

def save_schemas(cls_schema, ext_schema, domain):
    """Save the created schemas"""
    print_section("💾 Saving Schemas")
    
    kep_root = find_kep_root()
    schemas_dir = kep_root / "schemas"
    schemas_dir.mkdir(exist_ok=True)
    
    # Generate filenames
    safe_domain = domain.lower().replace(" ", "_").replace("-", "_")
    
    cls_filename = input(f"Classification schema filename [{safe_domain}_classification.json]: ").strip()
    if not cls_filename:
        cls_filename = f"{safe_domain}_classification.json"
    if not cls_filename.endswith('.json'):
        cls_filename += '.json'
    
    ext_filename = input(f"Extraction schema filename [{safe_domain}_extraction.json]: ").strip()
    if not ext_filename:
        ext_filename = f"{safe_domain}_extraction.json"
    if not ext_filename.endswith('.json'):
        ext_filename += '.json'
    
    # Save files
    cls_path = schemas_dir / cls_filename
    ext_path = schemas_dir / ext_filename
    
    try:
        with open(cls_path, 'w') as f:
            json.dump(cls_schema, f, indent=2)
        
        with open(ext_path, 'w') as f:
            json.dump(ext_schema, f, indent=2)
        
        print(f"✅ Schemas saved:")
        print(f"   📋 Classification: {cls_path}")
        print(f"   🏗️ Extraction: {ext_path}")
        
        # Show usage
        print(f"\n🚀 Use these schemas with:")
        print(f"   python run_pipeline.py \\")
        print(f"     --cls-schema ./schemas/{cls_filename} \\")
        print(f"     --ext-schema ./schemas/{ext_filename} \\")
        print(f"     --prompt-mode {'few' if cls_schema.get('EXAMPLE') else 'zero'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving schemas: {e}")
        return False

def validate_existing_schemas():
    """Validate all existing schemas"""
    print_header("✅ Schema Validation")
    
    kep_root = find_kep_root()
    schemas_dir = kep_root / "schemas"
    
    if not schemas_dir.exists():
        print("❌ No schemas directory found")
        return
    
    schema_files = list(schemas_dir.glob("*.json"))
    if not schema_files:
        print("❌ No schema files found")
        return
    
    print(f"Validating {len(schema_files)} schema files...\n")
    
    for schema_file in schema_files:
        validate_single_schema(schema_file)

def validate_single_schema(schema_path):
    """Validate a single schema file"""
    print(f"🔍 {schema_path.name}")
    print("-" * (len(schema_path.name) + 2))
    
    try:
        with open(schema_path, 'r') as f:
            schema = json.load(f)
    except Exception as e:
        print(f"❌ JSON parse error: {e}")
        return
    
    issues = []
    suggestions = []
    
    # Required fields
    required = ['PERSONA', 'TASK', 'INSTRUCTIONS', 'SCHEMAS']
    for field in required:
        if field not in schema:
            issues.append(f"Missing required field: {field}")
    
    # Validate persona
    persona = schema.get('PERSONA', '')
    if len(persona) < 20:
        suggestions.append("PERSONA could be more detailed")
    if 'assistant' not in persona.lower():
        suggestions.append("PERSONA should establish AI as an assistant")
    
    # Validate instructions
    instructions = schema.get('INSTRUCTIONS', [])
    if not isinstance(instructions, list):
        issues.append("INSTRUCTIONS should be a list")
    elif len(instructions) < 2:
        suggestions.append("Consider adding more detailed instructions")
    
    # Validate examples
    examples = schema.get('EXAMPLE', [])
    if not examples:
        suggestions.append("No examples - will run in zero-shot mode")
    else:
        for i, example in enumerate(examples):
            if 'text' not in example:
                issues.append(f"Example {i+1} missing 'text' field")
            if 'classification' not in example and 'output' not in example:
                issues.append(f"Example {i+1} missing result field")
    
    # Display results
    if not issues and not suggestions:
        print("✅ Schema is excellent!")
    else:
        if issues:
            print("❌ Issues found:")
            for issue in issues:
                print(f"   • {issue}")
        
        if suggestions:
            print("💡 Suggestions:")
            for suggestion in suggestions:
                print(f"   • {suggestion}")
    
    print()

def main():
    """Main custom schema creation function"""
    parser = argparse.ArgumentParser(description='KEP Custom Schema Creator')
    parser.add_argument('--template', choices=['materials', 'biomedical', 'environmental', 'energy'],
                       help='Use specific domain template')
    parser.add_argument('--validate', action='store_true',
                       help='Validate existing schemas')
    parser.add_argument('--examples', action='store_true',
                       help='Show example schemas')
    
    args = parser.parse_args()
    
    print("✏️ KEP Custom Schema Creator")
    print("Build domain-specific schemas for your research...")
    
    if args.validate:
        validate_existing_schemas()
        return True
    
    if args.examples:
        show_domain_templates()
        return True
    
    if args.template:
        templates = get_domain_templates()
        if args.template in templates:
            template = templates[args.template]
            print(f"\n📋 Building from {template['name']} template...")
            domain = input(f"Specific area within {template['name']}: ").strip() or template['name']
            cls_schema = build_classification_schema_from_template(template, domain)
            ext_schema = build_extraction_schema_from_template(template, domain)
            return save_schemas(cls_schema, ext_schema, domain)
        else:
            print(f"❌ Template '{args.template}' not found")
            return False
    
    # Interactive mode
    success = interactive_schema_builder()
    
    if success:
        print_header("🎉 Schema Creation Complete!")
        print("""
Your custom schemas are ready! Here's what to do next:

1️⃣ Test your schemas:
   • Run a small pilot with 1-2 PDFs
   • Check classification and extraction quality
   • Iterate on examples if needed

2️⃣ Optimize for your domain:
   • Add more diverse examples
   • Refine field descriptions
   • Adjust instructions based on results

3️⃣ Scale up processing:
   • Run on larger document collections
   • Monitor quality metrics
   • Export results for analysis

🚀 Ready to extract knowledge from your research domain!
""")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)