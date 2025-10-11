import os
import glob
from pathlib import Path
import typer
from typing_extensions import Annotated
from typing import List, Dict, Union 
import yaml

# Initialize the Typer app
app = typer.Typer(
    name="mkdoc-setup",
    help="A CLI tool to set up Material for MkDocs documentation for Python projects."
)

# --- Configuration ---
DOCS_FOLDER = "docs"
MKDOCS_CONFIG_FILE = "mkdocs.yml"

# --- Custom File Contents ---

# Content for extra.css
EXTRA_CSS_CONTENT = """
/* Center Markdown Tables (requires md_in_html extension) */
.center-table {
    text-align: center;
}

.md-typeset .center-table :is(td, th):not([align]) {
    /* Reset alignment for table cells */
    text-align: initial;
}
"""

# Content for katex.js (remains unchanged)
KATEX_JS_CONTENT = """
document$.subscribe(({ body }) => {
    renderMathInElement(body, {
        delimiters: [
            { left: "$$", right: "$$", display: true },
            { left: "$", right: "$", display: false },
            { left: "\\(", right: "\\)", display: false },
            { left: "\\[", right: "\\]", display: true },
        ],
    });
});
"""

# Content for README.md
README_MD_CONTENT = """
# Project Documentation

Welcome to the documentation for this project.

## Development Setup

1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`

## Running Documentation

The documentation is built using Material for MkDocs.

1. Install MkDocs and required plugins:
   `pip install mkdocs mkdocs-material mkdocstrings[python] mkdocs-jupyter glightbox`
2. Run the local server: `mkdocs serve`
"""

# Template for mkdocs.yml (Updated with all user requirements and using placeholder)
MKDOCS_YML_TEMPLATE = """
site_name: {site_name_placeholder}
theme:
  icon:
    admonition:
      example: simple/libreofficemath
  name: material
  features:
    - navigation.tabs
    - navigation.sections
    - navigation.expand
    - navigation.path
    - content.footnote.tooltips
    - content.code.copy
    - content.code.select
    - content.code.annotate
  language: en
  palette:
    # Palette toggle for light mode
    - scheme: default
      primary: indigo
      toggle:
        icon: material/lightbulb
        name: Switch to dark mode

    # Palette toggle for dark mode
    - scheme: slate
      primary: lime
      toggle:
        icon: material/lightbulb-outline
        name: Switch to light mode

markdown_extensions:
  - def_list
  - footnotes
  - pymdownx.critic
  - pymdownx.caret
  - pymdownx.keys
  - pymdownx.mark
  - pymdownx.tilde
  - pymdownx.highlight:
      anchor_linenums: true
      line_spans: __span
      pygments_lang_class: true
  - pymdownx.inlinehilite
  - pymdownx.snippets
  - pymdownx.superfences
  - admonition
  - pymdownx.details
  - pymdownx.superfences
  - attr_list
  - pymdownx.emoji
  - pymdownx.tasklist:
      custom_checkbox: true
  - md_in_html
  - pymdownx.arithmatex:
      generic: true
extra:
  annotate:
    json: [.s2]
plugins:
  - search
  - mkdocstrings
  - glightbox
  - mkdocs-jupyter
extra_css:
  - stylesheets/extra.css
  - https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.7/katex.min.css
extra_javascript:
  - javascripts/katex.js
  - https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.7/katex.min.js
  - https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.7/contrib/auto-render.min.js

nav:
  - Home: README.md
"""

def ignore_python_tags(loader, node):
    """Custom constructor that ignores the !!python/name tag."""
    # Simply return the string content of the node, which is the full Python path
    return loader.construct_scalar(node)

# Add the custom constructor to the SafeLoader BEFORE any YAML loading operation
try:
    # Check if the constructor is already added to prevent re-adding errors
    if 'tag:yaml.org,2002:python/name' not in yaml.SafeLoader.yaml_constructors:
        yaml.SafeLoader.add_constructor('tag:yaml.org,2002:python/name', ignore_python_tags)
except AttributeError:
    # Fallback or error handling if SafeLoader structure is different (unlikely)
    print("Warning: Could not configure custom YAML loader.")

# --- Helper Function for File Creation ---
def create_file_with_content(file_path: Path, content: str):
    """Creates a file if it doesn't exist, or overwrites it if content is different."""
    if not file_path.exists():
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w") as f:
            f.write(content.strip())
        return True
    return False

# --- Typer Commands ---

@app.command()
def create(
    project_name: Annotated[str, typer.Argument(
        help="The name of the project (e.g., MyAwesomeLib). Used for site_name in mkdocs.yml."
    )],
    overwrite_config: Annotated[bool, typer.Option(
        "--overwrite-config", "-o", 
        help="Overwrite the existing mkdocs.yml file if it exists."
    )] = False
):
    """
    Creates the initial 'docs' folder, 'mkdocs.yml', README.md, and required sub-folders/files.
    """
    typer.echo(f"✅ **CREATING**: Initial project structure for '{project_name}'...")
    
    # 0. Create README.md at docs
    readme_path = Path(f"{DOCS_FOLDER}/README.md")
    if create_file_with_content(readme_path, README_MD_CONTENT):
        typer.echo(f"   - File 'README.md' created at docs and populated.")
    else:
        typer.echo(f"   - File 'README.md' already exists. Skipping.")

    # 1. Create 'docs' folder
    docs_path = Path(DOCS_FOLDER)
    docs_path.mkdir(exist_ok=True)
    typer.echo(f"   - Directory '{DOCS_FOLDER}/' ensured.")

    # 2. Create sub-folders and files
    typer.echo("   - Creating custom folders and files:")
    
    # Folders to create under 'docs'
    sub_folders = ["assets", "stylesheets", "javascripts"]
    for folder in sub_folders:
        Path(docs_path / folder).mkdir(exist_ok=True)
        typer.echo(f"     -> Folder '{DOCS_FOLDER}/{folder}/' ensured.")

    # Files to create (Note: mathjax.js is removed)
    files_to_create = [
        (Path(docs_path / "stylesheets" / "extra.css"), EXTRA_CSS_CONTENT),
        (Path(docs_path / "javascripts" / "katex.js"), KATEX_JS_CONTENT),
    ]

    for file_path, content in files_to_create:
        if create_file_with_content(file_path, content):
            typer.echo(f"     -> File '{file_path}' populated.")
        else:
            typer.echo(f"     -> File '{file_path}' already exists. Skipping.")

    # 3. Create/Update 'mkdocs.yml'
    config_path = Path(MKDOCS_CONFIG_FILE)
    if not config_path.exists() or overwrite_config:
        mode = "Overwriting" if config_path.exists() else "Creating"
        
        # Inject the user-provided project name into the template
        final_yaml_content = MKDOCS_YML_TEMPLATE.strip().format(site_name_placeholder=project_name)
        
        with open(config_path, "w") as f:
            f.write(final_yaml_content)
        typer.echo(f"   - File '{MKDOCS_CONFIG_FILE}' {mode} with name '{project_name}' and custom file references.")
    else:
        typer.echo(f"   - File '{MKDOCS_CONFIG_FILE}' already exists. Skipping config update.")

def get_python_modules() -> List[Path]:
    """
    Finds all relevant Python modules in the project, excluding __init__.py files
    and files located within a 'scripts' or 'script' folder.
    """
    # 1. Find all Python files, excluding the setup script and those inside docs/
    python_files = [
        Path(p) for p in glob.glob("**/*.py", recursive=True)
        if Path(p) != Path(__file__) and not Path(p).is_relative_to(DOCS_FOLDER)
    ]
    
    modules = []
    
    for p in python_files:
        # 2. Exclude __init__.py files
        if p.name == "__init__.py":
            continue
            
        # 3. Exclude files under 'script' or 'scripts' folders (at any level)
        # We check the relative path components for 'script' or 'scripts'
        is_script = False
        for part in p.parts:
            if part.lower() in ('script', 'scripts'):
                is_script = True
                break
        
        if is_script:
            typer.echo(f"   - Ignoring script file: {p}")
            continue
            
        modules.append(p)
        
    return modules


def generate_api_doc_files(modules: List[Path]):
    """Generates and updates the Markdown stub files in docs/api/."""
    typer.echo(f"🔄 **UPDATING**: Generating API documentation stubs in '{DOCS_FOLDER}/api'...")

    docs_api_path = Path(DOCS_FOLDER) / "api"
    docs_api_path.mkdir(exist_ok=True)
    generated_count = 0
    updated_count = 0
    removed_count = 0

    api_nav_entries: List[Dict[str, str]] = []
    
    # Track which .md files should exist based on current modules
    expected_md_files = set()

    for py_file_path in modules:
        # Calculate Python import path (e.g., 'src/core.py' -> 'src.core')
        docstring_identifier = py_file_path.with_suffix("").as_posix().replace(os.sep, '.')
        
        # Determine the name for the Markdown file (e.g., docs/api/core.md)
        md_file_name = py_file_path.name.replace(".py", ".md")
        md_file_path = docs_api_path / md_file_name
        expected_md_files.add(md_file_path)
        
        # Generate the expected content for this module
        expected_content = f"# Reference: `{docstring_identifier}`\n\n::: {docstring_identifier}\n    options:\n      members: True\n      show_source: False\n"
        
        # 1. CREATE OR UPDATE MD STUB FILE
        if not md_file_path.exists():
            # Create new file
            with open(md_file_path, "w") as f:
                f.write(expected_content)
            typer.echo(f"   - Generated '{md_file_path}' for module '{docstring_identifier}'.")
            generated_count += 1
        else:
            # Check if existing file needs updating
            with open(md_file_path, "r") as f:
                existing_content = f.read()
            
            if existing_content.strip() != expected_content.strip():
                # Update existing file
                with open(md_file_path, "w") as f:
                    f.write(expected_content)
                typer.echo(f"   - Updated '{md_file_path}' for module '{docstring_identifier}'.")
                updated_count += 1
        
        # 2. COLLECT NAV ENTRY
        # Use the capitalized file name (stem) for the nav link name
        module_title = py_file_path.stem.replace('_', ' ').title()
        # The path is relative to the root mkdocs.yml
        nav_path = f"api/{md_file_name}"
        api_nav_entries.append({module_title: nav_path})

    # 3. REMOVE OBSOLETE MD FILES
    if docs_api_path.exists():
        for existing_md_file in docs_api_path.glob("*.md"):
            if existing_md_file not in expected_md_files:
                existing_md_file.unlink()
                typer.echo(f"   - Removed obsolete '{existing_md_file}' (module no longer exists).")
                removed_count += 1

    # Report summary
    if generated_count == 0 and updated_count == 0 and removed_count == 0:
        typer.echo("   - No changes needed for API documentation files.")
    else:
        summary_parts = []
        if generated_count > 0:
            summary_parts.append(f"{generated_count} new")
        if updated_count > 0:
            summary_parts.append(f"{updated_count} updated")
        if removed_count > 0:
            summary_parts.append(f"{removed_count} removed")
        typer.echo(f"   - API documentation files: {', '.join(summary_parts)}.")
    
    return api_nav_entries


def update_mkdocs_nav(api_nav_entries: List[Dict[str, str]]):
    """Reads mkdocs.yml and updates the 'nav' section with API entries."""
    if not Path(MKDOCS_CONFIG_FILE).exists():
        typer.echo(f"❌ **ERROR**: '{MKDOCS_CONFIG_FILE}' not found. Run 'mkdoc-setup create PROJECT_NAME' first.")
        raise typer.Exit(code=1)
    
    typer.echo(f"🔄 **UPDATING**: Dynamically updating 'nav' section in '{MKDOCS_CONFIG_FILE}'...")
    
    # Read the existing YAML configuration
    with open(MKDOCS_CONFIG_FILE, 'r') as f:
        config = yaml.load(f, Loader=yaml.SafeLoader) 
    
    if not isinstance(config, dict):
        typer.echo("❌ **ERROR**: Invalid YAML structure in mkdocs.yml.")
        raise typer.Exit(code=1)

    # 1. Build the new 'API' navigation item
    api_nav_item = {"API": api_nav_entries}
    
    # 2. Update the 'nav' list
    if 'nav' not in config or not isinstance(config['nav'], list):
        config['nav'] = []
        
    # Find and remove any existing 'API' section to replace it
    new_nav: List[Union[str, Dict[str, Union[str, List]]]] = []
    api_section_replaced = False
    
    for item in config['nav']:
        if isinstance(item, dict) and 'API' in item:
            # Replace the old API section with the new one
            new_nav.append(api_nav_item)
            api_section_replaced = True
        else:
            # Keep existing non-API items (like Home)
            new_nav.append(item)

    # If the API section was not found (first time running update), append it
    if not api_section_replaced:
        new_nav.append(api_nav_item)

    # Ensure "Home: README.md" is always first and not duplicated if possible
    # A safer approach is to reconstruct the nav completely based on known sections
    
    # Let's simplify: Ensure 'Home: README.md' is the first entry
    home_entry = {"Home": "README.md"}
    final_nav = [home_entry]
    
    # Add all unique entries from the old nav, excluding 'Home' and the old 'API'
    existing_keys = set(k for item in new_nav if isinstance(item, dict) for k in item.keys())
    
    if 'Home' in existing_keys:
        existing_keys.remove('Home')
    
    # Re-add non-Home/non-API items in order, then add the new API section
    for item in new_nav:
        if isinstance(item, dict):
            key = next(iter(item.keys()))
            if key != 'Home' and key != 'API':
                final_nav.append(item)
    
    final_nav.append(api_nav_item)
    
    # Assign the new, clean navigation list
    config['nav'] = final_nav
    
    # Write the updated configuration back to the file
    with open(MKDOCS_CONFIG_FILE, 'w') as f:
        yaml.safe_dump(config, f, sort_keys=False, default_flow_style=False)
        
    typer.echo("   - 'nav' section successfully updated with new API files.")


@app.command()
def update():
    """
    Scans for Python files, generates Markdown stubs, and updates the mkdocs.yml 'nav' section.
    """
    modules = get_python_modules()
    
    if not modules:
        typer.echo("\n⚠️ **WARNING**: No Python modules found (excluding __init__.py). Nothing to document.")
        return

    # 1. Generate the Markdown files and get the list of navigation entries
    api_nav_entries = generate_api_doc_files(modules)
    
    # 2. Update the mkdocs.yml navigation
    update_mkdocs_nav(api_nav_entries)

    typer.echo("\n✨ **COMPLETE**: API documentation stubs and mkdocs.yml updated.")
    typer.echo("   Run `mkdocs serve` to view your documentation.")

# --- Execution ---

if __name__ == "__main__":
    app()