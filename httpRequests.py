import requests

baseUrl = "https://vivenu.com/api/"

def getEventsPerSeller(token):
    print(f"Token received: '{token}'")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url=f"{baseUrl}events?top=1000&skip=0", headers=headers)

    if response.status_code == 200:
        print(response.json())
    else:
        print(f"Error: {response.status_code}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
