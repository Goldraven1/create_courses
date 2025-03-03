import json
import sys
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
def createConfig():
    with open(f'{dir_path}\\config\\config.json', 'w') as f:
            jsonFile = {
                 "host": "",
                 "port": "",
                 "password": "",
                 "dbname": "",
                 "user": ""
            }
            json.dump(jsonFile, f, indent=4)
    return
def getConfig():
    with open(f'{dir_path}\\config\\config.json', 'r') as f:
        jsonFile = json.load(f) 
        host = jsonFile['host']
        port = jsonFile['port']
        password = jsonFile['password']
        dbname = jsonFile['dbname']
        user = jsonFile['user']
    return host, port, password, dbname, user