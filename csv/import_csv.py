import pymysql
import pandas as pd
from datetime import datetime

# Conexión a la base de datos
conexion = pymysql.connect(
    host='172.31.216.156',     
    user='adminambientwet',          
    password='admin',  
    database='ambientweather'
)
cursor = conexion.cursor()

# Función para obtener la dirección MAC según el nombre del archivo CSV
def obtener_id(nombre_csv):
    sql = "SELECT id_station FROM station WHERE nombre = %s"
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
        UNIQUE(id_station, date), -- Evitar duplicados
        FOREIGN KEY (id_station) REFERENCES station(id_station) -- Relación con la tabla `station`
            ON DELETE CASCADE     -- Si se elimina un registro en `station`, se eliminarán los relacionados
            ON UPDATE CASCADE     -- Actualiza automáticamente los cambios en el id_station
    );
    """
    cursor.execute(sql)
    return nombre_tabla

# Función para procesar e insertar los datos
def procesar_datos_csv(nombre_csv):
    id_station = obtener_id(nombre_csv)
    if not id_station:
        print(f"No se encontró el ID de la estación para el archivo: {nombre_csv}")
        return

    archivo_csv = f"{nombre_csv}.csv"  # Nombre del archivo CSV
    datos = pd.read_csv(archivo_csv)

    # Reemplazar valores vacíos por ceros
    datos = datos.fillna(0)

    # Iterar sobre cada fila del CSV
    for _, fila in datos.iterrows():
        # Fecha y cálculo de mes y año
        fecha = datetime.fromisoformat(fila["Date"])
        mes = fecha.strftime("%B").lower()  # Ejemplo: 'enero'
        anio = fecha.year

        # Crear tabla si no existe
        nombre_tabla = crear_tabla_mes_anio(mes, anio)

        # Campos que podrían ser nulos
        valores = [
            id_station,
            fecha,
            fila["Outdoor Temperature (°C)"],
            fila["Feels Like (°C)"],
            fila["Dew Point (°C)"],
            fila["Wind Speed (km/hr)"],
            fila["Wind Gust (km/hr)"],
            fila["Max Daily Gust (km/hr)"],
            fila["Wind Direction (°)"],
            fila["Rain Rate (mm/hr)"],
            fila["Event Rain (mm)"],
            fila["Daily Rain (mm)"],
            fila["Weekly Rain (mm)"],
            fila["Monthly Rain (mm)"],
            fila["Yearly Rain (mm)"],
            fila["Total Rain (mm)"],
            fila["Relative Pressure (hPa)"],
            fila["Humidity (%)"],
            fila["Indoor Temperature (°C)"],
            fila["Indoor Humidity (%)"],
            fila["Avg Wind Direction (10 mins) (°)"],
            fila["Outdoor Battery"],
            fila["Absolute Pressure (hPa)"],
            fila["Indoor Feels Like (°C)"],
            fila["Indoor Dew Point (°C)"]
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

# Nombre del archivo CSV
nombre_csv = "ElvisCocho_TERE"  # Cambia según tu archivo
procesar_datos_csv(nombre_csv)

# Confirmar los cambios en la base de datos
conexion.commit()

# Cerrar la conexión
cursor.close()
conexion.close()

print(f"operacion finalizada de la estacion {nombre_csv}")

