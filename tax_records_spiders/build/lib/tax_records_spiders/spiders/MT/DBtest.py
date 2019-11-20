import mysql.connector

cnx = mysql.connector.connect(user='admin', password='mX5FBbbuaF_Kvn?F',
                              host='tax2profit-dev.cq1pnj9ijzbf.us-east-2.rds.amazonaws.com',
                              database='tax2profit_dev')
cursor = cnx.cursor()

add_property = ("CALL select_or_insert("
                "'04220029402080000',"
                "'1043308',"
                "'04-2200-29-4-02-08-0000',"
                "'MT',"
                "'Missoula County',"
                "'Donald Trump',"
                "'OWNER_FIRST_NAME',"
                "'OWNER_MIDDLE_NAME',"
                "'OWNER_LAST_NAME',"
                "'OWNER_SUFFIX',"
                "'OWNER_NICK_NAME',"
                "'C/O MISSOULA TAEKWANDO 2305 S GRANT ST MISSOULA, MT 598016539',"
                "'MAILING_ADDRESS_LINE_1',"
                "'MAILING_ADDRESS_LINE_2',"
                "'MAILING_ADDRESS_CITY',"
                "'MT',"
                "'MAILING_ADDRESS_POSTAL_CODE',"
                "'2309 GRANT ST, MISSOULA MT 59801',"
                "'PROPERTY_ADDRESS_LINE_1',"
                "'PROPERTY_ADDRESS_LINE_2',"
                "'PROPERTY_ADDRESS_CITY',"
                "'PROPERTY_ADDRESS_STATE',"
                "'82435',"
                "'true',"
                "'net_value',"
                "'2019-12-13',"
                "'false',"
                "'true',"
                "'true',"
                "'true')")


update_delinquent_status = ("CALL select_or_insert_is_delinquent("
                            "'04220029402080000',"
                            "'1043308',"
                            "'MT',"
                            "'Missoula County',"
                            "'true')")

send_scraper_error = ("INSERT INTO `scraper_errors`"
                       "(`parcel_id`,"
                       "`state`,"
                       "`county`,"
                       "`scraper_name`,"
                       "`error`)"
                       "VALUES"
                       "('04220029402080000',"
                       "'MT',"
                       "'Missoula County',"
                       "'scraper_name_goes_here',"
                       "'New Test Error...')")

print(add_property)

# Insert property information
cursor.execute(add_property)

# Make sure data is committed to the database
cnx.commit()

cursor.close()
cnx.close()