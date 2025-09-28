import os
import json
import time
import boto3


LOCALSTACK_URL = "http://127.0.0.1:55586"        # puerto de LocalStack
CREDIT_CARD_APP_URL = "http://127.0.0.1:59370"   # puerto de credit-card-app
TRUENATIVE_SERVICE_URL = "http://127.0.0.1:59390"
TRUENATIVE_SECRET = "your-actual-secure-token"

os.environ['AWS_ENDPOINT_URL'] = LOCALSTACK_URL
os.environ['AWS_ACCESS_KEY_ID'] = 'test'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'test'
os.environ['AWS_REGION'] = 'us-east-1'

os.environ['POLLING_QUEUE_URL'] = f"{LOCALSTACK_URL}/000000000000/credit-card-verification-queue"
os.environ['EMAIL_QUEUE_URL']   = f"{LOCALSTACK_URL}/000000000000/email-notification-queue"

os.environ['CREDIT_CARD_APP_URL']     = CREDIT_CARD_APP_URL
os.environ['TRUENATIVE_SERVICE_URL']  = TRUENATIVE_SERVICE_URL
os.environ['TRUENATIVE_SECRET_TOKEN'] = TRUENATIVE_SECRET

from card_verification_poller.src.main import lambda_handler

QUEUE_URL = os.environ['POLLING_QUEUE_URL']
sqs_client = boto3.client('sqs', endpoint_url=os.environ['AWS_ENDPOINT_URL'])

print("🚀 Worker local iniciado. Escuchando mensajes en la cola SQS de LocalStack...")
print(f"Cola de Verificación: {QUEUE_URL}")

while True:
    try:
        response = sqs_client.receive_message(
            QueueUrl=QUEUE_URL,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=10,
            MessageAttributeNames=['All'],
            AttributeNames=['All'],
        )

        if 'Messages' in response:
            message = response['Messages'][0]
            receipt_handle = message['ReceiptHandle']

            raw_body = message.get('Body', '') 
            lambda_event = {
                'Records': [{
                    'messageId': message.get('MessageId'),
                    'receiptHandle': receipt_handle,
                    'body': raw_body,  
                    'attributes': message.get('Attributes', {}),
                    'messageAttributes': message.get('MessageAttributes', {}),
                    'md5OfBody': message.get('MD5OfBody', ''),
                    'eventSource': 'aws:sqs',
                    'eventSourceARN': 'arn:aws:sqs:us-east-1:000000000000:credit-card-verification-queue',
                    'awsRegion': os.environ.get('AWS_REGION', 'us-east-1'),
                }]
            }
            print("\n📬 Mensaje recibido. Invocando handler del worker...")
            try:
                print("   body JSON:", json.loads(raw_body))
            except Exception:
                print("   body (texto):", raw_body)

            lambda_handler(lambda_event, None)

            sqs_client.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=receipt_handle)
            print("✅ Mensaje procesado y eliminado de la cola.")
    except KeyboardInterrupt:
        print("\nDeteniendo worker local.")
        break
    except Exception as e:
        print(f"Error procesando el mensaje: {e}")
        time.sleep(5)
