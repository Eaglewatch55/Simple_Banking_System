# Write your code here
import random
import sqlite3
import os


class CreditCard:
    def __init__(self, card_number, id_db, pin, balance=0):
        self.c_number = card_number
        self.ident = id_db
        self.sec_pin = pin
        self.bal = balance

    def get_card_number(self):
        return self.c_number

    def get_pin(self):
        return self.sec_pin

    def get_balance(self):
        return self.bal

    def get_id_db(self):
        return self.ident

def print_menu(menu_type="main"):
    if menu_type == "main":
        print("1. Create an account")
        print("2. Log into account")
        print("0. Exit")
    if menu_type == "logged":
        print("1. Balance")
        print("2. Log out")
        print("0. Exit")


def card_number_generator(card_num_list: list, num_length=16):
    card_number = 400000
    luhn = card_number * 2

    for n in range(num_length - len(str(card_number)) - 1):
        card_number *= 10
        luhn *= 10
        new_num = random.randint(0, 9)
        card_number += new_num

        # Checks digit if pair
        if (n + 1) % 2 == 0:
            luhn += new_num
        else:
            new_num *= 2
            luhn += new_num if new_num < 10 else new_num - 9

    val_digit = sum([int(n) for n in str(luhn)])
    val_digit = 10 - (val_digit % 10) if val_digit % 10 != 0 else 0

    card_number *= 10
    card_number += val_digit

    if card_number in card_num_list:
        return card_number_generator(card_num_list, num_length)
    else:
        return str(card_number)


def pin_generator(num_length=4):
    pin = str(random.randint(0, 9))
    for n in range(num_length - 1):
        pin += str(random.randint(0, 9))
    return pin


def generate_card(card_dict: dict, _id):
    list_num = [c.get_card_number() for c in card_dict.values()]
    c = CreditCard(card_number_generator(list_num), _id, pin_generator())
    n = c.get_card_number()
    return n, c


def logged_in(card):
    while True:
        print_menu("logged")
        logged_sel = input()

        if logged_sel == "1":
            print(f"\nBalance: {card.get_balance()}\n")
        elif logged_sel == "2":
            print("\nYou have successfully logged out!\n")
            return
        elif logged_sel == "0":
            print("\nBye!")
            exit()


def create_db():
    con = sqlite3.connect("card.s3db")
    cursor = con.cursor()
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS card(id INTEGER, number TEXT, pin TEXT, balance INTEGER DEFAULT 0
            );""")
    con.commit()
    cursor.close()
    con.close()


def modify_db(cursor, action, columns=(), values=()):
    action_dict = {"INSERT": f"INSERT INTO card ({','.join(columns)}) VALUES ({','.join(values)});"}
    cursor.execute(action_dict[action])


def consult_db(cursor, columns):
    cursor.execute(f"SELECT {columns} FROM card")
    return cursor.fetchall()


# def cleanup():
#     con = sqlite3.connect("card.s3db")
#     cursor = con.cursor()
#     cursor.execute("DROP TABLE IF EXISTS card")
#     con.commit()
#     cursor.close()
#     con.close()
# cleanup()

create_db()
conn = sqlite3.connect("card.s3db")
cur = conn.cursor()

while True:
    cards = {c[1]: CreditCard(c[1], c[0], c[2], c[3]) for c in consult_db(cur, "*")}

    try:
        curr_id = max([cards[c].get_id_db() for c in cards.keys()])
    except TypeError:
        curr_id = 0
    except ValueError:
        curr_id = 0

    print_menu()

    selection = input()

    if selection == "1":
        genCard = generate_card(cards, curr_id + 1)
        genCard = [str(genCard[1].get_id_db()), genCard[0], genCard[1].get_pin()]
        modify_db(cur, "INSERT", ["id", "number", "pin"], genCard)
        conn.commit()
        print("Your card has been created")
        print("Your card number:")
        print(genCard[1])
        print("Your card PIN:")
        print(genCard[2])
        print()

    elif selection == "2":
        print("Enter your card number:")
        input_card = input()
        print("Enter your PIN:")
        input_pin = input()

        if input_card in cards.keys() and cards[input_card].get_pin() == input_pin:
            print("\nYou have successfully logged in!\n")
            logged_in(cards[input_card])
        else:
            print("\nWrong card number or PIN!\n")

    elif selection == "0":
        print("\nBye!")
        cur.close()
        conn.close()
        exit()
