import time
from enviar_mensaje import enviar_mensaje_texto,recibir_img,enviar_mensaje_lista
from consultas_gerencia import (
    obtener_nombres_gerencia, 
    obtener_canales_por_gerencia, 
    obtener_tipos_falla_por_canal, 
    obtener_aplicaciones_por_falla, 
    obtener_fallas_por_torre, 
    obtener_torre_por_aplicacion,
    obtener_escenarios_por_falla  # Nueva función importada
)


def manejar_usuario_registrado(numero, texto_usuario, estado_usuario, mensaje_completo):
    estado = estado_usuario.get(numero, {})
    print("estado..............",estado)

    if not estado.get("mensaje_inicial_enviado", False):

        # enviar_mensaje_texto(numero, "Ahora desde aqui vera los mensajes masivos que le enviaré")
        time.sleep(2)
        
        # Actualizar el estado con los IDs válidos y la fase del flujo
        estado.update({
            "opciones_validas": [],  # Listar los IDs de las gerencias
            "intentos": 0,
            "fase": "logeo_usuario",
            "esperando_respuesta": True,
            "mensaje_inicial_enviado": True
        })

    elif estado.get("esperando_respuesta", False):

        if estado.get("fase") == "ingresar_descripcion":
            # Directamente almacenar la descripción
            descripcion = texto_usuario
            enviar_mensaje_texto(numero, "Descripción recibida. Desea ingresar una imagen?\n\n1⃣ Sí\n2⃣ No")
            estado["fase"] = "ingresar_imagen_opcion"
            estado["opciones_validas"] = [1, 2]  # Opciones para elegir si desea ingresar una imagen
            estado["intentos"] = 0

        elif estado.get("fase") == "ingresar_imagen_opcion":
            if texto_usuario == "1":
                enviar_mensaje_texto(numero, "Por favor, ingresa la imagen en cualquier formato común (jpg, jpeg, png, etc.).")
                estado["fase"] = "esperando_imagen"
                estado["intentos"] = 0
            elif texto_usuario == "2":
                enviar_mensaje_texto(numero, "No se ingresará ninguna imagen. Continuamos.")
                estado_usuario.pop(numero, None)
            else:
                estado["intentos"] += 1
                if estado["intentos"] < 2:
                    enviar_mensaje_texto(numero, "Por favor, responde con 1 para 'Sí' o 2 para 'No'.")
                else:
                    enviar_mensaje_texto(numero, "Intentos fallidos. Regresando al inicio.")
                    time.sleep(2)
                    estado.clear()
                    manejar_usuario_registrado(numero, "", estado_usuario,"")

        elif estado.get("fase") == "esperando_imagen":
            print("estado_usuario.......................",estado_usuario)
            # Aquí deberías tener la lógica para manejar la recepción de imágenes
            mime_type =mensaje_completo['image']["mime_type"]
            # Check for different image MIME types
            if mime_type == "image/jpeg":
                recibir_img(mensaje_completo['image']["id"],numero)
                print("The file is a JPEG image.")
                enviar_mensaje_texto(numero, "Imagen recibida. Continuamos.")
                estado_usuario.pop(numero, None)
                print("estado_usuario.......................",estado_usuario)
            elif mime_type == "image/png":
                recibir_img(mensaje_completo['image']["id"],numero)
                print("The file is a PNG image.")
                enviar_mensaje_texto(numero, "Imagen recibida. Continuamos.")
                estado_usuario.pop(numero, None)
                print("estado_usuario.......................",estado_usuario)
            elif mime_type == "image/jpg":
                recibir_img(mensaje_completo['image']["id"],numero)
                print("The file is a JPG image.")
                enviar_mensaje_texto(numero, "Imagen recibida. Continuamos.")
                estado_usuario.pop(numero, None)
                print("estado_usuario.......................",estado_usuario)
            else:
                estado["intentos"] += 1
                if estado["intentos"] < 2:
                    enviar_mensaje_texto(numero, "El archivo recibido no es una imagen válida. Por favor, intenta nuevamente.")
                else:
                    enviar_mensaje_texto(numero, "Intentos fallidos. Regresando al inicio.")
                    time.sleep(2)
                    estado.clear()
                    manejar_usuario_registrado(numero, "", estado_usuario,"")

        else:
            try:
                seleccion = int(texto_usuario)
                if seleccion in estado.get("opciones_validas", []):


                    if estado.get("fase") == "mensaje_inicial_enviado":
                        print("mensaje_completo...........................",mensaje_completo)
                        # enviar_mensaje_texto(numero, "Has seleccionado el escenario de falla. Ingresar la descripción de su consulta:")
                
                    
                    elif (texto_usuario) in "buscar evento":
                        print("texto_usuario..........",texto_usuario)

                        enviar_mensaje_texto(numero, "El Evento Buscado es ")
                        estado["fase"] = "ingresar_descripcion"
                        estado["intentos"] = 0


                # else:
                #     estado["intentos"] += 1
                #     if estado["intentos"] < 2:
                #         enviar_mensaje_texto(numero, f"Por favor, responda con un número entre 1 y {len(estado['opciones_validas'])} para seleccionar su opción. ({estado['intentos']}/2 intentos)")
                #     else:
                #         enviar_mensaje_texto(numero, "Intentos fallidos. Regresando al inicio.")
                #         time.sleep(2)
                #         estado.clear()
                #         manejar_usuario_registrado(numero, "", estado_usuario,"")


            except ValueError:
                print("ValueError.................................")
                # estado["intentos"] += 1
                # if estado["intentos"] < 2:
                #     enviar_mensaje_texto(numero, f"Por favor, responda con un número entre 1 y {len(estado['opciones_validas'])} para seleccionar su opción. ({estado['intentos']}/2 intentos)")
                # else:
                #     enviar_mensaje_texto(numero, "Intentos fallidos. Regresando al inicio.")
                #     time.sleep(2)
                #     estado.clear()
                #     manejar_usuario_registrado(numero, "", estado_usuario,"")



            # estado_usuario[numero] = estado
