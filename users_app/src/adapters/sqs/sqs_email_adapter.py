import json
import logging
import os

import boto3

from src.domain.models.user import User
from src.domain.ports.message_queue_port import MessageQueuePort
from src.errors import IntegrationError


class SQSMessageQueueAdapter(MessageQueuePort):

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

    def send_message(self, userDto: User) -> None:
        """Send a message to the SQS queue."""
        message = {
            "to": userDto.email,
            "subject": "Resultado de verificación de identidad",
            "body": f"Hola {userDto.name}, tu estado final es {userDto.status}. RUV: {userDto.ruv}",
        }
        response = self.sqs_client.send_message(
            QueueUrl=self.queue_url, MessageBody=json.dumps(message)
        )
        logging.info(f"Message sent to SQS: {message}, Response: {response}")
        if response.get("ResponseMetadata", {}).get("HTTPStatusCode") != 200:
            logging.error(f"Failed to send message to SQS: {response}")
            raise IntegrationError("Failed to send message to SQS")
