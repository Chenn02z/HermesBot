# Hermes Bot

> A specs-driven workspace for a personal finance research agent product.

Hermes Bot is a specs-driven workspace for building a single-user personal
finance research system. The current verified implementation is a fixture-backed
finance research foundation. Telegram delivery (push + on-demand), live
providers, OpenRouter-backed news synthesis, and AWS deployment remain future
milestone work until introduced by accepted specs.

Rather than becoming one giant prompt, HermesBot coordinates specialized agents,
deterministic tools, external APIs, and model-backed synthesis behind explicit
contracts. For model-backed runtime features that arrive in later specs,
OpenRouter is the planned gateway for varied model usage.

The runtime product direction is inspired by multi-agent trading research
systems: analyst-style agents gather and debate market evidence, while the
final output remains research-only. HermesBot may provide suggested research
entry prices or entry zones, but it must not execute trades, size positions,
track trades, guarantee outcomes, or present personalized financial advice.

---

## Vision

HermesBot exists to answer a simple question:

> *"How can one AI assistant coordinate many specialized experts without becoming one giant prompt?"*

Instead of embedding all logic into a single LLM call, HermesBot orchestrates multiple agents, deterministic tools, and external APIs to produce grounded, explainable outputs.

The long-term goal is to become a personal finance research system capable of
continuous market monitoring, evidence gathering, and research synthesis,
delivered through Telegram as the primary interface — both on-demand commands
and push delivery (morning brief and event-driven alerts).

## User Experience

- **On-demand**: `/research NVDA`, `/brief TSLA MSFT`, `/watch add NVDA`
- **Push — Morning brief**: once per day on US market clock, a single
  aggregated Telegram message covering macro conditions and a one-line
  status per watchlist ticker.
- **Push — Event-driven alerts**: per-ticker alerts when a price threshold
  is crossed or a transparent "good buy" composite score (technical +
  fundamental + news) triggers.

---

## Core Principles

- Agent-first architecture
- Deterministic calculations whenever possible
- LLMs for reasoning and news synthesis, not arithmetic or price claims
- Transparent scoring — no black-box verdicts
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
                     (primary interface)
                            │
                     FastAPI Webhook
                            │
                  Product Orchestrator
                            │
          Intent Router / Task Scheduler
                            │
 ┌──────────────────────────┴──────────────────────────┐
 │                                                     │
Finance Research Agent                           Future Agents
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
       Research Report + Suggested Entry Price/Zone
       + Transparent Composite Score (T/F/N)
                            │
              OpenRouter Model Gateway
        (news synthesis + confidence calibration)
                            │
       Qwen • Kimi • DeepSeek • GPT • Claude • ...
```

---

# Current Roadmap

- `docs/milestones/0001-finance-agent-foundation.md`: Verified
  fixture-backed finance foundation.
- `docs/milestones/0002-runtime-service-boundary.md`: Verified local FastAPI
  runtime boundary.
- `docs/milestones/0003-finance-evidence-provider-contract.md`: Accepted
  provider-neutral evidence adapter contract.
- `docs/milestones/0004-live-finance-provider-integration.md`: Accepted first
  live finance provider integration (AlphaVantage).
- `docs/milestones/0005-openrouter-model-routing-boundary.md`: Accepted
  OpenRouter model gateway boundary.
- `docs/milestones/0007-telegram-delivery-foundation.md`: Draft Telegram
  delivery foundation (push + on-demand).
- `docs/milestones/0008-persistence-watchlists-and-scheduling.md`: Draft
  personal persistence, watchlists, scheduling, and alert triggers.
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

- OpenRouter for future model-backed runtime features (news synthesis and
  confidence calibration)

Infrastructure

- AWS EC2 as future deployment target
- Docker as future runtime packaging target

Messaging

- Telegram Bot API as future delivery channel (push + on-demand)

Memory

- PostgreSQL

---

# Design Philosophy

HermesBot separates reasoning from execution.

```
LLM (news synthesis, confidence calibration)

↓

Plan (deterministic tools own prices, scores, data)

↓

Call deterministic tools + live providers

↓

Collect evidence across sources

↓

Score transparently (technical + fundamental + news)

↓

Synthesize via model

↓

Produce recommendation + composite score

↓

Deliver via Telegram (push or on-demand)
```

The language model never becomes the source of truth.

Instead, it synthesizes and reasons over trusted information produced
by deterministic systems. In finance workflows, deterministic tools and
validated evidence remain the source of price, market, score, and
strategy claims. The model's role is news synthesis (connecting macro +
company-specific narratives) and confidence calibration across sources.

---

# Future Example Workflows

**On-demand:**
```
User
  ↓
/research NVDA
  ↓
HermesBot: price + technicals + fundamentals + news synthesis
  ↓
Transparent composite score + suggested entry zone
  ↓
Telegram Report
```

**Push — Morning Brief (once daily, US market clock):**
```
Scheduler triggers
  ↓
Iterate watchlist: price checks + news scan
  ↓
Aggregate: macro summary + one-line per ticker
  ↓
Single Telegram message
```

**Push — Event-driven alert:**
```
Price threshold crossed or "good buy" score fires
  ↓
Per-ticker alert message via Telegram
```

---

# Example Response

## On-demand research report
```
NVIDIA (NVDA)

Current Price
$171.82

Suggested Research Entry

Suggested entry price from supplied fixture data
$166.50

Candidate entry zone from supplied fixture data
$165–168

Composite Score: 6.7/10
Technical: 7/10 (MA crossover + volume confirmation)
Fundamental: 5/10 (P/E above sector, high valuation)
News: 8/10 (positive AI sentiment, datacenter expansion)

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

This is a research-only suggested entry price and zone, not personalized
financial advice, position sizing, or a trade instruction.
```

## Morning brief (aggregated, once daily)
```
Morning Brief — Tue, 1 Jul 2025

US markets closed mixed. S&P flat, Nasdaq +0.3%. Fed minutes signal patience.

Your watchlist:
NVDA $171.82 • Entry zone $165–168 • Score 6.7/10 • No change
TSLA $258.40 • Approaching resistance at $260 • Score 5.1/10
META $512.10 • Strong momentum, above entry zone • Score 7.2/10
```

## Event-driven alert
```
NVDA crossed below $170 • Now $169.41
Entry zone $165–168 is approaching.
Composite score: 6.7/10 (T:7 F:5 N:8)
```

---

# Why HermesBot?

Most AI assistants answer questions.

HermesBot completes workflows.

Instead of asking a single model to "figure everything out", HermesBot coordinates specialised agents, deterministic software, APIs and language models into one coherent system — and delivers the result to your phone, on your schedule.

---

# Repository Status

🚧 Active Development

This project is being built as a long-term personal AI platform and AI engineering portfolio, with an emphasis on agent orchestration, production-quality software engineering, and practical daily utility.
