"""
Utilidades internas compartidas para los módulos de herramientas.

Módulo privado — solo para uso dentro del paquete app/tools/.
Centraliza constantes de validación y funciones auxiliares para
evitar duplicación entre los distintos módulos de herramientas.
"""

from __future__ import annotations

from typing import Final

# ---------------------------------------------------------------------------
# Períodos válidos por tipo de consulta
# ---------------------------------------------------------------------------

#: Períodos válidos para resúmenes, desgloses y comparaciones.
VALID_SUMMARY_PERIODS: Final[frozenset[str]] = frozenset({
    "current_month",
    "last_month",
    "current_quarter",
    "last_quarter",
    "current_year",
})

#: Períodos válidos para series de tendencias temporales.
VALID_TREND_PERIODS: Final[frozenset[str]] = frozenset({
    "last_3_months",
    "last_6_months",
    "last_12_months",
    "current_year",
})

#: Granularidades válidas para el desglose de tendencias de ingresos.
VALID_GRANULARITIES: Final[frozenset[str]] = frozenset({
    "weekly",
    "monthly",
})


# ---------------------------------------------------------------------------
# Validadores de parámetros
# ---------------------------------------------------------------------------

def validate_period(period: str, valid: frozenset[str], param: str = "period") -> None:
    """
    Verifica que el período sea uno de los valores permitidos.

    Args:
        period: Valor del período a validar.
        valid: Conjunto de valores válidos.
        param: Nombre del parámetro (usado en el mensaje de error).

    Raises:
        ValueError: Si el período no está en el conjunto de valores válidos.
    """
    if period not in valid:
        raise ValueError(
            f"Período inválido para '{param}': {period!r}. "
            f"Valores permitidos: {sorted(valid)}."
        )


def validate_positive_int(value: int, param: str) -> None:
    """
    Verifica que el valor entero sea mayor que cero.

    Args:
        value: Valor a validar.
        param: Nombre del parámetro (usado en el mensaje de error).

    Raises:
        ValueError: Si el valor no es un entero positivo.
    """
    if not isinstance(value, int) or value < 1:
        raise ValueError(
            f"'{param}' debe ser un entero positivo (recibido: {value!r})."
        )
