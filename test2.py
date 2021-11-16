import pymysql

rds_host='blackboxdatabase-1.cdnyxpurbpvu.us-east-2.rds.amazonaws.com'
name='blackboxadmin'
password='x6978293',
db_name='blackbox_database'

if __name__ == "__main__":
    try:
        conn = pymysql.connect(host=rds_host, user=name, password=str(password), database=db_name)
    except pymysql.MySQLError as e:
        print(e)
        print("ERROR: Unexpected error: Could not connect to MySQL instance.")