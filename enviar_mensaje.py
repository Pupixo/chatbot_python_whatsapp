import http.client
import json

PAGE_ID = "323605944180431"
ACCESS_TOKEN = "EAARZA5UhHwCUBO5woOQOPJZCH1TB62ZAX1kh2RsTMa4GwLVsnyAgTZCdWx9hZBm8GOfYZClTXstA1N513YLTlKQ8TAyoUdXUyHWFZCuqMBq3tkBXQrFdSxbEgTZB2YHqyQfpnod0BcH8zN0qOH5qZBXqMit2pzZCTJlBJIVXQfKtJh9cgj1nJ0ZBXnZCtRYUdBtyoG3VocqQndFy2ZB3rq5qFBM5ZAZA1AmvP94tct7jmoo"

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
