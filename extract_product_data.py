import os
import msgspec
import logging

"""Extract product data from raw product data files and consolidate it into a single JSON file.

Functions:
    - `extract_product_data_from_files`: Extracts product data from raw product data files and consolidates it into a single JSON file.

Example usage:
    extract_product_data_from_files("loblaws")
"""

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def extract_product_data_from_files(domain):
    product_list = []
    directory_path = os.path.join("raw_product_data", f"{domain}_raw_product_data")

    for file_name in os.listdir(directory_path):
        if file_name.startswith(f"{domain}_raw_product_data_") and file_name.endswith(".json"):
            input_file_path = os.path.join(directory_path, file_name)

            with open(input_file_path, "rb") as file:
                data = msgspec.json.decode(file.read())

                product_grid = (
                    data.get("layout", {})
                    .get("sections", {})
                    .get("productListingSection", {})
                    .get("components", [{}])[0]
                    .get("data", {})
                    .get("productGrid", {})
                    .get("productTiles", [])
                )

                logging.info(f"Extracted {len(product_grid)} products from {file_name}")
                
                product_list.extend(product_grid)

    logging.info(f"Total products extracted: {len(product_list)}")

    output_folder = "consolidated_product_data"
    os.makedirs(output_folder, exist_ok=True)
    output_file_path = os.path.join(output_folder, f"{domain}_consolidated_product_data.json")

    encoded_json = msgspec.json.encode(product_list)
    formatted_json = msgspec.json.format(encoded_json, indent=4)

    with open(output_file_path, "wb") as json_file:
        json_file.write(formatted_json)

    logging.info(f"Data saved to {output_file_path}")


if __name__ == "__main__":
    # You can't execute this code as it is. You need to have the the directory "{domain}_raw_product_data" nested inside
    # the "raw_product_data" directory. The "{domain}_raw_product_data" directory should contain the JSON files with the
    # raw product data. Sample raw product data files are: loblaws_raw_product_data_1.json, loblaws_raw_product_data_2.json, etc.

    # Example usage
    extract_product_data_from_files("loblaws")
