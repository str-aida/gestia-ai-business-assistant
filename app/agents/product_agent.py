# ruff: noqa
"""
Product Agent — Gestia AI Business Assistant.

Analyzes the product catalog, stock levels, best/worst sellers, and product mix.
All analysis is read-only. No data modification is ever performed.
"""

from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.genai import types

from app.app_utils.prompts import SHARED_AGENT_INSTRUCTIONS
from app.tools.product_tools import (
    get_product_catalog,
    get_best_selling_products,
    get_worst_selling_products,
    get_low_stock_products,
)

_PRODUCT_INSTRUCTION = """
Eres el Agente de Productos de Gestia Copilot.

Tu especialidad es analizar el catálogo de productos, el inventario y el
rendimiento de ventas por producto para ayudar al administrador a tomar
mejores decisiones sobre su oferta de productos.

## Áreas de expertise

- Análisis del catálogo de productos activos e inactivos
- Productos más vendidos (por unidades y por ingresos)
- Productos con menor desempeño y riesgo de obsolescencia
- Alertas de stock bajo y recomendaciones de reposición
- Mix de productos y análisis de categorías
- Identificación de oportunidades de expansión de catálogo

## Herramientas disponibles

Usa las herramientas disponibles para obtener datos reales del negocio antes
de responder. Siempre extrae el `business_id` del contexto de la conversación
y pásalo a cada herramienta.

""" + SHARED_AGENT_INSTRUCTIONS

product_agent = LlmAgent(
    name="product_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=_PRODUCT_INSTRUCTION,
    tools=[
        get_product_catalog,
        get_best_selling_products,
        get_worst_selling_products,
        get_low_stock_products,
    ],
)
