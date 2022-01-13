from riotwatcher import LolWatcher , ApiError
import requests, json, urllib, os

with open('data/api_key.txt', 'r') as file: api_key = file.read()
lol_watcher = LolWatcher(api_key)

version = json.loads(requests.get('https://ddragon.leagueoflegends.com/api/versions.json').text)
last_version = version[0]

""" Downloads images """
# # Descarga las imagenes de los champion de data dragon
# with open('json/champions_id_dictionary.json', 'r') as file: data = json.loads(file.read())
# data: dict
# for key,value in data.items():
#     if os.path.exists(f'images/champion/{value}.png'):
#         print(f'{value} already exists')
#     else:
#         urllib.request.urlretrieve(f"http://ddragon.leagueoflegends.com/cdn/{last_version}/img/champion/{value}.png", f"images/champion/{value}.png")
#         print(f'{value} download successfuly')


''' CHAMPION '''
# champion = json.loads( requests.get(f'http://ddragon.leagueoflegends.com/cdn/{last_version}/data/en_US/champion.json').text )

# # Crea un diccionario con key:id de los champions
# champions_id_dictionary = {}
# for key,value in champion['data'].items():
#     champions_id_dictionary[value['key']] = value['id']
# with open('json/champions_id_dictionary.json', 'w') as file:
#     file.write( json.dumps(champions_id_dictionary, indent=4) )

# # Crea un diccionario con id,name y key de los champions
# champions_key_dictionary = {}
# with open('json/champions_id_dictionary.json', 'r') as file: champions_id_dictionary = json.loads( file.read() )
# for key,value in champions_id_dictionary.items():
#     champions_key_dictionary[value] = key
#     champions_key_dictionary[value.lower()] = key
# with open('json/champions_name_dictionary.json', 'r') as file:
#     champions_name_dictionary = json.loads( file.read() )
# for key,value in champions_name_dictionary.items():
#     champions_key_dictionary[value] = key
#     champions_key_dictionary[value.lower()] = key
# with open('json/champions_key_dictionary.json', 'w') as file:
#     file.write( json.dumps(champions_key_dictionary, indent=4, sort_keys=True) )


''' ITEM '''
# data = json.loads(requests.get(f'http://ddragon.leagueoflegends.com/cdn/{last_version}/data/en_US/item.json').text)

# # Crea un diccionario con nombre:id de los items
# items_name_to_id = {}
# for key,value in data['data'].items():
#     items_name_to_id[value['name']] = key
# with open('json/items_name_to_id.json', 'w') as file:
#     file.write( json.dumps(items_name_to_id, indent=4, sort_keys=True) )

# # Crea un diccionario de tipo y lista de items
# items = data['data']
# items_by_type = {}
# items_by_type['Basic'] = []
# items_by_type['Normal'] = []
# items_by_type['Legendary'] = []
# items_by_type['Mythic'] = []
# for key,item in items.items():
#     if 'depth' not in item:
#         items_by_type['Basic'].append(key)
#     elif item['depth'] == 2:
#         items_by_type['Normal'].append(key)
#     else:
#         if item['description'].find('rarityMythic') == -1:
#             items_by_type['Legendary'].append(key)
#         else:
#             items_by_type['Mythic'].append(key)
# with open('json/items_by_type.json', 'w') as file:
#     file.write( json.dumps(items_by_type, indent=4) )