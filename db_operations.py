import json
import logging
from sqlmodel import Session
from schema import ProductInfo, ProductPrice, engine


"""Database operations for upserting product data into the database.

This module contains functions for inserting and/or updating product information in the database,
when given a consolidated list of products in JSON format. An example of the supported JSON format 
can be found down below.

Functions:
    - `upsert_product`: Inserts or updates a product in the database based on the product ID.
    - `update_products_from_json`: Updates the database with product information from a JSON file.

Example usage:
    update_products_from_json("combined_product_data.json")
"""


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def upsert_product(product_data: dict):
    product_id = product_data["productId"]
    with Session(engine) as session:
        try:
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

        except Exception as e:
            logging.error(f"Error processing product {product_id}: {e}")
            session.rollback()


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
                "price_cents": 100,
                "packageSizing": "1 bunch, $1.00/1ea"
            },
            {
                "store": "nofrills",
                "price_cents": 129,
                "packageSizing": "1 bunch, $1.29/1ea"
            },
            {
                "store": "zehrs",
                "price_cents": 100,
                "packageSizing": "1 bunch, $1.00/1ea"
            }
        ]
    },
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
