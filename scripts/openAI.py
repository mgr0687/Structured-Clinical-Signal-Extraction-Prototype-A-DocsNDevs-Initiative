"""
Example script demonstrating OpenAI API usage.

This script shows how to use the OpenAI API to generate text completions.
Make sure to set your OPENAI_API_KEY environment variable or create a .env file.

Usage:
    python scripts/openai_example.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to the path so we can import from src
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# Load environment variables from .env file
load_dotenv(project_root / ".env")

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai package not installed.")
    print("Install it with: pip install openai")
    sys.exit(1)


def main():
    """Main function to demonstrate OpenAI API usage."""
    
    # Get API key from environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        print("Please set it in your .env file or as an environment variable.")
        print("\nExample .env file content:")
        print("OPENAI_API_KEY=sk-your-api-key-here")
        sys.exit(1)
    
    # Initialize the OpenAI client
    client = OpenAI(api_key=api_key)
    
    print("OpenAI API Client initialized successfully!")
    print("-" * 50)
    
    # Example 1: Simple text completion
    print("\nExample 1: Simple text completion")
    print("-" * 50)
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello and tell me a fun fact about Python programming."}
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        print(f"Response: {response.choices[0].message.content}")
        print(f"Model: {response.model}")
        print(f"Usage: {response.usage.total_tokens} tokens")
        
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return
    
    # Example 2: JSON-structured output (useful for this project)
    print("\n\nExample 2: JSON-structured output")
    print("-" * 50)
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that returns JSON responses."},
                {"role": "user", "content": """Extract information from this text and return it as JSON:
                
Text: "The patient reported feeling depressed for the past two weeks. They mentioned having thoughts of self-harm but have no specific plan."
                
Return a JSON object with keys: 'mood', 'duration', 'thoughts', 'plan'."""}
            ],
            response_format={"type": "json_object"},
            max_tokens=200,
            temperature=0.3
        )
        
        print(f"Response: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return
    
    # Example 3: Using with the project's LLM client pattern
    print("\n\nExample 3: OpenAI client compatible with project's LLMClient protocol")
    print("-" * 50)
    
    class OpenAILLMClient:
        """OpenAI implementation of the LLMClient protocol."""
        
        def __init__(self, model: str = "gpt-3.5-turbo", api_key: str = None):
            self.model = model
            self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        
        def generate_json(self, prompt: str) -> dict:
            """Return a JSON-like dict. Must be valid JSON structure (no markdown)."""
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that returns valid JSON only, no markdown formatting."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.3
                )
                
                import json
                return json.loads(response.choices[0].message.content)
                
            except Exception as e:
                print(f"Error generating JSON: {e}")
                raise
    
    # Test the OpenAILLMClient
    openai_client = OpenAILLMClient()
    
    test_prompt = """Extract clinical signals from this text and return as JSON:
    
<<<TEXT>>>
The patient expressed feeling hopeless and mentioned thinking about ending their life. They have been experiencing these thoughts for the past month but have no specific plan.
<<<END_TEXT>>>

Return a JSON object with: suicidal_ideation (presence: present/absent/indeterminate), temporal (current/recent/past/future/unknown), and evidence (array of text spans)."""
    
    try:
        result = openai_client.generate_json(test_prompt)
        print("Generated JSON:")
        import json
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 50)
    print("Script completed successfully!")


if __name__ == "__main__":
    main()

