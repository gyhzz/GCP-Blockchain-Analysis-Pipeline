from google.cloud import storage
from kafka import KafkaProducer
import base64
import json
# Testing
from google.oauth2 import service_account


# Initialize the GCS client
key_path = "C:\\Users\\Admin\\Desktop\\github\\blockchain-analysis-pipeline\\storage-object-creator-key.json"
credentials = service_account.Credentials.from_service_account_file(key_path)
storage_client = storage.Client(credentials=credentials)

# Kafka configuration
KAFKA_BROKERS = '34.174.40.76:9094'  # Use the external IP and port for Kafka
KAFKA_TOPIC = 'eth-block-details'

def process_gcs_file_and_publish_to_kafka(event, context):
    """Triggered by a Google Cloud Pub/Sub message."""
    try:
        # Decode the Pub/Sub message
        pubsub_message = base64.b64decode(event['data']).decode('utf-8')
        message_json = json.loads(pubsub_message)
        print(message_json)
        
        # Extract the GCS bucket name and file name from the Pub/Sub message
        bucket_name = message_json['bucket']
        file_name = message_json['name']
        print(f"Bucket name:{bucket_name}, file name: {file_name}")
        
        # Read the file content from GCS
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        file_content = blob.download_as_bytes()
        file_data = json.loads(file_content)
        print(file_data)
        
        # Extract the block number or other relevant data from the file content
        block_number = int(file_data.get('number'), 16)  # Adjust according to actual file structure
        print(block_number)
        
        # Initialize Kafka producer
        producer = KafkaProducer(bootstrap_servers=KAFKA_BROKERS,
                                 security_protocol='PLAINTEXT')  # Use 'SASL_PLAINTEXT' or 'SASL_SSL' if your Kafka is secured
        
        # Publish message to Kafka
        producer.send(KAFKA_TOPIC, value=str(block_number).encode('utf-8'))
        producer.flush()
        
        print(f"Published block number {block_number} to Kafka topic {KAFKA_TOPIC}")
    except Exception as e:
        print(f"Failed to process GCS file and publish to Kafka: {e}")


# For testing
if __name__ == '__main__':
    # Simulate a Pub/Sub event
    simulated_event = {
        'data': base64.b64encode(b'{"bucket":"blockchain-data-lake","name":"ethereum_blocks/20240226/block19308031"}')
    }
    simulated_context = None
    
    # Call the main function
    process_gcs_file_and_publish_to_kafka(simulated_event, simulated_context)