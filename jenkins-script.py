import jenkins, pprint, sqlite3, os
from sqlite3 import Error
import datetime
import json
import requests
import time
from dotenv import load_dotenv

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
 
    return None


def create_table(conn, create_table_sql):
    """
    Create  table
    :param conn: the Connection object
    :param create_table_sql:
    :return:
    """
    cur = conn.cursor()
    cur.execute(create_table_sql)

def store_data(conn, sql, parameters):
    """
    Create a table data
    :param conn: the Connection object
    :param sql: the sql to run in db
    :param parameters: the store parameters
    :return:
    """
    cur = conn.cursor()
    cur.execute(sql, parameters)


def jenkins_connection(host, username, api_key):

    """
    Create Jenkins connection
    :param host: the host of the jenkins api
    :param user: the username of the jenkins api
    :param api_key: the api key of the jenkins api
    return
    """
    try: 
        server = jenkins.Jenkins(
            host,
            username=username,
            password=api_key
        )

        return server
    except Exception as e:
        print(e)
    
    return None

def jenkin_server_jobs(server):
    """
    Get all the jenkins job names
    """
    job_names = []

    jobs = server.get_jobs()

    for job in jobs:
        job_names.append(job['fullname'])
    
    return job_names

def get_database_file():
    """
    Create the database file in the created database folder
    for sqlite
    """
    db_folder = os.getcwd() + '/database'
        
    database = db_folder + '/jenkins_jobs.sqlite'
    

    if not os.path.exists(database):
        f = open(database, 'w') 
        f.close()
    
    return database

def select_all_jenkin_jobs(conn):
    """
    Query all rows in the jenkin_jobs table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM jenkin_jobs")
 
    rows = cur.fetchall()
 
    for row in rows:
        print(row, "\n")

def jenkins_job_status(host, username, api_key, job_name):
        
        try:
            url  = "http://%s:%s@%s/job/%s/lastBuild/api/json" %(username, api_key, host,  job_name)
            print(url)
            while True:
                data = requests.get(url).json()
                if data['building']:
                    # if the current job is stiil bulding wait for 1 minutes
                    time.sleep(60)
                else:
                    if data['result'] == "SUCCESS":
                            return 1
                    else:
                            return 0
        except Exception as e:
            print(e)
            return 0
 

def main():
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    # Jenkin API credentials
    schema = os.environ.get("SCHEMA")
    domain_name = os.environ.get("DOMAIN_NAME")
    username = os.environ.get("USERNAME")
    api_key = os.environ.get("API_KEY")
    host = schema + domain_name
    
    # SQL to create jenkin_jobs table
    sql = """
        CREATE TABLE IF NOT EXISTS jenkin_jobs (
            id integer PRIMARY KEY,
            job text(225) NOT NULL,
            status TINYINT(1) NOT NULL,
            create_at text(15)  NOT NULL
        );
    """

    # SQL insert data
    sql_insert = """
        INSERT INTO jenkin_jobs (
            job,
            status,
            create_at
        )
        VALUES (?, ?, ?)
    """

    # sql_db
    database = get_database_file()

    # Create sqlite database connection
    conn = create_connection(database)

    with conn:
        try:

            # Create table if it does not exist
            create_table(conn, sql)
        except Exception as e:
            print(e)

        # Create jenkins api connection
        jenkins_server = jenkins_connection(host, username, api_key)

        # Get all jobs at the jenkins api
        jenkin_jobs = jenkin_server_jobs(jenkins_server)


        for job in jenkin_jobs:
            job_status = jenkins_job_status(domain_name, username, api_key, job)
            today = str(datetime.date.today())
            jenkin_job = (job, job_status, today)
            store_data(conn, sql_insert, jenkin_job)

        select_all_jenkin_jobs(conn)

if __name__ == '__main__':
    main()
