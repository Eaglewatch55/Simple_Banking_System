# Write your code here
import random
import sqlite3


class CreditCard:
    def __init__(self, card_number, id_db, pin, balance=0):
        self.c_number = card_number
        self.ident = id_db
        try:
            self.sec_pin = str(pin)
        except TypeError:
            self.sec_pin = pin

        self.bal = balance

    def get_card_number(self):
        return self.c_number

    def get_pin(self):
        return self.sec_pin

    def get_balance(self):
        return self.bal

    def update_balance(self, amount):
        self.bal += amount

    def get_id_db(self):
        return self.ident


def print_menu(menu_type="main"):
    if menu_type == "main":
        print("1. Create an account")
        print("2. Log into account")
        print("0. Exit")

    if menu_type == "logged":
        print("1. Balance")
        print("2. Add income")
        print("3. Do transfer")
        print("4. Close account")
        print("5. Log out")
        print("0. Exit")


def card_number_generator(card_num_list: list, num_length=16):
    card_number = 400000
    luhn = card_number * 2

    for n in range(num_length - len(str(card_number)) - 1):
        card_number *= 10
        luhn *= 10
        new_num = random.randint(0, 9)
        card_number += new_num

    card_number *= 10
    card_number += luhn_algorithm(card_number)

    if card_number in card_num_list:
        return card_number_generator(card_num_list, num_length)
    else:
        return str(card_number)


def luhn_algorithm(number):
    luhn = 0
    number = str(number)
    for n in range(len(str(number))):
        new_num = int(number[n])
        if (n + 1) % 2 == 0:
            luhn += new_num
        else:
            new_num *= 2
            luhn += new_num if new_num < 10 else new_num - 9

    val_digit = 10 - (luhn % 10) if luhn % 10 != 0 else 0
    return val_digit


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


def logged_in(connection, cursor, card: CreditCard):
    while True:
        print_menu("logged")
        logged_sel = input()

        if logged_sel == "1":
            print(f"\nBalance: {card.get_balance()}\n")

        elif logged_sel == "2":
            #FINILIZE
            print("Enter income:")
            income = int(input())
            card.update_balance(income)
            modify_db(cursor, "UPDATE", ["balance"], [str(card.get_balance())], f"id={card.get_id_db()}")
            connection.commit()
            print("Income was added!")

        elif logged_sel == "3":
            print("Transfer")
            print("Enter card number:")
            d_card = input()

            if luhn_algorithm(int(d_card[:-1])) != int(d_card[-1]):
                print("Probably you made a mistake in the card number. Please try again!")
                continue

            if card.get_card_number() == d_card:
                print("You can't transfer money to the same account!")
                continue

            query = consult_db(cursor, "*", (["number"], [d_card]))
            if len(query) == 0:
                print("Such a card does not exist.")
                continue

            query = query[0]
            d_card = CreditCard(query[1], query[0], query[2], query[3])
            print("Enter how much money you want to transfer:")
            amount = int(input())
            if amount > card.get_balance():
                print("Not enough money!")
                continue

            card.update_balance(-amount)
            modify_db(cursor, "UPDATE", ["balance"], [str(card.get_balance())], f"id={card.get_id_db()}")
            d_card.update_balance(amount)
            modify_db(cursor, "UPDATE", ["balance"], [str(d_card.get_balance())], f"id={d_card.get_id_db()}")
            connection.commit()
            print("Success!")

        elif logged_sel == "4":
            modify_db(cursor, "DELETE", ["id"], [str(card.get_id_db())])
            connection.commit()
            print("The account has been closed!")
            return

        elif logged_sel == "5":
            print("\nYou have successfully logged out!\n")
            return

        elif logged_sel == "0":
            cursor.close()
            connection.close()
            print("\nBye!")
            exit()


def create_db():
    con = sqlite3.connect("card.s3db")
    cursor = con.cursor()
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS card(id INTEGER, 
            number TEXT, 
            pin TEXT, 
            balance INTEGER DEFAULT 0
            );""")
    con.commit()
    cursor.close()
    con.close()


def db_join_values(c, v):
    joined = []
    for i in range(len(c)):
        joined.append(str(c[i]) + '=' + str(v[i]))
    return ",".join(joined)


def modify_db(cursor, action, columns=[], values=[], cond=None):

    action_dict = {"INSERT": f"INSERT INTO card ({','.join(columns)}) VALUES ({','.join(values)});",
                   "UPDATE": f"UPDATE card SET {db_join_values(columns, values)} WHERE {cond}",
                   "DELETE": f"DELETE FROM card WHERE {db_join_values(columns, values)}"}
    cursor.execute(action_dict[action])


def consult_db(cursor, columns, cond=None):
    if cond is None:
        cursor.execute(f"SELECT {columns} FROM card")
        return cursor.fetchall()
    else:
        cursor.execute(f"SELECT {columns} FROM card WHERE {db_join_values(cond[0], cond[1])}")
        return cursor.fetchall()


# ADDED FOR CLEANING UP THE TESTING PROGRAM DATABASE
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
    # for key in cards.keys():
    #     print(key, cards[key].get_pin())
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
            logged_in(conn, cur, cards[input_card])
        else:
            print("\nWrong card number or PIN!\n")

    elif selection == "0":
        print("\nBye!")
        cur.close()
        conn.close()
        exit()
