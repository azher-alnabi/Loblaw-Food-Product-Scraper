import argparse
import json
import sys
import os
import glob
import shutil
import logging

from product_data_fetcher import fetch_response
from web_request_converter import curl_to_requests, fetch_request
from extract_product_data import extract_product_data_from_files

from data_pipeline import convert_and_combine, save_combined_data
from db_operations import update_products_from_json


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def sync_extract(domains: list[str]) -> None:
    logging.info("Starting data extraction process")

    for domain in domains:
        curl_command, domain = fetch_request(domain)
        fetch_response(**curl_to_requests(curl_command, domain))
        extract_product_data_from_files(domain)


def transform(domains: list[str]) -> None:
    logging.info(
        "Starting transformation of unprocessed data into a consolidated format"
    )

    combined_data = convert_and_combine(domains)
    save_combined_data(combined_data)

    if os.path.exists("consolidated_product_data"):
        shutil.rmtree("consolidated_product_data")

    if os.path.exists("raw_product_data"):
        shutil.rmtree("raw_product_data")


def load(input_json_cleaned_data: str) -> None:
    logging.info("Starting loading cleaned data into the database")

    update_products_from_json(input_json_cleaned_data)


def parse_arguments(supported_domains: list[str]) -> list:
    parser = argparse.ArgumentParser(description="Webscraper CLI")
    parser.add_argument(
        "-all", action="store_true", help="Harvest all supported domains"
    )
    parser.add_argument("domains", nargs="*", help="Specify domains to harvest")

    args = parser.parse_args()

    if args.all:
        return supported_domains

    if args.domains:
        invalid = [domain for domain in args.domains if domain not in supported_domains]
        if invalid:
            print(f"Invalid domains: {', '.join(invalid)}")
            print("Available domains:")
            print("\n".join(f"- {domain}" for domain in supported_domains))
            sys.exit(1)
        return args.domains

    parser.print_help()
    sys.exit(1)


def get_latest_combined_data_file(directory: str = "combined_product_data") -> str:
    files = glob.glob(os.path.join(directory, "combined_product_data_*.json"))
    if not files:
        logging.error("No combined product data files found.")
        sys.exit(1)
    latest_file = max(files, key=os.path.getctime)
    return latest_file


def main(domains: list) -> None:
    sync_extract(domains)
    transform(domains)
    load(get_latest_combined_data_file())


if __name__ == "__main__":
    # os.makedirs("logs", exist_ok=True)
    # I will need to create a logs folder in the root directory at a later time

    json_file = "supported_domains.json"

    try:
        with open(json_file, "r") as file:
            supported_domains = json.load(file)

    except FileNotFoundError:
        print(f"Error: {json_file} not found.")
        sys.exit(1)

    selected_domains = parse_arguments(supported_domains)

    main(selected_domains)
