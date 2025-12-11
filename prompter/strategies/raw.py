import json
from .base import PromptStrategy, register_strategy


@register_strategy("raw")
class Raw(PromptStrategy):
    def placeholder_values(self):
        return {
            "PROMPT":      self.ph.get("PROMPT", ""),
        }