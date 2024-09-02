import http.client
import json
import time
import requests
import os
from datetime import datetime



PAGE_ID = "323605944180431"
ACCESS_TOKEN = "EAARZA5UhHwCUBO5woOQOPJZCH1TB62ZAX1kh2RsTMa4GwLVsnyAgTZCdWx9hZBm8GOfYZClTXstA1N513YLTlKQ8TAyoUdXUyHWFZCuqMBq3tkBXQrFdSxbEgTZB2YHqyQfpnod0BcH8zN0qOH5qZBXqMit2pzZCTJlBJIVXQfKtJh9cgj1nJ0ZBXnZCtRYUdBtyoG3VocqQndFy2ZB3rq5qFBM5ZAZA1AmvP94tct7jmoo"
SAVE_DIRECTORY = 'imagenes_descargadas'  # Carpeta donde se guardarán las imágenes


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



def crear_directorio(directorio):
    if not os.path.exists(directorio):
        os.makedirs(directorio)

def recibir_img(media_id):
    conn = http.client.HTTPSConnection("graph.facebook.com")
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
    }

    # Solicitar los detalles del archivo multimedia
    conn.request("GET", f"/v15.0/{media_id}", headers=headers)
    res = conn.getresponse()

    if res.status == 200:
        data = res.read().decode("utf-8")
        response_json = json.loads(data)
        
        # Obtener la URL de descarga del archivo multimedia
        media_url = response_json.get('url')
        if media_url:
            # Crear la carpeta si no existe
            crear_directorio(SAVE_DIRECTORY)

            # Generar el nombre del archivo con ID y la fecha/hora
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{media_id}_{timestamp}.jpg"
            file_path = os.path.join(SAVE_DIRECTORY, filename)

            # Descargar la imagen
            img_response = requests.get(media_url)
            if img_response.status_code == 200:
                with open(file_path, 'wb') as f:
                    f.write(img_response.content)
                print(f"Imagen descargada exitosamente y guardada en {file_path}.")
                return file_path
            else:
                print(f"Error al descargar la imagen. Código de estado: {img_response.status_code}")
                return None
        else:
            print("No se encontró la URL de la imagen en la respuesta.")
            return None
    else:
        print(f"Error al obtener los detalles del archivo multimedia. Código de estado: {res.status}")
        return None