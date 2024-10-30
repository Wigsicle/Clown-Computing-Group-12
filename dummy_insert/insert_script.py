from pathlib import Path
import os
from dotenv import load_dotenv
from typing import Tuple
import mariadb
import csv

started_transactions:int = 0
completed_transactions:int = 0

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


def insert_sql_from_csv(table_name:str,csv_file_path:str) -> str:
    """Create a sql statement from the specified CSV filepath"""
    print(f"Writing SQL Statement for {table_name} table")
    try:
        with open(Path(__file__).parent / csv_file_path, encoding='utf8', mode='r') as file:
            csv_file = csv.reader(file)
            headers = map((lambda x: '`'+x+'`'), next(csv_file))
            insert_statement_start = f'INSERT INTO {table_name} (' + ", ".join(headers) + ") VALUES "
            sql_statement = insert_statement_start
            for row in csv_file:
                #values = map((lambda x: '"'+x+'"'), row)
                ''' ["x","y","z"] '''
                values:list = []
                for val in row:
                    if val != 'None':
                        values.append('"' + val + '"')
                    else:
                        values.append("NULL")
                    # ultra super cursed way to handle None to NULL vals
                values_line = "("+ ", ".join(values) +"),"
                sql_statement = sql_statement + values_line
                print(values_line)
            sql_statement = sql_statement[:-1]
            sql_statement = sql_statement + ";"
    except OSError:
        print(f"Failed to open file at {csv_file_path}")
        return ''
    return sql_statement


def execute_sql(sql_conn:mariadb.Connection, sql_statement:str, table_name:str='blank'):
    
    db_cursor = sql_conn.cursor()

    global started_transactions  
    global completed_transactions
    started_transactions += 1
    try:
        db_cursor.execute(sql_statement)
        sql_conn.commit()
        print(f"Succesfully run statement for {table_name} table")
        completed_transactions += 1
    except mariadb.Error as e:
        print(e)
    except:
        sql_conn.rollback()


def update_missing_values(table_name:str, csv_file_path:str, col_name:list[str]):
    col_count = col_name.count
    col_name_num:dict = []
    row_count = 1 # find column that is iterable 
    
    try:
        with open(Path(__file__).parent / csv_file_path, encoding='utf8', mode='r') as file:
            csv_file = csv.reader(file)
    except OSError:
        print(f"Failed to open file at {csv_file_path}")

    # CSV Header Row Section
    for col in col_name: # find csv column value that matches column name argument
        return    
    
    # CSV Body Section
    for row in csv_file:
        sql_statement = f'UPDATE {table_name} SET {col_name[0]} = {row} WHERE '

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
        execute_sql(connection, insert_sql_from_csv("event", "event.csv"),'event')
        execute_sql(connection, insert_sql_from_csv("user", 'user.csv'),'user')
        execute_sql(connection, insert_sql_from_csv("ticket", "ticket.csv"),'ticket')
        execute_sql(connection, insert_sql_from_csv("ticket_listing", "ticket_listing.csv"),'ticket_listing')


    finally:
        print(f"Transactions Completed: {completed_transactions}/{started_transactions}\nClosing connection")
        connection.close()