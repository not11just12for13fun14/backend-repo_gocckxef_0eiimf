"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Sneaker-specific product used by the app
class Sneaker(BaseModel):
    name: str
    brand: str
    price: float = Field(..., ge=0)
    image: str = Field(..., description="Image URL")
    colorway: Optional[str] = None
    description: Optional[str] = None
    sizes: List[int] = Field(default_factory=lambda: [6,7,8,9,10,11,12])
    in_stock: bool = True
    rating: float = Field(4.5, ge=0, le=5)

# Cart schemas
class CartItem(BaseModel):
    product_id: str
    quantity: int = Field(1, ge=1)
    size: int = Field(..., ge=1)
    price: float = Field(..., ge=0, description="Unit price snapshot")
    name: str
    image: str
    brand: str

class Cart(BaseModel):
    items: List[CartItem] = Field(default_factory=list)
    status: str = Field("open", description="open|paid|abandoned")
    subtotal: float = 0.0
    tax: float = 0.0
    total: float = 0.0

# Add your own schemas here:
# --------------------------------------------------

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
