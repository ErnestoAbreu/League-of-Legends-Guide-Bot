from telegram import Update, ChatAction
from telegram.ext import CallbackContext
from riotwatcher import LolWatcher, ApiError
import json, error, os

with open('api_key.txt', 'r') as file: api_key = file.read()
lol_watcher = LolWatcher(api_key)

with open('data/to_region_code.json', 'r') as file: to_region_code = json.loads(file.read())
with open('data/region_of.json') as file: region_of = json.loads(file.read())

def config(update: Update, context: CallbackContext) -> None:
    with open('data/registered_users.json') as file: registered_users = json.loads(file.read())
    users = registered_users['users']
    info = users[str(update.message.from_user.id)]

    text = 'Settings:\n'
    text += 'Region: '
    if 'region' in info:
        text += region_of[info['region']]
    text += "   /config_region\n"
    text += 'Summoner: '
    if 'summoner' in info:
        text += info['summoner']
    text += "   /config_summoner\n"
    text += 'Permission to spectate: '
    if info['spectator_permission']:
        text += '✅   /config_spectator_off\n'
    else:
        text += '❌   /config_spectator_on\n'
    text += 'Time Zone: '
    if info['time_zone'] == 0:
        text += 'UTC'
    elif info['time_zone'] > 0:
        text += 'UTC +' + str(info['time_zone'])
    else:
        text += 'UTC ' + str(info['time_zone'])
    text += '    /config_time_zone\n'
    text += '\n'
    text += "With the Region you can omit the 'region' argument when required.\n"
    text += "With the Summoner you can receive information from your summoner easier. This one needs the Region config before.\n"
    text += "With the Permission to spectate you can receive information about the match you are playing. This one needs the Region and Summoner before.\n"
    
    update.message.reply_text(text)

def region(update: Update, context: CallbackContext) -> None:
    if len(context.args) != 1:
        update.message.reply_chat_action(ChatAction.TYPING)
        update.message.reply_text("How to use config_region command:\n/config_region 'region'\nExample: /config_region lan")
    elif context.args[0] in to_region_code:
        region = context.args[0]

        with open('data/registered_users.json', 'r') as file: registered_users = json.loads(file.read())
        users = registered_users['users']
        info = users[str(update.message.from_user.id)]

        info['region'] = region
        if 'summoner' in info:
            info.pop('summoner')

        with open('data/registered_users.json', 'w') as file: file.write(json.dumps(registered_users, indent=4, sort_keys=True))
        
        update.message.reply_chat_action(ChatAction.TYPING)
        update.message.reply_text("Your settings have been save correctly.")
    else:
        update.message.reply_chat_action(ChatAction.TYPING)
        update.message.reply_text("The region should be br, eune, euw, jp, kr, na, lan, las, oce, ru, tr")

def summoner(update: Update, context: CallbackContext) -> None:
    if len(context.args) != 1:
        update.message.reply_chat_action(ChatAction.TYPING)
        update.message.reply_text("How to use config_summoner command:\n/config_summoner 'summoner_name'\nExample: /config_summoner pentaculos3k")
    else: 
        summoner_name = context.args[0]

        with open('data/registered_users.json', 'r') as file: registered_users = json.loads(file.read())
        users = registered_users['users']
        info = users[str(update.message.from_user.id)]
        
        if 'region' in info:
            region = to_region_code[info['region']]
            region_name = region_of[info['region']]
            try:
                _summoner = lol_watcher.summoner.by_name(region, summoner_name)
            except ApiError as err:
                where = [
                    'module: config', 
                    'function: def summoner(update: Update, context: CallbackContext) -> None:', 
                    f'line 86: _summoner = lol_watcher.summoner.by_name({region}, {summoner_name})'
                ]
                chat_id = update.message.from_user.id
                why = f'Mientras se solicitaba los datos de invocador por nombre para configurar el invocador del usuario {chat_id}'
                error.response(where, err.response.status_code, why)
                
                if err.response.status_code == 404:
                    update.message.reply_chat_action(ChatAction.TYPING)
                    update.message.reply_text(f'Probably {summoner_name} no exists in {region_name} server.')
                else:
                    update.message.reply_chat_action(ChatAction.TYPING)
                    update.message.reply_text('An error has ocurred')
            else:
                info['summoner'] = _summoner['name']
                info['encrypted_summoner_id'] = _summoner['id']
                info['puuid'] = _summoner['puuid']
                
                with open('data/registered_users.json', 'w') as file: file.write(json.dumps(registered_users, indent=4, sort_keys=True))
                
                update.message.reply_chat_action(ChatAction.TYPING)
                update.message.reply_text("Your settings have been save correctly.")
        else:
            update.message.reply_chat_action(ChatAction.TYPING)
            update.message.reply_text("You should configure Region first.")

def spectator_on(update: Update, context: CallbackContext) -> None:
    with open('data/registered_users.json', 'r') as file: registered_users = json.loads(file.read())
    users = registered_users['users']
    info = users[str(update.message.from_user.id)]

    info['spectator_permission'] = True

    with open('data/registered_users.json', 'w') as file: file.write(json.dumps(registered_users, indent=4, sort_keys=True))

    update.message.reply_chat_action(ChatAction.TYPING)
    update.message.reply_text("Your settings have been save correctly.")

def spectator_off(update: Update, context: CallbackContext) -> None:
    with open('data/registered_users.json', 'r') as file: registered_users = json.loads(file.read())
    users = registered_users['users']
    info = users[str(update.message.from_user.id)]

    info['spectator_permission'] = False

    with open('data/registered_users.json', 'w') as file: file.write(json.dumps(registered_users, indent=4, sort_keys=True))

    update.message.reply_chat_action(ChatAction.TYPING)
    update.message.reply_text("Your settings have been save correctly.")

def time_zone(update: Update, context: CallbackContext) -> None:
    try:
        time = int(context.args[0])
    except:
        update.message.reply_chat_action(ChatAction.TYPING)
        update.message.reply_text('Should be a number between -12 and 12.')
    else:
        if -12 < time < 12:
            with open('data/registered_users.json', 'r') as file: registered_users = json.loads(file.read())
            users = registered_users['users']
            info = users[str(update.message.from_user.id)]

            info['time_zone'] = time

            with open('data/registered_users.json', 'w') as file: file.write(json.dumps(registered_users, indent=4, sort_keys=True))
            
            update.message.reply_chat_action(ChatAction.TYPING)
            update.message.reply_text("Your settings have been save correctly.")
        else:
            update.message.reply_chat_action(ChatAction.TYPING)
            update.message.reply_text('Should be a number between -12 and 12.')