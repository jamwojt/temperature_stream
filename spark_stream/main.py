import time

from kafka.admin import KafkaAdminClient
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import ByteType, StringType, StructField, StructType


KAFKA_BROKER = "kafka:9092"
KAFKA_TOPIC = "sensor_queue"


def connect_admin_client(broker: str, retries: int, delay: int) -> KafkaAdminClient:
    for i in range(retries):
        try:
            kafka_admin = KafkaAdminClient(bootstrap_servers=broker)
            return kafka_admin
        except:
            print(f"attempt {i + 1}/{retries}: failed to connect to kafka")
            time.sleep(delay)


def wait_for_kafka(broker: str, topic: str, retries: int, delay: int) -> None:
    kafka_admin = connect_admin_client(broker, retries, delay)
    for i in range(retries):
        if topic in kafka_admin.list_topics():
            return None
        print(f"attempt {i + 1}/{retries}: waiting for topic to exist")
        time.sleep(delay)


wait_for_kafka(KAFKA_BROKER, KAFKA_TOPIC, retries=12, delay=5)

spark = (
    SparkSession.builder.appName("temp_stream")
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.1")
    .getOrCreate()
)


listener_df = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", KAFKA_BROKER)
    .option("subscribe", "sensor_queue")
    .option("startingOffsets", "earliest")
    .load()
)


transform_df = listener_df.selectExpr(
    "CAST(key AS STRING)", "CAST(value AS STRING)", "timestamp"
)

transform_df.writeStream.outputMode("append").format("console").start()

print("sleeping")
time.sleep(60)
