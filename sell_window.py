"""
Goals:
- When do tickets sell relative to the eventdate?
- What percentage of tickets are sold in the first week, last week, last 3 days?
- Does the pattern differ by seller category?

Result:
Sellers know when to optimize their marketing and selling strategy
"""

import pandas as pd
import numpy as np

from event_draw_profile import cleanForJson


def loadBuyerFeatures(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=False)
    df['created_at'] = pd.to_datetime(df['created_at'], utc=True, errors='coerce')
    df['start'] = pd.to_datetime(df['start'], utc=True, errors='coerce')
    df['sell_start'] = pd.to_datetime(df['sell_start'], utc=True, errors='coerce')

    # Clean
    df = df[df['seller_category'].notna()].copy()
    df = df[df['days_before_event'] >= -730].copy()

    print(f"Loaded {len(df)} orders across {df['event_id'].nunique()} events")
    return df

# ---- Sell window metrics ----
def buildSellWindowMetrics(df: pd.DataFrame) -> pd.DataFrame:
    event_totals = df.groupby('event_id')['ticket_count'].sum()

    windows = {
        'pct_sold_0_7_days': (0, 7),
        'pct_sold_8_14_days': (8, 14),
        'pct_sold_15_30_days': (15, 30),
        'pct_sold_31_60_days': (31, 60),
        'pct_sold_61_90_days': (61, 90),
        'pct_sold_over_90_days': (91, 9999),
    }

    window_df = pd.DataFrame({'event_id': event_totals.index}).reset_index(drop=True)

    for col_name, (low, high) in windows.items():
        mask = (
                (df['days_before_event'] >= low) &
                (df['days_before_event'] <= high)
        )
        tickets_in_window = df[mask].groupby(
            'event_id')['ticket_count'].sum()

        pct = (tickets_in_window / event_totals).fillna(0)

        # Map values back using event_id as the key
        window_df[col_name] = window_df['event_id'].map(pct)

    base = df.groupby('event_id').agg(
        seller_category=('seller_category', 'first'),
        event_city=('event_city', 'first'),
        event_start=('start', 'first'),
        sell_start=('sell_start', 'first'),
        total_tickets=('ticket_count', 'sum'),
        total_orders=('id', 'count'),
        max_amount=('max_amount', 'first'),
        sales_window_days=('days_from_sell_start', 'max'),
        median_days_before_event=('days_before_event', 'median'),
        p25_days_before_event=('days_before_event',
                               lambda x: x.quantile(0.25)),
        p75_days_before_event=('days_before_event',
                               lambda x: x.quantile(0.75)),
    ).reset_index()
    result = base.merge(window_df, on='event_id', how='left')
    result['sell_through_rate'] = (
        result['total_tickets'] / result['max_amount']
    ).clip(upper=1.0)
    print(f"Sell window metrics for {len(result)} events")
    print(f"\nAverage sales distribution by time window:")
    window_cols = list(windows.keys())
    print(result[window_cols].mean().round(3))
    return result

# ---- Metrics by category ----
def buildMetricsByCategory(metrics: pd.DataFrame) -> pd.DataFrame:
    window_cols = [
        'pct_sold_0_7_days',
        'pct_sold_8_14_days',
        'pct_sold_15_30_days',
        'pct_sold_31_60_days',
        'pct_sold_61_90_days',
        'pct_sold_over_90_days',
    ]

    category_profile = metrics.groupby('seller_category').agg(
        n_events=('event_id', 'count'),
        avg_sell_through_rate=('sell_through_rate', 'mean'),
        avg_sales_window = ('sales_window_days', 'mean'),
        median_days_before_event=('median_days_before_event', 'mean'),
        **{col: (col, 'mean') for col in window_cols}
    ).round(3).reset_index()

    print("Sell window profile by category:")
    print("=" * 60)
    print(category_profile.to_string(index=False))

    return category_profile


def saveSellWindow(metrics: pd.DataFrame,
                   category_profile: pd.DataFrame,
                   metrics_path: str,
                   category_path: str) -> None:
    metrics.to_csv(metrics_path, index=False, encoding='utf-8-sig')
    category_profile.to_csv(category_path, index=False, encoding='utf-8-sig')
    print(f"Saved sell metrics to csv to {metrics_path}")
    print(f"Saved category profile to csv {category_path}")

def getSellWindowMetrics(buyerFeaturesPath: str) -> list[dict]:
    df = loadBuyerFeatures(buyerFeaturesPath)
    metrics = buildSellWindowMetrics(df)
    return cleanForJson(metrics.to_dict('records'))

def getSellWindowCategoryProfile(buyerFeaturesPath: str) -> list[dict]:
    df = loadBuyerFeatures(buyerFeaturesPath)
    metrics = buildSellWindowMetrics(df)
    category_profile = buildMetricsByCategory(metrics)
    return cleanForJson(category_profile.to_dict('records'))

if __name__ == '__main__':
    df = loadBuyerFeatures('csv/buyerFeatures.csv')
    metrics = buildSellWindowMetrics(df)
    category_profile = buildMetricsByCategory(df, metrics)
    saveSellWindow(
        metrics,
        category_profile,
        'csv/sellWindowMetrics.csv',
        'csv/sellWindowCategoryProfile.csv'
    )

