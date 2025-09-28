import os
import json
import httpx
import boto3
from enum import Enum

# Configuración y clientes
CREDIT_CARD_APP_URL = os.getenv("CREDIT_CARD_APP_URL")
TRUENATIVE_SERVICE_URL = os.getenv("TRUENATIVE_SERVICE_URL")
TRUENATIVE_SECRET_TOKEN = os.getenv("TRUENATIVE_SECRET_TOKEN")
EMAIL_QUEUE_URL = os.getenv("EMAIL_QUEUE_URL")
POLLING_QUEUE_URL = os.getenv("POLLING_QUEUE_URL")  
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL") 

# Para reintentos / encolamiento con delay
BASE_DELAY_SECONDS = int(os.getenv("BASE_DELAY_SECONDS", "5"))      # 1er reintento
MAX_DELAY_SECONDS = int(os.getenv("MAX_DELAY_SECONDS", "15"))       # techo por mensaje
MAX_RETRY_COUNT   = int(os.getenv("MAX_RETRY_COUNT", "5"))         # máximo reintentos

if not all([CREDIT_CARD_APP_URL, TRUENATIVE_SERVICE_URL, TRUENATIVE_SECRET_TOKEN, EMAIL_QUEUE_URL, POLLING_QUEUE_URL]):
    raise ValueError("Variables de entorno incompletas para el poller.")

sqs_client = boto3.client("sqs", region_name=AWS_REGION, endpoint_url=AWS_ENDPOINT_URL)

class CreditCardStatus(str, Enum):
    REJECTED = "RECHAZADA"
    APPROVED = "APROBADA"

# Funciones auxiliares
def _httpx_client():
    # Un único cliente por request 
    return httpx.Client(timeout=10.0)

def _update_card_status_via_api(card_id: str, new_status: CreditCardStatus) -> None:
    base = CREDIT_CARD_APP_URL.rstrip("/")
    update_url = f"{base}/credit-cards/internal/cards/{card_id}/status"
    payload = {"status": new_status.value}
    with _httpx_client() as client:
        r = client.patch(update_url, json=payload)
        r.raise_for_status()

def _publish_email(card_id: str, user_email: str, status: CreditCardStatus) -> None:
    msg = {"card_id": card_id, "user_email": user_email, "verification_status": status.value}
    sqs_client.send_message(QueueUrl=EMAIL_QUEUE_URL, MessageBody=json.dumps(msg))

def _calc_delay_seconds(retry_count: int) -> int:
    # backoff exponencial con techo
    delay = BASE_DELAY_SECONDS * (2 ** retry_count)
    return min(delay, MAX_DELAY_SECONDS)

def _requeue_for_later(body: dict) -> None:
    retry_count = int(body.get("retryCount", 0)) + 1
    body["retryCount"] = retry_count
    if retry_count > MAX_RETRY_COUNT:
        # Dejamos que el redrive policy/DLQ se encargue si también falla allí,
        # reencolamos sin delay para que la política haga su trabajo.
        sqs_client.send_message(QueueUrl=POLLING_QUEUE_URL, MessageBody=json.dumps(body))
        return
    delay = _calc_delay_seconds(retry_count)
    sqs_client.send_message(
        QueueUrl=POLLING_QUEUE_URL,
        MessageBody=json.dumps(body),
        DelaySeconds=delay
    )

def _query_truenative_status(ruv: str) -> httpx.Response:
    with _httpx_client() as client:
        return client.get(
            f"{TRUENATIVE_SERVICE_URL}/native/cards/{ruv}",
            headers={"Authorization": f"Bearer {TRUENATIVE_SECRET_TOKEN}"}
        )

# Lambda function handler
def lambda_handler(event, context):
    """
    - Procesa un solo intento por mensaje.
    - Si TrueNative responde 202: reencola con DelaySeconds y termina (sin sleep).
    - Si 200: actualiza estado en credit_card_app y publica mensaje de email.
    - Si error inesperado: lanzamos excepción para que SQS+Lambda reintenten / DLQ.
    """
    for record in event.get("Records", []):
        body_raw = record.get("body", "{}")
        try:
            body = json.loads(body_raw)
        except Exception:
            print(f"Mensaje malformado: {body_raw}")
            # Dejar que falle para que el mensaje vaya a reintento/DLQ
            raise

        card_id    = body.get("cardId")
        ruv        = body.get("ruv")
        user_email = body.get("userEmail")
        retry_cnt  = int(body.get("retryCount", 0))

        if not all([card_id, ruv, user_email]):
            print(f"Mensaje sin campos requeridos: {body}")
            raise ValueError("Mensaje SQS malformado")

        print(f"[Attempt {retry_cnt}] Consultando TrueNative para RUV={ruv} (card={card_id})")

        try:
            resp = _query_truenative_status(ruv)

            if resp.status_code == 202:
                # Aún en proceso: reencolar y finalizar ejecución.
                print("TrueNative=202 (pendiente). Reencolando con backoff…")
                _requeue_for_later(body)
                continue

            if resp.status_code == 200:
                status_str = resp.json().get("status", "RECHAZADA")
                final_status = CreditCardStatus.APPROVED if status_str == "APROBADA" else CreditCardStatus.REJECTED

                # Actualiza en credit_card_app (endpoint interno) y envía email
                _update_card_status_via_api(card_id, final_status)
                _publish_email(card_id, user_email, final_status)
                print(f"Estado final {final_status.value}: actualizado y notificado.")
                continue

            print(f"Respuesta inesperada de TrueNative: {resp.status_code} - {resp.text}")
            raise RuntimeError(f"TrueNative error {resp.status_code}")

        except Exception as e:
            # Lanzar excepción permite reintentos automáticos / DLQ
            print(f"ERROR procesando mensaje {body}: {e}")
            raise

    return {"statusCode": 200, "body": json.dumps("OK")}