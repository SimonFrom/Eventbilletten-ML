def map_orders(response_json):
    orders = []
    for doc in response_json.get("docs", []):
        order = {
            "id": doc.get("_id"),
            "seller_id": doc.get("sellerId"),
            "event_id": doc.get("eventId"),
            "name": doc.get("name"),           # ← top level, not nested
            "email": doc.get("email"),
            "phone": doc.get("phone"),
            "city": doc.get("city"),
            "country": doc.get("country"),
            "postal": doc.get("postal"),
            "status": doc.get("status"),
            "payment_status": doc.get("paymentStatus"),
            "real_price": doc.get("realPrice"),
            "currency": doc.get("currency"),
            "tickets": doc.get("tickets", []),
            "created_at": doc.get("createdAt"),
        }
        orders.append(order)
    return {"orders": orders, "total": response_json.get("total")}