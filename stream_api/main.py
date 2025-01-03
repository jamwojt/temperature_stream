import json
import time

from fastapi import FastAPI
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import NoBrokersAvailable


def create_kafka_topic(broker: str, topic: str):
    kafka_admin = KafkaAdminClient(bootstrap_servers=broker)

    while True:
        try:
            if topic not in kafka_admin.list_topics():
                kafka_admin.create_topics(
                    [
                        NewTopic(name=topic, num_partitions=1, replication_factor=1),
                    ]
                )
                break

        except:
            print("waiting for kafka to start")
            time.sleep(2)

    kafka_admin.close()


def create_kafka_producer(broker: str, retries: int, delay: int) -> KafkaProducer:
    for i in range(retries):
        try:
            producer = KafkaProducer(bootstrap_servers=broker)
            return producer
        except NoBrokersAvailable:
            print(f"attempt {i + 1}/{retries}: Cannot find kafka broker")
            time.sleep(delay)
    raise Exception("Cannot connect producer to kafka broker")


app = FastAPI()

kafka_broker = "kafka:9092"
kafka_topic = "sensor_queue"

kafka_producer = None
kafka_topic_exists = False


@app.get("/")
def home():
    greet = {"hello": 5}
    return greet


@app.post("/pass-data/{temp}/{hum}")
def pass_data(temp: float, hum: float):
    global kafka_producer
    global kafka_topic_exists

    if not kafka_topic_exists:
        create_kafka_topic(kafka_broker, kafka_topic)
        kafka_topic_exists = True

    if kafka_producer is None:
        kafka_producer = create_kafka_producer(kafka_broker, retries=12, delay=5)

    data = json.dumps({"temperature": float(temp), "humidity": float(hum)}).encode(
        "utf-8"
    )
    kafka_producer.send(topic=kafka_topic, value=data)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="api", port=8000)
