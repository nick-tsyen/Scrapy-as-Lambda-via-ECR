import sys
import types
import os
import logging
from urllib.parse import urlparse
import time
from scrapy.spiderloader import SpiderLoader
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import boto3

logging.basicConfig(level=logging.INFO, force=True)
logger = logging.getLogger()


# Need to "mock" sqlite for the process to not crash in AWS Lambda / Amazon Linux
sys.modules["sqlite"] = types.ModuleType("sqlite")
sys.modules["sqlite3.dbapi2"] = types.ModuleType("sqlite.dbapi2")


def is_in_aws():
    return os.getenv('AWS_EXECUTION_ENV') is not None


def crawl(settings={}, spider_name="quotesimple", spider_kwargs={}):
    project_settings = get_project_settings()
    spider_loader = SpiderLoader(project_settings)
    logger.info(spider_name)
    spider_cls = spider_loader.load(spider_name)

    feed_uri = ""
    feed_format = "json"

    try:
        spider_key = urlparse(spider_kwargs.get("start_urls")[0]).hostname if spider_kwargs.get(
            "start_urls") else urlparse(spider_cls.start_urls[0]).hostname
    except Exception:
        logging.exception("Spider or kwargs need start_urls.")

    if is_in_aws():
		# Lambda can only write to the /tmp folder.
        settings['HTTPCACHE_DIR'] =  "/tmp"
    else:
        feed_uri = "file:///{}/%(name)s-{}-%(time)s.json".format(
            os.path.join(os.getcwd()), spider_key,
        )

    date_str = time.strftime('%Y%m%d')
    settings['FEED_URI'] = f's3://scrapy-sam/{date_str}/%(name)s.json'
    settings['OUTPUT_URI'] = feed_uri
    settings['FEED_FORMAT'] = feed_format

    process = CrawlerProcess({**project_settings, **settings})

    process.crawl(spider_cls, **spider_kwargs)
    process.start()