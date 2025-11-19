import pyfiglet as pf
import questionary as qu
from colorama import Fore as fr, Style as st

from functions.login import seller_login, customer_login, courier_login
from functions.register import register_seller, register_customer, register_courier

msg = pf.figlet_format("E-Butcher", font="larry3d")
print(fr.RED + st.BRIGHT + msg)


def login_menu():
    print(fr.CYAN + "[1] Seller Login")
    print("[2] Customer Login")
    print("[3] Courier Login")
    print("[0] Exit" + st.RESET_ALL)
    return qu.text("Choose login type:").ask()


def register_menu():
    print(fr.CYAN + "[4] Seller Registration")
    print("[5] Customer Registration")
    print("[6] Courier Registration")
    print("[0] Exit" + st.RESET_ALL)
    return qu.text("Choose registration type:").ask()


def main_menu():
    option = qu.select(
        "Already Have an Account?",
        choices=["Yes", "No", "Exit"]
    ).ask()

    if option == "Yes":
        return login_menu()
    elif option == "No":
        return register_menu()
    else:
        return "0"


while True:
    option = main_menu()

    # ===================== LOGIN =====================
    if option == "1":
        username = qu.text("Enter Username:").ask()
        password = qu.password("Enter Password:").ask()
        if seller_login(username, password):
            print(fr.GREEN + "[+] Seller login successful!" + st.RESET_ALL)
        else:
            print(fr.RED + "[-] Invalid username or password!" + st.RESET_ALL)
    elif option == "2":
        username = qu.text("Enter Username:").ask()
        password = qu.password("Enter Password:").ask()
        if customer_login(username, password):
            print(fr.GREEN + "[+] Customer login successful!" + st.RESET_ALL)
        else:
            print(fr.RED + "[-] Invalid username or password!" + st.RESET_ALL)
    elif option == "3":
        username = qu.text("Enter Username:").ask()
        password = qu.password("Enter Password:").ask()
        if courier_login(username, password):
            print(fr.GREEN + "[+] Courier login successful!" + st.RESET_ALL)
        else:
            print(fr.RED + "[-] Invalid username or password!" + st.RESET_ALL)


    # ===================== REGISTER =====================
    elif option == "4":  # seller register
        name = qu.text("Enter Full Name:").ask()
        phone = qu.text("Enter Phone Number (12 digits):").ask()
        username = qu.text("Choose Username:").ask()
        password = qu.password("Choose Password:").ask()
        if register_seller(name, phone, username, password):
            print(fr.GREEN + "[+] Seller registered successfully!" + st.RESET_ALL)
        else:
            print(fr.RED + "[-] Registration failed!" + st.RESET_ALL)
    elif option == "5":  # customer register
        name = qu.text("Enter Full Name:").ask()
        phone = qu.text("Enter Phone Number (12 digits):").ask()
        username = qu.text("Choose Username:").ask()
        password = qu.password("Choose Password:").ask()
        if register_customer(name, phone, username, password):
            print(fr.GREEN + "[+] Customer registered successfully!" + st.RESET_ALL)
        else:
            print(fr.RED + "[-] Registration failed!" + st.RESET_ALL)
    elif option == "6":  # courier register
        name = qu.text("Enter Full Name:").ask()
        phone = qu.text("Enter Phone Number (12 digits):").ask()
        username = qu.text("Choose Username:").ask()
        password = qu.password("Choose Password:").ask()
        if register_courier(name, phone, username, password):
            print(fr.GREEN + "[+] Courier registered successfully!" + st.RESET_ALL)
        else:
            print(fr.RED + "[-] Registration failed!" + st.RESET_ALL)
    elif option == "0":
        print(fr.YELLOW + "[!] Exiting program..." + st.RESET_ALL)
        break

    else:
        print(fr.RED + "[-] Invalid option!" + st.RESET_ALL)
