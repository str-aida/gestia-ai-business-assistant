# ruff: noqa
"""
Out-of-Scope Handler — Gestia AI Business Assistant.

Gracefully declines any request that:
- Asks the assistant to modify, create, or delete business data.
- Is unrelated to business analysis (personal questions, recipes, etc.).
- Could cause unintended autonomous actions.

This is a function node (not an LlmAgent) for deterministic, low-latency
responses that never depend on an LLM call.
"""

from typing import Any

from google.adk.agents.context import Context
from google.adk.events.event import Event
from google.genai import types


def out_of_scope_handler(ctx: Context, node_input: Any):
    """
    Declines out-of-scope or data-modification requests with a clear,
    respectful explanation of the copilot's purpose.

    This is a generator function node that yields Events directly,
    bypassing LLM inference for deterministic, instant responses.
    """
    message = (
        "Lo siento, eso está fuera de lo que puedo hacer. 🙏\n\n"
        "**Gestia Copilot** es un asistente de análisis de negocios. "
        "Mi función es ayudarte a entender tu negocio, detectar oportunidades "
        "y apoyar tus decisiones — pero no puedo modificar información ni "
        "realizar acciones en el sistema.\n\n"
        "Puedo ayudarte con:\n"
        "- 📊 **Ventas** — ¿Cuánto vendí este mes? ¿Cuáles son mis mejores productos?\n"
        "- 📦 **Productos** — ¿Qué productos tienen bajo stock? ¿Cuáles rinden menos?\n"
        "- 👥 **Clientes** — ¿Quiénes son mis mejores clientes? ¿Quiénes están inactivos?\n"
        "- 📈 **Analítica** — ¿Cómo está mi margen? ¿Cómo evolucionaron mis ingresos?\n"
        "- 💡 **Insights** — ¿Qué debería mejorar para crecer?\n\n"
        "¿En qué te puedo ayudar?"
    )

    yield Event(
        content=types.Content(
            role="model",
            parts=[types.Part.from_text(text=message)],
        )
    )
    yield Event(output=message)
