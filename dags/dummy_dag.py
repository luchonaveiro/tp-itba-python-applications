"""Dummy DAG."""
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.dummy import DummyOperator

with DAG(
    "dummy_dag",
    schedule_interval=timedelta(weeks=1),
    start_date=datetime(2021, 10, 11),
    catchup=False,
) as dag:
    t1 = DummyOperator(task_id="hello-world")
