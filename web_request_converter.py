from playwright.sync_api import sync_playwright
import re


"""
Capture, convert, and reformat web requests into cURL and Python requests.

This module captures network requests from Loblaws-affiliated websites (such as Loblaws, 
No Frills, and Zehrs), converts them into cURL commands, and then translates these commands 
into Python `requests` format for further processing.

Functions:
- `request_to_curl`: Converts a captured Playwright request to a cURL command.
- `fetch_request`: Navigates to a specified Loblaws domain URL, captures a network request, and 
  returns it as a cURL command.
- `curl_to_requests`: Parses a cURL command into Python `requests` format, extracting method, 
  URL, headers, and payload.

Example usage:
    curl_command = fetch_request("loblaws")
    request_details = curl_to_requests(curl_command)
"""


def request_to_curl(request):
    curl_command = f"curl '{request.url}' --compressed -X {request.method}"

    for key, value in request.headers.items():
        curl_command += f" -H '{key}: {value}'"

    if request.method == "POST" and request.post_data:
        curl_command += f" --data-raw '{request.post_data}'"

    return curl_command


def fetch_request(domain):
    url = f"https://www.{domain}.ca/food/c/27985"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        with page.expect_request(
            "https://api.pcexpress.ca/pcx-bff/api/v2/listingPage/27985"
        ) as first:
            page.goto(url)

        captured_request = first.value
        curl_command = request_to_curl(captured_request)

        browser.close()

    return curl_command


def curl_to_requests(curl_command):
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

    return {"method": method, "url": url, "headers": headers, "payload": payload}


if __name__ == "__main__":
    # Example usage
    curl_command = fetch_request("loblaws")
    curl_to_requests(curl_command)
