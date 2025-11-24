import psycopg2 as pg
from colorama import Fore as fr, Style as st
from functions.conf import DB

def conn():
    try:
        connection = pg.connect(**DB)
        cursor = connection.cursor()
        return connection, cursor

    except Exception as e:
        print(fr.RED + st.BRIGHT + "[-] Failed to connect to the database." + st.RESET_ALL)
        print(fr.YELLOW + st.BRIGHT + f"[!] Error details: {e}" + st.RESET_ALL)
        exit(1)
