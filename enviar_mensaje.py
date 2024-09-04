import http.client
import json
import time
import requests
import os
from datetime import datetime

from conexionbd import guardar_imagen_en_db


PAGE_ID = "323605944180431"
ACCESS_TOKEN = "EAARZA5UhHwCUBO56W9WBZA4IvuMRiou0Bizh5MPeNZA4oOuQAj8CV8YlOK71mKkiZCGG6xCfOQaOqekAdNiIZC9o66BXRJ6ulrT7Gfaen9G3joBSPz2zyWl9FJkROaDK96U6MarqiVQXF2vzPKHBI73rM7viDxRXd2KeTAcIJpvdvSnUKaz2rV3cgDN8FC5gGe1EB9ibKYzYmqtzSaWdOBhLoeO3msm8fXIYZD"




# def enviar_mensaje_lista(numero, lista_de_gerencia,titulo,mensaje_completo):

#     data ={
#             "messaging_product": "whatsapp",
#             "to": numero,
#             "type": "interactive",
#             "interactive":{
#                 "type" : "list",
#                 "body": {
#                     "text": "Selecciona Alguna Opción"
#                 },
#                 "footer": {
#                     "text": "Selecciona una de las opciones para poder ayudarte"
#                 },
#                 "action":{
#                     "button":"Ver Opciones",
#                     "sections":[
#                         {
#                             "title":"Compra y Venta",
#                             "rows":[
#                                 {
#                                     "id":"btncompra",
#                                     "title" : "Comprar",
#                                     "description": "Compra los mejores articulos de tecnologia"
#                                 },
#                                 {
#                                     "id":"btnvender",
#                                     "title" : "Vender",
#                                     "description": "Vende lo que ya no estes usando"
#                                 }
#                             ]
#                         },{
#                             "title":"Distribución y Entrega",
#                             "rows":[
#                                 {
#                                     "id":"btndireccion",
#                                     "title" : "Local",
#                                     "description": "Puedes visitar nuestro local."
#                                 },
#                                 {
#                                     "id":"btnentrega",
#                                     "title" : "Entrega",
#                                     "description": "La entrega se realiza todos los dias."
#                                 }
#                             ]
#                         }
#                     ]
#                 }
#             }
#         }
    

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