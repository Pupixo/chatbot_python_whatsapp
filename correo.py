# correo.py

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from conexionbd import obtener_credenciales  # Import the function from conexionbd.py

def enviar_correo(email, code):
    # Retrieve credentials using the function from conexionbd.py
    usuario, contraseña = obtener_credenciales()
    if not usuario or not contraseña:
        print("No se pudieron obtener las credenciales de la base de datos.")
        return

    # Ruta a la imagen descargada
    image_path = "OIP.jpg"  # Cambia esta ruta a donde tengas la imagen

    # Crear el mensaje de correo
    mensaje = MIMEMultipart()
    mensaje['To'] = email
    mensaje['Subject'] = "Código de validación"

    # Cuerpo del mensaje en formato HTML con imagen y código de validación
    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; text-align: center; background-color: #ffffff; margin: 0; padding: 0;">
        <table align="center" width="600" cellpadding="0" cellspacing="0" border="0" style="background-color: white; border-radius: 10px; margin: 0 auto;">
          <tr>
            <td style="padding: 0;">
              <img src="cid:myimage" alt="Claro" width="600" height="auto" style="display: block; border-radius: 10px 10px 0 0;">
            </td>
          </tr>
          <tr>
            <td style="padding: 20px;">
              <h1 style="color: #d62828; margin: 0;">Código de Validación</h1>
              <p style="font-size: 18px; color: #000; margin: 20px 0;">El código que debes ingresar para culminar el proceso de registro es:</p>
              <table align="center" cellpadding="0" cellspacing="0" border="0" style="background-color: #d62828; padding: 15px; border-radius: 10px;">
                <tr>
                  <td align="center" style="font-size: 36px; font-weight: bold; color: #ffffff;">
                    {code}
                  </td>
                </tr>
              </table>
              <p style="color: #000; margin-top: 30px;">Gracias por utilizar nuestros servicios.</p>
            </td>
          </tr>
        </table>
      </body>
    </html>
    """

    # Adjuntar el cuerpo HTML al mensaje
    mensaje.attach(MIMEText(html_body, 'html'))

    # Adjuntar la imagen utilizando MIMEImage
    with open(image_path, 'rb') as img_file:
        mime_image = MIMEImage(img_file.read())
        mime_image.add_header('Content-ID', '<myimage>')
        mime_image.add_header('Content-Disposition', 'inline', filename='OIP.jpg')
        mensaje.attach(mime_image)

    # Configuración del servidor SMTP para Gmail
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    mensaje['From'] = usuario

    # Conectar al servidor SMTP y enviar el correo
    try:
        servidor = smtplib.SMTP(smtp_server, smtp_port)
        servidor.starttls()  # Iniciar conexión TLS
        servidor.login(usuario, contraseña)
        servidor.send_message(mensaje)
        servidor.quit()
        print("Correo enviado con éxito.")
    except Exception as e:
        print(f"No se pudo enviar el correo. Error: {e}")
