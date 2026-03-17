import os
import json
import glob
import re
import ast
from pathlib import Path
from typing import List, Set
import yaml
import typer
from mkdocs_setup.constants import DOCS_FOLDER, MKDOCS_CONFIG_FILE

def get_project_dependencies() -> str:
    """
    Extracts project dependencies. Tries requirements.txt, then pyproject.toml,
    and falls back to scanning imports in Python files.
    """
    # 1. Check requirements.txt
    req_file = Path("requirements.txt")
    if req_file.exists():
        return f"DEPENDENCIES (from requirements.txt):\n{req_file.read_text()}"

    # 2. Check pyproject.toml
    pyproj_file = Path("pyproject.toml")
    if pyproj_file.exists():
        return f"DEPENDENCIES (from pyproject.toml):\n{pyproj_file.read_text()}"

    # 3. Fallback: Scan imports
    typer.echo("🔍 No dependency files found. Scanning imports instead...")
    from mkdocs_setup.utils import get_python_modules
    modules = get_python_modules()
    all_imports: Set[str] = set()

    for mod_path in modules:
        try:
            content = mod_path.read_text(encoding='utf-8')
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        all_imports.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        all_imports.add(node.module.split('.')[0])
        except Exception:
            continue
    
    if all_imports:
        # Filter out standard library might be hard, but we can just provide the list
        deps_list = "\n".join(sorted(list(all_imports)))
        return f"DEPENDENCIES (extracted from imports):\n{deps_list}"
    
    return "No dependencies identified."

def ignore_python_tags(loader, node):
    """Custom constructor that ignores the !!python/name tag."""
    # Simply return the string content of the node, which is the full Python path
    return loader.construct_scalar(node)

def setup_yaml_loader():
    """Configures the YAML SafeLoader to ignore custom Python tags."""
    try:
        # Check if the constructor is already added to prevent re-adding errors
        if 'tag:yaml.org,2002:python/name' not in yaml.SafeLoader.yaml_constructors:
            yaml.SafeLoader.add_constructor('tag:yaml.org,2002:python/name', ignore_python_tags)
    except AttributeError:
        # Fallback or error handling if SafeLoader structure is different (unlikely)
        print("Warning: Could not configure custom YAML loader.")

def create_file_with_content(file_path: Path, content: str, overwrite: bool = False):
    """Creates a file if it doesn't exist, or overwrites it if overwrite is True."""
    if not file_path.exists() or overwrite:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w") as f:
            f.write(content.strip())
        return True
    return False

def is_project_initialized() -> bool:
    """Checks if the project has been initialized (docs folder and mkdocs.yml exist)."""
    return Path(DOCS_FOLDER).exists() and Path(MKDOCS_CONFIG_FILE).exists()

def get_python_modules() -> List[Path]:
    """
    Finds all relevant Python modules in the project, excluding __init__.py files
    and files located within a 'scripts' or 'script' folder.
    """
    # 1. Find all Python files, excluding those inside docs/
    # We use a trick to avoid including the current cli.py if needed, 
    # but here we just want to avoid docs/ folder and maintenance scripts.
    python_files = [
        Path(p) for p in glob.glob("**/*.py", recursive=True)
        if not Path(p).is_relative_to(DOCS_FOLDER)
    ]
    
    modules = []
    
    for p in python_files:
        # 2. Exclude __init__.py files
        if p.name == "__init__.py":
            continue
            
        # 3. Exclude files under 'script' or 'scripts' folders (at any level)
        is_script_folder = False
        for part in p.parts:
            if part.lower() in ('script', 'scripts'):
                is_script_folder = True
                break
        
        if is_script_folder:
            # Silently ignore maintenance scripts
            continue

        # 4. Filter "pure scripts": only include if it contains 'class ' or 'def '
        try:
            with open(p, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'class ' not in content and 'def ' not in content:
                    # Silently ignore files without documentable elements
                    continue
        except Exception as e:
            typer.echo(f"   - Error reading {p}: {e}")
            continue
            
        modules.append(p)
        
    return modules

def get_entry_points() -> str:
    """
    Tries to find entry point scripts in setup.py or pyproject.toml,
    and also looks for __main__.py files.
    """
    entry_points_info = []

    # 1. Check setup.py
    setup_file = Path("setup.py")
    if setup_file.exists():
        try:
            content = setup_file.read_text()
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and getattr(node.func, 'id', '') == 'setup':
                    for keyword in node.keywords:
                        if keyword.arg == 'entry_points':
                            # Try to extract the entry_points dict or string
                            if isinstance(keyword.value, ast.Dict):
                                ep_dict = {}
                                for k, v in zip(keyword.value.keys, keyword.value.values):
                                    if isinstance(k, ast.Constant):
                                        ep_dict[k.value] = ast.unparse(v)
                                entry_points_info.append(f"ENTRY POINTS (from setup.py):\n{json.dumps(ep_dict, indent=4)}")
                            else:
                                entry_points_info.append(f"ENTRY POINTS (from setup.py):\n{ast.unparse(keyword.value)}")
                        elif keyword.arg == 'scripts':
                            entry_points_info.append(f"SCRIPTS (from setup.py):\n{ast.unparse(keyword.value)}")
        except Exception:
            # Fallback to simple regex if AST fails
            ep_match = re.search(r'entry_points\s*=\s*(\{.*?\})', setup_file.read_text(), re.DOTALL)
            if ep_match:
                entry_points_info.append(f"ENTRY POINTS (from setup.py - fallback):\n{ep_match.group(1)}")

    # 2. Check pyproject.toml
    pyproj_file = Path("pyproject.toml")
    if pyproj_file.exists():
        try:
            content = pyproj_file.read_text()
            # Look for [project.scripts] or [tool.poetry.scripts]
            for section in ["[project.scripts]", "[tool.poetry.scripts]", "[tool.setuptools.script-files]"]:
                if section in content:
                    parts = content.split(section)
                    if len(parts) > 1:
                        # Extract until next section or end of file
                        scripts = parts[1].split("\n[")[0].strip()
                        entry_points_info.append(f"SCRIPTS (from pyproject.toml {section}):\n{scripts}")
        except Exception:
            pass

    # 3. Look for __main__.py files
    main_files = list(Path().glob("**/__main__.py"))
    if main_files:
        main_info = "\n".join([f"- {p}" for p in main_files])
        entry_points_info.append(f"MAIN FILES (__main__.py):\n{main_info}")

    if entry_points_info:
        return "\n\n".join(entry_points_info)
    
    return "No explicit entry points or scripts found."
