"""
llm package – façade re-export.

Usage
-----
from llm import LLMFactory

client = LLMFactory.create(
    provider="watsonx",
    config_dir="llm"          # folder that holds per-client YAMLs
)
result = client.inference("Your prompt here")
"""
from .factory import LLMFactory          # noqa: F401