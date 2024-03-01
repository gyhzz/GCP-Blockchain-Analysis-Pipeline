from pyspark.sql import SparkSession
from pyspark.sql.functions import col, expr

def main():
    spark = SparkSession.builder \
        .appName("Ethereum Block Processor") \
        .getOrCreate()

    kafkaBootstrapServers = "34.174.40.76:9094"
    kafkaBootstrapServers = "kafka-service-cluster-kafka-bootstrap.kafka.svc:9092"  # Kafka internal server in GKE

    # Subscribe to the input Kafka topic
    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafkaBootstrapServers) \
        .option("subscribe", "eth_block_details") \
        .load()

    # # Assuming the Kafka message value is the block number in string format
    # # Here you can define transformations, such as enriching the Ethereum block data
    # transformedDf = df.selectExpr("CAST(value AS STRING) as block_number") \
    #                   .selectExpr("block_number", "transformBlockData(block_number) as enriched_data")

    # Write the transformed stream to another Kafka topic
    query = df \
        .selectExpr("CAST(block_number AS STRING) AS key", "CAST(ethereum_block AS STRING) AS value") \
        .writeStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafkaBootstrapServers) \
        .option("topic", "eth-block-number") \
        .option("checkpointLocation", "/path/to/checkpoint/dir") \
        .start()

    query.awaitTermination()

# def transformBlockData(blockNumber):
#     # Placeholder for a function that enriches block data from the Ethereum network
#     # This could involve API calls to Ethereum nodes or services to fetch additional block details
#     return f"Enriched data for block {blockNumber}"

if __name__ == "__main__":
    main()