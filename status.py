from datetime import datetime
import json
import os

class Data:
    def __init__(self):
        with open('data/api_key.txt', 'r') as file: api_key = file.read()
        with open('data/data.json', 'r') as file: data = json.loads(file.read())
        with open('data/last_version.txt', 'r') as file: last_version = file.read()
        with open('data/registered_users.json', 'r') as file: registered_users = json.loads(file.read())
        with open('data/token.txt', 'r') as file: token = file.read()
        
        self.api_key = api_key
        self.data = data
        self.last_version = last_version
        self.registered_users = registered_users
        self.token = token

    def save_data(self) -> None:
        with open('data/data.json', 'w') as file:
            file.write(json.dumps(self.data, indent=4, sort_keys=True))

    def save_version(self) -> None: 
        with open('data/last_version.txt', 'w') as file: 
            file.write(self.last_version)

    def save_registered_users(self) -> None:
        with open('data/registered_users.json', 'w') as file:
            file.write(json.dumps(self.registered_users, indent=4, sort_keys=True))

class Json:
    def __init__(self):
        with open('json/champions_id_dictionary.json') as file: champions_id = json.loads(file.read())
        with open('json/champions_key_dictionary.json') as file: champions_key = json.loads(file.read())
        with open('json/champions_name_dictionary.json') as file: champions_name = json.loads(file.read())
        with open('json/continent_of.json', 'r') as file: continent_of = json.loads(file.read())
        with open('json/items_by_type.json', 'r') as file: items_by_type = json.loads(file.read())
        with open('json/items_name_to_id.json', 'r') as file: items_name_to_id = json.loads(file.read())
        with open('json/match_of.json', 'r') as file: match_of = json.loads(file.read())
        with open('json/region_of.json', 'r') as file: region_of = json.loads(file.read())
        with open('json/to_region_code.json', 'r') as file: to_region_code = json.loads(file.read())

        self.champions_id = champions_id
        self.champions_key = champions_key
        self.champions_name = champions_name
        self.continent_of = continent_of
        self.items_by_type = items_by_type
        self.items_name_to_id = items_name_to_id
        self.match_of = match_of
        self.region_of = region_of
        self.to_region_code = to_region_code

class Text:
    def __init__(self):
        with open('text/config_region.txt') as file: config_region = file.read()
        with open('text/config_summoner.txt') as file: config_summoner = file.read()
        with open('text/config.txt') as file: config = file.read()
        with open('text/free_champions_help.txt') as file: free_champions_help = file.read()
        with open('text/help.txt') as file: help = file.read()
        with open('text/item.txt') as file: item = file.read()
        with open('text/region.txt') as file: region = file.read()
        with open('text/spectator_help.txt') as file: spectator_help = file.read()
        with open('text/start.txt') as file: start = file.read()
        with open('text/summoner_help.txt') as file: summoner_help = file.read()
        
        self.config_region = config_region
        self.config_summoner = config_summoner
        self.config = config
        self.free_champions_help = free_champions_help
        self.help = help
        self.item = item
        self.region = region
        self.spectator_help = spectator_help
        self.start = start
        self.summoner_help = summoner_help

class Status:
    def __init__(self):
        self.text = Text()
        self.data = Data()
        self.json = Json()

    def write(self, text: str) -> None:
        with open('data/status.log', 'a') as file:
            file.write(str(datetime.now()) + '  ' + text + '\n')

    def save_message(self, message: str, user_id: int) -> None:
        date = datetime.now().strftime("%Y_%m_%d")
        os.makedirs(f'messages/{date}', exist_ok=True)

        with open(f'messages/{date}/{user_id}.log', 'a') as file:
            file.write(str(datetime.now()) + ' ' + message + '\n')