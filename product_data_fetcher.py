from curl_cffi import requests as cr
import re
import msgspec
import os
import time
import random
import logging


"""Fetch and store paginated product data from API requests.

This module retrieves paginated JSON data from an API and saves each page's response as a formatted JSON file.

Functions:
    - `fetch_response`: Executes API requests for each page of product data, checks response status, 
      and logs successes or access restrictions. Calls `response_serialization` for each response.
    - `response_serialization`: Decodes, formats, and saves the JSON response to a domain-specific 
      output folder as a JSON file.

Example usage:
    curl_command, domain = fetch_request("loblaws")
    fetch_response(**curl_to_requests(curl_command, domain))
"""


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def fetch_response(method, url, headers, payload, domain):
    output_folder = os.path.join("raw_product_data", f"{domain}_raw_product_data")
    os.makedirs(output_folder, exist_ok=True)

    consecutive_none_count = 0
    pagination_number = 1

    while consecutive_none_count < 3:
        updated_payload = re.sub(
            r'("from":\s*\d+)', f'"from": {pagination_number}', payload
        )

        response = cr.request(
            method, url, headers=headers, data=updated_payload, impersonate="chrome"
        )

        if response.status_code == 200:
            logging.info(
                f"Request for page {pagination_number} succeeded with status 200."
            )

        elif response.status_code == 403:
            logging.warning(
                f"Request for page {pagination_number} returned forbidden status 403."
            )

        else:
            logging.info(
                f"Request for page {pagination_number} returned status {response.status_code}."
            )

        response_serialization(response.text, pagination_number, output_folder, domain)
        logging.info(f"{domain}_raw_product_data_{pagination_number} created.")

        file_path = os.path.join(
            output_folder, f"{domain}_raw_product_data_{pagination_number}.json"
        )

        if check_product_grid_value(file_path):
            consecutive_none_count += 1
            logging.info(
                f"Consecutive 'productGrid is None' count: {consecutive_none_count}"
            )

        else:
            consecutive_none_count = 0

        if consecutive_none_count >= 3:
            logging.info(
                "Exiting loop after 3 consecutive 'productGrid is None' results."
            )
            break

        pagination_number += 1
        time.sleep(random.normalvariate(0.5, 0.05))


def response_serialization(raw_response, pagination_number, output_folder, domain):
    response_data = msgspec.json.decode(raw_response.encode("utf-8"))
    encoded_json = msgspec.json.encode(response_data)
    formatted_json = msgspec.json.format(encoded_json, indent=4)

    file_path = os.path.join(
        output_folder, f"{domain}_raw_product_data_{pagination_number}.json"
    )
    with open(file_path, "wb") as json_file:
        json_file.write(formatted_json)


def check_product_grid_value(file_path):
    with open(file_path, "rb") as file:
        data = msgspec.json.decode(file.read())

        try:
            product_grid_value = data["layout"]["sections"]["productListingSection"]["components"][0]["data"]["productGrid"]
            return product_grid_value is None

        except KeyError:
            logging.warning(f"Key 'productGrid' not found in {file_path}")
            return False


if __name__ == "__main__":
    # Import functions from web_request_converter.py
    from web_request_converter import curl_to_requests, fetch_request

    # Example usage
    curl_command, domain = fetch_request("loblaws")
    fetch_response(**curl_to_requests(curl_command, domain))
