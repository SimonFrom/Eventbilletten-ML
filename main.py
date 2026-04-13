import httpRequests as http
import eventResponse as event
import transactionResponse as transaction
import pandas as pd



test_key = "key_674285ea23414d0f482c5baaa2d11eb99241707cff12665f344528dfd414a2629b3010369f9a7414851551bf1f41cd73";
mapped_events = []
mapped_orders = []


def getEventsForSeller(token):
    data = http.getEventsPerSeller(token)
    return event.map_events(data)

def getOrdersForSeller(token):
    data = http.getOrdersPerSeller(token)
    return transaction.map_orders(data)


def cleanOrderData():
    data = getOrdersForSeller(test_key)
    ordersDF = pd.DataFrame(data["orders"])
    ordersNonNull = ordersDF.dropna(subset=['postal'])

    return ordersNonNull

def cleanEventData():
    data = getEventsForSeller(test_key)
    eventsDF = pd.DataFrame(data["events"])
    print("Events count:")
    print(len(eventsDF))
    eventsNonGroup = eventsDF[eventsDF['event_type'] == 'GROUP']

    return eventsNonGroup

finalEvents = cleanEventData()
# mapped_events = getEventsForSeller(test_key)
finalOrders = cleanOrderData()

mergedDF = pd.merge(finalEvents, finalOrders, left_on='id', right_on='event_id')

# Orders per event
print("Orders per event")
print(mergedDF.groupby('name_x')['id_y'].count())

# Revenue per event
print("Revenue per event")
print(mergedDF.groupby('name_x')['real_price'].sum())

# Unique customers per event
print("Unique customers per event")
print(mergedDF.groupby('name_x')['email'].nunique())

# Orders per city
print("Orders per city")
print(mergedDF.groupby('city')['id_y'].count().sort_values(ascending=False))




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


