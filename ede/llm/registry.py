from pathlib import Path

import yaml

from .claude_client import ClaudeClient
from .gemini_client import GeminiClient

CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "providers.yaml"


def get_client(layer_name: str) -> ClaudeClient | GeminiClient:
    config = yaml.safe_load(CONFIG_PATH.read_text())
    layer_config = config[layer_name]
    provider = layer_config["provider"]

    if provider == "anthropic":
        return ClaudeClient(model=layer_config["model"])
    elif provider == "google":
        return GeminiClient(model=layer_config["model"])
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def get_layer_config(layer_name: str) -> dict:
    config = yaml.safe_load(CONFIG_PATH.read_text())
    return config[layer_name]
