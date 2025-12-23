import pika
import json
from rag_engine.src.config import (
    RABBITMQ_HOST,
    RABBITMQ_PORT,
    RABBITMQ_USER,
    RABBITMQ_PASSWORD,
    RABBITMQ_QUEUE_INDEXER
)

def inspect_queue():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        credentials=credentials
    )
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    
    method_frame, header_frame, body = channel.basic_get(queue=RABBITMQ_QUEUE_INDEXER)
    
    if method_frame:
        print("Found message!")
        data = json.loads(body)
        document_id = data.get("document_id")
        content = data.get("content", "")
        print(f"Document ID: {document_id}")
        print(f"Content Length: {len(content)}")
        print(f"Content Preview: {content[:500]}...")
        channel.basic_nack(delivery_tag=method_frame.delivery_tag, requeue=True)
    else:
        print("No messages in queue")
    
    connection.close()

if __name__ == "__main__":
    inspect_queue()
