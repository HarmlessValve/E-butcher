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
            print(result + "\n")
            option = qu.select("Account Management", choices=["Edit Account","Back"]).ask()
            
            if option == "Edit Account":
                result = edit_account(username, password)
                
                if result == "logout":
                    print(fr.GREEN + "[+] data updated, login requiered\n" + st.RESET_ALL)
                    break

        elif option == "Products":
            products = product(username, password)
            print(products)
            if not products:
                print(fr.YELLOW + "[-] data products not found\n" + st.RESET_ALL)
            
            option = qu.select("Products Management", choices=["Add Products","Edit Products", "Back"]).ask()
            
            if option == "Add Products":
                
                product_name = qu.text("Product Name: ").ask()
                stock = qu.text("Stock: ").ask()
                price = qu.text("Price: ").ask()
                category_name = qu.text("Category: ").ask()
                
                result = add_product(username, password, product_name, stock, price, category_name)
                
            elif option == "Edit Products":
                result = edit_product(username, password)
                
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
        return "[-] Seller not found."
    
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
        a.address_id, a.street_name, d.district_name
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
    
    seller_name, phone_num, old_username, old_password, address_id, street_name, district_name = data

    print(fr.YELLOW + "[!] Edit Account" + st.RESET_ALL)
    print("press Enter for non-updated datas\n")

    # Input baru
    new_name = qu.text(f"Seller Name ({seller_name}): ").ask() or seller_name
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

def product(username, password):
    connection, cursor = conn()

    query = """
        SELECT p.product_id, p.product_name, p.product_stock, p.price, c.category_name, p.is_deleted 
        FROM products p 
        JOIN product_categories c ON p.category_id = c.category_id 
        JOIN sellers s ON p.seller_id = s.seller_id 
        WHERE s.username = %s AND s.password = %s
    """
    cursor.execute(query, (username, password))
    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    if not rows:
        return fr.YELLOW + "[-] Data products not found." + st.RESET_ALL

    # Convert each row tuple → list
    data = [list(row) for row in rows]

    headers = ["Product ID", "Name", "Stock", "Price", "Category", "Display Product"]

    table = tb(data, headers=headers, tablefmt="fancy_grid")
    return table

def add_product(username, password, product_name, stock, price, category_name):
    connection, cursor = conn()

    try:
        # Cek seller terlebih dahulu
        cursor.execute(
            "SELECT seller_id FROM sellers WHERE username = %s AND password = %s",
            (username, password)
        )
        seller = cursor.fetchone()

        if not seller:
            print(fr.RED + "[-] Seller authentication failed." + st.RESET_ALL)
            cursor.close()
            connection.close()
            return False

        # Query insert produk + kategori
        query = """
            WITH category AS (
                INSERT INTO product_categories (category_name)
                VALUES (%s)
                RETURNING category_id
            ),
            seller_data AS (
                SELECT seller_id FROM sellers
                WHERE username = %s AND password = %s
            )
            INSERT INTO products (product_name, product_stock, price, seller_id, category_id)
            SELECT %s, %s, %s, s.seller_id, c.category_id
            FROM seller_data s, category c;
        """

        cursor.execute(query, (
            category_name,
            username, password,
            product_name, stock, price
        ))

        connection.commit()
        print(fr.GREEN + "[+] Product + Category inserted successfully!" + st.RESET_ALL)

        cursor.close()
        connection.close()
        return True

    except:
        print(fr.RED + "\n[-] invalid Input syntax" + st.RESET_ALL)
        
        connection.rollback()
        cursor.close()
        connection.close()
        return False
    
def edit_product(username, password):
    connection, cursor = conn()

    try:
        # ---------------------------------------------------------
        # 1. Authenticate seller
        # ---------------------------------------------------------
        cursor.execute(
            "SELECT seller_id FROM sellers WHERE username = %s AND password = %s",
            (username, password)
        )
        seller = cursor.fetchone()

        if not seller:
            print("[-] Seller authentication failed.")
            return

        seller_id = seller[0]

        # ---------------------------------------------------------
        # 2. Show seller's products
        # ---------------------------------------------------------
        cursor.execute("""
            SELECT p.product_id, p.product_name, p.product_stock, p.price, 
                   c.category_name, p.is_deleted
            FROM products p
            JOIN product_categories c ON p.category_id = c.category_id
            WHERE p.seller_id = %s
        """, (seller_id, ))

        rows = cursor.fetchall()

        if not rows:
            print("[-] No products found.")
            return

        print(tb(
            rows,
            headers=["Product ID", "Name", "Stock", "Price", "Category", "Display Product"],
            tablefmt="fancy_grid"
        ))

        # ---------------------------------------------------------
        # 3. Choose product
        # ---------------------------------------------------------
        product_id = qu.text("Enter Product ID to edit: ").ask()

        cursor.execute("""
            SELECT p.product_name, p.product_stock, p.price, 
                   c.category_name, p.is_deleted
            FROM products p
            JOIN product_categories c ON p.category_id = c.category_id
            WHERE p.product_id = %s AND p.seller_id = %s
        """, (product_id, seller_id))

        product = cursor.fetchone()

        if not product:
            print("[-] Product not found or not owned by this seller.")
            return

        old_name, old_stock, old_price, old_category, old_is_deleted = product

        # ---------------------------------------------------------
        # 4. New input (optional)
        # ---------------------------------------------------------
        print("press Enter for non-updated datas\n")

        new_name = qu.text(f"Product Name ({old_name}): ").ask() or old_name
        new_stock = qu.text(f"Stock ({old_stock}): ").ask() or old_stock
        new_price = qu.text(f"Price ({old_price}): ").ask() or old_price
        new_category = qu.text(f"Category ({old_category}): ").ask() or old_category

        # ---------------------------------------------------------
        # 5. NEW — select input for is_deleted (uses choices)
        # ---------------------------------------------------------
        visibility_choice = qu.select(
            f"Product Visibility (current: {'Showed' if old_is_deleted else 'Hidden'}): ",
            choices=[
                "Show",
                "Hide",
                "Keep current"
            ]
        ).ask()

        if visibility_choice.startswith("Show"):
            new_is_deleted = True
        elif visibility_choice.startswith("Hide"):
            new_is_deleted = False
        else:
            new_is_deleted = old_is_deleted

        # ---------------------------------------------------------
        # 6. Insert new category & update product
        # ---------------------------------------------------------
        query = """
            WITH category AS (
                INSERT INTO product_categories (category_name)
                VALUES (%s)
                RETURNING category_id
            )
            UPDATE products
            SET product_name = %s,
                product_stock = %s,
                price = %s,
                category_id = (SELECT category_id FROM category),
                is_deleted = %s
            WHERE product_id = %s AND seller_id = %s;
        """

        cursor.execute(query, (
            new_category,
            new_name, new_stock, new_price,
            new_is_deleted,
            product_id, seller_id
        ))

        connection.commit()
        print(fr.GREEN + "\n[+] Product updated!" + st.RESET_ALL)
        return "success"

    except Exception:
        connection.rollback()
        print(fr.RED + "\n[-] invalid input syntax" + st.RESET_ALL)
        return False

    finally:
        cursor.close()
        connection.close()
