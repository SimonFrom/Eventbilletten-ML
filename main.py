from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from event_draw_profile import getEventDrawProfile
from sell_window import getSellWindowMetrics, getSellWindowCategoryProfile

app = FastAPI(title="Eventbilletten ML API", version="1.0.0")

# ── CORS ──────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

buyer_features_path = "csv/buyerFeatures.csv"

# ---- Connection check ----
@app.get("/")
def root():
    return {"status": "OK", "message": "Welcome to Eventbilletten ML API"}

# Returns draw profile metrics for every event
@app.get("/event_draw_profile")
def event_draw_profile():
    data = getEventDrawProfile(buyer_features_path)
    return {"count": len(data), "Data": data}

@app.get("/sell_window")
def sell_window():
    data = getSellWindowMetrics(buyer_features_path)
    return {"count": len(data), "Data": data}

@app.get("/sell_window/categories")
def sell_window_categories():
    data = getSellWindowCategoryProfile(buyer_features_path)
    return {"count": len(data), "Data": data}