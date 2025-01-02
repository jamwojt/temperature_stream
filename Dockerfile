FROM python:3.11

COPY database_schema /app

RUN python /app/create_db.py
