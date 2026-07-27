from typing import Type, TypeVar, Any
from pydantic import BaseModel
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
import litellm
import os
from tools.brand_knowledge import fetch_brand_guidelines
    
T = TypeVar("T", bound=BaseModel)



class UniversalLLMProvider:
    def __init__(self, openai_key: str = "", anthropic_key: str = "", openrouter_key: str = "", custom_key: str = "", custom_base: str = ""):
        if openai_key:
            os.environ["OPENAI_API_KEY"] = openai_key
        if anthropic_key:
            os.environ["ANTHROPIC_API_KEY"] = anthropic_key
        if openrouter_key:
            os.environ["OPENROUTER_API_KEY"] = openrouter_key

        self.custom_key = custom_key
        self.custom_base = custom_base

        self._openai_client = AsyncOpenAI(api_key=openai_key) if openai_key else None
        self._anthropic_client = AsyncAnthropic(api_key=anthropic_key) if anthropic_key else None

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
        response_model: Type[T],
        timeout: float | None = None,
    ) -> T:
        import time
        from dependencies import planning_metrics
        
        start_time = time.time()
        
        kwargs = {}
        if self.custom_base:
            kwargs["api_base"] = self.custom_base
        if self.custom_key:
            kwargs["api_key"] = self.custom_key
        
        response = await litellm.acompletion(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format=response_model,
            timeout=timeout,
            **kwargs
        )
        
        duration = time.time() - start_time
        try:
            cost = litellm.completion_cost(completion_response=response) or 0.0
        except Exception:
            cost = 0.0
        
        planning_metrics["total_time_sec"] += duration
        planning_metrics["total_cost_usd"] += cost
        planning_metrics["api_calls"] += 1

        raw_json = response.choices[0].message.content
        return response_model.model_validate_json(raw_json)

    async def run_with_tools(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        response_model: Type[T],
        tools: list[dict] | None = None,
        tool_functions: dict | None = None,
    ) -> T:
        import json
        tools = tools or []
        tool_functions = tool_functions or {}
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
        
        kwargs = {}
        if self.custom_base:
            kwargs["api_base"] = self.custom_base
        if self.custom_key:
            kwargs["api_key"] = self.custom_key
        
        # 1. Ask the LLM
        response = await litellm.acompletion(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            **kwargs
        )
        msg = response.choices[0].message
        
        # 2. Did the LLM ask for a tool?
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            messages.append(msg) # Save the request to history
            
            for tool_call in msg.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)
                
                # Execute the actual Python function
                if func_name in tool_functions:
                    print(f"\n⚙️ [TOOL] LLM is running: {func_name}({func_args})")
                    result = tool_functions[func_name](**func_args)
                else:
                    result = f"Error: Tool {func_name} not found."
                
                # Hand the result back to the LLM
                messages.append({
                    "role": "tool",
                    "name": func_name,
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                })
                
        # 3. Call the LLM one last time to get our Pydantic object
        final_response = await litellm.acompletion(
            model=model,
            messages=messages,
            response_format=response_model, # type: ignore
            **kwargs
        )
        
        content = final_response.choices[0].message.content
        if not content:
            raise ValueError("Empty response")
        return response_model.model_validate_json(content)
