def map_events(response_json):
    events = []

    for row in response_json.get("rows", []):
        event = {
            "id": row.get("_id"),
            "seller_id": row.get("sellerId"),
            "name": row.get("name"),
            "event_type": row.get("eventType"),
            "start": row.get("start"),
            "end": row.get("end"),
            "timezone": row.get("timezone"),
            "sell_start": row.get("sellStart"),
            "sell_end": row.get("sellEnd"),
            "location": {
                "name": row.get("locationName"),
                "street": row.get("locationStreet"),
                "city": row.get("locationCity"),
                "postal": row.get("locationPostal"),
                "country": row.get("locationCountry"),
            },
            "image": row.get("image"),
            "url": row.get("url"),
            "max_amount": row.get("maxAmount"),
            "max_per_order": row.get("maxAmountPerOrder"),
            "min_per_order": row.get("minAmountPerOrder"),
            "hide_in_listing": row.get("hideInListing", False),
            "child_events": row.get("childEvents", []),
            "tickets": [
                {
                    "id": t.get("_id"),
                    "name": t.get("name"),
                    "price": t.get("price"),
                    "amount": t.get("amount"),
                    "active": t.get("active"),
                }
                for t in row.get("tickets", [])
            ],
            "categories": [
                {
                    "id": c.get("_id"),
                    "name": c.get("name"),
                    "ref": c.get("ref"),
                    "amount": c.get("amount"),
                    "active": c.get("active"),
                }
                for c in row.get("categories", [])
            ],
            "created_at": row.get("createdAt"),
            "updated_at": row.get("updatedAt"),
        }
        events.append(event)

    return {
        "events": events,
        "total": response_json.get("total")
    }