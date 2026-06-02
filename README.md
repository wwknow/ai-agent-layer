# AI Agent Layer

Self-hosted AI Agent Adapter Layer starter template for model routing, automation workers, website inspection, and authorized site reconstruction.

## Status

Alpha / MVP.

This repository provides a basic self-hosted AI Agent Adapter Layer template. It is not a production-ready AI website cloning platform yet.

Current version includes:

* Docker Compose infrastructure
* LiteLLM gateway
* FastAPI Agent API
* PostgreSQL
* Redis
* Model alias routing structure
* Worker folder placeholder
* Safe example configuration files

Not included yet:

* Real provider API keys
* Production authentication
* User accounts
* Quota and billing system
* Playwright worker
* Gemini CLI worker
* Codex worker
* Website screenshot pipeline
* Automatic UI reconstruction
* Automatic visual diff repair
* Production sandbox isolation

## Architecture

```text
SaaS / Admin Panel
        ↓
Agent API
        ↓
LiteLLM Gateway
        ↓
OpenAI / Gemini / Claude / DeepSeek / Qwen / Local Models
        ↓
Worker Layer
        ↓
Playwright / Shell / Docker / Code Generation
```

## Quick Start

Clone the repository:

```bash
git clone https://github.com/wwknow/ai-agent-layer.git
cd ai-agent-layer
```

Create local config files:

```bash
cp .env.example .env
cp litellm-config.example.yaml litellm-config.yaml
```

Edit `.env` and add your own provider API keys:

```env
LITELLM_MASTER_KEY=sk-your-master-key
LITELLM_SALT_KEY=change-this-random-salt
POSTGRES_PASSWORD=change-this-db-password

OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GEMINI_API_KEY=your_gemini_key
DEEPSEEK_API_KEY=your_deepseek_key
QWEN_API_KEY=your_qwen_key
```

Edit `litellm-config.yaml` and replace the example model names with real model names supported by your providers.

Start services:

```bash
docker compose up -d --build
```

Check containers:

```bash
docker compose ps
```

Check Agent API:

```bash
curl http://127.0.0.1:8088/health
```

## Important Notes

The repository does not include real API keys.

You must provide your own API keys and model names before real AI calls can work.

The default example configuration is only a template. It is expected that model calls will fail until valid provider credentials are added.

## Security

Do not commit:

* `.env`
* `litellm-config.yaml`
* API keys
* database files
* third-party screenshots
* customer workspaces
* cookies
* private keys
* generated projects containing private or copyrighted materials

## Intended Use

This project is intended for:

* AI model routing
* self-hosted LLM gateway experiments
* internal automation workers
* authorized website migration
* self-owned site reconstruction
* UI audit automation
* code generation workflows

Do not use this project to copy protected assets, private data, trademarks, copyrighted website materials, or third-party content without permission.

## License

MIT
