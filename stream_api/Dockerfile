FROM python:3.11

COPY requirements.txt .

RUN pip install -r requirements.txt
RUN rm requirements.txt

WORKDIR /app

COPY main.py /app/main.py

EXPOSE 8000

CMD ["python", "main.py"]
