from product_data_fetcher import fetch_response
from web_request_converter import curl_to_requests, fetch_request
from extract_product_data import extract_product_data_from_files


def main(domain, max_pages=1):
    curl_command, domain = fetch_request(domain)
    fetch_response(max_pages, **curl_to_requests(curl_command, domain))
    extract_product_data_from_files(domain)


if __name__ == "__main__":
    domain = "zehrs"
    main(domain, max_pages=209)
