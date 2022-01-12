def summoner_champion_mastery(data: str) -> bool:
    args = data.split(' ')
    password = args[0]
    if password == 'champion_mastery':
        return True
    else:
        return False

def back_to_summoner(data: str) -> bool:
    args = data.split(' ')
    password = args[0]
    if password == 'back_to_summoner':
        return True
    else:
        return False

def back_to_champion(data: str) -> bool:
    args = data.split(' ')
    password = args[0]
    if password == 'back_to_champion':
        return True
    else:
        return False

def champion_stats(data: str) -> bool:
    args = data.split(' ')
    password = args[0]
    if password == 'stats': 
        return True
    else:
        return False

def champion_tips(data: str) -> bool:
    args = data.split(' ')
    password = args[0]
    if password == 'tips': 
        return True
    else:
        return False

def champion_spells(data: str) -> bool:
    args = data.split(' ')
    password = args[0]
    if password == 'spells': 
        return True
    else:
        return False

def champion_skins(data: str) -> bool:
    args = data.split(' ')
    password = args[0]
    if password == 'skins': 
        return True
    else:
        return False