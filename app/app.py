import sys
import json

from simplescrapper import crawl


def scrape(event={}, context={}):
    crawl.crawl(**event)


def lambda_handler(event, context):
    scrape(event, context)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

# if __name__ == "__main__":
#     try:
#         event = json.loads(sys.argv[1])
#     except IndexError:
#         event = {}
#     scrape(event)