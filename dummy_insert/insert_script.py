from pathlib import Path
import os
from dotenv import load_dotenv
from typing import Tuple
import mariadb
import csv

def retrieve_env_vars(path:str) -> Tuple[str, str, str, str]:
    '''pull the local .env credentials  for use in the connection
    
    Checks the local project file system for the .env file and loads the database access credentials.
    
    Args:
        path: the relative file path to the .env file
        
    Return:
        db_username
        db_password
        host ip
        db_name'''
    load_dotenv(path)
    DB_USER = os.getenv('DB_USERNAME')
    DB_PASS = os.getenv('DB_PASSWORD')
    host = os.getenv('DB_HOST')
    name = os.getenv('DB_NAME')
    print(f"Using credentials\nHost:{host}\nDB Name:{name}\nUsername:{DB_USER}\nPwd:{DB_PASS}")
    return DB_USER, DB_PASS, host, name


def get_sql_from_csv(csv_file_path:str,table_name:str) -> str:
    """Create a sql statement from the specified CSV filepath"""
    print(f"Writing SQL Statement for {table_name} table")
    try:
        with open(Path(__file__).parent / csv_file_path, encoding='utf8', mode='r') as file:
            csv_file = csv.reader(file)
            headers = map((lambda x: '`'+x+'`'), next(csv_file))
            insert_statement_start = f'INSERT INTO {table_name} (' + ", ".join(headers) + ") VALUES "
            sql_statement = insert_statement_start
            for row in csv_file:
                values = map((lambda x: '"'+x+'"'), row)
                values_line = "("+ ", ".join(values) +"),"
                sql_statement = sql_statement + values_line
                print(values_line)
            sql_statement = sql_statement[:-1]
            sql_statement = sql_statement + ";"
    except OSError:
        print(f"Failed to open file at {csv_file_path}")
        return ''
    return sql_statement


def insert_table_values(sql_conn:mariadb.Connection, table_name:str, csv_file_path:str):
    
    db_cursor = sql_conn.cursor()
    sql_statement = get_sql_from_csv(csv_file_path, table_name)
    try:
        db_cursor.execute(sql_statement)
        sql_conn.commit()
        print(f"Succesfully populated table {table_name}")
    except:
        sql_conn.rollback()


if __name__ == '__main__':
    print("ticket_hive Database Insertion Script")
    db_user, db_pass, db_host, db_name = retrieve_env_vars('../.env')

    connection = mariadb.connect(
            host = db_host,
            user = db_user,
            password = db_pass,
            database= db_name
        )
    
    try:
        print(f"Succesfully connected to DB {db_name}\nStarting insert operations...")
        insert_table_values(connection, "event", "event.csv")  
        insert_table_values(connection, "user", 'user.csv')
        insert_table_values(connection, "ticket", "ticket.csv")
        insert_table_values(connection, "ticket_listing", "ticket_listing.csv")


    finally:
        print("Closing connection")
        connection.close()