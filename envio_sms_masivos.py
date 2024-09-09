# from flask import Flask, request, jsonify
import http.client
import json
import re
import random
import string


from conexionbd import obtener_usuarios

from enviar_mensaje import enviar_template,enviar_mensaje_texto, enviar_mensaje  # Importar desde enviar_mensaje.py


import requests
import json




if __name__ == '__main__':

    usuarios_total = obtener_usuarios()

    print("usuarios_total...................................",usuarios_total)

    # enviar_template(numero, mensaje_texto)


