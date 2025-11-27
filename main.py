import pyfiglet as pf
import questionary as qu
from colorama import Fore as fr, Style as st

from functions.login import seller_login, customer_login, courier_login
from functions.register import (register_seller,register_customer,register_courier,username_exists)
from functions.seller_dashboard import dashboard as seller_dashboard
from functions.customer_dashboard import dashboard as customer_dashboard
from functions.courier_dashboard import dashboard as courier_dashboard


# ========================= UTILS =========================

def validate_input(*fields):
    return all(field and field.strip() != "" for field in fields)

def validate_phone(phone):
    return phone.isdigit() and len(phone) == 12


# ========================= UI =========================

msg = pf.figlet_format("E-Butcher", font="larry3d")
print(fr.RED + st.BRIGHT + msg)


def login_menu():
    print(fr.CYAN + "[1] Seller Login")
    print("[2] Customer Login")
    print("[3] Courier Login")
    print("[0] Back\n" + st.RESET_ALL)
    return qu.text("Choose login type:").ask()


def register_menu():
    print(fr.CYAN + "[1] Seller Registration")
    print("[2] Customer Registration")
    print("[3] Courier Registration")
    print("[0] Back\n" + st.RESET_ALL)
    return qu.text("Choose registration type:").ask()


def main_menu():
    return qu.select(
        "Already Have an Account?",
        choices=["Login", "Register", "Exit"]
    ).ask()


# ========================= MAIN LOOP =========================

while True:
    option = main_menu()

    # ========== LOGIN ==========
    if option == "Login":
        choice = login_menu()

        if choice == "1":
            username = qu.text("Enter Username:").ask()
            password = qu.password("Enter Password:").ask()
            if seller_login(username, password):
                print(fr.GREEN + "[+] Seller login success\n" + st.RESET_ALL)
                seller_dashboard(username, password)
            else:
                print(fr.RED + "[-] Invalid username or password!\n" + st.RESET_ALL)

        elif choice == "2":
            username = qu.text("Enter Username:").ask()
            password = qu.password("Enter Password:").ask()
            if customer_login(username, password):
                print(fr.GREEN + "[+] Customer login successful!\n" + st.RESET_ALL)
                customer_dashboard(username, password)
            else:
                print(fr.RED + "[-] Invalid username or password!\n" + st.RESET_ALL)

        elif choice == "3":
            username = qu.text("Enter Username:").ask()
            password = qu.password("Enter Password:").ask()
            if courier_login(username, password):
                print(fr.GREEN + "[+] Courier login successful!\n" + st.RESET_ALL)
                courier_dashboard(username, password)
            else:
                print(fr.RED + "[-] Invalid username or password!\n" + st.RESET_ALL)
        else:
            print(fr.RED + "[-] Invalid input \n" + st.RESET_ALL)
        continue

    # ========== REGISTER ==========
    elif option == "Register":
        choice = register_menu()

        if choice == "1":      # seller register
            name = qu.text("Enter Full Name:").ask()
            phone = qu.text("Enter Phone Number (12 digits):").ask()
            username = qu.text("Choose Username:").ask()
            password = qu.password("Choose Password:").ask()
            street = qu.text("Enter Street:").ask()
            district = qu.text("Enter District:").ask()

            if not validate_input(name, phone, username, password):
                print(fr.RED + "[-] All fields must be filled!\n" + st.RESET_ALL)
                continue

            if not validate_phone(phone):
                print(fr.RED + "[-] Phone number must be 12 digits!\n" + st.RESET_ALL)
                continue

            if username_exists("sellers", username):
                print(fr.RED + "[-] Username already exists!\n" + st.RESET_ALL)
                continue

            if register_seller(name, phone, username, password, street, district):
                print(fr.GREEN + "[+] Seller registered successfully!\n" + st.RESET_ALL)
            else:
                print(fr.RED + "[-] Registration failed!\n" + st.RESET_ALL)

        elif choice == "2":    # customer register
            name = qu.text("Enter Full Name:").ask()
            phone = qu.text("Enter Phone Number (12 digits):").ask()
            username = qu.text("Choose Username:").ask()
            password = qu.password("Choose Password:").ask()
            street = qu.text("Enter Street:").ask()
            district = qu.text("Enter District:").ask()

            if not validate_input(name, phone, username, password):
                print(fr.RED + "[-] All fields must be filled!\n" + st.RESET_ALL)
                continue

            if not validate_phone(phone):
                print(fr.RED + "[-] Phone number must be 12 digits!\n" + st.RESET_ALL)
                continue

            if username_exists("customers", username):
                print(fr.RED + "[-] Username already exists!\n" + st.RESET_ALL)
                continue

            if register_customer(name, phone, username, password, street, district):
                print(fr.GREEN + "[+] Customer registered successfully!\n" + st.RESET_ALL)
            else:
                print(fr.RED + "[-] Registration failed!\n" + st.RESET_ALL)

        elif choice == "3":    # courier register
            name = qu.text("Enter Full Name:").ask()
            phone = qu.text("Enter Phone Number (12 digits):").ask()
            username = qu.text("Choose Username:").ask()
            password = qu.password("Choose Password:").ask()

            if not validate_input(name, phone, username, password):
                print(fr.RED + "[-] All fields must be filled!\n" + st.RESET_ALL)
                continue

            if not validate_phone(phone):
                print(fr.RED + "[-] Phone number must be 12 digits!\n" + st.RESET_ALL)
                continue

            if username_exists("couriers", username):
                print(fr.RED + "[-] Username already exists!\n" + st.RESET_ALL)
                continue

            if register_courier(name, phone, username, password):
                print(fr.GREEN + "[+] Courier registered successfully!\n" + st.RESET_ALL)
            else:
                print(fr.RED + "[-] Registration failed!\n" + st.RESET_ALL)
        else:
            print(fr.RED + "[-] Invalid Input \n" + st.RESET_ALL)
        continue

    # ========== EXIT ==========
    else:
        print(fr.YELLOW + "[!] Exiting program..." + st.RESET_ALL)
        break
