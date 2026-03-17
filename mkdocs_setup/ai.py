import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

def get_api_key(provider: str, cli_key: Optional[str] = None) -> Optional[str]:
    """Retrieves API key from CLI or environment variable."""
    if cli_key:
        return cli_key
    env_vars = {
        "openai": "OPENAI_API_KEY",
        "google": "GOOGLE_API_KEY",
        "deepseek": "DEEPSEEK_API_KEY",
        "mistral": "MISTRAL_API_KEY"
    }
    return os.getenv(env_vars.get(provider.lower(), ""))

def save_api_key(provider: str, key: str):
    """Saves the API key to the .env file and reloads environment variables."""
    env_vars = {
        "openai": "OPENAI_API_KEY",
        "google": "GOOGLE_API_KEY",
        "deepseek": "DEEPSEEK_API_KEY",
        "mistral": "MISTRAL_API_KEY"
    }
    env_key = env_vars.get(provider.lower())
    if not env_key:
        return

    env_path = Path(".env")
    existing_content = ""
    if env_path.exists():
        existing_content = env_path.read_text()
    
    if f"{env_key}=" in existing_content:
        # Update existing key (simple replacement logic)
        lines = existing_content.splitlines()
        new_lines = []
        for line in lines:
            if line.startswith(f"{env_key}="):
                new_lines.append(f"{env_key}={key}")
            else:
                new_lines.append(line)
        env_path.write_text("\n".join(new_lines) + "\n")
    else:
        # Append new key
        with open(env_path, "a") as f:
            if existing_content and not existing_content.endswith("\n"):
                f.write("\n")
            f.write(f"{env_key}={key}\n")
    
    # Update current environment
    os.environ[env_key] = key
    load_dotenv()

def call_llm(provider: str, api_key: str, system_prompt: str, user_prompt: str) -> str:
    """Generic LLM call wrapper."""
    try:
        if provider == "openai" or provider == "deepseek":
            from openai import OpenAI
            base_url = "https://api.deepseek.com" if provider == "deepseek" else None
            client = OpenAI(api_key=api_key, base_url=base_url)
            model = "deepseek-chat" if provider == "deepseek" else "gpt-4o"
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            return response.choices[0].message.content
        elif provider == "google":
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-pro')
            response = model.generate_content(f"{system_prompt}\n\n{user_prompt}")
            
            if response.candidates:
                return response.text
            else:
                return f"Error calling {provider}: No response candidates returned (possibly blocked by safety filters)."
        elif provider == "mistral":
            from mistralai.client import Mistral
            client = Mistral(api_key=api_key)
            response = client.chat.complete(
                model="mistral-large-latest",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            return response.choices[0].message.content
    except Exception as e:
        return f"Error calling {provider}: {e}"
    return "Unsupported provider"
