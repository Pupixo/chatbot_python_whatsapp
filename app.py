from flask import Flask, request, jsonify
import http.client
import json
import re
import random
import string
import os
from pathlib import Path
import logging


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



# @app.route('/get-mensajes', methods=['GET'])
# def get_mensajesbyjson():
#     # Obtener el parámetro 'number' de la solicitud GET
#     numero = request.args.get('number', default=None, type=int)

#     # Verificar si se ha proporcionado un número válido
#     if numero is None:
#         return jsonify({"error": "El parámetro 'number' es obligatorio."})

#     # Definir el nombre del archivo JSON basado en el número
#     json_file = f'usuario_{numero}.json'

#     try:
#         # Verificar si el archivo existe
#         if os.path.exists(json_file):
#             # Abrir el archivo JSON en modo lectura
#             with open(json_file, 'r') as file:
#                 # Cargar y retornar los datos contenidos en el archivo
#                 json_data = json.load(file)
#                 return jsonify(json_data)
#         else:
#             # Si el archivo no existe, retornar un mensaje apropiado
#             return jsonify({"error": "El archivo no existe."})

#     except Exception as e:
#         # Manejo de errores durante la lectura del archivo
#         print("Error al leer el archivo JSON:", e)
#         return jsonify({"error": "Error al leer el archivo JSON."})
    


@app.route('/get-mensajes/<number>', methods=['GET'])  # Utilizamos el número como parámetro en la URL
def get_mensajesbyjson(number):
    # Verificar si el número es válido
    print("number...............",number)
    if not number.isdigit():
        return jsonify({"error": "El parámetro 'number' debe ser un número válido."}), 400

    # Definir el nombre del archivo JSON basado en el número
    json_file = f'usuario_{number}.json'

    try:
        # Verificar si el archivo existe
        if os.path.exists(json_file):
            # Abrir el archivo JSON en modo lectura
            with open(json_file, 'r') as file:
                # Cargar y retornar los datos contenidos en el archivo
                json_data = json.load(file)
                return jsonify(json_data)
        else:
            # Si el archivo no existe, retornar un mensaje apropiado
            return jsonify({"error": "El archivo no existe."}), 404

    except Exception as e:
        # Manejo de errores durante la lectura del archivo
        print("Error al leer el archivo JSON:", e)
        return jsonify({"error": "Error al leer el archivo JSON."}), 500


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

        # Validar que el JSON contenga el campo 'id'
        if not data or 'numero' not in data:
            return jsonify({'error': 'No se proporcionó un numero de usuario válido para eliminar'}), 400
     
        numero = data['numero']
        print("numero a eliminar:", numero)  

        # Definir el nombre del archivo JSON
        json_file = f'usuario_{numero}.json'

        # Verificar si el archivo existe
        if os.path.exists(json_file):
            # Cargar los datos del archivo JSON
            with open(json_file, 'r') as file:
                try:
                    json_data = json.load(file)
                except json.JSONDecodeError:
                    return jsonify({'error': 'El archivo JSON está corrupto o mal formado'}), 500

            print("ID a json_data:", json_data)

            # Verificar que json_data es una lista
            if isinstance(json_data, list):
                print("isinstance")

                nuevos_datos = [
                                entry for entry in json_data 
                                if all(
                                    message.get('id') != id_eliminar
                                    for change in entry.get('entry', [{}])[0].get('changes', [{}])
                                    for message in change.get('value', {}).get('messages', [])
                                )
                            ]
            
                print("nuevos_datos",nuevos_datos)
                print("len  nuevos_datos",len(nuevos_datos))
                print("len  json_data",len(json_data))

                # Guardar los datos actualizados en el archivo JSON solo si hubo cambios
                if len(nuevos_datos) < len(json_data):
                    with open(json_file, 'w') as file:
                        json.dump(nuevos_datos, file, indent=4)
                    print("Mensaje eliminado correctamente")
                    return jsonify({'status': 'Mensaje eliminado correctamente'}), 200
                else:
                    print("No se encontró un mensaje con ese ID")
                    return jsonify({'status': 'No se encontró un mensaje con ese ID'}), 404
            else:
                print("no isinstance")
                return jsonify({'error': 'El formato del archivo JSON es incorrecto, debe ser una lista de mensajes'}), 500
        else:
            return jsonify({'error': 'El archivo no existe'}), 404

    except Exception as e:
        # Manejo de errores durante la lectura o escritura del archivo
        print("Error al procesar la eliminación del mensaje:", e)
        return jsonify({'error': f'Error al procesar la eliminación: {str(e)}'}), 500
    
# @app.route('/webhook', methods=['POST'])
# def recibir_mensajes():
#     try:
#         # Obtener los datos del POST request
#         data = request.get_json()
#         # Filtrar los datos recibidos usando la función filtrar_por_propiedad_text
#         messages = data['entry'][0]['changes'][0]['value'].get('messages')
#         print("messages......................",messages)
#         # Verificar si hay mensajes
#         json_data = []
#         if messages:               
#             numero = messages.get("from", "")
#             # Definir el nombre del archivo JSON
#             json_file = f'usuario_{numero}.json'
#             # Si el archivo existe, lo cargamos, si no, creamos una lista vacía
#             if os.path.exists(json_file):
#                 with open(json_file, 'r') as file:
#                     json_data = json.load(file)
#                     if not isinstance(json_data, list):  # Verificar si es un array
#                         json_data = []
#             else:
#                 json_data = []
#             json_data.append(data)  # Guardamos solo los datos filtrados
#             # Guardar los datos actualizados en el archivo JSON
#             with open(json_file, 'w') as file:
#                 json.dump(json_data, file, indent=4)
#             # Retornar una respuesta exitosa
#             return jsonify({'status': 'Datos recibidos y guardados correctamente'}), 200
#         else:
#             # Retornar una respuesta indicando que no hay mensajes
#             return jsonify({'status': 'No hay mensajes para guardar'}), 200
#     except Exception as e:
#         print("Error en el procesamiento del mensaje:", e)
#         return jsonify({'error': 'Error en el procesamiento del mensaje'}), 500


@app.route('/webhook', methods=['POST'])
def recibir_mensajes():
    try:
        # Obtener los datos del POST request
        data = request.get_json()
        
        # Verificar la estructura de los datos
        entry = data.get('entry')
        if not entry:
            return jsonify({'error': 'Estructura de datos inválida, falta el campo "entry"'}), 400
        
        changes = entry[0].get('changes')
        if not changes:
            return jsonify({'error': 'Estructura de datos inválida, falta el campo "changes"'}), 400

        value = changes[0].get('value')
        if not value:
            return jsonify({'error': 'Estructura de datos inválida, falta el campo "value"'}), 400
        
        messages = value.get('messages')
        logging.info(f"Mensajes recibidos: {messages}")

        # Verificar si hay mensajes
        if messages:
            # Obtener el número del remitente
            numero = messages.get("from", "")
            if not numero:
                return jsonify({'error': 'No se encontró el número del remitente'}), 400

            # Definir el nombre del archivo JSON
            json_file = Path(f'usuario_{numero}.json')

            # Si el archivo existe, lo cargamos, si no, creamos una lista vacía
            if json_file.exists():
                with json_file.open('r') as file:
                    try:
                        json_data = json.load(file)
                        if not isinstance(json_data, list):  # Verificar si es un array
                            json_data = []
                    except json.JSONDecodeError:
                        json_data = []
            else:
                json_data = []

            # Agregar los nuevos datos al archivo JSON
            json_data.append(data)

            # Guardar los datos actualizados en el archivo JSON
            with json_file.open('w') as file:
                json.dump(json_data, file, indent=4)

            # Retornar una respuesta exitosa
            return jsonify({'status': 'Datos recibidos y guardados correctamente'}), 200
        else:
            # Retornar una respuesta indicando que no hay mensajes
            return jsonify({'status': 'No hay mensajes para guardar'}), 200
    except KeyError as ke:
        logging.error(f"Error de clave en los datos recibidos: {ke}")
        return jsonify({'error': f'Error de clave en los datos recibidos: {ke}'}), 400
    except Exception as e:
        logging.error(f"Error en el procesamiento del mensaje: {e}")
        return jsonify({'error': 'Error en el procesamiento del mensaje'}), 500




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
