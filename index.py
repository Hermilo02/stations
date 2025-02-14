import requests
import csv
import os
import pandas as pd

#for month in range (12,0,-1):
for day in range (30,0,-1):
        mac_address = "CC:8D:A2:73:6D:04"
        end_date = f"2025-01-{day}T00:00:00Z"
        url = f"https://rt.ambientweather.net/v1/devices/{mac_address}"
        params = {
            "apiKey": "2b3bf76816104f14b5a26cdb5497b088b7de0421daa3434db01a74b8eb481f48",
            "applicationKey": "7f3e3552a51d44bab4c7f2c5e0e0c1e544fab8e60df6478bb43135761f1cbfbf",
            "endDate": end_date,  # Opcional
            "limit": 288  # Opcional
        }

        # Solicitud a la API
        response = requests.get(url, params=params)

        if response.status_code == 200:
            device_data = response.json()
            print("Datos obtenidos correctamente.")

            # Crear el nombre del archivo y la carpeta
            folder_name = f"{mac_address.replace(":", "_")}"
            os.makedirs(folder_name, exist_ok=True)  # Crear la carpeta si no existe
            csv_filename = f"{folder_name}/{mac_address.replace(':', '_')}_{end_date.split('T')[0]}.csv"

            # Verificar si hay datos disponibles
            if device_data:
                with open(csv_filename, mode='w', newline='', encoding='utf-8') as csv_file:
                    fieldnames = device_data[0].keys()  # Usar las claves del primer elemento como encabezados
                    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

                    writer.writeheader()  # Escribir encabezados
                    writer.writerows(device_data)  # Escribir filas de datos
                    
                print(f"Datos guardados en {csv_filename}.")
            else:
                print("No hay datos disponibles para guardar.")
        else:
            print("Error al obtener datos:", response.status_code, response.text)
            