from typing import Optional, List
from sqlmodel import Field, SQLModel, create_engine, Relationship

from datetime import datetime, timezone


"""This is the schema for the database that will store the product information.

This schema uses SQLModel to define the structure of the database tables. The tables involved
are "ProductInfo" and "ProductPrice".

Table Descriptions:
- ProductInfo:
    Stores the general information about a product. This general information includes the
    following: product ID, small image URL, brand name, title name, and type. 
- ProductPrice:
    Stores the pricing information for a product at a specific store. The tables are related such 
    that a "ProductInfo" can have multiple "ProductPrices" associated with it.
"""


class ProductInfo(SQLModel, table=True):
    product_id: str = Field(primary_key=True)
    small_image_url: str
    brand_name: Optional[str] = None
    title_name: str
    type: str
    prices: List["ProductPrice"] = Relationship(
        back_populates="product",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


## I need to look into temporal tables and how to implement them in SQLModel
## Temporal tables store historical data, which is useful in this case for tracking price changes
class ProductPrice(SQLModel, table=True):
    product_id: str = Field(foreign_key="productinfo.product_id", primary_key=True)
    store: str = Field(primary_key=True)
    price_cents: Optional[int] = None
    package_sizing: str
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    product: ProductInfo = Relationship(back_populates="prices")


engine = create_engine("sqlite:///database.db")
SQLModel.metadata.create_all(engine)
