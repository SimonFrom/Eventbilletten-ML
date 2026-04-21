from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from event_draw_profile import getEventDrawProfile
from sell_window import getSellWindowMetrics, getSellWindowCategoryProfile
from models import (
    EventDrawProfileModel,
    SellWindowMetricsModel,
    SellWindowCategoryModel,
    ApiResponse
)


buyer_features_path = "csv/buyerFeatures.csv"
cache = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading data into cache...")
    cache["event_draw_profile"] = getEventDrawProfile(buyer_features_path)
    cache["sell_window"] = getSellWindowMetrics(buyer_features_path)
    cache["sell_window_categories"] = getSellWindowCategoryProfile(buyer_features_path)
    print("Cache filled...")
    yield
    cache.clear()


app = FastAPI(title="Eventbilletten ML API", version="1.0.0", lifespan=lifespan)

# ---- CORS ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---- Connection check ----
@app.get("/")
def root():
    return {"status": "OK", "message": "Welcome to Eventbilletten ML API"}

# Returns draw profile metrics for every event
@app.get("/event_draw_profile", response_model=ApiResponse)
def event_draw_profile():
    data = getEventDrawProfile(buyer_features_path)
    return {"count": len(data), "Data": data}

@app.get("/sell_window", response_model=ApiResponse)
def sell_window():
    data = getSellWindowMetrics(buyer_features_path)
    return {"count": len(data), "Data": data}

@app.get("/sell_window/categories", response_model=ApiResponse)
def sell_window_categories():
    data = getSellWindowCategoryProfile(buyer_features_path)
    return {"count": len(data), "Data": data}