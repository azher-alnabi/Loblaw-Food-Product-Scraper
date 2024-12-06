import json
import os
import logging

from typing import List, Dict, Any
from datetime import datetime, timezone

from collections import defaultdict
from datetime import datetime


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


"""Data processing pipeline to combine and clean product data from multiple loblaw domains

This module takes in an array of domains (e.g. ["loblaws", "nofrills", "zehrs"]) and combines
product data from each domain into a single JSON file. The combined data is then saved to a file
called "combined_product_data.json" in the root directory. This combined product data is cleaned up
from any duplicate prices and saved in a format that can be easily upserted into a database.

Functions:
    - `extract_product_info`: This is a helper function that
      extracts relevant product information from a product object.
    - `add_price_if_unique`: This is a helper function that 
      adds a price to a product if it is unique to the product.
    - `convert_and_combine`: Combines product data from multiple domains into a single JSON file.
    - `save_combined_data`: Saves the combined product data to a JSON file.

Example usage:
    domains = ["loblaws", "nofrills", "zehrs"]
    combined_data = convert_and_combine(domains)
    save_combined_data(combined_data)
"""


def load_products_from_file(domain: str) -> List[Dict[str, Any]]:
    input_file = f"consolidated_product_data/{domain}_consolidated_product_data.json"
    try:
        with open(input_file, "r", encoding="utf-8") as file:
            logging.info(f"Loading products from {input_file}")
            return json.load(file)
    except FileNotFoundError:
        logging.error(f"File not found: {input_file}")
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON from {input_file}: {e}")
    return []


def extract_product_info(product: Dict[str, Any]) -> Dict[str, Any]:
    product_id = product.get("productId")

    small_url = None
    if product.get("productImage") and len(product["productImage"]) > 0:
        small_url = product["productImage"][0].get("smallUrl")
    if not small_url:
        small_url = "//assets.shop.loblaws.ca/products/NoImage/b1/en/front/NoImage_front_a06.png"

    brand = product.get("brand")
    title = product.get("title", "")
    price_str = product.get("pricing", {}).get("price", "0")
    price_cents = int(float(price_str) * 100)
    pricing_type = product.get("pricingUnits", {}).get("type", "")
    package_sizing = product.get("packageSizing", "")

    return {
        "productId": product_id,
        "smallUrl": small_url,
        "brand": brand,
        "title": title,
        "type": pricing_type,
        "price_cents": price_cents,
        "packageSizing": package_sizing,
    }


def add_price_if_unique(
    combined_data: Dict[str, Any],
    product_id: str,
    domain: str,
    price_cents: int,
    package_sizing: str,
) -> None:

    existing_prices = combined_data[product_id]["prices"]
    if not any(
        price["store"] == domain and price["price_cents"] == price_cents
        for price in existing_prices
    ):
        existing_prices.append(
            {
                "store": domain,
                "price_cents": price_cents,
                "packageSizing": package_sizing,
            }
        )
        logging.info(f"Added unique price for product {product_id} from {domain}")
    else:
        logging.debug(
            f"Duplicate price found for product {product_id} in {domain}, skipping."
        )


def convert_and_combine(domains: List[str]) -> List[Dict[str, Any]]:
    combined_data = defaultdict(
        lambda: {
            "productId": None,
            "smallUrl": None,
            "brand": None,
            "title": None,
            "type": None,
            "prices": [],
        }
    )

    for domain in domains:
        products = load_products_from_file(domain)
        logging.info(f"Processing {len(products)} products from {domain}")

        for product in products:
            info = extract_product_info(product)
            product_id = info["productId"]

            if combined_data[product_id]["productId"] is None:
                combined_data[product_id].update(
                    {
                        "productId": product_id,
                        "smallUrl": info["smallUrl"],
                        "brand": info["brand"],
                        "title": info["title"],
                        "type": info["type"],
                    }
                )
                logging.debug(f"Initialized product {product_id} in combined data.")

            add_price_if_unique(
                combined_data,
                product_id,
                domain,
                info["price_cents"],
                info["packageSizing"],
            )

    logging.info("Conversion and combination of product data complete.")
    return list(combined_data.values())


# Replace with msgspec later
def save_combined_data(
    combined_data: List[Dict[str, Any]],
    output_dir: str = "combined_product_data",
    base_filename: str = "combined_product_data.json",
) -> None:

    timestamp = datetime.now(timezone.utc).strftime("%Y_%m_%d_%H_%M")
    output_file = os.path.join(
        output_dir, f"{os.path.splitext(base_filename)[0]}_{timestamp}.json"
    )

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    try:
        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(combined_data, file, indent=4)
        logging.info(f"Combined data saved to {output_file}")
    except IOError as e:
        logging.error(f"Failed to save combined data to {output_file}: {e}")


if __name__ == "__main__":
    # Example usage
    domains = ["loblaws", "nofrills", "zehrs"]

    combined_data = convert_and_combine(domains)
    save_combined_data(combined_data)
