from functions.connection import conn
import questionary as qu


def username_exists(table, username):
    try:
        connection, cursor = conn()

        query = f"SELECT username FROM {table} WHERE username = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()

        cursor.close()
        connection.close()

        return result is not None

    except Exception as e:
        print("Error:", e)
        return True

def choose_district():
    connection, cursor = conn()

    cursor.execute("SELECT district_id, district_name FROM districts ORDER BY district_id ASC")
    district_data = cursor.fetchall()

    cursor.close()
    connection.close()

    if not district_data:
        print("[-] No districts found.")
        return None

    district_names = [d[1] for d in district_data]

    chosen_name = qu.select(
        "Select District:",
        choices=district_names
    ).ask()

    district_id = next(d[0] for d in district_data if d[1] == chosen_name)
    return district_id

def register_seller(name, phone, username, password, street):
    try:
        district_id = choose_district()
        if district_id is None:
            return False

        connection, cursor = conn()

        query = """
            WITH a AS (
                INSERT INTO addresses (street_name, district_id)
                VALUES (%s, %s)
                RETURNING address_id
            )
            INSERT INTO sellers (seller_name, phone_num, username, password, address_id)
            VALUES (%s, %s, %s, %s, (SELECT address_id FROM a));
        """

        cursor.execute(query, (street, district_id, name, phone, username, password))
        connection.commit()
        
        cursor.close()
        connection.close()
        return True
    
    except Exception as e:
        print("Error:", e)
        return False

def register_customer(name, phone, username, password, street):
    try:
        district_id = choose_district()
        if district_id is None:
            return False

        connection, cursor = conn()

        query = """
            WITH a AS (
                INSERT INTO addresses (street_name, district_id)
                VALUES (%s, %s)
                RETURNING address_id
            )
            INSERT INTO customers (customer_name, phone_num, username, password, address_id)
            VALUES (%s, %s, %s, %s, (SELECT address_id FROM a));
        """

        cursor.execute(query, (street, district_id, name, phone, username, password))
        connection.commit()

        cursor.close()
        connection.close()

        return True

    except Exception as e:
        print("Error:", e)
        return False


def register_courier(name, phone, username, password):
    try:
        connection, cursor = conn()

        query = """
            INSERT INTO couriers (courier_name, phone_num, username, password)
            VALUES (%s, %s, %s, %s)
        """

        cursor.execute(query, (name, phone, username, password))
        connection.commit()

        cursor.close()
        connection.close()

        return True

    except Exception as e:
        print("Error:", e)
        return False
