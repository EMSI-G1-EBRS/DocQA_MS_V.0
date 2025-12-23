import pika
import json
import threading
from typing import Dict, Any
from config import (
    RABBITMQ_HOST,
    RABBITMQ_PORT,
    RABBITMQ_USER,
    RABBITMQ_PASSWORD,
    RABBITMQ_QUEUE_INDEXER
)
from indexer_service import indexer_service

class RabbitMQConsumer:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.running = False
    
    def connect(self):
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
        parameters = pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=credentials,
            heartbeat=600,  # Keep connection alive during long processing
            blocked_connection_timeout=300
        )
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=RABBITMQ_QUEUE_INDEXER, durable=True)
    
    def process_message(self, ch, method, properties, body):
        try:
            message = json.loads(body)
            document_id = message.get("document_id")
            content = message.get("content")
            metadata = message.get("metadata", {})
            
            result = indexer_service.index_document(
                document_id=document_id,
                content=content,
                metadata=metadata
            )
            
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(f"Erreur lors de l'indexation: {str(e)}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def start_consuming(self):
        self.running = True
        while self.running:
            try:
                if not self.connection or self.connection.is_closed:
                    self.connect()
                
                self.channel.basic_qos(prefetch_count=1)
                self.channel.basic_consume(
                    queue=RABBITMQ_QUEUE_INDEXER,
                    on_message_callback=self.process_message
                )
                
                print("Indexer Consumer démarré, en attente de messages...", flush=True)
                self.channel.start_consuming()
            except Exception as e:
                print(f"Erreur consumer RabbitMQ: {str(e)}. Tentative de reconnexion dans 5s...", flush=True)
                import time
                time.sleep(5)
                try:
                    if self.connection and not self.connection.is_closed:
                        self.connection.close()
                except:
                    pass
                self.connection = None
    
    def stop_consuming(self):
        if self.channel and self.running:
            self.channel.stop_consuming()
            self.running = False
    
    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()

rabbitmq_consumer = RabbitMQConsumer()

