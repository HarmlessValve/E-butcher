import pyfiglet as pf
import questionary as qu
from tabulate import tabulate as tb
from colorama import Fore as fr, Style as st
from functions.connection import conn

def dashboard(username, password):
    msg = pf.figlet_format("Seller Dashboard", font="slant")
    print(fr.GREEN + st.BRIGHT + msg + st.RESET_ALL)

    while True:
        option = qu.select("dashboard menus", choices=["Account", "Products", "Orders", "Recap", "Exit"]).ask()

        if option == "Account":
            result = account(username, password)
            print((result))
            option = qu.select("Account Management", choices=["Edit Account","Back"]).ask()
            
            if option == "Edit Account":
                result = edit_account(username, password)
                
                if result == "logout":
                    print(fr.GREEN + "[+] data updated, login requiered\n" + st.RESET_ALL)
                    break

        elif option == "Products":
            result = product(username,password)
            
            if result == None:
                print(fr.YELLOW + "[-] data products not found\n" + st.RESET_ALL)
            
            option = qu.select("Products Management", choices=["Add Products","Edit Products", "Delete Products", "Exit"]).ask()


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
        SELECT s.seller_name, s.phone_num, s.username, s.password, a.street_name, d.district_name 
        FROM sellers s 
        JOIN addresses a ON s.address_id = a.address_id 
        JOIN districts d ON a.district_id = d.district_id
        WHERE s.username = %s AND s.password = %s
    """
    cursor.execute(query, (username, password))
    
    row = cursor.fetchone()
    if row is None:
        return "Akun tidak ditemukan."
    
    data = [list(row)]

    tb_headers = ["Seller Name", "Phone Number", "Username", "Password","Street Name", "District Name"]

    result = tb(data, headers=tb_headers, tablefmt="fancy_grid")

    cursor.close()
    connection.close()

    return result

def edit_account(username, password):
    connection, cursor = conn()

    # Ambil data user
    query = """
        SELECT s.seller_name, s.phone_num, s.username, s.password,
        a.address_id, a.street_name, d.district_id, d.district_name
        FROM sellers s
        JOIN addresses a ON s.address_id = a.address_id
        JOIN districts d ON a.district_id = d.district_id
        WHERE s.username = %s AND s.password = %s
    """
    cursor.execute(query, (username, password))
    data = cursor.fetchone()

    if not data:
        print("[-] Data not found.")
        return

    seller_name, phone_num, old_username, old_password, address_id, street_name, district_id, district_name = data

    print("[!] Edit Account")
    print("Press Enter for not updated data\n")

    # Input baru
    new_name = qu.text(f"Seller Name ({seller_name}): ").ask() or seller_name
    new_phone = qu.text(f"Phone Number ({phone_num}): ").ask() or phone_num
    new_username = qu.text(f"Username ({old_username}): ").ask() or old_username
    new_password = qu.text(f"Password ({old_password}): ").ask() or old_password
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
    update_seller = """
        UPDATE sellers
        SET seller_name = %s,
            phone_num = %s,
            username = %s,
            password = %s
        WHERE username = %s AND password = %s
    """
    cursor.execute(update_seller, (
        new_name, new_phone, new_username, new_password,
        old_username, old_password
    ))

    connection.commit()
    cursor.close()
    connection.close()

    return "logout"

def product(username,password):
    connection, cursor = conn()
    query = """
        SELECT p.product_id, p.product_name, p.product_stock, p.price, c.category_name 
        FROM products p 
        JOIN product_categories c ON p.category_id = c.category_id 
        JOIN sellers s ON p.seller_id = s.seller_id 
        WHERE username = %s AND password = %s
    """
    cursor.execute(query, (username, password))
    result = cursor.fetchone()

    cursor.close()
    connection.close()

    return result