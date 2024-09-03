import http.client
import json
import time
import requests
import os
from datetime import datetime



PAGE_ID = "323605944180431"
ACCESS_TOKEN = "EAARZA5UhHwCUBO2GNYBFjAzZAlBGXsEd0UJYwm6T97Vq8iUNu0O4Y3HeQPnMhhtobal02aHFd0mgh7ZC8k8ZAl0cph4ljsaFDzwj74NCqwLXa7x2Lpq4C4yISWwZA3SYwy1l9btUqZA0xX2qeD7uDNOVdZBBbblHXJfDkK9ckMqbgroGMNi846CgYHj50rkT0lZCagRactjwOSJIkx3A3dI8ioy74ZCZBQ2fMqdzYZD"


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



# def crear_directorio(directorio):
#     if not os.path.exists(directorio):
#         os.makedirs(directorio)


# def recibir_img(media_id):
#     conn = http.client.HTTPSConnection("graph.facebook.com")
#     headers = {
#         'Authorization': f'Bearer {ACCESS_TOKEN}',
#     }

#     # Solicitar los detalles del archivo multimedia
#     conn.request("GET", f"/v15.0/{media_id}", headers=headers)
#     res = conn.getresponse()
#     data = res.read().decode("utf-8")
    
#     if res.status == 200:
#         response_json = json.loads(data)
        
#         # Obtener la URL de descarga del archivo multimedia
#         media_url = response_json.get('url')
#         if media_url:
#             # Crear la carpeta si no existe
#             crear_directorio(SAVE_DIRECTORY)

#             # Generar el nombre del archivo con ID y la fecha/hora
#             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#             filename = f"{media_id}_{timestamp}.jpg"
#             file_path = os.path.join(SAVE_DIRECTORY, filename)

#             # Descargar la imagen con headers si es necesario
#             headers = {
#                 'Authorization': f'Bearer {ACCESS_TOKEN}',  # Incluye aquí cualquier otro encabezado necesario
#             }
#             try:
#                 img_response = requests.get(media_url, headers=headers)
#                 img_response.raise_for_status()  # Lanza un error para códigos de estado HTTP 4xx/5xx
#                 with open(file_path, 'wb') as f:
#                     f.write(img_response.content)
#                 print(f"Imagen descargada exitosamente y guardada en {file_path}.")
#             except requests.RequestException as e:
#                 print(f"Error al descargar la imagen: {e}")
#         else:
#             print("No se encontró la URL de la imagen en la respuesta.")
#     else:
#         print(f"Error al obtener los detalles del archivo multimedia. Código de estado: {res.status}")


def recibir_img(media_id):
    conn = http.client.HTTPSConnection("graph.facebook.com")
    headers = {'Authorization': f'Bearer {ACCESS_TOKEN}'}

    conn.request("GET", f"/v15.0/{media_id}", headers=headers)
    res = conn.getresponse()
    
    if res.status == 200:
        media_url = json.loads(res.read()).get('url')
        if media_url:
            os.makedirs(SAVE_DIRECTORY, exist_ok=True)
            filename = f"{media_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            file_path = os.path.join(SAVE_DIRECTORY, filename)
            
            try:
                img_response = requests.get(media_url, headers=headers)
                img_response.raise_for_status()
                with open(file_path, 'wb') as f:
                    f.write(img_response.content)
                print(f"Imagen guardada en {file_path}.")
            except requests.RequestException as e:
                print(f"Error al descargar la imagen: {e}")
        else:
            print("URL de la imagen no encontrada.")
    else:
        print(f"Error al obtener detalles. Código de estado: {res.status}")
