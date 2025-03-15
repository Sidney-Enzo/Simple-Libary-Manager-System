import tkinter as tk
from tkinter import ttk
import sv_ttk
from PIL import ImageTk, Image

import modules.connection as connection

def is_float(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False

class App:
    def __init__(self):
        # connect with the database
        self.store_connection = connection.Store_connection(
            'localhost',
            'root',
            '1234',
            'libary'
        )

        # Gui
        self.window = tk.Tk()
        self.window.title('Cash register')
        self.window.iconbitmap('icon.ico')

        helvetica_meddium = ('Helvetica', 16)
        onlyInt = self.window.register(lambda p: p.isdigit() or p == '')
        onlyNumbers = self.window.register(lambda p: is_float(p) or p == '')
        
        self.input_frame = tk.Frame(self.window, width=512, height=64)
        self.code_frame = tk.Frame(self.input_frame)
        self.code_label = tk.Label(self.code_frame, text='Code', font=helvetica_meddium)
        self.code_label.pack()

        self.code_entry = tk.Entry(self.code_frame, validate='all', vcmd=(onlyInt, '%P'), width=22, font=helvetica_meddium)
        self.code_entry.pack()
        self.code_frame.pack(side=tk.LEFT, padx=4, pady=4)
        
        self.amount_frame =tk.Frame(self.input_frame)
        self.amount_label = tk.Label(self.amount_frame, text='Amount', font=helvetica_meddium)
        self.amount_label.pack()

        self.amount_entry = tk.Entry(self.amount_frame, validate='all', vcmd=(onlyInt, '%P'), width=22, font=helvetica_meddium)
        self.amount_entry.pack()
        self.amount_frame.pack(side=tk.LEFT, padx=4, pady=4)

        self.img = Image.open('./assets/images/supermaket_logo.png')
        self.img = self.img.resize((64, 48))
        self.img = ImageTk.PhotoImage(self.img)
        self.supermaket_logo = tk.Label(self.input_frame, image=self.img)
        self.supermaket_logo.pack(side=tk.RIGHT)
        self.input_frame.pack(side=tk.TOP, anchor=tk.NW, padx=4, pady=4)

        self.bought_frame = tk.Frame(self.window, width=256, height=128)
        self.bought_items = ttk.Treeview(self.bought_frame, columns=('Name', 'Amount', 'Per_unit', 'Total'))
        self.bought_items.column('#0', stretch=True)
        self.bought_items.heading('#0', text='Code')

        self.bought_items.column('Name', stretch=True)
        self.bought_items.heading('Name', text='Name')

        self.bought_items.column('Amount', stretch=True)
        self.bought_items.heading('Amount', text='Amount')

        self.bought_items.column('Per_unit', stretch=True)
        self.bought_items.heading('Per_unit', text='Per unit')

        self.bought_items.column('Total', stretch=True)
        self.bought_items.heading('Total', text='Total')
        self.bought_items.pack(fill=tk.BOTH, expand=True)
        self.bought_frame.pack(side=tk.LEFT, padx=4, pady=4, fill=tk.BOTH, expand=True)
        
        self.right_frame = tk.Frame(self.window, width=200, height=316)
        self.output_frame = tk.Frame(self.right_frame, width=200, height=80, bg='black')
        self.last_product_text = tk.Label(self.output_frame, text='...', font=helvetica_meddium, wraplength=200, width=15, bg='black', fg='cyan')
        self.last_product_text.pack()
        
        self.total_price_text = tk.Label(self.output_frame, text='Total 0 R$', font=helvetica_meddium, bg='black', fg='cyan')
        self.total_price_text.pack()
        self.output_frame.pack()
        
        self.seller_frame = tk.Frame(self.right_frame, width=128, height=256)
        self.recived_text = tk.Label(self.seller_frame, text='Total recived', font=helvetica_meddium)
        self.recived_text.pack()

        self.recive_entry = tk.Entry(self.seller_frame, width=12, validate='all', vcmd=(onlyNumbers, '%P'), font=helvetica_meddium)
        self.recive_entry.pack()
        
        self.change_text = tk.Label(self.seller_frame, text='Change: 0.00 R$', font=helvetica_meddium)
        self.change_text.pack()
        self.seller_frame.pack()

        self.confirm_button = tk.Button(self.right_frame, text='Confirm', font=helvetica_meddium, command=self.send_product, bg='green', fg='white', width=12, height=3)
        self.confirm_button.pack()

        self.next_button = tk.Button(self.right_frame, text='Next', font=helvetica_meddium, command=self.switch_to_payment, bg='green', fg='white', width=12, height=3)
        self.next_button.pack()

        self.delete_button = tk.Button(self.right_frame, text="Delete", font=helvetica_meddium, command=self.remove_selection, bg='red', fg='white', width=12, height=3)
        self.delete_button.pack()

        self.cancel_button = tk.Button(self.right_frame, text='Cancel', font=helvetica_meddium, command=self.reset_seller, bg='red', fg='white', width=12, height=3)
        self.cancel_button.pack()

        self.right_frame.pack(side=tk.LEFT, padx=4, pady=4)
        sv_ttk.set_theme('dark')
        
        self.window.update()
        self.window.minsize(self.window.winfo_width(), self.window.winfo_height())

        self.product_list = []
        self.total_price = 0
        self.payment = 0

    def get_product_on_tree(self, code: str) -> bool | str:
        for child in self.bought_items.get_children(''):
            item = self.bought_items.item(child, 'text')

            if item == code:
                return child
        
        return False
    
    def get_product_on_list(self, code: str) -> bool | int:
        # Update the list incressing if the product already exist
        for i, (item, amount) in enumerate(self.product_list):
            if item["Code"] == code:
                return i
        
        return False
    
    def update_bought_treeview(self, product: dict[str, any], amount: int) -> None:
        if child := self.get_product_on_tree(product["Code"]):
            item = self.bought_items.item(child, 'values')
            self.bought_items.item(child, values=(product["Name"], int(item[1]) + amount, product["Price"], float(item[3]) + float(product["Price"])*amount))
        else:
            self.bought_items.insert('',
                tk.END, 
                text=product["Code"],
                values=(product["Name"], amount, product["Price"], product["Price"]*amount)
            )

    def switch_to_payment(self) -> None:
        if len(self.product_list) > 0:
            self.confirm_button.configure(command=self.send_payment)
        else:
            print('You still didn\'t bought anything')

    def send_product(self) -> None:
        product_code = self.code_entry.get()
        product = self.store_connection.get_product(product_code)
        if not product:
            print('Insert a valid product number')
            return

        # print(product)
        product_amount = int(self.amount_entry.get().strip())
        already_bought_amount = 0
        for seller, amount in self.product_list:
            if seller["Code"] == product_code:
                already_bought_amount += amount

        total_amount = already_bought_amount + product_amount
        if total_amount > product["OnStock"]:
            print(f'Only theres {product["OnStock"]} of this product on stock you can\'t get {total_amount} of them')
            return
        elif product_amount <= 0:
            print('(Invalid operation!) You got buy at least 1 unit of this item')
            return
        
        to_pay_product = float(product["Price"])*product_amount
        print(f'You\'re buying {product_amount} {product["Name"]}, it cost {to_pay_product} R$ still theres {product["OnStock"]} on stock')

        self.total_price += to_pay_product

        # Update the list incressing if the product already exist
        if product_index := self.get_product_on_list(product_code):
            self.product_list[product_index] = (product, amount + product_amount)
        else:
            self.product_list.append((product, product_amount))
        
        # reset entries
        self.code_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.update_bought_treeview(product, product_amount)

        # update last item labels
        self.total_price_text.configure(text=f'Total {self.total_price} R$')
        self.last_product_text.configure(text=f'\"{product["Name"]}\" {product_amount} {to_pay_product} R$')

    def send_payment(self) -> None:
        self.payment += float(self.recive_entry.get())
        if self.payment < self.total_price:
            print(f'You still got pay {(self.total_price - self.payment):.2f} R$')
            self.recive_entry.delete(0, tk.END)
            return
        
        # update db values
        self.store_connection.add_customer(self.total_price)
        
        # print  bill
        print(f'''
***Bill***
Cutomer: {self.store_connection.current_customer}
---''')

        for seller, amount in self.product_list:
            print(f'{seller["Name"]} {amount}: {seller["Price"]} R$')
            self.store_connection.add_seller(self.store_connection.current_customer, seller["Id"], amount, float(seller["Price"]))
            self.store_connection.withdraw(seller["Code"], amount)

        print(f'''---
Total: {self.total_price:.2f} R$;
Paid: {self.payment:.2f} R$;
Change: {abs(self.total_price - self.payment):.2f} R$;
***Thanks your preference***
''')
        print('Next costumer!')

        # update program values
        self.store_connection.current_customer += 1
        
        self.reset_seller()
    
    def remove_selection(self) -> None:
        selected_item = self.bought_items.selection()[0]
        selected_code = self.bought_items.item(selected_item, 'text')

        self.product_list = [(item, amount) for item, amount in self.product_list if item["Code"] != selected_code]
        self.total_price = sum(float(item["Price"])*amount for item, amount in self.product_list)
        
        self.bought_items.delete(selected_item)
        self.total_price_text.configure(text=f'Total {self.total_price} R$')

    def reset_seller(self) -> None:
        # reset widgets
        self.confirm_button.configure(command=self.send_product)

        # text labels
        self.total_price_text.configure(text='Total 0 R$')
        self.last_product_text.configure(text='...')
        self.change_text.configure(text=f'Change: {abs(self.total_price - self.payment):.2f} R$')
        
        # entries
        self.amount_entry.delete(0, tk.END)
        self.recive_entry.delete(0, tk.END)
        self.bought_items.delete(*self.bought_items.get_children())
        
        # Reset customer variables
        self.product_list = []
        self.total_price = 0

    def run(self) -> None:
        self.window.mainloop()
    
    def end(self) -> None:
        self.store_connection.close()