from flask import Flask,request,jsonify,render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import json

app = Flask(__name__)


# Configuración de la base de datos SQLITE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///metapython.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#Modelo de la tabla log
class Log(db.Model):
    id= db.Column(db.Integer,primary_key=True)
    fecha_y_hora = db.Column(db.DateTime,default=datetime.now(timezone.utc))
    text=db.Column(db.TEXT)

#CREAR UNA TABLA SI NO EXISTE
with app.app_context():
    db.create_all()

    # prueba1 = Log(text='Mensaje de Prueba 1')
    # prueba2 = Log(text='Mensaje de Prueba 2')

    # db.session.add(prueba1)
    # db.session.add(prueba2)
    # db.session.commit()

def ordenar_por_fecha_y_hora(registros):
    return sorted(registros, key=lambda x: x.fecha_y_hora,reverse=True)


@app.route('/')
def index():
    #obtener todos los registros
    registros= Log.query.all()
    registros_ordenados =ordenar_por_fecha_y_hora(registros)
    return render_template('index.html',registros=registros_ordenados)


mensajes_log = []
#Funcion para insertar mensajes y guardalos en la db
def agregar_mensajes_log(texto):
    mensajes_log.append(texto)
    # guardar en db
    nuevo_registro = Log(text=texto)
    db.session.add(nuevo_registro)
    db.session.commit()



#

#token de verificación para la configiración
TOKEN_NOCBOT="NOCBOTCODE"


@app.route('/webhook',methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        challenge = verificar_token(request)
        return challenge
    elif request.method == 'POST':
        reponse = recibir_mensajes(request)
        return reponse

def verificar_token(req):
    token = req.args.get('hub.verify_token')
    challenge = req.args.get('hub.challenge')

    if challenge and token ==TOKEN_NOCBOT:
        return challenge
    else:
        return jsonify({'error':'Token Invalido'}),401

def recibir_mensajes(req):
    req = request.get_json()
    agregar_mensajes_log(req)
    return jsonify({'message':'EVENT_RECEIVED'})

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80,debug=True)