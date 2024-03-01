from pyspark.sql import SparkSession

def main():
    spark = SparkSession.builder \
        .appName("Simple App") \
        .getOrCreate()

    data = [("Java", 20000), ("Python", 100000), ("Scala", 3000)]
    df = spark.createDataFrame(data, ["Language", "Users"])

    df.show(1)

    spark.stop()

if __name__ == "__main__":
    main()