from playwright.sync_api import sync_playwright, Request
import re
import logging
from typing import Tuple, Dict, Optional


"""Capture, convert, and reformat web requests into cURL and Python requests.

This module captures network requests from Loblaws-affiliated websites (such as Loblaws, 
No Frills, and Zehrs), converts them into cURL commands, and then translates these commands 
into Python `requests` format for further processing. This is used to mimic how a session
works in a browser and to automate the process of fetching product data from these websites.

Functions:
    - `fetch_request`: Navigates to a given Loblaws domain URL, captures a specific network request, 
      and returns the request as a cURL command.
    - `request_to_curl`: Converts a Playwright-captured request into a formatted cURL command.
    - `curl_to_requests`: Parses a cURL command into a Python `requests` dictionary with method, URL, 
      headers, and payload details for direct use in Python scripts.

Example usage:
    curl_command, domain = fetch_request("loblaws")
    request_details = curl_to_requests(curl_command, domain)
"""


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def fetch_request(domain: str) -> Tuple[str, str]:
    url = f"https://www.{domain}.ca/food/c/27985"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        with page.expect_response(
            "https://api.pcexpress.ca/pcx-bff/api/v2/listingPage/27985"
        ) as response_info:
            page.goto(url)

        captured_response = response_info.value
        response_status = captured_response.status

        if response_status == 200:
            logging.info(
                f"Request to {captured_response.url} succeeded with status 200."
            )
        elif response_status == 403:
            logging.warning(
                f"Request to {captured_response.url} returned forbidden status 403."
            )
        else:
            logging.info(
                f"Request to {captured_response.url} failed with status {response_status}."
            )

        captured_request = captured_response.request
        curl_command = request_to_curl(captured_request)

        browser.close()

    return curl_command, domain


def request_to_curl(request: Request) -> str:
    curl_command = f"curl '{request.url}' --compressed -X {request.method}"

    for key, value in request.headers.items():
        curl_command += f" -H '{key}: {value}'"

    if request.method == "POST" and request.post_data:
        curl_command += f" --data-raw '{request.post_data}'"

    return curl_command


def curl_to_requests(curl_command: str, domain: str) -> Dict[str, Optional[str]]:
    method_match = re.search(r"-X (\w+)", curl_command)
    method = method_match.group(1) if method_match else "GET"

    url_match = re.search(r"curl '([^']*)'", curl_command)
    url = url_match.group(1) if url_match else ""

    headers = {}
    header_matches = re.findall(r"-H '([^:]*): ([^']*)'", curl_command)
    for header, value in header_matches:
        headers[header] = value

    data_match = re.search(r"--data-raw '([^']*)'", curl_command)
    payload = data_match.group(1) if data_match else None

    return {
        "method": method,
        "url": url,
        "headers": headers,
        "payload": payload,
        "domain": domain,
    }


if __name__ == "__main__":
    # Example usage
    curl_command, domain = fetch_request("loblaws")
    request_details = curl_to_requests(curl_command, domain)
