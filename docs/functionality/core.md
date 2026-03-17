# `mkdocs_setup.core` Module Documentation

## Overview

The `mkdocs_setup.core` module provides automated documentation generation capabilities for Python projects using MkDocs. It streamlines the process of creating and maintaining technical reference documentation by generating API documentation stubs from Python source files.

## Core Features

### API Documentation Generation

The primary feature of this module is the automated generation of Markdown documentation files for Python modules. This functionality:

- Creates new documentation stubs for previously undocumented modules
- Updates existing documentation files when source code changes
- Maintains a clean synchronization between code and documentation
- Tracks documentation status (created, updated, or removed files)

### Navigation Integration

The module prepares navigation entries for integration with MkDocs' configuration, enabling automatic inclusion of generated API documentation in the project's documentation site structure.

## Key Algorithms

### Documentation Synchronization

The module implements a file synchronization algorithm that:

1. Identifies all Python modules requiring documentation
2. Generates standardized Markdown content for each module
3. Compares expected content with existing documentation
4. Updates only those files that have changed or are new
5. Tracks which files should exist based on current modules

### Path Conversion

The module converts filesystem paths to Python import paths through a systematic transformation process, ensuring proper reference generation for the documentation system.

## Inputs

### Primary Input

- **Python Module Paths**: A list of `Path` objects pointing to Python source files that require documentation generation

### Configuration Dependencies

- **Documentation Folder**: Uses the `DOCS_FOLDER` constant to determine where documentation files should be stored
- **MkDocs Configuration**: Prepares data for integration with the project's MkDocs configuration file

## Outputs

### File System Outputs

- **Markdown Documentation Files**: Creates or updates `.md` files in the `docs/api/` directory, each containing:
  - A reference header with the module's import path
  - MkDocs-compatible directives for API documentation generation

### Status Reporting

- **Operation Statistics**: Returns counts of generated, updated, and removed documentation files
- **Navigation Entries**: Produces structured data for integration with the MkDocs navigation system

### User Feedback

- Provides real-time console output about the documentation update process

## Technical Reference

For detailed technical specifications, including function signatures, parameters, and return values, please refer to the [API documentation](docs/api/core.md) in the `docs/api/` folder.