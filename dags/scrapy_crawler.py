import os
import sys
import datetime
from scrapy.crawler import CrawlerProcess

sys.path.extend(["/home/ubuntu/airflow/dags/scraper/pst_ag_project/"])
from scraper.pst_ag_project.pst_ag_project.spiders import rwjst_spider


AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')


def run_crawler():

    current_datetime = datetime.datetime.now()
    file_date = current_datetime.strftime("%Y-%m-%d:%H-%M-%S")
    process = CrawlerProcess(
        settings={
            "LOG_ENABLED": False,
            "FEEDS": {
                f"s3://airflow-snowflake-data-pipeline/{file_date}.csv": {
                    "format": "csv",
                },
            },
            "AWS_ACCESS_KEY_ID": AWS_ACCESS_KEY_ID,
            "AWS_SECRET_ACCESS_KEY": AWS_SECRET_ACCESS_KEY,
            "CONCURRENT_REQUESTS": 20,
            "ITEM_PIPELINES": {
                'pst_ag_project.pipelines.FormatRewardAmountPipeline': 100,
                'pst_ag_project.pipelines.ListtoStringPipeline': 200,
                'pst_ag_project.pipelines.FormatDatePipeline': 300
            }
        }

    )
    process.crawl(rwjst_spider.RwjstspiderSpider)
    process.start()

    return file_date
