from flask import Flask, request, jsonify
import http.client
import json
import re
import random
import string  # Para generar el código de validación alfanumérico
from conexionbd import obtener_mensaje_por_id, obtener_alternativas_por_id_pregunta, verificar_usuario_registrado
from correo import enviar_correo  # Importa la función de envío de correo

app = Flask(__name__)

TOKEN_ANDERCODE = "ANDERCODE"
PAGE_ID = "421866537676248"
ACCESS_TOKEN = "EAAYAnB4BMXoBO9EHKqeQkmLndJSNfvZCniqZBUZBji3SXYWz678zbuK3TdzZC8vLG8nF8ZBNlsoeBwtmCthPox62x8iKhHE19DtZAEIjcKtjVbNTsL7cMWKonZC0icywXEbCnvuy7lB1hreKbJB4JB9JbeaFXdO65gknLdZBLhrWkRP8Nb9c7duaMcIiOjry77IxP11l88NXQ6F4PcszNH03em8AbUYZD"

mensajes_procesados = set()
estado_usuario = {}

@app.route('/')
def index():
    return "Descargando virus..."

@app.route('/webhook', methods=['GET'])
def verificar_token():
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    if challenge and token == TOKEN_ANDERCODE:
        return challenge
    else:
        return jsonify({'error': 'Token Inválido'}), 401

def validar_nombre(nombre):
    return not any(char.isdigit() for char in nombre)

def validar_numero(numero):
    return numero.isdigit() and 5 <= len(numero) <= 20

def validar_codigo(codigo):
    if len(codigo) < 2:
        return False
    
    letra = codigo[0].upper()
    numeros = codigo[1:]
    
    if not letra.isalpha() or not numeros.isdigit():
        return False
    
    if letra == "E":
        return 5 <= len(codigo) <= 6
    elif letra == "C":
        return 5 <= len(codigo) <= 8
    elif letra == "D":
        return 10 <= len(codigo) <= 15
    else:
        return False

def generar_codigo_validacion():
    # Genera un código de 4 caracteres que incluye letras y números
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

@app.route('/webhook', methods=['POST'])
def recibir_mensajes():
    try:
        data = request.get_json()
        print("Data received:", data)

        entry = data.get('entry', [])[0]
        changes = entry.get('changes', [])[0]
        value = changes.get('value', {})
        objeto_mensaje = value.get('messages', [])

        if objeto_mensaje:
            messages = objeto_mensaje[0]
            numero = messages.get("from", "")
            mensaje_id = messages.get("id", "")
            texto_usuario = messages.get("text", {}).get("body", "").strip()

            if mensaje_id in mensajes_procesados:
                return jsonify({'status': 'Mensaje ya procesado'}), 200
            mensajes_procesados.add(mensaje_id)

            if numero not in estado_usuario:
                estado_usuario[numero] = {
                    "intentos_correo": 0,
                    "intentos_nombre": 0,
                    "intentos_apellido": 0,
                    "intentos_numero": 0,
                    "intentos_codigo": 0,
                    "intentos_pregunta_7": 0,
                    "intentos_pregunta_8": 0,
                    "intentos_codigo_validacion": 0,
                    "esperando_correo": False,
                    "esperando_nombre": False,
                    "esperando_apellido": False,
                    "esperando_numero": False,
                    "esperando_codigo": False,
                    "esperando_pregunta_7": False,
                    "esperando_pregunta_8": False,
                    "esperando_codigo_validacion": False,
                    "autenticacion_confirmada": False,
                    "recordatorio_enviado": False,
                    "tipo_codigo": "",
                    "correo": "",
                    "codigo_validacion": ""
                }
                enviar_mensaje_inicial(numero)
                return jsonify({'status': 'Mensaje inicial enviado'}), 200

            if verificar_usuario_registrado(numero):
                enviar_mensaje_texto(numero, "Usuario ya está registrado")
                return jsonify({'status': 'Usuario registrado'}), 200

            if messages.get("type") == "interactive":
                interactive_obj = messages.get("interactive", {})
                button_reply = interactive_obj.get("button_reply", {})
                seleccion = button_reply.get("id", "")
                
                if seleccion == "button_yes":
                    mensaje_si = obtener_mensaje_por_id(2)
                    enviar_mensaje_texto(numero, mensaje_si)
                    estado_usuario[numero]["esperando_correo"] = True
                    estado_usuario[numero]["autenticacion_confirmada"] = True
                    estado_usuario[numero]["recordatorio_enviado"] = False
                elif seleccion == "button_no":
                    enviar_mensaje_texto(numero, "Okey, nos vemos pronto")
                    estado_usuario.pop(numero, None)
                return jsonify({'status': 'Respuesta a botón procesada'}), 200

            if not estado_usuario[numero].get("autenticacion_confirmada", False):
                if not estado_usuario[numero].get("recordatorio_enviado", False):
                    enviar_mensaje_texto(numero, "Por favor, escoja uno de los botones para continuar: 'Sí' o 'No'.")
                    estado_usuario[numero]["recordatorio_enviado"] = True
                return jsonify({'status': 'Esperando selección de botón'}), 200

            if estado_usuario[numero].get("esperando_correo", False):
                if not validar_correo(texto_usuario):
                    estado_usuario[numero]["intentos_correo"] += 1
                    if estado_usuario[numero]["intentos_correo"] == 1:
                        enviar_mensaje_texto(numero, "Correo inválido, por favor vuelva a ingresar. Intento 1/2")
                    elif estado_usuario[numero]["intentos_correo"] == 2:
                        enviar_mensaje_texto(numero, "Correo inválido, nos vemos pronto.")
                        estado_usuario.pop(numero, None)
                else:
                    estado_usuario[numero]["correo"] = texto_usuario
                    mensaje_nombre = obtener_mensaje_por_id(3)
                    enviar_mensaje_texto(numero, mensaje_nombre)
                    estado_usuario[numero]["intentos_nombre"] = 0
                    estado_usuario[numero]["esperando_nombre"] = True
                    estado_usuario[numero]["esperando_correo"] = False
                return jsonify({'status': 'Intento de correo procesado'}), 200

            if estado_usuario[numero].get("esperando_nombre", False):
                if validar_nombre(texto_usuario):
                    estado_usuario[numero]["esperando_nombre"] = False
                    estado_usuario[numero]["esperando_apellido"] = True
                    mensaje_apellido = obtener_mensaje_por_id(4)
                    enviar_mensaje_texto(numero, mensaje_apellido)
                else:
                    estado_usuario[numero]["intentos_nombre"] += 1
                    if estado_usuario[numero]["intentos_nombre"] == 1:
                        enviar_mensaje_texto(numero, "Nombre inválido, por favor vuelva a ingresar. Intento 1/2")
                    elif estado_usuario[numero]["intentos_nombre"] == 2:
                        enviar_mensaje_texto(numero, "Nombre inválido, nos vemos pronto.")
                        estado_usuario.pop(numero, None)
                return jsonify({'status': 'Intento de nombre procesado'}), 200

            if estado_usuario[numero].get("esperando_apellido", False):
                if validar_nombre(texto_usuario):
                    estado_usuario[numero]["esperando_apellido"] = False
                    estado_usuario[numero]["esperando_numero"] = True
                    mensaje_numero = obtener_mensaje_por_id(5)
                    enviar_mensaje_texto(numero, mensaje_numero)
                else:
                    estado_usuario[numero]["intentos_apellido"] += 1
                    if estado_usuario[numero]["intentos_apellido"] == 1:
                        enviar_mensaje_texto(numero, "Apellido inválido, por favor vuelva a ingresar. Intento 1/2")
                    elif estado_usuario[numero]["intentos_apellido"] == 2:
                        enviar_mensaje_texto(numero, "Apellido inválido, nos vemos pronto.")
                        estado_usuario.pop(numero, None)
                return jsonify({'status': 'Intento de apellido procesado'}), 200

            if estado_usuario[numero].get("esperando_numero", False):
                if validar_numero(texto_usuario):
                    estado_usuario[numero]["esperando_numero"] = False
                    estado_usuario[numero]["esperando_codigo"] = True
                    mensaje_codigo = obtener_mensaje_por_id(6)
                    enviar_mensaje_texto(numero, mensaje_codigo)
                else:
                    estado_usuario[numero]["intentos_numero"] += 1
                    if estado_usuario[numero]["intentos_numero"] == 1:
                        enviar_mensaje_texto(numero, "Número inválido, por favor vuelva a ingresar. Intento 1/2")
                    elif estado_usuario[numero]["intentos_numero"] == 2:
                        enviar_mensaje_texto(numero, "Número inválido, nos vemos pronto.")
                        estado_usuario.pop(numero, None)
                return jsonify({'status': 'Intento de número procesado'}), 200

            if estado_usuario[numero].get("esperando_codigo", False):
                if validar_codigo(texto_usuario):
                    estado_usuario[numero]["esperando_codigo"] = False
                    estado_usuario[numero]["esperando_pregunta_7"] = True
                    estado_usuario[numero]["tipo_codigo"] = texto_usuario[0].upper()
                    
                    mensaje_pregunta_7 = obtener_mensaje_por_id(7)
                    alternativas_pregunta_7 = obtener_alternativas_por_id_pregunta(7)
                    
                    if alternativas_pregunta_7:
                        opciones = "\n".join([f"{i+1}️⃣ {alternativa}" for i, alternativa in enumerate(alternativas_pregunta_7)])
                        enviar_mensaje_texto(numero, f"{mensaje_pregunta_7}\n\n{opciones}")
                    else:
                        enviar_mensaje_texto(numero, "No se encontraron alternativas para la siguiente pregunta.")
                else:
                    estado_usuario[numero]["intentos_codigo"] += 1
                    if estado_usuario[numero]["intentos_codigo"] == 1:
                        enviar_mensaje_texto(numero, "Código inválido, por favor vuelva a ingresar. Intento 1/2")
                    elif estado_usuario[numero]["intentos_codigo"] == 2:
                        enviar_mensaje_texto(numero, "Código inválido, nos vemos pronto.")
                        estado_usuario.pop(numero, None)
                return jsonify({'status': 'Intento de código procesado'}), 200

            if estado_usuario[numero].get("esperando_pregunta_7", False):
                tipo_codigo = estado_usuario[numero]["tipo_codigo"]
                valid_ids = []

                if tipo_codigo == "E":
                    valid_ids = [4, 6, 7]
                elif tipo_codigo == "C":
                    valid_ids = [3]
                elif tipo_codigo == "D":
                    valid_ids = [5]

                try:
                    alternativa_id = int(texto_usuario)
                    id_map = {
                        1: 3,
                        2: 4,
                        3: 5,
                        4: 6,
                        5: 7
                    }
                    if id_map.get(alternativa_id) in valid_ids:
                        # enviar_mensaje_texto(numero, "Gracias, puede proceder.")
                        estado_usuario[numero]["esperando_pregunta_7"] = False
                        estado_usuario[numero]["esperando_pregunta_8"] = True
                        mensaje_pregunta_8 = obtener_mensaje_por_id(8)
                        alternativas_pregunta_8 = obtener_alternativas_por_id_pregunta(8)
                        if alternativas_pregunta_8:
                            opciones = "\n".join([f"{i+1}️⃣ {alternativa}" for i, alternativa in enumerate(alternativas_pregunta_8)])
                            enviar_mensaje_texto(numero, f"{mensaje_pregunta_8}\n\n{opciones}")
                        else:
                            enviar_mensaje_texto(numero, "No se encontraron alternativas para la siguiente pregunta.")
                    else:
                        estado_usuario[numero]["intentos_pregunta_7"] += 1
                        if estado_usuario[numero]["intentos_pregunta_7"] == 1:
                            enviar_mensaje_texto(numero, "Por favor, responda con un número entre 1 y 5 para seleccionar su canal donde corresponda. (1/2 intentos)")
                        elif estado_usuario[numero]["intentos_pregunta_7"] == 2:
                            enviar_mensaje_texto(numero, "Intentos fallidos, nos vemos pronto.")
                            estado_usuario.pop(numero, None)
                except ValueError:
                    estado_usuario[numero]["intentos_pregunta_7"] += 1
                    if estado_usuario[numero]["intentos_pregunta_7"] == 1:
                        enviar_mensaje_texto(numero, "Por favor, responda con un número entre 1 y 5 para seleccionar su canal donde corresponda. (1/2 intentos)")
                    elif estado_usuario[numero]["intentos_pregunta_7"] == 2:
                        enviar_mensaje_texto(numero, "Intentos fallidos, nos vemos pronto.")
                        estado_usuario.pop(numero, None)
                return jsonify({'status': 'Respuesta a pregunta 7 procesada'}), 200

            if estado_usuario[numero].get("esperando_pregunta_8", False):
                try:
                    alternativa_id = int(texto_usuario)
                    if 1 <= alternativa_id <= 4:
                        # Generar y enviar el código de validación alfanumérico
                        codigo_validacion = generar_codigo_validacion()
                        estado_usuario[numero]["codigo_validacion"] = codigo_validacion
                        enviar_correo(estado_usuario[numero]["correo"], codigo_validacion)  # Envía el correo con el código

                        # Preguntar por el código de validación
                        estado_usuario[numero]["esperando_codigo_validacion"] = True
                        estado_usuario[numero]["intentos_codigo_validacion"] = 0  # Inicializar el contador de intentos
                        enviar_mensaje_texto(numero, "Se envió a su correo un código de validación, ingrese el código para finalizar.")
                        estado_usuario[numero]["esperando_pregunta_8"] = False
                    else:
                        estado_usuario[numero]["intentos_pregunta_8"] += 1
                        if estado_usuario[numero]["intentos_pregunta_8"] == 1:
                            enviar_mensaje_texto(numero, "Por favor, responda con un número entre 1 y 4 para seleccionar su opción. (1/2 intentos)")
                        elif estado_usuario[numero]["intentos_pregunta_8"] == 2:
                            enviar_mensaje_texto(numero, "Intentos fallidos, nos vemos pronto.")
                            estado_usuario.pop(numero, None)
                except ValueError:
                    estado_usuario[numero]["intentos_pregunta_8"] += 1
                    if estado_usuario[numero]["intentos_pregunta_8"] == 1:
                        enviar_mensaje_texto(numero, "Por favor, responda con un número entre 1 y 4 para seleccionar su opción. (1/2 intentos)")
                    elif estado_usuario[numero]["intentos_pregunta_8"] == 2:
                        enviar_mensaje_texto(numero, "Intentos fallidos, nos vemos pronto.")
                        estado_usuario.pop(numero, None)
                return jsonify({'status': 'Respuesta a pregunta 8 procesada'}), 200

            # Validación del código de correo enviado
            if estado_usuario[numero].get("esperando_codigo_validacion", False):
                if texto_usuario == estado_usuario[numero]["codigo_validacion"]:
                    enviar_mensaje_texto(numero, "¡Felicidades! Su proceso de autenticación ha sido completado con éxito.")
                    estado_usuario.pop(numero, None)  # Finaliza el proceso
                else:
                    estado_usuario[numero]["intentos_codigo_validacion"] += 1
                    if estado_usuario[numero]["intentos_codigo_validacion"] == 1:
                        enviar_mensaje_texto(numero, "Código incorrecto, por favor intente nuevamente. Intento 1/2")
                    elif estado_usuario[numero]["intentos_codigo_validacion"] == 2:
                        enviar_mensaje_texto(numero, "Código incorrecto. Intentos fallidos, nos vemos pronto.")
                        estado_usuario.pop(numero, None)  # Finaliza el proceso después de 2 intentos fallidos
                return jsonify({'status': 'Validación de código procesada'}), 200
            
            return jsonify({'status': 'Respuesta procesada'}), 200
        else:
            return jsonify({'error': 'No hay mensajes para procesar'}), 400
    except Exception as e:
        print("Error en el procesamiento del mensaje:", e)
        return jsonify({'error': 'Error en el procesamiento del mensaje'}), 500

def enviar_mensaje_texto(numero, mensaje_texto):
    responder_mensaje = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "text",
        "text": {
            "body": mensaje_texto
        }
    }
    enviar_mensaje(responder_mensaje)

def validar_correo(correo):
    patron = r'^[A-Za-z]{5,}@(globalhitss\.com|claro\.com\.pe)$'
    return re.match(patron, correo) is not None

def enviar_mensaje_inicial(numero):
    mensaje_db = obtener_mensaje_por_id(1)
    alternativas = obtener_alternativas_por_id_pregunta(1)

    botones = [
        {
            "type": "reply",
            "reply": {
                "id": "button_yes",
                "title": alternativas[0] if len(alternativas) > 0 else "Sí"
            }
        },
        {
            "type": "reply",
            "reply": {
                "id": "button_no",
                "title": alternativas[1] if len(alternativas) > 1 else "No"
            }
        }
    ]

    responder_mensaje = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": mensaje_db
            },
            "action": {
                "buttons": botones
            }
        }
    }
    enviar_mensaje(responder_mensaje)

def enviar_mensaje(mensaje):
    conn = http.client.HTTPSConnection("graph.facebook.com")
    payload = json.dumps(mensaje)
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    conn.request("POST", f"/v15.0/{PAGE_ID}/messages", payload, headers)
    res = conn.getresponse()
    data = res.read()
    print("Respuesta de Facebook API:", data.decode("utf-8"))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
