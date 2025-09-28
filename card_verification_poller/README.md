# card_verification_poller

Aplicación serverless en AWS Lambda que realiza polling y verificación de tarjetas de crédito.  
El servicio se activa mediante eventos en SQS, consulta el estado en TrueNative y actualiza la tarjeta en credit_card_app.  
Finalmente, envía un mensaje de notificación a una cola de correos.

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

Este servicio se ejecuta únicamente en AWS.  
La función Lambda se integra con:

- SQS: recibe mensajes con información de la tarjeta.  
- TrueNative: API externa de verificación.  
- credit_card_app: microservicio interno donde se actualiza el estado de la tarjeta.  
- Cola de correos (SQS): destino para notificar al usuario.  

Variables de entorno obligatorias:

- `CREDIT_CARD_APP_URL` → URL base del microservicio de tarjetas de crédito.  
- `TRUENATIVE_SERVICE_URL` → URL base del servicio TrueNative.  
- `TRUENATIVE_SECRET_TOKEN` → Token de autenticación para TrueNative.  
- `EMAIL_QUEUE_URL` → URL de la cola SQS donde se envían las notificaciones.  
- `AWS_ENDPOINT_URL` → Endpoint de AWS (útil para LocalStack o pruebas locales).  
- `MAX_POLLING_RETRIES` → Número máximo de intentos de polling (default: `5`).  
- `POLLING_DELAY_SECONDS` → Tiempo de espera entre intentos (default: `5`).  

El despliegue puede realizarse con AWS SAM, Serverless Framework o Terraform, según la infraestructura definida. La Lambda se configura para ser disparada por la cola de entrada SQS.

### Uso

1. Se recibe el mensaje desde la cola de entrada.  
2. Se validan los campos requeridos: `cardId`, `ruv` y `userEmail`.  
3. Se inicia el polling contra TrueNative hasta obtener un estado final:  
   - Respuesta 200 con estado → se finaliza el polling.  
   - Respuesta 202 → se reintenta hasta agotar `MAX_POLLING_RETRIES`.  
   - Respuesta distinta → se considera error.  
4. Se actualiza el estado en `credit_card_app`.  
5. Se publica un mensaje de notificación en la cola de correos. 

## Pruebas

Pruebas recomendadas para validar el correcto funcionamiento:

- Mensaje SQS malformado: debe ignorarse.  
- Polling exitoso con tarjeta aprobada.  
- Polling exitoso con tarjeta rechazada.  
- TrueNative responde 202 varias veces: se realizan reintentos hasta agotar el máximo.  
- Error en `credit_card_app`: se registra y propaga.  
- Notificación enviada correctamente a la cola de correos.  

Las pruebas pueden implementarse con `pytest` y mocks de SQS y TrueNative.

## Autor
Jorge Paternina – [j.paterninam@uniandes.edu.co](mailto:j.paterninam@uniandes.edu.co)