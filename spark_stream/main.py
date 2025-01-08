import time

from kafka.admin import KafkaAdminClient
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import FloatType, StructField, StructType


KAFKA_BROKER = "kafka:9092"
KAFKA_TOPIC = "sensor_queue"

connected_to_kafka = False

schema = StructType(
    [
        StructField("temperature", FloatType(), True),
        StructField("humidity", FloatType(), True),
    ]
)


def connect_admin_client(broker: str, retries: int, delay: int) -> KafkaAdminClient:
    for i in range(retries):
        try:
            kafka_admin = KafkaAdminClient(bootstrap_servers=broker)
            return kafka_admin
        except:
            print(f"attempt {i + 1}/{retries}: failed to connect to kafka")
            time.sleep(delay)


def wait_for_kafka(broker: str, topic: str, retries: int, delay: int) -> None:
    print("connecting admin client")
    kafka_admin = connect_admin_client(broker, retries, delay)
    print("connected to admin")

    print("waiting for topic")
    for i in range(retries):
        if topic in kafka_admin.list_topics():
            print("done")
            return None
        print(f"attempt {i + 1}/{retries}: waiting for topic to exist")
        time.sleep(delay)

    print("topic did not appear")


if not connected_to_kafka:
    wait_for_kafka(KAFKA_BROKER, KAFKA_TOPIC, retries=12, delay=5)
    connected_to_kafka = True

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
    "timestamp", "CAST(value AS STRING) as json_string"
)
transform_df = transform_df.withColumn(
    "parsed_value", F.from_json("json_string", schema)
)
transform_df = transform_df.select(
    F.to_timestamp(
        F.date_format("timestamp", "yyyy-MM-dd HH:mm"), format="yyyy-MM-dd HH:mm"
    ).alias("datetime"),
    F.col("parsed_value.temperature"),
    F.col("parsed_value.humidity"),
)

transform_df = (
    transform_df.withWatermark("datetime", "1 minute")
    .groupBy(F.window("datetime", "1 minute"))
    .agg(
        F.round(F.mean(F.col("temperature")), 2).alias("temperature"),
        F.round(F.mean(F.col("humidity")), 2).alias("humidity"),
    )
)

transform_df.writeStream.outputMode("append").format("console").start()

while True:
    time.sleep(60)
