from riotwatcher import ApiError, LolWatcher
from datetime import datetime, timedelta
from status import Status
import copy
import json
import imgkit
import requests

status = Status()

lol_watcher = LolWatcher(status.data.api_key)
data = status.data.data

region_of = status.json.region_of
match_of = status.json.match_of
continent_of = status.json.continent_of
champions_name = status.json.champions_name
champions_id = status.json.champions_id

class Response:
    def __init__(self, text: str = "", photo: str = None, error: bool = True):
        self.text = text
        self.photo = photo
        self.error = error

class Summoner:
    def __init__(self, region: str, summoner_name: str, last_version: str = "12.2.1", user_time_zone: int = 0,):
        self.region = region
        self.summoner_name = summoner_name
        self.last_version = last_version
        self.user_time_zone = user_time_zone

    def main(self, Filter: str='full'):
        region_name = region_of[self.region]
        try:
            SummonerDTO = lol_watcher.summoner.by_name(self.region, self.summoner_name)
        except ApiError as error:
            response = Response()
            if error.response.status_code == 404:
                response.text = f"Probably {self.summoner_name} does not exists in {region_name} server."
            else:
                response.text = "Unexpected Error."
                status.write(f"Unexpected ERROR | Response Code: {str(error.response.status_code)} Response Text: {error.response.text}: code.Summoner.main({self.region}, {self.summoner_name})")
            return response
        else:
            self.summoner_name = SummonerDTO["name"]
            puuid = SummonerDTO["puuid"]
            encrypted_summoner_id = SummonerDTO["id"]
            continent = continent_of[self.region]
            Matches = dict()

            if str(self.region + self.summoner_name) not in data["SummonerData"]:
                data["SummonerData"][self.region + self.summoner_name] = dict()
            
            data["SummonerData"][self.region + self.summoner_name]["SummonerDTO"] = SummonerDTO

            if Filter == 'full' or Filter == 'spectator':
                LeagueEntryDTO = lol_watcher.league.by_summoner(self.region, encrypted_summoner_id)
                data["SummonerData"][self.region + self.summoner_name]["LeagueEntryDTO"] = LeagueEntryDTO

                ChampionMasteryDTO = lol_watcher.champion_mastery.by_summoner(self.region, encrypted_summoner_id)
                data["SummonerData"][self.region + self.summoner_name]["ChampionMasteryDTO"] = ChampionMasteryDTO

                ChampionPerformance = self.get_ChampionPerformance()
                data["SummonerData"][self.region + self.summoner_name]["ChampionPerformance"] = ChampionPerformance
            
            if Filter == 'full' or Filter == 'matches':
                Matches["0"] = lol_watcher.match.matchlist_by_puuid(continent, puuid)
                if Filter != 'matches':
                    Matches["420"] = lol_watcher.match.matchlist_by_puuid(continent, puuid, queue=420)
                    Matches["440"] = lol_watcher.match.matchlist_by_puuid(continent, puuid, queue=440)
                data["SummonerData"][self.region + self.summoner_name]["Matches"] = Matches

            status.data.save_data()

    def summoner(self) -> Response:
        response = Response()

        SummonerDTO = data["SummonerData"][self.region + self.summoner_name]["SummonerDTO"]
        LeagueEntryDTO = data["SummonerData"][self.region + self.summoner_name]["LeagueEntryDTO"]
        ChampionMasteryDTO = data["SummonerData"][self.region + self.summoner_name]["ChampionMasteryDTO"]

        region_name = region_of[self.region]
        encrypted_summoner_id = SummonerDTO["id"]
        summoner_level = str(SummonerDTO["summonerLevel"])
        summoner_profileIconId = str(SummonerDTO["profileIconId"])
        summoner_mastery_level = 0
        for champion in ChampionMasteryDTO:
            summoner_mastery_level += champion["championLevel"]
        SoloQ = None
        FlexQ = None
        for queue in LeagueEntryDTO:
            if queue["queueType"] == "RANKED_SOLO_5x5":
                SoloQ = queue
            if queue["queueType"] == "RANKED_FLEX_SR":
                FlexQ = queue

        response.text = f"<b>{self.summoner_name}</b>\n"
        response.text += f"Region: {region_name}\n"
        response.text += f"Level: {summoner_level}\n"
        response.text += f"Mastery Level: {summoner_mastery_level}\n\n"

        if SoloQ:
            response.text += "SoloQ:\n"
            response.text += "{} {} - <b>{}</b> LP\n".format(SoloQ["tier"], SoloQ["rank"], str(SoloQ["leaguePoints"]))
            response.text += "Matches: {}\n".format(str(SoloQ["wins"] + SoloQ["losses"]))
            porcent = str(round(SoloQ["wins"] * 100 / (SoloQ["wins"] + SoloQ["losses"]), 1))
            response.text += f"Winrate: {porcent}%\n\n"
        if FlexQ:
            response.text += "FlexQ:\n"
            response.text += "{} {} - <b>{}</b> LP\n".format(FlexQ["tier"], FlexQ["rank"], str(FlexQ["leaguePoints"]))
            response.text += "Matches: {}\n".format(str(FlexQ["wins"] + FlexQ["losses"]))
            porcent = str(round(FlexQ["wins"] * 100 / (FlexQ["wins"] + FlexQ["losses"]), 1))
            response.text += f"Winrate: {porcent}%\n\n"

        response.photo = f"http://ddragon.leagueoflegends.com/cdn/{self.last_version}/img/profileicon/{summoner_profileIconId}.png"
        response.error = False

        return response

    def champion_last_time_played(self) -> Response:
        response = Response()
        ChampionMasteryDTO = data["SummonerData"][self.region + self.summoner_name]["ChampionMasteryDTO"]

        champions_list = []
        for champion in ChampionMasteryDTO:
            champions_list.append([champion["lastPlayTime"], champion["championId"]])
        champions_list.sort(reverse=True)

        response.text = f"<b>{self.summoner_name}</b>'s last played champions:\n"
        for champion in champions_list[: min(20, len(champions_list))]:
            time = datetime.utcfromtimestamp(
                champion[0] / 1000 + self.user_time_zone * 60 * 60
            ).strftime("%Y-%m-%d %H:%M")
            response.text += (
                f"<code>{time} </code><b>{champions_name[str(champion[1])]}</b>\n"
            )

        response.error = False
        return response

    def champion_mastery(self) -> Response:
        response = Response()
        ChampionMasteryDTO = data["SummonerData"][self.region + self.summoner_name][
            "ChampionMasteryDTO"
        ]

        champions_list = []
        for champion in ChampionMasteryDTO:
            champions_list.append(
                [
                    champion["championLevel"],
                    champion["championPoints"],
                    champion["championId"],
                ]
            )
        champions_list.sort(reverse=True)

        response.text = (
            f"<b>{self.summoner_name}</b>'s highest mastery level champions:\n"
        )
        for champion in champions_list[: min(20, len(champions_list))]:
            response.text += f"Level: {champion[0]} - <b>{champions_name[str(champion[2])]}</b><code> </code>{champion[1]}\n"

        response.error = False
        return response

    def champion_winrate(self) -> Response:
        response = Response()
        ChampionPerformance = data["SummonerData"][self.region + self.summoner_name]["ChampionPerformance"]

        if ChampionPerformance["Season12"] == None:
            response.text = "Unexpected Error"
            status.write(f"Unexpected ERROR: code.Summoner.champion_winrate({self.region}, {self.summoner_name}, {self.last_version})")
            return response

        championStats = dict()

        for queueId, basicCP in ChampionPerformance["Season12"].items():
            for champion in basicCP:
                if champion["championId"] in championStats:
                    for key, value in champion.items():
                        if key == "maxKills" or key == "maxDeaths":
                            championStats[champion["championId"]][key] = max(
                                championStats[champion["championId"]][key], value
                            )
                        elif key == "championId":
                            pass
                        else:
                            championStats[champion["championId"]][key] += value
                else:
                    championStats[champion["championId"]] = copy.deepcopy(champion)

        champions_list = []
        for championId, champion in championStats.items():
            if champion["totalMatches"] >= 3:
                champions_list.append(
                    [
                        round(champion["wins"] / champion["totalMatches"] * 100, 1),
                        champion["totalMatches"],
                        championId,
                    ]
                )
        champions_list.sort(reverse=True)

        response.text = f"<b>{self.summoner_name}</b>'s highest winrate champions in ranked:\n"
        for champion in champions_list[: min(20, len(champions_list))]:
            response.text += f"<b>{champion[0]}%</b>   <b><i>{champions_name[str(champion[2])]}</i></b>   -   {champion[1]} matches\n"

        response.error = False
        return response

    def champion_kda(self) -> Response:
        response = Response()
        ChampionPerformance = data["SummonerData"][self.region + self.summoner_name]["ChampionPerformance"]
        
        if ChampionPerformance["Season12"] == None:
            response.text = "Unexpected Error"
            status.write(f"Unexpected ERROR: code.Summoner.champion_kda({self.region}, {self.summoner_name}, {self.last_version})")
            return response

        championStats = dict()

        for queueId, basicCP in ChampionPerformance["Season12"].items():
            for champion in basicCP:
                if champion["championId"] in championStats:
                    for key, value in champion.items():
                        if key == "maxKills" or key == "maxDeaths":
                            championStats[champion["championId"]][key] = max(
                                championStats[champion["championId"]][key], value
                            )
                        elif key == "championId":
                            pass
                        else:
                            championStats[champion["championId"]][key] += value
                else:
                    championStats[champion["championId"]] = copy.deepcopy(champion)

        champions_list = []
        for championId, champion in championStats.items():
            if champion["totalMatches"] >= 3:
                if champion["deaths"] == 0:
                    champion["deaths"] = 1
                champions_list.append(
                    [
                        round(
                            (champion["kills"] + champion["assists"])
                            / champion["deaths"],
                            1,
                        ),
                        championId,
                        champion["totalMatches"],
                        champion["kills"],
                        champion["deaths"],
                        champion["assists"],
                        champion["cs"],
                        champion["gold"],
                    ]
                )
        champions_list.sort(reverse=True)

        response.text = f"<b>{self.summoner_name}</b>'s highest kda champions in ranked:\n"
        for champion in champions_list[: min(20, len(champions_list))]:
            championId = str(champion[1])
            totalMatches = champion[2]
            kills = round(champion[3] / totalMatches, 1)
            deaths = round(champion[4] / totalMatches, 1)
            assists = round(champion[5] / totalMatches, 1)
            cs = round(champion[6] / totalMatches, 1)
            gold = round(champion[7] / totalMatches, 1)
            response.text += f" <b>{champion[0]}</b> <b><i>{champions_name[championId]}</i></b> | <b>{kills} / {deaths} / {assists}</b> | 💰{gold}\n"

        response.error = False
        return response

    def last_matches(self, queueId: int, count: int) -> Response:
        response = Response()
        Matches = data["SummonerData"][self.region + self.summoner_name]["Matches"]

        response.text = f"<b>{self.summoner_name}</b> last {count} matches:\n\n"

        for matchId in Matches[str(queueId)][:count]:
            matchObj = Match(continent_of[self.region], matchId)
            response.text += (matchObj.short_info(self.summoner_name, self.user_time_zone) + "\n")

        response.error = False
        return response
    
    def spectator(self) -> Response:
        response = Response()

        SummonerDTO = data["SummonerData"][self.region + self.summoner_name]['SummonerDTO']
        encrypted_summoner_id = SummonerDTO['id']
        
        try:
            CurrentGameInfo = lol_watcher.spectator.by_summoner(self.region, encrypted_summoner_id)
        except ApiError as error:
            if error.response.status_code == 404:
                text = 'This summoner is not playing.'
            else:
                text = 'Unexpected error.'
                status.write(f"Unexpected ERROR | Response Code: {str(error.response.status_code)} Response Text: {error.response.text}: code.Summoner.spectator({self.region}, {self.summoner_name})")
        except:
            text = 'Unexpected error.'
            status.write(f"Unexpected ERROR | Normal Except T-T : code.Summoner.spectator({self.region}, {self.summoner_name})")
        else:
            matchType = match_of[str(CurrentGameInfo['gameQueueConfigId'])]
            duration = datetime(1, 1, 1) + timedelta(seconds=CurrentGameInfo["gameLength"])
            participants = CurrentGameInfo['participants']
            banned = CurrentGameInfo['bannedChampions']
            
            teamA_text = ''
            teamB_text = ''
            for player in participants:
                summoner_name = player['summonerName']
                champion_id = player['championId']
                
                summonerObj = Summoner(self.region, summoner_name, self.last_version)
                summonerObj.main('spectator')
                
                SummonerDTO = data["SummonerData"][self.region + summoner_name]['SummonerDTO']
                ChampionMasteryDTO = data["SummonerData"][self.region + summoner_name]['ChampionMasteryDTO']
                LeagueEntryDTO = data["SummonerData"][self.region + summoner_name]["LeagueEntryDTO"]
                ChampionPerformance = data["SummonerData"][self.region + summoner_name]["ChampionPerformance"]

                summoner_lvl = SummonerDTO['summonerLevel']
                champion_name = champions_name[str(champion_id)] 
                champion_mastery_lvl = 0
                champion_mastery_ptos = 0
                for mastery in ChampionMasteryDTO:
                    if mastery['championId'] == champion_id:
                        champion_mastery_lvl = mastery['championLevel']
                        champion_mastery_ptos = mastery['championPoints']
                        if champion_mastery_ptos >= 1000000:
                            champion_mastery_ptos = champion_mastery_ptos // 1000000
                            champion_mastery_ptos = str(champion_mastery_ptos) + 'M'
                        elif champion_mastery_ptos >= 1000:
                            champion_mastery_ptos = champion_mastery_ptos // 1000
                            champion_mastery_ptos = str(champion_mastery_ptos) + 'k'

                champion_winrate = -1
                if CurrentGameInfo['gameQueueConfigId'] in [420,440]:
                    for champion in ChampionPerformance['Season12'][CurrentGameInfo['gameQueueConfigId']]:
                        if champion['championId'] == champion_id:
                            champion_winrate = round(champion['wins'] / champion['totalMatches'] * 100, 0)

                SoloQ = None
                FlexQ = None
                for queue in LeagueEntryDTO:
                    if queue["queueType"] == "RANKED_SOLO_5x5":
                        SoloQ = queue
                    if queue["queueType"] == "RANKED_FLEX_SR":
                        FlexQ = queue

                if player['teamId'] == 100:
                    teamA_text += f'🧑‍💻<b>{summoner_name}</b><code> lvl {summoner_lvl}</code>\n'
                    teamA_text += f'<code>   </code><b><i>{champion_name}</i></b><code> Mlvl {champion_mastery_lvl} - {champion_mastery_ptos} </code>'
                    if champion_winrate != -1:
                        teamA_text += f'<b>{champion_winrate}%</b>'
                    teamA_text += '\n'
                    if SoloQ:
                        teamA_text += '<code>   </code>SoloQ: <b><u>' + SoloQ['tier'] + ' ' + SoloQ['rank'] + '</u></b>'
                    if FlexQ:
                        teamA_text += '<code>   </code>FlexQ: <b><u>' + FlexQ['tier'] + ' ' + FlexQ['rank'] + '</u></b>'
                    if SoloQ or FlexQ:
                        teamA_text += '\n'
                    teamA_text += '\n'
                else:
                    teamB_text += f'🧑‍💻<b>{summoner_name}</b><code> lvl {summoner_lvl}</code>\n'
                    teamB_text += f'<code>   </code><b><i>{champion_name}</i></b><code> Mlvl {champion_mastery_lvl} - {champion_mastery_ptos} </code>'
                    if champion_winrate != -1:
                        teamB_text += f'<b>{champion_winrate}%</b>'
                    teamB_text += '\n'
                    if SoloQ:
                        teamB_text += '<code>   </code>SoloQ: <b><u>' + SoloQ['tier'] + ' ' + SoloQ['rank'] + '</u></b>'
                    if FlexQ:
                        teamB_text += '<code>   </code>FlexQ: <b><u>' + FlexQ['tier'] + ' ' + FlexQ['rank'] + '</u></b>'
                    if SoloQ or FlexQ:
                        teamB_text += '\n'
                    teamB_text += '\n'

            text = f'<b>{self.summoner_name}</b> is actually in <i>{matchType}</i>:\n\n'
            text += teamA_text + '🆚🆚🆚🆚🆚🆚🆚🆚🆚🆚🆚🆚🆚\n\n' + teamB_text
            text += "⏱" + ("%d:%d" % (duration.hour * 60 + duration.minute, duration.second)) + '\n'
            text += 'match_id: ' + str(CurrentGameInfo['gameId'])

            response.error = False

        response.text = text
        return response                    
            
    def get_ChampionPerformance(self) -> dict:
        ChampionPerformance = dict()

        url = "https://u.gg/api"
        headers = {"Content-Type": "application/json"}

        # For Season12
        ChampionPerformance["Season12"] = dict()

        payload = json.dumps(
            {
                "operationName": "getPlayerStats",
                "variables": {
                    "summonerName": self.summoner_name,
                    "regionId": self.region,
                    "role": 7,
                    "seasonId": 18,
                    "queueType": [420, 440],
                },
                "query": "query getPlayerStats($queueType: [Int!], $regionId: String!, $role: Int!, $seasonId: Int!, $summonerName: String!) {\n fetchPlayerStatistics(\n queueType: $queueType\n summonerName: $summonerName\n regionId: $regionId\n role: $role\n seasonId: $seasonId\n ) {\n basicChampionPerformances {\n assists\n championId\n cs\n damage\n damageTaken\n deaths\n doubleKills\n gold\n kills\n maxDeaths\n maxKills\n pentaKills\n quadraKills\n totalMatches\n tripleKills\n wins\n lpAvg\n }\n queueType\n}\n}\n",
            }
        )
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
        except:
            ChampionPerformance["Season12"] = None
        else:
            if response.status_code != 200:
                ChampionPerformance["Season12"] = None
            else:
                playerStats = response.json()
                for queue in playerStats["data"]["fetchPlayerStatistics"]:
                    basicChampionPerformance = queue["basicChampionPerformances"]
                    ChampionPerformance["Season12"][queue["queueType"]] = basicChampionPerformance

        return ChampionPerformance

class Match:
    def __init__(self, region: str, matchId: str):
        self.region = region
        self.matchId = matchId

        if self.matchId not in data["Matches"]:
            data["Matches"][self.matchId] = lol_watcher.match.by_id(
                self.region, self.matchId
            )
            status.data.save_data()

        self.Match = data["Matches"][self.matchId]

    def short_info(self, summoner_name, user_time_zone) -> str:
        text = ""
        matchInfo = self.Match["info"]
        duration = datetime(1, 1, 1) + timedelta(seconds=matchInfo["gameDuration"])
        for player in matchInfo["participants"]:
            if player["summonerName"] == summoner_name:
                if duration.hour * 60 + duration.minute < 5:
                    text += "🔄|"
                elif player["win"]:
                    text += "✅|"
                else:
                    text += "❌|"
                text += ("<code>" + datetime.utcfromtimestamp(matchInfo["gameStartTimestamp"] / 1000 + user_time_zone * 60 * 60).strftime("%Y-%m-%d %H:%M") + "</code>|")
                text += ("⏱" + ("%d:%d" % (duration.hour * 60 + duration.minute, duration.second)) + "|")
                text += match_of[str(matchInfo['queueId'])]
                text += "\n"
                text += f"<b><i>{player['championName']}</i></b>|"
                text += f"<code>lvl {player['champLevel']}</code>|"
                text += f"<b>{player['kills']}</b> / <b>{player['deaths']}</b> / <b>{player['assists']}</b>|"
                text += f"👾{player['neutralMinionsKilled'] + player['totalMinionsKilled']}|"
                text += f"💰{player['goldEarned']}"
                text += "\n"
                text += '<code>match_id: ' + str(matchInfo['gameId']) +'</code>'
                text += "\n"

        return text

class ImageWrap:
    # Pasar como argumento imageName: str nombre de la imagen
    def setup(self, imageName: str):
        # Escribe en 'data_base.txt' la imagen en formato HTML
        toDataBase = '<img src="' + imageName + '">'
        with open("temp/data_base.txt", "a") as x:
            x.write(toDataBase)

    def wrap(self):
        # Guarda en read_data todo la informacion de 'data_base'
        with open("temp/data_base.txt") as r:
            read_data = r.read()

        # Escribe en 'wrapper.html' las imagenes
        with open("temp/wrapper.html", "w") as f:
            f.write('<meta content="text/html; charset=utf-8" http-equiv="Content-type"><meta content="jpg" name="imgkit-format"><body>\n' + read_data + "</body>")

        # Escribir direccion de las imagenes
        options = {"allow": "images/champion/"}
        # Convierte el HTML en JPG
        imgkit.from_file("temp/wrapper.html", "temp/wrapped.jpg", options)

        # Limpia 'data_base.txt' y 'wrapper.html'
        with open("temp/wrapper.html", "w") as file:
            file.write("")
        with open("temp/data_base.txt", "w") as file:
            file.write("")

class Champions:
    def __init__(self):
        self.image_wrap = ImageWrap()

    def free_champions(self, region: str, type: int=0) -> Response:
        response = Response()
        
        rotation = lol_watcher.champion.rotations(region)

        if type == 0:
            free_champions = rotation["freeChampionIds"]

            text = "The current free champions are: "

            for key in free_champions:
                text += champions_name[str(key)] + ", "
                self.image_wrap.setup(f"../images/champion/{champions_id[str(key)]}.png")

            self.image_wrap.wrap()

            text = text[: len(text) - 2] + "."

            response.text = text
            response.photo = open("temp/wrapped.jpg", "rb")
            response.error = False

            return response
        else:
            new_player_level = rotation['maxNewPlayerLevel']
            free_champions = rotation['freeChampionIdsForNewPlayers']
            
            text = f"The current free champions for players up to level {new_player_level} are: "
            
            for key in free_champions:
                text += champions_name[str(key)] + ", "
                self.image_wrap.setup(f'../images/champion/{champions_id[str(key)]}.png')

            self.image_wrap.wrap()
            
            text = text[:len(text)-2] + '.'

            response.text = text
            response.photo = open("temp/wrapped.jpg", "rb")
            response.error = False
            
            return response