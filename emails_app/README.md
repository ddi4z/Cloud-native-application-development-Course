# emails_app

Este servicio se despliega en AWS como una función Lambda conectada a una cola SQS.  
Cuando llega un mensaje a la cola, la Lambda lo procesa y envía un correo electrónico utilizando un servidor SMTP.

Variables de entorno requeridas:

- `SMTP_USER` → usuario de la cuenta SMTP que envía los correos.  
- `SMTP_PASS` → contraseña de la cuenta SMTP.  
- `SMTP_HOST` → host del servidor SMTP (por defecto: smtp.gmail.com).  
- `SMTP_PORT` → puerto del servidor SMTP (por defecto: 587).  

La Lambda debe estar configurada con permisos adecuados para leer mensajes desde la cola SQS.

## Índice

1. [Estructura](#estructura)  
2. [Ejecución](#ejecución)  
3. [Uso](#uso)  
4. [Pruebas](#pruebas)  
5. [Autor](#autor)  

---

## Estructura

La aplicación se organiza de la siguiente manera:

```
.
├── src/
│ └── main.py # Lógica principal de la función Lambda
├── requirements.txt # Dependencias si se usa pip
└── README.md # Documentación del proyecto
```

---

## Ejecución

Servicio desplegado en AWS como función Lambda con disparador SQS. Al llegar un mensaje a la cola, la Lambda lo procesa y envía un correo vía SMTP.

Variables de entorno requeridas:

- `SMTP_USER`: usuario remitente en el servidor SMTP.  
- `SMTP_PASS`: contraseña o token del usuario SMTP.  
- `SMTP_HOST`: host del servidor SMTP (default: `smtp.gmail.com`).  
- `SMTP_PORT`: puerto del servidor SMTP (default: `587`; usa STARTTLS).

Requisitos de infraestructura:

- La Lambda debe tener configurado como trigger la cola SQS de entrada.  
- La Lambda debe poder salir a Internet (NAT/VPC o egress permitido) para conectarse al `SMTP_HOST`.  
- Registrar logs en CloudWatch ya que la app reporta éxito/errores mediante `logging`.


### Uso

Formato de mensaje esperado en la cola SQS (HTML en `body`):

```json
{
  "subject": "Asunto del correo",
  "body": "<p>Contenido en HTML</p>",
  "to": "destinatario@correo.com"
}
```
También se acepta la clave `emailTo` en lugar de `to`.

### Flujo de ejecución

1. Se recibe un mensaje desde la cola SQS.  
2. Se validan los campos `subject`, `body` y `to` (o `emailTo`).  
3. Se construye el `EmailMessage` con contenido HTML.  
4. Se abre conexión SMTP (`SMTP_HOST:SMTP_PORT`); si el puerto es `587`, se negocia STARTTLS.  
5. Se autentica con `SMTP_USER` y `SMTP_PASS`.  
6. Se envía el mensaje al destinatario.  
7. Se registran logs de éxito o error.


## Pruebas

Pruebas recomendadas para validar el funcionamiento extremo a extremo y de errores - no se incluyen en el código, se sugieren pruebas:

- Mensaje válido en SQS → se envía el correo y se registra `Email enviado a: <to>`.  
- Mensaje sin `subject`/`body`/`to|emailTo` → se descarta y se registra `Mensaje inválido`.  
- Credenciales inválidas (`SMTP_USER`/`SMTP_PASS`) → se captura excepción de autenticación y se registra el error.  
- Host o puerto SMTP incorrectos → error de conexión/timeout registrado mediante `logger.exception`.  
- Verificar ruta STARTTLS (puerto `587`) → el envío se realiza tras `starttls`.  
- Cuerpo HTML preservado → el correo recibido contiene el HTML esperado.  

Las pruebas pueden implementarse con `pytest`, usando mocks del cliente SMTP (`smtplib.SMTP`) y de eventos SQS para simular entradas válidas e inválidas.

## Autor
Daniel Felipe Díaz Moreno