from confluent_kafka import Producer
import base64
import json

# Kafka configuration
KAFKA_BROKERS = 'KAFKA_BROKER_LIST'  # e.g., "broker-1:9092,broker-2:9092"
KAFKA_TOPIC = 'eth-block-details'

def kafka_publish(event, context):
    """Background Cloud Function to be triggered by Pub/Sub."""
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    file_info = json.loads(pubsub_message)
    
    # Initialize Kafka producer
    producer = Producer({'bootstrap.servers': KAFKA_BROKERS})
    
    # Publish message to Kafka
    producer.produce(KAFKA_TOPIC, str(file_info))
    producer.flush()
    
    print(f"Published to Kafka topic {KAFKA_TOPIC}")
