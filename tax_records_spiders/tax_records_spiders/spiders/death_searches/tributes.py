import scrapy
from nameparser import HumanName
import traceback
from ...my_sql_funcs import *
import re
import time

class UpdateRecord(scrapy.Spider):
    name = 'tributes_death_search'

    def __init__(self, first='', last='', state='', year=''):

        self.start_urls = ["http://www.tributes.com/search/obituaries/?solr=&first={}&last={}&city=&state={}&search_type={}&dod=&keywords=".format(first, last, state, year)]
        self.state = state
        self.first = first
        self.last = last
        self.year = year
        self.website = 'tributes.com'

    def parse(self, response):

        search_record_id = get_death_search_record_id(self.year, self.first, self.last, self.state)
        if search_record_id:
            print("This search is already in the DB. The spider is exiting.")
            return

        search_errors = response.xpath('//*[@id="obituary_results"]/div/p/text()').extract_first(default='not-found')
        too_many_results = False
        no_results_found = False
        if search_errors == 'not-found':
            number_of_results = response.xpath('//*[@id ="pagination_bar"]/p/span[4]/text()').extract_first(default='not-found')
            status = number_of_results + ' results found'
        elif 'This search yielded too many names' in search_errors:
            status = 'This search yielded too many names'
            too_many_results = True
        elif 'No results were found using your search criteria' in search_errors:
            status = 'No results were found using this search criteria.'
            no_results_found = True
        else:
            status = 'Error (unknown response)'

        if too_many_results == False and no_results_found == False:
            results = response.xpath('//*[@id="results-item-list-id"]//a[contains(@href, "/obituary/show/")]/@href').extract()

            for link in results:
                yield scrapy.Request(response.urljoin(link), callback=self.parse_obituary)

        # send search record to the DB here
        add_or_update_death_search_record(self.year, self.first, self.last, self.state, too_many_results, self.website, status)

    def parse_obituary(self, response):
        items = {}
        items['full_name'] = response.xpath('//*[@id="main-content"]//span[@itemprop="name"]/text()').extract_first()
        try:
            name = HumanName(items['full_name'])
            items['name_title'] = name.title
            items['name_first'] = name.first
            items['name_middle'] = name.middle
            items['name_last'] = name.last
            items['name_suffix'] = name.suffix
            items['name_nickname'] = name.nickname
        except:
            traceback.print_exc()

            items['name_title'] = 'Error'
            items['name_first'] = 'Error'
            items['name_middle'] = 'Error'
            items['name_last'] = 'Error'
            items['name_suffix'] = 'Error'
            items['name_nickname'] = 'Error'

        items['obituary'] = ''.join(response.xpath('//*[@id="obit_text_page_1"]//text()').extract()).strip()
        items['dob'] = response.xpath('//*[@id="main-content"]//meta[@itemprop="birthDate"]/@content').extract_first()
        if items['dob'] == None:
            items['dob'] = ''

        items['dod'] = response.xpath('//*[@id="main-content"]//meta[@itemprop="deathDate"]/@content').extract_first()
        if items['dod'] == None:
            dates = response.xpath('//*[@id="main-content"]//li/text()').extract_first().strip()
            if '- ' in dates:
                dod = dates.split('- ', -1)[-1]
                struct_time = time.strptime(dod, '%B %Y')
                dod_year = struct_time.tm_year
                dod_mon = struct_time.tm_mon
                dod_mday = struct_time.tm_mday

                items['dod'] = '{}-{}-{}'.format(dod_year, dod_mon, dod_mday)
            else:
                items['dod'] = ''

        items['city_of_death'] = response.xpath('//*[@id="main-content"]//span[@itemprop="address"]/text()').extract_first()
        if type(items['city_of_death']) == str:
            if ',' in items['city_of_death']:
                items['city_of_death'] = items['city_of_death'].split(',')[0]

            items['city_of_death'] = re.findall(r"\S+", items['city_of_death'])[0]
        else:
            items['city_of_death'] = ''

        items['state_of_death'] = self.state
        items['obituary_url'] = response.url

        add_or_update_death_record(items)
