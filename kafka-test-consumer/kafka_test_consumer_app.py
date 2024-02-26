from kafka import KafkaConsumer

# Create a Kafka consumer
consumer = KafkaConsumer(
    'eth-block-details',
    bootstrap_servers=['34.174.40.76:9094'],
    auto_offset_reset='earliest',  # Start reading at the earliest message
    group_id='test-group')  # Use a unique group ID

# Read and print messages from the topic
for message in consumer:
    print("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                         message.offset, message.key,
                                         message.value.decode('utf-8')))