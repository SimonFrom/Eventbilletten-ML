from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class EventDrawProfileModel(BaseModel):
    event_id: str
    seller_category: Optional[str]
    event_city: Optional[str]
    event_postal: Optional[str]
    event_lat: Optional[float]
    max_amount: Optional[float]
    event_start: Optional[str]
    total_orders: Optional[float]
    total_tickets: Optional[float]
    total_revenue: Optional[float]
    avg_spend_per_order: Optional[float]
    avg_tickets_per_order: Optional[float]
    median_tickets_per_order: Optional[float]
    avg_days_before_event: Optional[float]
    median_days_before_event: Optional[float]
    n_unique_buyer_postals: Optional[float]
    n_orders_with_distance: Optional[float]
    avg_distance_km: Optional[float]
    median_distance_km: Optional[float]
    p80_distance_km: Optional[float]
    max_distance_km: Optional[float]
    sell_through_rate: Optional[float]
    pct_under_10km: Optional[float]
    pct_under_30km: Optional[float]
    pct_under_50km: Optional[float]
    pct_over_100km: Optional[float]
    pct_early_buyers: Optional[float]
    pct_late_buyers: Optional[float]


class SellWindowMetricsModel(BaseModel):
    event_id: str
    seller_category: Optional[str]
    event_city: Optional[str]
    event_start: Optional[str]
    sell_start: Optional[str]
    total_tickets: Optional[float]
    total_orders: Optional[float]
    max_amount: Optional[float]
    sales_window_days: Optional[float]
    median_days_before_event: Optional[float]
    p25_days_before_event: Optional[float]
    p75_days_before_event: Optional[float]
    sell_through_rate: Optional[float]
    pct_sold_0_7_days: Optional[float]
    pct_sold_8_14_days: Optional[float]
    pct_sold_15_30_days: Optional[float]
    pct_sold_31_60_days: Optional[float]
    pct_sold_61_90_days: Optional[float]
    pct_sold_over_90_days: Optional[float]


class SellWindowCategoryModel(BaseModel):
    seller_category: str
    n_events: Optional[float]
    avg_sell_through_rate: Optional[float]
    avg_sales_window: Optional[float]
    median_days_before_event: Optional[float]
    pct_sold_0_7_days: Optional[float]
    pct_sold_8_14_days: Optional[float]
    pct_sold_15_30_days: Optional[float]
    pct_sold_31_60_days: Optional[float]
    pct_sold_61_90_days: Optional[float]
    pct_sold_over_90_days: Optional[float]


class ApiResponse(BaseModel):
    count: float
    data: list