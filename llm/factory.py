"""
factory.py – implements Dependency-Inversion:
high-level code depends on `LLMClient`, never concrete classes.
"""

from __future__ import annotations
from typing import Dict, Type, Any
from pathlib import Path
from .base      import LLMClient
from .config    import load_client_cfg


class _Registry:
    _cls: Dict[str, Type[LLMClient]] = {}

    @classmethod
    def add(cls, name: str, client_cls: Type[LLMClient]):
        cls._cls[name.lower()] = client_cls

    @classmethod
    def get(cls, name: str) -> Type[LLMClient]:
        if name.lower() not in cls._cls:
            raise ValueError(f"Unknown provider '{name}'. "
                             f"Registered: {list(cls._cls)}")
        return cls._cls[name.lower()]


class LLMFactory:
    """
    Central entry-point: returns a ready client instance.
    """

    @staticmethod
    def create(
        *, provider: str,
        cfg: dict[str, Any],
        debug: bool = False
    ) -> LLMClient:
        """
        Parameters
        ----------
        provider     – e.g. "watsonx" | "rits"
        cfg   – config dict
        """
        from importlib import import_module
        provider = provider.lower()

        # --- dynamic import registers the concrete class via side-effect
        import_module(f"llm.{provider}.client")

        cls = _Registry.get(provider)
        return cls(config=cfg, debug=debug)


# helper decorator ----------------------------------------------------------
def register_provider(name: str):
    """
    Decorator used by concrete client modules
    to register themselves in the factory.
    """
    def _decorator(cls: Type[LLMClient]):
        _Registry.add(name, cls)
        return cls
    return _decorator