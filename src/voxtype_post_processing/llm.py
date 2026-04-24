from __future__ import annotations

from dataclasses import dataclass
import json
import os
import urllib.request


@dataclass(frozen=True)
class OpenAICompatibleConfig:
    base_url: str = "http://localhost:8000/v1"
    model: str = "local-model"
    timeout_seconds: float = 15.0
    max_tokens: int = 2048
    disable_thinking: bool = True

    @classmethod
    def from_env(cls) -> "OpenAICompatibleConfig":
        return cls(
            base_url=os.getenv("VOXTYPE_LLM_BASE_URL", cls.base_url).rstrip("/"),
            model=os.getenv("VOXTYPE_LLM_MODEL", cls.model),
            timeout_seconds=float(os.getenv("VOXTYPE_LLM_TIMEOUT", str(cls.timeout_seconds))),
            max_tokens=int(os.getenv("VOXTYPE_LLM_MAX_TOKENS", str(cls.max_tokens))),
            disable_thinking=os.getenv("VOXTYPE_LLM_DISABLE_THINKING", "true").lower()
            not in {"0", "false", "no", "off"},
        )


class OpenAICompatibleClient:
    def __init__(self, config: OpenAICompatibleConfig):
        self.config = config

    def complete(self, messages: list[dict[str, str]], *, max_tokens: int | None = None) -> str:
        payload: dict[str, object] = {
            "model": self.config.model,
            "messages": messages,
            "temperature": 0,
            "max_tokens": max_tokens if max_tokens is not None else self.config.max_tokens,
        }
        if self.config.disable_thinking:
            payload["chat_template_kwargs"] = {"enable_thinking": False}

        req = urllib.request.Request(
            f"{self.config.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=self.config.timeout_seconds) as response:
            data = json.load(response)

        return data["choices"][0]["message"].get("content") or ""
