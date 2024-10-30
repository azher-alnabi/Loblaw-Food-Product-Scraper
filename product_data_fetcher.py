from curl_cffi import requests as cr
import re
from web_request_converter import curl_to_requests, fetch_request
import msgspec
import os
import time
import random


"""Fetch and store paginated product data from API requests.

This module retrieves paginated JSON data from an API and saves each page's response as a formatted JSON file.
- `fetch_response`: Executes API requests for each page and calls serialization for each response.
- `response_serialization`: Decodes, formats, and saves the JSON response to a folder.

Example usage:
    curl_command = fetch_request("loblaws")
    fetch_response(max_pages=5, **curl_to_requests(curl_command))
"""


# I will come back and make this asynchonous later, also i can add a semaphore to limit the number of requests
def fetch_response(max_pages, method, url, headers, payload):
    output_folder = "raw_product_data"
    os.makedirs(output_folder, exist_ok=True)

    for pagination_number in range(1, max_pages + 1):
        updated_payload = re.sub(
            r'("from":\s*\d+)', f'"from": {pagination_number}', payload
        )

        response = cr.request(
            method, url, headers=headers, data=updated_payload, impersonate="chrome"
        )

        response_serialization(response.text, pagination_number, output_folder)
        time.sleep(random.random(0.75, 1.25))


def response_serialization(raw_response, pagination_number, output_folder):
    response_data = msgspec.json.decode(raw_response.encode("utf-8"))
    encoded_json = msgspec.json.encode(response_data)
    formatted_json = msgspec.json.format(encoded_json, indent=4)

    file_path = os.path.join(
        output_folder, f"raw_product_data_{pagination_number}.json"
    )
    with open(file_path, "wb") as json_file:
        json_file.write(formatted_json)


if __name__ == "__main__":
    # Example usage
    curl_command = fetch_request("loblaws")
    fetch_response(max_pages=1, **curl_to_requests(curl_command))
