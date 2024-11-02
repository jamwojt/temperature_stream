import datetime
import json

import redis
from fastapi import FastAPI


redis_db = redis.Redis(host="redis", port=6379, db=0)


app = FastAPI()


@app.get("/")
def home():
    greet = {"hello": 5}
    return greet


@app.post("/pass-data/{temp}/{hum}")
def pass_data(temp, hum):
    data = {"datetime": str(datetime.datetime.now()), "temp": temp, "hum": hum}
    redis_db.xadd("requests", data)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="api", port=8000)
