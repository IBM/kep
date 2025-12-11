"""
Few-shot prompt-building strategy
─────────────────────────────────
2025-05-01 update

Rules
•  Few-shot *always* pulls its examples from inside the schema JSON
   (keys accepted: “examples”, “EXAMPLES”, “EXAMPLE”, “example”).
•  No random sampling, no external overrides, no --num-exem juggling.
•  If no examples are present, we raise a hard error so the caller
   knows the schema has to be fixed.
"""

from __future__ import annotations

import json
from typing import Dict, List

from .base import PromptStrategy, register_strategy


@register_strategy("few")
class FewShot(PromptStrategy):
    # ------------------------------------------------------------------ helpers
    def _select_examples(self) -> List[Dict]:
        """
        Locate the examples array inside the schema placeholder map.
        Accepts a handful of historical spellings for backward-compat.
        """
        inside = (
            self.ph.get("EXAMPLES")     # preferred
            or self.ph.get("examples")
            or self.ph.get("EXAMPLE")   # legacy singular
            or self.ph.get("example")
            or []
        )
        if inside:
            return inside               # keep **all** – never sample

        # nothing found – hard-fail
        raise ValueError(
            "Few-shot mode requires an 'examples' array inside the schema JSON. "
            "None found."
        )

    # ------------------------------------------------------------------ public
    def placeholder_values(self) -> Dict[str, str]:
        examples = self._select_examples()
        return {
            "PERSONA":      self.ph.get("PERSONA", ""),
            "TASK":         self.ph.get("TASK", ""),
            "INSTRUCTIONS": "\n".join(self.ph.get("INSTRUCTIONS", [])),
            "SCHEMAS":      json.dumps(self.ph.get("SCHEMAS", {}), indent=2),
            "EXAMPLE":      json.dumps(examples, indent=2, ensure_ascii=False),
        }