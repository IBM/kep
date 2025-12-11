"""
Watsonx client – concrete implementation of `LLMClient`.
"""

from __future__ import annotations
from typing import Any, Dict
from ibm_watsonx_ai.foundation_models import ModelInference          # type: ignore
import os

from llm.base     import LLMClient
from llm.factory  import register_provider


@register_provider("watsonx")
class WatsonxClient(LLMClient):
    """Adapter around `ibm_watsonx_ai.foundation_models.ModelInference`."""

    # ------------------------------------------------------------------ init
    def __init__(self, *, config: Dict[str, Any], debug: bool = False):
        super().__init__(config=config, debug=debug)

        # 1) credentials - prioritize environment variables over config file
        url     = os.getenv("WATSONX_URL")     or config.get("url")
        apikey  = os.getenv("WATSONX_APIKEY")  or config.get("apikey")
        project_id = os.getenv("WATSONX_PROJECT_ID") or config.get("project_id")

        if not url or not apikey:
            raise ValueError(
                "Watsonx credentials missing.\n"
                "Set environment variables WATSONX_URL and WATSONX_APIKEY, "
                "or configure them in llm/watsonx/config.yaml"
            )

        self._params  = config.get("hyperparameters", {})
        self._project = project_id
        model_name = config["model_id"]
        # 2) create SDK object ----------------------------------------------
        self._model = ModelInference(
            params=self._params,
            model_id=config.get("model_id"),
            credentials={"url": url, "apikey": apikey},
            project_id=self._project,
        )
        self._dbg(f"WatsonxClient ready – model={model_name}")

    # ------------------------------------------------------------------ API
    def inference(self, prompt: str) -> Dict[str, Any]:
        if not isinstance(prompt, str):
            raise TypeError("Watsonx expects a single prompt string")

        self._dbg("Prompt:", (prompt[:120] + " …") if len(prompt) > 120 else prompt)
        if self._cfg.get("api_access") == "chat":
            res = self._model.chat([
                {"role": "system", "content": prompt}
                ])
            return {"generated_text": res["choices"][0]["message"]["content"]} # Chat interface
        res = self._model.generate(prompt)
        return {"generated_text": res["results"][0]["generated_text"]}   # type: ignore
