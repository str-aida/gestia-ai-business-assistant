# ruff: noqa
"""
Tools package for the Gestia AI Business Assistant.

Imports all read-only tool functions organized by domain.
Each tool accepts business_id as its first argument for tenant isolation.
"""

from app.tools.sales_tools import (
    get_sales_summary,
    get_sales_trends,
    get_sales_by_product,
    get_sales_by_customer,
)
from app.tools.product_tools import (
    get_product_catalog,
    get_best_selling_products,
    get_worst_selling_products,
    get_low_stock_products,
)
from app.tools.customer_tools import (
    get_customer_overview,
    get_top_customers,
    get_inactive_customers,
    get_customer_segments,
)
from app.tools.analytics_tools import (
    get_business_metrics,
    get_revenue_trend,
    get_conversion_metrics,
    get_comparative_performance,
)
from app.tools.insights_tools import (
    get_business_context,
    get_business_alerts,
)
from app.tools.chart_tools import (
    build_sales_trend_chart,
    build_revenue_trend_chart,
    build_top_products_chart,
    build_product_category_chart,
    build_customer_distribution_chart,
    build_sales_comparison_chart,
)

__all__ = [
    "get_sales_summary", "get_sales_trends", "get_sales_by_product", "get_sales_by_customer",
    "get_product_catalog", "get_best_selling_products", "get_worst_selling_products", "get_low_stock_products",
    "get_customer_overview", "get_top_customers", "get_inactive_customers", "get_customer_segments",
    "get_business_metrics", "get_revenue_trend", "get_conversion_metrics", "get_comparative_performance",
    "get_business_context", "get_business_alerts",
    # Visual analytics (chart data builders)
    "build_sales_trend_chart", "build_revenue_trend_chart", "build_top_products_chart",
    "build_product_category_chart", "build_customer_distribution_chart", "build_sales_comparison_chart",
]
