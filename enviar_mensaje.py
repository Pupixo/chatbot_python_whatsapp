import http.client
import json
import time
import requests
import os
from datetime import datetime

from conexionbd import guardar_imagen_en_db


PAGE_ID = "323605944180431"
ACCESS_TOKEN = "EAARZA5UhHwCUBO4UQUwpxJQKqv4Y9XqWysRnLgNhKmR7M8LUgvQIELZAzfSjfiSWHsw0jE0OGZCKQnBRkZBxnPy7MKZAC5m25d1xFj4lQ8YXnXTs2uWyEFxFC6cxHX8oWyrZAeKx1BUgXYqGDUbbgZBDYTUZAyY1oTdOp56U83e2WYpeZCQS8Kp3zPBKxpjOFZBrM30U1TrbWMvexS6BecaqXTWLTLHwPM5Kux6cSmJiBT8ZCsZD"



def enviar_mensaje_lista(numero, lista_de_gerencia, titulo, mensaje_completo):
    secciones = []
    for i in range(0, len(lista_de_gerencia), 5):
        seccion = {
            "title": f"Opciones {i // 5 + 1}",
            "rows": lista_de_gerencia[i:i + 5]
        }
        secciones.append(seccion)
    
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {
                "text": mensaje_completo
            },
            "footer": {
                "text": "Selecciona una de las opciones para poder ayudarte"
            },
            "action": {
                "button": titulo,
                "sections": secciones
            }
        }
    }

    return data


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



def recibir_img(media_id, numero):
    conn = http.client.HTTPSConnection("graph.facebook.com")
    headers = {'Authorization': f'Bearer {ACCESS_TOKEN}'}

    # directorio = os.path.join('img_tickets_req', numero)  # Carpeta donde se guardarán las imágenes
    # os.makedirs(directorio, exist_ok=True)  # Crea el directorio si no existe

    try:
        conn.request("GET", f"/v15.0/{media_id}", headers=headers)
        res = conn.getresponse()

        if res.status != 200:
            print(f"Error al obtener detalles. Código de estado: {res.status}")
            return

        response_data = json.loads(res.read())
        media_url = response_data.get('url')

        if not media_url:
            print("URL de la imagen no encontrada.")
            return
        # filename = f"{media_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        # file_path = os.path.join(directorio, filename)

        # Descargar la imagen
        try:
            img_response = requests.get(media_url, headers=headers)
            img_response.raise_for_status()
            img = img_response.content

            # Guardar la imagen en la base de datos
            guardar_imagen_en_db(media_id, numero, img, 1)

            print("Imagen guardada en la base de datos.")
        except requests.RequestException as e:
            print(f"Error al descargar la imagen: {e}")

    except http.client.HTTPException as e:
        print(f"Error en la conexión HTTP: {e}")

    finally:
        conn.close()



def enviar_template(numero, mensaje_texto):

    payload = json.dumps({
    "messaging_product": "whatsapp",
    "recipient_type": "individual",
    "to": numero,
    "type": "template",
    "template": {
        "name": "servicio_historial_detalle",
        "language": {
        "code": "es"
        },
        "components": [
        {
            "type": "header",
            "parameters": [
            {
                "type": "image",
                "image": {
                "link": "https://www.imprentaonline.net/blog/wp-content/uploads/DALL%C2%B7E-2023-10-16-10.41.49-Illustration-depicting-a-humanoid-robot-with-half-of-its-face-transparent-revealing-intricate-circuits-and-gears-inside.-The-robot-is-holding-a-light-1.png"
                }
            }
            ]
        },
        {
            "type": "body",
            "parameters": [
            {
                "type": "text",
                "text": "text-string"
            },
            {
                "type": "text",
                "text": "text-string"
            },
            {
                "type": "text",
                "text": "text-string"
            },
            {
                "type": "text",
                "text": "text-string"
            },
            {
                "type": "text",
                "text": "text-string"
            }
            ]
        },
        {
            "type": "button",
            "sub_type": "quick_reply",
            "index": "0",
            "parameters": [
            {
                "type": "payload",
                "payload": "1234567"
            }
            ]
        }
        ]
    }
    })
