from playwright.sync_api import sync_playwright
import json

'''


'''


def initalize(web_domain, semaphore_limit):
    with sync_playwright() as playwright:
        start_url = f"https://www.{web_domain}.ca/food/c/27985"
        chrome = playwright.chromium
        browser = chrome.launch(headless=False)
        page = browser.new_page()
        page.goto(start_url)
        page.wait_for_selector('.css-1rb8z0p', timeout=60000)
        end_page_number = int(page.query_selector_all('a.chakra-link.css-1vwc5vj').pop().inner_text())

        export = {
            "web_domain": web_domain,
            "end_page_number": end_page_number,
            "semaphore_limit": semaphore_limit,
        }

        browser.close()

        with open("configuration.json", "w") as file:
            json.dump(export, file)


if __name__ == "__main__":
    # Example input: web_domain, semaphore_limit
    initalize("zehrs", 5)