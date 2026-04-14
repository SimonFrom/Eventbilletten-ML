from http.cookiejar import unmatched
from platform import uname

import pandas as pd
import numpy as np
import ast


def loadFiles(eventPath: str, ordersPath: str):
    events = pd.read_csv(eventPath, low_memory=False)
    orders = pd.read_csv(ordersPath)
    return events, orders


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
        how='left'
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

    # Days before event
    df['days_before_event'] = (
        df['start'] - df['created_at']
    ).dt.days



events, orders = loadFiles("allEvents_with_seller_category.csv", "allOrders.csv")
orders = filterOrders(orders)


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