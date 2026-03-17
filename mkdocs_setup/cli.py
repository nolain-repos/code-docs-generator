import sys
from pathlib import Path
from typing import List, Optional
import typer
from typing_extensions import Annotated
from dotenv import load_dotenv

from mkdocs_setup.constants import DOCS_FOLDER, MKDOCS_CONFIG_FILE, DEFAULT_PARADIGM
from mkdocs_setup.ai import get_api_key, save_api_key
from mkdocs_setup.utils import get_python_modules, is_project_initialized
from mkdocs_setup.core import init_project, generate_api_doc_files, update_mkdocs_nav, add_existing_docs
from mkdocs_setup.ai_logic import generate_ai_docs
from mkdocs_setup.wizard import run_wizard

# Load environment variables from .env file
load_dotenv()

# Initialize the Typer app
app = typer.Typer(
    name="mkdocs-setup",
    help="A friendly tool to create and manage professional documentation for your Python projects."
)

@app.command()
def create(
    project_name: Annotated[str, typer.Argument(
        help="The name of your project (e.g., MyAwesomeProject)."
    )],
    overwrite_config: Annotated[bool, typer.Option(
        "--overwrite-config", "-o", 
        help="Start fresh by overwriting your existing configuration file."
    )] = False,
    include_paradigms: Annotated[Optional[List[str]], typer.Option(
        "--include-paradigms", "-p",
        help="List of default paradigm folders to include (quickstart, setups, etc.)."
    )] = None,
    extra_paradigms: Annotated[Optional[List[str]], typer.Option(
        "--extra-paradigms", "-e",
        help="List of additional custom paradigm folders to create."
    )] = None,
    openai_key: Annotated[Optional[str], typer.Option("--openai-key", help="OpenAI API Key")] = None,
    google_key: Annotated[Optional[str], typer.Option("--google-key", help="Google API Key")] = None,
    deepseek_key: Annotated[Optional[str], typer.Option("--deepseek-key", help="DeepSeek API Key")] = None,
    mistral_key: Annotated[Optional[str], typer.Option("--mistral-key", help="Mistral API Key")] = None
):
    """
    Sets up everything you need for your documentation: folders, files, and initial settings.
    """
    typer.echo(f"✨ **Welcome!** Building your documentation project for '{project_name}'...")
    
    # Save API keys to .env if provided
    keys_to_save = {
        "openai": openai_key,
        "google": google_key,
        "deepseek": deepseek_key,
        "mistral": mistral_key
    }
    
    saved_any = False
    for provider, key in keys_to_save.items():
        if key:
            save_api_key(provider, key)
            saved_any = True
    
    if saved_any:
        typer.echo(f"   - Your AI Assistant keys have been saved securely.")

    # Check and display AI Assistant Status
    typer.echo("\n🤖 **AI ASSISTANT STATUS**:")
    for provider in ["openai", "google", "deepseek", "mistral"]:
        status = "✅ Ready" if get_api_key(provider) else "❌ Not connected (AI features will be unavailable)"
        typer.echo(f"   - {provider.title()}: {status}")
    typer.echo("")

    init_project(
        project_name=project_name,
        include_paradigms=include_paradigms,
        extra_paradigms=extra_paradigms,
        overwrite_config=overwrite_config
    )

@app.command()
def update():
    """
    Scans for Python files, generates Markdown stubs, and updates the mkdocs.yml 'nav' section.
    """
    if not Path(DOCS_FOLDER).exists():
        typer.echo("\n❌ **Oopsy!**: I couldn't find your 'docs' folder.")
        typer.echo("   Please run the 'New Project' setup first to create your documentation structure.")
        return

    modules = get_python_modules()
    
    if not modules:
        typer.echo("\n⚠️ **WARNING**: No Python modules found (excluding __init__.py). Nothing to document.")
        return

    # 1. Generate the Markdown files and get the list of navigation entries
    api_nav_entries = generate_api_doc_files(modules)
    
    # 2. Update the mkdocs.yml navigation
    update_mkdocs_nav(api_nav_entries)

    typer.echo("\n✨ **All Done!** Your technical reference and menu have been updated.")
    typer.echo("   Run `mkdocs serve` to see the changes!")

@app.command()
def addAlreadyCreated(
    docs_dir: Annotated[str, typer.Option(
        "--docs-dir", "-d",
        help="Path to the directory containing .md files (relative to project root)."
    )] = DOCS_FOLDER
):
    """
    Scans for existing .md files in the specified directory and populates the 'nav' section of mkdocs.yml.
    """
    typer.echo(f"🔍 **SCANNING**: Looking for .md files in '{docs_dir}'...")
    add_existing_docs(docs_dir)
    typer.echo("\n✨ **All Done!** Your navigation is now updated.")
    typer.echo("   Run `mkdocs serve` to see the changes!")

@app.command()
def aiDocs(
    provider: Annotated[str, typer.Option("--provider", help="AI Provider (openai, google, deepseek, mistral)")] = "openai",
    openai_key: Annotated[Optional[str], typer.Option("--openai-key")] = None,
    google_key: Annotated[Optional[str], typer.Option("--google-key")] = None,
    deepseek_key: Annotated[Optional[str], typer.Option("--deepseek-key")] = None,
    mistral_key: Annotated[Optional[str], typer.Option("--mistral-key")] = None,
    docstrings: Annotated[bool, typer.Option("--docstrings", help="Generate/Update docstrings for methods")] = False,
    readme: Annotated[bool, typer.Option("--readme", help="Generate a comprehensive README.md")] = False,
    modules: Annotated[bool, typer.Option("--modules", help="Generate structured .md files for all active paradigm folders")] = False
):
    """
    Uses an LLM to generate documentation (docstrings, README, or module docs).
    """
    generate_ai_docs(
        provider=provider,
        openai_key=openai_key,
        google_key=google_key,
        deepseek_key=deepseek_key,
        mistral_key=mistral_key,
        docstrings=docstrings,
        readme=readme,
        modules=modules
    )


def main():
    # If no arguments are provided, run the interactive wizard
    if len(sys.argv) == 1:
        try:
            run_wizard()
        except (typer.Exit, typer.Abort):
            pass
        except Exception as e:
            # Handle click Exit exception if it bubbles up
            if "Exit" in str(type(e)):
                pass
            else:
                raise e
    else:
        app()

if __name__ == "__main__":
    main()
