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

# Affiliate marketing assistant app schemas

class AffiliateLink(BaseModel):
    """
    Affiliate links the user wants to promote.
    Collection name: "affiliatelink" (lowercase of class name)
    """
    title: str = Field(..., description="Product or offer title")
    url: str = Field(..., description="Destination URL (e.g., Lynk.id or merchant link)")
    code: str = Field(..., description="Short code for tracking, used in /r/{code}")
    platform: Optional[str] = Field(None, description="Primary platform audience (IG/TikTok/YouTube/etc)")
    commission_rate: Optional[float] = Field(None, ge=0, le=100, description="Estimated commission %")
    tags: Optional[List[str]] = Field(default=None, description="Tags or niches")
    image: Optional[str] = Field(default=None, description="Image URL for thumbnail")

class Click(BaseModel):
    """
    Click logs for redirects.
    Collection name: "click".
    """
    link_code: str = Field(..., description="AffiliateLink.code")
    source: Optional[str] = Field(None, description="Source parameter or platform")
    ip: Optional[str] = Field(None, description="IP address (best-effort)")
    user_agent: Optional[str] = Field(None, description="User agent string")
