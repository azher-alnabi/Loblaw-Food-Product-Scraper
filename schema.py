import json
import logging
from typing import Optional, List
from sqlmodel import Field, SQLModel, create_engine, Session, Relationship


"""This is the schema for the database that will store the product information.

This schema uses SQLModel to define the structure of the database tables. The tables involved
are "ProductInfo" and "ProductPrice".

- ProductInfo:
    Stores the general information about a product. This general information includes the
    following: product ID, small image URL, brand name, title name, and type. 
- ProductPrice:
    Stores the pricing information for a product at a specific store. The tables are related such 
    that a "ProductInfo" can have multiple "ProductPrices" associated with it.

Functions:
    - `upsert_product`: Inserts or updates a product in the database based on the product ID.
    - `update_products_from_json`: Updates the database with product information from a JSON file.

Example usage:
    update_products_from_json("combined_product_data.json")
"""


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/database_operations.log"),
        logging.StreamHandler(),
    ],
)


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


class ProductPrice(SQLModel, table=True):
    product_id: str = Field(foreign_key="productinfo.product_id", primary_key=True)
    store: str = Field(primary_key=True)
    price_cents: Optional[int] = None
    package_sizing: str
    product: ProductInfo = Relationship(back_populates="prices")


# Replace with PostgreSQL later
engine = create_engine("sqlite:///database.db")
SQLModel.metadata.create_all(engine)


def upsert_product(product_data: dict):
    product_id = product_data["productId"]
    with Session(engine) as session:
        product = session.get(ProductInfo, product_id)

        if product:
            product.small_image_url = product_data["smallUrl"]
            product.brand_name = product_data.get("brand")
            product.title_name = product_data["title"]
            product.type = product_data["type"]

            price_dict = {price.store: price for price in product.prices}
            for new_price in product_data["prices"]:
                store = new_price["store"]
                if store in price_dict:
                    price_dict[store].price_cents = new_price["price_cents"]
                    price_dict[store].package_sizing = new_price["packageSizing"]
                else:
                    product.prices.append(
                        ProductPrice(
                            store=store,
                            price_cents=new_price["price_cents"],
                            package_sizing=new_price["packageSizing"],
                        )
                    )
            logging.info(f"Updated product: {product_id}")

        else:
            product = ProductInfo(
                product_id=product_id,
                small_image_url=product_data["smallUrl"],
                brand_name=product_data.get("brand"),
                title_name=product_data["title"],
                type=product_data["type"],
                prices=[
                    ProductPrice(
                        store=price["store"],
                        price_cents=price["price_cents"],
                        package_sizing=price["packageSizing"],
                    )
                    for price in product_data["prices"]
                ],
            )
            session.add(product)
            logging.info(f"Inserted new product: {product_id}")

        session.commit()
        session.refresh(product)


# Replace with msgspec later
def update_products_from_json(json_file_path: str):
    try:
        with open(json_file_path, "r") as file:
            products_data = json.load(file)
        logging.info(f"Loaded JSON data from {json_file_path}")

    except FileNotFoundError:
        logging.error(f"File not found: {json_file_path}")
        return

    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON from {json_file_path}: {e}")
        return

    for product_data in products_data:
        try:
            upsert_product(product_data)
        except Exception as e:
            logging.error(
                f"Failed to upsert product {product_data.get('productId', 'unknown')}: {e}"
            )


if __name__ == "__main__":
    # Example usage
    update_products_from_json("combined_product_data.json")


"""
Here is the format of the JSON file called "combined_product_data.json".
This will be consumed by this script to upsert the database in a bulk operation.

```json
[
    {
        "productId": "20091825001_EA",
        "smallUrl": "https://assets.shop.loblaws.ca/products/20091825001/b1/en/front/20091825001_front_a01_@2.png",
        "brand": null,
        "title": "Cilantro",
        "type": "SOLD_BY_EACH",
        "prices": [
            {
                "store": "loblaws",
                "price_cents": 100
                "packageSizing": "1 bunch, $1.00/1ea"
            },
            {
                "store": "nofrills",
                "price_cents": 129
                "packageSizing": "1 bunch, $1.29/1ea"
            },
            {
                "store": "zehrs",
                "price_cents": 100
                "packageSizing": "1 bunch, $1.00/1ea"
            }
        ]
    }   
    {
        "productId": "20143381001_KG",
        "smallUrl": "https://assets.shop.loblaws.ca/products/20143381001/b1/en/front/20143381001_front_a01_@2.png",
        "brand": null,
        "title": "Roma Tomatoes",
        "type": "SOLD_BY_EACH_PRICED_BY_WEIGHT",
        "prices": [
            {
                "store": "loblaws",
                "price_cents": 79,
                "packageSizing": "$6.61/1kg $3.00/1lb"
            },
            {
                "store": "nofrills",
                "price_cents": 79,
                "packageSizing": "$6.61/1kg $3.00/1lb"
            },
            {
                "store": "zehrs",
                "price_cents": 79,
                "packageSizing": "$6.61/1kg $3.00/1lb"
            }
        ]
    }
]
```
"""
