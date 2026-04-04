import json

with open("sellers.json") as f:
    data = json.load(f)

sellers_list = data["Sellers"]
sellers = {
    seller["SellerName"]: {k: v for k, v in seller.items() if k != "SellerName"}
    for seller in sellers_list
}


#print(sellers["FIF HÃ¥ndbold"]["Configuration"]["VivenuAPIKey"])
#print(sellers_list[1]['Configuration']['VivenuURL'])



