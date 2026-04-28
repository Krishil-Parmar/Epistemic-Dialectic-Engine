import json
import re
from typing import Type, TypeVar

from google import genai
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


def _clean_schema(schema: dict) -> dict:
    defs = schema.pop("$defs", {})

    def _resolve(node: dict) -> dict:
        if "$ref" in node:
            ref_name = node["$ref"].split("/")[-1]
            node = defs[ref_name].copy()
            return _resolve(node)

        node.pop("additionalProperties", None)
        node.pop("default", None)
        node.pop("title", None)

        if "properties" in node:
            node["required"] = list(node["properties"].keys())
            for key, val in node["properties"].items():
                if isinstance(val, dict):
                    node["properties"][key] = _resolve(val)

        if "items" in node and isinstance(node["items"], dict):
            node["items"] = _resolve(node["items"])

        if "allOf" in node:
            merged = {}
            for item in node["allOf"]:
                merged.update(_resolve(item))
            node.pop("allOf")
            node.update(merged)

        if "anyOf" in node:
            resolved = node["anyOf"][0]
            if isinstance(resolved, dict):
                resolved = _resolve(resolved)
            node.pop("anyOf")
            node.update(resolved)

        return node

    return _resolve(schema)


class GeminiClient:
    def __init__(self, model: str = "gemini-3.1-pro-preview"):
        self._client = None
        self.model = model

    @property
    def client(self):
        if self._client is None:
            self._client = genai.Client()
        return self._client

    def _build_config(
        self, system_prompt: str, schema: Type[T], temperature: float, max_tokens: int
    ) -> genai.types.GenerateContentConfig:
        clean = _clean_schema(schema.model_json_schema())
        return genai.types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=temperature,
            max_output_tokens=max_tokens,
            response_mime_type="application/json",
            response_schema=clean,
        )

    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: Type[T],
        temperature: float = 0.0,
        max_tokens: int = 1024,
        max_retries: int = 3,
    ) -> T:
        config = self._build_config(system_prompt, schema, temperature, max_tokens)
        last_error = None

        for attempt in range(max_retries):
            prompt = user_prompt
            if last_error:
                prompt = (
                    f"{user_prompt}\n\n"
                    f"[Previous attempt failed: {last_error}. "
                    f"Return valid JSON matching the schema exactly.]"
                )

            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config,
            )

            text = response.text or ""
            try:
                parsed = json.loads(self._extract_json(text))
                return schema.model_validate(parsed)
            except (json.JSONDecodeError, ValidationError) as e:
                last_error = str(e)

        raise ValueError(
            f"Failed to get valid JSON from Gemini after {max_retries} attempts. "
            f"Last error: {last_error}"
        )

    @staticmethod
    def _extract_json(text: str) -> str:
        stripped = text.strip()
        if stripped.startswith("```"):
            lines = stripped.split("\n", 1)
            body = lines[1] if len(lines) > 1 else ""
            if body.endswith("```"):
                body = body[:-3]
            stripped = body.strip()
        stripped = re.sub(r",\s*([}\]])", r"\1", stripped)
        return stripped
