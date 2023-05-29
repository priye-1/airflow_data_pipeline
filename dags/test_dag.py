from datetime import timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from datetime import datetime


def testing():
    print("This is a test dag")


default_args = {
    'owner': 'airflow',
    'depends_on_past': 'False',
    'start_date': datetime(2023, 5, 25),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'schedule_interval': None,
    'retry_delay': timedelta(minutes=1)
}

dag = DAG(
    'test_dag',
    default_args=default_args,
    description="Dag to test airflow"
)

run_test = PythonOperator(
    task_id='run_tests',
    python_callable=testing,
    dag=dag
)

run_test
