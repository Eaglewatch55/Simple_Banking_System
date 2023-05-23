# Write your code here
import random


class CreditCard:
    def __init__(self, card_number, pin):
        self.c_number = card_number
        self.sec_pin = pin
        self.bal = 0

    def get_card_number(self):
        return self.c_number

    def get_pin(self):
        return self.sec_pin

    def get_balance(self):
        return self.bal


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
        return card_number


def pin_generator(num_length=4):
    pin = str(random.randint(0, 9))
    for n in range(num_length - 1):
        pin += str(random.randint(0, 9))
    return pin


def generate_card(card_dict: dict):
    list_num = [c.get_card_number() for c in card_dict.values()]
    c = CreditCard(card_number_generator(list_num), pin_generator())
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


cards = {}
while True:
    print_menu()

    selection = input()

    if selection == "1":
        genCard = generate_card(cards)
        cards[genCard[0]] = genCard[1]
        print("Your card has been created")
        print("Your card number:")
        print(genCard[0])
        print("Your card PIN:")
        print(genCard[1].get_pin())
        print()

    elif selection == "2":
        print("Enter your card number:")
        input_card = int(input())
        print("Enter your PIN:")
        input_pin = input()

        if input_card in cards.keys() and cards[input_card].get_pin() == input_pin:
            print("\nYou have successfully logged in!\n")
            logged_in(cards[input_card])
        else:
            print("\nWrong card number or PIN!\n")

    elif selection == "0":
        print("\nBye!")
        exit()
