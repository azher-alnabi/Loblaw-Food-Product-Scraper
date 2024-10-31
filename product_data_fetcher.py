from curl_cffi import requests as cr
import re
from web_request_converter import curl_to_requests, fetch_request
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
    fetch_response(max_pages=5, **curl_to_requests(curl_command, domain))
"""


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def fetch_response(max_pages, method, url, headers, payload, domain):
    output_folder = f"{domain}_raw_product_data"
    os.makedirs(output_folder, exist_ok=True)

    for pagination_number in range(1, max_pages + 1):
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
        print(f"{domain}_raw_product_data_{pagination_number} created.")
        time.sleep(random.normalvariate(1, 0.05))


def response_serialization(raw_response, pagination_number, output_folder, domain):
    response_data = msgspec.json.decode(raw_response.encode("utf-8"))
    encoded_json = msgspec.json.encode(response_data)
    formatted_json = msgspec.json.format(encoded_json, indent=4)

    file_path = os.path.join(
        output_folder, f"{domain}_raw_product_data_{pagination_number}.json"
    )
    with open(file_path, "wb") as json_file:
        json_file.write(formatted_json)


if __name__ == "__main__":
    # Example usage
    curl_command, domain = fetch_request("loblaws")
    fetch_response(max_pages=5, **curl_to_requests(curl_command, domain))