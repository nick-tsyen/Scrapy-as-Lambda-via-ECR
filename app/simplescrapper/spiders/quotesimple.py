import scrapy


class QuotesimpleSpider(scrapy.Spider):
    name = 'quotesimple'
    allowed_domains = ['www.brainyquote.com', 'brainyquote.com']
    start_urls = ['https://www.brainyquote.com/topics/scrap-quotes']

    def parse(self, response):
        quotes = response.xpath('//div[@id="quotesList"]/div[@id="qbcc"]/div/div[contains(@id, "pos_")]')
        if quotes.getall():
            for quote in quotes:
                quote_text = quote.xpath('./*/div/text()').get()
                if len(quote.xpath('./a').getall()) > 1:
                    quote_author = quote.xpath('./a')[1].xpath('text()').get()

                yield {
                    'quote_text': quote_text,
                    'quote_author': quote_author
                }

            page_items = response.xpath('//li[@class="page-item"]')
            if len(page_items) > 0:
                next_page = page_items.xpath('./*[contains(text(), "Next")]/@href').get()

            if next_page is not None:
                yield response.follow(next_page, callback=self.parse)
