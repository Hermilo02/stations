import requests
from datetime import datetime
import pytz
import pandas as pd

# Leer la dirección MAC desde un archivo TXT
def obtener_mac_desde_archivo(ruta_archivo):
    with open(ruta_archivo, "r") as file:
        return file.readline().strip()  # Tomar la primera línea y eliminar espacios en blanco

# Obtener la fecha actual en UTC con la hora fijada en 23:59:59
def obtener_fecha_utc():
    ahora_utc = datetime.now(pytz.utc)
    fecha_utc = ahora_utc.replace(hour=23, minute=59, second=59, microsecond=0)
    return fecha_utc.strftime("%Y-%m-%dT%H:%M:%S")   # Formato ISO 8601

# Configuración
ruta_archivo_mac = "mac_address.txt"  # Asegúrate de que el archivo contenga una dirección MAC válida
apikey = "a5dd230a0dcc4fe38b7336b8e9cbef548c7a3a2505d747c1b5b8d115b4202ecf" 
appkey = "f2a84982ccaa4901b4eaa4f92b441ae305088f37558b4d108ceeb270613791c1"  # ApplicationKey

# Obtener valores
mac_address = obtener_mac_desde_archivo(ruta_archivo_mac)
end_date = obtener_fecha_utc()

# URL de la API con la dirección MAC incluida
url = f"https://rt.ambientweather.net/v1/devices/{mac_address}?apiKey={apikey}&applicationKey={appkey}&endDate={end_date}&limit=288"

# Hacer la petición GET
response = requests.get(url)

# Verificar respuesta
if response.status_code == 200:
    data = response.json()
    df=pd.DataFrame(data)
    df.to_csv('datos.csv', index=False)
    print(f"Datos de MAC Address: {mac_address} obtenidos correctamente")
else:
    print(f"Error: {response.status_code}, {response.text}")
