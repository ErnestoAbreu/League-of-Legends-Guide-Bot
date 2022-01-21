from telegram import Update, ChatAction, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import CallbackContext
from riotwatcher import LolWatcher, TftWatcher, ApiError
from datetime import datetime, timedelta
import requests, json

from status import Status
import image_wrap, error


# Global variables
status = Status()

with open('json/items_name_to_id.json', 'r') as file: items_name_to_id = json.loads( file.read() )
with open('json/items_by_type.json', 'r') as file: items_by_type = json.loads( file.read() )
with open("json/champions_id_dictionary.json") as file: champions_id = json.loads( file.read() )
with open("json/champions_name_dictionary.json") as file: champions_name = json.loads( file.read() )
with open("json/champions_key_dictionary.json") as file: champions_key = json.loads( file.read() )
with open('json/to_region_code.json', 'r') as file: to_region_code = json.loads( file.read() )
with open('json/region_of.json', 'r') as file: region_of = json.loads( file.read() )
with open('json/continent_of.json', 'r') as file: continent_of = json.loads( file.read() )

api_key = status.get_riot_api()
lol_watcher = LolWatcher(api_key)
tft_watcher = TftWatcher(api_key)

last_version = status.get_last_version()


# Functions
def start(update: Update, context: CallbackContext) -> None:
    status.write('command.start was requested.')
    with open('text/start.txt') as file: text = file.read()

    update.message.reply_chat_action(ChatAction.TYPING)
    update.message.reply_text(f"Hello {update.message.from_user.first_name}. " + text)

def _help(update: Update, context: CallbackContext) -> None:
    with open('text/help.txt') as file: text = file.read()

    update.message.reply_chat_action(ChatAction.TYPING)
    update.message.reply_text(text)

def my_info(update: Update, context: CallbackContext) -> None:
    registered_users = status.get_users_data()
    users = registered_users['users']
    user = users[str(update.message.from_user.id)]

    if 'summoner' not in user:
        update.message.reply_chat_action(ChatAction.TYPING)
        update.message.reply_text("You haven't configured your summoner account yet. /config")
    else:
        context.args = [user['region'], user['summoner']]
        summoner(update, context)

def matches(update: Update, context: CallbackContext) -> None:
    registered_users = status.get_users_data()
    users = registered_users['users']
    user = users[str(update.message.from_user.id)]
    
    if 'summoner' not in user:
        update.message.reply_chat_action(ChatAction.TYPING)
        update.message.reply_text("You haven't configured your summoner account yet. /config")
    else:
        region = to_region_code[ user['region'] ]
        summoner_name = user['summoner']
        puuid = user['puuid']

        update.message.reply_chat_action(ChatAction.TYPING)
        
        num = 10
        if len(context.args) == 1:
            if context.args[0].isnumeric():
                if 1 <= int(context.args[0]) <= 20:
                    num = int(context.args[0])

        matchIds = lol_watcher.match.matchlist_by_puuid(continent_of[region], puuid, count=num)

        text = f'<b>{summoner_name}</b> last {num} matchs:\nResult | Champion | Level | K/D/A | CS | Gold\nDate | Duration | Type\n\n'

        for match_id in matchIds:
            match = lol_watcher.match.by_id(continent_of[region], match_id)['info']   

            duration = datetime(1, 1, 1) + timedelta(seconds=match['gameDuration'])
            for player in match['participants']:
                if player['summonerName'] == summoner_name:
                    if duration.hour * 60 + duration.minute < 5:
                        text += '🔄 | '
                    elif player['win']:
                        text += '✅ | '
                    else:
                        text += '❌ | '
                    text += f"<b><i>{player['championName']}</i></b> | "
                    text += f"<code>lvl {player['champLevel']}</code> | "
                    text += f"<b>{player['kills']}</b> / <b>{player['deaths']}</b> / <b>{player['assists']}</b> | "
                    text += f"👾 {player['neutralMinionsKilled'] + player['totalMinionsKilled']} | "
                    text += f"💰 {player['goldEarned']}"
            text += '\n'
            text += '<code>' + datetime.utcfromtimestamp( match['gameStartTimestamp'] / 1000 + user['time_zone'] * 60 * 60 ).strftime('%Y-%m-%d %H:%M') + '</code> | '
            text += '⏱' + ("%d:%d" % (duration.hour * 60 + duration.minute, duration.second) ) + ' | '
            text += match['gameMode']       
            text += '\n\n'
            
        update.message.reply_text(text, parse_mode=ParseMode.HTML)

def summoner(update: Update, context: CallbackContext, is_back: bool=False) -> None:
    registered_users = status.get_users_data()
    users = registered_users['users']
    
    if not is_back and len(context.args) != 0:  
        user = users[str(update.message.from_user.id)]
        
        if 'region' in user and context.args[0] not in to_region_code:
            lista = [user['region']]
            lista.extend(context.args)
            context.args = lista
            return summoner(update, context)

    if len(context.args) >= 2:
        region = context.args[0]
        summoner_name = ''
        for i in range(1,len(context.args)):
            summoner_name += context.args[i] + ' '
        summoner_name = summoner_name[:len(summoner_name)-1]

        if region in to_region_code:
            region_name = region_of[region]
            try:
                summoner_info = lol_watcher.summoner.by_name(to_region_code[region], summoner_name)
            except ApiError as err:
                if err.response.status_code == 404:
                    update.message.reply_chat_action(ChatAction.TYPING)
                    update.message.reply_text(f'Probably {summoner_name} does not exists in {region_name} server.')
                else:
                    update.message.reply_chat_action(ChatAction.TYPING)
                    update.message.reply_text('Error.')
            else:
                encrypted_summoner_id = summoner_info['id']
                
                text = '<b>' + summoner_info["name"] + '</b>\n'
                text += "Region: " + region_name + '\n'
                text += "Level: " + str(summoner_info["summonerLevel"]) + '\n'
                text += "Mastery Level: " + str(lol_watcher.champion_mastery.scores_by_summoner(to_region_code[region], encrypted_summoner_id)) + '\n\n'
                
                soloq_text = ''
                flex_text = ''
                for queue in lol_watcher.league.by_summoner(to_region_code[region], encrypted_summoner_id):
                    if queue["queueType"] == "RANKED_SOLO_5x5":
                        soloq_text += "SoloQ:\n<b>"
                        soloq_text += queue["tier"] + ' ' + queue["rank"] + '</b> - ' + str(queue["leaguePoints"]) + " LP\n"
                        soloq_text += "Matches: " + str(queue["wins"] + queue["losses"]) + '\n'
                        temp = str(queue["wins"] * 100 / (queue["wins"] + queue["losses"]) )
                        soloq_text += "WinRate: " + temp[0:min(4 , len(temp) )] + ' %\n\n'
                    if queue["queueType"] == "RANKED_FLEX_SR":
                        flex_text += "Flex:\n<b>"
                        flex_text += queue["tier"] + ' ' + queue["rank"] + '</b> - ' + str(queue["leaguePoints"]) + " LP\n"
                        flex_text += "Matches: " + str(queue["wins"] + queue["losses"]) + '\n'
                        temp = str(queue["wins"] * 100 / (queue["wins"] + queue["losses"]) )
                        flex_text += "WinRate: " + temp[0:min(4 , len(temp) )] + ' %\n\n'

                tft_text = ''
                for queue in tft_watcher.league.by_summoner(to_region_code[region], encrypted_summoner_id):
                    if queue["queueType"] == "RANKED_TFT":
                        tft_text += "TFT:\n<b>"
                        tft_text += queue["tier"] + ' ' + queue["rank"] + '</b> - ' + str(queue["leaguePoints"]) + " LP\n"
                        tft_text += "Matches: " + str(queue["wins"] + queue["losses"]) + '\n'
                        temp = str(queue["wins"] * 100 / (queue["wins"] + queue["losses"]) )
                        tft_text += "WinRate: " + temp[0:min(4 , len(temp) )] + ' %\n'
                
                text += soloq_text + flex_text + tft_text
                
                buttons = [[ InlineKeyboardButton('Champions Mastery', callback_data=f'champion_mastery {region} {summoner_name}')]]
                keyboardMarkup = InlineKeyboardMarkup(buttons)

                url = f'http://ddragon.leagueoflegends.com/cdn/{last_version}/img/profileicon/' + str(summoner_info['profileIconId']) + '.png'

                if is_back:
                    update.callback_query.edit_message_caption(text, reply_markup=keyboardMarkup, parse_mode=ParseMode.HTML)
                else:    
                    update.message.reply_chat_action(ChatAction.TYPING)
                    update.message.reply_photo(url, caption=text, reply_markup=keyboardMarkup, parse_mode=ParseMode.HTML)
        else:
            with open('text/region.txt', 'r') as file: text = file.read()
            update.message.reply_chat_action(ChatAction.TYPING)
            update.message.reply_text(text)
    else:
        with open('text/summoner_help.txt', 'r') as file: text = file.read()
        update.message.reply_chat_action(ChatAction.TYPING)
        update.message.reply_text(text)

def champion_mastery(update: Update, context: CallbackContext) -> None:
    args = update.callback_query.data.split(' ')
    password = args[0]
    region = args[1]
    summoner_name = ''
    for i in range(2,len(args)):
        summoner_name += args[i] + ' '
    summoner_name = summoner_name[:len(summoner_name)-1]

    summoner = lol_watcher.summoner.by_name(to_region_code[region], summoner_name)
    
    champion_mastery_list = lol_watcher.champion_mastery.by_summoner(to_region_code[region], summoner['id'])

    answer_list = []
    for champion in champion_mastery_list:
        answer_list.append([champion['championLevel'], champion['championPoints'], champion['championId']])
    answer_list.sort(reverse=True)

    text = f"<b>{summoner_name}</b>'s highest mastery level champions:\n"
    for i in range( min(10 , len(answer_list)) ):
        text += f"Level: {answer_list[i][0]} - <b>{champions_name[str(answer_list[i][2])]}</b><code> </code>{answer_list[i][1]}\n"
    
    buttons = [[InlineKeyboardButton("Back", callback_data=f'back_to_summoner {region} {summoner_name}')]]
    keyboardMarkup = InlineKeyboardMarkup(buttons)

    update.callback_query.answer()
    update.callback_query.edit_message_caption(text, reply_markup=keyboardMarkup, parse_mode=ParseMode.HTML)

def back_to_summoner(update: Update, context: CallbackContext) -> None:
    args = update.callback_query.data.split(' ')
    password = args[0]
    region = args[1]
    summoner_name = ''
    for i in range(2,len(args)):
        summoner_name += args[i] + ' '
    summoner_name = summoner_name[:len(summoner_name)-1]

    update.message = update.callback_query.message
    context.args = [region, summoner_name]
    return summoner(update, context, True)

def free_champion(update: Update , context: CallbackContext) -> None:
    registered_users = status.get_users_data()
    users = registered_users['users']
    user = users[str(update.message.from_user.id)]

    if 'region' in user and len(context.args) == 0:
        context.args = [user['region']]
        return free_champion(update, context)

    update.message.reply_chat_action(ChatAction.TYPING)

    text = "The current free champions are: "

    if len(context.args) == 1:
        if context.args[0] in to_region_code:
            region = context.args[0]
            
            status.write('rotations request to Riot API.')
            rotation = lol_watcher.champion.rotations(to_region_code[region])
            status.write('rotations request to Riot API successfully.')

            free_champions = rotation['freeChampionIds']
            for key in free_champions:
                text += champions_name[str(key)] + ", "
                image_wrap.setup(f'../images/champion/{champions_id[str(key)]}.png')
            image_wrap.wrap()
    
            text = text[:len(text)-2] + '.'

            update.message.reply_photo(open('temp/wrapped.jpg', 'rb'), caption=text)

            new_player_level = rotation['maxNewPlayerLevel']
            text = f"The current free champions for players up to level {new_player_level} are: "
            
            free_champions = rotation['freeChampionIdsForNewPlayers']
            for key in free_champions:
                text += champions_name[str(key)] + ", "
                image_wrap.setup(f'../images/champion/{champions_id[str(key)]}.png')
            image_wrap.wrap()
            
            text = text[:len(text)-2] + '.'

            update.message.reply_photo(open('temp/wrapped.jpg', 'rb'), caption=text)
        else:
            with open('text/region.txt', 'r') as file: text = file.read()
            update.message.reply_text(text)
    else:
        with open('text/free_champions_help.txt', 'r') as file: text = file.read()
        update.message.reply_text(text)

def _item(update: Update, context: CallbackContext) -> None:
    items = json.loads( requests.get(f'http://ddragon.leagueoflegends.com/cdn/{last_version}/data/en_US/item.json').text )
    data = items['data']

    item_name = ''
    for s in context.args:
        item_name += s + ' '
    item_name = item_name[:len(item_name)-1]

    if item_name in items_name_to_id:
        context.args = [ items_name_to_id[item_name] ]
        return _item(update, context)

    if len(context.args) == 1:
        if context.args[0] == 'all':
            context.args = [ 'Basic' ]
            _item(update, context)
            context.args = [ 'Normal' ]
            _item(update, context)
            context.args = [ 'Legendary' ]
            _item(update, context)
            context.args = [ 'Mythic' ]
            _item(update, context)

        elif context.args[0] == 'basic':
            text = 'Basic:\n'
            for item in items_by_type['Basic']:
                text += data[item]['name'] + ' <code>' + item + '</code>\n'

            update.message.reply_chat_action(ChatAction.TYPING)
            update.message.reply_text(text, parse_mode=ParseMode.HTML)
        
        elif context.args[0] == 'normal':
            text = 'Normal:\n'
            for item in items_by_type['Normal']:
                text += data[item]['name'] + ' <code>' + item + '</code>\n'
            
            update.message.reply_chat_action(ChatAction.TYPING)
            update.message.reply_text(text, parse_mode=ParseMode.HTML)

        elif context.args[0] == 'legendary':    
            text = 'Legendary:\n'
            for item in items_by_type['Legendary']:
                text += data[item]['name'] + ' <code>' + item + '</code>\n'
         
            update.message.reply_chat_action(ChatAction.TYPING)
            update.message.reply_text(text, parse_mode=ParseMode.HTML)
        
        elif context.args[0] == 'mythic':
            text = 'Mythic:\n'
            for item in items_by_type['Mythic']:
                text += data[item]['name'] + ' <code>' + item + '</code>\n'

            update.message.reply_chat_action(ChatAction.TYPING)
            update.message.reply_text(text, parse_mode=ParseMode.HTML)

        elif context.args[0] in data:
            item = data[ context.args[0] ]
            name = item['name']
            total = item['gold']['total']
            base = item['gold']['base']
            sell = item['gold']['sell']

            text = f'<b><i><u>{name}</u></i></b>  <code>{context.args[0]}</code>\n'
            if 'depth' in item:
                text += f'Cost: {total} <code>({base})</code>  -  Sell: {sell}\n'
            else:
                text += f'Cost: {total}  -  Sell: {sell}\n'
            
            text += '\n'
            text += transform_description(item['description'])

            if 'from' in item:
                text += 'From: \n'
                for id in item['from']:
                    it = data[id]
                    it_name = it['name']
                    it_cost = it['gold']['total']
                    text += f'<code>{id}</code> <b><i>{it_name}</i></b> Cost: {it_cost}\n'
                text += '\n'

            if 'into' in item:
                text += 'Into: \n'
                for id in item['into']:
                    it = data[id]
                    it_name = it['name']
                    it_cost = it['gold']['total']
                    text += f'<code>{id}</code> <b><i>{it_name}</i></b> Cost: {it_cost}\n'
                text += '\n'

            if 'tags' in item:
                text += 'Tags: '
                for tag in item['tags']:
                    text += tag + ', '
            text = text[:len(text)-2] + '\n\n'

            update.message.reply_chat_action(ChatAction.TYPING)
            update.message.reply_text(f'<a href="http://ddragon.leagueoflegends.com/cdn/{last_version}/img/item/{context.args[0]}.png"> </a>' + text, parse_mode=ParseMode.HTML)
        else:
            update.message.reply_chat_action(ChatAction.TYPING)
            if context.args[0].isnumeric():
                update.message.reply_text('Item no found with that id.')
            else:
                update.message.reply_text('Item no found with that name.')
    else:
        with open('text/item.txt', 'r') as file: text = file.read()
        update.message.reply_chat_action(ChatAction.TYPING)
        update.message.reply_text(text)


def champion(update: Update, context: CallbackContext, is_back: bool=False) -> None:
    champion_name = ''
    for s in context.args:
        champion_name += s + ' '
    champion_name = champion_name[:len(champion_name)-1]

    if champion_name in champions_key:
        context.args = [ champions_key[champion_name] ]
        return champion(update, context)
    
    if len(context.args) == 1:
        if context.args[0] in champions_id:
            _id = champions_id[context.args[0]]
            champions = json.loads( requests.get(f'http://ddragon.leagueoflegends.com/cdn/{last_version}/data/en_US/champion/{_id}.json').text )
            data = champions['data']
            _champion = data[_id]
            name = _champion['name']
            title = _champion['title']
            lore = _champion['lore']
            tags = _champion['tags']
            info = _champion['info']

            text = f'<b><i>{name}</i></b>  <i>{title}</i>\n\n' + lore + '\n\n'
            text += '<i>⚔️Attack: </i><b>' + str(info['attack']) + '</b>\n<i>🛡Defense: </i><b>' + str(info['defense']) + '</b>\n<i>💫Magic: </i><b>' + str(info['magic']) + '</b>\n\n<i>Difficulty: </i><b>' + str(info['difficulty']) + '</b>\n\n'
            text += 'Roles: '
            for tag in tags:
                text += tag + ' '
            text = text[:len(text)-1] + '\n'

            pass_data = context.args[0]
            buttons = [ 
                [ InlineKeyboardButton('Stats', callback_data=f'stats {pass_data}'), InlineKeyboardButton('Spells', callback_data=f'spells {pass_data} passive') ],
                [ InlineKeyboardButton('Skins', callback_data=f'skins {pass_data} 0'), InlineKeyboardButton('Tips', callback_data=f'tips {pass_data}') ]
            ]
            keyboardMarkup = InlineKeyboardMarkup(buttons)
            
            if is_back:
                update.callback_query.edit_message_caption(text, parse_mode=ParseMode.HTML, reply_markup=keyboardMarkup)
            else:
                update.message.reply_chat_action(ChatAction.TYPING)
                update.message.reply_photo(f'http://ddragon.leagueoflegends.com/cdn/img/champion/splash/{_id}_0.jpg', caption=text, parse_mode=ParseMode.HTML, reply_markup=keyboardMarkup)
        else:
            update.message.reply_chat_action(ChatAction.TYPING)
            update.message.reply_text("Champion with that name no found.")
    else:
        update.message.reply_chat_action(ChatAction.TYPING)
        update.message.reply_text("How to use champion command:\n/champion 'champion_name'")

def back_to_champion(update: Update, context: CallbackContext) -> None:
    password,key = update.callback_query.data.split(' ')
    update.message = update.callback_query.message
    context.args = [ key ]
    return champion(update, context, True)

def champion_stats(update: Update, context: CallbackContext) -> None:
    password,key = update.callback_query.data.split(' ')
    
    _id = champions_id[key]
    champions = json.loads( requests.get(f'http://ddragon.leagueoflegends.com/cdn/{last_version}/data/en_US/champion/{_id}.json').text )
    data = champions['data']

    _champion = data[_id]
    name = _champion['name']
    title = _champion['title']
    stats = _champion['stats']

    text = f'<b><i>{name}</i></b>  <i>{title}</i>\n\n'
    text += '<b>Energy:</b> ' + _champion['partype'] + '\n\n'
    text += '<b>Stats:</b>\n'
    
    text += '💚<i>Health Points:</i> <b>' + str(stats['hp']) + '   +' + str(stats['hpperlevel']) + '</b><i>  per level.</i>' + '\n'
    text += '💕<i>HP Regeneration:</i> <b>' + str(stats['hpregen']) + '   +' + str(stats['hpregenperlevel']) + '</b><i>  per level.</i>' + '\n\n'
    
    if _champion['partype'] == 'Mana':
        text += 'Ⓜ️<i>Mana Points:</i> <b>' + str(stats['mp']) + '</b><i>  per level:</i>  <b>' + str(stats['mpperlevel']) + '</b>\n'
        text += '🔹<i>MP Regeneration:</i> <b>' + str(stats['mpregen']) + '   +' + str(stats['mpregenperlevel']) + '</b><i>  per level.</i>' + '\n\n'
    
    text += '⚔️<i>Attack Damage:</i> <b>' + str(stats['attackdamage']) + '   +' + str(stats['attackdamageperlevel']) + '</b><i>  per level.</i>' + '\n'
    if stats['crit'] != 0 or stats['critperlevel'] != 0:
        text += '🗡<i>Critic:</i> <b>' + str(stats['crit']) + '   +' + str(stats['critperlevel']) + '</b><i>  per level.</i>' + '\n'
    text += '🔫<i>Attack Speed:</i> <b>' + str(stats['attackspeed']) + '   +' + str(stats['attackspeedperlevel'])  + '</b><i>  per level.</i>'+ '\n'
    text += '🎯<i>Attack Range:</i> <b>' + str(stats['attackrange']) + '</b>\n\n'

    text += '🥾<i>Move Speed:</i> <b>' + str(stats['movespeed']) + '</b>\n\n'
    
    text += '🛡<i>Armor:</i> <b>' + str(stats['armor']) + '   +' + str(stats['armorperlevel']) + '</b><i>  per level.</i>' + '\n'
    text += '🧿<i>Spell Block:</i> <b>' + str(stats['spellblock']) + '   +' + str(stats['spellblockperlevel']) + '</b><i>  per level.</i>' + '\n'

    pass_data = key
    buttons = [ [ InlineKeyboardButton('Back', callback_data=f'back_to_champion {pass_data}') ] ]
    keyboardMarkup = InlineKeyboardMarkup(buttons)

    update.callback_query.answer()
    update.callback_query.edit_message_caption(text, parse_mode=ParseMode.HTML, reply_markup=keyboardMarkup)

def champion_tips(update: Update, context: CallbackContext) -> None:
    password,key = update.callback_query.data.split(' ')
    
    _id = champions_id[key]
    champions = json.loads( requests.get(f'http://ddragon.leagueoflegends.com/cdn/{last_version}/data/en_US/champion/{_id}.json').text )
    data = champions['data']

    _champion = data[ champions_id[key] ]
    name = _champion['name']
    title = _champion['title']
    ally_tips = _champion['allytips']
    enemy_tips = _champion['enemytips']

    text = f'<b><i>{name}</i></b>  <i>{title}</i>\n\n'
    
    text += '<b>Ally tips:</b>\n'
    for tip in ally_tips:
        text += tip + '\n'
    
    text += '<b>Enemy tips:</b>\n'
    for tip in enemy_tips:
        text += tip + '\n'

    pass_data = key
    buttons = [ [ InlineKeyboardButton('Back', callback_data=f'back_to_champion {pass_data}') ] ]
    keyboardMarkup = InlineKeyboardMarkup(buttons)

    update.callback_query.answer()
    update.callback_query.edit_message_caption(text, parse_mode=ParseMode.HTML, reply_markup=keyboardMarkup)

def champion_spells(update: Update, context: CallbackContext) -> None:
    password,key,spell = update.callback_query.data.split(' ')

    _id = champions_id[key]
    champions = json.loads( requests.get(f'http://ddragon.leagueoflegends.com/cdn/{last_version}/data/en_US/champion/{_id}.json').text )
    data = champions['data']

    _champion = data[ champions_id[key] ]
    name = _champion['name']
    title = _champion['title']
    passive = _champion['passive']
    spellQ = _champion['spells'][0]
    spellW = _champion['spells'][1]
    spellE = _champion['spells'][2]
    spellR = _champion['spells'][3]

    text = f'<b><i>{name}</i></b>  <i>{title}</i>\n\n'
    
    if spell == 'passive':
        text += '<i>Passive</i>\n\n<b>' + passive['name'] + ':</b>\n'
        text += transform_description(passive['description']) + '\n'
        # text += '<a href=""> </a>'

    if spell == 'spellQ':
        text += '<i>Spell Q</i>\n\n<b>' + spellQ['name'] + ':</b>\n'
        text += transform_description(spellQ['description']) + '\n'

    if spell == 'spellW':
        text += '<i>Spell W</i>\n\n<b>' + spellW['name'] + ':</b>\n'
        text += transform_description(spellW['description']) + '\n'

    if spell == 'spellE':
        text += '<i>Spell E</i>\n\n<b>' + spellE['name'] + ':</b>\n'
        text += transform_description(spellE['description']) + '\n'

    if spell == 'spellR':
        text += '<i>Spell R</i>\n\n<b>' + spellR['name'] + ':</b>\n'
        text += transform_description(spellR['description']) + '\n'

    pass_data = key
    buttons = [ 
        [   
            InlineKeyboardButton('P', callback_data=f'spells {pass_data} passive'), 
            InlineKeyboardButton('Q', callback_data=f'spells {pass_data} spellQ'), 
            InlineKeyboardButton('W', callback_data=f'spells {pass_data} spellW'),
            InlineKeyboardButton('E', callback_data=f'spells {pass_data} spellE'),
            InlineKeyboardButton('R', callback_data=f'spells {pass_data} spellR')
        ],
        [ InlineKeyboardButton('Back', callback_data=f'back_to_champion {pass_data}') ] 
    ]
    keyboardMarkup = InlineKeyboardMarkup(buttons)

    update.callback_query.answer()
    update.callback_query.edit_message_caption(text, parse_mode=ParseMode.HTML, reply_markup=keyboardMarkup)

def champion_skins(update: Update, context: CallbackContext) -> None:
    password,key,skin = update.callback_query.data.split(' ')

    _id = champions_id[key]
    champions = json.loads( requests.get(f'http://ddragon.leagueoflegends.com/cdn/{last_version}/data/en_US/champion/{_id}.json').text )
    data = champions['data']

    _champion = data[ champions_id[key] ]
    _id = _champion['id']
    name = _champion['skins'][int(skin)]['name']
    if name == 'default':
        name = _champion['name']
    num = _champion['skins'][int(skin)]['num']
    
    text = f'<b><i>{name}</i></b>\n\n'
    
    pass_data = key
    buttons = [[]]
    
    i = 0
    k = 0
    for skin in _champion['skins']:
        if i < 10: text += '  ' + str(i) + ' : '
        else: text += str(i) + ' : ' 
        
        if skin['chromas']: text += '🎨 '
        else: text += '        '

        if skin['name'] == 'default': text += _champion['name'] + '\n'
        else: text += skin['name'] + '\n'
        if len(buttons[k]) == 5:
            k += 1
            buttons.append([])
        buttons[k].append(InlineKeyboardButton('Skin ' + str(i), callback_data=f'skins {pass_data} {i}'))
        i += 1

    buttons.append([ InlineKeyboardButton('Back', callback_data=f'back_to_champion {pass_data}') ])
    keyboardMarkup = InlineKeyboardMarkup(buttons)

    update.callback_query.answer()
    update.callback_query.delete_message()
    update.callback_query.message.chat.send_photo(f'http://ddragon.leagueoflegends.com/cdn/img/champion/splash/{_id}_{num}.jpg', caption=text, parse_mode=ParseMode.HTML, reply_markup=keyboardMarkup)

def transform_description(description: str) -> str:
    check_tag = False
    tag = ''
    text = ''
    for c in description:
        if c == '<':
            check_tag = True
            continue

        if c == '>':
            check_tag = False
            if tag == 'li': text += '\n'
            if tag == 'stats': text += '<i>'
            if tag == '/stats': text += '</i>'
            if tag == 'attention': text += '<b>'
            if tag == '/attention': text += '</b>'
            if tag == 'br': text += '\n'
            if tag == 'status': text += '<code>'
            if tag == '/status': text += '</code>'
            if tag == 'passive': text += '<b><i>'
            if tag == '/passive': text += '</i></b>'
            if tag == 'active': text += '<b><i>'
            if tag == '/active': text += '</i></b>'
            if tag == 'rarityMythic': text += '<b><i><u>'
            if tag == '/rarityMythic': text += '</u></i></b>'
            tag = ''
            continue
        
        if check_tag:
            tag += c
        else:
            text += c
    
    return text + '\n'    