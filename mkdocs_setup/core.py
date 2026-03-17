import os
from pathlib import Path
from typing import List, Dict
import yaml
import typer
from mkdocs_setup.constants import DOCS_FOLDER, MKDOCS_CONFIG_FILE, DEFAULT_PARADIGM
from mkdocs_setup.utils import setup_yaml_loader

def generate_api_doc_files(modules: List[Path]):
    """Generates and updates the Markdown stub files in docs/api/."""
    typer.echo(f"🔄 **UPDATING**: Updating your technical reference guide...")

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
            generated_count += 1
        else:
            # Check if existing file needs updating
            with open(md_file_path, "r") as f:
                existing_content = f.read()
            
            if existing_content.strip() != expected_content.strip():
                # Update existing file
                with open(md_file_path, "w") as f:
                    f.write(expected_content)
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
        typer.echo(f"   - Reference guide updated: {', '.join(summary_parts)}.")
    
    return api_nav_entries

def update_mkdocs_nav(api_nav_entries: List[Dict[str, str]]):
    """Reads mkdocs.yml and updates the 'nav' section with API entries."""
    if not Path(MKDOCS_CONFIG_FILE).exists():
        typer.echo(f"❌ **Oopsy!**: I couldn't find '{MKDOCS_CONFIG_FILE}'. Please run the setup first.")
        raise typer.Exit(code=1)
    
    typer.echo(f"🔄 **UPDATING**: Organizing your documentation menu...")
    
    setup_yaml_loader()
    
    # Read the existing YAML configuration
    with open(MKDOCS_CONFIG_FILE, 'r') as f:
        config = yaml.load(f, Loader=yaml.SafeLoader) 
    
    if not isinstance(config, dict):
        typer.echo("❌ **ERROR**: Invalid YAML structure in mkdocs.yml.")
        raise typer.Exit(code=1)

    # 1. Build the new 'API' navigation item
    api_nav_item = {"API": api_nav_entries}
    
    # 2. Build Paradigm sections
    paradigm_nav_items = []
    for paradigm in DEFAULT_PARADIGM.keys():
        p_path = Path(DOCS_FOLDER) / paradigm
        if p_path.exists():
            # Find all .md files in this paradigm
            p_files = list(p_path.glob("*.md"))
            if p_files:
                entries = []
                for pf in sorted(p_files):
                    title = pf.stem.replace('_', ' ').replace('-', ' ').title()
                    if pf.name == "index.md": title = "Overview"
                    entries.append({title: f"{paradigm}/{pf.name}"})
                paradigm_nav_items.append({paradigm.title(): entries})

    # 3. Update the 'nav' list
    if 'nav' not in config or not isinstance(config['nav'], list):
        config['nav'] = []
        
    # Reconstruct the nav
    home_entry = {"Home": "README.md"}
    final_nav = [home_entry]
    
    # Add paradigm sections
    final_nav.extend(paradigm_nav_items)
    
    # Add any other existing sections that are not Home, API, or paradigms
    paradigm_titles = [p.title() for p in DEFAULT_PARADIGM.keys()]
    for item in config['nav']:
        if isinstance(item, dict):
            key = next(iter(item.keys()))
            if key not in (['Home', 'API'] + paradigm_titles):
                final_nav.append(item)
    
    # Add API section at the end
    final_nav.append(api_nav_item)
    
    # Assign the new, clean navigation list
    config['nav'] = final_nav
    
    # Write the updated configuration back to the file
    with open(MKDOCS_CONFIG_FILE, 'w') as f:
        yaml.safe_dump(config, f, sort_keys=False, default_flow_style=False)
        
    typer.echo(f"   - Navigation menu is now organized and up to date.")

def init_project(
    project_name: str,
    include_paradigms: List[str] = None,
    extra_paradigms: List[str] = None,
    overwrite_config: bool = False
):
    """Logic for initializing a new documentation project."""
    from mkdocs_setup.constants import README_MD_CONTENT, EXTRA_CSS_CONTENT, KATEX_JS_CONTENT, MKDOCS_YML_TEMPLATE
    from mkdocs_setup.utils import create_file_with_content

    # 1. Determine Paradigm Folders
    selected_paradigms = []
    if include_paradigms is not None:
        selected_paradigms.extend([p for p in include_paradigms if p in DEFAULT_PARADIGM])
    else:
        # Default behavior: include all
        selected_paradigms = list(DEFAULT_PARADIGM.keys())
    
    if extra_paradigms:
        selected_paradigms.extend(extra_paradigms)

    # 2. Create 'docs' folder
    docs_path = Path(DOCS_FOLDER)
    docs_path.mkdir(exist_ok=True)

    if selected_paradigms:
        for paradigm in selected_paradigms:
            p_path = docs_path / paradigm
            p_path.mkdir(exist_ok=True)
            readme_p = p_path / "index.md"
            desc = DEFAULT_PARADIGM.get(paradigm, "Custom documentation section.")
            create_file_with_content(readme_p, f"# {paradigm.title()}\n\n{desc}")

    # 4. Create README.md at docs
    readme_path = Path(f"{DOCS_FOLDER}/README.md")
    create_file_with_content(readme_path, README_MD_CONTENT)

    # 4.1 Also copy to root and adjust hyperlinks for GitHub compatibility
    root_readme_content = README_MD_CONTENT
    for p in DEFAULT_PARADIGM.keys():
        root_readme_content = root_readme_content.replace(f"({p}/", f"({DOCS_FOLDER}/{p}/")
    
    create_file_with_content(Path("README.md"), root_readme_content, overwrite=True)
    typer.echo("   - Project root 'README.md' is now set up with documentation links.")

    # 5. Create sub-folders and files
    sub_folders = ["assets", "stylesheets", "javascripts"]
    for folder in sub_folders:
        Path(docs_path / folder).mkdir(exist_ok=True)

    files_to_create = [
        (Path(docs_path / "stylesheets" / "extra.css"), EXTRA_CSS_CONTENT),
        (Path(docs_path / "javascripts" / "katex.js"), KATEX_JS_CONTENT),
    ]

    for file_path, content in files_to_create:
        create_file_with_content(file_path, content)

    # 3. Create/Update 'mkdocs.yml'
    config_path = Path(MKDOCS_CONFIG_FILE)
    if not config_path.exists() or overwrite_config:
        # Inject the user-provided project name into the template
        final_yaml_content = MKDOCS_YML_TEMPLATE.strip().format(site_name_placeholder=project_name)
        
        with open(config_path, "w") as f:
            f.write(final_yaml_content)
        typer.echo(f"   - Configuration file '{MKDOCS_CONFIG_FILE}' is now set up for '{project_name}'.")
    else:
        typer.echo(f"   - Configuration file already exists. Skipping setup.")

def add_existing_docs(docs_dir: str):
    """Logic for adding existing .md files to navigation."""
    docs_path = Path(docs_dir)
    if not docs_path.exists():
        typer.echo(f"❌ **Oopsy!**: I couldn't find the folder '{docs_dir}'.")
        raise typer.Exit(code=1)
    
    if not Path(MKDOCS_CONFIG_FILE).exists():
        typer.echo(f"❌ **Oopsy!**: I couldn't find '{MKDOCS_CONFIG_FILE}'. Please run the setup first.")
        raise typer.Exit(code=1)
    
    md_files = list(docs_path.glob("**/*.md"))
    if not md_files:
        typer.echo(f"⚠️ **WARNING**: No .md files found in '{docs_dir}'.")
        return
    
    typer.echo(f"   - Found {len(md_files)} .md file(s).")
    
    nav_entries = []
    for md_file in sorted(md_files):
        relative_path = md_file.relative_to(Path.cwd())
        title = md_file.stem.replace('_', ' ').replace('-', ' ').title()
        if md_file.name.lower() == "readme.md":
            title = "Home"
        nav_entries.append({title: str(relative_path)})
    
    typer.echo(f"🔄 **UPDATING**: Populating 'nav' section in '{MKDOCS_CONFIG_FILE}'...")
    
    setup_yaml_loader()
    with open(MKDOCS_CONFIG_FILE, 'r') as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)
    
    if not isinstance(config, dict):
        typer.echo("❌ **ERROR**: Invalid YAML structure in mkdocs.yml.")
        raise typer.Exit(code=1)
    
    config['nav'] = nav_entries
    with open(MKDOCS_CONFIG_FILE, 'w') as f:
        yaml.safe_dump(config, f, sort_keys=False, default_flow_style=False)
    
    typer.echo("   - Menu updated with your existing files.")

