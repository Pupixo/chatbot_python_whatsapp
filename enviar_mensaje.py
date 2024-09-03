import http.client
import json
import time
import requests
import os
from datetime import datetime



PAGE_ID = "323605944180431"
ACCESS_TOKEN = "EAARZA5UhHwCUBO2GNYBFjAzZAlBGXsEd0UJYwm6T97Vq8iUNu0O4Y3HeQPnMhhtobal02aHFd0mgh7ZC8k8ZAl0cph4ljsaFDzwj74NCqwLXa7x2Lpq4C4yISWwZA3SYwy1l9btUqZA0xX2qeD7uDNOVdZBBbblHXJfDkK9ckMqbgroGMNi846CgYHj50rkT0lZCagRactjwOSJIkx3A3dI8ioy74ZCZBQ2fMqdzYZD"




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

    directorio = os.path.join('img_tickets_req', numero)  # Carpeta donde se guardarán las imágenes
    os.makedirs(directorio, exist_ok=True)  # Crea el directorio si no existe

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

        filename = f"{media_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        file_path = os.path.join(directorio, filename)

        # Descargar la imagen
        try:
            img_response = requests.get(media_url, headers=headers)
            img_response.raise_for_status()

            with open(file_path, 'wb') as f:
                f.write(img_response.content)

            print(f"Imagen guardada en {file_path}.")
        except requests.RequestException as e:
            print(f"Error al descargar la imagen: {e}")

    except http.client.HTTPException as e:
        print(f"Error en la conexión HTTP: {e}")

    finally:
        conn.close()