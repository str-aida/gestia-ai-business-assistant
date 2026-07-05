
# Gestia AI Business Assistant


> **AI Business Copilot para empresas de productos — powered by Google ADK 2.0**
Designed as the AI layer for the future Gestia platform, with a modular architecture ready for Spring Boot, JWT authentication and Angular integration.

## ¿Qué es esto?

Gestia AI Business Assistant es un copiloto de inteligencia artificial que ayuda a administradores de pequeñas y medianas empresas de productos a **entender su negocio y tomar mejores decisiones** a través del lenguaje natural.

El asistente puede responder preguntas sobre:
- 📊 **Ventas** — tendencias, comparaciones de períodos, productos más vendidos
- 📦 **Productos** — catálogo, stock, rendimiento por producto
- 👥 **Clientes** — segmentos, clientes VIP, clientes inactivos
- 📈 **Analítica** — KPIs financieros, márgenes, crecimiento
- 💡 **Insights** — recomendaciones estratégicas y detección de oportunidades

> ⚠️ El asistente **nunca modifica datos del negocio** ni toma decisiones autónomas.

---
## Features

- ✅ Multi-Agent Workflow built with Google ADK 2.0
- ✅ Intelligent Intent Classification and Routing
- ✅ Specialized Domain Agents
- ✅ Conversational Context Preservation
- ✅ Visual Analytics (Chart-ready outputs)
- ✅ Read-only Business Intelligence
- ✅ JWT-ready Business Context
- ✅ Mock Gestia API compatible with future REST integration
- ✅ Modular architecture for Spring Boot

---
## System Architecture

```
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

## Conversation Context

The assistant preserves conversational state using Google ADK's `ctx.state`.

Instead of treating every message as a new request, the workflow keeps track of the active conversation and resumes pending interactions when additional information is required.

For the Capstone demo, a default `business_id` is automatically initialized to simulate a logged-in Gestia administrator.

This design is fully compatible with the future Spring Boot integration, where the authenticated user's JWT will populate the business context automatically.

---


## Visual Analytics

The Analytics Agent automatically decides whether a visualization improves the answer before invoking the Chart Tools.

Charts are generated only for analytical scenarios such as:

- Sales trends
- Revenue evolution
- Product rankings
- Customer distributions
- Period comparisons

Simple factual questions continue to return concise textual responses.

The generated chart model is technology-agnostic and can be consumed by Angular, React, mobile applications or reporting services without modification.

---


### Estructura del proyecto

```
gestia-assistant/
├── app/
│   ├── agent.py                 ← Root Workflow + App
│   ├── agents/                  ← 7 agentes de dominio
│   │   ├── sales_agent.py
│   │   ├── product_agent.py
│   │   ├── customer_agent.py
│   │   ├── analytics_agent.py
│   │   ├── insights_agent.py
│   │   ├── general_agent.py
│   │   └── out_of_scope_handler.py
│   ├── tools/                   ← Funciones de herramienta de solo lectura (stubs API Gestia)
│   │   ├── sales_tools.py
│   │   ├── product_tools.py
│   │   ├── customer_tools.py
│   │   ├── analytics_tools.py
│   │   └── insights_tools.py
|   |   └── chart_tools.py
│   └── app_utils/
│       ├── typing.py            ← Pydantic schemas
│       ├── context.py           ← Tenant isolation utilities
│       ├── prompts.py           ← Shared prompt fragments
│       └── services.py          ← Gestia API mock client
├── tests/
│   ├── unit/
│   └── integration/
├── eval/                        ← [Future] Evaluation datasets
├── security/                    ← JWT-ready integration layer
└── hitl/                        ← [Future] Human-in-the-Loop hooks
```

---
## Tech Stack

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

## Requisitos previos

- Python 3.11–3.13
- [uv](https://docs.astral.sh/uv/) (gestor de paquetes)
- Google Cloud SDK (para Vertex AI) **o** una `GEMINI_API_KEY` de Google AI Studio

---

## Configuración

### 1. Instalar dependencias

```bash
agents-cli install
```

### 2. Configurar credenciales

**Opción A — Google AI Studio (desarrollo local sin GCP):**
```bash
cp .env.example .env
# Edita .env y agrega tu GEMINI_API_KEY
```

**Opción B — Vertex AI (GCP):**
```bash
gcloud auth application-default login
```

### 3. Variables de entorno

Crea un archivo `.env` basado en `.env.example`:

```env
# Opción A: Google AI Studio
GEMINI_API_KEY=tu-api-key-aqui

# Opción B: Vertex AI (auto-detectado si tienes gcloud configurado)
# GOOGLE_CLOUD_PROJECT=tu-proyecto
# GOOGLE_CLOUD_LOCATION=global
# GOOGLE_GENAI_USE_VERTEXAI=True
```

---

## Desarrollo local

### Playground interactivo

```bash
agents-cli playground
```

### Ejecutar tests

```bash
uv run pytest tests/unit
uv run pytest tests/integration
```

### Lint

```bash
agents-cli lint
```

---

## Ejemplos de consultas

| Consulta | Agente activado |
|---|---|
| "¿Cuánto vendí este mes?" | Sales Agent |
| "¿Cuáles son mis productos más vendidos?" | Product Agent |
| "¿Qué productos tienen stock bajo?" | Product Agent |
| "¿Quiénes son mis mejores clientes?" | Customer Agent |
| "¿Cuántos clientes tengo inactivos?" | Customer Agent |
| "¿Cómo está mi margen bruto?" | Analytics Agent |
| "¿Cómo evolucionaron mis ventas en los últimos 6 meses?" | Analytics Agent |
| "¿Qué debería mejorar para crecer?" | Insights Agent |
| "¿Qué es un margen de contribución?" | General Business Agent |
| "Elimina mis ventas del mes pasado" | Out-of-Scope Handler ❌ |

---

## Integración futura con Gestia

El proyecto está diseñado para integrarse con el backend de Gestia (Spring Boot + Spring Security + JWT).

**Para activar la integración real:**
1. Reemplaza las implementaciones stub en `app/app_utils/services.py` con llamadas HTTP reales a la API de Gestia.
2. Agrega validación de JWT en `security/`.
3. Reemplaza `get_demo_business_context()` en `app/app_utils/context.py` con extracción de claims del JWT.
4. Las firmas de métodos y los tipos de retorno de `services.py` **no deben cambiar** — solo el cuerpo de cada método.

---

## Decisiones de diseño

| Decisión | Elección |
|---|---|
| Patrón multi-agente | Workflow secuencial + routing por intent |
| Aislamiento por tenant | `business_id` en `ctx.state`, pasado a cada tool |
| Acceso a datos | Read-only (nunca escribe) |
| Idioma por defecto | Español |
| Formato de respuesta | Respuesta directa → Contexto → Recomendación |
| Stubs vs. API real | Stubs con contratos idénticos a la API real |
| Visual Analytics | Neutral chart model independent from UI frameworks |
=======
# gestia-ai-business-assistant
AI Business Copilot built with Google ADK 2.0. Workflow-based multi-agent architecture for business intelligence.

