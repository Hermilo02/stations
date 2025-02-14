import requests
import pymysql
from datetime import datetime, timedelta
import pytz

# Configuración de la base de datos
config_db = {
    'host': 'localhost',
    'user': 'adminambientwet',
    'password': 'admin',
    'database': 'ambientweather',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# Configuración de la API
api_key = "a5dd230a0dcc4fe38b7336b8e9cbef548c7a3a2505d747c1b5b8d115b4202ecf"
application_key = "f2a84982ccaa4901b4eaa4f92b441ae305088f37558b4d108ceeb270613791c1"

# Leer las direcciones MAC desde el archivo txt
def leer_mac_addresses():
    with open("mac_address.txt", "r") as archivo:
        mac_addresses = [linea.strip() for linea in archivo.readlines()]
    return mac_addresses

# Obtener el id_station a partir de la mac_address
def obtener_id_station(mac_address):
    conexion = pymysql.connect(**config_db)
    try:
        with conexion.cursor() as cursor:
            cursor.execute("SELECT id_station FROM station WHERE macaddress = %s", (mac_address,))
            resultado = cursor.fetchone()
            if resultado:
                return resultado['id_station']
            else:
                print(f"No se encontró id_station para la macaddress: {mac_address}")
                return None
    finally:
        conexion.close()

# Función para crear una tabla si no existe
def crear_tabla_mes_anio(mes, anio):
    nombre_tabla = f"datos_{mes}_{anio}"
    conexion = pymysql.connect(**config_db)
    try:
        with conexion.cursor() as cursor:
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {nombre_tabla} (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    id_station INT,
                    fecha DATETIME,
                    tempf FLOAT,
                    feelsLike FLOAT,
                    dewPoint FLOAT,
                    windspeedmph FLOAT,
                    windgustmph FLOAT,
                    maxdailygust FLOAT,
                    winddir FLOAT,
                    hourlyrainin FLOAT,
                    eventrainin FLOAT,
                    dailyrainin FLOAT,
                    weeklyrainin FLOAT,
                    monthlyrainin FLOAT,
                    yearlyrainin FLOAT,
                    totalrainin FLOAT,
                    baromrelin FLOAT,
                    humidity FLOAT,
                    tempinf FLOAT,
                    humidityin FLOAT,
                    winddir_avg10m FLOAT,
                    battout FLOAT,
                    baromabsin FLOAT,
                    FOREIGN KEY (id_station) REFERENCES station(id_station)
                )
            """)
        conexion.commit()
    except pymysql.err.OperationalError as e:
        print(f"Error al crear la tabla {nombre_tabla}: {e}")
    finally:
        conexion.close()
    return nombre_tabla

# Función para obtener datos de la API
def obtener_datos_api(mac_address, end_date):
    url = f"https://rt.ambientweather.net/v1/devices/{mac_address}"
    params = {
        "apiKey": api_key,
        "applicationKey": application_key,
        "endDate": end_date,
        "limit": 288
    }
    respuesta = requests.get(url, params=params)
    if respuesta.status_code == 200:
        return respuesta.json()
    else:
        print(f"Error al obtener datos para {mac_address} en {end_date}: {respuesta.status_code}")
        return None

# Función para insertar datos en la base de datos
def insertar_datos_en_db(nombre_tabla, datos):
    conexion = pymysql.connect(**config_db)
    try:
        with conexion.cursor() as cursor:
            query = f"""
                INSERT INTO {nombre_tabla} (
                    id_station, fecha, tempf, feelsLike, dewPoint, windspeedmph, windgustmph,
                    maxdailygust, winddir, hourlyrainin, eventrainin, dailyrainin, weeklyrainin,
                    monthlyrainin, yearlyrainin, totalrainin, baromrelin, humidity, tempinf,
                    humidityin, winddir_avg10m, battout, baromabsin
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.executemany(query, datos)
        conexion.commit()
    finally:
        conexion.close()

# Función principal para obtener datos históricos
def obtener_datos_historicos():
    mac_addresses = leer_mac_addresses()  # Leer las direcciones MAC desde el archivo
    fecha_actual = datetime.now(pytz.utc)  # Usamos UTC para coincidir con la API

    while True:
        for mac_address in mac_addresses:
            # Obtener el id_station correspondiente a la mac_address
            id_station = obtener_id_station(mac_address)
            if id_station is None:
                print(f"No se encontró id_station para {mac_address}. Saltando esta dirección MAC.")
                continue

            datos_del_dia = obtener_datos_api(mac_address, fecha_actual)
            if datos_del_dia is None or len(datos_del_dia) == 0:
                print(f"No hay más datos para {mac_address} en {fecha_actual}")
                continue

            # Procesar y almacenar los datos
            datos_para_db = []
            for fila in datos_del_dia:
                try:
                    # Verificar si dateutc es un timestamp (entero)
                    if isinstance(fila["dateutc"], int):
                        # Convertir el timestamp a datetime (asumiendo que está en milisegundos)
                        fecha = datetime.fromtimestamp(fila["dateutc"] / 1000, tz=pytz.utc)
                    else:
                        # Si no es un entero, asumir que es una cadena y usar strptime
                        fecha = datetime.strptime(fila["dateutc"], "%Y-%m-%dT%H:%M:%S.%fZ")
                    
                    # Definir los valores a insertar
                    valores = (
                        id_station,  # Usar el id_station obtenido
                        fecha,
                        fila.get("tempf", -9999),
                        fila.get("feelsLike", -9999),
                        fila.get("dewPoint", -9999),
                        fila.get("windspeedmph", -9999),
                        fila.get("windgustmph", -9999),
                        fila.get("maxdailygust", -9999),
                        fila.get("winddir", -9999),
                        fila.get("hourlyrainin", -9999),
                        fila.get("eventrainin", -9999),
                        fila.get("dailyrainin", -9999),
                        fila.get("weeklyrainin", -9999),
                        fila.get("monthlyrainin", -9999),
                        fila.get("yearlyrainin", -9999),
                        fila.get("totalrainin", -9999),
                        fila.get("baromrelin", -9999),
                        fila.get("humidity", -9999),
                        fila.get("tempinf", -9999),
                        fila.get("humidityin", -9999),
                        fila.get("winddir_avg10m", -9999),
                        fila.get("battout", -9999),
                        fila.get("baromabsin", -9999)
                    )
                    datos_para_db.append(valores)
                except KeyError as e:
                    print(f"Error: Falta la clave {e} en los datos de la API.")
                except Exception as e:
                    print(f"Error al procesar la fila: {e}")

            # Crear la tabla si no existe
            mes = fecha.strftime("%B").lower()
            anio = fecha_actual.year
            nombre_tabla = crear_tabla_mes_anio(mes, anio)

            # Insertar los datos en la base de datos
            insertar_datos_en_db(nombre_tabla, datos_para_db)
            print(f"Datos insertados para {mac_address} en {fecha_actual}")

        # Retroceder un día
        fecha_actual -= timedelta(days=1)

# Ejecutar el script
if __name__ == "__main__":
    obtener_datos_historicos()