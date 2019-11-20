import scrapy
# from scrapy.http import Request
from scourgify import normalize_address_record
from nameparser import HumanName
from ...items import UpdateTaxRecordsItem
from ...data_funcs import *
import traceback
# MySQL not being used yet
# from ...my_sql_funcs import *

class MtMissoulaCountyUpdateRecord(scrapy.Spider):
    name = 'mt_missoula_county_update_record'
    BASE_URL = "https://itax.missoulacounty.us/itax/"

    def start_requests(self, tax_id='', parcel_id=''):
        start_urls = ['https://itax.missoulacounty.us/itax/detail.aspx?taxid=' + self.tax_id]
        for url in start_urls:
            yield scrapy.Request(url=url, headers={'X-Crawlera-Session': 'create'}, callback=self.parse)

    def parse(self, response):
        items = UpdateTaxRecordsItem()

        state = 'MT'
        county = 'Missoula County'

        owner_full_name = response.xpath('//*[ @ id = "_ctl0_ContentPlaceHolder1_lblOwners"]/text()').extract_first()

        items['owner_is_company'] = is_company(owner_full_name)

        items['owner'] = owner_full_name
        try:
            owner = HumanName(owner_full_name)

            items['owner_first'] = owner.last
            items['owner_middle'] = owner.middle
            items['owner_last'] = owner.first
            items['owner_suffix'] = owner.suffix
            items['owner_nickname'] = owner.nickname
        except:
            traceback.print_exc()

            items['owner_first'] = 'Error'
            items['owner_middle'] = 'Error'
            items['owner_last'] = 'Error'
            items['owner_suffix'] = 'Error'
            items['owner_nickname'] = 'Error'

        tax_id = response.xpath('//*[ @ id = "_ctl0_ContentPlaceHolder1_lblTaxID"]/text()').extract_first()

        geo_code = response.xpath('//*[ @ id = "_ctl0_ContentPlaceHolder1_rptLegal__ctl0_lblLegal"]/b[contains(text(),"Geo")]/following::text()[1]').extract_first()

        if geo_code is None:
            parcel_id = tax_id
        else:
            geo_code = geo_code.strip()
            parcel_id = geo_code.replace('-', '')

        full_mailing_address = response.xpath('//*[ @ id = "_ctl0_ContentPlaceHolder1_lblMailing"]/text()').extract()
        full_mailing_address = ' '.join([str(elem) for elem in full_mailing_address])
        # remove line breaks
        full_mailing_address = full_mailing_address.replace('\r', '').replace('\n', '')


        items['mailing_address'] = full_mailing_address
        try:
            # converts a 9 digit zip code into a 5 digit zip code so we don't get a normalize_address error
            mailing_address = normalize_address_record(full_mailing_address)

            items['mailing_address_line_1'] = mailing_address['address_line_1']
            items['mailing_address_line_2'] = mailing_address['address_line_2']
            items['mailing_address_city'] = mailing_address['city']
            items['mailing_address_state'] = mailing_address['state']
            items['mailing_address_postal_code'] = mailing_address['postal_code']
        except:
            traceback.print_exc()

            result = full_mailing_address.split(' ')[-1]
            zip_code = ''.join([n for n in result if n.isdigit()])
            if len(zip_code) > 4:
                if len(zip_code) == 9:
                    items['mailing_address_postal_code'] = zip_code[:-4]
                else:
                    items['mailing_address_postal_code'] = zip_code

                result = full_mailing_address.split(',')[-1]
                address_state = result.replace(zip_code, '').strip()
                if len(address_state) == 2:
                    items['mailing_address_state'] = address_state
                else:
                    items['mailing_address_state'] = ''
            else:
                items['mailing_address_postal_code'] = ''
                items['mailing_address_state'] = ''

            items['mailing_address_line_1'] = ''
            items['mailing_address_line_2'] = ''
            items['mailing_address_city'] = ''

        try:
            full_property_address = response.xpath('//*[ @ id = "_ctl0_ContentPlaceHolder1_rptLegal__ctl0_lblLegal"]/b[contains(text(),"Property")]/following::text()[1]').extract_first()
            full_property_address = full_property_address.strip()
        except:
            traceback.print_exc()

            full_property_address = 'Error'

        items['property_address'] = full_property_address
        try:
            property_address = normalize_address_record(full_property_address)

            if property_address['address_line_1'] != None:
                items['property_address_line_1'] = property_address['address_line_1']
            else:
                items['property_address_line_1'] = ''

            if property_address['address_line_2'] != None:
                items['property_address_line_2'] = property_address['address_line_2']
            else:
                items['property_address_line_2'] = ''

            if property_address['city'] != None:
                items['property_address_city'] = property_address['city']
            else:
                items['property_address_city'] = ''

            # Will always be the same as the state variable
            items['property_address_state'] = state

            if property_address['postal_code'] != None:
                items['property_address_postal_code'] = property_address['postal_code']
            else:
                items['property_address_postal_code'] = ''
        except:
            traceback.print_exc()

            items['property_address_line_1'] = 'Error'
            items['property_address_line_2'] = 'Error'
            items['property_address_city'] = 'Error'
            items['property_address_state'] = state
            items['property_address_postal_code'] = 'Error'

        try:
            net_value = response.xpath('//*[ @ id = "_ctl0_ContentPlaceHolder1_lblValueMarket"]/text()').extract_first()
            net_value = net_value.replace('$', '').replace(',', '')
            items['net_value'] = net_value
        except:
            traceback.print_exc()
            items['net_value'] = ''

        items['parcel_id'] = parcel_id
        items['tax_id'] = tax_id
        items['geo_code'] = geo_code
        items['state'] = state
        items['county'] = county

        items['in_same_state'] = False
        items['has_same_mailing'] = False
        items['in_same_zip'] = False
        if items['mailing_address_state'] == items['property_address_state']:
            items['in_same_state'] = True
            if items['mailing_address_postal_code'] == items['property_address_postal_code']:
                items['in_same_zip'] = True
                if items['mailing_address_line_1'] == items['property_address_line_1']:
                    items['has_same_mailing'] = True

        try:
            status = response.xpath('//*[ @ id = "_ctl0_ContentPlaceHolder1_lblStatus"]/text()[1]').extract_first()
            if 'delinquent' in status.lower():
                items['is_delinquent'] = True
            else:
                items['is_delinquent'] = False
        except:
            traceback.print_exc()
            items['is_delinquent'] = True

        items['tax_sale_date'] = '2020-10-20'

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

        # This gets all the data we need for the values below.
        rows = response.xpath('//*[ @ id = "_ctl0_ContentPlaceHolder1_dgHistory"]/tr')
        for row in rows:
            tax_year = rows[1].xpath('td[1]/a/text()').extract()
            print('tax_year == ' + str(tax_year))
            bill_date = rows[1].xpath('td[3]/text()').extract()
            print('bill_date == ' + str(bill_date))
            bill_amount = rows[1].xpath('td[4]/text()').extract()
            print('bill_amount == ' + str(bill_amount))
            date_paid = rows[1].xpath('td[5]/text()').extract()
            print('date_paid == ' + str(date_paid))
            paid_amount = rows[1].xpath('td[6]/text()').extract()
            print('paid_amount == ' + str(paid_amount))

        # We need to yield all of these values for each tax year but we should not yield the same tax year more than once.
        # tax_year
        # bill_date_1st_half
        # bill_date_2nd_half
        # bill_amount_1st_half
        # bill_amount_2nd_half
        # date_paid_1st_half_1
        # date_paid_1st_half_2
        # date_paid_2nd_half_1
        # date_paid_2nd_half_2
        # paid_amount_1st_half_1
        # paid_amount_1st_half_2
        # paid_amount_2nd_half_1
        # paid_amount_2nd_half_2

        yield items