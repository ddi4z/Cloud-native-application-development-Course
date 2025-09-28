import os
import json
import time
import httpx
import boto3
from enum import Enum

# 1. CONFIGURACIÓN Y CLIENTES
CREDIT_CARD_APP_URL = os.getenv("CREDIT_CARD_APP_URL")
TRUENATIVE_SERVICE_URL = os.getenv("TRUENATIVE_SERVICE_URL")
TRUENATIVE_SECRET_TOKEN = os.getenv("TRUENATIVE_SECRET_TOKEN")
EMAIL_QUEUE_URL = os.getenv("EMAIL_QUEUE_URL")
AWS_ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL")

MAX_POLLING_RETRIES = int(os.getenv("MAX_POLLING_RETRIES", "5"))
POLLING_DELAY_SECONDS = int(os.getenv("POLLING_DELAY_SECONDS", "5"))

if not all([CREDIT_CARD_APP_URL, TRUENATIVE_SERVICE_URL, TRUENATIVE_SECRET_TOKEN, EMAIL_QUEUE_URL]):
    raise ValueError("Una o más variables de entorno críticas no están configuradas.")
# Inicializa el cliente de SQS
sqs_client = boto3.client('sqs', endpoint_url=AWS_ENDPOINT_URL)

# 2. ENUMS
class CreditCardStatus(str, Enum):
    """Enum para el estado de la tarjeta."""
    REJECTED = "RECHAZADA"
    APPROVED = "APROBADA"

# 3. FUNCIONES AUXILIARES
def update_card_status_via_api(card_id: str, new_status: CreditCardStatus):
    """Actualiza el estado de la tarjeta llamando a la API de credit_card_app."""
    base = CREDIT_CARD_APP_URL.rstrip("/") 
    update_url = f"{base}/credit-cards/internal/cards/{card_id}/status"
    payload = {"status": new_status.value}
    
    try:
        with httpx.Client() as client:
            response = client.patch(update_url, json=payload, timeout=10.0)
            response.raise_for_status() 
            print(f"Tarjeta {card_id} actualizada al estado {new_status.value} via API.")
            
    except httpx.HTTPStatusError as e:
        print(f"Error al actualizar estado vía API para tarjeta {card_id}: {e.response.status_code} - {e.response.text}")
        raise
    except httpx.RequestError as e:
        print(f"Error de conexión al intentar actualizar estado para tarjeta {card_id}: {e}")
        raise

def publish_notification_message(card_id: str, user_email: str, status: CreditCardStatus):
    """Publica un mensaje en la cola de emails con el resultado final."""
    message_body = {
        "card_id": card_id,
        "user_email": user_email,
        "verification_status": status.value
    }
    sqs_client.send_message(
        QueueUrl=EMAIL_QUEUE_URL,
        MessageBody=json.dumps(message_body)
    )
    print(f"Mensaje de notificación para {user_email} enviado a la cola de emails.")

# 4. HANDLER PRINCIPAL DE LAMBDA
def lambda_handler(event, context):
    """
    Función principal que se activa con SQS, realiza el polling y dispara la actualización vía API.
    """
    for record in event.get('Records', []):
        try:
            message_body = json.loads(record.get('body', '{}'))
            card_id = message_body.get('cardId')
            ruv = message_body.get('ruv')
            user_email = message_body.get('userEmail')

            if not all([card_id, ruv, user_email]):
                print(f"Mensaje SQS malformado, saltando: {message_body}")
                continue

            print(f"Iniciando polling para tarjeta {card_id} (RUV: {ruv})")
            
            final_status_str = "RECHAZADA"
            for attempt in range(MAX_POLLING_RETRIES):
                with httpx.Client() as client:
                    response = client.get(
                        f"{TRUENATIVE_SERVICE_URL}/native/cards/{ruv}",
                        headers={"Authorization": f"Bearer {TRUENATIVE_SECRET_TOKEN}"},
                        timeout=10.0
                    )
                
                if response.status_code == 200:
                    final_status_str = response.json().get("status", "RECHAZADA")
                    print(f"Polling exitoso. Estado final de TrueNative: {final_status_str}")
                    break
                
                if response.status_code != 202:
                    print(f"TrueNative respondió con un error inesperado ({response.status_code}). Finalizando polling.")
                    break

                print(f"Intento {attempt + 1}/{MAX_POLLING_RETRIES}: Verificación pendiente. Esperando {POLLING_DELAY_SECONDS}s...")
                time.sleep(POLLING_DELAY_SECONDS)
            
            final_status = CreditCardStatus.APPROVED if final_status_str == "APROBADA" else CreditCardStatus.REJECTED
            
            update_card_status_via_api(card_id, final_status)
            publish_notification_message(card_id, user_email, final_status)

        except Exception as e:
            print(f"ERROR: Fallo catastrófico procesando el mensaje. Error: {e}")
            raise e
            
    return {'statusCode': 200, 'body': json.dumps('Procesamiento de mensajes completado.')}