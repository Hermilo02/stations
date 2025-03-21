import mysql.connector
from flask import Flask, request, jsonify
from flask_cors import CORS
from Connection_db import get_db_connection

app = Flask(__name__)
CORS(app)

@app.route('/estaciones', methods=['GET'])
def get_estaciones():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT id_station, nombre FROM station")
    estaciones = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(estaciones)

@app.route('/estacion/<int:id_station>/<int:mes>/<int:anio>', methods=['GET'])
def get_datos_estacion_mes(id_station, mes, anio):
    table_name = f"datos_{mes:02d}_{anio}"  # Formato datos_MM_YYYY

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        query = f"SELECT * FROM {table_name} WHERE id_station = %s"
        cursor.execute(query, (id_station,))
        datos = cursor.fetchall()
    except mysql.connector.Error as err:
        return jsonify({"error": f"Error en la consulta: {err}"}), 500
    finally:
        cursor.close()
        connection.close()

    if datos:
        return jsonify(datos)
    else:
        return jsonify({"error": "No se encontraron datos para esta estación en el mes y año especificados"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=8000)
