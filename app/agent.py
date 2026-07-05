# ruff: noqa
"""
Gestia AI Business Assistant — Root Workflow.

This module defines the complete ADK 2.0 Workflow for the Gestia AI Business
Copilot. It orchestrates intent classification and routing to the correct
domain agent.

Workflow execution order (new message):
    START
      → process_input        (normalize query, inject business context)
            ├─ pending_agent + short reply  → <same domain agent> (resume)
            └─ default                       → intent_classifier
      → intent_classifier    (structured intent detection via LLM)
      → route_intent         (deterministic router; stores pending_agent)
      → <domain_agent>       (one of: sales, products, customers, analytics,
                               insights, general, out_of_scope)

Design notes:
    - process_input is a function node (no LLM call) for fast context injection.
      It also decides whether to resume the last active agent (conversation
      context preservation) or re-run classification (new topic).
    - intent_classifier uses structured output (IntentClassification) to ensure
      reliable, parseable routing decisions.
    - route_intent is a function node that reads the classified intent, stores
      it in ctx.state["pending_agent"], and emits a named route.
    - All domain agents are read-only — no business data is ever modified.
    - business_id is injected at process_input and flows through ctx.state AND
      through ADK’s {{business_id}} instruction interpolation, ensuring strict
      tenant isolation and eliminating all agent prompts for business_id.
"""

import os
from typing import Any

import google.auth
from dotenv import load_dotenv

from google.adk.agents import LlmAgent
from google.adk.agents.context import Context
from google.adk.apps import App
from google.adk.events.event import Event
from google.adk.models import Gemini
from google.adk.workflow import Workflow
from google.genai import types
from pydantic import BaseModel

# Load .env file if present (local development)
load_dotenv()

# ---------------------------------------------------------------------------
# Google Cloud / Vertex AI setup
# ---------------------------------------------------------------------------

try:
    _, project_id = google.auth.default()
    if project_id:
        os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
        os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
        os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")
except Exception:
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"

# ---------------------------------------------------------------------------
# Shared model configuration
# ---------------------------------------------------------------------------

_model = Gemini(
    model="gemini-2.5-flash",
    retry_options=types.HttpRetryOptions(attempts=3),
)

# ---------------------------------------------------------------------------
# Import domain agents (Step 8)
# ---------------------------------------------------------------------------

from app.agents.sales_agent import sales_agent
from app.agents.product_agent import product_agent
from app.agents.customer_agent import customer_agent
from app.agents.analytics_agent import analytics_agent
from app.agents.insights_agent import insights_agent
from app.agents.general_agent import general_agent
from app.agents.out_of_scope_handler import out_of_scope_handler

# ---------------------------------------------------------------------------
# Import utilities
# ---------------------------------------------------------------------------

from app.app_utils.context import get_demo_business_context
from app.app_utils.typing import IntentClassification, BusinessIntent

# ---------------------------------------------------------------------------
# Node 1: Input Processor (function node — no LLM call)
# ---------------------------------------------------------------------------

def process_input(ctx: Context, node_input: Any) -> Event:
    """
    Normalizes the raw user input and injects the business context into
    session state for downstream agents and tools to consume.

    Conversation context: if a domain agent was active in the previous turn
    (stored as ``ctx.state["pending_agent"]``) and the current message is a
    short reply (≤7 words), the workflow skips the intent classifier and routes
    directly back to the same agent.  Longer or new-topic queries always go
    through the classifier so the intent can be re-evaluated.

    Tenant isolation: business_id is extracted here and stored in ctx.state.
    ADK’s instruction templating then substitutes {{business_id}} into every
    domain agent’s system prompt automatically — agents never need to ask the
    user for the business_id.

    Future: Replace get_demo_business_context() with JWT claim extraction
    from the authenticated Gestia request context.
    """
    # --- Extract raw query text ---
    query_text = ""
    if isinstance(node_input, str):
        query_text = node_input
    elif hasattr(node_input, "parts") and node_input.parts:
        query_text = "".join(p.text for p in node_input.parts if hasattr(p, "text") and p.text)
    elif isinstance(node_input, dict) and "text" in node_input:
        query_text = node_input["text"]
    else:
        query_text = str(node_input)

    # --- Inject business context (tenant isolation + ADK instruction interpolation) ---
    business_ctx = get_demo_business_context()
    ctx.state["business_context"] = business_ctx.model_dump()
    ctx.state["business_id"] = business_ctx.business_id
    ctx.state["query_text"] = query_text

    # --- Conversation context: resume pending agent for short follow-up replies ---
    # A short message (≤7 words) after an active agent turn is treated as a
    # follow-up answer (e.g. "current_month", "yes", "last quarter").  Longer
    # messages are always re-classified so the user can switch topics freely.
    pending_agent = ctx.state.get("pending_agent")
    word_count = len(query_text.strip().split())
    if pending_agent and word_count <= 7:
        return Event(output=query_text, route=pending_agent)

    # No pending context or new-topic query — run the intent classifier
    return Event(output=query_text, route="classify")

# ---------------------------------------------------------------------------
# Node 2: Intent Classifier (LLM agent with structured output)
# ---------------------------------------------------------------------------

intent_classifier = LlmAgent(
    name="intent_classifier",
    model=_model,
    instruction="""Eres el clasificador de intenciones de Gestia Copilot, un asistente de negocios para empresas de productos.

Tu única función es analizar la consulta del usuario y determinar a cuál de los siguientes dominios pertenece:

- **sales**: Preguntas operativas sobre ventas, ingresos o facturación de un período específico, sin análisis histórico, comparaciones, métricas ni visualizaciones.
  Incluye: ventas de hoy, ventas de este mes, cuánto facturé en mayo, pedidos recientes, ticket promedio, productos más vendidos, ventas por cliente.
  Ejemplos: "¿cuánto vendí este mes?", "¿cuánto vendí ayer?", "¿cuánto facturé en mayo?", "¿quién me compró más este mes?", "¿cuáles son mis productos más vendidos?".

- **products**: Preguntas sobre el catálogo de productos, disponibilidad de stock, niveles de inventario, atributos de producto (precio, SKU, descripción, categoría).
  Incluye: productos con bajo stock, productos sin stock, stock actual, alertas de inventario, información del catálogo.
  Ejemplos: "¿cuáles son mis productos con menor stock?", "¿qué productos están agotados?", "¿cuántas unidades tengo de X?".

- **customers**: Preguntas sobre clientes, segmentos, retención, clientes inactivos, mejores compradores.

- **analytics**: Preguntas sobre evolución temporal, tendencias, comparaciones entre períodos, KPIs, márgenes, rentabilidad, crecimiento, dashboards, informes y visualizaciones (gráficos, tablas de tendencia).
  Incluye: evolución de ventas, tendencia de ingresos, comparación entre meses o años, métricas del negocio, KPIs, gráficos de ventas, dashboards, crecimiento mensual, análisis de márgenes, rentabilidad por producto, performance histórica.
  Ejemplos: "¿cómo evolucionaron mis ventas en los últimos 6 meses?", "compará mis ventas entre enero y junio", "mostrame un gráfico de ventas", "¿cómo evolucionaron mis ingresos?", "¿cuál fue la tendencia de ventas este año?", "compará mis ventas con el mes pasado".

- **insights**: Preguntas que requieren analizar múltiples áreas del negocio al mismo tiempo para generar recomendaciones estratégicas.

- **general**: Preguntas generales de negocio, explicación de conceptos, preguntas sobre el copilot mismo.

- **out_of_scope**: Cualquier solicitud de modificar datos, eliminar registros, o consultas completamente ajenas al análisis de negocios.

## Regla crítica de desambiguación — Analytics vs Sales

Esta es la distinción MÁS IMPORTANTE del clasificador:

| Concepto | Dominio correcto | Razón |
|---|---|---|
| "¿Cuánto vendí este mes?" | **sales** | Consulta puntual de un período fijo, sin análisis temporal |
| "¿Cómo evolucionaron mis ventas en los últimos 6 meses?" | **analytics** | Requiere análisis de evolución histórica |
| "Mostrame un gráfico de ventas" | **analytics** | Solicita una visualización |
| "Compará mis ventas con el mes pasado" | **analytics** | Comparación entre períodos |
| "¿Cuál fue la tendencia de ventas este año?" | **analytics** | Requiere análisis de tendencia temporal |
| "Mostrame las métricas del negocio" | **analytics** | Solicita KPIs agregados del negocio |
| "Mostrame el dashboard del negocio" | **analytics** | Requiere análisis y visualización |

REGLA DE ORO: Si la consulta contiene cualquiera de estas señales, SIEMPRE clasifica como **analytics**, aunque la pregunta mencione "ventas":
- gráfico, graficar, gráfica, chart, visualización, mostrar visualmente
- evolución, evolucionaron, cómo fue evolucionando
- tendencia, tendencias
- comparar, comparación, compará, comparame
- últimos N meses/semanas/años, a lo largo del tiempo, histórico, historial de tendencia
- crecimiento, creció, rentabilidad, margen
- métricas
- KPI
- KPIs
- dashboard
- tablero

## Regla crítica de desambiguación — Sales vs Products

| Concepto | Dominio correcto | Razón |
|---|---|---|
| Productos más vendidos | **sales** | Se calcula desde el historial de ventas |
| Productos con menor stock / bajo stock | **products** | Se calcula desde el inventario actual |
| Ingresos por producto | **sales** | Dato financiero derivado de transacciones |
| Stock disponible de un producto | **products** | Dato de inventario, no de ventas |

IMPORTANTE: "stock", "inventario", "disponibilidad" y "unidades disponibles" siempre pertenecen a **products**, aunque la pregunta mencione "productos". Nunca los clasifiques como "sales".

Devuelve siempre un JSON con los campos: intent, confidence (0.0 a 1.0), y summary (resumen de la consulta en una oración).""",
    output_schema=IntentClassification,
)

# ---------------------------------------------------------------------------
# Node 3: Intent Router (function node — no LLM call)
# ---------------------------------------------------------------------------

def route_intent(ctx: Context, node_input: Any) -> Event:
    """
    Reads the structured IntentClassification output, persists the resolved
    intent as ``ctx.state["pending_agent"]`` for conversation continuity, and
    emits a named route to direct execution to the appropriate domain agent.
    """
    intent = BusinessIntent.OUT_OF_SCOPE  # safe default

    if isinstance(node_input, dict):
        raw_intent = node_input.get("intent", "out_of_scope")
        try:
            intent = BusinessIntent(raw_intent)
        except ValueError:
            intent = BusinessIntent.OUT_OF_SCOPE
    elif hasattr(node_input, "intent"):
        intent = node_input.intent

    # Persist the active agent so process_input can resume conversation context
    # on the next user turn without re-running intent classification.
    ctx.state["pending_agent"] = intent.value

    query_text = ctx.state.get("query_text", "")
    return Event(output=query_text, route=intent.value)

# ---------------------------------------------------------------------------
# Root Workflow definition
# ---------------------------------------------------------------------------

root_agent = Workflow(
    name="gestia_business_copilot",
    edges=[
        # Entry point: normalize input, inject business context, check conversation state
        ("START", process_input),

        # process_input routes to the intent classifier (new topic / long query)
        # OR directly to a domain agent (short follow-up in an active conversation).
        (process_input, {
            "classify":                           intent_classifier,
            BusinessIntent.SALES.value:           sales_agent,
            BusinessIntent.PRODUCTS.value:        product_agent,
            BusinessIntent.CUSTOMERS.value:       customer_agent,
            BusinessIntent.ANALYTICS.value:       analytics_agent,
            BusinessIntent.INSIGHTS.value:        insights_agent,
            BusinessIntent.GENERAL.value:         general_agent,
            BusinessIntent.OUT_OF_SCOPE.value:    out_of_scope_handler,
        }),

        # Classify the user's intent into a business domain
        (intent_classifier, route_intent),

        # Domain routing map — each route leads to a specialized agent
        (route_intent, {
            BusinessIntent.SALES.value:           sales_agent,
            BusinessIntent.PRODUCTS.value:        product_agent,
            BusinessIntent.CUSTOMERS.value:       customer_agent,
            BusinessIntent.ANALYTICS.value:       analytics_agent,
            BusinessIntent.INSIGHTS.value:        insights_agent,
            BusinessIntent.GENERAL.value:         general_agent,
            BusinessIntent.OUT_OF_SCOPE.value:    out_of_scope_handler,
        }),
    ],
)

# ---------------------------------------------------------------------------
# App container
# ---------------------------------------------------------------------------

app = App(
    root_agent=root_agent,
    name="app",
)
