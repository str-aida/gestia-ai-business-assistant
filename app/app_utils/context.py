# ruff: noqa
"""
Tenant context utilities for the Gestia AI Business Assistant.

Responsibilities:
- Build a BusinessContext from session state or request metadata.
- Extract and validate business_id for tenant isolation.
- Provide a default demo BusinessContext (pastry business) for local testing.

Future integration note:
  In production, business_id and BusinessContext metadata will be injected
  from the validated JWT claims provided by the Gestia Spring Boot API.
  Replace `get_demo_business_context()` with a JWT-parsing utility.
"""

from app.app_utils.typing import BusinessContext


# ---------------------------------------------------------------------------
# Demo business context (used during local development and Capstone demo)
# ---------------------------------------------------------------------------

DEMO_BUSINESS_CONTEXT = BusinessContext(
    business_id="demo-pastry-001",
    business_name="La Pastelería Artesanal",
    business_type="bakery",
    currency="ARS",
    locale="es-AR",
    timezone="America/Argentina/Buenos_Aires",
)


def get_demo_business_context() -> BusinessContext:
    """
    Returns the demo BusinessContext for the Capstone pastry business.

    Future: Replace with JWT claim extraction from the authenticated request.
    """
    return DEMO_BUSINESS_CONTEXT


def extract_business_context(state: dict) -> BusinessContext:
    """
    Extracts the BusinessContext from session state.

    Args:
        state: The ADK context state dictionary (ctx.state).

    Returns:
        BusinessContext for the current tenant session.

    Raises:
        ValueError: If no business context is found in state.

    Future: Validate business_id against a whitelist or the Gestia tenant registry.
    """
    ctx_data = state.get("business_context")
    if ctx_data is None:
        # Fallback to demo context for local/dev runs
        return DEMO_BUSINESS_CONTEXT
    if isinstance(ctx_data, BusinessContext):
        return ctx_data
    return BusinessContext(**ctx_data)


def get_business_id(state: dict) -> str:
    """
    Convenience helper to extract just the business_id from session state.

    Args:
        state: The ADK context state dictionary (ctx.state).

    Returns:
        The business_id string for tenant-scoped tool calls.
    """
    return extract_business_context(state).business_id
