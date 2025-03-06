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

# Conectar a la base de datos
def conectar_db():
    return mysql.connector.connect(**DB_CONFIG)

# Obtener las macaddress desde el archivo txt
def obtener_macaddress():
    with open("mac_address.txt", "r") as file:
        macs = [line.strip() for line in file.readlines() if line.strip()]
    return macs

# Obtener id_station según macaddress
def obtener_id_station(macaddress):
    conn = conectar_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_station FROM station WHERE macaddress = %s", (macaddress,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result["id_station"] if result else None

# Crear tabla si no existe
def crear_tabla_si_no_existe(anio, mes):
    tabla = f"datos_{mes:02d}_{anio}"
    conn = conectar_db()
    cursor = conn.cursor()
    query = f'''
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
    )'''
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()
    return tabla

def registro_existe(tabla, id_station, dateutc):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute(f"SELECT 1 FROM {tabla} WHERE id_station = %s AND dateutc = %s LIMIT 1", (id_station, dateutc))
    existe = cursor.fetchone() is not None
    cursor.close()
    conn.close()
    return existe

# Insertar datos evitando duplicados
def insertar_datos(tabla, id_station, datos):
    conn = conectar_db()
    cursor = conn.cursor()
    query = f'''
    INSERT IGNORE INTO {tabla} (id_station, date, dateutc, tempf, humidity, windspeedmph, windgustmph, maxdailygust, winddir,
                                winddir_avg10m, hourlyrainin, eventrainin, dailyrainin, weeklyrainin, monthlyrainin, yearlyrainin,
                                totalrainin, battout, tempinf, humidityin, baromrelin, baromabsin, feelsLike, dewPoint, feelsLikein, dewPointin, lastRain)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    
    duplicados_consecutivos = 0  # Contador de registros duplicados seguidos
    
    for row in datos:
        if registro_existe(tabla, id_station, row.get("dateutc", -9999)):
            duplicados_consecutivos += 1
            if duplicados_consecutivos >= 2:  # Si se encuentran 2 duplicados seguidos, se pasa a la siguiente estación
                print(f"Se encontraron 2 registros duplicados seguidos en {tabla}, pasando a la siguiente estación...")
                return True
            continue  # Omitir la inserción si el registro ya existe

        # Reiniciar el contador si encontramos un registro nuevo
        duplicados_consecutivos = 0
        
        values = (
            id_station,
            row.get("date", None),
            row.get("dateutc", -9999),
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
        )
        cursor.execute(query, values)

    conn.commit()
    cursor.close()
    conn.close()
    return False

# Descargar datos históricos
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
            print(f"Obteniendo datos de {macaddress}")
            url = BASE_URL.format(macaddress, API_KEY, APP_KEY, fecha_str)
            response = requests.get(url)
            
            if response.status_code == 200:
                datos = response.json()
                if not datos:
                    print(f"No hay mas registros para {macaddress} pasando a la siguiente dirección")
                    break  # No hay más registros
                
                anio, mes = fecha.year, fecha.month
                tabla = crear_tabla_si_no_existe(anio, mes)
                
                existe = insertar_datos(tabla, id_station, datos)
                
                if existe:
                    break
            else:
                print(f"Error obteniendo datos para {macaddress} en {fecha_str}")
            
            fecha -= timedelta(days=1)  # Ir un día hacia atrás
            time.sleep(1)  # Pausa para evitar sobrecargar la API

main()