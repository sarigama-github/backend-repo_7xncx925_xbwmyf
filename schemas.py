from typing import Optional, List
from pydantic import BaseModel, Field


class Product(BaseModel):
    name: str
    description: str
    price: float = Field(gt=0)
    image_url: str
    sizes: List[str] = Field(default_factory=list)
    type: str = Field(description="Style/type of the Kuse shoe, e.g., Khussa, Bridal, Casual")
    in_stock: bool = True


class Review(BaseModel):
    product_id: str
    name: str
    rating: int = Field(ge=1, le=5)
    comment: str


class OrderItem(BaseModel):
    product_id: str
    name: str
    size: str
    qty: int = Field(ge=1)
    price: float


class CustomerInfo(BaseModel):
    name: str
    email: str
    phone: str
    address: str


class Order(BaseModel):
    items: List[OrderItem]
    customer: CustomerInfo
    total: float = Field(ge=0)
