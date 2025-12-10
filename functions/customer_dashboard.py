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
            seller_id = sellers()
            print(seller_id)
            print()
            
            product = products(seller_id)
            
            if product == "back":
                return dashboard(username, password)
            
            print(product + "\n")
            option = qu.select("Orders Menu", choices=["Make Order","Cancel Order", "Back"]).ask()
            
            if option == "Make Order":
                make_order(username, password)
            elif option == "Cancel Order":
                cancel_order(username, password)

        elif option == "Payment":
            payment(username, password)

        elif option == "Exit":
            print("[!] Exiting dashboard...")
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

def validate_input(*fields):
    return all(field and field.strip() != "" for field in fields)

def validate_input_name(*fields):
    return all(
        field 
        and field.strip() != "" 
        and field.replace(" ", "").isalpha()
        for field in fields
    )

def validate_phone(phone):
    return phone.isdigit() and len(phone) == 12

def edit_account(username, password):
    connection, cursor = conn()

    query = """
        SELECT c.customer_name, c.phone_num, c.username, c.password, a.address_id, a.street_name, a.district_id
        FROM customers c
        JOIN addresses a ON c.address_id = a.address_id
        WHERE c.username = %s AND c.password = %s AND c.is_deleted = FALSE
    """
    cursor.execute(query, (username, password))
    data = cursor.fetchone()

    if not data:
        print(fr.RED + "[-] Data not found." + st.RESET_ALL)
        return

    customer_name, phone_num, old_username, old_password, address_id, street_name, district_id = data

    delete_choice = qu.select(
        "Do you want to delete your account?",
        choices=["No", "Yes"]
    ).ask()

    if delete_choice == "Yes":
        cursor.execute("""
            UPDATE customers
            SET is_deleted = TRUE
            WHERE username = %s AND password = %s
        """, (old_username, old_password))

        connection.commit()
        cursor.close()
        connection.close()

        print(fr.GREEN + "[+] Account deleted successfully." + st.RESET_ALL)
        return "logout"

    print(fr.YELLOW + "[!] Edit Account" + st.RESET_ALL)
    print("Press Enter for non-updated fields.\n")

    new_name = qu.text(f"Customer Name ({customer_name}): ").ask() or customer_name
    new_phone = qu.text(f"Phone Number ({phone_num}): ").ask() or phone_num
    new_username = qu.text(f"Username ({old_username}): ").ask() or old_username
    new_password = qu.password(f"Password ({old_password}): ").ask() or old_password
    new_street = qu.text(f"Street Name ({street_name}): ").ask() or street_name

    if not validate_input_name(new_name):
        print(fr.RED + "[-] Invalid input customer name!\n" + st.RESET_ALL)
    
    if not validate_input(new_phone, new_username, new_password):
        print(fr.RED + "[-] All fields must be filled!\n" + st.RESET_ALL)
        return

    if not validate_phone(new_phone):
        print(fr.RED + "[-] Phone number must be 12 digits!\n" + st.RESET_ALL)
        return

    cursor.execute("SELECT district_id, district_name FROM districts ORDER BY district_id ASC")
    district_data = cursor.fetchall()

    district_names = [d[1] for d in district_data]
    current_district_name = next(d[1] for d in district_data if d[0] == district_id)

    new_district_name = qu.select(
        f"District (Current: {current_district_name})",
        choices=district_names
    ).ask()

    new_district_id = next(d[0] for d in district_data if d[1] == new_district_name)

    cursor.execute("""
        UPDATE addresses
        SET street_name = %s, district_id = %s
        WHERE address_id = %s
    """, (new_street, new_district_id, address_id))

    cursor.execute("""
        UPDATE customers
        SET customer_name = %s,
            phone_num = %s,
            username = %s,
            password = %s
        WHERE username = %s AND password = %s
    """, (
        new_name, new_phone, new_username, new_password,
        old_username, old_password
    ))

    connection.commit()
    cursor.close()
    connection.close()

    print(fr.GREEN + "[+] Account updated successfully!" + st.RESET_ALL)
    return "logout"

def sellers():
    connection, cursor = conn()

    query = """
        SELECT seller_id, seller_name, phone_num
        FROM sellers
        WHERE is_deleted = FALSE
        ORDER BY seller_id
    """
    cursor.execute(query)
    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    if not rows:
        print(fr.YELLOW + "[-] Data sellers not found." + st.RESET_ALL)
        return "back"

    data = [list(row) for row in rows]
    headers = ["Seller ID", "Name", "Phone Number"]

    print(tb(data, headers=headers, tablefmt="fancy_grid"))

    while True:
        seller_id = qu.text("Enter Seller ID to view products:").ask()

        try:
            seller_id = int(seller_id)
            return seller_id
        except:
            print(fr.RED + "[!] Seller ID must be a number!" + st.RESET_ALL)

def products(seller_id):
    connection, cursor = conn()

    query = """
        SELECT p.product_id, p.product_name, p.product_stock, p.price, pc.category_name 
        FROM products p 
        JOIN product_categories pc ON p.category_id = pc.category_id
        JOIN sellers s ON p.seller_id = s.seller_id
        WHERE p.is_deleted = FALSE AND s.seller_id = %s
        ORDER BY p.product_id
    """
    cursor.execute(query, (seller_id,))
    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    if not rows:
        print(fr.YELLOW + "[-] no products in this seller." + st.RESET_ALL)
        return "back"

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

    # Create Payment
    cursor.execute("""
        INSERT INTO payments (payment_status, method_id)
        VALUES ('N', 1)
        RETURNING payment_id
    """)
    payment_id = cursor.fetchone()[0]

    # Create Delivery (default pending)
    cursor.execute("""
        INSERT INTO deliveries (delivery_date, delivery_status_id, courier_id)
        VALUES (%s, 1, 1)
        RETURNING delivery_id
    """, (datetime.now(),))
    delivery_id = cursor.fetchone()[0]

    # Create Order
    cursor.execute("""
        INSERT INTO orders (order_date, order_status_id, payment_id, customer_id, delivery_id, is_deleted)
        VALUES (%s, 1, %s, %s, %s, false)
        RETURNING order_id
    """, (datetime.now(), payment_id, customer_id, delivery_id))
    order_id = cursor.fetchone()[0]

    # Insert Order Items (NO STOCK DEDUCTION HERE)
    for pid, qty, price in order_items:

        discount = 10 if qty % 5 == 0 else 0

        cursor.execute("""
            INSERT INTO order_details (quantity, discount, price, product_id, order_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (qty, discount, price, pid, order_id))

    connection.commit()
    cursor.close()
    connection.close()

    return fr.GREEN + f"[+] Order #{order_id} created successfully!" + st.RESET_ALL

def cancel_order(username, password):
    connection, cursor = conn()

    cursor.execute("""
        SELECT customer_id, customer_name
        FROM customers
        WHERE username = %s AND password = %s
    """, (username, password))
    
    customer = cursor.fetchone()

    if not customer:
        print(fr.RED + "[!] Invalid customer credentials." + st.RESET_ALL)
        return

    customer_id, customer_name = customer

    print(f"\n{fr.CYAN}Hello {customer_name}! These are your cancellable orders:{st.RESET_ALL}\n")

    cursor.execute("""
        SELECT o.order_id
        FROM orders o
        WHERE o.customer_id = %s
        AND o.is_deleted = false
        AND o.order_status_id = 1
    """, (customer_id,))

    pending_orders = [row[0] for row in cursor.fetchall()]

    if not pending_orders:
        print(fr.YELLOW + "[!] You have no pending orders to cancel." + st.RESET_ALL)
        return

    cursor.execute("""
        SELECT 
            o.order_id, 
            o.order_date, 
            s.order_status,
            p.payment_status
        FROM orders o
        JOIN order_status s ON o.order_status_id = s.order_status_id
        JOIN payments p ON o.payment_id = p.payment_id
        WHERE o.order_id = ANY(%s)
        ORDER BY o.order_id
    """, (pending_orders,))

    rows = cursor.fetchall()

    data = [list(row) for row in rows]
    headers = ["Order ID", "Order Date", "Status", "Payment"]
    print(tb(data, headers=headers, tablefmt="fancy_grid"))

    order_id = qu.text("\nEnter the Order ID you want to cancel: ").ask()

    try:
        order_id = int(order_id)
    except:
        print(fr.RED + "[!] Order ID must be a number." + st.RESET_ALL)
        return

    if order_id not in pending_orders:
        print(fr.RED + "[!] Invalid Order ID! Choose one from the table above." + st.RESET_ALL)
        return

    cursor.execute("""
        UPDATE orders
        SET order_status_id = 4
        WHERE order_id = %s
    """, (order_id,))

    connection.commit()

    print(fr.GREEN + f"[+] Order #{order_id} successfully cancelled!" + st.RESET_ALL)

    cursor.close()
    connection.close()

def payment(username, password):
    connection, cursor = conn()

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

    cursor.execute("""
        SELECT 
            o.order_id,
            o.order_date,
            pd.product_name,
            p.payment_status,
            (od.quantity * od.price) - ((od.quantity * od.price) * od.discount/100) AS total_price
        FROM orders o
        JOIN payments p ON o.payment_id = p.payment_id
        JOIN order_details od ON o.order_id = od.order_id
		JOIN products pd ON pd.product_id = od.product_id
        WHERE o.customer_id = %s 
            AND o.is_deleted = FALSE
            AND p.payment_status = 'N'
        ORDER BY o.order_id ASC
    """, (customer_id,))

    unpaid_orders = cursor.fetchall()

    if unpaid_orders:
        print("\n" + fr.CYAN + "Orders that need payment:" + st.RESET_ALL)

        headers = ["Order ID", "Order Date", "Product", "Payment Status", "Total Price"]
        print(tb(unpaid_orders, headers=headers, tablefmt="fancy_grid"))

    else:
        print(fr.YELLOW + "\n[!] You have no unpaid orders." + st.RESET_ALL)
        return False

    order_id = qu.text("\nEnter Order ID to process payment: ").ask()

    if not order_id.strip():
        print(fr.YELLOW + "[!] Cancelled.\n" + st.RESET_ALL)
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


    if payment_status == "Y":
        print(fr.GREEN + "[!] This order is already paid." + st.RESET_ALL)
        return True

    method = qu.select(
        "Select payment method:",
        choices=["Transfer", "COD", "Cancel"]
    ).ask()

    if method == "Cancel":
        print(fr.YELLOW + "\n[!] Payment cancelled." + st.RESET_ALL)
        return False

    if method == "Transfer":
        cursor.execute("""
            UPDATE payments
            SET payment_status = 'Y', method_id = 2
            WHERE payment_id = %s
        """, (payment_id,))
        
        connection.commit()
        print(fr.GREEN + "\n[+] Payment completed via Transfer!" + st.RESET_ALL)
        return True

    if method == "COD":
        cod_status = qu.select(
            "COD Status:",
            choices=["Received", "Back"]
        ).ask()

        if cod_status == "Received":
            cursor.execute("""
                UPDATE payments
                SET payment_status = 'Y'
                WHERE payment_id = %s
            """, (payment_id,))
            connection.commit()
            print(fr.GREEN + "\n[+] COD Payment marked as Received!" + st.RESET_ALL)
            return True

        if cod_status == "Back":
            cursor.execute("""
                UPDATE payments
                SET payment_status = 'N'
                WHERE payment_id = %s
            """, (payment_id,))
            connection.commit()
            print(fr.YELLOW + "\n[!] COD returned. Payment remains unpaid." + st.RESET_ALL)
            return False
    return False
