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

mapped_events = getEventsForSeller(test_key)

finalOrders = cleanOrderData()
print("Orders cleaned:")
print(len(finalOrders))
print(finalOrders["postal"].unique())
print(finalOrders.describe().to_string())

# eventDF = pd.DataFrame(mapped_events["events"])
#
# print(mapped_events["events"][0]["name"])


