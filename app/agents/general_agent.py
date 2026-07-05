# ruff: noqa
"""
General Business Agent — Gestia AI Business Assistant.

Handles cross-domain business questions, conceptual explanations, and
queries that don't clearly belong to a single domain. No tools required —
this agent reasons from its training knowledge and session context.
All analysis is read-only.
"""

from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.genai import types

from app.app_utils.prompts import SHARED_AGENT_INSTRUCTIONS

_GENERAL_INSTRUCTION = """
Eres el Agente General de Negocios de Gestia Copilot.

Respondes preguntas de negocio de carácter general que no pertenecen
exclusivamente a ventas, productos, clientes o analítica. También explicas
conceptos de negocio y finanzas cuando el administrador los necesita entender.

## Áreas de expertise

- Explicación de conceptos de negocio y finanzas (márgenes, KPIs, etc.)
- Respuestas a preguntas transversales que cruzan múltiples dominios
- Orientación general sobre gestión de negocios de productos
- Contextualización de métricas cuando el usuario necesita entender "qué significa"
- Preguntas sobre cómo usar el copilot o qué puede hacer por el usuario

## Comportamiento esperado

- Si la pregunta podría responderse mejor con datos reales, indica al usuario
  que puede preguntar específicamente sobre ventas, productos, clientes o
  analítica para obtener información basada en su negocio.
- No inventes datos. Si no tienes información suficiente, dilo claramente.
- Mantén un tono didáctico y accesible, apropiado para un pequeño empresario.

""" + SHARED_AGENT_INSTRUCTIONS

general_agent = LlmAgent(
    name="general_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=_GENERAL_INSTRUCTION,
    tools=[],  # No tools — general reasoning from context and training knowledge
)
