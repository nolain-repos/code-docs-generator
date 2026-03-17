# Architecture Overview

## System Design

**mkdocs-setup** is a modular command-line tool designed to automate and enhance Python project documentation workflows. The system integrates multiple components that work together to provide a seamless documentation experience, from initial setup to AI-assisted content generation.

---

## Core Components

### 1. Command-Line Interface (CLI)

The CLI serves as the primary entry point for users, built using the **Typer** library. It exposes commands for initializing projects, generating documentation, and managing configurations.

- **Entry Point**: The `cli.py` module defines the CLI structure and maps commands to internal functions (e.g., `mkdocs-setup create`).
- **Commands**:
  - `create`: Initializes a new documentation project.
  - `wizard`: Launches an interactive setup guide (via `run_wizard` in `wizard.py`).
  - Additional commands for API key management and documentation updates.

The CLI interacts with other components by invoking core functions (e.g., `init_project`, `generate_api_doc_files`) and passing user inputs.

---

### 2. Project Initialization and Configuration

Handled by the `core.py` module, this component manages the setup of the documentation infrastructure.

- **Key Functions**:
  - `init_project`: Creates the `docs/` directory, initializes `mkdocs.yml`, and sets up default configurations.
  - `generate_api_doc_files`: Generates Markdown stubs for Python modules in `docs/api/` using **mkdocstrings**.
  - `update_mkdocs_nav`: Dynamically updates the `mkdocs.yml` navigation section to include generated API docs.

- **Dependencies**:
  - **PyYAML**: For parsing and writing YAML configurations.
  - **mkdocs**: For static site generation templates.

---

### 3. AI-Powered Documentation

The `ai_logic.py` module leverages large language models (LLMs) to generate human-readable documentation.

- **Key Functions**:
  - `generate_ai_docs`: Uses LLM providers (OpenAI, Google, DeepSeek, Mistral) to generate content for project documentation.
  - `clean_llm_markdown_output`: Sanitizes LLM responses to ensure valid Markdown output.

- **API Key Management**:
  - The `ai.py` module handles API key retrieval and storage via `.env` files (using **python-dotenv**).
  - Supports multiple providers, with keys sourced from CLI arguments or environment variables.

- **Integration**:
  - Calls to LLMs are abstracted via `call_llm` (in `ai.py`), which routes requests to the appropriate provider.
  - Generated content is written to Markdown files in `docs/`.

---

### 4. Interactive Wizard

The `wizard.py` module provides a guided setup experience using the **questionary** library.

- **Workflow**:
  1. Detects if the project is already initialized (via `is_project_initialized` in `utils.py`).
  2. Prompts the user for project details (e.g., path, API keys, documentation preferences).
  3. Orchestrates calls to `core.py` and `ai_logic.py` to generate documentation.

- **User Experience**:
  - Context-aware prompts (e.g., skips API key setup if keys are already configured).
  - Progress feedback via **Typer**'s styled output.

---

### 5. Utilities

The `utils.py` module provides helper functions for project introspection and file operations.

- **Key Functions**:
  - `get_python_modules`: Scans the project directory for Python files to document.
  - `get_project_dependencies`: Extracts dependencies from `requirements.txt`, `pyproject.toml`, or source code imports.
  - `get_entry_points`: Identifies CLI entry points for inclusion in documentation.
  - `setup_yaml_loader`: Configures YAML parsing for `mkdocs.yml`.

- **Integration**:
  - Used by `core.py` to discover modules for API documentation.
  - Used by `ai_logic.py` to gather project context for AI-generated content.

---

## Data Flow

1. **Initialization**:
   - User runs `mkdocs-setup create` or `mkdocs-setup wizard`.
   - CLI invokes `init_project` to set up the `docs/` directory and `mkdocs.yml`.
   - `get_python_modules` scans the project for Python files.

2. **API Documentation**:
   - `generate_api_doc_files` creates Markdown stubs for each module in `docs/api/`.
   - `update_mkdocs_nav` updates the navigation in `mkdocs.yml`.

3. **AI-Generated Content**:
   - `generate_ai_docs` calls the LLM provider (via `call_llm`) with project context (dependencies, entry points, etc.).
   - Sanitized output is written to Markdown files in `docs/`.

4. **Static Site Generation**:
   - **MkDocs** (with the **Material** theme) renders the documentation as a static site.
   - Plugins like **mkdocstrings** and **mkdocs-jupyter** enhance functionality.

---

## External Integrations

### 1. MkDocs Ecosystem
- **mkdocs**: Static site generator for documentation.
- **mkdocs-material**: Theme for professional-looking docs.
- **mkdocstrings**: Auto-generates API documentation from docstrings.
- **mkdocs-jupyter**: Supports Jupyter notebooks in documentation.
- **mkdocs-glightbox**: Adds image lightbox functionality.

### 2. LLM Providers
- **OpenAI**: GPT-based models for content generation.
- **Google Generative AI**: Google's LLM for documentation assistance.
- **DeepSeek**: Alternative LLM provider.
- **Mistral**: Open-source LLM option.

### 3. Environment Management
- **python-dotenv**: Loads API keys and configurations from `.env` files.

---

## Key Design Principles

1. **Modularity**:
   - Components are decoupled (e.g., `ai_logic.py` is independent of `core.py`).
   - Shared utilities (e.g., `utils.py`) avoid code duplication.

2. **Extensibility**:
   - New LLM providers can be added by extending `ai.py`.
   - Additional documentation formats (e.g., Sphinx) could be supported with minimal changes.

3. **User Experience**:
   - Interactive wizard for beginners.
   - CLI commands for advanced users.
   - Progress feedback via styled output.

4. **Security**:
   - API keys are stored in `.env` files (excluded from version control).
   - Keys can be passed via CLI or environment variables.

---

## Example Workflow

1. **Setup**:
   - User runs `mkdocs-setup wizard`.
   - Wizard detects an uninitialized project and prompts for details.
   - `init_project` creates the `docs/` directory and `mkdocs.yml`.

2. **API Documentation**:
   - `get_python_modules` scans the project for Python files.
   - `generate_api_doc_files` creates Markdown stubs in `docs/api/`.
   - `update_mkdocs_nav` updates the navigation in `mkdocs.yml`.

3. **AI-Generated Content**:
   - User selects an LLM provider (e.g., OpenAI).
   - `generate_ai_docs` calls the LLM with project context.
   - Generated content is saved to `docs/`.

4. **Static Site Generation**:
   - User runs `mkdocs serve` to preview the documentation.
   - **MkDocs** renders the site using the Material theme.