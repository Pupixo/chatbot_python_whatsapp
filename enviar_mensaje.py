import http.client
import json
import time

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




def enviar_mensaje_lista(numero, filas, title):
    max_rows_per_section = 10
    max_sections_per_message = 10

    rows_data = []
    sections = []
    mensaje_listo = False

    # Dividir las filas en secciones de 10 elementos
    for i, nombre in enumerate(filas):
        numero_icono = "".join(f"{digit}\u20E3" for digit in str(i + 1))
        rows_data.append({"id": numero_icono, "title": nombre, "description": nombre})
        
        # Crear una nueva sección cada 10 filas
        if len(rows_data) == max_rows_per_section or i == len(filas) - 1:
            sections.append({
                "title": f"Opciones {len(sections) + 1}",
                "rows": rows_data
            })
            rows_data = []  # Reiniciar para la próxima sección

        # Enviar el mensaje si alcanzamos 10 secciones
        if len(sections) == max_sections_per_message:
            responder_mensaje = {
                "messaging_product": "whatsapp",
                "to": numero,
                "type": "interactive",
                "interactive": {
                    "type": "list",
                    "body": {
                        "text": "Selecciona Alguna Opción"
                    },
                    "footer": {
                        "text": "Selecciona una de las opciones para poder ayudarte"
                    },
                    "action": {
                        "button": "Ver Opciones",
                        "sections": sections
                    }
                }
            }
            enviar_mensaje(responder_mensaje)
            sections = []  # Reiniciar para la próxima tanda de secciones
            mensaje_listo = True  # Indica que hemos enviado un mensaje

    # Enviar cualquier sección restante
    if sections:
        responder_mensaje = {
            "messaging_product": "whatsapp",
            "to": numero,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {
                    "text": "Selecciona Alguna Opción"
                },
                "footer": {
                    "text": "Selecciona una de las opciones para poder ayudarte"
                },
                "action": {
                    "button": "Ver Opciones",
                    "sections": sections
                }
            }
        }
        enviar_mensaje(responder_mensaje)
        mensaje_listo = True

    # Si ningún mensaje fue enviado (cuando filas <= 10)
    if not mensaje_listo:
        print("No se envió ningún mensaje. Verifica la cantidad de filas.")



# def enviar_mensaje_lista(numero, filas,title):

#     rows_data = []
#     sections = []

#     # Dividir las filas en secciones de 10 elementos
#     for i, nombre in enumerate(filas):
#         numero_icono = "".join(f"{digit}\u20E3" for digit in str(i + 1))
#         rows_data.append({"id": numero_icono, "title": nombre, "description": nombre})
        
#         # Cada 10 filas, crea una nueva sección
#         if len(rows_data) == 10 or i == len(filas) - 1:
#             sections.append({
#                 "title": f"Opciones {len(sections) + 1}",
#                 "rows": rows_data
#             })
#             rows_data = []  # Reiniciar para la próxima sección

#     time.sleep(4)
#     print("sections...................", sections)

#     responder_mensaje = {
#         "messaging_product": "whatsapp",
#         "to": numero,
#         "type": "interactive",
#         "interactive": {
#             "type": "list",
#             "body": {
#                 "text": "Selecciona Alguna Opción"
#             },
#             "footer": {
#                 "text": "Selecciona una de las opciones para poder ayudarte"
#             },
#             "action": {
#                 "button": "Ver Opciones",
#                 "sections": sections
#             }
#         }
#     }

#     enviar_mensaje(responder_mensaje)
