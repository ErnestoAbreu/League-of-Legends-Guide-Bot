def check(key: str, password: str) -> bool:
    if key == password: return True
    else: return False


""" Summoner Buttons """
def summoner_champion_last_time_played(callback_data: str) -> bool:
    args = callback_data.split(' ')
    return check(args[0], 'champion_last_time_played')

def summoner_champion_mastery(callback_data: str) -> bool:
    args = callback_data.split(' ')
    return check(args[0], 'champion_mastery')

def summoner_champion_winrate(callback_data: str) -> bool:
    args = callback_data.split(' ')
    return check(args[0], 'champion_winrate')

def summoner_champion_kda(callback_data: str) -> bool:
    args = callback_data.split(' ')
    return check(args[0], 'champion_kda')

def summoner_last_matches(callback_data: str) -> bool:
    args = callback_data.split(' ')
    return check(args[0], 'summoner_last_matches')

def summoner_match_draft_pick(callback_data: str) -> bool:
    args = callback_data.split(' ')
    return check(args[0], 'summoner_match_draft_pick')

def summoner_match_soloq(callback_data: str) -> bool:
    args = callback_data.split(' ')
    return check(args[0], 'summoner_match_soloq')

def summoner_match_flexq(callback_data: str) -> bool:
    args = callback_data.split(' ')
    return check(args[0], 'summoner_match_flexq')

def back_to_summoner(callback_data: str) -> bool:
    args = callback_data.split(' ')
    return check(args[0], 'back_to_summoner')


""" Champion Buttons """
def back_to_champion(callback_data: str) -> bool:
    args = callback_data.split(' ')
    return check(args[0], 'back_to_champion')

def champion_stats(callback_data: str) -> bool:
    args = callback_data.split(' ')
    return check(args[0], 'stats')

def champion_tips(callback_data: str) -> bool:
    args = callback_data.split(' ')
    return check(args[0], 'tips')

def champion_spells(callback_data: str) -> bool:
    args = callback_data.split(' ')
    return check(args[0], 'spells')

def champion_skins(callback_data: str) -> bool:
    args = callback_data.split(' ')
    return check(args[0], 'skins')
