from pyspark.sql import SparkSession
from pyspark.sql.functions import concat, lit, col

if __name__ == "__main__":
    # Initialize a SparkSession
    spark = SparkSession \
        .builder \
        .appName("KafkaEthBlockDetailsProcessor") \
        .getOrCreate()

    # Adjust the log level to reduce verbosity
    spark.sparkContext.setLogLevel("WARN")

    # Define Kafka parameters
    kafka_bootstrap_servers = '34.174.40.76:9094'
    subscribe_topic = 'eth-block-details'
    publish_topic = 'eth-block-number'
    group_id = 'main-pipe'

    # Read data from the input Kafka topic
    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
        .option("subscribe", subscribe_topic) \
        .option("startingOffsets", "earliest") \
        .option("kafka.group.id", group_id) \
        .load()

    # Assuming the value in the Kafka topic is in string format
    # Perform a simple transformation: append some strings to the value
    transformed_df = df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)") \
        .withColumn("value", concat(col("value"), lit(" - processed")))

    # Write the transformed data to the output Kafka topic
    query = transformed_df \
        .selectExpr("CAST(key AS STRING) AS key", "CAST(value AS STRING) AS value") \
        .writeStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
        .option("topic", publish_topic) \
        .option("checkpointLocation", "/path/to/checkpoint/dir") \
        .start()

    query.awaitTermination()
