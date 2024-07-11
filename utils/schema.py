
import traceback
import json
import sys
import os
from flask import session

# Get the absolute path to current file
current_file_path = os.path.abspath(__file__)
utils_folder = os.path.dirname(current_file_path)
parts = utils_folder.split("utils")
# Add the root directory to sys.path
sys.path.append(parts[0])

import source.sql_connect as sc

class Schema:
    
    def __init__(self, session):
        try:
            self.file_name = "./utils/retrieve_schema.json"
            self.session = session
            self.sql_connect = sc.SQLConnect(session)
            # Load the JSON file
            with open(self.file_name) as f:
                self.json_data = json.load(f)

        except Exception as e:
            print("Error Initializing SQL Connection:",e)
            traceback.print_exc()

    def get_table_names(self):
        get_tablenames_sql_stmt = self.json_data[self.session]['get_tablenames']
        table_names = self.sql_connect.get_sql_data(get_tablenames_sql_stmt)
        return table_names

    def get_column_data(self, table_name):
        columndata_sql_stmt = self.json_data[self.session]['get_columnnames']
        columndata_sql_stmt = columndata_sql_stmt.format(table_name)
        #print("Get Column Names SQL Statement:\n",get_columnnames_sql_stmt)
        column_data = self.sql_connect.get_sql_data(columndata_sql_stmt)
        return column_data

    def generate_schema(self, table_name, column_data):
        columns = []
        for column_name, data_type in column_data:
            columns.append(f"{column_name} {data_type}")

        return f"CREATE TABLE {table_name} ({','.join(columns)});"

session_name = "Covid"
s = Schema(session_name)
table_names = s.get_table_names()
table_names = [name[0] for name in table_names[1]]
#print("Table Name:",table_names)
idx = 0

session_info = {}
create_table_schemas = {}

for t in table_names:
    print("Table Name:",t)
    column_data = s.get_column_data(t)
    #print("Column Data:",column_data)
    create_schema = s.generate_schema(t, column_data[1])
    create_table_schemas[t] = create_schema
    idx += 1

session_info[session_name] = create_table_schemas

# Write create table schemas to a JSON file
with open('./data/covid.json', 'w') as json_file:
    json.dump(session_info, json_file, indent=4)
