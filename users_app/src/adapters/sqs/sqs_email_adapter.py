import json
import logging
import boto3


from src.errors import IntegrationError
from src.domain.models.user import User
from src.domain.ports.message_queue_port import MessageQueuePort


class SQSMessageQueueAdapter(MessageQueuePort):

    def __init__(self, queue_url: str):
        self.sqs_client = boto3.client("sqs")
        self.queue_url = queue_url

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
