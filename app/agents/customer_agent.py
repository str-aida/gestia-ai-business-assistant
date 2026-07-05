# ruff: noqa
"""
Customer Agent — Gestia AI Business Assistant.

Analyzes the customer base, segments, top buyers, inactive customers,
and retention metrics. All analysis is read-only.
"""

from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.genai import types

from app.app_utils.prompts import SHARED_AGENT_INSTRUCTIONS
from app.tools.customer_tools import (
    get_customer_overview,
    get_top_customers,
    get_inactive_customers,
    get_customer_segments,
)

_CUSTOMER_INSTRUCTION = """
Eres el Agente de Clientes de Gestia Copilot.

Tu especialidad es analizar la base de clientes para ayudar al administrador
a entender quiénes son sus mejores clientes, detectar riesgos de churn,
y descubrir oportunidades de fidelización y reactivación.

## Áreas de expertise

- Visión general de la base de clientes (crecimiento, retención, churn)
- Identificación de los clientes más valiosos
- Clientes inactivos con potencial de reactivación
- Segmentación de clientes por comportamiento de compra
- Análisis de frecuencia de compra y valor del cliente
- Estrategias de retención y reactivación (solo recomendación, sin ejecución)

## Herramientas disponibles

Usa las herramientas disponibles para obtener datos reales del negocio antes
de responder. Siempre extrae el `business_id` del contexto de la conversación
y pásalo a cada herramienta.

""" + SHARED_AGENT_INSTRUCTIONS

customer_agent = LlmAgent(
    name="customer_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=_CUSTOMER_INSTRUCTION,
    tools=[
        get_customer_overview,
        get_top_customers,
        get_inactive_customers,
        get_customer_segments,
    ],
)
