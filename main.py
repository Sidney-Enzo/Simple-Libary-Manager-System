import pymysql
import pymysql.cursors

def get_store_products(cursor: pymysql.cursors.Cursor, ageRestriction: int = 19) -> list[dict[str, any]]:
    cursor.execute(f'''
SELECT *
FROM `storage`
WHERE code in (
    SELECT min(`Code`)
    FROM `storage`
    GROUP BY `Item`
) AND ageRestriction < {ageRestriction};
''')

    # get Fetch data
    return cursor.fetchall()

def update_stock(cursor: pymysql.cursors.Cursor, code: str, amount: int) -> None:
    cursor.execute(f'''
UPDATE `storage`
SET OnStock = {amount}
WHERE Code = \'{code}\';
''')

def getProduct(store: list[dict[str, any]], item_code: int) -> dict[str, any]:
    for item in store:
        if item["Code"] == item_code:
            return item
    
    return False

def get_int_input(message: str, excepction_error: str='Plase insert a integer number') -> int:
    while True:
        try:
            return int(input(message) or '0')
        except ValueError:
            print(excepction_error)

def get_float_input(message: str, excepction_error: str='Plase insert a number') -> float:
    while True:
        try:
            return float(input(message) or '0')
        except ValueError:
            print(excepction_error)

def main() -> None:
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='1234',
        db='libary',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = connection.cursor()

    try:
        total_value = 0.0
        products = get_store_products(cursor)
        for product in products:
            print(product)

        while True:
            product_code = input('What are you buying? ').strip()
            if product_code == 'next':
                money_given = get_float_input('Pay ', 'It is not money')
                cursor.execute(f'''
INSERT INTO `customers`(Total) VALUES ({total_value});
''')
                connection.commit()
                print(f'''
Total {total_value}
Money {money_given}
Change {(total_value - money_given):.2f}

***Obrigado a preferencia***
Next costumer!''')
                total_value = 0
                continue
            
            product = getProduct(products, product_code)
            if not product:
                print('This product does not exist on storage')
                continue

            if product["OnStock"] < 1:
                print('We re out of this product on stock.')
                continue

            product_amount = get_int_input('How many of this product are you buying? ')
            if product["OnStock"] < product_amount:
                print('We re out of this product on stock.')
                continue
            
            to_pay = product["Price"]*product_amount
            print(f'You\'re buying {product_amount} manga of {product["Item"]} it cost: R${to_pay}')
            
            total_value += to_pay
            print('Total to pay: R$', total_value)
            
            product["OnStock"] -= product_amount
            update_stock(cursor, product_code, product["OnStock"])
            cursor.execute(f'''
INSERT INTO `sellers`(CustumerId, ProductId, Amount, Price) VALUES 
    ((SELECT COALESCE(MAX(`Id`), 1) FROM `customers`), {product["Id"]}, {product_amount}, \'{product["Price"]}\');
''')
            # print(f'Still there\'s {product["OnStock"]} of this product on stock.')
            connection.commit()
    finally:
        connection.close()

if __name__ == '__main__':
    main()  