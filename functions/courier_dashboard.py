import pyfiglet as pf
import questionary as qu
from datetime import datetime
from tabulate import tabulate as tb
from colorama import Fore as fr, Style as st
from functions.connection import conn

def dashboard(username, password):
    msg = pf.figlet_format("Courier Dashboard", font="slant")
    print(fr.BLUE + st.BRIGHT + msg + st.RESET_ALL)

    while True:
        option = qu.select("dashboard menus", choices=["Account", "Order", "Delivery", "Exit"]).ask()

        if option == "Account":
            result = account(username, password)
            print(result + "\n")
            option = qu.select("Account Management", choices=["Edit Account","Back"]).ask()
            
            if option == "Edit Account":
                result = edit_account(username, password)
                
                if result == "logout":
                    print(fr.GREEN + "[+] data updated, login requiered\n" + st.RESET_ALL)
                    break
                
        elif option == "Orders":
            print()
        elif option == "Payment":
            print()
        elif option == "Exit":
            print("Keluar dari dashboard.")
            break

def account(username, password):
    connection, cursor = conn()
    query = """
        SELECT c.courier_name, c.phone_num, c.username, c.password
        FROM couriers c
        WHERE c.username = %s AND c.password = %s
    """
    cursor.execute(query, (username, password))
    
    row = cursor.fetchone()
    if row is None:
        return "[-] Courier not found."
    
    data = [list(row)]

    tb_headers = ["Courier Name", "Phone Number", "Username", "Password"]

    result = tb(data, headers=tb_headers, tablefmt="fancy_grid")

    cursor.close()
    connection.close()

    return result

def edit_account(username, password):
    connection, cursor = conn()

    # Ambil data user
    query = """
        SELECT c.courier_name, c.phone_num, c.username, c.password
        FROM couriers c
        WHERE c.username = %s AND c.password = %s
    """
    cursor.execute(query, (username, password))
    data = cursor.fetchone()

    if not data:
        print("[-] Data not found.")
        return 
    
    courier_name, phone_num, old_username, old_password = data

    print(fr.YELLOW + "[!] Edit Account" + st.RESET_ALL)
    print("press Enter for non-updated datas\n")

    # Input baru
    new_name = qu.text(f"Courier Name ({courier_name}): ").ask() or courier_name
    new_phone = qu.text(f"Phone Number ({phone_num}): ").ask() or phone_num
    new_username = qu.text(f"Username ({old_username}): ").ask() or old_username
    new_password = qu.password(f"Password ({old_password}): ").ask() or old_password

    update_courier = """
        UPDATE couriers
        SET courier_name = %s,
            phone_num = %s,
            username = %s,
            password = %s
        WHERE username = %s AND password = %s
    """
    cursor.execute(update_courier, (new_name, new_phone, new_username, new_password, old_username, old_password
    ))

    connection.commit()
    cursor.close()
    connection.close()

    return "logout"

