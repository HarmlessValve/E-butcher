from functions.connection import conn


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


def register_seller(name, phone, username, password):
    try:
        connection, cursor = conn()

        query = """
            INSERT INTO sellers (seller_name, phone_num, username, password)
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


def register_customer(name, phone, username, password):
    try:
        connection, cursor = conn()

        query = """
            INSERT INTO customers (customer_name, phone_num, username, password)
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
