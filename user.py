from telegram import Update, ChatAction, ParseMode
from telegram.ext import Updater, CallbackContext
from riotwatcher import LolWatcher, ApiError
from datetime import datetime, timedelta
import json, command, error, threading, time, os 

with open('data/api_key.txt', 'r') as file: api_key = file.read()
lol_watcher = LolWatcher(api_key)

with open('json/to_region_code.json') as file: to_region_code = json.loads(file.read())
with open('json/region_of.json') as file: region_of = json.loads(file.read())

def check(update: Update , context: CallbackContext) -> None:
    with open(f'messages/user_{update.message.from_user.id}.log', 'a') as file:
        file.write(str(datetime.now()) + ' ' + update.message.text + '\n')

    with open('data/registered_users.json', 'r') as file: registered_users = json.loads(file.read())
    users = registered_users['users']

    if str(update.message.from_user.id) not in users:
        users[str(update.message.from_user.id)] = { "username": update.message.from_user.username, 'last_gameId': -1, 'spectator_permission': True, 'time_zone': 0 }
        registered_users['counter'] += 1

    with open('data/registered_users.json', 'w') as file: 
        file.write(json.dumps(registered_users, indent=4, sort_keys=True))

def LiveMatch(update: Updater, chat_id: str, user: dict) -> None:
    region = to_region_code[user['region']]
    summoner_name = user['summoner']
    encrypted_summoner_id = user['encrypted_summoner_id']
    try:
        live_match = lol_watcher.spectator.by_summoner(region, encrypted_summoner_id)
    except ApiError as err:
        where = [
            'module: user', 
            'function: def persistent(update: Updater, chat_id: str, user: dict) -> None:', 
            f'line 45: live_match = lol_watcher.spectator.by_summoner({region}, {encrypted_summoner_id})'
        ]
        why = f'Mientras se solicitaba los datos de espectador por invocador del usuario {chat_id}'
        if err.response.status_code != 404:
            error.response(where, err.response.status_code, why)

        if(err.response.status_code != 404 and err.response.status_code != 403):
            print('* Error encontrado en: ', chat_id)
            update.bot.send_chat_action(chat_id, ChatAction.TYPING)
            update.bot.send_message(chat_id, 'An error has ocurred while I request your current match data.')
            time.sleep(600)
    except:
        print('ERROR PARA', chat_id)
    else:
        if live_match['gameMode'] == 'CLASSIC' and live_match['gameId'] != user['last_gameId']:
            participants = live_match['participants']
    
            with open('json/champions_name_dictionary.json') as file: champs = json.loads(file.read())

            teamA = participants[0]['teamId']
            teamA_text = ''
            teamB_text = ''
            for player in participants:
                time.sleep(1)
                summoner = lol_watcher.summoner.by_name(region, player['summonerName'])
                encrypted_summoner_id = summoner['id']
                try:
                    champion_mastery = lol_watcher.champion_mastery.by_summoner_by_champion(region, encrypted_summoner_id, player['championId'])
                except:
                    champion_mastery = { 'championLevel': 0 }
                finally:
                    summoner_name = player['summonerName']
                    summoner_level = summoner['summonerLevel']
                    champion_id = player['championId']
                    champion_mastery_level = champion_mastery['championLevel']
                    champion_name = champs[ str(champion_id) ] 
                    soloq_text = ''
                    flex_text = ''
                    if player['teamId'] == teamA:
                        teamA_text += f"🧑‍💻 <b>{summoner_name}</b> <code>lvl</code> <code>{summoner_level} </code> -  <b><i>{champion_name}</i></b> <code>Mlvl</code> <code>{champion_mastery_level}</code>\n"
                        for queue in lol_watcher.league.by_summoner(region , encrypted_summoner_id):
                            if queue["queueType"] == "RANKED_SOLO_5x5":
                                tier = queue['tier']
                                rank = queue['rank']
                                soloq_text += f'        SoloQ: <b><u>{tier} {rank}</u></b>'
                            if queue["queueType"] == "RANKED_FLEX_SR":
                                tier = queue['tier']
                                rank = queue['rank']
                                flex_text += f'        Flex: <b><u>{tier} {rank}</u></b>'
                        if len(soloq_text) != 0:
                            teamA_text += soloq_text
                        if len(flex_text) != 0:
                            teamA_text += flex_text
                        if len(soloq_text) != 0 or len(flex_text) != 0:
                            teamA_text += '\n'
                        teamA_text += '\n'
                    else:
                        teamB_text += f"🧑‍💻 <b>{summoner_name}</b> <code>lvl</code> <code>{summoner_level} </code> -  <b><i>{champion_name}</i></b> <code>Mlvl</code> <code>{champion_mastery_level}</code>\n"
                        for queue in lol_watcher.league.by_summoner(region , encrypted_summoner_id):
                            if queue["queueType"] == "RANKED_SOLO_5x5":
                                tier = queue['tier']
                                rank = queue['rank']
                                soloq_text += f'        SoloQ: <b><u>{tier} {rank}</u></b>'
                            if queue["queueType"] == "RANKED_FLEX_SR":
                                tier = queue['tier']
                                rank = queue['rank']
                                flex_text += f'        Flex: <b><u>{tier} {rank}</u></b>'
                        if len(soloq_text) != 0:
                            teamB_text += soloq_text
                        if len(flex_text) != 0:
                            teamB_text += flex_text
                        if len(soloq_text) != 0 or len(flex_text) != 0:
                            teamB_text += '\n'
                        teamB_text += '\n'
    
            update.bot.send_message(chat_id, 'You just started a game with:\n' + teamA_text + '🆚🆚🆚🆚🆚🆚🆚🆚🆚🆚🆚🆚🆚🆚🆚🆚🆚🆚\n\n' + teamB_text, parse_mode=ParseMode.HTML)
            
            user['last_gameId'] = live_match['gameId']
            with open('data/registered_users.json', 'r') as file: registered_users = json.loads(file.read())
            users = registered_users['users']
            users[chat_id] = user
            
            with open('data/registered_users.json', 'w') as file: file.write(json.dumps(registered_users, indent=4, sort_keys=True))

def spectator(update: Updater) -> None:
    while True:
        with open('data/registered_users.json', 'r') as file: registered_users = json.loads(file.read())
        users = registered_users['users']

        for key,value in users.items():
            if value['spectator_permission'] and 'summoner' in value:
                thread = threading.Thread(target=LiveMatch, args=(update, key, value))
                thread.start()
                time.sleep(30)

    

    

