# Grocery-Webscraper
A webscraper built for pulling food product information from Canadian grocery stores


## Sites Supported:
- https://www.loblaws.ca/food/c/27985
- https://www.zehrs.ca/food/c/27985
- https://www.yourindependentgrocer.ca/food/c/27985
- https://www.valumart.ca/food/c/27985
- https://www.atlanticsuperstore.ca/food/c/27985
- https://www.newfoundlandgrocerystores.ca/food/c/27985
- https://www.fortinos.ca/food/c/27985
- https://www.wholesaleclub.ca/food/c/27985
- https://www.realcanadiansuperstore.ca/food/c/27985
- https://www.nofrills.ca/food/c/27985
- https://www.independentcitymarket.ca/food/c/27985


## Future Sites to Support:
- https://www.provigo.ca/alimentation/c/27985 [French]
- https://www.maxi.ca/alimentation/c/27985 [French]

## Website Update frequency
From first glance, it seems that the websites update their offerings on their website on Fridays, heading into the weekend. 
I will try to update the scraper on Fridays to ensure that the data is up to date.

## Topics to revisit:

### The use of css/xpath selectors for scraping

XPath and CSS selectors can be tied to the DOM structure or implementation. 
These selectors can break when the DOM structure changes. 
Long CSS or XPath chains are bad practice that leads to unstable tests.
Currently, the scraper uses CSS selectors to find the product information.
I will need to revisit it at a later time and implement "locator objects" instead of using css/xpath selectors directly.
```
https://playwright.dev/docs/locators#locator-vs-elementhandle
```


## Playwright

This is needed to switch from default chromium browser to firefox browser.
```
playwright install firefox
```


## I got the private json:

https://api.pcexpress.ca/pcx-bff/api/v2/listingPage/27985