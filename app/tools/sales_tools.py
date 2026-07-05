"""
Herramientas de análisis de ventas — Gestia AI Business Assistant.

Todas las funciones son de solo lectura. Delegan al GestiaApiClient y
devuelven datos estructurados en formato JSON para que el Agente de Ventas
los analice e interprete para el administrador del negocio.

Separación de responsabilidades:
    Agente de Ventas → sales_tools → GestiaApiClient → API REST de Gestia

Integración futura: el GestiaApiClient realizará llamadas HTTP reales a
la API REST de Gestia con autenticación JWT Bearer.
"""

from __future__ import annotations

import json

from app.app_utils.services import get_gestia_client
from app.tools._utils import (
    VALID_SUMMARY_PERIODS,
    VALID_TREND_PERIODS,
    validate_period,
)


def get_sales_summary(business_id: str, period: str = "current_month") -> str:
    """
    Retorna un resumen agregado de ventas para el período indicado.

    Incluye ingresos totales, cantidad de pedidos, ticket promedio,
    categoría más vendida y porcentaje de crecimiento respecto al
    período anterior equivalente (MoM, QoQ o YoY según corresponda).

    Args:
        business_id: Identificador único del negocio (tenant).
        period: Período a analizar. Valores válidos:
                ``'current_month'``, ``'last_month'``,
                ``'current_quarter'``, ``'last_quarter'``,
                ``'current_year'``.

    Returns:
        Cadena JSON con los campos: ``business_id``, ``period``,
        ``total_revenue``, ``total_orders``, ``average_order_value``,
        ``top_category``, ``growth_vs_previous_period`` (porcentaje).

    Raises:
        ValueError: Si ``period`` no es un valor válido.
    """
    validate_period(period, VALID_SUMMARY_PERIODS)
    result = get_gestia_client().get_sales_summary(business_id, period)
    return result.model_dump_json(indent=2)


def get_sales_trends(business_id: str, period: str = "last_6_months") -> str:
    """
    Retorna la serie temporal de ventas para el período indicado.

    Permite identificar estacionalidad, tendencias de crecimiento y
    anomalías en el volumen de ventas a lo largo del tiempo.

    Args:
        business_id: Identificador único del negocio (tenant).
        period: Rango temporal. Valores válidos:
                ``'last_3_months'``, ``'last_6_months'``,
                ``'last_12_months'``, ``'current_year'``.

    Returns:
        Cadena JSON con un array de puntos mensuales. Cada punto contiene:
        ``date`` (formato YYYY-MM), ``revenue`` (ingresos del mes)
        y ``order_count`` (pedidos del mes).

    Raises:
        ValueError: Si ``period`` no es un valor válido.
    """
    validate_period(period, VALID_TREND_PERIODS)
    results = get_gestia_client().get_sales_trends(business_id, period)
    return json.dumps([r.model_dump() for r in results], indent=2, ensure_ascii=False)


def get_sales_by_product(business_id: str, period: str = "current_month") -> str:
    """
    Retorna el desglose de ventas por producto para el período indicado.

    Permite identificar qué productos generaron más ingresos y unidades
    en el período, facilitando decisiones sobre el mix de productos,
    stock y promociones.

    Args:
        business_id: Identificador único del negocio (tenant).
        period: Período a analizar. Valores válidos:
                ``'current_month'``, ``'last_month'``,
                ``'current_quarter'``, ``'last_quarter'``,
                ``'current_year'``.

    Returns:
        Cadena JSON con un array de productos que tuvieron ventas en el
        período. Cada elemento contiene: ``product_id``, ``product_name``,
        ``units_sold`` y ``revenue``.

    Raises:
        ValueError: Si ``period`` no es un valor válido.
    """
    validate_period(period, VALID_SUMMARY_PERIODS)
    results = get_gestia_client().get_sales_by_product(business_id, period)
    return json.dumps([r.model_dump() for r in results], indent=2, ensure_ascii=False)


def get_sales_by_customer(business_id: str, period: str = "current_month") -> str:
    """
    Retorna el desglose de ventas por cliente para el período indicado.

    Permite identificar los clientes más activos y su contribución al
    ingreso total del negocio, útil para acciones de fidelización y
    análisis de concentración de clientes.

    Args:
        business_id: Identificador único del negocio (tenant).
        period: Período a analizar. Valores válidos:
                ``'current_month'``, ``'last_month'``,
                ``'current_quarter'``, ``'last_quarter'``,
                ``'current_year'``.

    Returns:
        Cadena JSON con un array de clientes que compraron en el período.
        Cada elemento contiene: ``customer_id``, ``customer_name``,
        ``total_orders`` y ``total_spent``.

    Raises:
        ValueError: Si ``period`` no es un valor válido.
    """
    validate_period(period, VALID_SUMMARY_PERIODS)
    results = get_gestia_client().get_sales_by_customer(business_id, period)
    return json.dumps([r.model_dump() for r in results], indent=2, ensure_ascii=False)
