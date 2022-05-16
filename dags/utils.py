"""Functions used by the Stocks DAG."""
import json
import logging
import os

import requests
from sqlite_cli import SqLiteClient

logger = logging.getLogger(__name__)

POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

DB_URI = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"


def get_api_data(end_point, date):
    """Fetches data from Alphavantage API."""
    logger.info(f"Getting data from {end_point}...")
    r = requests.get(end_point)

    data = json.loads(r.content)["Time Series (Daily)"]
    if date in data:
        day_data = data[date]
        open_value = round(float(day_data["1. open"]), 2)
        high_value = round(float(day_data["2. high"]), 2)
        low_value = round(float(day_data["3. low"]), 2)
        close_value = round(float(day_data["4. close"]), 2)
    else:
        logger.info(f"{end_point} returned empty data for {date}")
        open_value = high_value = low_value = close_value = float("nan")

    return open_value, high_value, low_value, close_value


def get_plot_data(stock_symbol, date_to):
    """Queries data from stocks DB on the format to be plotted."""
    logger.info(f"Querying data for {stock_symbol} from {date_to}")

    sql_cli = SqLiteClient(DB_URI)
    plot_data = sql_cli.to_frame(
        f"""
        SELECT date,
            AVG(close) OVER (
                ORDER BY CAST(date AS TIMESTAMP) RANGE BETWEEN
                INTERVAL '6 DAYS' PRECEDING AND CURRENT ROW
                ) AS close
        FROM stock_value
        WHERE symbol = '{stock_symbol}' AND
        close IS NOT NULL AND
        date <= '{date_to}'
        ORDER BY date ASC"""
    )
    plot_data = plot_data.set_index("date")

    return plot_data
