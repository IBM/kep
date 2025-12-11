"""
Public façade

    from prompter import Prompter

    p = Prompter(schema_json="schemas/materials.json",
                 strategy="few",
                 num_examples=3)
    prompt = p.build()
"""
from .prompter import Prompter  # noqa: F401