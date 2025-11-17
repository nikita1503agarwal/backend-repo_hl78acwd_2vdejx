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

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import date as DateType, time as TimeType

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

# Napoli Restaurant Schemas

class MenuItem(BaseModel):
    """Menu items for Napoli restaurant
    Collection: "menuitem"
    """
    name: str = Field(..., description="Dish name")
    description: Optional[str] = Field(None, description="Dish description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Category e.g., Antipasti, Pizza, Pasta, Dolci")
    is_vegetarian: bool = Field(False, description="Vegetarian option")
    is_spicy: bool = Field(False, description="Spicy indicator")

class Reservation(BaseModel):
    """Reservations for Napoli
    Collection: "reservation"
    """
    name: str = Field(..., min_length=2, description="Guest full name")
    email: EmailStr = Field(..., description="Guest email")
    phone: str = Field(..., min_length=7, description="Contact phone")
    party_size: int = Field(..., ge=1, le=20, description="Number of guests")
    reservation_date: DateType = Field(..., description="Reservation date")
    reservation_time: TimeType = Field(..., description="Reservation time")
    notes: Optional[str] = Field(None, max_length=500, description="Special requests")
