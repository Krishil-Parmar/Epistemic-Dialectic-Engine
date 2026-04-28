import json
from typing import Type, TypeVar

import anthropic
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


class ClaudeClient:
    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        self.client = anthropic.AsyncAnthropic()
        self.model = model

    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: Type[T],
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> T:
        tool_name = schema.__name__
        tool_schema = schema.model_json_schema()

        messages = [{"role": "user", "content": user_prompt}]

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=messages,
            tools=[
                {
                    "name": tool_name,
                    "description": f"Output structured data as {tool_name}",
                    "input_schema": tool_schema,
                }
            ],
            tool_choice={"type": "tool", "name": tool_name},
        )

        for block in response.content:
            if block.type == "tool_use":
                try:
                    return schema.model_validate(block.input)
                except ValidationError as e:
                    return await self._retry_with_error(
                        system_prompt, user_prompt, schema,
                        temperature, max_tokens, str(e),
                    )

        raise RuntimeError(f"No tool_use block in response: {response.content}")

    async def _retry_with_error(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: Type[T],
        temperature: float,
        max_tokens: int,
        error: str,
    ) -> T:
        retry_prompt = (
            f"{user_prompt}\n\n"
            f"[Previous attempt failed validation: {error}. Fix the output.]"
        )

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": retry_prompt}],
            tools=[
                {
                    "name": schema.__name__,
                    "description": f"Output structured data as {schema.__name__}",
                    "input_schema": schema.model_json_schema(),
                }
            ],
            tool_choice={"type": "tool", "name": schema.__name__},
        )

        for block in response.content:
            if block.type == "tool_use":
                return schema.model_validate(block.input)

        raise RuntimeError("Retry also failed to produce tool_use block")
