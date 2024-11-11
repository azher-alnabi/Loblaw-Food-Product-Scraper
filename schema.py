import json
from typing import Optional
from sqlmodel import Field, SQLModel, create_engine, Session, Relationship, select


class ProductInfo(SQLModel, table=True):
    product_id: str = Field(primary_key=True)
    small_image_url: str
    brand_name: Optional[str] = None
    title_name: str
    type: str
    package_sizing: str
    prices: list["ProductPrice"] = Relationship(back_populates="product")


class ProductPrice(SQLModel, table=True):
    product_id: str = Field(foreign_key="productinfo.product_id", primary_key=True)
    store: str = Field(primary_key=True)
    price_cents: Optional[int] = None
    product: ProductInfo = Relationship(back_populates="prices")


engine = create_engine("sqlite:///database.db")
SQLModel.metadata.create_all(engine)


def upsert_product(product_data: dict):
    product_id = product_data["product_id"]

    with Session(engine) as session:
        statement = select(ProductInfo).where(ProductInfo.product_id == product_id)
        product = session.exec(statement).one_or_none()

        if product:
            if 'small_image_url' in product_data:
                product.small_image_url = product_data['small_image_url']
            if 'brand_name' in product_data:
                product.brand_name = product_data['brand_name']
            if 'title_name' in product_data:
                product.title_name = product_data['title_name']
            if 'type' in product_data:
                product.type = product_data['type']
            if 'package_sizing' in product_data:
                product.package_sizing = product_data['package_sizing']
            if 'prices' in product_data:
                for new_price in product_data['prices']:
                    store = new_price['store']
                    price_entry = next((p for p in product.prices if p.store == store), None)
                    if price_entry:
                        price_entry.price_cents = new_price.get('price_cents', price_entry.price_cents)
                    else:
                        product.prices.append(ProductPrice(store=store, price_cents=new_price.get('price_cents')))
            print(f"Updated product: {product_id}")
        else:
            product = ProductInfo(
                product_id=product_data["product_id"],
                small_image_url=product_data["small_image_url"],
                brand_name=product_data.get("brand_name"),
                title_name=product_data["title_name"],
                type=product_data["type"],
                package_sizing=product_data["package_sizing"]
            )

            for price in product_data["prices"]:
                product.prices.append(ProductPrice(store=price["store"], price_cents=price["price_cents"]))

            session.add(product)
            print(f"Inserted new product: {product_id}")

        session.commit()
        session.refresh(product)


def update_products_from_json(json_file_path: str):
    with open(json_file_path, 'r') as file:
        products_data = json.load(file)

    for product_data in products_data:
        upsert_product(product_data)


if __name__ == "__main__":
    update_products_from_json("updated_products.json")


"""
Sample Data "updated_products.json":

```json
[
    {
        "product_id": "20091825001_EA",
        "small_image_url": "https://assets.shop.loblaws.ca/products/20091825001/b1/en/front/20091825001_front_a01_@2.png",
        "brand_name": null,
        "title_name": "Cilantro",
        "type": "SOLD_BY_EACH",
        "package_sizing": "1 bunch, $1.00/1ea",
        "prices": [
            {"store": "zehrs", "price_cents": 100},
            {"store": "loblaws", "price_cents": 125},
            {"store": "nofrills", "price_cents": 75}
        ]
    },
    {
        "product_id": "20179038001_KG",
        "small_image_url": "https://assets.shop.loblaws.ca/products/20179038001/b1/en/front/20179038001_front_a01_@2.png",
        "brand_name": "Rooster",
        "title_name": "Ginger",
        "type": "SOLD_BY_EACH",
        "package_sizing": "$6.61/1kg $3.00/1lb",
        "prices": [
            {"store": "zehrs", "price_cents": 139},
            {"store": "loblaws", "price_cents": 139},
            {"store": "nofrills", "price_cents": 139}
        ]
    }
]
```
"""