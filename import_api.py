import requests
import mysql.connector
import pandas as pd
import time
from datetime import datetime, timedelta

# Configuración de la base de datos
DB_CONFIG = {
    "host": "localhost",
    "user": "adminambientwet",
    "password": "admin",
    "database": "ambientweather"
}

# Configuración de la API
API_KEY = "f48c0472e7264b0da49e4a133e297989cc2122ea46fb47df8cd87572c0d0a16a"
APP_KEY = "4ddfff7a5eab48a1ad792148df5aebfc5ef1b32954fc4a9a8dba87119959b1e3"
BASE_URL = "https://rt.ambientweather.net/v1/devices/{}?apiKey={}&applicationKey={}&endDate={}&limit=288"

#Conexion a la base de datos
def conectar_db():
    return mysql.connector.connect(**DB_CONFIG)

#obtencion de las direcciones mac del archivo txt
def obtener_macaddress():
    with open("mac_address.txt", "r") as file:
        return [line.strip() for line in file.readlines() if line.strip()]

#Consulta a la base de datos para obtener el id de la estacion segun su dirección mac
def obtener_id_station(macaddress):
    conn = conectar_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_station FROM station WHERE macaddress = %s", (macaddress,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result["id_station"] if result else None

#Funcion para crear la tabla si no existe segun el registro 
def crear_tabla_si_no_existe(anio, mes):
    tabla = f"datos_{mes:02d}_{anio}"
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {tabla} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            id_station INT,
            date DATETIME,
            dateutc BIGINT UNSIGNED UNIQUE,
            tempf DECIMAL(5,2),
            humidity TINYINT UNSIGNED,
            windspeedmph DECIMAL(4,2),
            windgustmph DECIMAL(4,2),
            maxdailygust DECIMAL(4,2),
            winddir SMALLINT UNSIGNED,
            winddir_avg10m SMALLINT UNSIGNED,
            hourlyrainin DECIMAL(4,2),
            eventrainin DECIMAL(4,2),
            dailyrainin DECIMAL(4,2),
            weeklyrainin DECIMAL(5,2),
            monthlyrainin DECIMAL(5,2),
            yearlyrainin DECIMAL(6,2),
            totalrainin DECIMAL(6,2),
            battout TINYINT,
            tempinf DECIMAL(5,2),
            humidityin TINYINT UNSIGNED,
            baromrelin DECIMAL(5,2),
            baromabsin DECIMAL(5,2),
            feelsLike DECIMAL(5,2),
            dewPoint DECIMAL(5,2),
            feelsLikein DECIMAL(5,2),
            dewPointin DECIMAL(5,2),
            lastRain DATETIME,
            FOREIGN KEY (id_station) REFERENCES station(id_station)
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()
    return tabla

#Funcion para hacer una consulta en la base de datos y verificar si existe en la tabla corres
def obtener_dateutc_existentes(tabla, id_station):
    """ Obtiene los dateutc ya registrados en la base de datos para evitar duplicados. """
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute(f"SELECT dateutc FROM {tabla} WHERE id_station = %s", (id_station,))
    registros = {row[0] for row in cursor.fetchall()}
    cursor.close()
    conn.close()
    return registros

def insertar_datos(tabla, id_station, datos):
    conn = conectar_db()
    cursor = conn.cursor()
    
    # Obtener los registros ya existentes para evitar consultas repetitivas
    dateutc_existentes = obtener_dateutc_existentes(tabla, id_station)
    
    registros_a_insertar = []
    duplicados_consecutivos = 0

    for row in datos:
        dateutc = row.get("dateutc", -9999)
        
        if dateutc in dateutc_existentes:
            duplicados_consecutivos += 1
            if duplicados_consecutivos >= 2:  # Si hay 2 duplicados seguidos, pasamos a la siguiente estación
                print(f"Se encontraron 2 registros duplicados seguidos en {tabla}, pasando a la siguiente estación...")
                break
            continue  # No insertar duplicados
        
        # Si encontramos un registro nuevo, reiniciamos el contador de duplicados
        duplicados_consecutivos = 0

        registros_a_insertar.append((
            id_station,
            row.get("date", None),
            dateutc,
            row.get("tempf", -9999),
            row.get("humidity", -9999),
            row.get("windspeedmph", -9999),
            row.get("windgustmph", -9999),
            row.get("maxdailygust", -9999),
            row.get("winddir", -9999),
            row.get("winddir_avg10m", -9999),
            row.get("hourlyrainin", -9999),
            row.get("eventrainin", -9999),
            row.get("dailyrainin", -9999),
            row.get("weeklyrainin", -9999),
            row.get("monthlyrainin", -9999),
            row.get("yearlyrainin", -9999),
            row.get("totalrainin", -9999),
            row.get("battout", -9999),
            row.get("tempinf", -9999),
            row.get("humidityin", -9999),
            row.get("baromrelin", -9999),
            row.get("baromabsin", -9999),
            row.get("feelsLike", -9999),
            row.get("dewPoint", -9999),
            row.get("feelsLikein", -9999),
            row.get("dewPointin", -9999),
            row.get("lastRain", None)
        ))

    # Ejecutamos la inserción en batch si hay registros nuevos
    if registros_a_insertar:
        cursor.executemany(f'''
            INSERT IGNORE INTO {tabla} (id_station, date, dateutc, tempf, humidity, windspeedmph, windgustmph, maxdailygust, winddir,
                                        winddir_avg10m, hourlyrainin, eventrainin, dailyrainin, weeklyrainin, monthlyrainin, yearlyrainin,
                                        totalrainin, battout, tempinf, humidityin, baromrelin, baromabsin, feelsLike, dewPoint, feelsLikein, dewPointin, lastRain)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', registros_a_insertar)
        conn.commit()

    cursor.close()
    conn.close()

def main():
    macaddresses = obtener_macaddress()
    fecha_actual = datetime.utcnow()
    
    for macaddress in macaddresses:
        id_station = obtener_id_station(macaddress)
        if id_station is None:
            print(f"No se encontró id_station para {macaddress}")
            continue
        
        fecha = fecha_actual
        
        while True:
            fecha_str = fecha.strftime("%Y-%m-%dT23:59:59Z")
            url = BASE_URL.format(macaddress, API_KEY, APP_KEY, fecha_str)
            response = requests.get(url)
            
            if response.status_code == 200 and response.json():
                datos = response.json()
                tabla = crear_tabla_si_no_existe(fecha.year, fecha.month)
                insertar_datos(tabla, id_station, datos)
            else:
                break
            
            fecha -= timedelta(days=1)
            time.sleep(1)

main()
