import scrapy, io, re, PyPDF2
from ...my_sql_funcs import *
from scrapy.http import Request

class MtMissoulaCountyGetDelinquentListIds(scrapy.Spider):
    name = 'mt_missoula_county_get_delinquent_list_ids'
    state = 'MT'
    county = 'Missoula County'

    def __init__(self):
        self.start_urls = ['https://missoulacounty.us/government/administration/clerk-treasurer/treasurer/property-taxes/delinquent-taxes']

    def parse(self, response):
        url_text = response.xpath('//*[@id="widget_4_9867_5947"]/p[3]/a[3]/following::text()[1]').extract_first()
        if 'Complete PDF' in url_text:
            delinquent_list_url = response.xpath('//*[@id="widget_4_9867_5947"]/p[3]/a[3]/@href').extract_first()
            delinquent_list_pdf_url = response.urljoin(delinquent_list_url)

            yield Request(delinquent_list_pdf_url, self.parse_pdf)
        else:
            # sends an error to our website log
            error = 'The Complete PDF link could not be found.'
            send_scraper_error(state=self.state, county=self.county, scraper_name=self.name, error=error)

    def parse_pdf(self, response):
        reader = PyPDF2.PdfFileReader(io.BytesIO(response.body))
        pdf_text = ''
        for page in reader.pages:
            pdf_text += page.extractText()

        parcels = re.findall(r'Parcel # \d+', pdf_text)

        parcels_ids = []
        parcels = list(set(parcels)) #Get unique values
        for parcel in parcels:
            parcels_ids.append(parcel.replace('Parcel # ', ''))

        # Send the delinquent parcels to the website
        for parcel in parcels_ids:
            update_delinquent_status = ("CALL select_or_insert_is_delinquent("
                                        "'{}',"
                                        "'{}',"
                                        "'{}',"
                                        "'{}',"
                                        "'true')").format(parcel, parcel, 'MT', self.county)

            print("Sending: " + update_delinquent_status)
            execute_query(update_delinquent_status)