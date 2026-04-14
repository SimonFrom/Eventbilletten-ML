import pandas as pd
import numpy as np
import ast
from dk_postal_coords import DK_POSTAL_COORDS


def loadFiles(eventPath: str, ordersPath: str):
    events = pd.read_csv(eventPath, low_memory=False)
    orders = pd.read_csv(ordersPath)
    return events, orders

# ------ Filter out internal and null events ------
def filterInternalSeller(events: pd.DataFrame) -> pd.DataFrame:
    seller_cat = ['internal']

    filtered = events[
        ~(events['seller_category'].isin(seller_cat) | events['seller_category'].isna())
        ].copy()
    print(filtered['seller_category'].isna().sum())
    print(f"Events before internal filter: {len(events)}")
    print(f"Events after internal filter: {len(filtered)}")
    return filtered



# ------ Return a filtered dataframe with non complete orders removed ------
def filterOrders(orders: pd.DataFrame) -> pd.DataFrame:
    complete_statuses = ['COMPLETE']
    complete_payments = ['RECEIVED', 'LOCAL-RECEIVED', 'POS-RECEIVED']

    filterd = orders[
        (orders['status'].isin(complete_statuses)) &
        (orders['payment_status'].isin(complete_payments))
        ].copy()
    print(f"Orders before filtering: {len(orders)}")
    print(f"Orders after filtering: {len(filterd)}")
    return filterd


# ---- Count tickets in order ----
def countTicketsInOrder(ticket: str) -> int:
    try:
        tickets = ast.literal_eval(ticket)
        return sum(t.get('amount', 0) for t in tickets)
    except (ValueError, SyntaxError):
        return 0


# ---- Get time stamps ----
def parseTimeStamps(orders: pd.DataFrame, events: pd.DataFrame) -> tuple:
    orders['created_at'] = pd.to_datetime(orders['created_at'], utc=True)
    events['start'] = pd.to_datetime(events['start'], utc=True)
    events['sell_start'] = pd.to_datetime(events['sell_start'], utc=True)
    return orders, events


# ---- Extract location ----
def extractEventLocation(events: pd.DataFrame) -> pd.DataFrame:
    def parseLocation(loc_str):
        try:
            loc = ast.literal_eval(str(loc_str))
            return loc.get('city', ''), loc.get('postal', '')
        except (ValueError, SyntaxError):
            return '', ''

    parsed = events['location'].apply(parseLocation)
    events['event_city'] = [x[0] for x in parsed]
    events['event_postal'] = [x[1] for x in parsed]

    print(f"Events cities sample:")
    print(events['event_city'].value_counts().head(10))
    return events


# ---- Join event meta data to each order ----
def joinOrdersToEvents(orders: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    event_cols = [
        'id',
        'seller_category',
        'seller_name',
        'event_city',
        'event_postal',
        'max_amount',
        'start',
        'sell_start'
    ]

    # Rename events id to avoid collision with orders id
    events_subset = events[event_cols].rename(columns={'id': 'event_id'})

    df = orders.merge(
        events_subset,
        on='event_id',
        how='inner'
    )

    # drop seller_name from one file
    df = df.rename(columns={'seller_name_order': 'seller_name'})
    df = df.drop(columns=['seller_name_event'], errors = 'ignore')

    unmatched = df['seller_category'].isna().sum()
    print(f"Total orders after join: {len(df)}")
    print(f"Orders with no matching event: {unmatched}")
    print(f"Seller category distribution: ")
    print(df['seller_category'].value_counts())

    return df


# ---- Time features ----
def addTimeFeatures(df: pd.DataFrame) -> pd.DataFrame:

    # Days before event order was placed
    df['days_before_event'] = (
        df['start'] - df['created_at']
    ).dt.days

    # How many days after sell_start was order placed
    df['days_from_sell_start'] = (
        df['created_at'] - df['sell_start']
    ).dt.days

    # Timestamp
    df['purchase_hour'] = df['created_at'].dt.hour

    df['purchase_day_of_week'] = df['created_at'].dt.dayofweek

    print(f"Days before event starts: ")
    print(df['days_before_event'].describe().round(1))

    return df

# ---- Clean postal codes ----
def cleanPostal(val) -> str | None:
    try:
        s = str(val).strip()
        s = s.split('.')[0]
        if len(s) == 4 and s.isdigit():
            return s
    except:
        return None


# ---- Add postal codes ----
def addPostalCodes(df: pd.DataFrame) -> pd.DataFrame:
    df['buyer_postal_clean'] = df['postal'].apply(cleanPostal)
    df['event_postal_clean'] = df['event_postal'].apply(cleanPostal)

    buyer_coverage = df['buyer_postal_clean'].notna().mean() * 100
    event_coverage = df['event_postal_clean'].notna().mean() * 100

    print(f"Buyer postal coverage: {buyer_coverage:.1f}%")
    print(f"Event postal coverage: {event_coverage:.1f}%")

    return df

# ---- Calcutate distance from buyer to event----
def haversineKm(lat1: float,
                lon1: float,
                lat2: float,
                lon2: float) -> float:
    km_per_degree_lat = 111.0
    km_per_degree_lon = 111.0 * np.cos(np.radians((lat1 + lat2) / 2))

    dlat = abs(lat2 - lat1) * km_per_degree_lat
    dlon = abs(lon2 - lon1) * km_per_degree_lon

    return np.sqrt((dlat ** 2) + (dlon ** 2))

# ---- Add distance to df via dk_postal_codes.py ----
def addDistance(df: pd.DataFrame) -> pd.DataFrame:
    def getLat(postal):
        if postal and postal in DK_POSTAL_COORDS:
            return DK_POSTAL_COORDS[postal][0]
        return np.nan

    def getLon(postal):
        if postal and postal in DK_POSTAL_COORDS:
            return DK_POSTAL_COORDS[postal][1]
        return np.nan

    df['buyer_lat'] = df['buyer_postal_clean'].apply(getLat)
    df['buyer_lon'] = df['buyer_postal_clean'].apply(getLon)
    df['event_lat'] = df['event_postal_clean'].apply(getLat)
    df['event_lon'] = df['event_postal_clean'].apply(getLon)

    # Only calc for ones with both
    has_coords = (
        df['buyer_lat'].notna() &
        df['event_lat'].notna()
    )
    df['distance_km'] = np.nan

    df.loc[has_coords, 'distance_km'] = haversineKm(
        df.loc[has_coords, 'buyer_lat'].values,
        df.loc[has_coords, 'buyer_lon'].values,
        df.loc[has_coords, 'event_lat'].values,
        df.loc[has_coords, 'event_lon'].values
    )

    # Labels for df
    bins = [0, 10, 30, 50, 100, 200, 9999]
    labels = ['<10km', '10-30km', '30-50km', '50-100km', '100-200km', '>200km']
    df['distance_bucket'] = pd.cut(
        df['distance_km'], bins=bins, labels=labels
    )

    coverage = has_coords.mean() * 100
    print(f"Distance calculated for {coverage:.1f}% of orders")
    print(f"\nDistance distribution: ")
    print(df['distance_bucket'].value_counts().sort_index())

    return df

# ---- Save buyer features ----
def saveBuyerFeatures(df: pd.DataFrame, outputPath: str) -> None:
    keep_cols = [
        'id',
        'event_id',
        'seller_name',
        'seller_category',
        'name',
        'email',
        'city',
        'postal',
        'country',
        'real_price',
        'ticket_count',
        'created_at',
        'event_city',
        'event_postal',
        'max_amount',
        'start',
        'sell_start',
        'days_before_event',
        'days_from_sell_start',
        'purchase_hour',
        'purchase_day_of_week',
        'buyer_postal_clean',
        'event_postal_clean',
        'buyer_lat',
        'buyer_lng',
        'event_lat',
        'event_lng',
        'distance_km',
        'distance_bucket',
    ]

    existing_cols = [c for c in keep_cols if c in df.columns]
    output = df[existing_cols]

    output.to_csv(outputPath, index=False, encoding='utf-8-sig')
    print(f"Saved {len(output)} rows and {len(existing_cols)} columns to {outputPath}")

events, orders = loadFiles("csv/allEvents_with_seller_category.csv", "csv/allOrders.csv")
orders = filterOrders(orders)
events = filterInternalSeller(events)


print("------ Ticket info ------ :")
orders['ticket_count'] = orders['tickets'].apply(countTicketsInOrder)
print(f"Avg ticket amount: {orders['ticket_count'].mean():.2f}")
print(f"Ticket count sample:\n{orders['ticket_count'].value_counts().head(10)}")


print(" ------ Parse timestamps ------ :")
orders, events = parseTimeStamps(orders, events)


print(f"Orders data range:")
print(f"  Earliest order: {orders['created_at'].min()}")
print(f"  Latest order: {orders['created_at'].max()}")


print(" ------ Extract location ------ :")
events = extractEventLocation(events)


print(" ------ Join tables ------ :")
df = joinOrdersToEvents(orders, events)

print(" ------ Add timestamp ------ :")
df = addTimeFeatures(df)

print(" ------ Add postal codes ------ :")
df = addPostalCodes(df)

print(" ------ Add distance ------ :")
df = addDistance(df)

print(" ------ Save features ------ :")
saveBuyerFeatures(df, outputPath="csv/buyerFeatures.csv")



