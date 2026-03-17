# Quickstart Guide for mkdocs-setup

## Installation

1. Install the package using pip:
```bash
pip install mkdocs-setup
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

This will start a local development server at `http://127.0.0.1:8000`.

## Environment Configuration

Set API keys for LLM providers in your `.env` file:
```env
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key
DEEPSEEK_API_KEY=your_deepseek_key
MISTRAL_API_KEY=your_mistral_key
```