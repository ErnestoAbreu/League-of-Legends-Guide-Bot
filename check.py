def check(key: str, password: str) -> bool:
    if key == password: return True
    else: return False


""" Summoner Buttons """
def summoner_champion_mastery(callback_data: str) -> bool:
    args = callback_data.split(' ')
    return check(args[0], 'champion_mastery')
    
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
