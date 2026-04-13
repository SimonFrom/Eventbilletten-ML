import requests


baseUrl = "https://vivenu.com/api/"


def getEventsPerSeller(token):
    #print(f"Token received: '{token}'")
    headers = {"Authorization": f"Bearer {token}"}
    all_docs = []
    skip = 0
    top = 100

    while True:
        response = requests.get(
            url=f"{baseUrl}events?top={top}&skip={skip}",
            headers=headers
        )

        if response.status_code == 200:
            #print(response.json())
            print("Repsonse received")
            return response.json()

        data = response.json()
        rows = data.get("rows", [])
        all_docs.extend(rows)

        total = data.get("total", 0)
        skip += top

        print(f"Fetched events {len(all_docs)}/{total}")

        if skip >= total:
            break

    return {"docs": all_docs, "total": len(all_docs)}


def getOrdersPerSeller(token):
    headers = {"Authorization": f"Bearer {token}"}
    all_docs = []
    skip = 0
    top = 100

    while True:
        response = requests.get(
            url=f"{baseUrl}transactions?top={top}&skip={skip}",
            headers=headers
        )

        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
            break

        data = response.json()
        docs = data.get("docs", [])
        all_docs.extend(docs)

        total = data.get("total", 0)
        skip += top

        print(f"Fetched orders {len(all_docs)}/{total}")

        if skip >= total:
            break

    return {"docs": all_docs, "total": len(all_docs)}