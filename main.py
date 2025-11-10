import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Sneaker, Cart, CartItem

app = FastAPI(title="Sneaker Store API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Utility to convert Mongo docs
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)


def serialize_doc(doc):
    if not doc:
        return doc
    doc["id"] = str(doc.pop("_id"))
    return doc


@app.get("/")
def read_root():
    return {"message": "Sneaker Store API running"}


@app.get("/schema")
def get_schema():
    # basic info for viewer
    return {
        "collections": ["sneaker", "cart"],
    }


# Seed initial sneakers if collection empty
@app.post("/seed")
def seed_products():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    count = db["sneaker"].count_documents({})
    if count > 0:
        return {"inserted": 0, "message": "Already seeded"}

    sneakers: List[Sneaker] = [
        Sneaker(
            name="Air Jordan 1 Retro High",
            brand="Nike",
            price=180.0,
            image="https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=1200&q=80",
            colorway="Bred",
            description="Iconic high-top with premium leather and timeless style.",
            rating=4.8,
        ),
        Sneaker(
            name="Yeezy Boost 350 V2",
            brand="adidas",
            price=220.0,
            image="https://images.unsplash.com/photo-1542293787938-c9e299b88054?w=1200&q=80",
            colorway="Zebra",
            description="Primeknit upper with Boost cushioning for all-day comfort.",
            rating=4.6,
        ),
        Sneaker(
            name="New Balance 550",
            brand="New Balance",
            price=110.0,
            image="https://images.unsplash.com/photo-1603808033192-65fe6f565c95?w=1200&q=80",
            colorway="White/Green",
            description="Retro basketball silhouette with modern comfort.",
            rating=4.4,
        ),
        Sneaker(
            name="Nike Air Max 97",
            brand="Nike",
            price=175.0,
            image="https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=1200&q=80",
            colorway="Silver Bullet",
            description="Wavy lines and visible Air cushioning for a smooth ride.",
            rating=4.5,
        ),
        Sneaker(
            name="ASICS Gel-Kayano 14",
            brand="ASICS",
            price=150.0,
            image="https://images.unsplash.com/photo-1605346476686-c9c5c70c8f47?w=1200&q=80",
            colorway="Metallic Silver",
            description="Reissued runner with GEL cushioning and 2000s aesthetics.",
            rating=4.7,
        ),
    ]

    inserted_ids = []
    for s in sneakers:
        _id = create_document("sneaker", s)
        inserted_ids.append(_id)

    return {"inserted": len(inserted_ids), "ids": inserted_ids}


@app.get("/products")
def list_products():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    docs = get_documents("sneaker")
    return [serialize_doc(d) for d in docs]


class AddToCartPayload(BaseModel):
    product_id: str
    quantity: int = 1
    size: int


@app.post("/cart/add")
def add_to_cart(payload: AddToCartPayload):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    prod = db["sneaker"].find_one({"_id": ObjectId(payload.product_id)})
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")

    item = CartItem(
        product_id=str(prod["_id"]),
        quantity=payload.quantity,
        size=payload.size,
        price=float(prod["price"]),
        name=prod["name"],
        image=prod["image"],
        brand=prod["brand"],
    )

    # For demo, create a separate cart document each time (no auth)
    cart = Cart(items=[item])

    # compute totals
    subtotal = sum(i.price * i.quantity for i in cart.items)
    tax = round(subtotal * 0.08, 2)
    total = round(subtotal + tax, 2)
    cart.subtotal = round(subtotal, 2)
    cart.tax = tax
    cart.total = total

    cart_id = create_document("cart", cart)
    return {"cart_id": cart_id, "cart": cart.model_dump()}


@app.get("/cart/{cart_id}")
def get_cart(cart_id: str):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    doc = db["cart"].find_one({"_id": ObjectId(cart_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Cart not found")

    doc = serialize_doc(doc)
    return doc


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
