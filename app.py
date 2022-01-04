from models import Base, session, Product, engine
import datetime
import csv

def clean_date(date_str):
    split_date = date_str.split('/')
    month = int(split_date[0])
    day = int(split_date[1])
    year = int(split_date[2])
    return datetime.date(year, month, day)


def clean_price(price_str):
    price_float = float(price_str.split('$')[1])
    return int(price_float * 100)

   
def add_csv():
    with open('inventory.csv') as csvfile:
        data = csv.reader(csvfile)
        for row in data:
            print(row)
            product = row[0]
            price = clean_price(row[1])
            quantity = int(row[2])
            date = clean_date(row[3])
            new_product = Product(product_name=product, product_price=price, product_quantity=quantity, date_updated=date)
            session.add(new_product)
        session.commit()

if __name__ == '__main__':
    Base.metadata.create_all(engine)
    add_csv()

    for product in session.query(Product):
        print(product)