import logging

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, ByteType


def get_logger(name: str, log_level):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler()
    handler.setLevel(log_level)

    logger.addHandler(handler)

    return logger


def get_spark_session(app_name: str):
    spark = SparkSession.builder.appName(app_name).getOrCreate()

    return spark


def get_redis_tools(host: str, port: int, db: int):
    redis_client = redis.StrictRedis(host=host, port=port, db=db)

    return redis_client


def get_redis_data(redis_client: redis.StrictRedis, start_id: str):
    response = redis_client.xread({b"requests": f"{start_id}"}, block=5000)

    try:
        clean_response = list(
            map(
                lambda x: (
                    x[0].decode("utf-8"),
                    x[1][b"datetime"],
                    x[1][b"temp"],
                    x[1][b"hum"],
                ),
                response[0][1],
            )
        )

        # last record's decoded id
        start_id = clean_response[-1][0]

        return clean_response, start_id
    except:
        return response, start_id


def stream_from_redis(redis_client, spark_session, logger):
    start_id = "0-0"
    schema = StructType([
        StructField("id", StringType(), True),
        StructField("datetime", ByteType(), True),
        StructField("temperature", ByteType(), True),
        StructField("humidity", ByteType(), True)
    ])
    empty_df = spark_session.createDataFrame(
        data=spark_session.sparkContext.emptyRDD(),
        schema=schema,
    )
    response, start_id = get_redis_data(redis_client, start_id)
    if len(response) == 0:
        logger.info("no new data")
        return empty_df

    df = spark_session.createDataFrame(
        response, schema=["id", "datetime", "temperture", "humidity"]
    )

    logger.info(f"df row count {df.count()}")
    # logger.info(f"new records: {len(response)}")
    logger.debug(f"final ID: {start_id}")

    yield df


def main():
    logger = get_logger(name="spark_logger", log_level=logging.DEBUG)
    spark = get_spark_session("temp_streaming")
    redis_client = get_redis_tools(host="redis", port=6379, db=0)

    while True:
        time.sleep(5)
        new_df = next(stream_from_redis(redis_client, spark, logger))

        transform_df = new_df.withColumnRenamed("temperature", "temp")

        query = transform_df.writeStream.outputMode("append").format("console").start()

        query.awaitTermination()


if __name__ == "__main__":
    main()
