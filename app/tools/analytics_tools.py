"""
Herramientas de analítica de negocio — Gestia AI Business Assistant.

Todas las funciones son de solo lectura. Delegan al GestiaApiClient y
devuelven métricas estructuradas en formato JSON para que el Agente de
Analítica las interprete y presente al administrador del negocio.

Separación de responsabilidades:
    Agente de Analítica → analytics_tools → GestiaApiClient → API REST de Gestia

Integración futura: el GestiaApiClient realizará llamadas HTTP reales a
la API REST de Gestia con autenticación JWT Bearer.
"""

from __future__ import annotations

import json

from app.app_utils.services import get_gestia_client
from app.tools._utils import (
    VALID_GRANULARITIES,
    VALID_SUMMARY_PERIODS,
    VALID_TREND_PERIODS,
    validate_period,
)


def get_business_metrics(business_id: str, period: str = "current_month") -> str:
    """
    Retorna los KPIs financieros principales del negocio para el período indicado.

    Proporciona las métricas de salud financiera más importantes: ingresos,
    ganancia bruta, margen bruto, gastos totales, utilidad neta, cantidad
    de pedidos y ticket promedio.

    Args:
        business_id: Identificador único del negocio (tenant).
        period: Período a analizar. Valores válidos:
                ``'current_month'``, ``'last_month'``,
                ``'current_quarter'``, ``'last_quarter'``,
                ``'current_year'``.

    Returns:
        Cadena JSON con los campos: ``business_id``, ``period``,
        ``revenue``, ``gross_profit``, ``gross_margin_pct`` (porcentaje),
        ``total_expenses``, ``net_profit``, ``orders_count``
        y ``average_ticket``.

    Raises:
        ValueError: Si ``period`` no es un valor válido.
    """
    validate_period(period, VALID_SUMMARY_PERIODS)
    result = get_gestia_client().get_business_metrics(business_id, period)
    return result.model_dump_json(indent=2)


def get_revenue_trend(
    business_id: str,
    period: str = "last_6_months",
    granularity: str = "monthly",
) -> str:
    """
    Retorna la serie temporal de ingresos para el período y granularidad indicados.

    Permite identificar patrones de crecimiento, estacionalidad y anomalías
    en la evolución de los ingresos, con distintos niveles de detalle
    según la granularidad seleccionada.

    Args:
        business_id: Identificador único del negocio (tenant).
        period: Rango temporal. Valores válidos:
                ``'last_3_months'``, ``'last_6_months'``,
                ``'last_12_months'``, ``'current_year'``.
        granularity: Frecuencia de los puntos de datos.
                     Valores válidos: ``'weekly'``, ``'monthly'``.

    Returns:
        Cadena JSON con un array de puntos de tendencia. Cada elemento
        contiene: ``label`` (etiqueta del período, por ejemplo "Ene"),
        ``revenue`` (ingresos) y ``orders`` (pedidos).

    Raises:
        ValueError: Si ``period`` o ``granularity`` no son valores válidos.
    """
    validate_period(period, VALID_TREND_PERIODS)
    if granularity not in VALID_GRANULARITIES:
        raise ValueError(
            f"Granularidad inválida: {granularity!r}. "
            f"Valores permitidos: {sorted(VALID_GRANULARITIES)}."
        )
    results = get_gestia_client().get_revenue_trend(business_id, period, granularity)
    return json.dumps([r.model_dump() for r in results], indent=2, ensure_ascii=False)


def get_conversion_metrics(business_id: str, period: str = "current_month") -> str:
    """
    Retorna las métricas de conversión y cumplimiento para el período indicado.

    Incluye la tasa de conversión de presupuesto a pedido, la tasa de
    cumplimiento de pedidos y la tasa de recompra de clientes. Estas métricas
    miden la eficiencia operativa y comercial del negocio.

    Args:
        business_id: Identificador único del negocio (tenant).
        period: Período a analizar. Valores válidos:
                ``'current_month'``, ``'last_month'``,
                ``'current_quarter'``, ``'last_quarter'``,
                ``'current_year'``.

    Returns:
        Cadena JSON con los campos: ``business_id``, ``period``,
        ``quote_to_order_rate`` (% presupuestos convertidos a pedido),
        ``order_to_fulfillment_rate`` (% pedidos entregados) y
        ``repeat_purchase_rate`` (% de clientes que recompraron).

    Raises:
        ValueError: Si ``period`` no es un valor válido.

    Note:
        La API retorna un diccionario en lugar de un modelo tipado.
        Cuando se integre la API real, este método se migrará a un
        modelo ``ConversionMetrics`` en ``app/app_utils/typing.py``.
    """
    validate_period(period, VALID_SUMMARY_PERIODS)
    result = get_gestia_client().get_conversion_metrics(business_id, period)
    return json.dumps(result, indent=2, ensure_ascii=False)


def get_comparative_performance(
    business_id: str,
    period_a: str = "current_month",
    period_b: str = "last_month",
) -> str:
    """
    Retorna una comparación lado a lado de métricas clave entre dos períodos.

    Permite análisis mes a mes (MoM), trimestre a trimestre (QoQ) o año a año
    (YoY) para cualquier par de períodos que el administrador quiera contrastar.
    Incluye la dirección de la tendencia para facilitar la interpretación.

    Args:
        business_id: Identificador único del negocio (tenant).
        period_a: Período principal (más reciente) para la comparación.
                  Valores válidos: ``'current_month'``, ``'last_month'``,
                  ``'current_quarter'``, ``'last_quarter'``,
                  ``'current_year'``.
        period_b: Período de referencia (más antiguo) para la comparación.
                  Valores válidos: los mismos que ``period_a``.

    Returns:
        Cadena JSON con un array de métricas comparadas. Cada elemento
        contiene: ``metric`` (nombre de la métrica), ``period_a_value``,
        ``period_b_value``, ``change_pct`` (variación porcentual) y
        ``trend`` (``'up'``, ``'down'`` o ``'stable'``).

    Raises:
        ValueError: Si ``period_a`` o ``period_b`` no son valores válidos.
    """
    validate_period(period_a, VALID_SUMMARY_PERIODS, "period_a")
    validate_period(period_b, VALID_SUMMARY_PERIODS, "period_b")
    results = get_gestia_client().get_comparative_performance(
        business_id, period_a, period_b
    )
    return json.dumps([r.model_dump() for r in results], indent=2, ensure_ascii=False)
