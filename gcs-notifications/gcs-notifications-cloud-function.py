from google.cloud import storage
from kafka import KafkaProducer
import base64
import json
import os
import logging

# Initialize the GCS client
storage_client = storage.Client()

# Environment variables for Kafka configuration
KAFKA_BROKERS = os.getenv('KAFKA_BROKERS')  # e.g., "broker-1:9092,broker-2:9092"
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC')  # Your Kafka topic name

def process_gcs_file_and_publish_to_kafka(event, context):
    """Triggered by a Google Cloud Pub/Sub message."""
    try:
        # Decode the Pub/Sub message
        pubsub_message = base64.b64decode(event['data']).decode('utf-8')
        message_json = json.loads(pubsub_message)
        
        # Extract the GCS bucket name and file name from the Pub/Sub message
        bucket_name = message_json['bucket']
        file_name = message_json['name']
        
        # Read the file content from GCS
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        file_content = blob.download_as_bytes()
        file_data = json.loads(file_content)
        
        # Extract the block number or other relevant data from the file content
        block_number = file_data.get('number')  # Example key, adjust according to actual file structure
        
        # Initialize Kafka producer and publish message
        producer = KafkaProducer(bootstrap_servers=KAFKA_BROKERS)
        producer.send(KAFKA_TOPIC, value=str(block_number).encode('utf-8'))
        producer.flush()
        
        logging.info(f"Published block number {block_number} to Kafka topic {KAFKA_TOPIC}")
    except Exception as e:
        logging.error(f"Failed to process GCS file and publish to Kafka: {e}")