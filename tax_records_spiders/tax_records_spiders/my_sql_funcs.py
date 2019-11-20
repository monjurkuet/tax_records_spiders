import mysql.connector


def execute_query(query):
    print("Sending MySQL query: " + query)

    cnx = mysql.connector.connect(user='admin', password='mX5FBbbuaF_Kvn?F',
                                  host='tax2profit-dev.cq1pnj9ijzbf.us-east-2.rds.amazonaws.com',
                                  database='tax2profit_dev')
    cursor = cnx.cursor()
    cursor.execute(query)
    result = cursor.fetchone()

    # Make sure data is committed to the database
    cnx.commit()

    cursor.close()
    cnx.close()

    return result


# sends errors to the website log
def send_scraper_error(parcel_id='N/A', state='', county='', scraper_name='', error=''):
    send_scraper_error = ("INSERT INTO `scraper_errors`"
                          "(`parcel_id`,"
                          "`state`,"
                          "`county`,"
                          "`scraper_name`,"
                          "`error`)"
                          "VALUES"
                          "('{}',"
                          "'{}',"
                          "'{}',"
                          "'{}',"
                          "'Could not find PDF link')").format(parcel_id, state, county, scraper_name, error)

    execute_query(send_scraper_error)


def add_or_update_death_search_record(year, first_name, last_name, state, too_many_results, website, status):
    add_record = ("INSERT INTO `death_searches`"
                  "(`year`,"
                  "`first_name`,"
                  "`last_name`,"
                  "`state`,"
                  "`too_many_results`,"
                  "`website`,"
                  "`status`)"
                  "VALUES("
                  "'{}',"
                  "'{}',"
                  "'{}',"
                  "'{}',"
                  "'{}',"
                  "'{}',"
                  "'{}')").format(year, first_name, last_name, state, too_many_results, website, status)

    execute_query(add_record)


def add_or_update_property(items):
    add_property = ("CALL select_or_insert("
                    "'{}',"
                    "'{}',"
                    "'{}',"
                    "'{}',"
                    "'{}',"
                    "'{}',"
                    "'{}',"
                    "'{}',"
                    "'{}',"
                    "'{}',"
                    "'{}',"
                    "'{}',"
                    "'{}',"
                    "'{}',"
                    "'{}',"
                    "'{}',"
                    "'{}',"
                    "'{}',"
                    "'{}',"
                    "'{}',"
                    "'{}',"
                    "'{}',"
                    "'{}',"
                    "'{}',"
                    "'{}',"
                    "'{}',"
                    "'{}',"
                    "'{}',"
                    "'{}',"
                    "'{}')").format(
        items['parcel_id'],
        items['tax_id'],
        items['geo_code'],
        items['state'],
        items['county'],
        items['owner'],
        items['owner_first'],
        items['owner_middle'],
        items['owner_last'],
        items['owner_suffix'],
        items['owner_nickname'],
        items['mailing_address'],
        items['mailing_address_line_1'],
        items['mailing_address_line_2'],
        items['mailing_address_city'],
        items['mailing_address_state'],
        items['mailing_address_postal_code'],
        items['property_address'],
        items['property_address_line_1'],
        items['property_address_line_2'],
        items['property_address_city'],
        items['property_address_state'],
        items['property_address_postal_code'],
        items['is_delinquent'],
        items['net_value'],
        '2019-12-13',
        items['owner_is_company'],
        items['has_same_mailing'],
        items['in_same_zip'],
        items['in_same_state']
    )
    execute_query(add_property)


def add_or_update_death_record(items):
    add_death_record = ("CALL death_records_save_or_update("
                        "'{}',"
                        "'{}',"
                        "'{}',"
                        "'{}',"
                        "'{}',"
                        "'{}',"
                        "'{}',"
                        "'{}',"
                        "'{}',"
                        "'{}',"
                        "'{}',"
                        "'{}',"
                        "'{}')").format(
        items['full_name'],
        items['name_title'],
        items['name_first'],
        items['name_middle'],
        items['name_last'],
        items['name_suffix'],
        items['name_nickname'],
        items['obituary_url'],
        items['obituary'],
        items['dob'],
        items['dod'],
        items['city_of_death'],
        items['state_of_death'])

    execute_query(add_death_record)


def get_death_search_record_id(year, first_name, last_name, state):
    get_id = ("SELECT "
              "id "
              "FROM "
              "death_searches "
              "WHERE "
              "year = '{}' "
              "AND first_name = '{}' "
              "AND last_name = '{}' "
              "AND state = '{}'").format(year, first_name, last_name, state)

    return execute_query(get_id)

