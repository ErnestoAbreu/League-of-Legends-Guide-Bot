from telegram import Update, ChatAction
from telegram.ext import CallbackContext
from riotwatcher import LolWatcher, ApiError
import json

from status import Status
import error


# Global variables
status = Status()

api_key = status.get_riot_api()
lol_watcher = LolWatcher(api_key)

with open('json/region_of.json') as file: region_of = json.loads( file.read() )
with open('json/to_region_code.json', 'r') as file: to_region_code = json.loads( file.read() )


# Functions
def config(update: Update, context: CallbackContext) -> None:
    registered_users = status.get_users_data()
    users = registered_users['users']
    user = users[str(update.message.from_user.id)]

    text = 'Settings:\n'
    
    text += 'Region: '
    if 'region' in user:
        text += region_of[user['region']]
    text += "   /config_region\n"
    
    text += 'Summoner: '
    if 'summoner' in user:
        text += user['summoner']
    text += "   /config_summoner\n"

    text += 'Notify: '
    if user['notify_update']:
        text += '✅   /config_notify_off\n'
    else:
        text += '❌   /config_notify_on\n'

    text += 'Spectate: '
    if user['spectator_permission']:
        text += '✅   /config_spectator_off\n'
    else:
        text += '❌   /config_spectator_on\n'
    
    text += 'Time Zone: '
    if user['time_zone'] == 0:
        text += 'UTC'
    elif user['time_zone'] > 0:
        text += 'UTC +' + str(user['time_zone'])
    else:
        text += 'UTC ' + str(user['time_zone'])
    text += '    /config_time_zone\n'
    text += '\n'
    
    with open('text/config.txt', 'r') as file: text += file.read()

    update.message.reply_text(text)

def region(update: Update, context: CallbackContext) -> None:
    if len(context.args) != 1:
        update.message.reply_chat_action(ChatAction.TYPING)
        update.message.reply_text("How to use config_region command:\n/config_region 'region'\nExample: /config_region lan")
    elif context.args[0] in to_region_code:
        region = context.args[0]

        registered_users = status.get_users_data()
        users = registered_users['users']
        user = users[str(update.message.from_user.id)]

        user['region'] = region
        if 'summoner' in user:
            user.pop('summoner')

        status.save_users_data(registered_users)
        
        update.message.reply_chat_action(ChatAction.TYPING)
        update.message.reply_text("Your settings have been save correctly.")
    else:
        update.message.reply_chat_action(ChatAction.TYPING)
        update.message.reply_text("The region should be br, eune, euw, jp, kr, na, lan, las, oce, ru, tr")


def summoner(update: Update, context: CallbackContext) -> None:
    if len(context.args) == 0:
        update.message.reply_chat_action(ChatAction.TYPING)
        update.message.reply_text("How to use config_summoner command:\n/config_summoner 'summoner_name'\nExample: /config_summoner pentaculos3k")
    else: 
        summoner_name = ''
        for s in context.args:
            summoner_name += s + ' '
        summoner_name = summoner_name[:len(summoner_name)-1]

        registered_users = status.get_users_data()
        users = registered_users['users']
        user = users[str(update.message.from_user.id)]
        
        if 'region' in user:
            region = to_region_code[user['region']]
            region_name = region_of[user['region']]
            try:
                _summoner = lol_watcher.summoner.by_name(region, summoner_name)
            except ApiError as err:
                if err.response.status_code == 404:
                    update.message.reply_chat_action(ChatAction.TYPING)
                    update.message.reply_text(f'Probably {summoner_name} no exists in {region_name} server.')
                else:
                    update.message.reply_chat_action(ChatAction.TYPING)
                    update.message.reply_text('An error has ocurred.')
                    status.write(f'Error {err.response.status_code} for summoner endpoint: {region}, {summoner_name} in config.summoner.')
            else:
                user['summoner'] = _summoner['name']
                user['encrypted_summoner_id'] = _summoner['id']
                user['puuid'] = _summoner['puuid']
                
                status.save_users_data(registered_users)
                
                update.message.reply_chat_action(ChatAction.TYPING)
                update.message.reply_text("Your settings have been save correctly.")
        else:
            update.message.reply_chat_action(ChatAction.TYPING)
            update.message.reply_text("You should configure Region first.")


def notify(update: Update, context: CallbackContext, state: bool) -> None:
    registered_users = status.get_users_data()
    users = registered_users['users']
    user = users[str(update.message.from_user.id)]

    user['notify_update'] = state

    status.save_users_data(registered_users)

    update.message.reply_chat_action(ChatAction.TYPING)
    update.message.reply_text("Your settings have been save correctly.")

def notify_on(update: Update, context: CallbackContext) -> None:
    notify(update, context, True)

def notify_off(update: Update, context: CallbackContext) -> None:
    notify(update, context, False)


def spectator(update: Update, context: CallbackContext, state: bool) -> None:
    registered_users = status.get_users_data()
    users = registered_users['users']
    user = users[str(update.message.from_user.id)]

    user['spectator_permission'] = state

    status.save_users_data(registered_users)

    update.message.reply_chat_action(ChatAction.TYPING)
    update.message.reply_text("Your settings have been save correctly.")

def spectator_on(update: Update, context: CallbackContext) -> None:
    spectator(update, context, True)

def spectator_off(update: Update, context: CallbackContext) -> None:
    spectator(update, context, False)


def time_zone(update: Update, context: CallbackContext) -> None:
    try:
        time = int(context.args[0])
    except:
        update.message.reply_chat_action(ChatAction.TYPING)
        update.message.reply_text('Should be a number between -12 and 12.')
    else:
        if -12 < time < 12:
            registered_users = status.get_users_data()
            users = registered_users['users']
            user = users[str(update.message.from_user.id)]

            user['time_zone'] = time

            status.save_users_data(registered_users)
            
            update.message.reply_chat_action(ChatAction.TYPING)
            update.message.reply_text("Your settings have been save correctly.")
        else:
            update.message.reply_chat_action(ChatAction.TYPING)
            update.message.reply_text('Should be a number between -12 and 12.')