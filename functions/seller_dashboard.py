import pyfiglet as pf
import questionary as qu
from colorama import Fore as fr, Style as st
from functions.connection import conn

def dashboard(username, password):
    msg = pf.figlet_format("Seller Dashboard", font="slant")
    print(fr.GREEN + st.BRIGHT + msg + st.RESET_ALL)
    option = qu.select("dashboard menus", choices=["Account", "Product", "Order", "Recap", "Exit"]).ask()

    if option == "Account":
        try:
            connection, cursor = conn()
            query = """
            SELECT s.seller_name, s.phone_num, s.username, s.password, a.street_name, d.district_name 
            FROM sellers s JOIN addresses a 
            on s.address_id = a.address_id 
            JOIN districts d
            on a.district_id = d.district_id
            WHERE username = %s and password = %s"""
            cursor.execute(query, (username, password))
            result = cursor.fetchone()
            print(result)
            
            cursor.close()
            connection.close()
                
            return result
        except Exception as e:
            
            print("Error:", e)
            return False