import pymysql
import requests
import pandas as pd
from datetime import datetime

# Conexión a la base de datos
conexion = pymysql.connect(
    host='localhost',     
    user='adminambientwet',          
    password='admin',  
    database='ambientweather'
)
cursor = conexion.cursor()

# Función para obtener la dirección MAC según el nombre del archivo CSV
def obtener_id(nombre_csv):
    sql = "SELECT id_station FROM station WHERE macaddress = %s"
    cursor.execute(sql, (nombre_csv,))
    resultado = cursor.fetchone()
    return resultado[0] if resultado else None

# Función para crear una tabla dinámica
def crear_tabla_mes_anio(mes, anio):
    nombre_tabla = f"datos_{mes}_{anio}"
    sql = f"""
    CREATE TABLE IF NOT EXISTS `{nombre_tabla}` (
        id INT AUTO_INCREMENT PRIMARY KEY,
        id_station INT,
        date DATETIME,
        datesimple DATETIME,
        outdoor_temp FLOAT,
        feels_like FLOAT,
        dew_point FLOAT,
        wind_speed FLOAT,
        wind_gust FLOAT,
        max_daily_gust FLOAT,
        wind_direction FLOAT,
        rain_rate FLOAT,
        event_rain FLOAT,
        daily_rain FLOAT,
        weekly_rain FLOAT,
        monthly_rain FLOAT,
        yearly_rain FLOAT,
        total_rain FLOAT,
        rel_pressure FLOAT,
        humidity INT,
        indoor_temp FLOAT,
        indoor_humidity INT,
        avg_wind_dir FLOAT,
        outdoor_battery FLOAT,
        abs_pressure FLOAT,
        indoor_feels_like FLOAT,
        indoor_dew_point FLOAT,
        UNIQUE(id_station, date),
        FOREIGN KEY (id_station) REFERENCES station(id_station) ON DELETE CASCADE ON UPDATE CASCADE
    );
    """
    cursor.execute(sql)
    return nombre_tabla

# Función para obtener datos de la API
def obtener_datos_api(mac_address, end_date):
    url = f"https://rt.ambientweather.net/v1/devices/{mac_address}"
    params = {
        "apiKey": "a5dd230a0dcc4fe38b7336b8e9cbef548c7a3a2505d747c1b5b8d115b4202ecf",
        "applicationKey": "f2a84982ccaa4901b4eaa4f92b441ae305088f37558b4d108ceeb270613791c1",
        "endDate": end_date,
        "limit": 288
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return pd.DataFrame(response.json()).fillna(-9999)
    return pd.DataFrame()

# Función para procesar e insertar los datos
def procesar_datos_api(mac_address):
    id_station = obtener_id(mac_address)
    if not id_station:
        print(f"No se encontró el ID de la estación para la MAC: {mac_address}")
        return
    
    end_date = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    df = obtener_datos_api(mac_address, end_date)
    
    if df.empty:
        print("No se encontraron datos en la API.")
        return
    
    for _, fila in df.iterrows():
        fecha = datetime.utcfromtimestamp(fila["dateutc"] / 1000)
        mes = fecha.strftime("%B").lower()
        anio = fecha.year

        # Crear tabla si no existe
        nombre_tabla = crear_tabla_mes_anio(mes, anio)
        
        valores = [
            id_station,
            fecha,
            fila["tempf"],
            fila["feelsLike"],
            fila["dewPoint"],
            fila["windspeedmph"],
            fila["windgustmph"],
            fila["maxdailygust"],
            fila["winddir"],
            fila["hourlyrainin"],
            fila["eventrainin"],
            fila["dailyrainin"],
            fila["weeklyrainin"],
            fila["monthlyrainin"],
            fila["yearlyrainin"],
            fila["totalrainin"],
            fila["baromrelin"],
            fila["humidity"],
            fila["tempinf"],
            fila["humidityin"],
            fila["winddir_avg10m"],
            fila["battout"],
            fila["baromabsin"],
            fila["feelsLike"],
            fila["dewPoint"]
        ]
        
        # Verificar si el registro ya existe
        sql_verificar = f"SELECT COUNT(*) FROM `{nombre_tabla}` WHERE id_station = %s AND date = %s"
        cursor.execute(sql_verificar, (id_station, fecha))
        existe = cursor.fetchone()[0]

        if existe == 0:
            # Insertar en la tabla correspondiente
            sql_insertar = f"""
            INSERT INTO `{nombre_tabla}` (
                id_station, date, outdoor_temp, feels_like, dew_point, wind_speed, 
                wind_gust, max_daily_gust, wind_direction, rain_rate, event_rain, 
                daily_rain, weekly_rain, monthly_rain, yearly_rain, total_rain, 
                rel_pressure, humidity, indoor_temp, indoor_humidity, avg_wind_dir, 
                outdoor_battery, abs_pressure, indoor_feels_like, indoor_dew_point
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            try:
                cursor.execute(sql_insertar, valores)
            except Exception as e:
                print(f"Error al insertar datos: {e}")
        else:
            print(f"Registro duplicado: {id_station}, {fecha}")
    
    conexion.commit()
    print("Datos importados correctamente.")

procesar_datos_api("54:32:04:42:2B:64")

cursor.close()
conexion.close()