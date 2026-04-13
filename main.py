import httpRequests as http
import eventResponse as event
import transactionResponse as transaction
import pandas as pd
import json



test_key = "key_674285ea23414d0f482c5baaa2d11eb99241707cff12665f344528dfd414a2629b3010369f9a7414851551bf1f41cd73";

all_events = []
all_orders = []

with open("sellers.json") as f:
    data = json.load(f)

sellers_list = data["Sellers"]
sellers = {
    seller["SellerName"]: {k: v for k, v in seller.items() if k != "SellerName"}
    for seller in sellers_list
}


def getEventsForSeller(token):
    data = http.getEventsPerSeller(token)
    return event.map_events(data)

def getOrdersForSeller(token):
    data = http.getOrdersPerSeller(token)
    return transaction.map_orders(data)


def cleanEventData(data):
    df = pd.DataFrame(data["events"])
    print("Events count:", len(df))
    return df[df['event_type'] == 'GROUP']

def cleanOrderData(data):
    df = pd.DataFrame(data["orders"])
    return df.dropna(subset=['postal'])


def getAllSellersAndTransactions():
    all_events = {"events": []}
    all_orders = {"orders": []}

    for seller_name, seller_data in sellers.items():
        api_key = seller_data["Configuration"]["VivenuAPIKey"]
        all_events["events"].extend(getEventsForSeller(api_key)["events"])
        all_orders["orders"].extend(getOrdersForSeller(api_key)["orders"])

    all_eventsDF = pd.DataFrame(all_events)
    all_ordersDF = pd.DataFrame(all_orders)

    # clean_events = cleanEventData(all_events)
    # clean_orders = cleanOrderData(all_orders)

    # mergedDF = pd.merge(all_eventsDF, all_ordersDF, left_on='id', right_on='event_id')
    # return mergedDF
    all_eventsDF.to_csv("allEvents.csv")
    all_ordersDF.to_csv("allOrders.csv")









# ---- Get all events and transactions and write to csv-----
# DFtoCSV = getAllSellersAndTransactions()
#
# DFtoCSV.to_csv("DirtyMergedEvents.csv")

# ------ Testing ------
# print("Orders cleaned:")
# print(len(finalOrders))
# print(finalOrders["postal"].unique())
# print(finalOrders.describe().to_string())
# print(finalOrders[["postal"]].describe().to_string())

# eventDF = pd.DataFrame(mapped_events["events"])
#
# for event in mapped_events["events"]:
#     print(event["name"])

# print(mapped_events["events"][0]["name"])
# print(len(finalEvents))
#
# # Orders per event
# print("Orders per event")
# print(mergedDF.groupby('name_x')['id_y'].count())
#
# # Revenue per event
# print("Revenue per event")
# print(mergedDF.groupby('name_x')['real_price'].sum())
#
# # Unique customers per event
# print("Unique customers per event")
# print(mergedDF.groupby('name_x')['email'].nunique())
#
# # Orders per city
# print("Orders per city")
# print(mergedDF.groupby('city')['id_y'].count().sort_values(ascending=False))


