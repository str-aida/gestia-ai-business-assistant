# ruff: noqa
"""
Shared Pydantic schemas for the Gestia AI Business Assistant.

This module defines:
- IntentClassification: structured output for the intent router.
- BusinessContext: tenant-scoped session metadata.
- Tool return types: one model per domain, returned by mock stubs
  (and later by real Gestia REST API clients).
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Intent Classification
# ---------------------------------------------------------------------------

class BusinessIntent(str, Enum):
    """Supported business query intents for routing."""
    SALES = "sales"
    PRODUCTS = "products"
    CUSTOMERS = "customers"
    ANALYTICS = "analytics"
    INSIGHTS = "insights"
    GENERAL = "general"
    OUT_OF_SCOPE = "out_of_scope"


class IntentClassification(BaseModel):
    """Structured output from the intent classifier agent."""
    intent: BusinessIntent = Field(
        description=(
            "The business intent of the user's query. Use 'out_of_scope' for "
            "any request that involves modifying data or is unrelated to business analysis."
        )
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Confidence score for the classification, between 0.0 and 1.0."
    )
    summary: str = Field(
        description="One-sentence summary of the user's question in the detected intent."
    )


# ---------------------------------------------------------------------------
# Business Context (Tenant Isolation)
# ---------------------------------------------------------------------------

class BusinessContext(BaseModel):
    """
    Tenant-scoped metadata for a conversation session.
    Injected by process_input and stored in ctx.state['business_context'].
    Every tool call receives business_id from this context.
    """
    business_id: str = Field(description="Unique identifier for the business tenant.")
    business_name: str = Field(description="Display name of the business.")
    business_type: str = Field(
        default="product_based",
        description="Type of business (e.g., 'product_based', 'bakery', 'retail')."
    )
    currency: str = Field(default="ARS", description="ISO 4217 currency code.")
    locale: str = Field(default="es-AR", description="BCP 47 locale tag for language/region.")
    timezone: str = Field(default="America/Argentina/Buenos_Aires", description="IANA timezone.")


# ---------------------------------------------------------------------------
# Sales Tool Return Types
# ---------------------------------------------------------------------------

class SalesSummary(BaseModel):
    """Aggregated sales figures for a given period."""
    business_id: str
    period: str
    total_revenue: float
    total_orders: int
    average_order_value: float
    top_category: str
    growth_vs_previous_period: float = Field(
        description="Percentage change vs the previous equivalent period."
    )


class SalesTrend(BaseModel):
    """A single data point in a sales trend series."""
    date: str
    revenue: float
    order_count: int


class SalesByProduct(BaseModel):
    """Sales breakdown per product."""
    product_id: str
    product_name: str
    units_sold: int
    revenue: float


class SalesByCustomer(BaseModel):
    """Sales breakdown per customer."""
    customer_id: str
    customer_name: str
    total_orders: int
    total_spent: float


# ---------------------------------------------------------------------------
# Product Tool Return Types
# ---------------------------------------------------------------------------

class Product(BaseModel):
    """A single product in the catalog."""
    product_id: str
    name: str
    category: str
    price: float
    stock: int
    is_active: bool


class ProductPerformance(BaseModel):
    """Sales performance for a single product."""
    product_id: str
    product_name: str
    units_sold: int
    revenue: float
    rank: int


class LowStockProduct(BaseModel):
    """A product flagged for low stock."""
    product_id: str
    product_name: str
    current_stock: int
    reorder_threshold: int


# ---------------------------------------------------------------------------
# Customer Tool Return Types
# ---------------------------------------------------------------------------

class CustomerOverview(BaseModel):
    """High-level customer base statistics."""
    business_id: str
    total_customers: int
    new_customers_this_period: int
    returning_customers: int
    churn_rate: float


class CustomerSummary(BaseModel):
    """Summary data for a single customer."""
    customer_id: str
    name: str
    total_orders: int
    total_spent: float
    last_purchase_date: str


class CustomerSegment(BaseModel):
    """A named customer segment with aggregate stats."""
    segment_name: str
    customer_count: int
    average_spend: float
    description: str


# ---------------------------------------------------------------------------
# Analytics Tool Return Types
# ---------------------------------------------------------------------------

class BusinessMetrics(BaseModel):
    """Core KPIs for a given period."""
    business_id: str
    period: str
    revenue: float
    gross_profit: float
    gross_margin_pct: float
    total_expenses: float
    net_profit: float
    orders_count: int
    average_ticket: float


class RevenueTrendPoint(BaseModel):
    """A single point in the revenue trend series."""
    label: str        # e.g. "2025-01", "Semana 3"
    revenue: float
    orders: int


class ComparativePerformance(BaseModel):
    """Side-by-side comparison of two periods."""
    metric: str
    period_a_value: float
    period_b_value: float
    change_pct: float
    trend: str  # "up", "down", "stable"


# ---------------------------------------------------------------------------
# Business Insights Tool Return Types
# ---------------------------------------------------------------------------

class BusinessAlert(BaseModel):
    """A threshold violation or anomaly detected in the business."""
    alert_id: str
    severity: str       # "high", "medium", "low"
    category: str       # "sales", "inventory", "customers"
    title: str
    description: str
    recommended_action: str


class BusinessSnapshot(BaseModel):
    """
    Aggregated business context used by the Insights Agent
    to produce holistic, cross-domain recommendations.
    """
    business_id: str
    business_name: str
    period: str
    revenue: float
    top_product: str
    top_customer: str
    low_stock_count: int
    inactive_customer_count: int
    alerts: list[BusinessAlert]
    growth_trend: str  # "growing", "stable", "declining"


# ---------------------------------------------------------------------------
# Feedback Model (used by /feedback endpoint in fast_api_app.py)
# ---------------------------------------------------------------------------

class Feedback(BaseModel):
    """
    User feedback collected via the /feedback endpoint.
    Logged to Cloud Logging for quality monitoring.
    """
    score: int = Field(
        ge=1, le=5,
        description="Feedback score from 1 (poor) to 5 (excellent)."
    )
    user_id: str = Field(description="ID of the user submitting the feedback.")
    session_id: str = Field(description="Session ID associated with the feedback.")
    text: str = Field(default="", description="Optional free-text comment from the user.")
