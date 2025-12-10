import pyfiglet as pf
import questionary as qu
from tabulate import tabulate as tb
from colorama import Fore as fr, Style as st
from functions.connection import conn

def dashboard(username, password):
    msg = pf.figlet_format("Courier Dashboard", font="slant")
    print(fr.BLUE + st.BRIGHT + msg + st.RESET_ALL)

    while True:
        option = qu.select("dashboard menus", choices=["Account", "Orders", "Delivery", "Exit"]).ask()

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
                Order = take_order(username, password)
                print(Order)
                
        elif option == "Delivery":
            Delivery = delivery(username, password)
            print(Delivery)
        elif option == "Exit":
            print("[!] Exiting dashboard...")
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

def validate_input(*fields):
    return all(field and field.strip() != "" for field in fields)

def validate_phone(phone):
    return phone.isdigit() and len(phone) == 12


def edit_account(username, password):
    connection, cursor = conn()

    query = """
        SELECT c.courier_name, c.phone_num, c.username, c.password
        FROM couriers c
        WHERE c.username = %s AND c.password = %s AND c.is_deleted = FALSE
    """
    cursor.execute(query, (username, password))
    data = cursor.fetchone()

    if not data:
        print(fr.RED + "[-] Data not found." + st.RESET_ALL)
        return

    courier_name, phone_num, old_username, old_password = data

    delete_choice = qu.select(
        "Do you want to delete your account?",
        choices=["No", "Yes"]
    ).ask()

    if delete_choice == "Yes":
        cursor.execute("""
            UPDATE couriers
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

    new_name = qu.text(f"Courier Name ({courier_name}): ").ask() or courier_name
    new_phone = qu.text(f"Phone Number ({phone_num}): ").ask() or phone_num
    new_username = qu.text(f"Username ({old_username}): ").ask() or old_username
    new_password = qu.password(f"Password ({old_password}): ").ask() or old_password

    if not validate_input(new_name, new_phone, new_username, new_password):
        print(fr.RED + "[-] All fields must be filled!\n" + st.RESET_ALL)
        return

    if not validate_phone(new_phone):
        print(fr.RED + "[-] Phone number must be 12 digits!\n" + st.RESET_ALL)
        return

    cursor.execute("""
        UPDATE couriers
        SET courier_name = %s,
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

def take_order(username, password):
    connection, cursor = conn()

    cursor.execute("""
        SELECT courier_id 
        FROM couriers
        WHERE username = %s AND password = %s AND is_deleted = FALSE
    """, (username, password))
    courier = cursor.fetchone()
    if not courier:
        print(fr.RED + "[-] Courier not found." + st.RESET_ALL)
        return
    courier_id = courier[0]

    cursor.execute("SELECT delivery_status_id FROM delivery_status WHERE delivery_status = 'Ready'")
    ready_id = cursor.fetchone()[0]

    cursor.execute("SELECT delivery_status_id FROM delivery_status WHERE delivery_status = 'Sending'")
    sending_id = cursor.fetchone()[0]

    cursor.execute("""
        SELECT o.order_id, o.order_date, c.customer_name, a.street_name, ds.district_name
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        JOIN deliveries d ON o.delivery_id = d.delivery_id
		JOIN addresses a ON a.address_id = c.address_id
		JOIN districts ds ON ds.district_id = a.district_id
        WHERE d.delivery_status_id = %s AND o.is_deleted = FALSE
        ORDER BY o.order_id
    """, (ready_id,))
    rows = cursor.fetchall()

    if not rows:
        print(fr.YELLOW + "[-] No orders available to take." + st.RESET_ALL)
        return

    print(tb(rows, headers=["Order ID", "Date", "Customer", "Street", "District"], tablefmt="fancy_grid"))

    while True:
        order_input = qu.text("Enter Order ID to take (enter = cancel): ").ask()
        if not order_input.strip():
            print(fr.YELLOW + "[*] Cancelled." + st.RESET_ALL)
            return

        if not order_input.isdigit():
            print(fr.RED + "[!] Must be number!" + st.RESET_ALL)
            continue

        order_id = int(order_input)

        cursor.execute("""
            SELECT d.delivery_id
            FROM orders o
            JOIN deliveries d ON o.delivery_id = d.delivery_id
            WHERE o.order_id = %s AND d.delivery_status_id = %s
        """, (order_id, ready_id))

        result = cursor.fetchone()

        if not result:
            print(fr.RED + "[-] Order not found or not Ready!" + st.RESET_ALL)
            continue

        delivery_id = result[0]

        cursor.execute("""
            UPDATE deliveries
            SET delivery_status_id = %s,
                courier_id = %s
            WHERE delivery_id = %s
        """, (sending_id, courier_id, delivery_id))

        connection.commit()
        print(fr.GREEN + f"[+] Order {order_id} marked as Sending." + st.RESET_ALL)

        more = qu.select("Take another?", ["Yes", "No"]).ask()
        if more == "No":
            break

    cursor.close()
    connection.close()

def delivery(username, password):
    connection, cursor = conn()

    cursor.execute("""
        SELECT courier_id
        FROM couriers
        WHERE username = %s AND password = %s AND is_deleted = FALSE
    """, (username, password))

    data = cursor.fetchone()
    if not data:
        print(fr.RED + "[-] Courier not found or account deleted." + st.RESET_ALL)
        cursor.close()
        connection.close()
        return

    courier_id = data[0]

    cursor.execute("SELECT delivery_status_id FROM delivery_status WHERE delivery_status = 'Sending'")
    sending_id = cursor.fetchone()[0]

    cursor.execute("SELECT delivery_status_id FROM delivery_status WHERE delivery_status = 'Received'")
    received_id = cursor.fetchone()[0]

    cursor.execute("""
        SELECT 
            d.delivery_id,
            d.delivery_date,

            c.customer_name,
            ca.street_name AS customer_street,
            cd.district_name AS customer_district,

            s.seller_name,
            sa.street_name AS seller_street,
            sd.district_name AS seller_district,

            ds.delivery_status, py.payment_status , pm.method_name,
            (p.price * od.quantity) - ((p.price * od.quantity) * od.discount / 100) AS total_price

        FROM deliveries d
        JOIN orders o ON o.delivery_id = d.delivery_id
		JOIN payments py ON o.payment_id = py.payment_id
		JOIN payment_methods pm ON pm.method_id = py.method_id
        JOIN customers c ON c.customer_id = o.customer_id
        JOIN addresses ca ON ca.address_id = c.address_id
        JOIN districts cd ON cd.district_id = ca.district_id
        JOIN order_details od ON od.order_id = o.order_id
        JOIN products p ON p.product_id = od.product_id
        JOIN sellers s ON s.seller_id = p.seller_id
        JOIN addresses sa ON sa.address_id = s.address_id
        JOIN districts sd ON sd.district_id = sa.district_id
        JOIN delivery_status ds ON ds.delivery_status_id = d.delivery_status_id
        WHERE d.courier_id = %s AND d.delivery_status_id = %s AND o.is_deleted = FALSE
        GROUP BY d.delivery_id, d.delivery_date, c.customer_name, ca.street_name, cd.district_name,
        s.seller_name, sa.street_name, sd.district_name, ds.delivery_status, pm.method_name, py.payment_status, total_price
        ORDER BY d.delivery_id
    """, (courier_id, sending_id))

    rows = cursor.fetchall()

    if not rows:
        print(fr.YELLOW + "[-] No deliveries to mark as Received." + st.RESET_ALL)
        cursor.close()
        connection.close()
        return

    headers = [
        "Delivery ID",
        "Date",
        "Customer",
        "Customer Street",
        "Customer District",
        "Seller",
        "Seller Street",
        "Seller District",
        "Delivery Status",
        "Payment Status",
        "Payment Method",
        "Total Price"
    ]

    print(tb(rows, headers=headers, tablefmt="fancy_grid"))

    while True:
        delivery_input = qu.text("Enter Delivery ID to mark as Received (Enter to cancel):").ask()

        if delivery_input.strip() == "":
            print(fr.YELLOW + "[*] Action cancelled." + st.RESET_ALL)
            cursor.close()
            connection.close()
            return

        if not delivery_input.isdigit():
            print(fr.RED + "[!] Delivery ID must be a number!" + st.RESET_ALL)
            continue

        delivery_id = int(delivery_input)

        cursor.execute("""
            SELECT delivery_id
            FROM deliveries
            WHERE delivery_id = %s AND courier_id = %s AND delivery_status_id = %s
        """, (delivery_id, courier_id, sending_id))

        check = cursor.fetchone()

        if not check:
            print(fr.RED + "[-] Delivery not found or not in Sending status!" + st.RESET_ALL)
            continue

        cursor.execute("""
            UPDATE deliveries
            SET delivery_status_id = %s
            WHERE delivery_id = %s
        """, (received_id, delivery_id))

        connection.commit()

        print(fr.GREEN + f"[+] Delivery {delivery_id} successfully marked as Received." + st.RESET_ALL)

        more = qu.select("Mark another delivery?", choices=["Yes", "No"]).ask()
        if more == "No":
            break

    cursor.close()
    connection.close()
    return
