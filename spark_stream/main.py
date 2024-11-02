import logging

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import ByteType, StringType, StructField, StructType


# def get_logger(name: str, log_level):
#     logger = logging.getLogger(name)
#     logger.setLevel(logging.DEBUG)
#
#     handler = logging.StreamHandler()
#     handler.setLevel(log_level)
#
#     logger.addHandler(handler)
#
#     return logger


spark = (
    SparkSession.builder.appName("temp_stream")
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.1")
    .getOrCreate()
)

kafka_broker = "kafka:29092"


listener_df = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", kafka_broker)
    .option("subscribe", "sensor_queue")
    .option("startingOffsets", "earliest")
    .load()
)


transform_df = listener_df.selectExpr(
    "CAST(key AS STRING)", "CAST(value AS STRING)", "timestamp"
)

transform_df.writeStream.format("console").outputMode("append").start()


transform_df.awaitTermination()
