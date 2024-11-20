from flask import Flask, request, jsonify
import http.client
import json
import re
import random
import string
import os
from pathlib import Path
import logging
import requests
import time

app = Flask(__name__)

TOKEN_ANDERCODE = "ANDERCODE"
PAGE_ID = "391832127348225"
ACCESS_TOKEN = "EAAOcMhFbbo0BOZBhf6UnBNXlmkrS8JAqWNp2VZBUbXYp69bYpLZCCl5OYOnggjFXKkxHIK4m8cUnLTheQrRzUvG7c7YtPWOzBhYcqLPRRu9H88MuRA1CZAacLtWMtZB85jCJhhImvWBzS1ZBsoHZAek8u87htftZA4Rs5mwJMPj9c3ZCIZCkaUourDXwXwKlOF9xdLjm9mBtN7b0ql3uuGh43ijkBcCwxWQB93ExSTcYskgGsZD"


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

@app.route('/get-mensajes/<number>', methods=['GET'])  # Utilizamos el número como parámetro en la URL
def get_mensajesbyjson(number):
    # Verificar si el número es válido
    print("number...............",number)
    if not number.isdigit():
        return jsonify({"error": "El parámetro 'number' debe ser un número válido."}), 400

    # Definir el nombre del archivo JSON basado en el número
    json_file = f'usu_numbers/usuario_{number}.json'

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
        json_file = f'usu_numbers/usuario_{numero}.json'

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

@app.route('/listar-jsons-usu', methods=['GET'])
def obtener_nombres_todos_los_jsons():
    try:
        # Carpeta donde se almacenan los archivos JSON
        folder = 'usu_numbers'

        # Verificar si la carpeta existe
        if not os.path.exists(folder):
            return jsonify({'usuarios': []})

        # Obtener la lista de archivos en la carpeta
        files = os.listdir(folder)

        # Filtrar los archivos con extensión .json y que comiencen con 'usuario_'
        files_jsons = [f for f in files if f.endswith('.json') and f.startswith('usuario_')]

        # Si no hay archivos que cumplan el criterio, retornar lista vacía
        if not files_jsons:
            return jsonify({'usuarios': []})

        # Extraer el número de usuario de los nombres de archivo (lo que está después del '_')
        usuarios = [f.split('_')[1].replace('.json', '') for f in files_jsons]

        # Ordenar los archivos por fecha de última modificación (si fuera necesario)
        files_jsons.sort(key=lambda f: os.path.getmtime(os.path.join(folder, f)), reverse=True)

        # Retornar la lista de números de usuario en formato JSON
        return jsonify({'usuarios': usuarios})

    except Exception as e:
        # Manejo de errores durante la lectura de los archivos
        print("Error al obtener los nombres de los archivos json y listarlos:", e)
        return jsonify({'error': f'Error al obtener los nombres de los archivos json y listarlos: {str(e)}'}), 500

@app.route('/webhook', methods=['POST'])
def recibir_mensajes():
    try:
        data = request.get_json()
        if data is None:
            return jsonify({'error': 'No se recibieron datos JSON válidos'}), 400

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

        if isinstance(messages, list) and messages:  # Verificamos que sea una lista no vacía
            for message in messages:
                numero = message.get("from", "")
                if not numero:
                    return jsonify({'error': 'No se encontró el número del remitente'}), 400

                json_file = f'usu_numbers/usuario_{numero}.json'

                if os.path.exists(json_file):
                    with open(json_file, 'r') as file:
                        try:
                            json_data = json.load(file)
                            if not isinstance(json_data, list):
                                json_data = []
                        except json.JSONDecodeError:
                            json_data = []
                else:
                    json_data = []

                json_data.append(data)

                # Verificar permisos de escritura y existencia del directorio
                if not os.path.exists('usu_numbers'):
                    os.makedirs('usu_numbers')

                with open(json_file, 'w') as file:
                    json.dump(json_data, file, indent=4)

            return jsonify({'status': 'Datos recibidos y guardados correctamente'}), 200
        else:
            return jsonify({'status': 'No hay mensajes para guardar'}), 200
    except KeyError as ke:
        logging.error(f"Error de clave en los datos recibidos: {ke}", exc_info=True)
        return jsonify({'error': f'Error de clave en los datos recibidos: {ke}'}), 400
    except Exception as e:
        logging.error(f"Error en el procesamiento del mensaje: {e}", exc_info=True)
        return jsonify({'error': 'Error en el procesamiento del mensaje'}), 500

@app.route('/enviar_msg_masivos-whatsapp_api', methods=['POST'])
def enviar_msg_whatsapp_api():
    try:
        # Obtener el criterio de eliminación desde el cuerpo de la solicitud POST
        data = request.get_json()
        print("data...........................................................",data)

        mensaje = data['mensaje']
        numero= data['numero']
        mensaje_id= data['mensaje_id'] 
        
        print("mensaje...........................................................",mensaje)

        conn = http.client.HTTPSConnection("graph.facebook.com")
        payload = mensaje
        headers = {
            'Authorization': f'Bearer {ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }
        conn.request("POST", f"/v20.0/{PAGE_ID}/messages", payload, headers)
        res = conn.getresponse()
        data = res.read()
        print("Respuesta de Facebook API:", data.decode("utf-8"))

        try:
            if mensaje_id == None:
                id_eliminar = mensaje_id
                print("ID a eliminar:", id_eliminar)
                print("numero a eliminar:", numero)  
                # Definir el nombre del archivo JSON
                json_file = f'usu_numbers/usuario_{numero}.json'

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
            else:

                print("no se elimina nada, ya que es un mensaje de envio")  

        except Exception as e:
            # Manejo de errores durante la lectura o escritura del archivo
            print("Error al procesar la eliminación del mensaje:", e)
            return jsonify({'error': f'Error al procesar la eliminación: {str(e)}'}), 500

    except Exception as e:
        # Manejo de errores durante la lectura o escritura del archivo
        print("Error al procesar la eliminación del mensaje:", e)
        return jsonify({'error': f'Error al procesar la eliminación: {str(e)}'}), 500


@app.route('/enviar_msg-whatsapp_api', methods=['POST'])
def enviar_msg_whatsapp_api():
    try:
        # Obtener el criterio de eliminación desde el cuerpo de la solicitud POST
        data = request.get_json()
        print("data...........................................................",data)

        mensaje = data['mensaje']
        numero= data['numero']
        mensaje_id= data['mensaje_id'] 
        
        print("mensaje...........................................................",mensaje)

        conn = http.client.HTTPSConnection("graph.facebook.com")
        payload = json.dump(mensaje)  
        
        headers = {
            'Authorization': f'Bearer {ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }
        conn.request("POST", f"/v20.0/{PAGE_ID}/messages", payload, headers)
        res = conn.getresponse()
        data = res.read()
        print("Respuesta de Facebook API:", data.decode("utf-8"))

        try:
            if mensaje_id == None:
                id_eliminar = mensaje_id
                print("ID a eliminar:", id_eliminar)
                print("numero a eliminar:", numero)  
                # Definir el nombre del archivo JSON
                json_file = f'usu_numbers/usuario_{numero}.json'

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
            else:

                print("no se elimina nada, ya que es un mensaje de envio")  

        except Exception as e:
            # Manejo de errores durante la lectura o escritura del archivo
            print("Error al procesar la eliminación del mensaje:", e)
            return jsonify({'error': f'Error al procesar la eliminación: {str(e)}'}), 500

    except Exception as e:
        # Manejo de errores durante la lectura o escritura del archivo
        print("Error al procesar la eliminación del mensaje:", e)
        return jsonify({'error': f'Error al procesar la eliminación: {str(e)}'}), 500















## token de Envio 
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
