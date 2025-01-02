import time
from kafka import KafkaProducer


producer = KafkaProducer(bootstrap_servers="127.0.0.1:9092")


while True:
    producer.send(topic="test_topic", key=b"hello_key", value=b"hello_value")
    time.sleep(1)
    print("sent a message")
