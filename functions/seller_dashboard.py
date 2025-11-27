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
            order = orders(username, password)
            print(order)
            if not order:
                print(fr.YELLOW + "[-] data orders not found\n" + st.RESET_ALL)
            
            option = qu.select("Orders Management", choices=["Accept Orders","Reject Orders", "Back"]).ask()
            
            if option == "Accept Orders":
                accept_order(username, password)
            elif option == "Reject Orders":
                reject_order(username, password)
                
        elif option == "Recap":
            
            option = qu.select("Recap", choices=["Recap Order","Recap Delivery", "Back"]).ask()
            
            if option == "Recap Order":
                recap = recap_order(username, password)
                print(recap)
                if not recap:
                    print(fr.YELLOW + "[-] data recap not found\n" + st.RESET_ALL)
                    
            elif option == "Recap Delivery":
                recap = recap_delivery(username, password)
                print(recap)
                if not recap:
                    print(fr.YELLOW + "[-] data recap not found\n" + st.RESET_ALL)
                
        elif option == "Exit":
            print(fr.YELLOW + "[!] Exiting Dashboard..." + st.RESET_ALL)
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

    headers = ["Product ID", "Name", "Stock", "Price", "Category", "Remove Product"]

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
            SELECT p.product_id, p.product_name, p.product_stock, p.price, c.category_name, p.is_deleted
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
            headers=["Product ID", "Name", "Stock", "Price", "Category", "Remove Product"],
            tablefmt="fancy_grid"
        ))

        # ---------------------------------------------------------
        # 3. Choose product
        # ---------------------------------------------------------
        product_id = qu.text("Enter Product ID to edit: ").ask()

        cursor.execute("""
            SELECT p.product_name, p.product_stock, p.price, c.category_name, p.is_deleted
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
            f"Product Visibility (current: {'Hidden' if old_is_deleted else 'Show'}): ",
            choices=[
                "Show",
                "Hide",
                "Keep current"
            ]
        ).ask()

        if visibility_choice.startswith("Show"):
            new_is_deleted = False
        elif visibility_choice.startswith("Hide"):
            new_is_deleted = True
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

def orders(username, password):
    connection, cursor = conn()

    query = """
    SELECT o.order_id, p.product_name, pc.category_name, p.product_stock,
    od.quantity, p.price, od.discount, os.order_status, c.customer_name, py.payment_status,
    pm.method_name
    FROM products p 
    JOIN product_categories pc ON p.category_id = pc.category_id 
    JOIN sellers s ON p.seller_id = s.seller_id
    JOIN order_details od ON p.product_id = od.product_id
    JOIN orders o ON od.order_id = o.order_id
    JOIN customers c ON o.customer_id = c.customer_id
    JOIN order_status os ON o.order_status_id = os.order_status_id
    JOIN payments py ON o.payment_id = py.payment_id
    JOIN payment_methods pm ON py.method_id = pm.method_id
    WHERE s.username = %s AND s.password = %s AND o.is_deleted = false
    ORDER BY o.order_id
    """
    cursor.execute(query, (username, password))
    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    if not rows:
        return fr.YELLOW + "[-] Data orders not found." + st.RESET_ALL

    data = [list(row) for row in rows]

    headers = ["Order ID", "Name", "Category", "Stock", "Order Quantity", "Price", "Discount", "Order Status", "Customer", "Payment Status", "Payment Method"]

    table = tb(data, headers=headers, tablefmt="fancy_grid")
    return table

def accept_order(username, password):
    connection, cursor = conn()
    
    try:
        # Validasi seller
        cursor.execute(
            "SELECT seller_id FROM sellers WHERE username = %s AND password = %s",
            (username, password)
        )
        seller = cursor.fetchone()
        
        if not seller:
            print("[-] Seller authentication failed.")
            return False

        seller_id = seller[0]

        # Input order ID
        order_id = qu.text("Enter Order ID to mark as accepted: ").ask()

        # Cek bahwa order milik produk seller
        cursor.execute("""
            SELECT o.order_id
            FROM orders o
            JOIN order_details od ON o.order_id = od.order_id
            JOIN products p ON od.product_id = p.product_id
            WHERE o.order_id = %s 
            AND p.seller_id = %s 
            AND o.is_deleted = false
            LIMIT 1
        """, (order_id, seller_id))

        valid = cursor.fetchone()

        if not valid:
            print(fr.RED + "[-] Order not found or does not belong to your products." + st.RESET_ALL)
            return False

        # ===========================================================
        # 1. Ambil SEMUA produk & quantity dalam order tersebut
        # ===========================================================
        cursor.execute("""
            SELECT p.product_id, od.quantity
            FROM order_details od
            JOIN products p ON od.product_id = p.product_id
            WHERE od.order_id = %s
            AND p.seller_id = %s
        """, (order_id, seller_id))

        items = cursor.fetchall()

        if not items:
            print(fr.RED + "[-] No products found for this order." + st.RESET_ALL)
            return False

        # ===========================================================
        # 2. Kurangi stok produk per item
        # ===========================================================
        for product_id, qty in items:
            cursor.execute("""
                UPDATE products
                SET product_stock = product_stock - %s
                WHERE product_id = %s
            """, (qty, product_id))

        # ===========================================================
        # 3. Update status order menjadi accepted (3)
        # ===========================================================
        cursor.execute("""
            UPDATE orders
            SET order_status_id = 3
            WHERE order_id = %s
        """, (order_id,))

        connection.commit()
        print(fr.GREEN + "\n[+] Order marked as accepted and stock updated!" + st.RESET_ALL)
        return True

    except Exception as e:
        connection.rollback()
        print(fr.RED + f"\n[-] Error: {e}" + st.RESET_ALL)
        return False

    finally:
        cursor.close()
        connection.close()

def reject_order(username, password):
    connection, cursor = conn()
    
    try:
        cursor.execute(
            "SELECT seller_id FROM sellers WHERE username = %s AND password = %s",
            (username, password)
        )
        seller = cursor.fetchone()
        
        if not seller:
            print("[-] Seller authentication failed.")
            return False

        seller_id = seller[0]

        order_id = qu.text("Enter Order ID to mark as rejected: ").ask()

        cursor.execute("""
            SELECT o.order_id
            FROM orders o
            JOIN order_details od ON o.order_id = od.order_id
            JOIN products p ON od.product_id = p.product_id
            WHERE o.order_id = %s AND p.seller_id = %s AND o.is_deleted = false
        """, (order_id, seller_id))

        valid = cursor.fetchone()

        if not valid:
            print("[-] Order not found")
            return False

        cursor.execute("""
            UPDATE orders
            SET order_status_id = 2
            WHERE order_id = %s
        """, (order_id,))

        connection.commit()
        print(fr.GREEN + "\n[+] Order marked as rejected" + st.RESET_ALL)
        return True

    except Exception:
        connection.rollback()
        print(fr.RED + "\n[-] invalid Input syntax" + st.RESET_ALL)
        return False

    finally:
        cursor.close()
        connection.close()

def recap_order(username, password):
    connection, cursor = conn()

    query = """
            SELECT o.order_date, p.product_name, pc.category_name, od.quantity, p.price, od.discount, 
            p.price - (p.price * od.discount / 100) as discounted_price,
            os.order_status, c.customer_name, py.payment_status, pm.method_name
            FROM products p 
            JOIN product_categories pc ON p.category_id = pc.category_id 
            JOIN sellers s ON p.seller_id = s.seller_id
            JOIN order_details od ON p.product_id = od.product_id
            JOIN orders o ON od.order_id = o.order_id
            JOIN customers c ON o.customer_id = c.customer_id
            JOIN order_status os ON o.order_status_id = os.order_status_id
            JOIN payments py ON o.payment_id = py.payment_id
            JOIN payment_methods pm ON py.method_id = pm.method_id
            WHERE s.username = %s AND s.password = %s AND o.is_deleted = false AND os.order_status = 'Accepted' AND py.payment_status = 'Y'
            ORDER BY c.customer_name
    """
    cursor.execute(query, (username, password))
    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    if not rows:
        return fr.YELLOW + "[-] Data orders not found." + st.RESET_ALL

    data = [list(row) for row in rows]

    headers = ["Order Date", "Name", "Category", "Order Quantity", "Price", "Discount", "Discounted Price", "Order Status", "Customer", "Payment Status", "Payment Method"]

    table = tb(data, headers=headers, tablefmt="fancy_grid")
    return table

def recap_delivery(username, password):
    connection, cursor = conn()

    query = """
            SELECT o.order_date, p.product_name, pc.category_name, od.quantity,
            os.order_status, c.customer_name, ds.delivery_status, cr.courier_name
            FROM products p 
            JOIN product_categories pc ON p.category_id = pc.category_id 
            JOIN sellers s ON p.seller_id = s.seller_id
            JOIN order_details od ON p.product_id = od.product_id
            JOIN orders o ON od.order_id = o.order_id
            JOIN customers c ON o.customer_id = c.customer_id
            JOIN order_status os ON o.order_status_id = os.order_status_id
            JOIN payments py ON o.payment_id = py.payment_id
            JOIN payment_methods pm ON py.method_id = pm.method_id
			JOIN deliveries de ON o.delivery_id = de.delivery_id
			JOIN delivery_status ds ON de.delivery_status_id = ds.delivery_status_id
			JOIN couriers cr ON de.courier_id = cr.courier_id
            WHERE s.username = 'ta' AND s.password = 'ta' AND o.is_deleted = false AND os.order_status = 'Accepted' AND py.payment_status = 'Y'
            ORDER BY c.customer_name
    """
    cursor.execute(query, (username, password))
    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    if not rows:
        return fr.YELLOW + "[-] Data orders not found." + st.RESET_ALL

    data = [list(row) for row in rows]

    headers = ["Order Date", "Name", "Category", "Order Quantity", "Order Status", "Customer", "Delivery Status", "Courier"]

    table = tb(data, headers=headers, tablefmt="fancy_grid")
    return table
