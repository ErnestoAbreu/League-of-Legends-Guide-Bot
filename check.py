def check(key: str, password: str) -> bool:
    if key == password: return True
    else: return False

def summoner_champion_mastery(data: str) -> bool:
    args = data.split(' ')
    return check(args[0], 'champion_mastery')
    
def back_to_summoner(data: str) -> bool:
    args = data.split(' ')
    return check(args[0], 'back_to_summoner')

def back_to_champion(data: str) -> bool:
    args = data.split(' ')
    return check(args[0], 'back_to_champion')

def champion_stats(data: str) -> bool:
    args = data.split(' ')
    return check(args[0], 'stats')

def champion_tips(data: str) -> bool:
    args = data.split(' ')
    return check(args[0], 'tips')

def champion_spells(data: str) -> bool:
    args = data.split(' ')
    return check(args[0], 'spells')

def champion_skins(data: str) -> bool:
    args = data.split(' ')
    return check(args[0], 'skins')
