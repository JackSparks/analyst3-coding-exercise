"""Helper utilities for LLM calls and other common operations."""

import os
from openai import OpenAI
from pydantic import BaseModel
from typing import Optional, Type
from dotenv import load_dotenv

load_dotenv()


def call_llm(
    prompt: str,
    model: str = "gpt-4o",
    system_message: Optional[str] = None,
    response_schema: Optional[Type[BaseModel]] = None,
    temperature: float = 0,
    api_key: Optional[str] = None,
):
    """
    Call OpenAI LLM with a prompt and return the response.

    Args:
        prompt: The user prompt to send to the LLM
        model: OpenAI model to use (default: gpt-4o)
        system_message: Optional system message to set context
        response_schema: Optional Pydantic model for structured output
        temperature: Temperature for response randomness (0-2, default: 0)
        max_tokens: Maximum tokens in response (default: 16384)
        api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)

    Returns:
        If response_schema is provided: Pydantic model instance
        Otherwise: String response from the LLM

    Example usage:
        # Simple text response
        response = call_llm("What is the capital of France?")

        # With structured output
        class CompanyInfo(BaseModel):
            name: str
            industry: str

        result = call_llm(
            prompt="Extract company info from: ...",
            response_schema=CompanyInfo
        )
    """
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

    # Build messages
    messages = []
    if system_message:
        messages.append({"role": "system", "content": system_message})
    messages.append({"role": "user", "content": prompt})

    # Make API call with or without structured output
    if response_schema:
        # Use structured output with Pydantic schema
        response = client.responses.parse(
            model=model,
            input=messages,
            text_format=response_schema,
            temperature=temperature,
        )
        return response.output_parsed
    else:
        # Standard completion
        response = client.chat.completions.create(model=model, messages=messages, temperature=temperature)
        return response.choices[0].message.content


if __name__ == "__main__":
    print("Testing call_llm function with simple text response...")
    response = call_llm(
        prompt="What is the capital of France?",
        system_message="You are a helpful assistant",
        response_schema=None,
    )
    print("Response:", response)

    print("Testing call_llm function with structured output...")

    class CitySchema(BaseModel):
        name: str
        country: str

    response = call_llm(
        prompt="What is the capital of France?",
        system_message="You are a helpful assistant",
        response_schema=CitySchema,
    )
    print("Response:", response)
