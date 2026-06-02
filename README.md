# AI Agent Layer

Self-hosted AI Agent Adapter Layer for model routing, automation workers, website inspection, and authorized site reconstruction.

## Architecture

SaaS / Admin Panel -> Agent API -> LiteLLM Gateway -> Model Providers -> Worker Layer -> Playwright / Shell / Docker.

## Quick Start

These are README instructions for future users after cloning the repository:

1. cp .env.example .env
2. cp litellm-config.example.yaml litellm-config.yaml
3. docker compose up -d --build

## Security

Do not commit .env, litellm-config.yaml, API keys, database files, third-party screenshots, customer workspaces, cookies, or private keys.
