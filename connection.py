import pymysql
import pymysql.cursors

class Store_connection(pymysql.connect):
    def __init__(self, host: str, user: str, password: str, database: str):
        # connect with the database
        super().__init__(host, user, password, database, cursorclass=pymysql.cursors.DictCursor)

        # Create a cursor for database controlling
        self.controler_cursor = self.cursor()

        # print(self.get_stock())

        # Get next Customer
        self.current_customer = self.get_next_costumer()
    
    def get_stock(self) -> dict[str, any]:
        """Get all products from stock"""

        self.controler_cursor.execute('SELECT * FROM `products`;')
        return self.controler_cursor.fetchall()
    
    def get_product(self, id: str) -> dict[str, any]:
        """Get the product with the correponding id"""

        self.controler_cursor.execute("SELECT * FROM `products` WHERE `id` = %s", (id))
        return self.controler_cursor.fetchall()
    
    def get_next_costumer(self) -> int:
        self.controler_cursor.execute('SELECT COALESCE(MAX(`Id`), 1) AS `LastCustomer` FROM `customers`;')
        return self.controler_cursor.fetchall()[0]["LastCustomer"]

    def withdraw(self, id: str, amount: int) -> None:
        """Decress the amount of the product availiable on stock"""
        
        self.controler_cursor.execute('UPDATE `products` SET `OnStock` = `OnStock` - %s WHERE `Id` = %s;', (amount, id))
        self.commit()
    
    def add_seller(self, customer_id: str, product_id: str, amount: int, per_unit: float) -> None:
        """Add a new seller to the sellers table"""

        self.controler_cursor.execute('''
INSERT INTO `sellers`(CustomerId, ProductId, Amount, Total) VALUES 
    (%s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
    `Amount` = `Amount` + VALUES(`Amount`),
    `Total` = `Total` + VALUES(`Total`)
;
''', (
    customer_id,
    product_id,
    amount,
    round(amount*per_unit, 2)
))
        self.commit()

    def add_customer(self, total_price: float) -> None:
        """Insert a new costumer to the costumers tables"""

        self.controler_cursor.execute('INSERT INTO `customers`(Total) VALUES (%s);', (round(total_price, 2)))
        self.commit()