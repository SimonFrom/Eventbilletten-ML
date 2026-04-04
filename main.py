import httpRequests
import httpRequests as http
from loadJSON import sellers_list
import eventResponse as event

test_key = "key_674285ea23414d0f482c5baaa2d11eb99241707cff12665f344528dfd414a2629b3010369f9a7414851551bf1f41cd73";
mapped_events = []


def getDataForSeller(token):
    data = http.getEventsPerSeller(token)
    mapped_events = event.map_events(data)

getDataForSeller(test_key)
print(mapped_events[1])


# for seller in sellers_list:
#     print(f"Getting events for seller {seller['SellerName']}")
#     http.getEventsPerSeller(seller['Configuration']['VivenuAPIKey'])
#     print("----- Done -----")

# httpRequests.getEventsPerSeller(sellers_list[1]['Configuration']['VivenuAPIKey'])