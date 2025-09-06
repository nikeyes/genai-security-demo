# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a security-focused GenAI chatbot demonstrating defensive security measures for generative AI applications. The project showcases various protection mechanisms including input/output guardrails, prompt injection detection, and secure chat implementations.

## Key Commands

### Development Setup
```bash
# Install uv and all dependencies (including dev)
make install

# Run the web interface
uv run python chatbot_webui.py

# Console version
uv run python chatbot_console.py
```

### Testing
```bash
# Run all tests locally (requires API keys) - RECOMMENDED
make local-tests

# Run CI tests (excludes real provider tests)  
make ci-tests

# Individual test commands
uv run pytest -v --cov=src --no-cov-on-fail --cov-report=term-missing tests/
uv run pytest -v tests/ -m "not real_provider"  # CI-safe tests only
```

### Code Quality
```bash
# Lint and format with auto-fix
make lint-fix

# Check linting only
make lint
uv run ruff check
```

## Architecture

### Core Components

- **`src/config/`** - LLM provider configurations (Bedrock, OpenAI, Groq, Anthropic)
- **`src/chatbot/`** - Bot implementations with different security levels
- **`src/ui/`** - Gradio web interfaces for different demo scenarios
- **`src/prompts.py`** - System prompts and guardrail templates

### Security Features

The project integrates Meta Llama security tools controlled by `LLAMA_SECURITY_FAMILY` in `src/config/llm_config.py`:
- **Llama PromptGuard** - Input guardrail detection
- **Purple-Llama CodeShield** - Output content filtering

### Bot Types

- **`UnprotectedBot`** - Basic implementation without security measures
- **`SecureBot`** - Implements instruction change guardrails and canary word detection
- **Input/Output Guardrail Bots** - Specialized bots with Meta Llama security integration

### Provider System

LLM providers are abstracted through a common interface with specific implementations for:
- Amazon Bedrock (default)
- OpenAI
- Groq  
- Anthropic

## Environment Configuration

### Required for Testing
- `GROQ_API_KEY`
- `OPENAI_API_KEY` 
- `AWS_DEFAULT_PROFILE`
- `ANTHROPIC_API_KEY`
- `HF_TOKEN` (for Llama security models)

### AWS Bedrock Setup
```bash
# Configure AWS SSO profile
aws configure set sso_start_url https://YOUR_ORGANIZATION.awsapps.com/start --profile PROFILE_NAME
aws sso login --profile PROFILE_NAME
export AWS_DEFAULT_PROFILE=PROFILE_NAME
```

## Testing Strategy

- **Unit tests** in `tests/unit_tests/`
- **Integration tests** in `tests/integration_tests/` (marked as `real_provider`)  
- **Approval tests** in `tests/approval_tests/`
- Use `-m "not real_provider"` to skip tests requiring real API calls

## Security Considerations

- Canary word detection for prompt leakage (`lightblueeagle`)
- Instruction change guardrails using async task racing
- Sandwich defense pattern implementation
- Input validation through PromptGuard
- Output filtering through CodeShield