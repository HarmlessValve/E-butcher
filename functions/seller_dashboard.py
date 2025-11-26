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
            result = product(username, password)
            if result:
                print(result)
            
            option = qu.select("Products Management", choices=["Add Products","Edit Products", "Back"]).ask()
            
            if option == "Add Products":
                category_name = qu.text("Enter Category Name:").ask()
                product_name = qu.text("Enter Product Name:").ask()
                product_stock = qu.text("Enter Product Stock:").ask()
                price = qu.text("Enter Price:").ask()

                result = add_product(category_name, product_name, product_stock, price)
                print(result + "\n")
            elif option == "Edit Products":
                result = edit_product()
                
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

    # Get seller_id from username and password
    cursor.execute("SELECT seller_id FROM sellers WHERE username = %s AND password = %s", (username, password))
    seller = cursor.fetchone()
    if not seller:
        print("[-] Seller not found.")
        cursor.close()
        connection.close()
        return

    seller_id = seller[0]

    cursor.execute("""
        SELECT c.category_name, p.product_name, p.product_stock, p.price
        FROM products p
        JOIN product_categories c ON p.category_id = c.category_id
        WHERE p.seller_id = %s
    """, (seller_id,))

    rows = cursor.fetchall()

    if not rows:
        print("[-] No products found.")
        cursor.close()
        connection.close()
        return

    print(tb(
        rows,
        headers=["Category Name", "Product Name", "Stock", "Price"],
        tablefmt="fancy_grid"
    ))

    cursor.close()
    connection.close()

def add_product(category_name, product_name, product_stock, price):
    connection, cursor = conn()

    try:
        # Use default seller_id for testing (no authentication)
        seller_id = 1  # Assuming seller_id 1 exists

        # Insert or get category_id
        cursor.execute("SELECT category_id FROM product_categories WHERE category_name = %s", (category_name,))
        category = cursor.fetchone()
        if category:
            category_id = category[0]
        else:
            cursor.execute("INSERT INTO product_categories (category_name) VALUES (%s) RETURNING category_id", (category_name,))
            category_id = cursor.fetchone()[0]

        # Insert new product
        cursor.execute("""
            INSERT INTO products (product_name, product_stock, price, category_id, seller_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (product_name, product_stock, price, category_id, seller_id))

        connection.commit()
        return fr.GREEN + "[+] Product added successfully!" + st.RESET_ALL

    except Exception as e:
        connection.rollback()
        return fr.RED + f"[-] Error adding product: {str(e)}" + st.RESET_ALL

    finally:
        cursor.close()
        connection.close()
    
def edit_product():
    connection, cursor = conn()

    try:
        # Use default seller_id for testing (no authentication)
        seller_id = 1  # Assuming seller_id 1 exists

        # ---------------------------------------------------------
        # 2. Show seller's products
        # ---------------------------------------------------------
        cursor.execute("""
            SELECT p.product_id, p.product_name, p.product_stock, p.price,
                   c.category_name
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
            headers=["Product ID", "Name", "Stock", "Price", "Category"],
            tablefmt="fancy_grid"
        ))

        # ---------------------------------------------------------
        # 3. Choose product
        # ---------------------------------------------------------
        product_id = qu.text("Enter Product ID to edit: ").ask()

        cursor.execute("""
            SELECT p.product_name, p.product_stock, p.price,
                   c.category_name
            FROM products p
            JOIN product_categories c ON p.category_id = c.category_id
            WHERE p.product_id = %s AND p.seller_id = %s
        """, (product_id, seller_id))

        product = cursor.fetchone()

        if not product:
            print("[-] Product not found or not owned by this seller.")
            return

        old_name, old_stock, old_price, old_category = product

        # ---------------------------------------------------------
        # 4. New input (optional)
        # ---------------------------------------------------------
        print("press Enter for non-updated datas\n")

        new_category = qu.text(f"Category ({old_category}): ").ask() or old_category
        new_name = qu.text(f"Product Name ({old_name}): ").ask() or old_name
        new_stock = qu.text(f"Stock ({old_stock}): ").ask() or old_stock
        new_price = qu.text(f"Price ({old_price}): ").ask() or old_price

        # ---------------------------------------------------------
        # 5. Insert new category & update product
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
                category_id = (SELECT category_id FROM category)
            WHERE product_id = %s AND seller_id = %s;
        """

        cursor.execute(query, (
            new_category,
            new_name, new_stock, new_price,
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
