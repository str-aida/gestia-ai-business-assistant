"""
Herramientas de análisis de clientes — Gestia AI Business Assistant.

Todas las funciones son de solo lectura. Delegan al GestiaApiClient y
devuelven datos estructurados en formato JSON para que el Agente de Clientes
los analice e interprete para el administrador del negocio.

Separación de responsabilidades:
    Agente de Clientes → customer_tools → GestiaApiClient → API REST de Gestia

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


def get_customer_overview(business_id: str) -> str:
    """
    Retorna una vista general de la base de clientes del negocio.

    Proporciona métricas agregadas de alto nivel: total de clientes,
    nuevos clientes en el período actual, clientes recurrentes y
    tasa de churn (porcentaje de clientes perdidos).

    Args:
        business_id: Identificador único del negocio (tenant).

    Returns:
        Cadena JSON con los campos: ``business_id``, ``total_customers``,
        ``new_customers_this_period``, ``returning_customers``
        y ``churn_rate`` (porcentaje).
    """
    result = get_gestia_client().get_customer_overview(business_id)
    return result.model_dump_json(indent=2)


def get_top_customers(
    business_id: str,
    period: str = "current_month",
    limit: int = 5,
) -> str:
    """
    Retorna los clientes de mayor valor para el período indicado.

    Permite identificar a los clientes más importantes del negocio
    tanto por frecuencia de compra como por monto total gastado,
    útil para estrategias de fidelización y atención prioritaria.

    Args:
        business_id: Identificador único del negocio (tenant).
        period: Período a analizar. Valores válidos:
                ``'current_month'``, ``'last_month'``,
                ``'current_quarter'``, ``'last_quarter'``,
                ``'current_year'``.
        limit: Máximo de clientes a retornar. Debe ser un entero
               positivo (valor predeterminado: 5).

    Returns:
        Cadena JSON con un array de hasta ``limit`` clientes ordenados
        por valor. Cada elemento contiene: ``customer_id``, ``name``,
        ``total_orders``, ``total_spent`` y ``last_purchase_date``.

    Raises:
        ValueError: Si ``period`` no es válido o ``limit`` no es positivo.
    """
    validate_period(period, VALID_SUMMARY_PERIODS)
    validate_positive_int(limit, "limit")
    results = get_gestia_client().get_top_customers(business_id, period, limit)
    return json.dumps([r.model_dump() for r in results], indent=2, ensure_ascii=False)


def get_inactive_customers(business_id: str, days_inactive: int = 60) -> str:
    """
    Retorna los clientes que no han realizado compras en el período indicado.

    Permite identificar riesgos de churn y planificar campañas de
    reactivación dirigidas. No modifica ningún dato del negocio.

    Args:
        business_id: Identificador único del negocio (tenant).
        days_inactive: Días consecutivos sin compra para considerar al
                       cliente inactivo. Debe ser un entero positivo
                       (valor predeterminado: 60).

    Returns:
        Cadena JSON con un array de clientes inactivos. Cada elemento
        contiene: ``customer_id``, ``name``, ``total_orders`` (histórico),
        ``total_spent`` (histórico) y ``last_purchase_date``.

    Raises:
        ValueError: Si ``days_inactive`` no es un entero positivo.
    """
    validate_positive_int(days_inactive, "days_inactive")
    results = get_gestia_client().get_inactive_customers(business_id, days_inactive)
    return json.dumps([r.model_dump() for r in results], indent=2, ensure_ascii=False)


def get_customer_segments(business_id: str) -> str:
    """
    Retorna los segmentos de clientes con estadísticas agregadas por grupo.

    Los segmentos se definen según el comportamiento de compra (por ejemplo:
    VIP, regulares, ocasionales, inactivos) y permiten diseñar estrategias
    comerciales diferenciadas para cada grupo.

    Args:
        business_id: Identificador único del negocio (tenant).

    Returns:
        Cadena JSON con un array de segmentos. Cada elemento contiene:
        ``segment_name``, ``customer_count``, ``average_spend``
        y ``description`` (descripción del perfil del segmento).
    """
    results = get_gestia_client().get_customer_segments(business_id)
    return json.dumps([r.model_dump() for r in results], indent=2, ensure_ascii=False)
