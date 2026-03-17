# `mkdocs_setup.wizard` Module

## Overview

The `mkdocs_setup.wizard` module provides an interactive command-line interface (CLI) wizard for setting up and managing MkDocs-based documentation projects. This module streamlines the documentation workflow by guiding users through common tasks such as project initialization, code synchronization, and AI-assisted documentation generation.

## Key Features

### Interactive Setup Wizard
- **User-Friendly Interface**: Presents a menu-driven interface using the `questionary` library for intuitive navigation.
- **Project Initialization**: Guides users through the initial setup of a documentation project, including directory selection and configuration.
- **Context Awareness**: Detects whether a project is already initialized and adjusts available options accordingly.

### Project Management
- **Directory Handling**: Allows users to specify or change the project directory, with support for relative and absolute paths.
- **Project Lifecycle**: Supports both initial project setup and starting fresh with a new project configuration.

### Documentation Workflows
- **Code Synchronization**: Facilitates updating the reference documentation to reflect changes in the codebase.
- **AI-Assisted Documentation**: Integrates AI-powered documentation generation to automate the creation of docstrings and narrative documentation.

## Inputs

### User Inputs
- **Project Directory**: Path to the project root (defaults to the current directory).
- **Menu Selection**: User choices from the interactive menu to determine the next action (e.g., setup, sync, AI documentation, or exit).
- **API Key (for AI features)**: Optional input for configuring AI services (handled by the `ai` submodule).

### System Inputs
- **Project State**: Detects whether the current directory is already initialized as a documentation project.
- **Python Modules**: Scans the project directory for Python modules to document (handled by the `utils` submodule).

## Outputs

### File System Outputs
- **Project Initialization**: Creates or updates configuration files (e.g., `mkdocs.yml`) and directory structures for documentation.
- **API Documentation**: Generates or updates Markdown files in the `docs/api` folder for Python modules, classes, and functions.
- **Navigation Updates**: Modifies the `mkdocs.yml` navigation section to include newly generated documentation.

### User Feedback
- **Status Messages**: Provides real-time feedback on actions taken, errors encountered, and next steps.
- **Visual Indicators**: Uses colored text and emojis to enhance readability and user experience.

### API Documentation
For detailed technical specifications, including function signatures, parameters, and return values, refer to the [API documentation](docs/api/mkdocs_setup.wizard.md) in the `docs/api` folder.

## Algorithms and Logic

### Project Initialization
- Validates the target directory and ensures it is accessible.
- Generates default configuration files based on the `DEFAULT_PARADIGM` constant.
- Sets up the basic structure for MkDocs, including directories for source files and API documentation.

### Code Synchronization
- Scans the project for Python modules using `get_python_modules`.
- Generates or updates API documentation files in Markdown format using `generate_api_doc_files`.
- Updates the `mkdocs.yml` navigation section to include the new or updated API documentation.

### AI-Assisted Documentation
- Leverages the `ai_logic` submodule to generate docstrings and narrative documentation.
- Handles API key management for AI services, including retrieval and secure storage.

## Dependencies

- **`typer`**: Used for building the CLI and providing rich text output.
- **`questionary`**: Enables interactive prompts and menus.
- **`mkdocs_setup` Submodules**: Relies on `constants`, `utils`, `ai`, `core`, and `ai_logic` for specific functionalities.

## Usage Context

This module serves as the primary entry point for users interacting with the `mkdocs_setup` tool. It abstracts the complexity of individual submodules, providing a cohesive and guided experience for documentation management. For programmatic access to specific functionalities, users should refer to the respective submodules directly.