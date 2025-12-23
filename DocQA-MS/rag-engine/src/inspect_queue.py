import pika
import json
from config import (
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
        content = data.get("content", "")
        print(f"Content Length: {len(content)}")
        
        try:
            from chunker import chunker
            print("Running chunker on content...")
            
            tokens = chunker.tokenizer.encode(content, add_special_tokens=False)
            print(f"Total tokens from tokenizer: {len(tokens)}")

            chunk_size = chunker.chunk_size
            chunk_overlap = chunker.chunk_overlap
            print(f"Chunk Size: {chunk_size}, Overlap: {chunk_overlap}")
            
            start = 0
            while start < len(tokens):
                end = min(start + chunk_size, len(tokens))
                print(f"Start: {start}, End: {end}, Next Start: {end - chunk_overlap}")
                start = end - chunk_overlap
                if start > 20000: # Safety break
                    print("Loop going too long!")
                    break
                    
        except ImportError:
            print("Could not import chunker")
            
        channel.basic_nack(delivery_tag=method_frame.delivery_tag, requeue=True)
    else:
        print("No messages in queue")
    
    connection.close()

if __name__ == "__main__":
    inspect_queue()
