import pymysql
import pymysql.cursors
from sys import exit

def get_libary_products(cursor: pymysql.cursors.DictCursor) -> list[dict[str, any]]:
    cursor.execute('SELECT * FROM `products`;')
    return cursor.fetchall()

def get_product(products: dict[str, any], code: str) -> dict[str, any] | bool:
    for product in products:
        if product["Code"] == code:
            return product
    
    return False

def get_int_input(message: str, error: str = 'It is not a number') -> int:
    while True:
        try:
            return int(input(message))
        except ValueError:
            print(error)
        except KeyboardInterrupt | EOFError:
            exit('Bye')

def get_float_input(message: str, error: str = 'It is not a number') -> int:
    while True:
        try:
            return float(input(message))
        except ValueError:
            print(error)
        except (KeyboardInterrupt, EOFError):
            exit('Bye')

def main() -> None:
    try:
        # connect with the database
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='1234',
            database='libary',
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = connection.cursor()

        # get database data
        libary_products = get_libary_products(cursor)
        print(libary_products)

        # init variables
        total_to_pay = 0
        cursor.execute('SELECT COALESCE(MAX(`Id`), 1) AS `LastCustomer` FROM `customers`;')
        current_customer = cursor.fetchall()[0]["LastCustomer"]
        while True:
            try:
                product_code = input('Please insert product code: ')
            except (KeyboardInterrupt, EOFError):
                exit('bye')
            
            if product_code == 'next':
                payment = 0
                while payment < total_to_pay:
                    print(f'You still got pay {total_to_pay - payment} R$')
                    payment += get_float_input('Plase insert payment value: ')
                
                # print  bill
                print(f'''
***Bill***
Cutomer: {current_customer}
---''')
                
                print(f'''Total: {total_to_pay:.2f} R$;
Paid: {payment:.2f} R$;
Change: {abs(total_to_pay - payment):.2f} R$;
***Thanks your preference***
''')
                print('Next costumer!')

                # update program valus
                current_customer += 1
                # update db values
                cursor.execute(f'INSERT INTO `customers`(Total) VALUES (\'{total_to_pay:.2f}\');')
                connection.commit()
                # reset program values
                total_to_pay = 0
                continue
            elif not (product := get_product(libary_products, product_code)):
                print('Product does not exist on the storage')
                continue
            
            print(product)
            product_amount = 0
            while True:
                product_amount = get_int_input('How much of this product are you buying? ')
                if product_amount > product["OnStock"]:
                    print(f'Only theres {product["OnStock"]} of this product on stock you can\'t get {product_amount} of them')
                    break
                elif product_amount <= 0:
                    print('(Invalid operation!) You got buy at least 1 unit of this item')
                    break
            
            to_pay_product = float(product["Price"])*product_amount
            print(f'You\'re buying {product_amount} {product["Name"]}, it cost {to_pay_product} R$')

            total_to_pay += to_pay_product
            print(f'Total to pay {total_to_pay} R$')
    finally:
        connection.close()

if __name__ == '__main__':
    main()
