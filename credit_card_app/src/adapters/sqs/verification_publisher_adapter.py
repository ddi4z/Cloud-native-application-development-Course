print("Python está leyendo el archivo: verification_publisher_adapter.py")
import boto3
from botocore.exceptions import NoRegionError
import os
import json
from uuid import UUID
from src.domain.ports.verification_publisher_port import VerificationPublisherPort

class SQSVerificationPublisherAdapter(VerificationPublisherPort):
    def __init__(self):
        self.queue_url = os.environ["POLLING_QUEUE_URL"]  
        region = os.getenv("AWS_REGION", "us-east-1")
        endpoint = os.getenv("AWS_SQS_ENDPOINT")  
        try:
            self.sqs_client = boto3.client("sqs", region_name=region, endpoint_url=endpoint)
        except NoRegionError:
            self.sqs_client = boto3.client("sqs", region_name="us-east-1", endpoint_url=endpoint)

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

print("Python terminó de definir la clase SQSVerificationPublisherAdapter.")