import pymssql

def obtener_conexion():
    server = 'chatwsp.database.windows.net'
    database = 'chatbot'
    username = 'wspbot'
    password = 'B@t264as'

    try:
        conn = pymssql.connect(server=server, user=username, password=password, database=database)
        return conn
    except pymssql.Error as e:
        print("Error al conectar a la base de datos:", e)
        return None

def obtener_mensaje_por_id(id):
    conn = obtener_conexion()
    if conn is None:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT formulario FROM Preguntas WHERE ID = %s", (id,))
        row = cursor.fetchone()
        return row[0] if row else None
    except pymssql.Error as e:
        print("Error al ejecutar la consulta:", e)
        return None
    finally:
        conn.close()

def obtener_alternativas_por_id_pregunta(id_pregunta):
    conn = obtener_conexion()
    if conn is None:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT alternativas FROM alternativas_preguntas WHERE ID_preguntas = %s", (id_pregunta,))
        rows = cursor.fetchall()
        return [row[0] for row in rows] if rows else []
    except pymssql.Error as e:
        print("Error al ejecutar la consulta:", e)
        return []
    finally:
        conn.close()

def obtener_alternativa_por_id(id):
    conn = obtener_conexion()
    if conn is None:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT alternativas FROM alternativas_preguntas WHERE ID = %s", (id,))
        row = cursor.fetchone()
        return row[0] if row else None
    except pymssql.Error as e:
        print("Error al obtener alternativa por ID:", e)
        return None
    finally:
        conn.close()

def verificar_usuario_registrado(numero):
    conn = obtener_conexion()
    if conn is None:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT celular FROM usuario WHERE celular = %s", (numero,))
        row = cursor.fetchone()
        return row is not None
    except pymssql.Error as e:
        print("Error al verificar usuario registrado:", e)
        return False
    finally:
        conn.close()

def registrar_usuario(data):
    conn = obtener_conexion()
    if conn is None:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO usuario (celular, correo, nombre, apellido, dni, codigo_usuario, canal_ventas, site_reportado, id_perfil, fecha_registro)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, GETDATE())
        """, (
            data["celular"],
            data["correo"],
            data["nombre"],
            data["apellido"],
            data["dni"],
            data["codigo_usuario"],
            data["canal_ventas"],
            data["site_reportado"],
            data["id_perfil"]
        ))
        conn.commit()
        return True
    except pymssql.Error as e:
        print("Error al registrar el usuario:", e)
        return False
    finally:
        conn.close()
def obtener_credenciales():
    conn = obtener_conexion()
    if conn is None:
        return (None, None)
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT usu, contr FROM basecorreo WHERE ID = 1")  # Adjust query as needed
        row = cursor.fetchone()
        return row if row else (None, None)
    except pymssql.Error as e:
        print("Error al obtener credenciales de la base de datos:", e)
        return (None, None)
    finally:
        conn.close()