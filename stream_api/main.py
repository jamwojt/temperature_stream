from fastapi import FastAPI
from kafka import KafkaProducer
import time


app = FastAPI()

kafka_broker = "kafka:9092"
kafka_topic = "sensor_queue"

connected = False
connecting_time = 0

while connecting_time <= 60 and not connected:
    try:
        print(f"connecting to kafka... ({connecting_time})")
        kafka_producer = KafkaProducer(bootstrap_servers=kafka_broker)
        print("connected to the kafka broker")
        connected = True
    except:
        connected += 2
        time.sleep(2)

if connecting_time > 60:
    print("couldn't connect with kafka broker")

@app.get("/")
def home():
    greet = {"hello": 5}
    return greet


@app.post("/pass-data/{temp}/{hum}")
def pass_data(temp: float, hum: float):
    data = {"temperature": float(temp), "humidity": float(hum)}
    kafka_producer.send(topic=kafka_topic, value=data)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="api", port=8000)
