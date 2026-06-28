# Hermes Bot

> A specs-driven workspace for a personal AI operations product.

Hermes Bot is a Hermes Agent development workspace for building a dingle-user 
sersonal AI operations system. The current verified implementation is a 
fixture-backed finance research foundation. Telegram delivery, live
providers, Hermes Agent runtime integration, OpenRouter-backed model synthesis,
and AWS deployment remain future milestone work until introduced by accepted
specs.

Rather than becoming one giant prompt, Hermes coordinates specialized agents,
deterministic tools, external APIs, and model-backed synthesis behind explicit
contracts. For model-backed runtime features that arrive in later specs,
OpenRouter is the planned gateway for varied model usage.

---

## Vision

Hermes exists to answer a simple question:

> *"How can one AI assistant coordinate many specialized experts without becoming one giant prompt?"*

Instead of embedding all logic into a single LLM call, Hermes orchestrates multiple agents, deterministic tools, and external APIs to produce grounded, explainable outputs.

The long-term goal is to become a personal AI operating system capable of continuously assisting across multiple domains.

---

## Core Principles

- Agent-first architecture
- Deterministic calculations whenever possible
- LLMs for reasoning, not arithmetic
- Modular and extensible
- Provider agnostic
- Human remains in control

---

# Long-Term Architecture Sketch

The verified foundation starts with deterministic fixture-backed finance report
generation. Telegram, scheduling, live provider integrations, OpenRouter model
routing, and runtime finance sub-agents are deferred to later specs.

```
                        Telegram
                            │
                     FastAPI Webhook
                            │
                   Hermes Orchestrator
                            │
          Intent Planner / Task Scheduler
                            │
 ┌──────────────────────────┴──────────────────────────┐
 │                                                     │
Finance Agent                                     Future Agents
 │                                                     │
 ├─────────────┬──────────────┬───────────────┐        │
 │             │              │               │        │
News Agent   Price Agent   Valuation Agent  Risk Agent │
 │             │              │               │        │
Market News  Price APIs    Fundamentals     Macro      │
Filings      OHLCV         Multiples        Earnings   │
Earnings     Indicators    Fair Value       Thesis     │
Sentiment    Support/Res   Margin Safety    Risks      │
 └─────────────┴──────────────┴───────────────┘        │
                            │
                    Chief Analyst
                            │
              Deterministic Finance Report
                            │
           Optional OpenRouter Model Gateway
                            │
       Qwen • Kimi • DeepSeek • GPT • Claude • ...
```

---

# Current Roadmap

- `docs/milestones/0001-finance-agent-foundation.md`: Verified
  fixture-backed finance foundation.
- `docs/milestones/0002-runtime-service-boundary.md`: Accepted local FastAPI
  runtime boundary.
- `docs/milestones/0003-finance-evidence-provider-contract.md`: Draft
  provider-neutral evidence adapter contract.
- `docs/milestones/0004-live-finance-provider-integration.md`: Draft first
  live finance provider integration.
- `docs/milestones/0005-openrouter-model-routing-boundary.md`: Draft
  OpenRouter model gateway boundary.
- `docs/milestones/0006-hermes-agent-runtime-integration.md`: Draft Hermes
  Agent runtime integration.
- `docs/milestones/0007-telegram-delivery-foundation.md`: Draft Telegram
  delivery foundation.
- `docs/milestones/0008-persistence-watchlists-and-scheduling.md`: Draft
  personal persistence, watchlists, and scheduling.
- `docs/milestones/0009-containerization-and-runtime-config.md`: Draft
  containerization and runtime config.
- `docs/milestones/0010-aws-ec2-deployment-foundation.md`: Draft AWS EC2
  deployment foundation.
- `docs/milestones/0011-production-operations-hardening.md`: Draft operations
  hardening.

Future roadmap work should be introduced as individual milestone files under
`docs/milestones/`, not as one consolidated roadmap handoff.


---

# Technology Stack

Backend

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic

AI

- Hermes
- OpenRouter for future model-backed runtime features

Infrastructure

- AWS EC2 as future deployment target
- Docker as future runtime packaging target

Messaging

- Telegram Bot API as future delivery channel

Memory

- PostgreSQL
- pgvector

---

# Design Philosophy

Hermes separates reasoning from execution.

```
LLM

↓

Plan

↓

Call deterministic tools

↓

Collect evidence

↓

Reason over evidence

↓

Produce recommendation
```

The language model never becomes the source of truth.

Instead, it explains, synthesises and reasons over trusted information produced
by deterministic systems. In finance workflows, deterministic tools and
validated evidence remain the source of price, market, news, score, and
strategy claims.

---

# Future Example Workflow

```
User

↓

/research NVDA

↓

Hermes

↓

News Agent

↓

Financial Data

↓

Technical Analysis

↓

Risk Assessment

↓

Chief Analyst

↓

Telegram Report
```

---

# Example Response

```
NVIDIA (NVDA)

Current Price
$171.82

Research-Only Pullback Zone

Candidate zone from supplied fixture data
$165–168

Investment Thesis

• AI demand remains strong
• Datacenter revenue continues to expand
• Valuation remains above historical average
• Recent pullback driven by macro sentiment rather than company fundamentals

Risks

• Export restrictions
• High valuation
• Increased competition

Limitations

This is a research-only pullback zone, not personalized financial advice or a
trade instruction.
```

---

# Why Hermes?

Most AI assistants answer questions.

Hermes completes workflows.

Instead of asking a single model to "figure everything out", Hermes coordinates specialised agents, deterministic software, APIs and language models into one coherent system.

---

# Repository Status

🚧 Active Development

This project is being built as a long-term personal AI platform and AI engineering portfolio, with an emphasis on agent orchestration, production-quality software engineering, and practical daily utility.
