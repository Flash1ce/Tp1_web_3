import mysql.connector
from mysql.connector import Error

# Connection a la bd sur Wamp, C'EST PAS LA BD QUI EST HÉBERGER!
def ouvrir_connexion() :
    try:
        conn = mysql.connector.connect(
            user="root",
            password="",
            host="127.0.0.1",
            database="tp1appweb")
        return conn
    except Error as e:
        print(f"Erreur de connexion à mysql: {e}")