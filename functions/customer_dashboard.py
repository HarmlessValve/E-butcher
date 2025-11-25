import pyfiglet as pf
import questionary as qu
from tabulate import tabulate as tb
from colorama import Fore as fr, Style as st
from functions.connection import conn

def dashboard(username, password):
    msg = pf.figlet_format("Customers Dashboard", font="slant")
    print(fr.BLUE + st.BRIGHT + msg + st.RESET_ALL)

    while True:
        option = qu.select("dashboard menus", choices=["Account", "Orders", "Exit"]).ask()

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
            print("Order menu... (belum dibuat)")

        elif option == "Recap":
            print("Recap menu... (belum dibuat)")

        elif option == "Exit":
            print("Keluar dari dashboard.")
            break

def account(username, password):
    connection, cursor = conn()
    query = """
        SELECT c.customer_name, c.phone_num, c.username, c.password, a.street_name, d.district_name 
        FROM customers c
        JOIN addresses a ON c.address_id = a.address_id 
        JOIN districts d ON a.district_id = d.district_id
        WHERE c.username = %s AND c.password = %s
    """
    cursor.execute(query, (username, password))
    
    row = cursor.fetchone()
    if row is None:
        return "[-] Customer not found."
    
    data = [list(row)]

    tb_headers = ["Customer Name", "Phone Number", "Username", "Password","Street Name", "District Name"]

    result = tb(data, headers=tb_headers, tablefmt="fancy_grid")

    cursor.close()
    connection.close()

    return result

def edit_account(username, password):
    connection, cursor = conn()

    # Ambil data user
    query = """
        SELECT c.customer_name, c.phone_num, c.username, c.password,
        a.address_id, a.street_name, d.district_name
        FROM customers c
        JOIN addresses a ON c.address_id = a.address_id
        JOIN districts d ON a.district_id = d.district_id
        WHERE c.username = %s AND c.password = %s
    """
    cursor.execute(query, (username, password))
    data = cursor.fetchone()

    if not data:
        print("[-] Data not found.")
        return 
    
    customer_name, phone_num, old_username, old_password, address_id, street_name, district_name = data

    print(fr.YELLOW + "[!] Edit Account" + st.RESET_ALL)
    print("press Enter for non-updated datas\n")

    # Input baru
    new_name = qu.text(f"Customer Name ({customer_name}): ").ask() or customer_name
    new_phone = qu.text(f"Phone Number ({phone_num}): ").ask() or phone_num
    new_username = qu.text(f"Username ({old_username}): ").ask() or old_username
    new_password = qu.password(f"Password ({old_password}): ").ask() or old_password
    new_street = qu.text(f"Street Name ({street_name}): ").ask() or street_name
    new_district = qu.text(f"District Name ({district_name}): ").ask() or district_name

    # ---------------------------------------------------------
    # UPDATE address (POSTGRESQL version)
    # ---------------------------------------------------------
    update_address = """
        UPDATE addresses AS a
        SET street_name = %s
        FROM districts AS d
        WHERE a.address_id = %s
        AND a.district_id = d.district_id
    """
    cursor.execute(update_address, (new_street, address_id))

    # UPDATE district_name (harus query terpisah)
    update_district = """
        UPDATE districts
        SET district_name = %s
        WHERE district_id = (
            SELECT district_id FROM addresses WHERE address_id = %s
        )
    """
    cursor.execute(update_district, (new_district, address_id))

    # ---------------------------------------------------------
    # UPDATE seller data
    # ---------------------------------------------------------
    update_customer = """
        UPDATE customers
        SET customer_name = %s,
            phone_num = %s,
            username = %s,
            password = %s
        WHERE username = %s AND password = %s
    """
    cursor.execute(update_customer, (
        new_name, new_phone, new_username, new_password,
        old_username, old_password
    ))

    connection.commit()
    cursor.close()
    connection.close()

    return "logout"
