from pathlib import Path
from typing import List, Optional
import json
import typer
from mkdocs_setup.constants import DOCS_FOLDER, DEFAULT_PARADIGM, COMPANY_INFO
from mkdocs_setup.ai import get_api_key, call_llm
from mkdocs_setup.utils import get_python_modules, create_file_with_content, is_project_initialized, get_project_dependencies, get_entry_points
from mkdocs_setup.core import generate_api_doc_files, update_mkdocs_nav

def clean_llm_markdown_output(content: str) -> str:
    """Removes markdown code block wrapping from LLM output if present."""
    content = content.strip()
    # Handle cases like ```markdown ... ``` or just ``` ... ```
    if content.startswith("```markdown"):
        content = content.removeprefix("```markdown")
        if content.endswith("```"):
            content = content.removesuffix("```")
    elif content.startswith("```"):
        content = content.removeprefix("```")
        if content.endswith("```"):
            content = content.removesuffix("```")
    return content.strip()

def generate_ai_docs(
    provider: str,
    openai_key: Optional[str] = None,
    google_key: Optional[str] = None,
    deepseek_key: Optional[str] = None,
    mistral_key: Optional[str] = None,
    docstrings: bool = False,
    readme: bool = False,
    modules: bool = False
):
    """Logic for generating documentation using AI."""
    if not is_project_initialized():
        typer.echo("\n❌ **Oopsy!**: Your documentation project isn't fully set up yet.")
        typer.echo("   Please run the 'New Project' setup first so I know where to put the AI-generated content.")
        return

    # 1. Get API Key
    key = None
    if provider == "openai": key = get_api_key("openai", openai_key)
    elif provider == "google": key = get_api_key("google", google_key)
    elif provider == "deepseek": key = get_api_key("deepseek", deepseek_key)
    elif provider == "mistral": key = get_api_key("mistral", mistral_key)

    if not key:
        typer.secho(f"❌ **Oopsy!**: I couldn't find an API key for '{provider}'.", fg=typer.colors.RED, bold=True)
        typer.echo(f"   Please provide it using --{provider}-key or add it to your .env file.")
        raise typer.Exit(code=1)

    typer.secho(f"🤖 **AI ASSISTANT**: Using {provider.title()} to help write your documentation...", fg=typer.colors.CYAN, bold=True)

    system_prompt = "You are an expert technical writer and Python developer. Your goal is to produce high-quality, clear, and concise documentation. Use Google format for docstrings. DO NOT wrap your markdown output in triple backticks (```markdown ... ```)."

    py_modules = get_python_modules()
    if not py_modules:
        if docstrings or modules:
            typer.secho("⚠️ **WARNING**: No Python modules found to process (excluding __init__.py and script folders).", fg=typer.colors.YELLOW)
        
        # If we only wanted docstrings or modules, and there are none, we might as well stop if no readme is requested.
        if not readme:
            typer.echo("ℹ️ No tasks to perform.")
            return

    if docstrings:
        typer.echo("📝 Adding descriptions to your code...")
        success_count = 0
        for mod_path in py_modules:
            try:
                with open(mod_path, 'r') as f:
                    content = f.read()
                
                user_prompt = f"Analyze the following Python code and add docstrings (Google format) to all classes and methods. Keep existing code unchanged, just add docstrings where missing or improve existing ones. Return ONLY the full code.\n\n```python\n{content}\n```"
                updated_content = call_llm(provider, key, system_prompt, user_prompt)
                
                if "Error calling" in updated_content:
                    typer.secho(f"   ❌ Error for '{mod_path}': {updated_content}", fg=typer.colors.RED)
                    continue

                # Basic cleanup if LLM included markdown blocks (here we expect python code)
                if "```python" in updated_content:
                    updated_content = updated_content.split("```python")[1].split("```")[0].strip()
                elif "```" in updated_content:
                    updated_content = updated_content.split("```")[1].split("```")[0].strip()
                
                with open(mod_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                success_count += 1
                typer.echo(f"   ✅ Processed '{mod_path}'")
            except Exception as e:
                typer.secho(f"   ❌ Failed to process '{mod_path}': {e}", fg=typer.colors.RED)
        
        typer.secho(f"✨ Finished adding descriptions to {success_count}/{len(py_modules)} files.", fg=typer.colors.GREEN)

    if readme:
        typer.echo("📖 Writing a professional project overview for you...")
        try:
            # Gather info from all modules for better context
            context = ""
            for mod_path in py_modules[:5]: # limit context size
                context += f"\nFile {mod_path}:\n{mod_path.read_text()[:1000]}\n"
            
            # Check which documentation folders exist to build the documentation section links
            available_sections = []
            for p in DEFAULT_PARADIGM.keys():
                if (Path(DOCS_FOLDER) / p).exists():
                    available_sections.append(p)
            
            sections_md = ""
            for p in available_sections:
                desc = DEFAULT_PARADIGM.get(p, "")
                sections_md += f"- [{p.title()}]({p}/index.md): {desc}\n"

            user_prompt = f"""
Generate a professional README.md for this project's documentation site. 
The README.md MUST follow this exact structure and order:

1. **Description of the project** (## header): Provide a clear, concise, and professional overview of what this project does based on the provided code context.
2. **Project Documentation** (## header): List exactly these available sections with their hyperlinks and short descriptions:
{sections_md}
3. **Contributing** (## header): Write a brief section on how others can contribute to this project.
4. **Who we are?** (## header): Use the following content exactly:
{COMPANY_INFO}

---
This project documentation was generated using the [https://github.com/nolain-repos/code-docs-generator](code-docs-generator) repo

Context from project modules:
{context}

IMPORTANT: Return the markdown content directly. DO NOT wrap it in markdown code blocks.
"""
            readme_content = call_llm(provider, key, system_prompt, user_prompt)
            
            if "Error calling" in readme_content:
                typer.secho(f"   ❌ AI Error: {readme_content}", fg=typer.colors.RED)
            else:
                readme_content = clean_llm_markdown_output(readme_content)
                overwritten = create_file_with_content(Path(DOCS_FOLDER) / "README.md", readme_content, overwrite=True)
                if overwritten:
                    typer.secho(f"   ✅ Your new homepage at '{DOCS_FOLDER}/README.md' is ready.", fg=typer.colors.GREEN)
                    
                    # Also copy to root and adjust hyperlinks for GitHub compatibility
                    root_readme_content = readme_content
                    for p in available_sections:
                        root_readme_content = root_readme_content.replace(f"({p}/", f"({DOCS_FOLDER}/{p}/")
                    # Also handle API links if they happen to be there
                    root_readme_content = root_readme_content.replace("(api/", f"({DOCS_FOLDER}/api/")
                    
                    create_file_with_content(Path("README.md"), root_readme_content, overwrite=True)
                    typer.secho("   ✅ Also updated project root 'README.md' with adjusted links.", fg=typer.colors.GREEN)
                else:
                    typer.secho(f"   ⚠️ Could not update '{DOCS_FOLDER}/README.md'.", fg=typer.colors.YELLOW)
        except Exception as e:
            typer.secho(f"   ❌ Failed to generate README: {e}", fg=typer.colors.RED)

    if modules:
        typer.echo("📁 Generating structured documentation based on your folders...")
        
        # Gather comprehensive context
        context = "PROJECT CONTEXT:\n"
        for filename in ["README.md", "requirements.txt", "package.json", "setup.py", "pyproject.toml"]:
            p = Path(filename)
            if p.exists():
                try:
                    context += f"\nFile {filename}:\n{p.read_text()[:1500]}\n"
                except: pass
        
        for mod_path in py_modules[:15]:
            try:
                context += f"\nFile {mod_path}:\n{mod_path.read_text()[:1000]}\n"
            except: pass

        # Identify which paradigm folders exist
        available_folders = [f.name for f in Path(DOCS_FOLDER).iterdir() if f.is_dir() and f.name in DEFAULT_PARADIGM]
        
        for folder in available_folders:
            typer.echo(f"  📂 Processing '{folder}'...")
            
            if folder == "quickstart":
                # 1. General Quickstart
                entry_points = get_entry_points()
                prompt = f"{context}\n\n{entry_points}\n\nCreate a general 'index.md' quickstart document for this project. It MUST contain step-by-step details on how to run the project, including entry point scripts and arguments. This is an execution guide ONLY. Do not include any other explanations. If there are explicit entry points provided above, use them. Return ONLY markdown content directly. DO NOT wrap in backticks."
                content = clean_llm_markdown_output(call_llm(provider, key, system_prompt, prompt))
                create_file_with_content(Path(DOCS_FOLDER) / "quickstart" / "index.md", content, overwrite=True)
                
                # 2. Independent Modules Quickstart
                prompt = f"{context}\n\nIdentify if there are modules or components in this project that can be run independently. For each one, provide its name and a brief execution guide. Return as a JSON list of objects with 'name' and 'content' (markdown) keys. If none, return []."
                resp = call_llm(provider, key, system_prompt, prompt)
                try:
                    # JSON cleaning
                    if "```json" in resp: resp = resp.split("```json")[1].split("```")[0].strip()
                    elif "```" in resp: resp = resp.split("```")[1].split("```")[0].strip()
                    mods = json.loads(resp)
                    for m in mods:
                        m_content = clean_llm_markdown_output(m['content'])
                        create_file_with_content(Path(DOCS_FOLDER) / "quickstart" / f"{m['name'].lower().replace(' ', '_')}.md", m_content, overwrite=True)
                except: pass

            elif folder == "setups":
                deps_context = get_project_dependencies()
                prompt = f"{context}\n\n{deps_context}\n\nIdentify all software, libraries, SDKs, tools, or APIs that need setup (e.g., Python, GitHub, Stripe, Docker). Use the provided dependency information as primary context. For each, create a step-by-step setup guide. Return as a JSON list of objects with 'name' (e.g., 'stripe.md') and 'content' (markdown) keys. ONLY setup instructions. Return ONLY JSON."
                resp = call_llm(provider, key, system_prompt, prompt)
                try:
                    if "```json" in resp: resp = resp.split("```json")[1].split("```")[0].strip()
                    elif "```" in resp: resp = resp.split("```")[1].split("```")[0].strip()
                    setups = json.loads(resp)
                    for s in setups:
                        s_content = clean_llm_markdown_output(s['content'])
                        create_file_with_content(Path(DOCS_FOLDER) / "setups" / s['name'], s_content, overwrite=True)
                except: pass

            elif folder == "assumptions":
                prompt = f"{context}\n\nCreate a single 'index.md' document listing all assumptions made in the models, workflows, and expected user interactions of this project. Return ONLY markdown content directly. DO NOT wrap in backticks."
                content = clean_llm_markdown_output(call_llm(provider, key, system_prompt, prompt))
                create_file_with_content(Path(DOCS_FOLDER) / "assumptions" / "index.md", content, overwrite=True)

            elif folder == "alternatives":
                prompt = f"{context}\n\nCreate a single 'index.md' document listing tech stack alternatives to those used in this project. Return ONLY markdown content directly. DO NOT wrap in backticks."
                content = clean_llm_markdown_output(call_llm(provider, key, system_prompt, prompt))
                create_file_with_content(Path(DOCS_FOLDER) / "alternatives" / "index.md", content, overwrite=True)

            elif folder == "functionality":
                # One doc per module
                api_exists = (Path(DOCS_FOLDER) / "api").exists()
                for mod_path in py_modules:
                    prompt = f"Context for {mod_path}:\n{mod_path.read_text()[:2000]}\n\nExplain what this module does. Focus on features, algorithms, inputs, and outputs. DO NOT include code snippets or line-by-line explanations."
                    if api_exists:
                        prompt += " Point to the API documentation in the docs/api folder for technical details."
                    prompt += " Return ONLY markdown content directly. DO NOT wrap in backticks."
                    content = clean_llm_markdown_output(call_llm(provider, key, system_prompt, prompt))
                    create_file_with_content(Path(DOCS_FOLDER) / "functionality" / f"{mod_path.stem}.md", content, overwrite=True)

            elif folder == "architecture":
                prompt = f"{context}\n\nCreate a high-level system overview 'index.md'. Explain how components connect and communicate (system design perspective). You can reference libraries, APIs, methods, and classes, but AVOID code snippets. Return ONLY markdown content directly. DO NOT wrap in backticks."
                content = clean_llm_markdown_output(call_llm(provider, key, system_prompt, prompt))
                create_file_with_content(Path(DOCS_FOLDER) / "architecture" / "index.md", content, overwrite=True)

        typer.secho(f"✨ Structured documentation complete!", fg=typer.colors.GREEN)

    # Update nav after AI generation
    typer.echo("🔄 Refreshing navigation structure...")
    update_mkdocs_nav(generate_api_doc_files(py_modules))

    typer.secho("\n🎉 **All Done!** Your AI Assistant has finished its work!", fg=typer.colors.GREEN, bold=True)
