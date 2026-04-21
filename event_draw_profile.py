import os

import pandas as pd
import numpy as np

path = "csv/buyerFeatures.csv"

def loadBuyerFeatures(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=False)
    df['created_at'] = pd.to_datetime(df['created_at'], utc=True, errors='coerce')
    df['start'] = pd.to_datetime(df['start'], utc=True, errors='coerce')
    print(f"Loaded {len(df)} orders across {df['event_id'].nunique()} events")
    return df

def filterNoise(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)

    # Remove rows with long buy date before event start
    df = df[df['days_before_event'] >= -730].copy()

    # Remove events with no seller match
    df = df[df['seller_category'].notna()].copy()


    after = len(df)

    print(f"Rows before filtering: {before}")
    print(f"Rows after filtering: {after}")
    print(f"Removed {before - after} rows")
    return df


def buildEventDrawProfile(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate order-level data up to event level.
    One row per event with draw profile metrics.
    """

    # ── Base aggregation ───────────────────────────────────────
    profile = df.groupby('event_id').agg(
        seller_category=('seller_category', 'first'),
        event_city=('event_city', 'first'),
        event_postal=('event_postal_clean', 'first'),
        event_lat=('event_lat', 'first'),
        max_amount=('max_amount', 'first'),
        event_start=('start', 'first'),
        total_orders=('id', 'count'),
        total_tickets=('ticket_count', 'sum'),
        total_revenue=('real_price', 'sum'),
        avg_spend_per_order=('real_price', 'mean'),
        avg_tickets_per_order=('ticket_count', 'mean'),
        median_tickets_per_order=('ticket_count', 'median'),
        avg_days_before_event=('days_before_event', 'mean'),
        median_days_before_event=('days_before_event', 'median'),
        n_unique_buyer_postals=('buyer_postal_clean', 'nunique'),
        n_orders_with_distance=('distance_km', 'count'),
        avg_distance_km=('distance_km', 'mean'),
        median_distance_km=('distance_km', 'median'),
        p80_distance_km=('distance_km', lambda x: x.quantile(0.8)),
        max_distance_km=('distance_km', 'max'),
    ).reset_index()

    # ── Sell through rate ──────────────────────────────────────
    # Clip at 1.0 to handle edge cases where tickets sold
    # slightly exceeds max_amount due to data quirks
    profile['sell_through_rate'] = (
        profile['total_tickets'] / profile['max_amount']
    ).clip(upper=1.0)

    # ── Distance buckets ───────────────────────────────────────
    # Only calculated where we have distance data
    has_dist = df[df['distance_km'].notna()].copy()

    dist_buckets = has_dist.groupby('event_id').agg(
        pct_under_10km=('distance_km', lambda x: (x < 10).mean()),
        pct_under_30km=('distance_km', lambda x: (x < 30).mean()),
        pct_under_50km=('distance_km', lambda x: (x < 50).mean()),
        pct_over_100km=('distance_km', lambda x: (x > 100).mean()),
    ).reset_index()

    profile = profile.merge(dist_buckets, on='event_id', how='left')

    # ── Early vs late booking ──────────────────────────────────
    # Early = more than 14 days before event
    # Late = 14 days or fewer before event
    early = df[df['days_before_event'] >= 14].groupby(
        'event_id')['id'].count()
    late = df[df['days_before_event'] < 14].groupby(
        'event_id')['id'].count()
    total = early.add(late, fill_value=0)

    profile['pct_early_buyers'] = (
        early / total
    ).reindex(profile['event_id']).values

    profile['pct_late_buyers'] = (
        late / total
    ).reindex(profile['event_id']).values

    print(f"Event draw profile built for {len(profile)} events")
    print(f"\nSell through rate by category:")
    print(
        profile.groupby('seller_category')['sell_through_rate']
        .mean()
        .round(2)
        .sort_values(ascending=False)
    )

    return profile

# ---- Save to csv
def saveEventDrawProfile(profile: pd.DataFrame, outputPath: str) -> None:
    if os.path.exists(outputPath):
        print(f"CSV already exists at {outputPath}")
    else:
        print(f"Creating CSV at {outputPath}")
        profile.to_csv(outputPath, index=False)

# ---- Returns a dict with eventDraw for c#
def getEventDrawProfile(buyerFeaturesPath: str) -> list[dict]:
    df = loadBuyerFeatures(buyerFeaturesPath)
    df = filterNoise(df)
    profile = buildEventDrawProfile(df)

    # records make sure that the dict returned will have one item per row for c#
    return cleanForJson(profile.to_dict('records'))

def cleanForJson(data: list[dict]) -> list[dict]:
    cleaned = []
    for row in data:
        clean_row = {
            k: (None if isinstance(v, float) and np.isnan(v) else v)
            for k, v in row.items()
        }
        cleaned.append(clean_row)
    return cleaned

# ---- Load feature list ----
df = loadBuyerFeatures(path)
# print(df.columns.tolist())

# ---- Filter csv -----
df = filterNoise(df)

# ---- Event draw profile ----
profile = buildEventDrawProfile(df)

# ---- Save to csv ----
saveEventDrawProfile(df, "csv/event_draw_profile.csv")