# mkdoc-setup: Python Documentation Starter Kit 🐍

The **`mkdoc-setup`** CLI is a bootstrapping tool designed to instantly set up a Python project with a professional documentation structure using **Material for MkDocs** and automatic API documentation via **MkDocstrings**.

It handles configuration, theme setup, custom assets (KaTeX, custom CSS), and dynamically builds the navigation structure based on your Python modules.

## Installation

This tool is designed to be installed once in your development environment and used across all your Python projects.

1.  **Install the Tool (from its repository folder):**

    ```bash
    # Run this command from the tool's root directory (e.g., your docsgenerator folder)
    # The '-e' flag installs it in editable mode for development
    pip install -e .
    ```
-----

## Usage

Navigate to the **root directory of your Python project** (where your main package folder resides) and run the following commands.

### 1\. The `create` Command (Initial Setup)

This command initializes the entire documentation boilerplate. You must provide the desired **project name** for the documentation title (`site_name`).

| Argument | Description |
| :--- | :--- |
| `PROJECT_NAME` | The title used for `site_name` in `mkdocs.yml` (e.g., `My Awesome Project`). |
| `--overwrite-config, -o` | (Optional) Force overwrite of an existing `mkdocs.yml` file. |

**Example:**

```bash
mkdoc-setup create AI-Data-Extractor
```

**What it does:**

  * Creates **`README.md`** at the project root.
  * Creates the **`docs/`** directory with sub-folders (`assets/`, `stylesheets/`, `javascripts/`).
  * Creates and populates custom files (`extra.css`, `katex.js`).
  * Creates **`mkdocs.yml`** with the full configuration, setting the dynamic `site_name`.

-----

### 2\. The `update` Command (Sync API)

After running `create` and adding new Python files to your project, run `update` to automatically synchronize your API documentation.

**Command:**

```bash
mkdoc-setup update
```

**What it does:**

  * Scans your project directory for all Python modules.
  * **Excludes** files named `__init__.py` and files located within folders named `script` or `scripts`.
  * Creates a new Markdown stub (`.md`) file in **`docs/api/`** for every discovered module.
  * **Dynamically updates** the `nav` section in your `mkdocs.yml` file to list all generated API modules under an **"API"** heading, using paths relative to the `docs/` folder (e.g., `api/my_module.md`).

-----

## Development Workflow

1.  **Start Project:**
    ```bash
    cd my-new-project
    mkdoc-setup create MyProjectName
    ```
2.  **Develop Code:** Write your Python modules and include proper docstrings (e.g., `my_package/core.py`).
3.  **Update Docs:** After adding new modules, synchronize the navigation:
    ```bash
    mkdoc-setup update
    ```
4.  **Preview Docs:** Serve the documentation locally:
    ```bash
    mkdocs serve
    ```
    (View the output at `http://127.0.0.1:8000`)
5.  **Build Final Docs:**
    ```bash
    mkdocs build
    ```
    (This generates the static site in the `site/` folder).
