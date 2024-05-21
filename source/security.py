
import json

json_file = "./data/credential.json"

def get_credentials(session,filename=json_file):

    # Load the JSON file
    with open(filename) as f:
        config = json.load(f)

    # Retrieve the values
    username = config[session]['username']
    password = config[session]['password']
    account = config[session]['account']
    warehouse = config[session]['warehouse']
    database = config[session]['database']
    schema = config[session]['schema']

    return [username,password,account,warehouse,database,schema]

def get_sessions(filename=json_file):

    # Load the JSON file
    with open(filename) as f:
        config = json.load(f)

    names = list(config.keys())
    print("Session Names:\n",names)
    return names