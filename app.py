from os import X_OK
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

def clean_id(id_str, options):
    try:
        selected_product_id = int(id_str)
    except ValueError:
        input('''
            \n***** ID ERROR *****
            \rThe id should be a number
            \rPress enter to try again.
            \r********************''')
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
    selected_product = session.query(Product).filter(Product.product_id==id_choice).first()
    print(f'''
        \n{selected_product.product_name}: \n
        \rQuantity: {selected_product.product_quantity}
        \rPrice: ${selected_product.product_price / 100}
        \rDate Updated: {selected_product.date_updated}
        ''')
    

   
def add_csv():
    with open('inventory.csv') as csvfile:
        data = csv.reader(csvfile)
        next(data)
        for row in data:
            product_in_db = session.query(Product).filter(Product.product_name==row[0]).one_or_none()
            if product_in_db == None:
                product = row[0]
                price = clean_price(row[1])
                quantity = int(row[2])
                date = clean_date(row[3])
                new_product = Product(product_name=product, product_price=price, product_quantity=quantity, date_updated=date)
                session.add(new_product)
        session.commit()

def menu():
    while True:
        print('STORE INVENTORY:\n')
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
                \rPlease choose an option from above: v, a, or b
                \rPress enter to try again.''')


def app():
    app_running = True
    while app_running:
        choice = menu()
        if choice == 'v':
            get_product_by_ID()
        elif choice == 'a':
            #add product to database
            pass
        elif choice == 'b':
            #back up database to csv
            pass
        elif choice == 'x':
            print('\nGoodbye!')
            app_running = False
            
        
        






if __name__ == '__main__':
    Base.metadata.create_all(engine)
    # add_csv()

    # for product in session.query(Product):
    #     print(product)
    app()