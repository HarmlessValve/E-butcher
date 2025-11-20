import pyfiglet as pf
import questionary as qu
from colorama import Fore as fr, Style as st

def dashboard():
    msg = pf.figlet_format("Seller Dashboard", font="slant")
    print(fr.GREEN + st.BRIGHT + msg + st.RESET_ALL)
    return qu.select("dashboard menus", choices=["Account", "Product", "Order", "Recap", "Exit"]).ask()