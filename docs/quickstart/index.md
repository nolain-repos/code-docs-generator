# Quickstart Guide for mkdocs-setup

## Installation

1. Install the package using pip:
```bash
pip install mkdocs-setup
```

## Basic Usage

### 1. Initialize a new documentation project
```bash
mkdocs-setup create PROJECT_NAME
```

Replace `PROJECT_NAME` with your project's name (e.g., `MyAwesomeProject`).

**Optional arguments:**
- `--overwrite-config`: Overwrite existing mkdocs.yml configuration (default: False)
- `--docs-folder PATH`: Specify custom docs folder location (default: "docs")
- `--paradigm PARADIGM`: Documentation paradigm (choices: "google", "numpy", "sphinx"; default: "google")

### 2. Run the interactive setup wizard
```bash
mkdocs-setup wizard
```

Follow the interactive prompts to:
- Set up documentation in an existing project
- Configure API keys for AI-assisted documentation
- Generate documentation content

### 3. Generate API documentation
```bash
mkdocs-setup generate-api
```

**Optional arguments:**
- `--docs-folder PATH`: Specify custom docs folder location (default: "docs")
- `--paradigm PARADIGM`: Documentation paradigm (choices: "google", "numpy", "sphinx"; default: "google")

### 4. Generate AI-assisted documentation
```bash
mkdocs-setup generate-ai-docs MODULE_NAME
```

Replace `MODULE_NAME` with the name of the module to document.

**Optional arguments:**
- `--provider PROVIDER`: LLM provider (choices: "openai", "google", "deepseek", "mistral"; default: "openai")
- `--api-key KEY`: API key for the LLM provider (default: reads from environment variables)
- `--docs-folder PATH`: Specify custom docs folder location (default: "docs")
- `--paradigm PARADIGM`: Documentation paradigm (choices: "google", "numpy", "sphinx"; default: "google")

### 5. Add existing documentation
```bash
mkdocs-setup add-existing-docs
```

**Optional arguments:**
- `--docs-folder PATH`: Specify custom docs folder location (default: "docs")

### 6. Serve documentation locally
```bash
mkdocs serve
```

This will start a local development server at `http://127.0.0.1:8000`.

## Environment Configuration

Set API keys for LLM providers in your `.env` file:
```env
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key
DEEPSEEK_API_KEY=your_deepseek_key
MISTRAL_API_KEY=your_mistral_key
```