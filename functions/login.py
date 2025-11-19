from functions.connection import conn

def seller_login(username, password):
    try:
        connection, cursor = conn()

        query = """
            SELECT username 
            FROM sellers 
            WHERE username = %s AND password = %s
        """
        cursor.execute(query, (username, password))
        result = cursor.fetchone()

        cursor.close()
        connection.close()

        return result is not None

    except Exception as e:
        print("Error:", e)
        return False


def customer_login(username, password):
    try:
        connection, cursor = conn()

        query = """
            SELECT username 
            FROM customers 
            WHERE username = %s AND password = %s
        """
        cursor.execute(query, (username, password))
        result = cursor.fetchone()

        cursor.close()
        connection.close()

        return result is not None

    except Exception as e:
        print("Error:", e)
        return False


def courier_login(username, password):
    try:
        connection, cursor = conn()

        query = """
            SELECT username 
            FROM couriers 
            WHERE username = %s AND password = %s
        """
        cursor.execute(query, (username, password))
        result = cursor.fetchone()

        cursor.close()
        connection.close()

        return result is not None

    except Exception as e:
        print("Error:", e)
        return False
