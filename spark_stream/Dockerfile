FROM apache/spark:latest

USER root

RUN apt-get update

RUN apt-get install -y python3
RUN export PATH="$PATH:$(which python3)"

ENV PYSPARK_MAJOR_PYTHON_VERSION=3

COPY requirements.txt .

RUN pip install -r requirements.txt
RUN rm requirements.txt

WORKDIR /app

COPY main.py /app/main.py

CMD ["python3", "main.py"]
