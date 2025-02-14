import requests
import pymysql
import pandas as pd

# Conexión a la base de datos
conexion = pymysql.connect(
    host='localhost',     
    user='adminambientwet',          
    password='admin',  
    database='ambientweather'
)

cursor = conexion.cursor()

# URL de la API
url = "https://rt.ambientweather.net/v1/devices?applicationKey=7f3e3552a51d44bab4c7f2c5e0e0c1e544fab8e60df6478bb43135761f1cbfbf&apiKey=2b3bf76816104f14b5a26cdb5497b088b7de0421daa3434db01a74b8eb481f48"

# Obtener datos de la API
response = requests.get(url)

if response.status_code == 200:
    estaciones = response.json()
    
    for estacion in estaciones:
        mac_address = estacion.get("macAddress")
        nombre = estacion.get("info", {}).get("name", "Desconocido")
        
        # Consulta SQL para insertar o actualizar la tabla
        sql = """
        INSERT INTO station (macaddress, nombre)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE macaddress = VALUES(macaddress)
        """
        
        try:
            cursor.execute(sql, (mac_address, nombre))
            print(f"Estación {nombre} con MAC {mac_address} actualizada/insertada.")
        except Exception as e:
            print(f"Error al insertar/actualizar la estación {nombre}: {e}")

    # Confirmar los cambios en la base de datos
    conexion.commit()
else:
    print(f"Error al obtener los datos de la API: {response.status_code}")
    
#consulta para obtener todas las direcciones mac
sqlmacaddress = "SELECT macaddress FROM station"
cursor.execute(sqlmacaddress)

#obtener todos los resultados 
mac_address = cursor.fetchall()

# Cerrar la conexión
cursor.close()
conexion.close()

#Crear data frame
df = pd.DataFrame(mac_address, columns=["macaddress"])

#Exportar el dataframe a un archivo txt
archivo_txt = "mac_address.txt"
df.to_csv(archivo_txt, index=False, header=False)