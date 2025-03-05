import pymysql
import pymysql.cursors
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image

class App:
    def __init__(self):
        # connect with the database
        self.connection = pymysql.connect(
            host='localhost',
            user='root',
            password='1234',
            database='libary',
            cursorclass=pymysql.cursors.DictCursor
        )
        self.cursor = self.connection.cursor()

        # print(self.get_stock())

        # Get next Customer
        self.cursor.execute('SELECT COALESCE(MAX(`Id`), 1) AS `LastCustomer` FROM `customers`;')
        self.current_customer = self.cursor.fetchall()[0]["LastCustomer"]

        # Gui
        self.window = tk.Tk()
        self.window.title('Cash register')

        self.input_frame = tk.Frame(self.window, width=512, height=64)
        self.code_frame = tk.Frame(self.input_frame)
        self.code_label = tk.Label(self.code_frame, text='Code', font=('Helvetica', 16))
        self.code_label.pack()

        self.code_entry = tk.Entry(self.code_frame, width=22, font=('Helvetica', 16))
        self.code_entry.pack()
        self.code_frame.pack(side=tk.LEFT)
        
        self.amount_frame =tk.Frame(self.input_frame)
        self.amount_label = tk.Label(self.amount_frame, text='Amount', font=('Helvetica', 16))
        self.amount_label.pack()

        self.amount_entry = tk.Entry(self.amount_frame, width=22, font=('Helvetica', 16))
        self.amount_entry.pack()
        self.amount_frame.pack(side=tk.LEFT)

        self.img = Image.open('./assets/images/supermaket_logo.png')
        self.img = self.img.resize((64, 48))
        self.img = ImageTk.PhotoImage(self.img)
        self.supermaket_logo = tk.Label(self.input_frame, image=self.img)
        self.supermaket_logo.pack(side=tk.RIGHT)
        self.input_frame.pack(side=tk.TOP, anchor=tk.NW, padx=4, pady=4)

        self.bought_frame = tk.Frame(self.window, width=316, height=128)
        self.bought_items = ttk.Treeview(self.bought_frame, columns=('Name', 'Amount', 'Per_unit', 'Total'))
        self.bought_items.column('#0', width=128)
        self.bought_items.heading('#0', text='Id')

        self.bought_items.column('Name', width=128)
        self.bought_items.heading('Name', text='Name')

        self.bought_items.column('Amount', width=128)
        self.bought_items.heading('Amount', text='Amount')

        self.bought_items.column('Per_unit', width=128)
        self.bought_items.heading('Per_unit', text='Per unit')

        self.bought_items.column('Total', width=128)
        self.bought_items.heading('Total', text='Total')
        self.bought_items.pack(fill=tk.Y, expand=True)
        self.bought_frame.pack(side=tk.LEFT, padx=4, pady=4, fill=tk.Y)
        
        self.right_frame = tk.Frame(self.window, width=200, height=316)
        self.output_frame = tk.Frame(self.right_frame, width=200, height=64, bg='black')
        self.last_product_text = tk.Label(self.output_frame, text='...', font=('Helvetica', 16), wraplength=200, bg='black', fg='cyan')
        self.last_product_text.pack()
        
        self.total_price_text = tk.Label(self.output_frame, text='Total 0 R$', font=('Helvetica', 16), bg='black', fg='cyan')
        self.total_price_text.pack()
        self.output_frame.pack()
        
        self.seller_frame = tk.Frame(self.right_frame, width=128, height=256)
        self.recived_text = tk.Label(self.seller_frame, text='Total recived', font=('Helvetica', 16))
        self.recived_text.pack()

        self.recive_entry = tk.Entry(self.seller_frame, width=12, font=('Helvetica', 16))
        self.recive_entry.pack()
        
        self.change_text = tk.Label(self.seller_frame, text='Change: 0 R$', font=('Helvetica', 16))
        self.change_text.pack()
        self.seller_frame.pack()

        self.confirm_button = tk.Button(self.right_frame, text='Confirm', font=('Helvetica', 16), command=self.send_product, bg='green', fg='white', width=12, height=3)
        self.confirm_button.pack()

        self.next_button = tk.Button(self.right_frame, text='Next', font=('Helvetica', 16), command=self.switch_to_payment, bg='green', fg='white', width=12, height=3)
        self.next_button.pack()
        self.right_frame.pack(side=tk.LEFT, padx=4, pady=4)
        self.window.update()
        self.window.minsize(self.window.winfo_width(), self.window.winfo_height())

        self.product = None
        self.product_list = []
        self.total_price = 0
        self.payment = 0
    
    def update_stock(self, on_stock: int, id: str) -> None:
        self.cursor.execute(f'''
UPDATE `products` SET `OnStock` = {on_stock} WHERE `Id` = \'{id}\';
''')
        self.connection.commit()

    def get_stock(self) -> dict[str, any]:
        self.cursor.execute('SELECT * FROM `products`;')
        return self.cursor.fetchall()

    def get_product(self, code: str) -> dict[str, any] | bool:
        for product in self.get_stock():
            if product["Code"] == code:
                return product
        
        return False

    def add_seller(self, customer_id: str, product_id: str, amount: int, per_unit: float) -> None:
        self.cursor.execute(f'''
INSERT INTO `sellers`(CustomerId, ProductId, Amount, Total) VALUES 
    ({customer_id}, {product_id}, {amount}, \'{(amount*per_unit):.2f}\')
ON DUPLICATE KEY UPDATE
    `Amount` = `Amount` + {amount},
    `Total` = `Total` + \'{(amount*per_unit):.2f}\'
;
''')
        self.connection.commit()
    
    def add_customer(self, total_price: float) -> None:
        self.cursor.execute(f'''
INSERT INTO `customers`(Total) VALUES 
    (\'{total_price:.2f}\');
''')
        self.connection.commit()

    def product_was_bought(self, id: int) -> bool:
        for child in self.bought_items.get_children(''):
            item = self.bought_items.item(child, 'text')

            if int(item) == id:
                return child
            
        return False

    def update_bought_treeview(self, product: dict[str, any], amount: int) -> None:
        if child := self.product_was_bought(product['Id']):
            item = self.bought_items.item(child, 'values')
            self.bought_items.item(child, values=(product['Name'], int(item[1]) + amount, product["Price"], float(item[3]) + float(product["Price"])*amount))
        else:
            self.bought_items.insert('',
                tk.END, 
                text=product['Id'],
                values=(product['Name'], amount, product["Price"], product["Price"]*amount)
            )

    def switch_to_payment(self) -> None:
        if len(self.product_list) > 0:
            self.confirm_button.configure(command= self.send_payment)

    def send_product(self) -> None:
        product_code = self.code_entry.get()
        product = self.get_product(product_code)
        if not product:
            print('Product does not exist on the storage')
            return

        # print(product)
        product_amount = int(self.amount_entry.get().strip())
        if product_amount > product["OnStock"]:
            print(f'Only theres {product["OnStock"]} of this product on stock you can\'t get {product_amount} of them')
            return
        elif product_amount <= 0:
            print('(Invalid operation!) You got buy at least 1 unit of this item')
            return
        
        self.update_stock(product["OnStock"] - 1, product["Id"])

        to_pay_product = float(product["Price"])*product_amount
        print(f'You\'re buying {product_amount} {product["Name"]}, it cost {to_pay_product} R$')

        self.total_price += to_pay_product
        self.product_list.append((product, product_amount))

        self.code_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.update_bought_treeview(product, product_amount)

        self.total_price_text.configure(text=f'Total {self.total_price} R$')
        self.last_product_text.configure(text=f'\"{product["Name"]}\" {product_amount} {to_pay_product} R$')

    def send_payment(self) -> None:
        self.payment += float(self.recive_entry.get())
        if self.payment < self.total_price:
            print(f'You still got pay {(self.total_price - self.payment):.2f} R$')
            self.recive_entry.delete(0, tk.END)
            return
        
        # update db values
        self.add_customer(self.total_price)
        
        # print  bill
        print(f'''
***Bill***
Cutomer: {self.current_customer}
---''')

        for seller, amount in self.product_list:
            print(f'{seller["Name"]} {amount}: {seller["Price"]} R$')
            self.add_seller(self.current_customer, seller["Id"], amount, float(seller["Price"]))
        
        print(f'''---
Total: {self.total_price:.2f} R$;
Paid: {self.payment:.2f} R$;
Change: {abs(self.total_price - self.payment):.2f} R$;
***Thanks your preference***
''')
        print('Next costumer!')

        # update program valus
        self.current_customer += 1
        
        # reset program values
        self.confirm_button.configure(command=self.send_product)

        self.total_price_text.configure(text='Total price: 0 R$')
        self.last_product_text.configure(text='...')
        self.change_text.configure(text=f'Change: {abs(self.total_price - self.payment):.2f}')
        
        self.amount_entry.delete(0, tk.END)
        self.recive_entry.delete(0, tk.END)
        self.bought_items.delete(*self.bought_items.get_children())
        
        # Reset customer variables
        self.product_list = []
        self.total_price = 0

    def run(self) -> None:
        self.window.mainloop()
    
    def end(self) -> None:
        self.connection.close()

def main() -> None:
    cash = App()
    cash.run()
    cash.end()

if __name__ == '__main__':
    main()
