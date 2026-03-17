# mkdocs-setup CLI Module

## Overview

The `mkdocs-setup` CLI module provides a command-line interface for creating and managing professional documentation for Python projects. This tool automates the setup of MkDocs-based documentation, including API documentation generation, project structure initialization, and integration with AI-powered documentation assistants.

## Core Features

### Project Initialization
- Creates a complete MkDocs documentation structure with configurable paradigms (documentation templates)
- Supports both default paradigms (quickstart, setups, etc.) and custom paradigm folders
- Handles configuration file creation with optional overwrite capability

### Documentation Generation
- Automatically generates API documentation from Python docstrings
- Updates MkDocs navigation configuration to include generated documentation
- Integrates existing markdown documentation into the project structure

### AI Integration
- Supports multiple AI providers (OpenAI, Google, DeepSeek, Mistral) for enhanced documentation generation
- Securely manages API keys through environment variables
- Provides interactive setup for AI configuration

### Project Management
- Wizard-based interactive setup for new users
- Checks for existing project initialization
- Identifies Python modules for documentation generation

## Key Components

### Command Structure
The CLI centers around the `create` command, which serves as the primary entry point for documentation project setup. This command orchestrates the entire documentation creation process.

### Configuration Management
- Handles MkDocs configuration file (`mkdocs.yml`) creation and updates
- Manages documentation folder structure
- Supports environment variable configuration for sensitive data

### Paradigm System
- Implements a flexible paradigm system for documentation templates
- Allows inclusion of default paradigms and custom paradigms
- Provides a foundation for consistent documentation structure

## Inputs

### Command-line Arguments
- **Project Name**: Required identifier for the documentation project
- **Configuration Options**: Flags for overwriting existing configuration
- **Paradigm Selection**: Lists of default and custom paradigms to include
- **API Keys**: Optional AI provider keys for enhanced documentation generation

### Project Files
- Python source files (for API documentation generation)
- Existing markdown documentation (for integration)
- Environment configuration (`.env` file for API keys)

## Outputs

### Documentation Structure
- Complete MkDocs project structure in the `docs/` folder
- Generated API documentation from Python modules
- Updated MkDocs navigation configuration
- Paradigm-based documentation templates

### Configuration Files
- `mkdocs.yml` configuration file
- Environment variable configuration for AI services

## Workflow

1. **Initialization**: Sets up the basic documentation structure based on the specified paradigms
2. **API Documentation**: Generates documentation from Python source files
3. **Navigation Update**: Configures the MkDocs navigation to include all documentation
4. **AI Integration**: Optionally configures AI services for enhanced documentation
5. **Finalization**: Completes the setup and provides user feedback

For detailed technical specifications and API documentation, refer to the [API documentation in the docs/api folder](../api/cli.md).