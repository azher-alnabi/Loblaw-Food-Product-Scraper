# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright
import time


chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"

with sync_playwright() as playwright:
    spoof_mobile = playwright.devices["Galaxy S5 landscape"]
    browser = playwright.chromium.launch(
        executable_path=chrome_path,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-blink-features=RendererCodeIntegrity",
            "--disable-infobars"
        ],
    )

    context = browser.new_context(
        # **spoof_mobile,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
        viewport={"width": 1920, "height": 867}
    )


    page = context.new_page()

    page.goto("https://bot-detector.rebrowser.net/")
    page.screenshot(path="ztest-rb.png", full_page=True)

    page.goto("https://arh.antoinevastel.com/bots/areyouheadless")
    page.screenshot(path="ztest-av.png", full_page=True)

    page.goto("https://arh.antoinevastel.com/bots/")
    page.screenshot(path="ztest-av2.png", full_page=True)

    page.goto("https://deviceandbrowserinfo.com/are_you_a_bot")
    time.sleep(3)
    page.get_by_role("button", name="Decline").click()
    page.screenshot(path="ztest-db.png", full_page=True)

    page.goto("https://pixelscan.net/")
    time.sleep(8)
    page.screenshot(path="ztest-ps.png", full_page=True)
    
    browser.close()