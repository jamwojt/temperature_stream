CREATE TABLE IF NOT EXISTS temp_store (
    id SERIAL PRIMARY KEY,
    datetime TIMESTAMP WITH TIME ZONE,
    temperature REAL,
    humidity REAL
);

CREATE TABLE IF NOT EXISTS hourly_agg (
    id PRIMARY KEY,
    datetime TIMESTAMP,
    temperature REAL,
    humidity REAL
);
