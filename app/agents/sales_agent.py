# ruff: noqa
"""
Sales Agent — Gestia AI Business Assistant.

Analyzes sales volumes, trends, top/bottom performers, and period comparisons.
All analysis is read-only. No data modification is ever performed.
"""

from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.genai import types

from app.app_utils.prompts import SHARED_AGENT_INSTRUCTIONS
from app.tools.sales_tools import (
    get_sales_summary,
    get_sales_trends,
    get_sales_by_product,
    get_sales_by_customer,
)

_SALES_INSTRUCTION = """
Eres el Agente de Ventas de Gestia Copilot.

Tu especialidad es analizar los datos de ventas del negocio y ayudar al
administrador a entender el rendimiento comercial, identificar tendencias
y detectar oportunidades de mejora.

## Áreas de expertise

- Resúmenes de ventas por período (mes, trimestre, año)
- Tendencias de ventas a lo largo del tiempo
- Comparación entre períodos (MoM, QoQ, YoY)
- Ventas por producto y categoría
- Ventas por cliente
- Análisis de estacionalidad

## Herramientas disponibles

Usa las herramientas disponibles para obtener datos reales del negocio antes
de responder. Siempre extrae el `business_id` del contexto de la conversación
(campo `business_id` en el estado de sesión) y pásalo a cada herramienta.

""" + SHARED_AGENT_INSTRUCTIONS

sales_agent = LlmAgent(
    name="sales_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=_SALES_INSTRUCTION,
    tools=[
        get_sales_summary,
        get_sales_trends,
        get_sales_by_product,
        get_sales_by_customer,
    ],
)
