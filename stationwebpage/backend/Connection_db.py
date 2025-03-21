import mysql.connector

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='adminambientwet',
            password='admin',
            database='ambientweather'
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error de conexión: {err}")
        return None
