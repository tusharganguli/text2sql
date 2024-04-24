
import json

def get_credentials(filename="credential.json"):

    # Load the JSON file
    with open(filename) as f:
        config = json.load(f)

    # Retrieve the values
    username = config['snowflake_database']['username']
    password = config['snowflake_database']['password']
    account = config['snowflake_database']['account']
    warehouse = config['snowflake_database']['warehouse']
    database = config['snowflake_database']['database']
    schema = config['snowflake_database']['schema']

    return [username,password,account,warehouse,database,schema]

