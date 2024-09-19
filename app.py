from flask import Flask, request, jsonify
import http.client
import json
import re
import random
import string
import os

app = Flask(__name__)

TOKEN_ANDERCODE = "ANDERCODE"
mensajes_procesados = set()
estado_usuario = {}

@app.route('/')
def index():
    return ""

@app.route('/webhook', methods=['GET'])
def verificar_token():
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    if challenge and token == TOKEN_ANDERCODE:
        return challenge
    else:
        return jsonify({'error': 'Token Inválido'}), 401



@app.route('/get-mensajes', methods=['GET'])
def get_mensajesbyjson():
    # Definir el nombre del archivo JSON
    json_file = 'data.json'

    try:
        # Verificar si el archivo existe
        if os.path.exists(json_file):
            # Abrir el archivo JSON en modo lectura
            with open(json_file, 'r') as file:
                # Cargar y retornar los datos contenidos en el archivo
                json_data = json.load(file)
                return json_data
        else:
            # Si el archivo no existe, retornar un mensaje apropiado
            return {"error": "El archivo no existe."}

    except Exception as e:
        # Manejo de errores durante la lectura del archivo
        print("Error al leer el archivo JSON:", e)
        return {"error": "Error al leer el archivo JSON."}



@app.route('/eliminar-mensajes', methods=['POST'])
def eliminar_json_whatsapp_api():
    try:
        # Obtener el criterio de eliminación desde el cuerpo de la solicitud POST
        data = request.get_json()

        # Validar que el JSON contenga el campo 'id'
        if not data or 'id' not in data:
            return jsonify({'error': 'No se proporcionó un ID válido para eliminar'}), 400
        
        id_eliminar = data['id']
        print("ID a eliminar:", id_eliminar)

        # Definir el nombre del archivo JSON
        json_file = 'data.json'

        # Verificar si el archivo existe
        if os.path.exists(json_file):
            # Cargar los datos del archivo JSON
            with open(json_file, 'r') as file:
                try:
                    json_data = json.load(file)
                except json.JSONDecodeError:
                    return jsonify({'error': 'El archivo JSON está corrupto o mal formado'}), 500

            # Verificar que json_data es una lista
            if isinstance(json_data, list):
                # Filtrar los mensajes cuyo 'id' no coincida con id_eliminar
                nuevos_datos = [entry for entry in json_data if entry.get('entry', [{}])[0].get('id') != id_eliminar]

                # Guardar los datos actualizados en el archivo JSON solo si hubo cambios
                if len(nuevos_datos) < len(json_data):
                    with open(json_file, 'w') as file:
                        json.dump(nuevos_datos, file, indent=4)
                    return jsonify({'status': 'Mensaje eliminado correctamente'}), 200
                else:
                    return jsonify({'status': 'No se encontró un mensaje con ese ID'}), 404
            else:
                return jsonify({'error': 'El formato del archivo JSON es incorrecto, debe ser una lista de mensajes'}), 500
        else:
            return jsonify({'error': 'El archivo no existe'}), 404

    except Exception as e:
        # Manejo de errores durante la lectura o escritura del archivo
        print("Error al procesar la eliminación del mensaje:", e)
        return jsonify({'error': f'Error al procesar la eliminación: {str(e)}'}), 500


@app.route('/webhook', methods=['POST'])
def recibir_mensajes():
    try:
        # Obtener los datos del POST request
        data = request.get_json()
        print("Datos recibidos:", data)

        # Definir el nombre del archivo JSON
        json_file = 'data.json'

        # Si el archivo existe, lo cargamos, si no, creamos una lista vacía
        if os.path.exists(json_file):
            with open(json_file, 'r') as file:
                json_data = json.load(file)
                if not isinstance(json_data, list):  # Verificar si es un array
                    json_data = []
        else:
            json_data = []

        # Añadir los nuevos datos recibidos al array de objetos JSON
        json_data.append(data)

        # Guardar los datos actualizados en el archivo JSON
        with open(json_file, 'w') as file:
            json.dump(json_data, file, indent=4)

        # Retornar una respuesta exitosa
        return jsonify({'status': 'Datos recibidos correctamente'}), 200

    except Exception as e:
        print("Error en el procesamiento del mensaje:", e)
        return jsonify({'error': 'Error en el procesamiento del mensaje'}), 500





if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
