from datetime import datetime
import json

class Status:
    def write(self, text: str) -> None:
        with open('data/status.log', 'a') as file:
            file.write(str(datetime.now()) + '  ' + text + '\n')
    

    """ Get Data """
    def get_users_data(self) -> dict:
        with open('data/registered_users.json', 'r') as file:
            registered_users = json.loads( file.read() )
        
        return registered_users
    
    def get_token(self) -> str:
        with open('data/token.txt', 'r') as file:
            token = file.read()
        
        return token
    
    def get_riot_api(self) -> str:
        with open('data/api_key.txt', 'r') as file:
            api_key = file.read()

        return api_key

    def get_last_version(self) -> str:
        with open('data/last_version.txt', 'r') as file:
            last_version = file.read()

        return last_version


    """ Save Data """
    def save_users_data(self, registered_users: dict) -> None:
        with open('data/registered_users.json', 'w') as file:
            file.write( json.dumps(registered_users, indent=4, sort_keys=True) )

    def save_version(self, version: str) -> None: 
        with open('data/last_version.txt', 'w') as file: 
            file.write(version)
