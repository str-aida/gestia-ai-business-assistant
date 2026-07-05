"""
Herramientas de insights estratégicos — Gestia AI Business Assistant.

Todas las funciones son de solo lectura. Delegan al GestiaApiClient y
retornan contexto agregado del negocio para que el Agente de Insights
genere recomendaciones estratégicas cruzando múltiples dominios.

Separación de responsabilidades:
    Agente de Insights → insights_tools → GestiaApiClient → API REST de Gestia

Integración futura: el GestiaApiClient realizará llamadas HTTP reales a
la API REST de Gestia con autenticación JWT Bearer.
"""

from __future__ import annotations

import json

from app.app_utils.services import get_gestia_client


def get_business_context(business_id: str) -> str:
    """
    Retorna un snapshot completo del negocio para el razonamiento estratégico.

    Agrega datos de múltiples dominios (ventas, productos, clientes) en un
    único objeto de contexto. El Agente de Insights utiliza este snapshot
    para generar recomendaciones cruzadas sin necesidad de llamar a cada
    dominio por separado. Las alertas activas están incluidas en el snapshot.

    Args:
        business_id: Identificador único del negocio (tenant).

    Returns:
        Cadena JSON con los campos: ``business_id``, ``business_name``,
        ``period``, ``revenue``, ``top_product``, ``top_customer``,
        ``low_stock_count``, ``inactive_customer_count``,
        ``alerts`` (array de alertas activas) y ``growth_trend``
        (``'growing'``, ``'stable'`` o ``'declining'``).
    """
    result = get_gestia_client().get_business_context(business_id)
    return result.model_dump_json(indent=2)


def get_business_alerts(business_id: str) -> str:
    """
    Retorna las alertas activas y anomalías detectadas en el negocio.

    Las alertas representan violaciones de umbrales o patrones que requieren
    atención inmediata, como stock crítico, caídas de ingresos inusuales
    o concentración de clientes inactivos.

    El Agente de Insights debe priorizar la respuesta a estas alertas cuando
    estén presentes, explicando el impacto potencial y proponiendo acciones
    concretas y realizables.

    Args:
        business_id: Identificador único del negocio (tenant).

    Returns:
        Cadena JSON con un array de alertas. Cada elemento contiene:
        ``alert_id``, ``severity`` (``'high'``, ``'medium'`` o ``'low'``),
        ``category``, ``title``, ``description`` y ``recommended_action``.
        Retorna un array vacío si no hay alertas activas.
    """
    results = get_gestia_client().get_business_alerts(business_id)
    return json.dumps([r.model_dump() for r in results], indent=2, ensure_ascii=False)
