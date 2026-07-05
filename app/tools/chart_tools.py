# ruff: noqa
"""
Chart Tools — Gestia AI Business Assistant.

Transforms business data from the Gestia API into structured, technology-agnostic
chart-ready objects. This module is a Business Intelligence (BI) layer: its sole
responsibility is to PREPARE visualization-ready data, NOT to render graphics.

Design philosophy
─────────────────
- Technology-agnostic: No dependency on Chart.js, Angular, React, or any UI framework.
- Reusable: The same JSON output is consumable by Angular dashboards, React frontends,
  mobile apps, reporting services, or any future Gestia integration without modification.
- BI-layer: Mirrors the responsibility separation of tools like Metabase or Tableau —
  the data pipeline is decoupled from the presentation layer.

Chart data model
────────────────
Every chart function returns a JSON string containing a ChartPayload structure:

    {
        "chartType": "line" | "bar" | "pie" | "doughnut" | "radar",
        "title":     <human-readable Spanish title>,
        "labels":    [...],             # X-axis labels or category names
        "datasets":  [                  # One dataset per data series
            {
                "label": "...",
                "data":  [...]
            }
        ],
        "metadata":  {                  # Optional hints for frontend renderers
            "currency": "ARS",
            "unit":     "...",
            "period":   "..."
        }
    }

Supported chart types
─────────────────────
1.  build_sales_trend_chart          — Monthly sales revenue trend (line)
2.  build_revenue_trend_chart        — Revenue + orders dual-axis trend (line)
3.  build_top_products_chart         — Top-selling products by revenue (bar)
4.  build_product_category_chart     — Revenue share by product category (doughnut)
5.  build_customer_distribution_chart — Customer distribution by segment (pie)
6.  build_sales_comparison_chart     — Period-over-period metric comparison (bar)

Frontend integration
────────────────────
Any frontend receives the JSON and maps it directly to its charting library:

    Angular (ng2-charts / Chart.js):
        chartData = { labels: payload.labels, datasets: payload.datasets }

    React (recharts / Chart.js):
        <LineChart data={payload.datasets[0].data} />

    Mobile (Victory / react-native-chart-kit):
        data={{ labels: payload.labels, datasets: payload.datasets }}

Separation of concerns
───────────────────────
    Analytics Agent → chart_tools → GestiaApiClient → Gestia REST API
                 ↓
            ChartPayload (JSON)
                 ↓
        Angular / React / Mobile / Report
"""

from __future__ import annotations

import json
from typing import Any

from app.app_utils.services import get_gestia_client
from app.tools._utils import (
    VALID_SUMMARY_PERIODS,
    VALID_TREND_PERIODS,
    validate_period,
)


# ---------------------------------------------------------------------------
# Internal chart builder helpers
# ---------------------------------------------------------------------------

def _make_chart(
    chart_type: str,
    title: str,
    labels: list[str],
    datasets: list[dict[str, Any]],
    metadata: dict[str, Any] | None = None,
) -> str:
    """
    Assembles and serializes a technology-agnostic ChartPayload to JSON.

    Args:
        chart_type: One of ``'line'``, ``'bar'``, ``'pie'``, ``'doughnut'``.
        title:      Human-readable Spanish title for the chart.
        labels:     X-axis labels or category names.
        datasets:   List of ``{"label": str, "data": list}`` dicts.
        metadata:   Optional extra hints (currency, unit, period) for renderers.

    Returns:
        JSON string representing the complete ChartPayload.
    """
    payload: dict[str, Any] = {
        "chartType": chart_type,
        "title": title,
        "labels": labels,
        "datasets": datasets,
    }
    if metadata:
        payload["metadata"] = metadata
    return json.dumps(payload, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# 1. Monthly sales trend
# ---------------------------------------------------------------------------

def build_sales_trend_chart(
    business_id: str,
    period: str = "last_6_months",
) -> str:
    """
    Genera un gráfico de línea con la tendencia de ventas mensuales.

    Útil para visualizar la evolución de los ingresos a lo largo del tiempo,
    detectar estacionalidad y comparar el crecimiento mes a mes.

    Cuándo usar: tendencias, evolución histórica, crecimiento, estacionalidad.

    Args:
        business_id: Identificador único del negocio (tenant).
        period: Rango temporal. Valores válidos:
                ``'last_3_months'``, ``'last_6_months'``,
                ``'last_12_months'``, ``'current_year'``.

    Returns:
        JSON con ChartPayload de tipo ``'line'`` listo para cualquier frontend.
        Contiene: ``chartType``, ``title``, ``labels`` (meses),
        ``datasets`` (ingresos), ``metadata`` (moneda, período).
    """
    validate_period(period, VALID_TREND_PERIODS)
    client = get_gestia_client()
    trend_points = client.get_revenue_trend(business_id, period, granularity="monthly")

    labels = [pt.label for pt in trend_points]
    revenue_data = [pt.revenue for pt in trend_points]

    return _make_chart(
        chart_type="line",
        title="Tendencia de Ventas Mensuales",
        labels=labels,
        datasets=[
            {"label": "Ingresos (ARS)", "data": revenue_data},
        ],
        metadata={"currency": "ARS", "unit": "pesos", "period": period},
    )


# ---------------------------------------------------------------------------
# 2. Revenue + order volume dual-series trend
# ---------------------------------------------------------------------------

def build_revenue_trend_chart(
    business_id: str,
    period: str = "last_6_months",
) -> str:
    """
    Genera un gráfico de línea de doble serie con ingresos y cantidad de pedidos.

    Permite correlacionar la evolución de ingresos con el volumen de pedidos
    para detectar si el crecimiento proviene de más transacciones o de mayor
    ticket promedio.

    Cuándo usar: análisis de crecimiento, correlación ingresos-volumen,
    tendencias de largo plazo.

    Args:
        business_id: Identificador único del negocio (tenant).
        period: Rango temporal. Valores válidos:
                ``'last_3_months'``, ``'last_6_months'``,
                ``'last_12_months'``, ``'current_year'``.

    Returns:
        JSON con ChartPayload de tipo ``'line'`` con dos datasets:
        ingresos y cantidad de pedidos. Incluye ``metadata`` con
        moneda y período.
    """
    validate_period(period, VALID_TREND_PERIODS)
    client = get_gestia_client()
    trend_points = client.get_revenue_trend(business_id, period, granularity="monthly")

    labels = [pt.label for pt in trend_points]
    revenue_data = [pt.revenue for pt in trend_points]
    orders_data = [pt.orders for pt in trend_points]

    return _make_chart(
        chart_type="line",
        title="Tendencia de Ingresos y Pedidos",
        labels=labels,
        datasets=[
            {"label": "Ingresos (ARS)", "data": revenue_data},
            {"label": "Pedidos", "data": orders_data},
        ],
        metadata={"currency": "ARS", "unit": "mixto", "period": period},
    )


# ---------------------------------------------------------------------------
# 3. Top-selling products by revenue (horizontal bar)
# ---------------------------------------------------------------------------

def build_top_products_chart(
    business_id: str,
    period: str = "current_month",
    limit: int = 5,
) -> str:
    """
    Genera un gráfico de barras con los productos más vendidos por ingresos.

    Permite identificar visualmente qué productos generan la mayor parte de los
    ingresos del negocio y comparar su desempeño relativo de un vistazo.

    Cuándo usar: rankings de productos, análisis de portafolio, comparación
    de desempeño por producto.

    Args:
        business_id: Identificador único del negocio (tenant).
        period: Período a analizar. Valores válidos:
                ``'current_month'``, ``'last_month'``,
                ``'current_quarter'``, ``'last_quarter'``,
                ``'current_year'``.
        limit: Cantidad máxima de productos a incluir (1–10, por defecto 5).

    Returns:
        JSON con ChartPayload de tipo ``'bar'`` con etiquetas de productos
        y dataset de ingresos. Incluye ``metadata`` con moneda y período.
    """
    validate_period(period, VALID_SUMMARY_PERIODS)
    limit = max(1, min(10, int(limit)))
    client = get_gestia_client()
    performers = client.get_best_selling_products(business_id, period, limit)

    labels = [p.product_name for p in performers]
    revenue_data = [p.revenue for p in performers]

    return _make_chart(
        chart_type="bar",
        title=f"Top {limit} Productos por Ingresos",
        labels=labels,
        datasets=[
            {"label": "Ingresos (ARS)", "data": revenue_data},
        ],
        metadata={"currency": "ARS", "unit": "pesos", "period": period},
    )


# ---------------------------------------------------------------------------
# 4. Product category revenue distribution (doughnut)
# ---------------------------------------------------------------------------

def build_product_category_chart(
    business_id: str,
    period: str = "current_month",
) -> str:
    """
    Genera un gráfico de dona con la distribución de ingresos por categoría.

    Muestra visualmente qué categorías de productos concentran la mayor
    proporción de ingresos del negocio, facilitando decisiones de portafolio.

    Cuándo usar: distribuciones, participación de mercado interno, análisis
    de portafolio por categoría.

    Args:
        business_id: Identificador único del negocio (tenant).
        period: Período a analizar. Valores válidos:
                ``'current_month'``, ``'last_month'``,
                ``'current_quarter'``, ``'last_quarter'``,
                ``'current_year'``.

    Returns:
        JSON con ChartPayload de tipo ``'doughnut'`` con categorías de productos
        como etiquetas y sus ingresos totales como dataset.
    """
    validate_period(period, VALID_SUMMARY_PERIODS)
    client = get_gestia_client()
    sales_by_product = client.get_sales_by_product(business_id, period)

    # Aggregate revenue by category using the product catalog for category lookup
    catalog = client.get_product_catalog(business_id)
    category_map: dict[str, str] = {p.product_id: p.category for p in catalog}

    category_revenue: dict[str, float] = {}
    for sale in sales_by_product:
        cat = category_map.get(sale.product_id, "Otras")
        category_revenue[cat] = category_revenue.get(cat, 0.0) + sale.revenue

    labels = list(category_revenue.keys())
    revenue_data = [round(v, 2) for v in category_revenue.values()]

    return _make_chart(
        chart_type="doughnut",
        title="Distribución de Ingresos por Categoría",
        labels=labels,
        datasets=[
            {"label": "Ingresos (ARS)", "data": revenue_data},
        ],
        metadata={"currency": "ARS", "unit": "pesos", "period": period},
    )


# ---------------------------------------------------------------------------
# 5. Customer segment distribution (pie)
# ---------------------------------------------------------------------------

def build_customer_distribution_chart(business_id: str) -> str:
    """
    Genera un gráfico de torta con la distribución de clientes por segmento.

    Visualiza cómo está segmentada la base de clientes del negocio: VIP,
    regulares, ocasionales e inactivos. Útil para estrategias de retención
    y fidelización.

    Cuándo usar: distribución de clientes, análisis de segmentos, estrategia
    de retención, fidelización.

    Args:
        business_id: Identificador único del negocio (tenant).

    Returns:
        JSON con ChartPayload de tipo ``'pie'`` con los nombres de segmento
        como etiquetas y la cantidad de clientes por segmento como dataset.
    """
    client = get_gestia_client()
    segments = client.get_customer_segments(business_id)

    labels = [s.segment_name for s in segments]
    count_data = [s.customer_count for s in segments]

    return _make_chart(
        chart_type="pie",
        title="Distribución de Clientes por Segmento",
        labels=labels,
        datasets=[
            {"label": "Cantidad de clientes", "data": count_data},
        ],
        metadata={"unit": "clientes"},
    )


# ---------------------------------------------------------------------------
# 6. Period-over-period sales comparison (grouped bar)
# ---------------------------------------------------------------------------

def build_sales_comparison_chart(
    business_id: str,
    period_a: str = "current_month",
    period_b: str = "last_month",
) -> str:
    """
    Genera un gráfico de barras agrupadas comparando métricas entre dos períodos.

    Permite visualizar lado a lado el rendimiento del período actual frente al
    período anterior en métricas clave: ingresos, pedidos, ticket promedio y
    margen bruto. Ideal para análisis MoM, QoQ o YoY.

    Cuándo usar: comparaciones entre períodos, análisis MoM/QoQ/YoY,
    evolución de KPIs, impacto de acciones.

    Args:
        business_id: Identificador único del negocio (tenant).
        period_a: Período principal (más reciente). Valores válidos:
                  ``'current_month'``, ``'last_month'``,
                  ``'current_quarter'``, ``'last_quarter'``,
                  ``'current_year'``.
        period_b: Período de referencia. Mismos valores válidos que ``period_a``.

    Returns:
        JSON con ChartPayload de tipo ``'bar'`` con dos datasets (uno por período)
        y métricas comparadas como etiquetas (Ingresos, Pedidos, Ticket promedio,
        Margen bruto %).
    """
    validate_period(period_a, VALID_SUMMARY_PERIODS, "period_a")
    validate_period(period_b, VALID_SUMMARY_PERIODS, "period_b")
    client = get_gestia_client()
    comparison = client.get_comparative_performance(business_id, period_a, period_b)

    labels = [c.metric for c in comparison]
    period_a_data = [c.period_a_value for c in comparison]
    period_b_data = [c.period_b_value for c in comparison]

    _PERIOD_LABELS: dict[str, str] = {
        "current_month":   "Mes actual",
        "last_month":      "Mes anterior",
        "current_quarter": "Trimestre actual",
        "last_quarter":    "Trimestre anterior",
        "current_year":    "Año actual",
    }

    return _make_chart(
        chart_type="bar",
        title=f"Comparación de Rendimiento: {_PERIOD_LABELS.get(period_a, period_a)} vs {_PERIOD_LABELS.get(period_b, period_b)}",
        labels=labels,
        datasets=[
            {"label": _PERIOD_LABELS.get(period_a, period_a), "data": period_a_data},
            {"label": _PERIOD_LABELS.get(period_b, period_b), "data": period_b_data},
        ],
        metadata={"period_a": period_a, "period_b": period_b},
    )
