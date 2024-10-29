from playwright.async_api import async_playwright
import json
import asyncio
import time

''' Script to asynchronously scrape food data from a website using playwright

This script will scrape any loblaw's affiliated website for food data and store it in a dataclass


If i get the time, replace the css selectors with playwright locators
'''
starting_time = time.time()

async def scrape_page(page_number, browser, web_domain, semaphore, data_list):
    async with semaphore:
        page = await browser.new_page()

        await page.goto(f"https://www.{web_domain}.ca/food/c/27985?page={page_number}")
        await page.wait_for_selector('.css-1rb8z0p', timeout=60000)
        await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")

        food_items = await page.query_selector_all("div.css-0")
        for food in food_items:
            image_url = await food.query_selector('div[data-testid="product-image"] img')
            brand = await food.query_selector('p[data-testid="product-brand"]')
            title = await food.query_selector('h3[data-testid="product-title"]')
            package_size = await food.query_selector('p[data-testid="product-package-size"]')
            regular_price = await food.query_selector('span[data-testid="regular-price"]'),
            sale_price = await food.query_selector('span[data-testid="sale-price"]'),
            non_member_price = await food.query_selector('span[data-testid="non-member-price"]'),
            former_price = await food.query_selector('span[data-testid="was-price"]')

            data_list.append({
                "image_url": await image_url.get_attribute('src') if image_url else None,
                "product-brand": await brand.inner_text() if brand else None,
                "title": await title.inner_text() if title else None,
                "package-size": await package_size.inner_text() if package_size else None,
                #"regular-price": await regular_price.inner_text() if regular_price else None,
                #"sale-price": await sale_price.inner_text() if sale_price else None,
                #"non-member-price": await non_member_price.inner_text() if non_member_price else None,
                "former-price": await former_price.inner_text() if former_price else None,
            })

        await page.close()
        print(f"\nTime taken: {time.time() - starting_time}")

async def scrape(end_page_number, web_domain, semaphore_limit):
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)
        semaphore = asyncio.Semaphore(semaphore_limit)
        data_list = []

        tasks = [
            scrape_page(page_number, browser, web_domain, semaphore, data_list) for page_number in range(1, end_page_number + 1)
        ]
        
        await asyncio.gather(*tasks)
        await browser.close()


        with open("data.json", "w") as json_file:
            json.dump(data_list, json_file, indent=4)

def yield_raw_food_data():
    with open("configuration.json", "r") as file:
        configuration = json.load(file)
        return asyncio.run(scrape(**configuration))



if __name__ == "__main__":
    # Example input: end_page_number, web_domain, semaphore_limit
    asyncio.run(scrape(209, "zehrs", 5))