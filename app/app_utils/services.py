# ruff: noqa
"""
Gestia API Mock Client.

This module simulates the Gestia Spring Boot REST API for local development
and testing. All methods return realistic mock data that mirrors the shape
of the real API responses.

## Future integration

Replace the body of each method with an `httpx` (or `requests`) HTTP call to
the corresponding Gestia REST endpoint. The method signatures and return types
MUST NOT change — doing so would require changes in the tool layer above.

Example (future production pattern):
    async def get_sales_summary(self, business_id: str, period: str) -> SalesSummary:
        response = await self._client.get(
            f"{self._base_url}/api/v1/businesses/{business_id}/sales/summary",
            params={"period": period},
            headers={"Authorization": f"Bearer {self._jwt_token}"},
        )
        response.raise_for_status()
        return SalesSummary(**response.json())

Authentication note:
    In production, the JWT token is obtained by the Gestia backend and passed
    to the agent session via the request context. This client will hold a
    short-lived token refreshed per session — never stored in code.
"""

import random
from datetime import date, timedelta

from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService

from app.app_utils.typing import (
    SalesSummary, SalesTrend, SalesByProduct, SalesByCustomer,
    Product, ProductPerformance, LowStockProduct,
    CustomerOverview, CustomerSummary, CustomerSegment,
    BusinessMetrics, RevenueTrendPoint, ComparativePerformance,
    BusinessAlert, BusinessSnapshot,
)

# ---------------------------------------------------------------------------
# Service URIs (in-memory defaults for local dev; override via env vars
# in Cloud Run / Agent Engine deployments).
# ---------------------------------------------------------------------------

SESSION_SERVICE_URI: str = ""   # Empty string → InMemorySessionService
ARTIFACT_SERVICE_URI: str = ""  # Empty string → InMemoryArtifactService


def get_session_service() -> InMemorySessionService:
    """Returns an in-memory session service for local / dev use.

    Future: replace with a Cloud Firestore-backed session service by returning
    a service initialized with SESSION_SERVICE_URI when it is set.
    """
    return InMemorySessionService()


def get_artifact_service() -> InMemoryArtifactService:
    """Returns an in-memory artifact service for local / dev use.

    Future: replace with a GCS-backed artifact service by returning a service
    initialized with ARTIFACT_SERVICE_URI when it is set.
    """
    return InMemoryArtifactService()


class GestiaApiClient:
    """
    Mock implementation of the Gestia REST API client.

    All methods are synchronous and return Pydantic model instances.

    Future: Convert to async + real HTTP calls with JWT auth.
    Replace each method body with an httpx call like:

        async def get_sales_summary(self, business_id, period):
            response = await self._http.get(
                f"{self._base_url}/api/v1/businesses/{business_id}/sales/summary",
                params={"period": period},
                headers=self._auth_headers(),
            )
            response.raise_for_status()
            return SalesSummary(**response.json())
    """

    def __init__(self, base_url: str = "http://localhost:8080", jwt_token: str = ""):
        # Stored for future real HTTP calls — never logged or committed.
        self._base_url = base_url
        self._jwt_token = jwt_token

    def _auth_headers(self) -> dict:
        """Returns HTTP headers with a Bearer token for Gestia REST API calls.

        When jwt_token is empty (local dev / mock mode) the Authorization
        header value will be 'Bearer ' — harmless for mock stubs.

        Future: jwt_token will be supplied per-session from the validated
        JWT claim extracted by the Gestia Spring Boot API gateway.
        """
        return {"Authorization": f"Bearer {self._jwt_token}"}

    # -----------------------------------------------------------------------
    # Sales endpoints
    # -----------------------------------------------------------------------

    def get_sales_summary(self, business_id: str, period: str = "current_month") -> SalesSummary:
        """
        Mock: GET /api/v1/businesses/{business_id}/sales/summary?period={period}
        Returns aggregated sales figures for the given period.
        """
        return SalesSummary(
            business_id=business_id,
            period=period,
            total_revenue=487_350.75,
            total_orders=312,
            average_order_value=1562.02,
            top_category="Tortas personalizadas",
            growth_vs_previous_period=12.4,
        )

    def get_sales_trends(self, business_id: str, period: str = "last_6_months") -> list[SalesTrend]:
        """
        Mock: GET /api/v1/businesses/{business_id}/sales/trends?period={period}
        Returns daily/weekly/monthly sales data points.
        """
        base_date = date.today().replace(day=1)
        return [
            SalesTrend(
                date=(base_date - timedelta(days=30 * i)).strftime("%Y-%m"),
                revenue=round(random.uniform(380_000, 520_000), 2),
                order_count=random.randint(250, 380),
            )
            for i in range(6, 0, -1)
        ]

    def get_sales_by_product(self, business_id: str, period: str = "current_month") -> list[SalesByProduct]:
        """
        Mock: GET /api/v1/businesses/{business_id}/sales/by-product?period={period}
        Returns sales broken down by product.
        """
        products = [
            ("p-001", "Torta de chocolate", 87, 156_600),
            ("p-002", "Medialunas de manteca", 245, 48_755),
            ("p-003", "Cheesecake de frutos rojos", 63, 107_100),
            ("p-004", "Budín de naranja", 124, 61_380),
            ("p-005", "Alfajores artesanales", 310, 43_400),
        ]
        return [SalesByProduct(product_id=p[0], product_name=p[1], units_sold=p[2], revenue=p[3]) for p in products]

    def get_sales_by_customer(self, business_id: str, period: str = "current_month") -> list[SalesByCustomer]:
        """
        Mock: GET /api/v1/businesses/{business_id}/sales/by-customer?period={period}
        Returns sales broken down by customer.
        """
        customers = [
            ("c-001", "Restaurante El Mirador", 24, 89_400),
            ("c-002", "Hotel Buenos Aires Gran", 18, 67_200),
            ("c-003", "Cafetería Central", 31, 54_650),
            ("c-004", "María González", 8, 22_800),
            ("c-005", "Eventos Corporativos SA", 6, 48_000),
        ]
        return [SalesByCustomer(customer_id=c[0], customer_name=c[1], total_orders=c[2], total_spent=c[3]) for c in customers]

    # -----------------------------------------------------------------------
    # Product endpoints
    # -----------------------------------------------------------------------

    def get_product_catalog(self, business_id: str) -> list[Product]:
        """
        Mock: GET /api/v1/businesses/{business_id}/products
        Returns the full active product catalog.
        """
        catalog = [
            ("p-001", "Torta de chocolate", "Tortas", 1800.00, 12, True),
            ("p-002", "Medialunas de manteca", "Facturas", 198.75, 80, True),
            ("p-003", "Cheesecake de frutos rojos", "Tortas", 1700.00, 8, True),
            ("p-004", "Budín de naranja", "Budines", 495.00, 25, True),
            ("p-005", "Alfajores artesanales", "Golosinas", 140.00, 4, True),
            ("p-006", "Tarta de limón", "Tartas", 1200.00, 0, False),
        ]
        return [Product(product_id=p[0], name=p[1], category=p[2], price=p[3], stock=p[4], is_active=p[5]) for p in catalog]

    def get_best_selling_products(self, business_id: str, period: str = "current_month", limit: int = 5) -> list[ProductPerformance]:
        """
        Mock: GET /api/v1/businesses/{business_id}/products/best-sellers?period={period}&limit={limit}
        Returns top-performing products by revenue.
        """
        performers = [
            ("p-001", "Torta de chocolate", 87, 156_600, 1),
            ("p-003", "Cheesecake de frutos rojos", 63, 107_100, 2),
            ("p-002", "Medialunas de manteca", 245, 48_755, 3),
            ("p-004", "Budín de naranja", 124, 61_380, 4),
            ("p-005", "Alfajores artesanales", 310, 43_400, 5),
        ]
        return [ProductPerformance(product_id=p[0], product_name=p[1], units_sold=p[2], revenue=p[3], rank=p[4]) for p in performers[:limit]]

    def get_worst_selling_products(self, business_id: str, period: str = "current_month", limit: int = 5) -> list[ProductPerformance]:
        """
        Mock: GET /api/v1/businesses/{business_id}/products/worst-sellers?period={period}&limit={limit}
        Returns bottom-performing products by revenue.
        """
        performers = [
            ("p-005", "Alfajores artesanales", 18, 2_520, 1),
            ("p-004", "Budín de naranja", 12, 5_940, 2),
            ("p-006", "Tarta de limón", 0, 0, 3),
        ]
        return [ProductPerformance(product_id=p[0], product_name=p[1], units_sold=p[2], revenue=p[3], rank=p[4]) for p in performers[:limit]]

    def get_low_stock_products(self, business_id: str) -> list[LowStockProduct]:
        """
        Mock: GET /api/v1/businesses/{business_id}/products/low-stock
        Returns products at or below their reorder threshold.
        """
        return [
            LowStockProduct(product_id="p-005", product_name="Alfajores artesanales", current_stock=4, reorder_threshold=20),
            LowStockProduct(product_id="p-003", product_name="Cheesecake de frutos rojos", current_stock=8, reorder_threshold=10),
        ]

    # -----------------------------------------------------------------------
    # Customer endpoints
    # -----------------------------------------------------------------------

    def get_customer_overview(self, business_id: str) -> CustomerOverview:
        """
        Mock: GET /api/v1/businesses/{business_id}/customers/overview
        Returns high-level customer base statistics.
        """
        return CustomerOverview(
            business_id=business_id,
            total_customers=148,
            new_customers_this_period=23,
            returning_customers=125,
            churn_rate=8.4,
        )

    def get_top_customers(self, business_id: str, period: str = "current_month", limit: int = 5) -> list[CustomerSummary]:
        """
        Mock: GET /api/v1/businesses/{business_id}/customers/top?period={period}&limit={limit}
        Returns the highest-value customers for the period.
        """
        top = [
            ("c-001", "Restaurante El Mirador", 24, 89_400, "2025-06-28"),
            ("c-002", "Hotel Buenos Aires Gran", 18, 67_200, "2025-06-30"),
            ("c-005", "Eventos Corporativos SA", 6, 48_000, "2025-06-25"),
            ("c-003", "Cafetería Central", 31, 54_650, "2025-06-29"),
            ("c-004", "María González", 8, 22_800, "2025-06-15"),
        ]
        return [CustomerSummary(customer_id=c[0], name=c[1], total_orders=c[2], total_spent=c[3], last_purchase_date=c[4]) for c in top[:limit]]

    def get_inactive_customers(self, business_id: str, days_inactive: int = 60) -> list[CustomerSummary]:
        """
        Mock: GET /api/v1/businesses/{business_id}/customers/inactive?days={days_inactive}
        Returns customers who haven't purchased in the given number of days.
        """
        return [
            CustomerSummary(customer_id="c-010", name="Panadería La Estrella", total_orders=5, total_spent=12_500, last_purchase_date="2025-04-10"),
            CustomerSummary(customer_id="c-011", name="Club Deportivo Norte", total_orders=3, total_spent=8_700, last_purchase_date="2025-03-22"),
            CustomerSummary(customer_id="c-012", name="Ana Rodríguez", total_orders=2, total_spent=4_200, last_purchase_date="2025-04-01"),
        ]

    def get_customer_segments(self, business_id: str) -> list[CustomerSegment]:
        """
        Mock: GET /api/v1/businesses/{business_id}/customers/segments
        Returns customer segments with aggregate statistics.
        """
        return [
            CustomerSegment(segment_name="Clientes VIP", customer_count=12, average_spend=65_000, description="Compras frecuentes y alto valor"),
            CustomerSegment(segment_name="Clientes regulares", customer_count=67, average_spend=18_400, description="Compras mensuales consistentes"),
            CustomerSegment(segment_name="Clientes ocasionales", customer_count=49, average_spend=5_200, description="Compran 1-2 veces por trimestre"),
            CustomerSegment(segment_name="Clientes inactivos", customer_count=20, average_spend=0, description="Sin compras en los últimos 60 días"),
        ]

    # -----------------------------------------------------------------------
    # Analytics endpoints
    # -----------------------------------------------------------------------

    def get_business_metrics(self, business_id: str, period: str = "current_month") -> BusinessMetrics:
        """
        Mock: GET /api/v1/businesses/{business_id}/analytics/metrics?period={period}
        Returns core KPIs for the business.
        """
        return BusinessMetrics(
            business_id=business_id,
            period=period,
            revenue=487_350.75,
            gross_profit=243_675.00,
            gross_margin_pct=50.0,
            total_expenses=178_400.00,
            net_profit=65_275.00,
            orders_count=312,
            average_ticket=1562.02,
        )

    def get_revenue_trend(self, business_id: str, period: str = "last_6_months", granularity: str = "monthly") -> list[RevenueTrendPoint]:
        """
        Mock: GET /api/v1/businesses/{business_id}/analytics/revenue-trend?period={period}&granularity={granularity}
        Returns revenue trend data points for charting and analysis.
        """
        months = ["Ene", "Feb", "Mar", "Abr", "May", "Jun"]
        revenues = [412_000, 398_500, 445_800, 471_200, 459_000, 487_350]
        orders = [265, 258, 290, 301, 287, 312]
        return [RevenueTrendPoint(label=m, revenue=r, orders=o) for m, r, o in zip(months, revenues, orders)]

    def get_conversion_metrics(self, business_id: str, period: str = "current_month") -> dict:
        """
        Mock: GET /api/v1/businesses/{business_id}/analytics/conversion?period={period}
        Returns conversion and funnel metrics.
        Future: Returns a typed ConversionMetrics model.
        """
        return {
            "business_id": business_id,
            "period": period,
            "quote_to_order_rate": 68.5,
            "order_to_fulfillment_rate": 97.2,
            "repeat_purchase_rate": 84.5,
        }

    def get_comparative_performance(self, business_id: str, period_a: str, period_b: str) -> list[ComparativePerformance]:
        """
        Mock: GET /api/v1/businesses/{business_id}/analytics/compare?period_a={period_a}&period_b={period_b}
        Returns side-by-side comparison of two periods.
        """
        return [
            ComparativePerformance(metric="Ingresos", period_a_value=487_350, period_b_value=433_500, change_pct=12.4, trend="up"),
            ComparativePerformance(metric="Pedidos", period_a_value=312, period_b_value=278, change_pct=12.2, trend="up"),
            ComparativePerformance(metric="Ticket promedio", period_a_value=1562, period_b_value=1559, change_pct=0.2, trend="stable"),
            ComparativePerformance(metric="Margen bruto %", period_a_value=50.0, period_b_value=47.3, change_pct=2.7, trend="up"),
        ]

    # -----------------------------------------------------------------------
    # Insights endpoints
    # -----------------------------------------------------------------------

    def get_business_context(self, business_id: str) -> BusinessSnapshot:
        """
        Mock: GET /api/v1/businesses/{business_id}/snapshot
        Returns an aggregated business snapshot for holistic insights reasoning.
        """
        alerts = [
            BusinessAlert(
                alert_id="a-001",
                severity="high",
                category="inventory",
                title="Stock crítico: Alfajores artesanales",
                description="Solo 4 unidades en stock. El umbral de reorden es 20.",
                recommended_action="Reponer stock antes del fin de semana para evitar quiebre.",
            ),
            BusinessAlert(
                alert_id="a-002",
                severity="medium",
                category="customers",
                title="20 clientes sin compras en 60+ días",
                description="Hay 20 clientes inactivos que históricamente representaban el 14% de los ingresos.",
                recommended_action="Lanzar una campaña de reactivación con una oferta especial.",
            ),
        ]
        return BusinessSnapshot(
            business_id=business_id,
            business_name="La Pastelería Artesanal",
            period="Junio 2025",
            revenue=487_350.75,
            top_product="Torta de chocolate",
            top_customer="Restaurante El Mirador",
            low_stock_count=2,
            inactive_customer_count=20,
            alerts=alerts,
            growth_trend="growing",
        )

    def get_business_alerts(self, business_id: str) -> list[BusinessAlert]:
        """
        Mock: GET /api/v1/businesses/{business_id}/alerts
        Returns active business alerts and anomalies.
        """
        return self.get_business_context(business_id).alerts


# ---------------------------------------------------------------------------
# Module-level singleton (used by all tool functions)
# ---------------------------------------------------------------------------

_client = GestiaApiClient()


def get_gestia_client() -> GestiaApiClient:
    """Returns the module-level Gestia API client instance."""
    return _client
