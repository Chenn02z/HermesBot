# Hermes Bot

> Your personal AI operations platform.

Hermes is a Telegram-native AI orchestrator that coordinates specialized agents for personal use cases

Rather than being a single chatbot, Hermes acts as an operating system for AI agents. It receives requests, plans workflows, delegates work to the appropriate agents, synthesizes results using frontier and open-source language models, and delivers concise, actionable responses through Telegram.

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

# Architecture

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
                    Telegram Report
                            │
                   OpenRouter Gateway
                            │
       Qwen • Kimi • DeepSeek • GPT • Claude • ...
```

---

# Current Roadmap

## Phase 1

Finance Agent

- Responsible for producing entry-price analysis and market updates
- Telegram interface
- Hermes orchestration
- OpenRouter integration
- It can delegate internally to specialised finance sub-agents:
    - News Agent
    - Price Agent
    - Valuation Agent
    - Risk Agent
    - Chief Analyst


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
- OpenRouter

Infrastructure

- AWS EC2
- Docker

Messaging

- Telegram Bot API

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

Instead, it explains, synthesises and reasons over trusted information produced by deterministic systems.

---

# Example Workflow

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

Suggested Buy Zones

Starter
$165–168

Strong Conviction
$155–160

Investment Thesis

• AI demand remains strong
• Datacenter revenue continues to expand
• Valuation remains above historical average
• Recent pullback driven by macro sentiment rather than company fundamentals

Risks

• Export restrictions
• High valuation
• Increased competition

Action

Wait for pullback towards the first buy zone.
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