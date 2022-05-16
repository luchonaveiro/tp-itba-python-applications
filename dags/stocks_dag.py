"""Stocks DAG."""
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from time import sleep

import matplotlib.pyplot as plt
import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator
from sqlalchemy.exc import IntegrityError
from sqlite_cli import SqLiteClient
from utils import get_api_data, get_plot_data

# Set up Logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

BASE_URL = "https://www.alphavantage.co/query"
API_KEY = "TFHNYCWBD71JBSON"
STOCK_FN = "TIME_SERIES_DAILY"

POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

DB_URI = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"

STOCK_SYMBOLS = ["goog", "msft", "amzn"]

STORE_DIR = Path(__file__).resolve().parent / "tmp-files" / "stocks_plots"
Path.mkdir(STORE_DIR, exist_ok=True, parents=True)


def _get_stock_data(stock_symbols, **context):
    sleep(60)  # to prevent the API returning an error on frequent requests (5 per minute)
    date = context["ds"]  # read execution date from context

    for stock_symbol in stock_symbols:
        end_point = (
            f"{BASE_URL}?function={STOCK_FN}&symbol={stock_symbol}"
            f"&apikey={API_KEY}&datatype=json"
        )

        open_vale, high_value, low_value, close_value = get_api_data(end_point, date)
        data = [[stock_symbol, date, open_vale, high_value, low_value, close_value]]
        df = pd.DataFrame(data, columns=["symbol", "date", "open", "high", "low", "close"])
        sql_cli = SqLiteClient(DB_URI)
        try:
            logger.info(f"Inserting {stock_symbol} values for {context['ds']}")
            sql_cli.insert_from_frame(df, "stock_value")
        except IntegrityError:
            logger.info(f"Already have {stock_symbol} values for {context['ds']} on DB")
        except Exception as e:
            logger.info(f"Unknown error: {e}")


def _plot_weekly_data(stock_symbols, **context):
    date_to = context["ds"]

    for stock_symbol in stock_symbols:

        plot_data = get_plot_data(stock_symbol, date_to)

        ax = plot_data.plot(
            figsize=(20, 10),
            title=f"{stock_symbol}: Closing Price Evolution (1 week moving average)",
        )
        for x, y in zip(plot_data.index, plot_data.close):
            ax.annotate(
                f"$ {round(y, 2)}",
                (x, y),
                textcoords="offset points",
                xytext=(0, 10),
                ha="center",
            )

        plt.savefig(STORE_DIR / f"{stock_symbol}_{date_to}_plot.png")
        logger.info(f"{stock_symbol} plot saved on {STORE_DIR}")


default_args = {"owner": "luciano.naveiro"}

with DAG(
    "stocks_dag",
    schedule_interval="0 0 * * 1-5",
    start_date=datetime(2022, 1, 1),
    catchup=True,
    max_active_runs=1,
    default_args=default_args,
) as dag:
    get_daily_data = PythonOperator(
        task_id="get_daily_data",
        python_callable=_get_stock_data,
        op_args=[STOCK_SYMBOLS],
        retries=3,
        retry_delay=timedelta(seconds=90),
    )

    plot_weekly_data = PythonOperator(
        task_id="plot_weekly_data",
        python_callable=_plot_weekly_data,
        op_args=[STOCK_SYMBOLS],
    )


get_daily_data >> plot_weekly_data
