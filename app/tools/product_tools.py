"""
Herramientas de análisis de productos — Gestia AI Business Assistant.

Todas las funciones son de solo lectura. Delegan al GestiaApiClient y
devuelven datos estructurados en formato JSON para que el Agente de Productos
los analice e interprete para el administrador del negocio.

Separación de responsabilidades:
    Agente de Productos → product_tools → GestiaApiClient → API REST de Gestia

Integración futura: el GestiaApiClient realizará llamadas HTTP reales a
la API REST de Gestia con autenticación JWT Bearer.
"""

from __future__ import annotations

import json

from app.app_utils.services import get_gestia_client
from app.tools._utils import (
    VALID_SUMMARY_PERIODS,
    validate_period,
    validate_positive_int,
)


def get_product_catalog(business_id: str) -> str:
    """
    Retorna el catálogo completo de productos del negocio.

    Incluye todos los productos (activos e inactivos) con su precio,
    stock actual y categoría. Útil para obtener una visión integral
    del surtido disponible.

    Args:
        business_id: Identificador único del negocio (tenant).

    Returns:
        Cadena JSON con un array de productos. Cada elemento contiene:
        ``product_id``, ``name``, ``category``, ``price``,
        ``stock`` y ``is_active``.
    """
    results = get_gestia_client().get_product_catalog(business_id)
    return json.dumps([r.model_dump() for r in results], indent=2, ensure_ascii=False)


def get_best_selling_products(
    business_id: str,
    period: str = "current_month",
    limit: int = 5,
) -> str:
    """
    Retorna los productos más vendidos por ingresos en el período indicado.

    Permite identificar los productos estrella del negocio para
    tomar decisiones sobre inventario prioritario, destacados en
    catálogo y estrategias de promoción.

    Args:
        business_id: Identificador único del negocio (tenant).
        period: Período a analizar. Valores válidos:
                ``'current_month'``, ``'last_month'``,
                ``'current_quarter'``, ``'last_quarter'``,
                ``'current_year'``.
        limit: Máximo de productos a retornar. Debe ser un entero
               positivo (valor predeterminado: 5).

    Returns:
        Cadena JSON con un array de hasta ``limit`` productos ordenados
        por ingresos. Cada elemento contiene: ``product_id``,
        ``product_name``, ``units_sold``, ``revenue`` y ``rank``.

    Raises:
        ValueError: Si ``period`` no es válido o ``limit`` no es positivo.
    """
    validate_period(period, VALID_SUMMARY_PERIODS)
    validate_positive_int(limit, "limit")
    results = get_gestia_client().get_best_selling_products(business_id, period, limit)
    return json.dumps([r.model_dump() for r in results], indent=2, ensure_ascii=False)


def get_worst_selling_products(
    business_id: str,
    period: str = "current_month",
    limit: int = 5,
) -> str:
    """
    Retorna los productos con menor desempeño de ventas en el período indicado.

    Permite identificar productos en riesgo de obsolescencia o con baja
    rotación, candidatos a ajustes de precio, promoción o discontinuación.

    Args:
        business_id: Identificador único del negocio (tenant).
        period: Período a analizar. Valores válidos:
                ``'current_month'``, ``'last_month'``,
                ``'current_quarter'``, ``'last_quarter'``,
                ``'current_year'``.
        limit: Máximo de productos a retornar. Debe ser un entero
               positivo (valor predeterminado: 5).

    Returns:
        Cadena JSON con un array de hasta ``limit`` productos ordenados
        por menor desempeño. Cada elemento contiene: ``product_id``,
        ``product_name``, ``units_sold``, ``revenue`` y ``rank``.

    Raises:
        ValueError: Si ``period`` no es válido o ``limit`` no es positivo.
    """
    validate_period(period, VALID_SUMMARY_PERIODS)
    validate_positive_int(limit, "limit")
    results = get_gestia_client().get_worst_selling_products(business_id, period, limit)
    return json.dumps([r.model_dump() for r in results], indent=2, ensure_ascii=False)


def get_low_stock_products(business_id: str) -> str:
    """
    Retorna los productos cuyo stock actual está en o por debajo del umbral de reorden.

    Permite tomar acción preventiva antes de que ocurra un quiebre de
    stock que pueda afectar ventas o la experiencia del cliente.

    Args:
        business_id: Identificador único del negocio (tenant).

    Returns:
        Cadena JSON con un array de productos con stock crítico. Cada
        elemento contiene: ``product_id``, ``product_name``,
        ``current_stock`` y ``reorder_threshold``.
        Retorna un array vacío si todos los productos están bien abastecidos.
    """
    results = get_gestia_client().get_low_stock_products(business_id)
    return json.dumps([r.model_dump() for r in results], indent=2, ensure_ascii=False)
