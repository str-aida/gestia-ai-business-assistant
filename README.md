# Gestia AI Business Assistant

> **AI Business Copilot for product-based businesses — powered by Google ADK 2.0**

Designed as the AI layer for the future Gestia platform, featuring a modular workflow-based architecture ready for Spring Boot, JWT authentication, and Angular integration.

---

# Overview

Gestia AI Business Assistant is an AI copilot that helps administrators of small and medium-sized product-based businesses understand their business and make better decisions using natural language.

The assistant can answer questions about:

- 📊 **Sales** — revenue, trends, period comparisons, best-selling products
- 📦 **Products** — catalog, inventory, stock levels and product performance
- 👥 **Customers** — customer segmentation, VIP customers and inactive customers
- 📈 **Analytics** — KPIs, profitability, margins and business performance
- 💡 **Insights** — strategic recommendations and business opportunities

> ⚠️ The assistant is strictly **read-only**. It never modifies business data or makes autonomous business decisions.

---

# Features

- ✅ Multi-Agent Workflow built with Google ADK 2.0
- ✅ Intelligent Intent Classification and Routing
- ✅ Specialized Domain Agents
- ✅ Conversational Context Preservation
- ✅ Visual Analytics (Chart-ready outputs)
- ✅ Read-only Business Intelligence
- ✅ JWT-ready Business Context
- ✅ Mock Gestia API compatible with future REST integration
- ✅ Modular architecture prepared for Spring Boot integration

---

# System Architecture

```text
                           User Query
                                │
                                ▼
                        process_input
                                │
               ┌────────────────┴────────────────┐
               │                                 │
      Pending conversation?                 New request
               │                                 │
               ▼                                 ▼
      Resume previous agent             intent_classifier
               │                                 │
               └───────────────┬─────────────────┘
                               ▼
                         route_intent
                               │
      ┌──────────┬──────────┬──────────┬──────────┬──────────┬──────────┐
      ▼          ▼          ▼          ▼          ▼          ▼
   Sales      Products   Customers  Analytics  Insights   General
      │                                  │
      │                                  ▼
      │                        Analytics Tools
      │                                  │
      │                                  ▼
      │                           Chart Tools
      │                                  │
      └──────────────────────────────────┘
                     │
                     ▼
          Gestia API (Mock → Future REST API)
```

---

# Conversation Context

The assistant preserves conversational context using Google ADK's `ctx.state`.

Instead of treating every message as a new request, the workflow keeps track of the active conversation and resumes pending interactions whenever additional information is required.

For the Capstone demo, a default `business_id` is automatically initialized to simulate an authenticated Gestia administrator.

This design is fully compatible with the future Spring Boot integration, where the authenticated user's JWT will automatically populate the business context.

---

# Visual Analytics

The Analytics Agent automatically decides whether a visualization improves the response before invoking the Chart Tools.

Charts are generated only for analytical scenarios such as:

- Sales trends
- Revenue evolution
- Product rankings
- Customer distributions
- Period comparisons

Simple factual questions continue to return concise textual responses.

The generated chart model is technology-agnostic and can be consumed directly by Angular, React, mobile applications or reporting services without modification.

---

# Project Structure

```text
gestia-assistant/
├── app/
│   ├── agent.py                 ← Root workflow and application entry point
│   ├── agents/
│   │   ├── sales_agent.py
│   │   ├── product_agent.py
│   │   ├── customer_agent.py
│   │   ├── analytics_agent.py
│   │   ├── insights_agent.py
│   │   ├── general_agent.py
│   │   └── out_of_scope_handler.py
│   ├── tools/                   ← Read-only business tools
│   │   ├── sales_tools.py
│   │   ├── product_tools.py
│   │   ├── customer_tools.py
│   │   ├── analytics_tools.py
│   │   ├── insights_tools.py
│   │   ├── chart_tools.py
│   │   └── ...
│   └── app_utils/
│       ├── typing.py
│       ├── context.py
│       ├── prompts.py
│       └── services.py
├── tests/
│   ├── unit/
│   └── integration/
├── eval/                        ← Future evaluation datasets
├── security/                    ← JWT-ready integration layer
└── hitl/                        ← Future Human-in-the-Loop hooks
```

---

# Tech Stack

| Layer | Technology |
|--------|------------|
| AI Framework | Google ADK 2.0 |
| LLM | Gemini 2.5 Flash |
| Language | Python 3.11+ |
| Validation | Pydantic |
| Package Manager | uv |
| Future Backend | Spring Boot |
| Future Authentication | Spring Security + JWT |
| Future Frontend | Angular |

---

# Prerequisites

- Python 3.11–3.13
- `uv` package manager
- Google Cloud SDK (Vertex AI) **or** a Google AI Studio `GEMINI_API_KEY`

---

# Setup

## 1. Install dependencies

```bash
agents-cli install
```

## 2. Configure credentials

### Option A — Google AI Studio

```bash
cp .env.example .env
```

Then edit the `.env` file and add your API key.

### Option B — Vertex AI

```bash
gcloud auth application-default login
```

## 3. Environment variables

Create a `.env` file based on `.env.example`.

```env
GEMINI_API_KEY=your-api-key

# Vertex AI
# GOOGLE_CLOUD_PROJECT=your-project
# GOOGLE_CLOUD_LOCATION=global
# GOOGLE_GENAI_USE_VERTEXAI=True
```

---

# Local Development

## Interactive Playground

```bash
agents-cli playground
```

## Run Tests

```bash
uv run pytest tests/unit
uv run pytest tests/integration
```

## Lint

```bash
agents-cli lint
```

---

# Example Queries

| User Query | Routed Agent |
|------------|--------------|
| How much did I sell this month? | Sales Agent |
| Which products are my best sellers? | Sales Agent |
| Which products have low stock? | Product Agent |
| Who are my best customers? | Customer Agent |
| How many inactive customers do I have? | Customer Agent |
| What is my gross margin? | Analytics Agent |
| How have my sales evolved over the last six months? | Analytics Agent |
| What should I improve to grow? | Insights Agent |
| What is contribution margin? | General Business Agent |
| Delete last month's sales | Out-of-Scope Handler ❌ |

---

# Future Integration with Gestia

The project is designed to integrate seamlessly with the future Gestia backend (Spring Boot + Spring Security + JWT).

To activate the production integration:

1. Replace the stub implementations in `app/app_utils/services.py` with real HTTP calls.
2. Add JWT validation inside the `security/` module.
3. Replace `get_demo_business_context()` with JWT claim extraction.
4. Keep all service interfaces and return types unchanged.

---

# Design Decisions

| Decision | Choice |
|----------|--------|
| Multi-agent architecture | Sequential workflow with intent routing |
| Tenant isolation | `business_id` stored in `ctx.state` |
| Data access | Read-only |
| Default language | Spanish |
| Response format | Direct Answer → Business Context → Actionable Recommendation |
| API integration | Mock services with production-compatible contracts |
| Visual Analytics | Neutral chart model independent from UI frameworks |