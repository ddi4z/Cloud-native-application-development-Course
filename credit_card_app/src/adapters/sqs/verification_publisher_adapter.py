import boto3
import os
import json
from uuid import UUID
from src.domain.ports.verification_publisher_port import VerificationPublisherPort

class SQSVerificationPublisherAdapter(VerificationPublisherPort):
    def __init__(self):
        """
        Inicializa el cliente de SQS.
        Se conecta a LocalStack si la variable de entorno AWS_ENDPOINT_URL está definida.
        De lo contrario, se conecta a la AWS real.
        """
        # 1. Lee la URL del endpoint. Será None si la variable no existe (en producción).
        endpoint_url = os.getenv("AWS_ENDPOINT_URL")
        # 2. Lee la región, con un valor por defecto si no está definida.
        region = os.getenv("AWS_REGION", "us-east-1")
        # 3. Inicializa el cliente de boto3 de forma directa y limpia.
        self.sqs_client = boto3.client(
            "sqs", 
            region_name=region, 
            endpoint_url=endpoint_url
        )
        # 4. Obtiene la URL de la cola y falla de forma controlada si no existe.
        self.queue_url = os.getenv("POLLING_QUEUE_URL")
        if not self.queue_url:
            raise ValueError("La variable de entorno POLLING_QUEUE_URL es obligatoria.")

    def publish_for_polling(self, card_id: UUID, ruv: str, user_email: str) -> None:
        message_body = {
            "cardId": str(card_id),
            "ruv": ruv,
            "userEmail": user_email,
            "retryCount": 0
        }
        self.sqs_client.send_message(
            QueueUrl=self.queue_url,
            MessageBody=json.dumps(message_body)
        )