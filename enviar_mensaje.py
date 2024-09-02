import http.client
import json

PAGE_ID = "323605944180431"
ACCESS_TOKEN = "EAARZA5UhHwCUBO2ocDNDIuwPPZBXR9rtLdsGob4UJ5rCeZB8IYaOG8eKENx1mG0vfz3KnJZBeox1JXiKFda1NPpAL3ciQZA0UoSTO9fI0ONKZCfTTkTd9uwm0OwcuKhFWW8wZAC9WULE1ykbwVExM27bG3CvLWayzA2VwOTmeapSQtuKWGBL32EZCfIsjUFMr3OGqdbR7e0ER7l7g3pJoYjjEOYHW82EZA8LqK8AZD"

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
