from typing import TypeVar, Any
from pydantic import BaseModel
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
import litellm
import os

T = TypeVar("T", bound=BaseModel)


class UniversalLLMProvider:
    def __init__(self, openai_key: str, anthropic_key: str):
        os.environ["OPENAI_API_KEY"] = openai_key
        os.environ["ANTHROPIC_API_KEY"] = anthropic_key

        self._openai_client = AsyncOpenAI(api_key=openai_key)
        self._anthropic_client = AsyncAnthropic(api_key=anthropic_key)

    def get_native_client(self, provider: str) -> Any:
        if provider == "openai":
            return self._openai_client
        elif provider == "anthropic":
            return self._anthropic_client
        else:
            raise ValueError(f"No native client available for {provider}")

    async def generate_structured_output(
        self, 
        model: str, 
        system_prompt: str, 
        user_prompt: str, 
        response_model: type[T]
    ) -> T:
        """
        Uses LiteLLM to route to ANY model and return a validated Pydantic object.
        """
        # We cast response to Any because litellm's generic return types confuse the IDE
        response: Any = await litellm.acompletion(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format=response_model # type: ignore
        )
        
        raw_json_string = response.choices[0].message.content
        if not raw_json_string:
            raise ValueError("The model returned an empty response.")
            
        return response_model.model_validate_json(raw_json_string)
