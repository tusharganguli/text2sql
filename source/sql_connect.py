
import snowflake.connector
import pandas as pd
from flask import session

from source.security import get_credentials
class SQLConnect:
    def __init__(self,session_name=""):
        try: 
            if session_name == "":
                session_name = session.get('session')
            else:
                session_name=session_name
            # Snowflake connection parameters
            username,password,account,warehouse,database,schema = get_credentials(session_name)

            self.conn = snowflake.connector.connect( user=username, password=password,
                                                account=account, warehouse=warehouse,
                                                database=database, schema=schema
                                              )
        except snowflake.connector.errors.DatabaseError as e:
            err_msg = e
            # Handle the error (e.g., log it, display a message to the user, etc.)
            print("Error:", e)
            raise Exception("Error connecting to Database.")

    def __del__(self):
        self.conn.close()

    def get_sql_data(self, sql_stmt):                
        column_names = []
        rows = []

        try:
            cur = self.conn.cursor()
            cur.execute(sql_stmt)
            column_names = [desc[0] for desc in cur.description]    
            rows = cur.fetchmany(1000)
            cur.close()            
        except Exception as e:
            # Handle other types of errors
            print("Error in get_sql_data:",e)
            raise Exception("Error in retrieving data.")
        
        return column_names,rows
    
    def match_data(self, word, table_name, column_names):
        
        sql_stmt =  """ SELECT COUNT(*) AS count_of_occurrences
                        FROM {table_name}
                        WHERE {column_name} ILIKE '%{word}%';
                    """
        column_lst = []
        try:
            cur =  self.conn.cursor()
            for column in column_names:
                fmt_sql_stmt = sql_stmt.format(table_name=table_name, column_name=column, word=word)
                #print("SQL Statement to execute:", fmt_sql_stmt)
                cur.execute(fmt_sql_stmt)
                row = cur.fetchall()
                #print(row[0][0])
                if row[0][0] > 0:
                    column_lst.append(column)
            cur.close()
        except Exception as e:
            print("Exception in SQLConnect:match_data:",e)
            raise Exception("Error retrieving data for matching query.:",fmt_sql_stmt)
        
        return column_lst

    def match_data2(self, word, table_name, column_names):

        sql_stmt =  "SELECT * FROM {table_name} WHERE"
        sql_stmt = sql_stmt.format(table_name=table_name)

        column_lst = []
        first = True
        try:
            cur =  self.conn.cursor()
            for column in column_names:
                if first:
                    clause = " '{column_name}' ILIKE '%{word}%'"
                    first = False
                else:
                    clause = " or '{column_name}' ILIKE '%{word}%'"
                sql_stmt += clause
                sql_stmt = sql_stmt.format(column_name=column, word=word)
                #print("SQL Statement to execute:", fmt_sql_stmt)
            sql_stmt += ";"
            #print("Final SQL Statement:",sql_stmt)
            cur.execute(sql_stmt)
            rows = cur.fetchall()
            column_names = [desc[0] for desc in cur.description]
            cur.close()

            df = pd.DataFrame(rows,columns=column_names)
            #print("Fetched Data:\n",df)

            for column_name in df.columns:
                matches = []
                column_data = df[column_name]
                column_data = column_data.unique()
                # Check if the column data contains the keyword
                #print("Column Name:", column_name)
                for value in column_data:
                    if value is None or not isinstance(value, str):
                        continue
                    if word.lower() in value.lower():
                        #print("Word:{}, Value:{}".format(word.lower(),value.lower()))
                        matches.append(value)
                #matches = [str(value) for value in column_data if value is not None and isinstance(value, str) and word.lower() in value.lower()]
                # If matches are found, print the column name
                if matches:
                    column_lst.append(column_name)    
            
        except Exception as e:
            print("Exception in SQLConnect:match_data:",e)
            raise Exception("Error retrieving data for matching query:",sql_stmt)

        return column_lst
