"""
RITS (DeepSeek etc.) client – chat style HTTP API.
"""

from __future__ import annotations
from typing import Any, Dict, List
import requests
import os

from llm.base    import LLMClient
from llm.factory import register_provider


@register_provider("rits")
class RitsClient(LLMClient):
    """Adapter for RITS chat-completion endpoint."""

    def __init__(self, *, config: Dict[str, Any], debug: bool = False):
        super().__init__(config=config, debug=debug)
        
        # Prioritize environment variables over config file
        self._url = os.getenv("RITS_API_URL") or config.get("api_url")
        self._key = os.getenv("RITS_API_KEY") or config.get("rits_api_key")
        
        if not self._url or not self._key:
            raise ValueError(
                "RITS credentials missing.\n"
                "Set environment variables RITS_API_URL and RITS_API_KEY, "
                "or configure them in llm/rits/config.yaml"
            )
        
        self._defaults = config.get("request_defaults", {})
        self._dbg("RitsClient initialised – endpoint:", self._url)

    # ------------------------------------------------------------------
    def inference(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        if not isinstance(messages, list):
            raise TypeError("RITS expects a list[dict] of messages (chat format)")

        headers = {
            "accept": "application/json",
            "RITS_API_KEY": self._key,
            "Content-Type": "application/json",
        }
        body = {**self._defaults, "messages": messages}

        self._dbg("POST", self._url)
        response = requests.post(self._url, headers=headers, json=body, timeout=60)
        response.raise_for_status()
        data = response.json()

        # Unify output – put the assistant text under 'generated_text'
        content = (
            data["choices"][0]["message"]["content"]
            if "choices" in data
            else data.get("content", "")
        )
        return {"generated_text": content, "raw": data}