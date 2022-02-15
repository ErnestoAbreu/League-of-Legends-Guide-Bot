from telegram import ChatAction, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler, Filters, MessageHandler, Updater
from datetime import datetime, timedelta
from code import Response, Summoner, Champions
from status import Status
import threading
import requests
import time
import check

status = Status()

TOKEN = status.data.token
last_version = status.data.last_version
registered_users = status.data.registered_users
users = registered_users["users"]

to_region_code = status.json.to_region_code
region_of = status.json.region_of

def start(update: Update, context: CallbackContext) -> None:
    text = status.text.start
    update.message.reply_chat_action(ChatAction.TYPING)
    update.message.reply_text(f"Hello {update.message.from_user.first_name}. " + text)

def help(update: Update, context: CallbackContext) -> None:
    text = status.text.help
    update.message.reply_chat_action(ChatAction.TYPING)
    update.message.reply_text(text)

def my_info(update: Update, context: CallbackContext) -> None:
    user = users[str(update.message.from_user.id)]

    if "summoner" not in user:
        update.message.reply_chat_action(ChatAction.TYPING)
        update.message.reply_text("You have not configured your summoner account yet. /config")
    else:
        context.args = [user["region"], user["summoner"]]
        summoner(update, context)

def summoner(update: Update, context: CallbackContext) -> None:
    if len(context.args) == 0:
        text = status.text.summoner_help
        update.message.reply_chat_action(ChatAction.TYPING)
        update.message.reply_text(text)
    else:
        user = users[str(update.message.from_user.id)]

        if "region" in user and context.args[0] not in to_region_code:
            lista = [user["region"]]
            lista.extend(context.args)
            context.args = lista
            return summoner(update, context)

        if len(context.args) == 1:
            update.message.reply_chat_action(ChatAction.TYPING)
            update.message.reply_text("You have not configured your region yet. /config")
        else:
            region = context.args[0]
            summoner_name = " ".join(context.args[1:])

            if region in to_region_code:
                region_code = to_region_code[region]
                summonerObj = Summoner(region_code, summoner_name, last_version, user["time_zone"])

                summonerObj.main()
                response = summonerObj.summoner()
                summoner_name = summonerObj.summoner_name

                if response.photo == None:
                    update.message.reply_chat_action(ChatAction.TYPING)
                    update.message.reply_text(response.text, parse_mode=ParseMode.HTML)
                else:
                    userID = update.message.from_user.id

                    buttons = [
                        [
                            InlineKeyboardButton("Champions Stats", callback_data=f"champion_last_time_played {userID} {region} {summoner_name}")
                        ],
                        [
                            InlineKeyboardButton("Last Matches", callback_data=f"summoner_last_matches {userID} {region} {summoner_name}")
                        ]
                    ]
                    keyboardMarkup = InlineKeyboardMarkup(buttons)

                    update.message.reply_chat_action(ChatAction.TYPING)
                    update.message.reply_photo(response.photo, response.text, reply_markup=keyboardMarkup, parse_mode=ParseMode.HTML)
            else:
                text = status.text.region
                update.message.reply_chat_action(ChatAction.TYPING)
                update.message.reply_text(text)

def summoner_last_matches(update: Update, context: CallbackContext) -> None:
    args = update.callback_query.data.split(" ")
    password = args[0]
    owner = int(args[1])
    region = args[2]
    summoner_name = " ".join(args[3 : len(args)])

    if update.callback_query.from_user.id == owner:
        user = users[str(owner)]
        region_code = to_region_code[region]
        summonerObj = Summoner(region_code, summoner_name, last_version, user["time_zone"])

        # response = Response()
        if password == "summoner_last_matches":
            response = summonerObj.last_matches(0, 5)
        if password == "summoner_match_soloq":
            response = summonerObj.last_matches(420, 5)
        if password == "summoner_match_flexq":
            response = summonerObj.last_matches(440, 5)

        buttons = [
            [
                InlineKeyboardButton(
                    "SoloQ",
                    callback_data=f"summoner_match_soloq {owner} {region} {summoner_name}",
                ),
                InlineKeyboardButton(
                    "FlexQ",
                    callback_data=f"summoner_match_flexq {owner} {region} {summoner_name}",
                ),
            ],
            [
                InlineKeyboardButton(
                    "Back",
                    callback_data=f"back_to_summoner {owner} {region} {summoner_name}",
                )
            ],
        ]
        keyboardMarkup = InlineKeyboardMarkup(buttons)

        update.callback_query.answer()
        update.callback_query.edit_message_caption(
            response.text, reply_markup=keyboardMarkup, parse_mode=ParseMode.HTML
        )
    else:
        update.callback_query.answer("This message does not belong to you.")


def champion_stats(update: Update, context: CallbackContext) -> None:
    args = update.callback_query.data.split(" ")
    password = args[0]
    owner = int(args[1])
    region = args[2]
    summoner_name = " ".join(args[3 : len(args)])

    if update.callback_query.from_user.id == owner:
        user = users[str(owner)]
        region_code = to_region_code[region]
        summonerObj = Summoner(
            region_code, summoner_name, last_version, user["time_zone"]
        )

        if password == "champion_last_time_played":
            response = summonerObj.champion_last_time_played()
        if password == "champion_mastery":
            response = summonerObj.champion_mastery()
        if password == "champion_winrate":
            response = summonerObj.champion_winrate()
        if password == "champion_kda":
            response = summonerObj.champion_kda()

        buttons = [
            [
                InlineKeyboardButton(
                    "Last Time",
                    callback_data=f"champion_last_time_played {owner} {region} {summoner_name}",
                ),
                InlineKeyboardButton(
                    "Mastery",
                    callback_data=f"champion_mastery {owner} {region} {summoner_name}",
                ),
                InlineKeyboardButton(
                    "Winrate",
                    callback_data=f"champion_winrate {owner} {region} {summoner_name}",
                ),
                InlineKeyboardButton(
                    "KDA",
                    callback_data=f"champion_kda {owner} {region} {summoner_name}",
                ),
            ],
            [
                InlineKeyboardButton(
                    "Back",
                    callback_data=f"back_to_summoner {owner} {region} {summoner_name}",
                )
            ],
        ]
        keyboardMarkup = InlineKeyboardMarkup(buttons)

        update.callback_query.answer()
        update.callback_query.edit_message_caption(
            response.text, reply_markup=keyboardMarkup, parse_mode=ParseMode.HTML
        )
    else:
        update.callback_query.answer("This message does not belong to you.")


def back_to_summoner(update: Update, context: CallbackContext) -> None:
    args = update.callback_query.data.split(" ")
    password = args[0]
    owner = int(args[1])
    region = args[2]
    summoner_name = " ".join(args[3 : len(args)])

    if update.callback_query.from_user.id == owner:
        user = users[str(owner)]
        region_code = to_region_code[region]
        summonerObj = Summoner(region_code, summoner_name, last_version, user["time_zone"])

        response = summonerObj.summoner()

        buttons = [
            [
                InlineKeyboardButton(
                    "Champions Stats",
                    callback_data=f"champion_last_time_played {owner} {region} {summoner_name}",
                )
            ],
            [
                InlineKeyboardButton(
                    "Last Matches",
                    callback_data=f"last_matches {owner} {region} {summoner_name}",
                )
            ],
        ]
        keyboardMarkup = InlineKeyboardMarkup(buttons)

        update.callback_query.answer()
        update.callback_query.edit_message_caption(
            response.text, reply_markup=keyboardMarkup, parse_mode=ParseMode.HTML
        )
    else:
        update.callback_query.answer("This message does not belong to you.")

def matches(update: Update, context: CallbackContext) -> None:
    user = users[str(update.message.from_user.id)]

    if "summoner" not in user:
        update.message.reply_chat_action(ChatAction.TYPING)
        update.message.reply_text("You haven't configured your summoner account yet. /config")
    else:
        region_code = to_region_code[user["region"]]
        summoner_name = user["summoner"]
        user_time_zone = user["time_zone"]

        count = 10
        if len(context.args) == 1:
            if context.args[0].isnumeric():
                if 1 <= int(context.args[0]) <= 20:
                    count = int(context.args[0])
                else:
                    update.message.reply_chat_action(ChatAction.TYPING)
                    update.message.reply_text("The number of matches must be between 1 and 20.")
                    return

        summonerObj = Summoner(region_code, summoner_name, last_version, user_time_zone)
        summonerObj.main('matches')
        
        update.message.reply_chat_action(ChatAction.TYPING)
        response = summonerObj.last_matches(0, count)

        update.message.reply_text(response.text, parse_mode=ParseMode.HTML)

def free_champions(update: Update, context: CallbackContext, type: int=0) -> None:
    user = users[str(update.message.from_user.id)]

    if "region" in user and len(context.args) == 0:
        context.args = [user["region"]]
        return free_champions(update, context, type)

    update.message.reply_chat_action(ChatAction.TYPING)

    if len(context.args) == 1:
        if context.args[0] in to_region_code:
            region = context.args[0]

            obj = Champions()
            response = obj.free_champions(to_region_code[region], type)

            update.message.reply_photo(response.photo, response.text)
        else:
            text = status.text.region
            update.message.reply_text(text)
    else:
        text = status.text.free_champions_help
        update.message.reply_text(text)

def free_champion_for_new_players(update: Update, context: CallbackContext) -> None:
    free_champions(update, context, 1)

def config(update: Update, context: CallbackContext) -> None:
    user = users[str(update.message.from_user.id)]

    if 'region' in user: 
        region = region_of[user['region']]
    else: 
        region = 'None'
    
    if 'summoner' in user: 
        summoner = user['summoner']
    else: 
        summoner = 'None'

    if user['notify']:
        notify = '✅   /config_notify_off'
    else:
        notify = '❌   /config_notify_on'

    if user['time_zone'] == 0:
        time_zone = 'UTC'
    elif user['time_zone'] > 0:
        time_zone = 'UTC +' + str(user['time_zone'])
    else:
        time_zone = 'UTC ' + str(user['time_zone'])
    
    text = status.text.config.format(region=region, summoner=summoner, notify=notify, time_zone=time_zone)

    update.message.reply_chat_action(ChatAction.TYPING)
    update.message.reply_text(text, parse_mode=ParseMode.HTML)

def config_region(update: Update, context: CallbackContext) -> None:
    if len(context.args) != 1:
        text = status.text.config_region

        update.message.reply_chat_action(ChatAction.TYPING)
        update.message.reply_text(text)
    elif context.args[0] in to_region_code:
        region = context.args[0]

        user = users[str(update.message.from_user.id)]

        user['region'] = region
        if 'summoner' in user:
            user.pop('summoner')

        status.data.save_registered_users()
        
        update.message.reply_chat_action(ChatAction.TYPING)
        update.message.reply_text("Your settings have been save correctly.")
    else:
        status.text.region

        update.message.reply_chat_action(ChatAction.TYPING)
        update.message.reply_text(text)


def config_summoner(update: Update, context: CallbackContext) -> None:
    if len(context.args) == 0:
        text = status.text.config_summoner

        update.message.reply_chat_action(ChatAction.TYPING)
        update.message.reply_text(text)
    else: 
        summoner_name = " ".join(context.args)
        user = users[str(update.message.from_user.id)]
        
        if 'region' in user:
            region = to_region_code[user['region']]

            summonerObj = Summoner(region, summoner_name, last_version, user['time_zone'])
            response = summonerObj.main()
            if response.error:
                update.message.reply_chat_action(ChatAction.TYPING)
                update.message.reply_text(response.text)
            else:
                user['summoner'] = summonerObj.summoner_name
                
                status.data.save_registered_users()
                
                update.message.reply_chat_action(ChatAction.TYPING)
                update.message.reply_text("Your settings have been save correctly.")
        else:
            update.message.reply_chat_action(ChatAction.TYPING)
            update.message.reply_text("You should configure Region first.")


def config_notify(update: Update, context: CallbackContext, state: bool) -> None:
    user = users[str(update.message.from_user.id)]

    user['notify'] = state

    status.data.save_registered_users()

    update.message.reply_chat_action(ChatAction.TYPING)
    update.message.reply_text("Your settings have been save correctly.")

def config_notify_on(update: Update, context: CallbackContext) -> None:
    config_notify(update, context, True)

def config_notify_off(update: Update, context: CallbackContext) -> None:
    config_notify(update, context, False)

def config_time_zone(update: Update, context: CallbackContext) -> None:
    try:
        time = int(context.args[0])
    except:
        update.message.reply_chat_action(ChatAction.TYPING)
        update.message.reply_text('Should be a number between -12 and 12.')
    else:
        if -12 < time < 12:
            user = users[str(update.message.from_user.id)]

            user['time_zone'] = time

            status.data.save_registered_users()
            
            update.message.reply_chat_action(ChatAction.TYPING)
            update.message.reply_text("Your settings have been save correctly.")
        else:
            update.message.reply_chat_action(ChatAction.TYPING)
            update.message.reply_text('Should be a number between -12 and 12.')

def message(update: Update , context: CallbackContext) -> None:
    if update.message == None: return

    status.save_message(update.message.text, update.message.from_user.id)

    if str(update.message.from_user.id) not in users:
        users[str(update.message.from_user.id)] = { 
            "username": update.message.from_user.username,
            'notify': False,
            'time_zone': 0 
        }
        registered_users['counter'] += 1

    status.data.save_registered_users()

def update(updater: Updater) -> None:
    while True:
        versions = requests.get('https://ddragon.leagueoflegends.com/api/versions.json').json()
        new_version = versions[0]
        global last_version

        if last_version != new_version:
            status.data.last_version = new_version
            status.data.save_version()
            
            for chat_id,value in users.items():
                if value['notify']:
                    try:
                        updater.bot.send_chat_action(chat_id, ChatAction.TYPING)
                        updater.bot.send_message(chat_id, f'New update is coming soon. Version: {last_version}.')
                    except:
                        users[chat_id]['notify'] = False
                        status.data.save_registered_users()

        time.sleep(3600*4)

def spectator(update: Update, context: CallbackContext) -> None:
    if len(context.args) == 0:
        text = status.text.spectator_help
        update.message.reply_chat_action(ChatAction.TYPING)
        update.message.reply_text(text)
    else:
        user = users[str(update.message.from_user.id)]

        if "region" in user and context.args[0] not in to_region_code:
            lista = [user["region"]]
            lista.extend(context.args)
            context.args = lista
            return spectator(update, context)

        if len(context.args) == 1:
            update.message.reply_chat_action(ChatAction.TYPING)
            update.message.reply_text("You have not configured your region yet. /config")
        else:
            region = context.args[0]
            summoner_name = " ".join(context.args[1:])

            if region in to_region_code:
                region_code = to_region_code[region]

                summonerObj = Summoner(region_code, summoner_name, last_version, user['time_zone'])
                summonerObj.main('other')
                response = summonerObj.spectator()
                
                update.message.reply_chat_action(ChatAction.TYPING)
                update.message.reply_text(response.text, parse_mode=ParseMode.HTML)
            else:
                text = status.text.region
                update.message.reply_chat_action(ChatAction.TYPING)
                update.message.reply_text(text)

def my_spectator(update: Update, context: CallbackContext) -> None:
    user = users[str(update.message.from_user.id)]

    if "summoner" not in user:
        update.message.reply_chat_action(ChatAction.TYPING)
        update.message.reply_text("You have not configured your summoner account yet. /config")
    else:
        context.args = [user["region"], user["summoner"]]
        spectator(update, context)

def main():

    updater = Updater(TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CommandHandler("my_info", my_info))
    dispatcher.add_handler(CommandHandler("my_lastmatches", matches))
    dispatcher.add_handler(CommandHandler("my_current_match", my_spectator))
    dispatcher.add_handler(CommandHandler("summoner", summoner))
    dispatcher.add_handler(CallbackQueryHandler(champion_stats, pattern=check.summoner_champion_last_time_played))
    dispatcher.add_handler(CallbackQueryHandler(champion_stats, pattern=check.summoner_champion_mastery))
    dispatcher.add_handler(CallbackQueryHandler(champion_stats, pattern=check.summoner_champion_winrate))
    dispatcher.add_handler(CallbackQueryHandler(champion_stats, pattern=check.summoner_champion_kda))
    dispatcher.add_handler(CallbackQueryHandler(summoner_last_matches, pattern=check.summoner_last_matches))
    dispatcher.add_handler(CallbackQueryHandler(summoner_last_matches, pattern=check.summoner_match_draft_pick))
    dispatcher.add_handler(CallbackQueryHandler(summoner_last_matches, pattern=check.summoner_match_soloq))
    dispatcher.add_handler(CallbackQueryHandler(summoner_last_matches, pattern=check.summoner_match_flexq))
    dispatcher.add_handler(CallbackQueryHandler(back_to_summoner, pattern=check.back_to_summoner))
    dispatcher.add_handler(CommandHandler("current_match", spectator))
    dispatcher.add_handler(CommandHandler("freechampions", free_champions))
    dispatcher.add_handler(CommandHandler("freechampions_fornewplayers", free_champion_for_new_players))

    dispatcher.add_handler(CommandHandler("config", config))
    dispatcher.add_handler(CommandHandler("config_region", config_region))
    dispatcher.add_handler(CommandHandler("config_summoner", config_summoner))
    dispatcher.add_handler(CommandHandler("config_notify_on", config_notify_on))
    dispatcher.add_handler(CommandHandler("config_notify_off", config_notify_off))
    dispatcher.add_handler(CommandHandler("config_time_zone", config_time_zone))

    # dispatcher.add_handler(CommandHandler("item", command._item), group=0)
    # dispatcher.add_handler(CommandHandler("champion", command.champion), group=0)
    # dispatcher.add_handler(CallbackQueryHandler(command.back_to_champion, pattern=check.back_to_champion))
    # dispatcher.add_handler(CallbackQueryHandler(command.champion_stats, pattern=check.champion_stats))
    # dispatcher.add_handler(CallbackQueryHandler(command.champion_tips, pattern=check.champion_tips))
    # dispatcher.add_handler(CallbackQueryHandler(command.champion_spells, pattern=check.champion_spells))
    # dispatcher.add_handler(CallbackQueryHandler(command.champion_skins, pattern=check.champion_skins))

    dispatcher.add_handler(MessageHandler(Filters.text, message), group=1)

    """ Start """
    updater.start_polling()
    status.write("")
    status.write("START")

    thread = threading.Thread(target=update, args=(updater,))
    thread.start()

    updater.idle()
    """ End """


if __name__ == "__main__":
    main()
