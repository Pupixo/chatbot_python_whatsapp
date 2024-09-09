from flask import Flask, request, jsonify
import http.client
import json
import re
import random
import string


from conexionbd import obtener_usuarios
from correo import enviar_correo  # Importa la función de envío de correo
from gerencia import manejar_usuario_registrado  # Importar la función desde gerencia.py
from enviar_mensaje import enviar_mensaje_texto, enviar_mensaje  # Importar desde enviar_mensaje.py


import requests
import json




if __name__ == '__main__':

    usuarios_total = obtener_usuarios()

    print("usuarios_total...................................",usuarios_total)


