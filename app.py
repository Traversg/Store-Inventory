from os import X_OK
from types import new_class

from sqlalchemy.sql.expression import update
from models import Base, session, Product, engine
import datetime
import csv
import time


def clean_date(date_str):
    split_date = date_str.split('/')
    try:
        month = int(split_date[0])
        day = int(split_date[1])
        year = int(split_date[2])
        return_date = datetime.date(year, month, day)
    except ValueError:
        input('''
            \n***** DATE ERROR *****
            \rThe date from should include a valid Day/Month/Year
            \rEx. 1/05/2021
            \rPress enter to try again.
            \r**********************''')
        return
    else:
        return return_date


def clean_price(price_str):
    try:
        price_float = float(price_str.split('$')[1])
    except IndexError:
        input('''
            \n***** PRICE ERROR *****
            \rThe price from should be a number with a $ symbol
            \rEx. $7.51
            \rPress enter to try again.
            \r**********************''')
    else:
        return int(price_float * 100)


def clean_id(id_str, options):
    try:
        selected_product_id = int(id_str)
    except ValueError:
        input('''
            \n***** ID ERROR *****
            \rThe id should be a number
            \rPress enter to try again.
            \r********************
            ''')
        return
    else:
        if selected_product_id in options:
            return selected_product_id
        else:
            input('''
                \n***** ID ERROR *****
                \rPlease select a valid product number
                \rPress enter to try again.
                \r********************''')
            return


def get_product_by_ID():
    id_options = []
    for product in session.query(Product):
        id_options.append(product.product_id)
    id_error = True
    while id_error:
        id_choice = input('\nPlease select product by product number: ')
        id_choice = clean_id(id_choice, id_options)
        if type(id_choice) == int:
            id_error = False
    selected_product = (session.query(Product)
                        .filter(Product.product_id == id_choice).first())
    print(f'''
        \n{selected_product.product_name}: \n
        \rQuantity: {selected_product.product_quantity}
        \rPrice: ${selected_product.product_price / 100}
        \rDate Updated: {selected_product.date_updated}
        ''')
    time.sleep(1.5)


def add_product():
    product = input('Product: ')
    price_error = True
    while price_error:
        price = input('Price (Ex. $7.51): ')
        price = clean_price(price)
        if type(price) == int:
            price_error = False
    quantity_error = True
    while quantity_error:
        try:
            quantity = int(input('Quantity (Ex. 13): '))
            quantity_error = False
        except ValueError:
            input('''
                \n***** QUANTITY ERROR *****
                \rThe quantity should be a number
                \r(Ex. 13)
                \rPress enter to try again.
                \r********************
                ''')
    date_error = True
    while date_error:
        date = input("Today's Date (ex. 1/5/2021): ")
        date = clean_date(date)
        if type(date) == datetime.date:
            date_error = False
    new_product = (Product(product_name=product,
                           product_price=price,
                           product_quantity=quantity,
                           date_updated=date))
    if check_duplicate(new_product):
        session.add(new_product)
        session.commit()


def check_duplicate(new_product):
    product_names = []
    for product in session.query(Product):
        product_names.append(product.product_name)
    if new_product.product_name in product_names:
        for product in session.query(Product):
            if new_product.product_name == (product.product_name and
                                            new_product.date_updated >=
                                            product.date_updated):
                new_product.product_id = product.product_id
                session.delete(product)
                session.commit()
                print('\nItem updated!')
                time.sleep(1.5)
                return True
            elif new_product.product_name == (product.product_name and
                                              new_product.date_updated <
                                              product.date_updated):
                print('\nThis product is already up to date in the inventory')
                time.sleep(1.5)
                return False
    else:
        print('\nNew product added!')
        time.sleep(1.5)
        return True


def backup_csv():
    with open('backup.csv', 'a') as csvfile:
        fieldnames = ['product_name',
                      'product_price',
                      'product_quantity',
                      'date_updated']
        productwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
        productwriter.writeheader()
        for product in session.query(Product):
            two_decimal_float = '{:.2f}'.format(product.product_price / 100)
            string_date = product.date_updated.strftime('%-m/%-d/%Y')
            productwriter.writerow({
                'product_name': f'{product.product_name}',
                'product_price': f'${two_decimal_float}',
                'product_quantity': f'{product.product_quantity}',
                'date_updated': f'{string_date}'
            })
        print('\nBackup created!')
        time.sleep(1.5)


def add_csv():
    with open('inventory.csv') as csvfile:
        data = csv.reader(csvfile)
        next(data)
        for row in data:
            product_in_db = (session.query(Product)
                             .filter(Product.product_name ==
                             row[0]).one_or_none())
            if product_in_db is None:
                product = row[0]
                price = clean_price(row[1])
                quantity = int(row[2])
                date = clean_date(row[3])
                new_product = Product(product_name=product,
                                      product_price=price,
                                      product_quantity=quantity,
                                      date_updated=date)
                session.add(new_product)
            elif product_in_db is not None:
                new_date = clean_date(row[3])
                product = (session.query(Product)
                           .filter(Product.product_name == row[0]).first())
                if product_in_db.product_name == (product.product_name and
                                                  product.date_updated <=
                                                  new_date):
                    product.product_price = clean_price(row[1])
                    product.product_quantity = int(row[2])
                    product.date_updated = new_date
        session.commit()


def menu():
    while True:
        print('\nSTORE INVENTORY:\n')
        for product in session.query(Product):
            print(f'{product.product_id}. {product.product_name}')
        print('''
            \rEnter v to View Product Details
            \rEnter a to Add New Product
            \rEnter b to Make a Backup
            \rEnter x to Exit
            ''')
        choice = input('What would you like to do? ').lower()
        if choice in ['v', 'a', 'b', 'x']:
            return choice
        else:
            input('''
                \rPlease choose an option from above: v, a, b, or x
                \rPress enter to try again.''')


def app():
    app_running = True
    while app_running:
        choice = menu()
        if choice == 'v':
            get_product_by_ID()
        elif choice == 'a':
            add_product()
        elif choice == 'b':
            backup_csv()
        elif choice == 'x':
            print('\nGoodbye!')
            app_running = False


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    add_csv()
    app()
