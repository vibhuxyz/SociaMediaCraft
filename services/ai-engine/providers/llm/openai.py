import asyncio
from typing import Type, TypeVar, Any
from pydantic import BaseModel
from openai import AsyncOpenAI
from schemas.production_plan import ProductionPlan

T = TypeVar("T", bound=BaseModel)

class OpenAIProvider:
    """
    Object-Oriented wrapper around the AsyncOpenAI client.
    Focuses on Asyncio, Type Hints, and Structured Outputs.
    """
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)

    async def generate_structured_output(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        response_model: Type[T],
        model: str = "gpt-4o-mini"
    ) -> T:
        """
        Uses OpenAI's JSON mode and Function Calling (via Pydantic schemas)
        to guarantee a structured output matching the provided response_model.
        """
        try:
            # For openai v1.3.5, we explicitly inject the JSON Schema into the prompt
            import json
            schema_str = json.dumps(response_model.model_json_schema(), indent=2)
            enhanced_system_prompt = f"{system_prompt}\n\nCRITICAL: You MUST return ONLY a valid JSON object that exactly matches this schema structure. Do NOT wrap it in markdown. Do NOT use your own keys:\n{schema_str}"
            
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": enhanced_system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2, # Lower temperature for more deterministic schema adherence
            )
            
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Received empty response from OpenAI.")
            
            # Validate and parse the JSON string into our strongly-typed Pydantic model
            return response_model.model_validate_json(content)
            
        except Exception as e:
            print(f"Error during LLM generation: {str(e)}")
            raise
