import scrapy


class UpdateTaxRecordsItem(scrapy.Item):
    # define the fields for your item here like:
    owner = scrapy.Field()
    table = scrapy.Field()


class UpdateRecord(scrapy.Spider):
    name = 'update_record'
    BASE_URL = "https://itax.missoulacounty.us/itax/"

    # def __init__(self, tax_id='', parcel_id=''):
    #     # self.start_urls = ['https://itax.missoulacounty.us/itax/detail.aspx?taxid=' + tax_id]
    #     url = 'https://itax.missoulacounty.us/itax/detail.aspx?taxid=' + tax_id
    #     self.make_requests_from_url(url=url)
    #
    #     # for url in self.start_urls:
    #     # scrapy.Request(url=url, headers={'X-Crawlera-Session': 'create'}, callback=self.parse)

    def start_requests(self, tax_id='', parcel_id=''):
        start_urls = ['https://itax.missoulacounty.us/itax/detail.aspx?taxid=' + self.tax_id]
        for url in start_urls:
            yield scrapy.Request(url=url, headers={'X-Crawlera-Session': 'create'}, callback=self.parse)

    def parse(self, response):
        items = UpdateTaxRecordsItem()

        owner_full_name = response.xpath('//*[ @ id = "_ctl0_ContentPlaceHolder1_lblOwners"]/text()').extract_first()
        items['owner'] = owner_full_name

        # Gets the URL  https://itax.missoulacounty.us/itax/history.aspx
        session_id = response.headers.get('X-Crawlera-Session', '')
        history_url = self.BASE_URL + response.xpath(
            '//*[ @ id = "_ctl0_ContentPlaceHolder1_linkHistory"]/@href').extract_first()
        request = scrapy.Request(history_url, callback=self.parse_history_page,
                                 headers={'X-Crawlera-Session': session_id})
        request.meta['items'] = items
        yield request

    def parse_history_page(self, response):
        items = response.meta['items']
        table = response.xpath('//*[ @ id = "_ctl0_ContentPlaceHolder1_dgHistory"]').extract()
        items['table'] = table
        yield items
