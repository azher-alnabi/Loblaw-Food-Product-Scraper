# Loblaw Companies Limited Food Product Webscraper

## Description:

This is tool that allows you to scrape all the food products from the Loblaw Companies Limited websites for future data processing and analysis.
This includes a significant amount of websites that are owned by Loblaw Companies Limited, such as Loblaws, No Frills, Zehrs, and more. 

The tool will scrape the following product information:

- The unique identifier of the product
- The image of the product
- The brand of the product
- The title of the product
- How the product is sold (ex. per kg, per 100g, per 1L, etc.)
- If the product is sold by weight or volume
- The price(s) of the product (if multiple domains are used during the scraping process)

The prices will be stored in two ways:
- JSON file
- SQLite database with two tables (one to many relationship):
    - productinfo
    - productprices

The limitations of this tool is that it will only scrape food products inside of Ontario, Canada, for the websites found below.


## Intended audiance for this tool:

- People who want to compare prices of products between different Loblaw Companies Limited websites.
- People who want to track CPI (Consumer Price Index) of food products overtime.
- People who want to track the price of a specific product over time.


## Setup

### Pulling the Repository and navigating to the directory

Pull the repository and navigate to the directory
```bash
git clone https://github.com/azher-alnabi/Loblaw-Food-Product-Scraper.git
cd Loblaw-Food-Product-Scraper
```


### Windows:
create a virtual environment
```bash
python -m venv venv
```

activate the virtual environment
```bash
source venv/Scripts/activate
```

install the required packages
```bash
pip install -r requirements.txt
```


### Linux:
create a virtual environment
```bash
python3 -m venv venv
```

activate the virtual environment
```bash
source venv/bin/activate
```

install the required packages
```bash
pip3 install -r requirements.txt
```


## Usage

To harvest the data from all the supported domains, run the following command:

```bash
python main.py -all
```

or you can specify the domain you want to scrape:

Example:
```bash
python main.py loblaws nofrills zehrs
```

To see all the available options, run the following command:

```bash
python main.py -h
```


## Domains Supported:
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


## Future Domains to Support:
- https://www.independentcitymarket.ca/food/c/27985
- https://www.provigo.ca/alimentation/c/27985 [French]
- https://www.maxi.ca/alimentation/c/27985 [French]
