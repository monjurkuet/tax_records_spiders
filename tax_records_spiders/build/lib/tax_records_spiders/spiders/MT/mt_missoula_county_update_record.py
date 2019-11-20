import scrapy
from scrapy.http import Request
# from scrapy.http import FormRequest
from scourgify import normalize_address_record
from nameparser import HumanName
from ...items import UpdateTaxRecordsItem
import traceback


class MtMissoulaCountyUpdateRecord(scrapy.Spider):
    name = 'mt_missoula_county_update_record'

    def __init__(self, tax_id='', parcel_id=''):
        self.start_urls = ['https://itax.missoulacounty.us/itax/detail.aspx?taxid=' + tax_id]


    def parse(self, response):

        items = UpdateTaxRecordsItem()

        state = 'MT'

        county = 'Missoula County'

        owner_full_name = response.xpath('//*[ @ id = "_ctl0_ContentPlaceHolder1_lblOwners"]/text()').extract_first()

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
        except Exception:
            traceback.print_exc()

            items['property_address_line_1'] = 'Error'
            items['property_address_line_2'] = 'Error'
            items['property_address_city'] = 'Error'
            items['property_address_state'] = state
            items['property_address_postal_code'] = 'Error'

        items['parcel_id'] = parcel_id
        items['tax_id'] = tax_id
        items['geo_code'] = geo_code
        items['state'] = state
        items['county'] = county

        history_url = response.xpath('//*[ @ id = "_ctl0_ContentPlaceHolder1_linkHistory"]/@href').extract()[0]
        history_page = response.urljoin(history_url)

        yield Request(history_page, self.parse_history_page,
                      meta={'items': items})

    def parse_history_page(self, response):
        items = response.meta['items']
        print(response.url)
        table = response.xpath('//*[ @ id = "_ctl0_ContentPlaceHolder1_Panel2"]').extract()

        items['table'] = "test"
        yield items