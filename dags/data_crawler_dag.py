import sys
from datetime import datetime
from datetime import timedelta
from airflow import AirflowException
from airflow.decorators import dag, task
from airflow.providers.amazon.aws.hooks.s3 import S3Hook


sys.path.extend(["/home/ubuntu/airflow/dags/scrapy_crawler/"])
from scrapy_crawler import run_crawler

default_args = {
    'owner': 'airflow',
    'depends_on_past': 'False',
    'start_date': datetime(2023, 5, 29),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'schedule_interval': None,
    'retry_delay': timedelta(seconds=20)
}

BUCKET = "airflow-snowflake-data-pipeline"

@dag(default_args=default_args, catchup=False)
def data_crawler_dag():

    @task
    def start_crawler():
        file_date = run_crawler()

        return file_date

    @task
    def confirm_s3_data_loaded(file_date: str):

        # connect to s3
        s3_hook = S3Hook(aws_conn_id='s3_conn')

        # Read data
        data_status = s3_hook.check_for_key(
                key=f"{file_date}.csv", bucket_name=BUCKET
            )
        if data_status is True:
            print(f"Object stored in s3: {file_date}")
        else:
            raise AirflowException("Object not successfully loaded on S3")

    confirm_s3_data_loaded(start_crawler())

data_crawler_dag()


