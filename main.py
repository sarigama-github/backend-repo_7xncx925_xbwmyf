from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
from bson import ObjectId
from database import db, create_document, get_documents
from schemas import Product, Review, Order

app = FastAPI(title="Kuse Shoes Store API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def serialize_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    if not doc:
        return doc
    d = dict(doc)
    if "_id" in d:
        d["id"] = str(d.pop("_id"))
    # Convert any nested ObjectIds
    for k, v in list(d.items()):
        if isinstance(v, ObjectId):
            d[k] = str(v)
        if isinstance(v, list):
            d[k] = [str(x) if isinstance(x, ObjectId) else x for x in v]
        if isinstance(v, dict):
            d[k] = serialize_doc(v)
    return d


@app.get("/")
def root():
    return {"message": "Kuse Shoes Store API is running"}


@app.get("/test")
def test_connection():
    try:
        collections = db.list_collection_names() if db else []
        return {
            "backend": "fastapi",
            "database": "mongodb",
            "database_url": "configured" if db else "missing",
            "database_name": db.name if db else None,
            "connection_status": "ok" if db else "unavailable",
            "collections": collections,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/seed")
def seed_products():
    products = get_documents("product", {}, limit=1)
    if products:
        return {"message": "Products already seeded"}
    sample_products = [
        {
            "name": "Royal Red Khussa",
            "description": "Handcrafted leather khussa with gold embroidery",
            "price": 59.99,
            "image_url": "https://images.unsplash.com/photo-1593032457862-bc35e5ad9d1d?q=80&w=1600&auto=format&fit=crop",
            "sizes": ["6", "7", "8", "9", "10"],
            "type": "Bridal",
            "in_stock": True,
        },
        {
            "name": "Classic Gold Khussa",
            "description": "Traditional gold-stitched khussa for festive wear",
            "price": 49.99,
            "image_url": "https://images.unsplash.com/photo-1520975916090-3105956dac38?q=80&w=1600&auto=format&fit=crop",
            "sizes": ["5", "6", "7", "8"],
            "type": "Festive",
            "in_stock": True,
        },
        {
            "name": "Everyday Comfort Khussa",
            "description": "Soft sole, perfect for daily wear with subtle gold accent",
            "price": 39.99,
            "image_url": "https://images.unsplash.com/photo-1528701800489-20be3c2ea1b3?q=80&w=1600&auto=format&fit=crop",
            "sizes": ["6", "7", "8", "9"],
            "type": "Casual",
            "in_stock": True,
        },
    ]
    for p in sample_products:
        create_document("product", p)
    return {"message": "Seeded sample products", "count": len(sample_products)}


@app.get("/products")
def list_products(
    size: Optional[str] = None,
    type: Optional[str] = Query(None, alias="ptype"),
):
    query: Dict[str, Any] = {}
    if size:
        query["sizes"] = {"$in": [size]}
    if type:
        query["type"] = type
    products = get_documents("product", query, limit=100)
    return [serialize_doc(p) for p in products]


@app.post("/products", status_code=201)
def create_product(product: Product):
    doc_id = create_document("product", product.dict())
    return {"id": doc_id}


@app.get("/reviews")
def list_reviews(product_id: Optional[str] = None):
    query: Dict[str, Any] = {}
    if product_id:
        query["product_id"] = product_id
    reviews = get_documents("review", query, limit=200)
    return [serialize_doc(r) for r in reviews]


@app.post("/reviews", status_code=201)
def create_review(review: Review):
    doc_id = create_document("review", review.dict())
    return {"id": doc_id}


@app.post("/orders", status_code=201)
def create_order(order: Order):
    order_id = create_document("order", order.dict())
    return {"message": "Order received", "id": order_id}
