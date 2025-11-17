import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import MenuItem, Reservation

app = FastAPI(title="Napoli Restaurant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def seed_menu_if_empty():
    try:
        if db is None:
            return
        count = db["menuitem"].count_documents({})
        if count == 0:
            sample_items = [
                # Antipasti
                MenuItem(name="Bruschetta al Pomodoro", description="Grilled bread, marinated tomatoes, basil, EVOO", price=9.5, category="Antipasti", is_vegetarian=True, is_spicy=False),
                MenuItem(name="Calamari Fritti", description="Crispy squid with lemon aioli", price=14.0, category="Antipasti"),
                # Pizza
                MenuItem(name="Margherita DOP", description="San Marzano, fior di latte, basil, EVOO", price=16.0, category="Pizza", is_vegetarian=True),
                MenuItem(name="Diavola", description="Spicy salami, mozzarella, chili oil", price=18.5, category="Pizza", is_spicy=True),
                # Pasta
                MenuItem(name="Spaghetti alle Vongole", description="Manila clams, garlic, white wine, parsley", price=22.0, category="Pasta"),
                MenuItem(name="Rigatoni alla Norma", description="Eggplant, tomato, ricotta salata", price=19.0, category="Pasta", is_vegetarian=True),
                # Secondi
                MenuItem(name="Pollo al Limone", description="Roasted chicken, lemon-caper sauce", price=24.0, category="Secondi"),
                MenuItem(name="Branzino Arrosto", description="Whole roasted sea bass, herbs, charred lemon", price=32.0, category="Secondi"),
                # Dolci
                MenuItem(name="Tiramisù", description="Espresso-soaked ladyfingers, mascarpone", price=10.0, category="Dolci", is_vegetarian=True),
                MenuItem(name="Panna Cotta al Limone", description="Silky lemon panna cotta, berry coulis", price=9.0, category="Dolci", is_vegetarian=True),
            ]
            for it in sample_items:
                create_document("menuitem", it)
            print("Seeded sample menu items for Napoli.")
    except Exception as e:
        print(f"Menu seed error: {e}")

@app.get("/")
def read_root():
    return {"message": "Napoli Restaurant Backend is running"}

@app.get("/api/menu", response_model=List[MenuItem])
def get_menu(category: Optional[str] = None):
    try:
        filter_q = {"category": category} if category else {}
        items = get_documents("menuitem", filter_q)
        return [MenuItem(**{k: v for k, v in item.items() if k not in ["_id", "created_at", "updated_at"]}) for item in items]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/menu", status_code=201)
def add_menu_item(item: MenuItem):
    try:
        inserted_id = create_document("menuitem", item)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ReservationResponse(BaseModel):
    id: str

@app.post("/api/reservations", response_model=ReservationResponse, status_code=201)
def create_reservation(res: Reservation):
    try:
        inserted_id = create_document("reservation", res)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reservations")
def list_reservations(limit: int = 50):
    try:
        items = get_documents("reservation", {}, limit=limit)
        for item in items:
            if isinstance(item.get("_id"), ObjectId):
                item["id"] = str(item.pop("_id"))
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
