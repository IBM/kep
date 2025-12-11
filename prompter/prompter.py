"""
prompter/prompter.py
────────────────────
Builds the final prompt string by

  1.  loading a template YAML that only says **which placeholders appear
      in which order**;
  2.  asking a *strategy* object (zero-shot, few-shot, …) for the
      concrete values of those placeholders;
  3.  stitching everything together with sensible defaults.

Drop a new YAML file into *prompter/templates/* and call

    Prompter(schema_json="schemas/…json",
             strategy="my_strategy")

and you’re done – no code changes required.
"""

from __future__ import annotations
from pathlib import Path
from types import MappingProxyType
from typing import Any, Dict, List, Optional
import json, random, yaml

from .strategies import get_strategy_cls

# folder that holds zero_shot.yaml, few_shot.yaml, …
_TEMPLATE_DIR = Path(__file__).parent / "templates"


# --------------------------------------------------------------------------- helpers
def _wrap(placeholder: str, value: Any) -> str:
    """Pretty-print common sections."""
    if value is None or value == "":
        return ""

    if placeholder == "INSTRUCTIONS":
        if isinstance(value, list):
            return "\n".join(value)
    if placeholder == "SCHEMAS":
        return "Schema:\n" + (
            value if isinstance(value, str)
            else json.dumps(value, indent=2, ensure_ascii=False)
        )
    if placeholder in {"EXAMPLE", "EXAMPLES"}:
        return "Examples:\n" + (
            value if isinstance(value, str)
            else json.dumps(value, indent=2, ensure_ascii=False)
        )
    return str(value)


# --------------------------------------------------------------------------- main class
class Prompter:
    """
    Parameters
    ----------
    schema_json      path/str/dict – JSON that carries all raw values
    strategy         zero | few | any other you add under templates/
    num_examples     how many few-shot examples to keep (few-shot only)
    """

    def __init__(
        self,
        *,
        schema_json: str | Path | Dict[str, Any],
        strategy: str = "zero",
        num_examples: int = 3,
        chosen_examples: Optional[List[Dict[str, Any]]] = None,
        fallback_dataset: Optional[List[Dict[str, Any]]] = None,
        rng_seed: Optional[int] = None,
    ):
        # 1) -------- placeholder source ----------------------------------
        if isinstance(schema_json, (str, Path)):
            self._ph = json.loads(Path(schema_json).read_text(encoding="utf-8"))
        elif isinstance(schema_json, dict):
            self._ph = schema_json
        else:
            raise TypeError("schema_json must be path-like or dict")

        # 2) -------- strategy object ------------------------------------
        strat_cls = get_strategy_cls(strategy)
        self._strategy = strat_cls(
            placeholders=MappingProxyType(self._ph),
            num_examples=num_examples,
            chosen_examples=chosen_examples,
            fallback_dataset=fallback_dataset,
            rng=random.Random(rng_seed),
        )

        # 3) -------- load template YAML ---------------------------------
        cand = [
            _TEMPLATE_DIR / f"{strategy}.yaml",
            _TEMPLATE_DIR / f"{strategy.lower()}_shot.yaml",
        ]
        tpl_path = next((p for p in cand if p.exists()), None)
        if tpl_path is None:
            raise FileNotFoundError(
                f"No template YAML for strategy='{strategy}'. "
                f"Tried: {', '.join(str(p) for p in cand)}"
            )

        with tpl_path.open(encoding="utf-8") as f:
            self._order: List[str] = yaml.safe_load(f)

        if not isinstance(self._order, list):
            raise ValueError(
                f"Template {tpl_path} must be a YAML list of placeholder names"
            )

    # ------------------------------------------------------------------ public API
    def build(self) -> str:
        """Return the fully-assembled prompt."""
        # base values from strategy
        values = self._strategy.placeholder_values()

        # TASK is universal – if the strategy didn’t supply, take from JSON
        values.setdefault("TASK", self._ph.get("TASK", ""))

        # assemble in the order requested by the YAML template
        sections: List[str] = []
        for key in self._order:
            content = values.get(key) or self._ph.get(key)
            part = _wrap(key, content)
            if part:
                sections.append(part)

        return "\n\n".join(sections).strip()