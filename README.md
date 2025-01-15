# Streaming Temperature Sensor Data with PySpark and Kafka
In this project, I want to learn the basics of streaming data using PySpark. Since I did not have any previous experience with streaming data, major part of this project was research and trying multiple solutions.

## Possible solutions

The full idea is to have an ESP32 microcontroler with a DHT22 sensor connected with spark that will aggregate the data sent from the sensor. I had multiple ideas on how to do this, but it took me a while to get to the actual solution.

0. I know that Kafka is the industry standard for handling real-time data, but because of how small the stream would be, I decided to look for alternatives before.

1. ESP32 -> PySpark
The first "no research / common sense" approach was to just use the microcontroler's internet module to send http requests to Spark. This very quickly showed its flaws.
 - Spark cannot handle bare http requests
 - if somethings goes wrong, the data is just gone

2. ESP32 -> API -> Redis -> Spark
This approach resolves the problem of small control over the data flow. I have an API that accepts http requests and pushes the data. Redis serves as resiliance layer because it can make backups on disk, so if anything goes wrong, the amount of lost data is limited. Then, Spark can just read the microbatches from Redis, and process them. This would be my favourite approach for this project given the volume of data. Unfortunately, this was not a feasible solution for me mostly because Spark cannot connect to a Redis instance by default. I would have to use a custom connector, which does exist, but it is not updated to any Spark version I could use.

3. ESP32 -> API -> Kakfa -> Spark
I ended up running out of time for implementing the solution, so I ended up at square one. I had some trouble understanding all the port connections between my API, Kafa instance, and Spark, but once this was resolved, I ended up with the base communication:
 - API accespts http requests and pushes data to a Kafka topic
 - Kafka stores the information before it is processed, providing a layer of resilience
 - Spark reads data of Kafka and aggregates it using watermarks

## Future steps
Since I only had a semester and I didn't have any experience setting all of this up, there is a lot that still has to be done to fully complete this project.
Firstly, I was not able to write code for the microcontroler. I quickly decided to focus on the part that is more important for the university part of the project.
While Spark can correctly read and aggregate the data from Kafka, it is not in the optimal shape. Using watermark changes the column with datetime to an entire window. Changing this sothat it becomes an actual timestamp.
Lastly, for now, I am just printing the aggregated data to console. In the future I would like to save the results to a database.

## How to use it?
Currently, not all modules are published to Docker Hub. Therefore, it is necessary to clone this repository and run it with "docker compose up" command.
I do not have the code for the microcontroler at this point, so providing something that can send requests to the API endpoint is required.
