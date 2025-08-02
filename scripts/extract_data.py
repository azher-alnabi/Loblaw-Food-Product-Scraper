import json
import logging
from sqlmodel import Session, select
from database.schema import ProductInfo, engine


"""Script to return a snapshot of the product data from the db.

Doesn't return the "updated_at" field, as this just pulls product information.

Functions:
    - `extract_data_to_json`: Extracts product data from the database and writes it to a JSON file.

Example usage:
    update_products_from_json("foods.json")
"""


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def extract_data_to_json(output_file: str) -> None:
    logging.info(f"Beginning to extract data from database into {output_file}")
    
    with Session(engine) as session:
        statement = select(ProductInfo)
        products = session.exec(statement).all()

        data = []
        for product in products:
            product_data = {
                "productId": product.product_id,
                "smallUrl": product.small_image_url,
                "brand": product.brand_name,
                "title": product.title_name,
                "type": product.type,
                "prices": [
                    {
                        "store": price.store,
                        "price_cents": price.price_cents,
                        "packageSizing": price.package_sizing,
                    }
                    for price in product.prices
                ],
            }
            data.append(product_data)

        # Replace with msgspec later
        with open(output_file, "w") as file:
            json.dump(data, file, indent=4)

        logging.info(f"Data extracted to {output_file}")


if __name__ == "__main__":
    extract_data_to_json("foods.json")