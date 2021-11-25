import pymysql
from flaskw import constants as constants

rds_host='blackboxdatabase.cdnyxpurbpvu.us-east-2.rds.amazonaws.com'
name='blackboxadmin'
password='x6978293',
db_name='blackbox_database'

if __name__ == "__main__":
    try:
        conn = pymysql.connect(host=constants.mysql_host, user=constants.mysql_user, password=constants.mysql_password, 
                               database=constants.mysql_db)
    except pymysql.MySQLError as e:
        print(e)
        print("ERROR: Unexpected error: Could not connect to MySQL instance.")