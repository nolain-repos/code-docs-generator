# Quickstart Guide for mkdocs-setup

## Installation

1. Install the package in your conda environment using pip:
```bash
pip install -e .
```

## Basic Usage

### 1. Run the interactive setup wizard
```bash
mkdocs-setup
```

Follow the interactive prompts to:
- Set up documentation in an existing project
- Configure API keys for AI-assisted documentation
- Generate documentation content


## Serve documentation locally
Run the following command to serve the documentation locally:

```bash
mkdocs serve
```

and enter the url in your browser (or press CTRL + Click on the link).

## Environment Configuration

Set API keys for LLM providers in your `.env` file:
```env
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key
DEEPSEEK_API_KEY=your_deepseek_key
MISTRAL_API_KEY=your_mistral_key
```