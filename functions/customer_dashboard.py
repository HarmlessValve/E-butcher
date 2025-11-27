import pyfiglet as pf
import questionary as qu
from datetime import datetime
from tabulate import tabulate as tb
from colorama import Fore as fr, Style as st
from functions.connection import conn

def dashboard(username, password):
    msg = pf.figlet_format("Customers Dashboard", font="slant")
    print(fr.BLUE + st.BRIGHT + msg + st.RESET_ALL)

    while True:
        option = qu.select("dashboard menus", choices=["Account", "Orders", "Payment", "Exit"]).ask()

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
            product = products()
            print(product + "\n")
            option = qu.select("Orders Menu", choices=["Make Order","Cancel Order", "Back"]).ask()
            
            if option == "Make Order":
                make_order(username, password)
            elif option == "Cancel Order":
                cancel_order(username, password)

        elif option == "Payment":
            payment(username, password)

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

def products():
    connection, cursor = conn()

    query = """
        SELECT p.product_id, p.product_name, p.product_stock, p.price, pc.category_name 
        FROM products p 
        JOIN product_categories pc ON p.category_id = pc.category_id
        WHERE p.is_deleted = false 
        ORDER BY p.product_id
    """
    cursor.execute(query)
    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    if not rows:
        return fr.YELLOW + "[-] Data products not found." + st.RESET_ALL
    
    data = [list(row) for row in rows]

    headers = ["Product ID", "Name", "Stock", "Price", "Category"]

    table = tb(data, headers=headers, tablefmt="fancy_grid")
    return table

def make_order(username, password):
    connection, cursor = conn()

    cursor.execute("""
        SELECT customer_id, customer_name
        FROM customers
        WHERE username = %s AND password = %s
    """, (username, password))

    customer = cursor.fetchone()

    if not customer:
        return fr.RED + "[!] Invalid customer credentials." + st.RESET_ALL

    customer_id, customer_name = customer

    print(f"\n{fr.CYAN}Hello {customer_name}! Please select products to order.{st.RESET_ALL}\n")

    order_items = []

    while True:

        # ------------------------------
        # PRODUCT ID INPUT
        # ------------------------------
        pid = qu.text("Enter Product ID you want to order:").ask()

        if pid.strip() == "":
            print(fr.YELLOW + "\n[!] Order cancelled." + st.RESET_ALL)
            return

        try:
            pid = int(pid)
        except:
            print(fr.RED + "[!] Product ID must be a number." + st.RESET_ALL)
            continue

        cursor.execute("""
            SELECT product_id, product_name, product_stock, price
            FROM products
            WHERE product_id = %s AND is_deleted = false
        """, (pid,))

        product = cursor.fetchone()

        if not product:
            print(fr.RED + "[!] Product not found." + st.RESET_ALL)
            continue

        product_id, name, stock, price = product

        # ------------------------------
        # QUANTITY INPUT
        # ------------------------------
        qty = qu.text(f"Quantity for {name} (Stock {stock})").ask()

        if qty.strip() == "":
            print(fr.YELLOW + "\n[!] Order cancelled." + st.RESET_ALL)
            return

        try:
            qty = int(qty)
        except:
            print(fr.RED + "[!] Quantity must be a number." + st.RESET_ALL)
            continue

        if qty <= 0 or qty > stock:
            print(fr.RED + f"[!] Invalid quantity for {name}." + st.RESET_ALL)
            continue

        order_items.append((product_id, qty, price))

        more = qu.select("Add another product?", choices=["Yes", "No"]).ask()
        if more == "No":
            break

    if not order_items:
        return fr.YELLOW + "[!] No items selected. Order cancelled." + st.RESET_ALL

    # ------------------------------
    # PURCHASE PROCESS
    # ------------------------------
    cursor.execute("""
        INSERT INTO payments (payment_status, method_id)
        VALUES ('N', 1)
        RETURNING payment_id
    """)
    payment_id = cursor.fetchone()[0]

    cursor.execute("""
        INSERT INTO deliveries (delivery_date, delivery_status_id, courier_id)
        VALUES (%s, 1, 1)
        RETURNING delivery_id
    """, (datetime.now(),))
    delivery_id = cursor.fetchone()[0]

    cursor.execute("""
        INSERT INTO orders (order_date, order_status_id, payment_id, customer_id, delivery_id, is_deleted)
        VALUES (%s, 1, %s, %s, %s, false)
        RETURNING order_id
    """, (datetime.now(), payment_id, customer_id, delivery_id))
    order_id = cursor.fetchone()[0]

    for pid, qty, price in order_items:
        cursor.execute("""
            INSERT INTO order_details (quantity, discount, price, product_id, order_id)
            VALUES (%s, 0, %s, %s, %s)
        """, (qty, price, pid, order_id))

        cursor.execute("""
            UPDATE products
            SET product_stock = product_stock - %s
            WHERE product_id = %s
        """, (qty, pid))

    connection.commit()
    cursor.close()
    connection.close()

    return fr.GREEN + f"[+] Order #{order_id} created successfully!" + st.RESET_ALL

def cancel_order(username, password):
    connection, cursor = conn()

    # Validasi customer
    cursor.execute("""
        SELECT customer_id, customer_name
        FROM customers
        WHERE username = %s AND password = %s
    """, (username, password))
    
    customer = cursor.fetchone()

    if not customer:
        return fr.RED + "[!] Invalid customer credentials." + st.RESET_ALL

    customer_id, customer_name = customer

    print(f"\n{fr.CYAN}Hello {customer_name}! These are your orders:{st.RESET_ALL}\n")

    # ===============================
    # TAMPILKAN SEMUA ORDER CUSTOMER
    # ===============================
    cursor.execute("""
        SELECT 
            o.order_id, 
            o.order_date, 
            s.order_status,
            p.payment_status
        FROM orders o
        JOIN order_status s ON o.order_status_id = s.order_status_id
        JOIN payments p ON o.payment_id = p.payment_id
        WHERE o.customer_id = %s 
        AND o.is_deleted = false
        ORDER BY o.order_id
    """, (customer_id,))

    rows = cursor.fetchall()

    if not rows:
        cursor.close()
        connection.close()
        return fr.YELLOW + "[!] You have no orders to cancel." + st.RESET_ALL

    # Tampilkan tabel rapi
    data = [list(row) for row in rows]
    headers = ["Order ID", "Order Date", "Status", "Payment"]
    print(tb(data, headers=headers, tablefmt="fancy_grid"))

    # ===============================
    # PILIH ORDER UNTUK DIBATALKAN
    # ===============================
    order_id = qu.text("\nEnter the Order ID you want to cancel: ").ask()

    try:
        order_id = int(order_id)
    except:
        return fr.RED + "[!] Order ID must be a number." + st.RESET_ALL

    # Pastikan order miliknya
    cursor.execute("""
        SELECT order_status_id
        FROM orders
        WHERE order_id = %s 
        AND customer_id = %s 
        AND is_deleted = false
    """, (order_id, customer_id))
    
    order = cursor.fetchone()

    if not order:
        return fr.RED + "[!] Order not found or does not belong to you." + st.RESET_ALL

    current_status = order[0]

    # Validasi status
    if current_status == 4:
        return fr.YELLOW + "[!] This order is already canceled." + st.RESET_ALL

    if current_status == 3:
        return fr.YELLOW + "[!] Accepted orders cannot be canceled." + st.RESET_ALL

    # Eksekusi cancel
    cursor.execute("""
        UPDATE orders
        SET order_status_id = 4
        WHERE order_id = %s
    """, (order_id,))

    connection.commit()
    cursor.close()
    connection.close()

    return fr.GREEN + f"[+] Order #{order_id} has been successfully canceled!" + st.RESET_ALL

def payment(username, password):
    connection, cursor = conn()

    # ------------------------------------------------------
    # VERIFIKASI CUSTOMER
    # ------------------------------------------------------
    cursor.execute("""
        SELECT customer_id 
        FROM customers 
        WHERE username = %s AND password = %s
    """, (username, password))

    customer = cursor.fetchone()
    if not customer:
        print(fr.RED + "[!] Invalid customer credentials." + st.RESET_ALL)
        return False

    customer_id = customer[0]

    # ------------------------------------------------------
    # TAMPILKAN ORDER YANG BELUM DIBAYAR
    # ------------------------------------------------------
    cursor.execute("""
        SELECT 
            o.order_id,
            o.order_date,
            p.payment_status,
            SUM(od.quantity * od.price) AS total_price
        FROM orders o
        JOIN payments p ON o.payment_id = p.payment_id
        JOIN order_details od ON o.order_id = od.order_id
        WHERE o.customer_id = %s 
            AND o.is_deleted = FALSE
            AND p.payment_status = 'N'
        GROUP BY o.order_id, o.order_date, p.payment_status
        ORDER BY o.order_id ASC
    """, (customer_id,))

    unpaid_orders = cursor.fetchall()

    if unpaid_orders:
        print("\n" + fr.CYAN + "Orders that need payment:" + st.RESET_ALL)

        headers = ["Order ID", "Order Date", "Payment Status", "Total Price"]
        print(tb(unpaid_orders, headers=headers, tablefmt="fancy_grid"))

    else:
        print(fr.YELLOW + "\n[!] You have no unpaid orders." + st.RESET_ALL)
        return False

    # ------------------------------------------------------
    # INPUT ORDER ID
    # ------------------------------------------------------
    order_id = qu.text("\nEnter Order ID to process payment: ").ask()

    if not order_id.strip():
        print(fr.YELLOW + "[!] Cancelled." + st.RESET_ALL)
        return False

    cursor.execute("""
        SELECT o.order_id, p.payment_id, p.payment_status
        FROM orders o
        JOIN payments p ON o.payment_id = p.payment_id
        WHERE o.order_id = %s AND o.customer_id = %s AND o.is_deleted = false
    """, (order_id, customer_id))

    order = cursor.fetchone()
    if not order:
        print(fr.RED + "[-] Order not found." + st.RESET_ALL)
        return False

    _, payment_id, payment_status = order

    # Sudah dibayar
    if payment_status == "Y":
        print(fr.GREEN + "[!] This order is already paid." + st.RESET_ALL)
        return True

    # ------------------------------------------------------
    # METODE PEMBAYARAN
    # ------------------------------------------------------
    method = qu.select(
        "Select payment method:",
        choices=["Transfer", "COD", "Cancel"]
    ).ask()

    if method == "Cancel":
        print(fr.YELLOW + "\n[!] Payment cancelled." + st.RESET_ALL)
        return False

    # ------------------------------------------------------
    # TRANSFER
    # ------------------------------------------------------
    if method == "Transfer":
        cursor.execute("""
            UPDATE payments
            SET payment_status = 'Y'
            WHERE payment_id = %s
        """, (payment_id,))
        
        connection.commit()
        print(fr.GREEN + "\n[+] Payment completed via Transfer!" + st.RESET_ALL)
        return True

    # ------------------------------------------------------
    # COD
    # ------------------------------------------------------
    if method == "COD":
        cod_status = qu.select(
            "COD Status:",
            choices=["Received", "Back", "Cancel"]
        ).ask()

        if cod_status == "Cancel":
            print(fr.YELLOW + "[!] Payment cancelled." + st.RESET_ALL)
            return False

        if cod_status == "Received":
            cursor.execute("""
                UPDATE payments
                SET payment_status = 'Y'
                WHERE payment_id = %s
            """, (payment_id,))
            connection.commit()
            print(fr.GREEN + "\n[+] COD Payment marked as RECEIVED!" + st.RESET_ALL)
            return True

        if cod_status == "Back":
            cursor.execute("""
                UPDATE payments
                SET payment_status = 'N'
                WHERE payment_id = %s
            """, (payment_id,))
            connection.commit()
            print(fr.YELLOW + "\n[!] COD returned. Payment remains UNPAID." + st.RESET_ALL)
            return False

    return False
